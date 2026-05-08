"""Persistance des abonnements Stripe côté PLI.

Toutes les écritures passent par ces fonctions — jamais directement depuis
les webhooks — pour que l'audit, le changement de plan et l'envoi de mail
restent cohérents.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import structlog

from ..db import get_pg_conn
from .plans import Plan, plan_from_subscription_status

log = structlog.get_logger()


async def upsert_subscription(
    *,
    tenant_id: str,
    user_id: str,
    stripe_customer_id: str,
    stripe_subscription_id: str,
    status: str,
    price_id: str | None,
    current_period_end: datetime | None,
    trial_end: datetime | None,
    cancel_at_period_end: bool,
) -> Plan:
    """Crée / met à jour l'abonnement du user. Retourne le plan PLI calculé."""
    plan = plan_from_subscription_status(status=status, price_id=price_id)  # type: ignore[arg-type]
    async with get_pg_conn(tenant_id) as c:
        await c.execute(
            """
            INSERT INTO subscriptions (
              user_id, stripe_customer_id, stripe_subscription_id,
              status, price_id, plan,
              current_period_end, trial_end, cancel_at_period_end,
              updated_at
            )
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9, now())
            ON CONFLICT (stripe_subscription_id) DO UPDATE SET
              status = EXCLUDED.status,
              price_id = EXCLUDED.price_id,
              plan = EXCLUDED.plan,
              current_period_end = EXCLUDED.current_period_end,
              trial_end = EXCLUDED.trial_end,
              cancel_at_period_end = EXCLUDED.cancel_at_period_end,
              updated_at = now()
            """,
            user_id,
            stripe_customer_id,
            stripe_subscription_id,
            status,
            price_id,
            plan.value,
            current_period_end,
            trial_end,
            cancel_at_period_end,
        )
        # Garde l'effet sur le user pour un accès rapide côté API
        await c.execute(
            """
            UPDATE users
               SET plan = $1,
                   stripe_customer_id = $2,
                   plan_updated_at = now()
             WHERE id = $3
            """,
            plan.value,
            stripe_customer_id,
            user_id,
        )
    log.info(
        "subscription_upserted",
        tenant_id=tenant_id,
        user_id=user_id,
        plan=plan.value,
        status=status,
    )
    return plan


async def mark_subscription_canceled(
    *,
    tenant_id: str,
    user_id: str,
    stripe_subscription_id: str,
) -> None:
    async with get_pg_conn(tenant_id) as c:
        await c.execute(
            """
            UPDATE subscriptions
               SET status = 'canceled', plan = 'free', updated_at = now()
             WHERE stripe_subscription_id = $1
            """,
            stripe_subscription_id,
        )
        await c.execute(
            """
            UPDATE users
               SET plan = 'free', plan_updated_at = now()
             WHERE id = $1
            """,
            user_id,
        )
    log.info("subscription_canceled", tenant_id=tenant_id, user_id=user_id)


async def get_subscription_by_user(tenant_id: str, user_id: str) -> dict[str, Any] | None:
    async with get_pg_conn(tenant_id) as c:
        row = await c.fetchrow(
            "SELECT * FROM subscriptions WHERE user_id = $1 ORDER BY updated_at DESC LIMIT 1",
            user_id,
        )
        return dict(row) if row else None
