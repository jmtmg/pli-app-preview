"""Reset password — request + confirm."""

from __future__ import annotations

import time

from ..config import settings
from ..db import get_conn, get_pg_conn
from .passwords import hash_password
from .tokens import consume_password_reset_token, create_password_reset_token


async def request_reset(email: str) -> None:
    """Toujours réussit côté API (ne révèle pas si l'email existe)."""
    email = email.strip().lower()
    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            row = await conn.fetchrow(
                "SELECT id FROM users WHERE email = $1 AND deleted_at IS NULL", email
            )
    else:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT id FROM users WHERE email = ? AND deleted_at IS NULL", (email,)
            ).fetchone()

    if not row:
        return  # silence

    token = await create_password_reset_token(row["id"])
    from ..emails.sender import send_password_reset_email

    try:
        await send_password_reset_email(email, token)
    except Exception:
        import structlog

        structlog.get_logger().warning("reset_email_failed", email=email)


async def confirm_reset(token: str, new_password: str) -> bool:
    user_id = await consume_password_reset_token(token)
    if not user_id:
        return False
    new_hash = hash_password(new_password)
    now = int(time.time())
    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            await conn.execute(
                "UPDATE users SET password_hash = $1, updated_at = $2 WHERE id = $3",
                new_hash,
                now,
                user_id,
            )
            # Invalide toutes les sessions actives
            await conn.execute(
                "UPDATE user_sessions SET revoked_at = $1 WHERE user_id = $2 AND revoked_at IS NULL",
                now,
                user_id,
            )
    else:
        with get_conn() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                (new_hash, now, user_id),
            )
            conn.execute(
                "UPDATE user_sessions SET revoked_at = ? WHERE user_id = ? AND revoked_at IS NULL",
                (now, user_id),
            )
            conn.commit()
    return True
