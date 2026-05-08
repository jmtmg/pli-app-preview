"""Dispatcher webhooks Stripe — idempotent via `webhook_events`.

Contrat :
 1. Le handler HTTP vérifie la signature via `construct_event()`.
 2. Il appelle `handle_event(event)` qui :
      a) insère `webhook_events(event_id, type, received_at)` en ON CONFLICT NOTHING ;
      b) si l'insert a retourné 0 ligne → event déjà traité, on short-circuite ;
      c) sinon, dispatch vers un handler dédié (checkout.session.completed,
         customer.subscription.{created,updated,deleted}, invoice.paid,
         invoice.payment_failed).

La transaction d'audit est distincte du traitement métier pour éviter les
verrous longs — on accepte un petit risque de double-envoi d'email si le
handler métier crash après l'insert, mais l'idempotence persistante côté
`subscriptions.stripe_subscription_id` (ON CONFLICT) limite les dégâts.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import structlog
from asyncpg.exceptions import UniqueViolationError

from ..db import get_pg_conn
from ..emails.sender import send_invoice_email
from .licenses import issue_license_for_subscription
from .subscriptions import mark_subscription_canceled, upsert_subscription

log = structlog.get_logger()


def _ts(unix: int | None) -> datetime | None:
    if unix is None:
        return None
    return datetime.fromtimestamp(unix, tz=UTC)


async def _record_event(event_id: str, event_type: str) -> bool:
    """Enregistre un event. Retourne True si c'est la première fois."""
    # webhook_events est en table publique (pas tenant-scopé) → PG direct sans tenant
    async with get_pg_conn(tenant_id=None, bypass_rls=True) as c:
        try:
            await c.execute(
                "INSERT INTO webhook_events (event_id, event_type, received_at) "
                "VALUES ($1, $2, now())",
                event_id,
                event_type,
            )
            return True
        except UniqueViolationError:
            log.info("stripe_event_duplicate", event_id=event_id, type=event_type)
            return False


def _pli_meta(obj: dict[str, Any]) -> tuple[str | None, str | None]:
    """Extrait (tenant_id, user_id) depuis les metadata Stripe."""
    md = obj.get("metadata") or {}
    return md.get("pli_tenant_id"), md.get("pli_user_id")


# ---------------------------------------------------------------------------
# Handlers individuels
# ---------------------------------------------------------------------------


async def _on_checkout_completed(event: dict[str, Any]) -> None:
    session = event["data"]["object"]
    tenant_id, user_id = _pli_meta(session)
    if not (tenant_id and user_id):
        log.warning("checkout_completed_missing_meta", id=session.get("id"))
        return
    # Les détails d'abonnement arriveront via customer.subscription.* — on note
    # juste le customer_id pour pouvoir ouvrir le portail plus tard.
    customer_id = session.get("customer")
    if customer_id:
        async with get_pg_conn(tenant_id) as c:
            await c.execute(
                "UPDATE users SET stripe_customer_id = $1 WHERE id = $2",
                customer_id,
                user_id,
            )


async def _on_subscription_changed(event: dict[str, Any]) -> None:
    sub = event["data"]["object"]
    tenant_id, user_id = _pli_meta(sub)
    if not (tenant_id and user_id):
        log.warning("subscription_event_missing_meta", id=sub.get("id"))
        return
    items = sub.get("items", {}).get("data", [])
    price_id = items[0]["price"]["id"] if items else None
    plan = await upsert_subscription(
        tenant_id=tenant_id,
        user_id=user_id,
        stripe_customer_id=sub["customer"],
        stripe_subscription_id=sub["id"],
        status=sub["status"],
        price_id=price_id,
        current_period_end=_ts(sub.get("current_period_end")),
        trial_end=_ts(sub.get("trial_end")),
        cancel_at_period_end=bool(sub.get("cancel_at_period_end")),
    )
    # Si le plan devient "plus_monthly" ou "plus_yearly" → émettre une licence
    if plan.is_paid:
        await issue_license_for_subscription(
            tenant_id=tenant_id,
            user_id=user_id,
            stripe_subscription_id=sub["id"],
            plan=plan.value,
            valid_until=_ts(sub.get("current_period_end")),
        )


async def _on_subscription_deleted(event: dict[str, Any]) -> None:
    sub = event["data"]["object"]
    tenant_id, user_id = _pli_meta(sub)
    if not (tenant_id and user_id):
        return
    await mark_subscription_canceled(
        tenant_id=tenant_id,
        user_id=user_id,
        stripe_subscription_id=sub["id"],
    )


async def _on_invoice_paid(event: dict[str, Any]) -> None:
    inv = event["data"]["object"]
    tenant_id, user_id = _pli_meta(inv)
    # Les invoice events n'ont pas toujours les metadata — fallback sur subscription
    if not (tenant_id and user_id):
        sub_md = (inv.get("subscription_details") or {}).get("metadata") or {}
        tenant_id = tenant_id or sub_md.get("pli_tenant_id")
        user_id = user_id or sub_md.get("pli_user_id")
    if not (tenant_id and user_id):
        log.warning("invoice_paid_missing_meta", id=inv.get("id"))
        return
    email = inv.get("customer_email")
    if not email:
        log.warning("invoice_paid_missing_email", id=inv.get("id"))
        return
    lines = inv.get("lines", {}).get("data", [])
    plan_desc = (lines[0].get("description") if lines else None) or "PLI Plus"
    amount_paid = inv.get("amount_paid", 0)
    currency = (inv.get("currency") or "eur").upper()
    amount_str = f"{amount_paid / 100:.2f} {currency}"
    paid_at = _ts(inv.get("status_transitions", {}).get("paid_at")) or datetime.now(tz=UTC)
    next_charge = _ts(inv.get("next_payment_attempt")) or _ts(inv.get("period_end"))
    await send_invoice_email(
        to=email,
        plan=plan_desc,
        amount=amount_str,
        paid_at=paid_at,
        invoice_number=inv.get("number") or inv.get("id") or "—",
        invoice_url=inv.get("hosted_invoice_url") or inv.get("invoice_pdf") or "",
        next_charge_at=next_charge,
        tenant_id=tenant_id,
        user_id=user_id,
    )


async def _on_invoice_failed(event: dict[str, Any]) -> None:
    inv = event["data"]["object"]
    log.warning(
        "invoice_payment_failed",
        id=inv.get("id"),
        customer=inv.get("customer"),
        attempt=inv.get("attempt_count"),
    )
    # La bascule de plan est portée par l'event customer.subscription.updated
    # (status devient past_due/unpaid) — pas de traitement ici, juste audit.


_HANDLERS = {
    "checkout.session.completed": _on_checkout_completed,
    "customer.subscription.created": _on_subscription_changed,
    "customer.subscription.updated": _on_subscription_changed,
    "customer.subscription.trial_will_end": _on_subscription_changed,
    "customer.subscription.deleted": _on_subscription_deleted,
    "invoice.paid": _on_invoice_paid,
    "invoice.payment_succeeded": _on_invoice_paid,
    "invoice.payment_failed": _on_invoice_failed,
}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


async def handle_event(event: dict[str, Any]) -> None:
    event_id = event["id"]
    event_type = event["type"]

    first_time = await _record_event(event_id, event_type)
    if not first_time:
        return  # idempotent: already processed

    handler = _HANDLERS.get(event_type)
    if handler is None:
        log.info("stripe_event_ignored", type=event_type)
        return

    try:
        await handler(event)
    except Exception:
        log.exception("stripe_event_handler_failed", event_id=event_id, type=event_type)
        # NB: on ne rollback pas webhook_events — Stripe retry livrera
        # à nouveau l'event ; si le handler est idempotent (upsert, licence
        # ON CONFLICT), le deuxième passage aboutira.
        raise
