"""Liste des conversations (groupees par contact).

US-1.6 Sprint 1 · owner BE.

Principes :
- Un contact = une conversation (agregation WhatsApp-style).
- Tri : pinned en tete (pinned_order ASC), puis last_msg_at DESC.
- Pagination : cursor opaque (base64 de "{last_msg_at}:{id}") pour stabilite
  malgre les insertions concurrentes. Le client renvoie le cursor du dernier
  item recu.
- Filtres : all | humans | notifs | unread | attachments.
"""

from __future__ import annotations

import base64
import binascii
import sqlite3
from datetime import UTC, datetime
from typing import Literal, cast

import structlog
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..db import get_conn

router = APIRouter()
log = structlog.get_logger()

# ---------------------------------------------------------------------------
# Cursor opaque
# ---------------------------------------------------------------------------


def _encode_cursor(last_msg_at: int, contact_id: str) -> str:
    """Encode (ts, id) en base64url. Format interne cache au client."""
    raw = f"{last_msg_at}:{contact_id}".encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _decode_cursor(cursor: str) -> tuple[int, str]:
    """Retourne (last_msg_at, contact_id). Leve 400 si cursor invalide."""
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        raw = base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8")
        ts_str, _, cid = raw.partition(":")
        return int(ts_str), cid
    except (binascii.Error, UnicodeDecodeError, ValueError) as e:
        raise HTTPException(400, f"Cursor invalide: {e}") from e


# ---------------------------------------------------------------------------
# Response model
# ---------------------------------------------------------------------------


class ConversationItem(BaseModel):
    contact_id: str
    account_id: str
    email: str
    email_normalized: str
    display_name: str | None
    kind: Literal["human", "notif"]
    is_pinned: bool
    pinned_order: int | None
    is_muted: bool
    unread_count: int
    has_attachments: bool
    last_msg_at: datetime | None
    last_preview: str | None


class ConversationListResponse(BaseModel):
    items: list[ConversationItem]
    next_cursor: str | None


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------


@router.get(
    "",
    summary="Liste des conversations groupees par contact",
    response_model=ConversationListResponse,
)
def list_conversations(
    account_id: str | None = Query(None, description="Filtrer sur un compte"),
    filter: Literal["all", "humans", "notifs", "unread", "attachments"] = Query(
        "humans", description="Filtre principal de la liste"
    ),
    limit: int = Query(50, ge=1, le=200),
    cursor: str | None = Query(None, description="Opaque, issu de la reponse precedente"),
) -> ConversationListResponse:
    """Retourne les conversations ordonnees :
    - pinned d'abord (pinned_order ASC)
    - puis le reste par last_msg_at DESC, id DESC (tie-breaker)

    Le cursor encode (last_msg_at, id) du dernier item renvoye. On compare en
    "strictement inferieur" pour ne pas re-produire cet item.
    """
    sql = [
        """
        SELECT c.id, c.account_id, c.email, c.email_normalized, c.display_name,
               c.kind, c.is_pinned, c.pinned_order, c.is_muted,
               c.unread_count, c.has_attachments, c.last_msg_at,
               (SELECT m.snippet FROM messages m
                WHERE m.contact_id = c.id
                ORDER BY m.received_at DESC LIMIT 1) AS last_preview
        FROM contacts c
        WHERE c.is_archived = 0
        """,
    ]
    params: list[object] = []

    if account_id:
        sql.append(" AND c.account_id = ?")
        params.append(account_id)

    match filter:
        case "humans":
            sql.append(" AND c.kind = 'human'")
        case "notifs":
            sql.append(" AND c.kind = 'notif'")
        case "unread":
            sql.append(" AND c.unread_count > 0")
        case "attachments":
            sql.append(" AND c.has_attachments = 1")
        case "all":
            pass

    if cursor:
        cur_ts, cur_id = _decode_cursor(cursor)
        # On ne pagine que sur la partie "non-pinned" (pinned < 100 par compte,
        # sert toujours en premier). Requis pour stabilite.
        sql.append(
            " AND c.is_pinned = 0 AND ((c.last_msg_at < ?) OR (c.last_msg_at = ? AND c.id < ?))"
        )
        params.extend([cur_ts, cur_ts, cur_id])

    sql.append(
        """
        ORDER BY c.is_pinned DESC,
                 CASE WHEN c.is_pinned = 1 THEN c.pinned_order ELSE 999999 END ASC,
                 c.last_msg_at DESC,
                 c.id DESC
        LIMIT ?
        """
    )
    # +1 pour detecter s'il y a une page suivante
    params.append(limit + 1)

    with get_conn() as conn:
        rows = conn.execute("".join(sql), params).fetchall()

    has_more = len(rows) > limit
    rows = rows[:limit]

    items: list[ConversationItem] = []
    for r in rows:
        last_dt = (
            datetime.fromtimestamp(r["last_msg_at"], tz=UTC)
            if r["last_msg_at"] is not None
            else None
        )
        items.append(
            ConversationItem(
                contact_id=r["id"],
                account_id=r["account_id"],
                email=r["email"],
                email_normalized=r["email_normalized"],
                display_name=r["display_name"],
                kind=r["kind"],
                is_pinned=bool(r["is_pinned"]),
                pinned_order=r["pinned_order"],
                is_muted=bool(r["is_muted"]),
                unread_count=r["unread_count"],
                has_attachments=bool(r["has_attachments"]),
                last_msg_at=last_dt,
                last_preview=r["last_preview"],
            )
        )

    next_cursor: str | None = None
    if has_more and rows:
        last = rows[-1]
        # On ne genere un cursor que si le dernier item a bien un last_msg_at
        # (un contact sans message ne peut pas etre pagine — rare mais possible)
        if last["last_msg_at"] is not None:
            next_cursor = _encode_cursor(last["last_msg_at"], last["id"])

    return ConversationListResponse(items=items, next_cursor=next_cursor)


# ---------------------------------------------------------------------------
# Actions rapides liste : pin / non-lu / silence / archive
# ---------------------------------------------------------------------------


def _get_contact_action_context(conn: sqlite3.Connection, contact_id: str) -> sqlite3.Row:
    row = conn.execute(
        "SELECT id, account_id, is_pinned, pinned_order FROM contacts WHERE id = ?",
        (contact_id,),
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Conversation introuvable")
    return cast(sqlite3.Row, row)


@router.post("/{contact_id}/pin", summary="Epingler une conversation (max 3 par compte)")
def pin(contact_id: str) -> dict[str, object]:
    with get_conn() as conn:
        contact = _get_contact_action_context(conn, contact_id)
        if contact["is_pinned"]:
            return {"ok": True, "contact_id": contact_id}

        pinned_count = conn.execute(
            "SELECT COUNT(*) AS n FROM contacts WHERE account_id = ? AND is_pinned = 1",
            (contact["account_id"],),
        ).fetchone()["n"]
        if pinned_count >= 3:
            return {"ok": False, "reason": "limit_3_reached"}
        conn.execute(
            "UPDATE contacts SET is_pinned = 1, pinned_order = ? WHERE id = ?",
            (pinned_count + 1, contact_id),
        )
        conn.commit()
    return {"ok": True, "contact_id": contact_id}


@router.post("/{contact_id}/unpin")
def unpin(contact_id: str) -> dict[str, object]:
    with get_conn() as conn:
        contact = _get_contact_action_context(conn, contact_id)
        old_order = contact["pinned_order"]
        conn.execute(
            "UPDATE contacts SET is_pinned = 0, pinned_order = NULL WHERE id = ?",
            (contact_id,),
        )
        if old_order is not None:
            conn.execute(
                """
                UPDATE contacts
                SET pinned_order = pinned_order - 1
                WHERE account_id = ? AND is_pinned = 1 AND pinned_order > ?
                """,
                (contact["account_id"], old_order),
            )
        conn.commit()
    return {"ok": True, "contact_id": contact_id}


@router.post("/{contact_id}/mark-unread", summary="Marquer la conversation non lue")
def mark_conversation_unread(contact_id: str) -> dict[str, object]:
    with get_conn() as conn:
        _get_contact_action_context(conn, contact_id)
        latest_incoming = conn.execute(
            """
            SELECT id FROM messages
            WHERE contact_id = ? AND direction = 'in'
            ORDER BY received_at DESC, id DESC
            LIMIT 1
            """,
            (contact_id,),
        ).fetchone()
        if latest_incoming is None:
            return {"ok": False, "contact_id": contact_id, "reason": "no_incoming_message"}

        conn.execute("UPDATE messages SET is_read = 0 WHERE id = ?", (latest_incoming["id"],))
        unread_count = conn.execute(
            """
            SELECT COUNT(*) AS n FROM messages
            WHERE contact_id = ? AND direction = 'in' AND is_read = 0
            """,
            (contact_id,),
        ).fetchone()["n"]
        conn.execute(
            "UPDATE contacts SET unread_count = ? WHERE id = ?",
            (unread_count, contact_id),
        )
        conn.commit()
    return {"ok": True, "contact_id": contact_id, "unread_count": unread_count}


@router.post("/{contact_id}/mute")
def mute(contact_id: str, muted: bool = True) -> dict[str, object]:
    with get_conn() as conn:
        _get_contact_action_context(conn, contact_id)
        conn.execute(
            "UPDATE contacts SET is_muted = ? WHERE id = ?",
            (1 if muted else 0, contact_id),
        )
        conn.commit()
    return {"ok": True, "muted": muted}


@router.post("/{contact_id}/archive", summary="Archiver / désarchiver une conversation")
def archive(contact_id: str, archived: bool = True) -> dict[str, object]:
    with get_conn() as conn:
        _get_contact_action_context(conn, contact_id)
        conn.execute(
            """
            UPDATE contacts
            SET is_archived = ?,
                is_pinned = CASE WHEN ? = 1 THEN 0 ELSE is_pinned END,
                pinned_order = CASE WHEN ? = 1 THEN NULL ELSE pinned_order END
            WHERE id = ?
            """,
            (1 if archived else 0, 1 if archived else 0, 1 if archived else 0, contact_id),
        )
        conn.commit()
    return {"ok": True, "contact_id": contact_id, "archived": archived}
