"""Login PLI + gestion session refresh."""

from __future__ import annotations

import time
from dataclasses import dataclass

from ulid import ULID

from ..config import settings
from ..db import get_conn, get_pg_conn
from .jwt import (
    REFRESH_TTL_S,
    UserClaim,
    _hash_refresh,
    generate_refresh_token,
    issue_access_token,
    revoke_access_jti,
)
from .passwords import hash_password, needs_rehash, verify_password


class InvalidCredentials(Exception):
    pass


class EmailNotVerified(Exception):
    pass


@dataclass(frozen=True, slots=True)
class LoginResult:
    access_token: str
    refresh_token: str
    user_id: str
    email: str
    plan: str


# ---------------------------------------------------------------------------
# Load user
# ---------------------------------------------------------------------------


async def _get_user_by_email(email: str) -> dict | None:
    email = email.strip().lower()
    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            row = await conn.fetchrow(
                "SELECT id, email, password_hash, is_verified, plan FROM users "
                "WHERE email = $1 AND deleted_at IS NULL",
                email,
            )
            return dict(row) if row else None
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, email, password_hash, is_verified, plan FROM users "
            "WHERE email = ? AND deleted_at IS NULL",
            (email,),
        ).fetchone()
        return dict(row) if row else None


async def _update_password_hash(user_id: str, new_hash: str) -> None:
    now = int(time.time())
    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            await conn.execute(
                "UPDATE users SET password_hash = $1, updated_at = $2 WHERE id = $3",
                new_hash,
                now,
                user_id,
            )
    else:
        with get_conn() as conn:
            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?",
                (new_hash, now, user_id),
            )
            conn.commit()


# ---------------------------------------------------------------------------
# Session creation
# ---------------------------------------------------------------------------


async def _create_session(user_id: str, refresh_token: str, ua: str | None, ip: str | None) -> None:
    now = int(time.time())
    session_id = str(ULID())
    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            await conn.execute(
                """INSERT INTO user_sessions(id, user_id, refresh_token_hash,
                                             user_agent, ip_address, issued_at, expires_at)
                   VALUES($1, $2, $3, $4, $5, $6, $7)""",
                session_id,
                user_id,
                _hash_refresh(refresh_token),
                ua,
                ip,
                now,
                now + REFRESH_TTL_S,
            )
    else:
        with get_conn() as conn:
            conn.execute(
                "INSERT INTO user_sessions(id,user_id,refresh_token_hash,user_agent,ip_address,issued_at,expires_at) "
                "VALUES(?,?,?,?,?,?,?)",
                (
                    session_id,
                    user_id,
                    _hash_refresh(refresh_token),
                    ua,
                    ip,
                    now,
                    now + REFRESH_TTL_S,
                ),
            )
            conn.commit()


# ---------------------------------------------------------------------------
# Login entry point
# ---------------------------------------------------------------------------


async def login(
    email: str, password: str, *, user_agent: str | None, ip: str | None
) -> LoginResult:
    user = await _get_user_by_email(email)
    if not user:
        # Timing-safe : hash simulé pour ne pas révéler l'absence de compte
        from .passwords import _hasher

        _hasher.hash("dummy-password-for-timing")
        raise InvalidCredentials()

    if not verify_password(password, user["password_hash"]):
        raise InvalidCredentials()

    if not user["is_verified"]:
        raise EmailNotVerified()

    if needs_rehash(user["password_hash"]):
        await _update_password_hash(user["id"], hash_password(password))

    refresh = generate_refresh_token()
    await _create_session(user["id"], refresh, user_agent, ip)
    access = issue_access_token(UserClaim(id=user["id"], email=user["email"], plan=user["plan"]))

    return LoginResult(
        access_token=access,
        refresh_token=refresh,
        user_id=user["id"],
        email=user["email"],
        plan=user["plan"],
    )


# ---------------------------------------------------------------------------
# Refresh (rotation)
# ---------------------------------------------------------------------------


async def rotate_refresh(refresh_token: str) -> LoginResult:
    """Rotation : invalide l'ancien refresh, émet un nouveau + un access.

    Règle de sécurité : si l'ancien est déjà marqué `rotated_at`, on révoque
    toute la chaîne (vol de token détecté).
    """
    th = _hash_refresh(refresh_token)
    now = int(time.time())

    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            row = await conn.fetchrow(
                "SELECT id, user_id, expires_at, rotated_at, revoked_at FROM user_sessions "
                "WHERE refresh_token_hash = $1",
                th,
            )
            if not row or row["revoked_at"] or row["expires_at"] < now:
                raise InvalidCredentials()
            if row["rotated_at"]:
                # Possible vol : révoque toutes les sessions du user
                await conn.execute(
                    "UPDATE user_sessions SET revoked_at = $1 WHERE user_id = $2",
                    now,
                    row["user_id"],
                )
                raise InvalidCredentials()

            user = await conn.fetchrow(
                "SELECT id, email, plan FROM users WHERE id = $1", row["user_id"]
            )
            new_refresh = generate_refresh_token()
            new_th = _hash_refresh(new_refresh)
            new_id = str(ULID())
            await conn.execute(
                "UPDATE user_sessions SET rotated_at = $1 WHERE id = $2",
                now,
                row["id"],
            )
            await conn.execute(
                """INSERT INTO user_sessions(id, user_id, refresh_token_hash, issued_at, expires_at)
                   VALUES($1, $2, $3, $4, $5)""",
                new_id,
                user["id"],
                new_th,
                now,
                now + REFRESH_TTL_S,
            )
            access = issue_access_token(
                UserClaim(id=user["id"], email=user["email"], plan=user["plan"])
            )
            return LoginResult(
                access_token=access,
                refresh_token=new_refresh,
                user_id=user["id"],
                email=user["email"],
                plan=user["plan"],
            )

    # SQLite branch
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, user_id, expires_at, rotated_at, revoked_at FROM user_sessions "
            "WHERE refresh_token_hash = ?",
            (th,),
        ).fetchone()
        if not row or row["revoked_at"] or row["expires_at"] < now:
            raise InvalidCredentials()
        if row["rotated_at"]:
            conn.execute(
                "UPDATE user_sessions SET revoked_at = ? WHERE user_id = ?",
                (now, row["user_id"]),
            )
            conn.commit()
            raise InvalidCredentials()
        user = conn.execute(
            "SELECT id, email, plan FROM users WHERE id = ?",
            (row["user_id"],),
        ).fetchone()
        new_refresh = generate_refresh_token()
        new_th = _hash_refresh(new_refresh)
        conn.execute(
            "UPDATE user_sessions SET rotated_at = ? WHERE id = ?",
            (now, row["id"]),
        )
        conn.execute(
            "INSERT INTO user_sessions(id,user_id,refresh_token_hash,issued_at,expires_at) "
            "VALUES(?,?,?,?,?)",
            (str(ULID()), user["id"], new_th, now, now + REFRESH_TTL_S),
        )
        conn.commit()
        access = issue_access_token(
            UserClaim(id=user["id"], email=user["email"], plan=user["plan"])
        )
        return LoginResult(
            access_token=access,
            refresh_token=new_refresh,
            user_id=user["id"],
            email=user["email"],
            plan=user["plan"],
        )


async def logout(
    refresh_token: str, access_jti: str | None = None, access_exp: int | None = None
) -> None:
    th = _hash_refresh(refresh_token)
    now = int(time.time())
    if settings.mode == "cloud":
        async with get_pg_conn() as conn:
            await conn.execute(
                "UPDATE user_sessions SET revoked_at = $1 WHERE refresh_token_hash = $2",
                now,
                th,
            )
    else:
        with get_conn() as conn:
            conn.execute(
                "UPDATE user_sessions SET revoked_at = ? WHERE refresh_token_hash = ?",
                (now, th),
            )
            conn.commit()
    if access_jti and access_exp:
        await revoke_access_jti(access_jti, access_exp)
