"""Tokens one-shot : vérif email, reset password.

Pattern : on génère un token opaque, on stocke son SHA-256 en DB avec TTL.
Le token en clair n'existe que dans l'URL envoyée à l'utilisateur.
"""

from __future__ import annotations

import hashlib
import secrets
import time

from ..config import settings
from ..db import get_conn, get_pg_conn

VERIFY_TTL_S = 24 * 3600  # 24 h
RESET_TTL_S = 60 * 60  # 1 h


def _hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def create_verification_token(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    th = _hash(token)
    now = int(time.time())
    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            await conn.execute(
                "INSERT INTO email_verifications(token_hash, user_id, expires_at) VALUES($1,$2,$3)",
                th,
                user_id,
                now + VERIFY_TTL_S,
            )
    else:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO email_verifications(token_hash, user_id, expires_at, created_at) VALUES(?,?,?,?)",
                (th, user_id, now + VERIFY_TTL_S, now),
            )
            conn.commit()
    return token


async def consume_verification_token(token: str) -> str | None:
    """Retourne user_id si token valide, None sinon (erreurs : expiré, déjà utilisé, inconnu)."""
    th = _hash(token)
    now = int(time.time())
    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            row = await conn.fetchrow(
                "SELECT user_id FROM email_verifications "
                "WHERE token_hash = $1 AND used_at IS NULL AND expires_at > $2",
                th,
                now,
            )
            if not row:
                return None
            await conn.execute(
                "UPDATE email_verifications SET used_at = $1 WHERE token_hash = $2",
                now,
                th,
            )
            await conn.execute(
                "UPDATE users SET is_verified = 1 WHERE id = $1",
                row["user_id"],
            )
            return row["user_id"]
    else:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT user_id FROM email_verifications "
                "WHERE token_hash = ? AND used_at IS NULL AND expires_at > ?",
                (th, now),
            ).fetchone()
            if not row:
                return None
            conn.execute(
                "UPDATE email_verifications SET used_at = ? WHERE token_hash = ?",
                (now, th),
            )
            conn.execute(
                "UPDATE users SET is_verified = 1 WHERE id = ?",
                (row["user_id"],),
            )
            conn.commit()
            return row["user_id"]


async def create_password_reset_token(user_id: str) -> str:
    token = secrets.token_urlsafe(32)
    th = _hash(token)
    now = int(time.time())
    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            await conn.execute(
                "INSERT INTO password_resets(token_hash, user_id, expires_at) VALUES($1,$2,$3)",
                th,
                user_id,
                now + RESET_TTL_S,
            )
    else:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO password_resets(token_hash, user_id, expires_at, created_at) VALUES(?,?,?,?)",
                (th, user_id, now + RESET_TTL_S, now),
            )
            conn.commit()
    return token


async def consume_password_reset_token(token: str) -> str | None:
    th = _hash(token)
    now = int(time.time())
    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            row = await conn.fetchrow(
                "SELECT user_id FROM password_resets "
                "WHERE token_hash = $1 AND used_at IS NULL AND expires_at > $2",
                th,
                now,
            )
            if not row:
                return None
            await conn.execute(
                "UPDATE password_resets SET used_at = $1 WHERE token_hash = $2",
                now,
                th,
            )
            return row["user_id"]
    else:
        with get_conn() as conn:
            row = conn.execute(
                "SELECT user_id FROM password_resets "
                "WHERE token_hash = ? AND used_at IS NULL AND expires_at > ?",
                (th, now),
            ).fetchone()
            if not row:
                return None
            conn.execute(
                "UPDATE password_resets SET used_at = ? WHERE token_hash = ?",
                (now, th),
            )
            conn.commit()
            return row["user_id"]
