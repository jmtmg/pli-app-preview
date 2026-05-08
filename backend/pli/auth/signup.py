"""Création d'un compte PLI."""

from __future__ import annotations

import time
from dataclasses import dataclass

from ulid import ULID  # ulid-py

from ..config import settings
from ..db import get_conn, get_pg_conn
from .passwords import hash_password
from .tokens import create_verification_token


@dataclass(frozen=True, slots=True)
class CreatedUser:
    id: str
    email: str
    plan: str = "free"


class EmailAlreadyExists(ValueError):
    pass


async def create_user(email: str, password: str) -> CreatedUser:
    email = email.strip().lower()
    pw_hash = hash_password(password)
    user_id = str(ULID())
    now = int(time.time())

    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            try:
                await conn.execute(
                    """
                    INSERT INTO users(id, email, password_hash, plan, created_at, updated_at)
                    VALUES($1, $2, $3, 'free', $4, $4)
                    """,
                    user_id,
                    email,
                    pw_hash,
                    now,
                )
            except Exception as e:  # asyncpg UniqueViolationError
                if "users_email_key" in str(e) or "duplicate key" in str(e).lower():
                    raise EmailAlreadyExists(email) from e
                raise
    else:
        with get_conn() as conn:
            try:
                conn.execute(
                    "INSERT INTO users(id,email,password_hash,plan,created_at,updated_at) VALUES(?,?,?,?,?,?)",
                    (user_id, email, pw_hash, "free", now, now),
                )
                conn.commit()
            except Exception as e:
                msg = str(e).lower()
                if "unique" in msg and "email" in msg:
                    raise EmailAlreadyExists(email) from e
                raise

    user = CreatedUser(id=user_id, email=email, plan="free")

    # Envoi email de vérification (async, non bloquant)
    token = await create_verification_token(user_id)
    from ..emails.sender import send_verification_email

    try:
        await send_verification_email(user.email, token)
    except Exception:
        # On loggue mais on n'échoue pas le signup — l'utilisateur peut redemander
        import structlog

        structlog.get_logger().warning("verification_email_failed", user_id=user_id)

    return user
