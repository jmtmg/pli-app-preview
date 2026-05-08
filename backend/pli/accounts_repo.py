"""Repository `accounts` — persistance locale (SQLite) des comptes mail.

Toutes les écritures passent d'ici. Les tokens OAuth sont chiffrés avant d'atterrir
en base (Fernet via `pli.crypto.get_crypto()`).

En mode cloud, une impl équivalente vivra dans `pli/accounts_repo_cloud.py` avec
asyncpg + RLS (M3).
"""

from __future__ import annotations

import hashlib
import secrets
import time
from typing import Literal

import structlog

from .crypto import encrypt_str
from .db import get_conn
from .models import Account

log = structlog.get_logger()

Provider = Literal["gmail", "microsoft"]

# Palette bronze — cohérente avec `frontend/src/styles/tokens.css`.
# L'index est dérivé de l'email pour une couleur stable entre sessions.
_AVATAR_PALETTE = (
    "#c9a47d",  # bronze primaire
    "#b8916a",
    "#a17c58",
    "#d4b08c",
    "#8b6c4a",
    "#e0c4a0",
)


def _pick_avatar_color(email: str) -> str:
    """Sélection déterministe dans la palette — même email → même couleur."""
    digest = hashlib.sha1(email.lower().encode("utf-8")).digest()
    return _AVATAR_PALETTE[digest[0] % len(_AVATAR_PALETTE)]


def _new_account_id() -> str:
    """Identifiant opaque, URL-safe, 22 chars. Upgrade vers ULID lexicographique en M2."""
    return secrets.token_urlsafe(16)


def upsert_from_oauth(
    *,
    provider: Provider,
    email: str,
    display_name: str | None,
    access_token: str,
    refresh_token: str | None,
    expires_in_seconds: int,
) -> Account:
    """Upsert idempotent après un échange OAuth réussi.

    * Nouveau compte  → INSERT avec id + avatar_color.
    * Compte existant → UPDATE tokens + display_name + is_active=1.

    Contrainte Google : un ré-consent **sans** `prompt=consent` peut omettre
    `refresh_token`. Dans ce cas, on **préserve** la valeur persistée précédemment
    plutôt que d'écraser par NULL — sinon on perdrait la capacité de refresh.
    """
    email_norm = email.strip().lower()
    expiry_epoch = int(time.time()) + int(expires_in_seconds)

    oauth_access_enc = encrypt_str(access_token)
    oauth_refresh_enc = encrypt_str(refresh_token) if refresh_token else None

    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id, oauth_refresh FROM accounts WHERE provider = ? AND email = ?",
            (provider, email_norm),
        ).fetchone()

        if existing is None:
            account_id = _new_account_id()
            avatar_color = _pick_avatar_color(email_norm)
            conn.execute(
                """
                INSERT INTO accounts (
                    id, provider, email, display_name,
                    oauth_access, oauth_refresh, oauth_expiry,
                    avatar_color, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
                """,
                (
                    account_id,
                    provider,
                    email_norm,
                    display_name,
                    oauth_access_enc,
                    oauth_refresh_enc,
                    expiry_epoch,
                    avatar_color,
                ),
            )
            conn.commit()
            log.info(
                "account_created",
                account_id=account_id,
                provider=provider,
                email=email_norm,
            )
        else:
            account_id = existing["id"]
            # Préserver l'ancien refresh_token si Google n'en retourne pas
            final_refresh = oauth_refresh_enc or existing["oauth_refresh"]
            conn.execute(
                """
                UPDATE accounts SET
                    display_name = COALESCE(?, display_name),
                    oauth_access = ?,
                    oauth_refresh = ?,
                    oauth_expiry = ?,
                    is_active = 1,
                    last_error = NULL
                WHERE id = ?
                """,
                (
                    display_name,
                    oauth_access_enc,
                    final_refresh,
                    expiry_epoch,
                    account_id,
                ),
            )
            conn.commit()
            log.info(
                "account_reconnected",
                account_id=account_id,
                provider=provider,
                email=email_norm,
            )

    # Re-lire en DB pour retourner un objet cohérent (évite un Account partiel)
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM accounts WHERE id = ?", (account_id,)).fetchone()
    return Account.model_validate(dict(row))
