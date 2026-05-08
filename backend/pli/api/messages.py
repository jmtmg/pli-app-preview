"""Endpoints messages — lecture, marquage lu, envoi (Sprint 3).

GET  /messages/by-contact/{contact_id}
    Retourne les messages d'une conversation, tri ASC par received_at
    (chronologique, les plus anciens en haut — comme WhatsApp).
    Projection publique : pas de body_html, pas de raw_headers, pas de
    provider_id.

POST /messages/{id}/read
    Bascule le flag is_read + decrement du compteur contacts.unread_count.

POST /messages/send
    En mode local uniquement, persiste un message sortant fictif sans provider.
    Hors local, le vrai send provider reste un stub 501.

POST /messages/drafts
    Sprint 3 — stub 501.
"""

from __future__ import annotations

import json
import time
import uuid
from typing import Any, Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict

from ..config import settings
from ..db import get_conn
from ..models import Draft

router = APIRouter()


class MessageItem(BaseModel):
    """Projection publique d'un message pour la pane conversation.

    Contrat FE (frontend/src/api/queries.ts::Message) :
      - sent_at en epoch seconds (le FE formatte avec new Date(ts*1000))
      - body_snippet contient soit `snippet` provider, soit les 240 premiers
        chars de `body_text` (fallback).
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    contact_id: str
    direction: Literal["in", "out"]
    subject: str | None = None
    body_snippet: str = ""
    sent_at: int
    has_attachments: bool = False
    is_read: bool = False


def _row_to_message(row: dict[str, Any]) -> MessageItem:
    # Priorite au `snippet` provider ; sinon fallback body_text tronque.
    snippet = row.get("snippet")
    if not snippet:
        body_text = row.get("body_text") or ""
        snippet = body_text[:240]
    return MessageItem(
        id=row["id"],
        contact_id=row["contact_id"],
        direction=row["direction"],
        subject=row.get("subject"),
        body_snippet=snippet or "",
        sent_at=int(row["received_at"]),
        has_attachments=bool(row.get("has_attachments", 0)),
        is_read=bool(row.get("is_read", 0)),
    )


@router.get(
    "/by-contact/{contact_id}",
    response_model=list[MessageItem],
    summary="Messages d'une conversation (chronologique)",
)
def messages_by_contact(contact_id: str, limit: int = 200) -> list[MessageItem]:
    """Retourne les messages d'un contact en ordre chronologique (ASC).

    404 si le contact n'existe pas. limit est borne a 500 (garde-fou UI).
    """
    limit = max(1, min(int(limit), 500))
    with get_conn() as conn:
        contact = conn.execute(
            "SELECT id FROM contacts WHERE id = ?", (contact_id,)
        ).fetchone()
        if not contact:
            raise HTTPException(404, "contact introuvable")
        rows = conn.execute(
            """
            SELECT id, contact_id, direction, subject, snippet, body_text,
                   received_at, has_attachments, is_read
            FROM messages
            WHERE contact_id = ?
            ORDER BY received_at ASC
            LIMIT ?
            """,
            (contact_id, limit),
        ).fetchall()
    return [_row_to_message(dict(r)) for r in rows]


@router.post("/{message_id}/read", summary="Marquer lu / non lu")
def mark_read(message_id: str, read: bool = True) -> dict[str, object]:
    """Bascule is_read et met a jour contacts.unread_count si changement reel."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT contact_id, is_read FROM messages WHERE id = ?",
            (message_id,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "message introuvable")
        was_read = bool(row["is_read"])
        target = bool(read)
        if was_read == target:
            return {"ok": True, "message_id": message_id, "is_read": target, "changed": False}
        conn.execute(
            "UPDATE messages SET is_read = ? WHERE id = ?",
            (1 if target else 0, message_id),
        )
        # Delta sur le compteur denormalise. Clamp a 0 pour eviter les negatifs.
        delta = -1 if target else +1
        conn.execute(
            "UPDATE contacts SET unread_count = MAX(0, unread_count + ?) WHERE id = ?",
            (delta, row["contact_id"]),
        )
        conn.commit()
    return {"ok": True, "message_id": message_id, "is_read": target, "changed": True}


class SendMessageInput(BaseModel):
    """Payload minimal used by the MVP composer.

    In local/demo mode this creates a local outgoing message. Real provider send
    remains a later provider-specific implementation.
    """

    contact_id: str
    body: str
    subject: str | None = None
    account_id: str | None = None


# -------- Drafts / send — Sprint 3 --------


@router.post("/drafts", response_model=Draft)
def save_draft(draft: Draft) -> Draft:
    """Sprint 3 . BE — upsert brouillon avec deduplication par id."""
    raise HTTPException(501, "Sprint 3 — to implement")


@router.post("/send", response_model=MessageItem, summary="Envoyer un message")
async def send_message(payload: SendMessageInput) -> MessageItem:
    """Create an outgoing local message for the MVP composer.

    This makes PLI functional locally without OAuth provider credentials. The
    row is marked with a ``local-out-*`` provider id so it is easy to replace by
    a real Gmail/Microsoft send adapter later.
    """
    if settings.mode != "local":
        raise HTTPException(501, "envoi provider non implémenté hors mode local")
    body = payload.body.strip()
    if not body:
        raise HTTPException(422, "body vide")
    now = int(time.time())
    message_id = f"local-out-{uuid.uuid4().hex}"
    with get_conn() as conn:
        contact = conn.execute(
            """
            SELECT c.id, c.account_id, c.email, c.display_name, a.email AS account_email
            FROM contacts c
            JOIN accounts a ON a.id = c.account_id
            WHERE c.id = ?
            """,
            (payload.contact_id,),
        ).fetchone()
        if not contact:
            raise HTTPException(404, "contact introuvable")
        account_id = payload.account_id or contact["account_id"]
        if account_id != contact["account_id"]:
            raise HTTPException(400, "account_id ne correspond pas au contact")
        conn.execute(
            """
            INSERT INTO messages(
                id, account_id, contact_id, provider_id, thread_id, direction,
                subject, snippet, body_text, body_html, from_email, from_name,
                to_emails, cc_emails, received_at, is_read, is_starred,
                has_attachments, raw_headers, created_at
            ) VALUES (?, ?, ?, ?, ?, 'out', ?, ?, ?, NULL, ?, ?, ?, '[]', ?, 1, 0, 0, '', ?)
            """,
            (
                message_id,
                account_id,
                payload.contact_id,
                message_id,
                f"local-thread-{payload.contact_id}",
                payload.subject,
                body[:240],
                body,
                contact["account_email"],
                "PLI local",
                json.dumps([contact["email"]]),
                now,
                now,
            ),
        )
        conn.execute(
            "UPDATE contacts SET last_msg_at = ? WHERE id = ?",
            (now, payload.contact_id),
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT id, contact_id, direction, subject, snippet, body_text,
                   received_at, has_attachments, is_read
            FROM messages WHERE id = ?
            """,
            (message_id,),
        ).fetchone()
    return _row_to_message(dict(row))
