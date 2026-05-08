"""JWT access/refresh tokens + rotation (ADR-0003).

- Access : HS256, TTL 15 min, revoquable par jti (table `revoked_access_jti`)
- Refresh : opaque random 256-bit, stocké hashé SHA-256 en DB (table `user_sessions`)
            rotation : chaque appel /auth/refresh invalide l'ancien et émet un nouveau
"""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass
from typing import Any

import jwt as pyjwt
from jwt import InvalidTokenError

from ..config import settings

ACCESS_TTL_S = 15 * 60
REFRESH_TTL_S = 30 * 24 * 3600
CLOCK_SKEW_S = 30

ALGO = "HS256"


class TokenError(Exception):
    pass


def _secret() -> str:
    return settings.secret_key.get_secret_value()


@dataclass(frozen=True, slots=True)
class UserClaim:
    id: str
    email: str
    plan: str


def issue_access_token(user: UserClaim) -> str:
    now = int(time.time())
    payload: dict[str, Any] = {
        "sub": user.id,
        "email": user.email,
        "plan": user.plan,
        "iat": now,
        "nbf": now,
        "exp": now + ACCESS_TTL_S,
        "jti": secrets.token_urlsafe(16),
        "typ": "access",
    }
    return pyjwt.encode(payload, _secret(), algorithm=ALGO)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        claims = pyjwt.decode(
            token,
            _secret(),
            algorithms=[ALGO],
            options={"require": ["exp", "sub", "jti", "typ"]},
            leeway=CLOCK_SKEW_S,
        )
    except InvalidTokenError as e:
        raise TokenError(str(e)) from e
    if claims.get("typ") != "access":
        raise TokenError("wrong_token_type")
    # Vérif liste de révocation
    if _is_access_revoked(claims["jti"]):
        raise TokenError("token_revoked")
    return claims


def _is_access_revoked(jti: str) -> bool:
    from ..db import get_conn, get_pg_conn

    if settings.mode == "cloud":
        import asyncio

        async def _check() -> bool:
            async with get_pg_conn() as conn:
                row = await conn.fetchrow(
                    "SELECT 1 FROM revoked_access_jti WHERE jti = $1 AND expires_at > $2",
                    jti,
                    int(time.time()),
                )
                return row is not None

        return asyncio.get_event_loop().run_until_complete(_check())  # pragma: no cover
    with get_conn() as conn:
        row = conn.execute(
            "SELECT 1 FROM revoked_access_jti WHERE jti = ? AND expires_at > ?",
            (jti, int(time.time())),
        ).fetchone()
        return row is not None


async def revoke_access_jti(jti: str, expires_at: int) -> None:
    from ..db import get_conn, get_pg_conn

    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            await conn.execute(
                "INSERT INTO revoked_access_jti(jti, expires_at) VALUES($1, $2) "
                "ON CONFLICT DO NOTHING",
                jti,
                expires_at,
            )
    else:
        with get_conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO revoked_access_jti(jti, expires_at) VALUES(?, ?)",
                (jti, expires_at),
            )
            conn.commit()


# ---------------------------------------------------------------------------
# Refresh tokens — opaques, stockés hashés
# ---------------------------------------------------------------------------


def _hash_refresh(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)  # 384 bits
