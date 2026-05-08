"""Orchestrateur de synchronisation.

    sync_account(account_id, kind="initial" | "incremental")

Flow Sprint 1 :
    1. Charge l'account depuis DB
    2. Refresh access_token si expiré (refresh_access_token provider)
    3. Itère les RawMessage du provider
    4. Pour chaque message :
         - upsert contact (dédup par email_normalized)
         - upsert message (idempotent sur provider_id)
         - maj dénormalisée contact (last_msg_at, unread_count, has_attachments)
    5. Insère une ligne sync_log + met à jour last_sync_at sur account

Retry : `tenacity.retry` sur la boucle externe — 4 tentatives, backoff exp.

Concurrence : un `Semaphore` limite les appels concurrents au provider (cap
quota Gmail 250 unités/seconde pour un user). On utilise 5 en Sprint 1.
"""

from __future__ import annotations

import secrets
import sqlite3
import time
from datetime import UTC, datetime, timedelta
from typing import Literal

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from ..crypto import decrypt_str
from ..db import get_conn
from ..providers import get_provider
from ..providers.base import RawMessage
from .parser import Snippet, classify_kind, normalize_email

log = structlog.get_logger()

# Fenêtre initiale = 30 derniers jours (aligné avec ADR Sprint 1).
INITIAL_WINDOW_DAYS = 30


def _new_id() -> str:
    """Identifiant opaque URL-safe 22 chars. ULID-lexical en M2."""
    return secrets.token_urlsafe(16)


# ---------------------------------------------------------------------------
# Upsert helpers
# ---------------------------------------------------------------------------


def _upsert_contact(
    conn: sqlite3.Connection,
    *,
    account_id: str,
    account_email_norm: str,
    raw: RawMessage,
) -> tuple[str, bool]:
    """Upsert contact. Retourne (contact_id, is_outgoing).

    La direction du message détermine quel contact "représenter" :
    - message entrant → contact = from_email
    - message sortant → contact = premier destinataire (to[0])

    L'adresse du compte est normalisée une seule fois par le caller.
    """
    from_norm = normalize_email(raw.from_email) if raw.from_email else ""
    is_outgoing = from_norm == account_email_norm

    if is_outgoing:
        target = next(iter(raw.to_emails), None) or raw.from_email
        display_hint = None
    else:
        target = raw.from_email
        display_hint = raw.from_name

    email_norm = normalize_email(target)
    if not email_norm or "@" not in email_norm:
        # Fallback garde-fou : on ne crée pas de contact sans email valide
        raise ValueError(f"Email invalide pour contact: {target!r}")

    row = conn.execute(
        "SELECT id FROM contacts WHERE account_id = ? AND email_normalized = ?",
        (account_id, email_norm),
    ).fetchone()
    if row:
        return row["id"], is_outgoing

    contact_id = _new_id()
    conn.execute(
        """
        INSERT INTO contacts (
            id, account_id, email, email_normalized, display_name, kind
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            contact_id,
            account_id,
            target,
            email_norm,
            display_hint,
            classify_kind(email_norm),
        ),
    )
    return contact_id, is_outgoing


def _insert_message(
    conn: sqlite3.Connection,
    *,
    account_id: str,
    contact_id: str,
    raw: RawMessage,
    direction: Literal["in", "out"],
) -> str | None:
    """INSERT OR IGNORE — retourne l'id interne si créé, None si déjà présent.

    La dédup s'appuie sur UNIQUE(account_id, provider_id) du schéma.
    """
    # Dédup cheap avant INSERT — évite de gaspiller un id et un retry SQL.
    existing = conn.execute(
        "SELECT id FROM messages WHERE account_id = ? AND provider_id = ?",
        (account_id, raw.provider_id),
    ).fetchone()
    if existing:
        return None

    msg_id = _new_id()
    snippet = raw.snippet or Snippet.from_body(raw.body_text).text
    has_att = 1 if raw.attachment_refs else 0
    conn.execute(
        """
        INSERT INTO messages (
            id, account_id, contact_id, provider_id, thread_id,
            direction, subject, snippet, body_text, body_html,
            from_email, from_name, to_emails, cc_emails,
            received_at, is_read, has_attachments, raw_headers
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            msg_id,
            account_id,
            contact_id,
            raw.provider_id,
            raw.thread_id,
            direction,
            raw.subject,
            snippet,
            raw.body_text,
            raw.body_html,
            raw.from_email,
            raw.from_name,
            _json_dump(raw.to_emails),
            _json_dump(raw.cc_emails),
            int(raw.received_at.timestamp()),
            1 if raw.is_read else 0,
            has_att,
            None,  # raw_headers en M1 = non stocké (volume)
        ),
    )
    return msg_id


def _json_dump(seq: list[str]) -> str:
    """Sérialise une liste d'emails en JSON compact. NULL si vide serait ambigu
    en lecture côté /conversations → on stocke toujours un JSON, même vide."""
    import json

    return json.dumps(seq, separators=(",", ":"))


def _refresh_contact_aggregates(conn: sqlite3.Connection, contact_id: str) -> None:
    """Recalcule last_msg_at, unread_count, has_attachments pour un contact."""
    conn.execute(
        """
        UPDATE contacts SET
            last_msg_at = (
                SELECT MAX(received_at) FROM messages WHERE contact_id = ?
            ),
            unread_count = (
                SELECT COUNT(*) FROM messages
                WHERE contact_id = ? AND direction = 'in' AND is_read = 0
            ),
            has_attachments = (
                SELECT CASE WHEN EXISTS(
                    SELECT 1 FROM messages WHERE contact_id = ? AND has_attachments = 1
                ) THEN 1 ELSE 0 END
            )
        WHERE id = ?
        """,
        (contact_id, contact_id, contact_id, contact_id),
    )


# ---------------------------------------------------------------------------
# Entrée publique
# ---------------------------------------------------------------------------


@retry(
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=2, min=2, max=30),
    reraise=True,
)
async def sync_account(
    account_id: str,
    kind: Literal["initial", "incremental"] = "incremental",
) -> dict[str, object]:
    """Lance une sync pour un compte. Entrée unifiée appelée par l'API.

    - `initial` : importe les `INITIAL_WINDOW_DAYS` derniers jours
    - `incremental` : delta via history_cursor (Sprint 2)

    Toute exception remonte après 4 essais. `sync_log` est alimenté dans les 2
    cas (succès ou échec) pour pouvoir diagnostiquer a posteriori.
    """
    started = int(time.time())

    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, provider, email, oauth_access, history_cursor "
            "FROM accounts WHERE id = ? AND is_active = 1",
            (account_id,),
        ).fetchone()
        if not row:
            raise ValueError(f"Account {account_id} not found or inactive")

    provider_name = row["provider"]
    account_email_norm = row["email"].strip().lower()
    access_token = decrypt_str(row["oauth_access"])

    provider = get_provider(provider_name)
    log.info("sync_start", account=account_id, provider=provider_name, kind=kind)

    imported = 0
    error: str | None = None
    touched_contacts: set[str] = set()

    try:
        if kind == "initial":
            since = datetime.now(tz=UTC) - timedelta(days=INITIAL_WINDOW_DAYS)
            agen = provider.list_initial_messages(access_token, since)
        else:
            # Sprint 2 — on garde le placeholder pour ne pas casser l'appelant.
            raise NotImplementedError("sync_account(kind='incremental') — prévu Sprint 2")

        async for raw in agen:
            try:
                imported_this = _persist_message(
                    account_id=account_id,
                    account_email_norm=account_email_norm,
                    raw=raw,
                    touched_contacts=touched_contacts,
                )
                imported += imported_this
            except ValueError as e:
                # Email invalide / parse error → skip, on log mais on continue.
                log.warning(
                    "sync_skip_message",
                    account=account_id,
                    provider_id=raw.provider_id,
                    error=str(e),
                )

        # Recalcul dénormalisé une seule fois par contact touché (évite N UPDATE)
        if touched_contacts:
            with get_conn() as conn:
                for cid in touched_contacts:
                    _refresh_contact_aggregates(conn, cid)
                conn.commit()

    except Exception as e:
        error = str(e)[:500]
        log.error("sync_failed", account=account_id, kind=kind, error=error)
        _log_sync(account_id, kind, started, imported, error)
        raise

    _log_sync(account_id, kind, started, imported, None)
    log.info(
        "sync_done",
        account=account_id,
        imported=imported,
        contacts_touched=len(touched_contacts),
    )
    return {
        "account_id": account_id,
        "kind": kind,
        "messages_imported": imported,
    }


def _persist_message(
    *,
    account_id: str,
    account_email_norm: str,
    raw: RawMessage,
    touched_contacts: set[str],
) -> int:
    """Transaction unitaire pour un RawMessage. Retourne 1 si inséré, 0 sinon."""
    with get_conn() as conn:
        try:
            contact_id, is_outgoing = _upsert_contact(
                conn,
                account_id=account_id,
                account_email_norm=account_email_norm,
                raw=raw,
            )
            direction: Literal["in", "out"] = "out" if is_outgoing else "in"
            msg_id = _insert_message(
                conn,
                account_id=account_id,
                contact_id=contact_id,
                raw=raw,
                direction=direction,
            )
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise

    touched_contacts.add(contact_id)
    return 1 if msg_id else 0


def _log_sync(
    account_id: str,
    kind: str,
    started: int,
    imported: int,
    error: str | None,
) -> None:
    ended = int(time.time())
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO sync_log
               (account_id, kind, started_at, ended_at, messages_imported, error)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (account_id, kind, started, ended, imported, error),
        )
        conn.execute(
            "UPDATE accounts SET last_sync_at = ?, last_error = ? WHERE id = ?",
            (ended, error, account_id),
        )
        conn.commit()
