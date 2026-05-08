"""Émission / révocation de licences PLI Plus (cloud).

NB : les licences *Local* (offline, signées Ed25519) sont gérées dans
`pli.licensing.local`. Ici, on parle de la trace côté Cloud d'un abonnement
actif — la source de vérité reste `subscriptions`.
"""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import structlog

from ..db import get_pg_conn

log = structlog.get_logger()


async def issue_license_for_subscription(
    *,
    tenant_id: str,
    user_id: str,
    stripe_subscription_id: str,
    plan: str,
    valid_until: datetime | None,
) -> str:
    """Insère une licence Cloud si absente. Retourne la license_key."""
    license_key = f"plus_{uuid4().hex}"
    async with get_pg_conn(tenant_id) as c:
        row = await c.fetchrow(
            """
            INSERT INTO licenses
                (license_key, user_id, plan, stripe_subscription_id, valid_until, status)
            VALUES ($1, $2, $3, $4, $5, 'active')
            ON CONFLICT (stripe_subscription_id) DO UPDATE SET
                plan = EXCLUDED.plan,
                valid_until = EXCLUDED.valid_until,
                status = 'active',
                updated_at = now()
            RETURNING license_key
            """,
            license_key,
            user_id,
            plan,
            stripe_subscription_id,
            valid_until,
        )
    key = row["license_key"] if row else license_key
    log.info("license_issued", tenant_id=tenant_id, user_id=user_id, plan=plan)
    return key


async def get_active_license(*, tenant_id: str, user_id: str) -> dict | None:
    async with get_pg_conn(tenant_id) as c:
        row = await c.fetchrow(
            """
            SELECT license_key, plan, valid_until, status
              FROM licenses
             WHERE user_id = $1 AND status = 'active'
             ORDER BY updated_at DESC LIMIT 1
            """,
            user_id,
        )
        return dict(row) if row else None
