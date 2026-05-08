"""Fonctions d'envoi des emails transactionnels.

Chaque fonction :
 1. rend le template HTML + texte (Jinja2 minimal — pas de dépendance lourde).
 2. appelle le provider sélectionné.
 3. journalise l'envoi dans `outbound_emails` pour audit.

Les erreurs du provider sont propagées : les appelants décident du retry
(worker de sync, endpoint HTTP, etc.). L'audit log est best-effort (exception
swallow) pour ne jamais bloquer le flux métier.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog
from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..config import settings
from ..db import get_conn, get_pg_conn
from .provider import EmailMessage, get_email_provider

log = structlog.get_logger()

_TEMPLATES_DIR = Path(__file__).parent / "templates"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
    keep_trailing_newline=True,
)


def _render(template: str, ctx: dict[str, Any]) -> tuple[str, str]:
    """Rend la paire (html, text) pour un template donné."""
    ctx = {**ctx, "app_url": settings.app_url}
    body_html = _env.get_template(f"{template}.html").render(**ctx)
    # On embarque le body dans base.html
    base = _env.get_template("base.html")
    html = base.render(subject=ctx.get("subject", "PLI"), body=body_html, app_url=settings.app_url)
    text = _env.get_template(f"{template}.txt").render(**ctx)
    return html, text


async def _record_audit(
    *,
    tenant_id: str | None,
    user_id: str | None,
    to: str,
    template: str,
    subject: str,
    provider_msg_id: str | None,
    status: str,
    error: str | None = None,
) -> None:
    """Persiste un enregistrement outbound_emails.

    - En mode local → pas de colonne user_id (un seul utilisateur).
    - En mode cloud → scope tenant_id.
    """
    try:
        if settings.mode == "cloud":
            if tenant_id is None:
                return  # pas d'audit sans tenant en cloud
            async with get_pg_conn(tenant_id) as c:
                await c.execute(
                    """
                    INSERT INTO outbound_emails
                        (user_id, template, to_address, subject, provider_msg_id, status, error, sent_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, now())
                    """,
                    user_id,
                    template,
                    to,
                    subject,
                    provider_msg_id,
                    status,
                    error,
                )
        else:
            with get_conn() as c:
                c.execute(
                    """
                    INSERT INTO outbound_emails
                        (template, to_address, subject, provider_msg_id, status, error, sent_at)
                    VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                    """,
                    (template, to, subject, provider_msg_id, status, error),
                )
                c.commit()
    except Exception as exc:  # audit best-effort
        log.warning("outbound_email_audit_failed", error=str(exc), template=template)


async def _send(
    *,
    to: str,
    subject: str,
    template: str,
    ctx: dict[str, Any],
    tenant_id: str | None = None,
    user_id: str | None = None,
    headers: dict[str, str] | None = None,
) -> str | None:
    html, text = _render(template, {**ctx, "subject": subject})
    msg = EmailMessage(
        to=to,
        subject=subject,
        html=html,
        text=text,
        template=template,
        context=ctx,
        headers=headers or {},
    )
    provider = get_email_provider()
    try:
        provider_msg_id = await provider.send(msg)
    except Exception as exc:
        log.error("email_send_failed", to=to, template=template, error=str(exc))
        await _record_audit(
            tenant_id=tenant_id,
            user_id=user_id,
            to=to,
            template=template,
            subject=subject,
            provider_msg_id=None,
            status="failed",
            error=str(exc),
        )
        raise
    await _record_audit(
        tenant_id=tenant_id,
        user_id=user_id,
        to=to,
        template=template,
        subject=subject,
        provider_msg_id=provider_msg_id,
        status="sent",
    )
    log.info("email_sent", to=to, template=template, provider_msg_id=provider_msg_id)
    return provider_msg_id


# ---------------------------------------------------------------------------
# API publique — une fonction par template
# ---------------------------------------------------------------------------


async def send_verification_email(
    *,
    to: str,
    token: str,
    tenant_id: str | None = None,
    user_id: str | None = None,
) -> str | None:
    verify_url = f"{settings.app_url}/auth/verify?token={token}"
    return await _send(
        to=to,
        subject="Activez votre compte PLI",
        template="verify",
        ctx={"verify_url": verify_url},
        tenant_id=tenant_id,
        user_id=user_id,
    )


async def send_password_reset_email(
    *,
    to: str,
    token: str,
    tenant_id: str | None = None,
    user_id: str | None = None,
) -> str | None:
    reset_url = f"{settings.app_url}/auth/reset?token={token}"
    return await _send(
        to=to,
        subject="Réinitialisation de votre mot de passe PLI",
        template="password_reset",
        ctx={"reset_url": reset_url},
        tenant_id=tenant_id,
        user_id=user_id,
    )


async def send_trial_reminder_email(
    *,
    to: str,
    days_left: int,
    tenant_id: str | None = None,
    user_id: str | None = None,
) -> str | None:
    billing_url = f"{settings.app_url}/settings/billing"
    subject = (
        "Votre essai PLI Plus se termine demain"
        if days_left == 1
        else f"Votre essai PLI Plus se termine dans {days_left} jours"
    )
    return await _send(
        to=to,
        subject=subject,
        template="trial_reminder",
        ctx={"days_left": days_left, "billing_url": billing_url},
        tenant_id=tenant_id,
        user_id=user_id,
    )


async def send_invoice_email(
    *,
    to: str,
    plan: str,
    amount: str,
    paid_at: datetime,
    invoice_number: str,
    invoice_url: str,
    next_charge_at: datetime | None,
    tenant_id: str | None = None,
    user_id: str | None = None,
) -> str | None:
    billing_url = f"{settings.app_url}/settings/billing"
    return await _send(
        to=to,
        subject=f"Facture PLI Plus — {invoice_number}",
        template="invoice",
        ctx={
            "plan": plan,
            "amount": amount,
            "paid_at": paid_at.astimezone(UTC).strftime("%d/%m/%Y"),
            "invoice_number": invoice_number,
            "invoice_url": invoice_url,
            "next_charge_at": (
                next_charge_at.astimezone(UTC).strftime("%d/%m/%Y") if next_charge_at else "—"
            ),
            "billing_url": billing_url,
        },
        tenant_id=tenant_id,
        user_id=user_id,
    )
