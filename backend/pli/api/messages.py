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
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from ..config import settings
from ..db import get_conn
from ..models import Draft
from ..sync.parser import normalize_email

router = APIRouter()

MAX_LOCAL_ATTACHMENT_BYTES = 25 * 1024 * 1024
MAX_LOCAL_ATTACHMENTS = 20


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
    cc_emails: list[str] = Field(default_factory=list)


def _parse_public_email_list(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return []
    if not isinstance(parsed, list):
        return []
    return [str(item) for item in parsed if isinstance(item, str) and item.strip()]


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
        cc_emails=_parse_public_email_list(row.get("cc_emails")),
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
                   received_at, has_attachments, is_read, cc_emails
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


class LocalAttachmentInput(BaseModel):
    """Metadata-only attachment selected in the local composer.

    No file bytes are accepted here. The row stored in ``attachments`` keeps
    only filename/type/size so the local UI can display chips and contact PJ
    history without pretending a provider upload happened.
    """

    filename: str = Field(..., min_length=1, max_length=255)
    mime_type: str | None = Field(default=None, max_length=200)
    size_bytes: int | None = Field(default=None, ge=0, le=MAX_LOCAL_ATTACHMENT_BYTES)

    @field_validator("filename")
    @classmethod
    def filename_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("filename vide")
        return stripped

    @field_validator("mime_type")
    @classmethod
    def empty_mime_type_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class SendMessageInput(BaseModel):
    """Payload minimal used by the MVP composer.

    In local/demo mode this creates a local outgoing message. Real provider send
    remains a later provider-specific implementation.

    `contact_id` is used for replies/existing conversations. `to_email` +
    `account_id` powers the new-message modal and creates/reuses a local contact.
    """

    contact_id: str | None = None
    to_email: EmailStr | None = None
    body: str
    subject: str | None = None
    account_id: str | None = None
    cc_emails: list[EmailStr] = Field(default_factory=list)
    bcc_emails: list[EmailStr] = Field(default_factory=list)
    attachments: list[LocalAttachmentInput] = Field(
        default_factory=list,
        max_length=MAX_LOCAL_ATTACHMENTS,
    )

    @model_validator(mode="after")
    def recipient_required(self) -> SendMessageInput:
        if not self.contact_id and not self.to_email:
            raise ValueError("contact_id ou to_email requis")
        if self.to_email and not self.account_id:
            raise ValueError("account_id requis pour un nouveau destinataire")
        return self


# -------- Drafts / send — Sprint 3 --------


def _draft_row_to_model(row: dict[str, Any]) -> Draft:
    return Draft(
        id=row["id"],
        account_id=row["account_id"],
        contact_id=row.get("contact_id"),
        in_reply_to=row.get("in_reply_to"),
        to_emails=json.loads(row.get("to_emails") or "[]"),
        cc_emails=json.loads(row.get("cc_emails") or "[]"),
        subject=row.get("subject"),
        body_text=row.get("body_text") or "",
        signature_active=bool(row.get("signature_active", 1)),
    )


def _existing_draft_id(
    conn: Any,
    *,
    account_id: str,
    contact_id: str | None,
) -> str | None:
    row = conn.execute(
        """
        SELECT id FROM drafts
        WHERE account_id = ?
          AND COALESCE(contact_id, '') = COALESCE(?, '')
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (account_id, contact_id),
    ).fetchone()
    return row["id"] if row else None


def _validate_draft_scope(conn: Any, draft: Draft) -> None:
    if draft.contact_id:
        contact = conn.execute(
            "SELECT id, account_id, email FROM contacts WHERE id = ?",
            (draft.contact_id,),
        ).fetchone()
        if not contact:
            raise HTTPException(404, "contact introuvable")
        if contact["account_id"] != draft.account_id:
            raise HTTPException(400, "account_id ne correspond pas au contact")
    account = conn.execute("SELECT id FROM accounts WHERE id = ?", (draft.account_id,)).fetchone()
    if not account:
        raise HTTPException(404, "account introuvable")


def _resolve_send_contact(conn: Any, payload: SendMessageInput, now: int) -> Any:
    """Return the target contact row for reply or local new-message send."""
    if payload.contact_id:
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
        return contact

    assert payload.account_id is not None
    assert payload.to_email is not None
    account = conn.execute(
        "SELECT id, email FROM accounts WHERE id = ?",
        (payload.account_id,),
    ).fetchone()
    if not account:
        raise HTTPException(404, "account introuvable")

    recipient_email = str(payload.to_email).strip()
    normalized = normalize_email(recipient_email)
    contact = conn.execute(
        """
        SELECT c.id, c.account_id, c.email, c.display_name, a.email AS account_email
        FROM contacts c
        JOIN accounts a ON a.id = c.account_id
        WHERE c.account_id = ? AND c.email_normalized = ?
        """,
        (payload.account_id, normalized),
    ).fetchone()
    if contact:
        return contact

    contact_id = f"local-contact-{uuid.uuid4().hex}"
    local_part = recipient_email.split("@", 1)[0]
    conn.execute(
        """
        INSERT INTO contacts(
            id, account_id, email, email_normalized, display_name,
            kind, last_msg_at, unread_count, has_attachments, created_at
        ) VALUES (?, ?, ?, ?, ?, 'human', ?, 0, 0, ?)
        """,
        (contact_id, payload.account_id, recipient_email, normalized, local_part, now, now),
    )
    return conn.execute(
        """
        SELECT c.id, c.account_id, c.email, c.display_name, a.email AS account_email
        FROM contacts c
        JOIN accounts a ON a.id = c.account_id
        WHERE c.id = ?
        """,
        (contact_id,),
    ).fetchone()


def _json_email_list(emails: list[EmailStr]) -> str:
    return json.dumps([str(email) for email in emails])


def _store_local_attachment_metadata(
    conn: Any,
    *,
    message_id: str,
    contact_id: str,
    attachments: list[LocalAttachmentInput],
    now: int,
) -> None:
    for attachment in attachments:
        attachment_id = f"local-att-{uuid.uuid4().hex}"
        conn.execute(
            """
            INSERT INTO attachments(
                id, message_id, contact_id, filename, mime_type,
                size_bytes, provider_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                attachment_id,
                message_id,
                contact_id,
                attachment.filename,
                attachment.mime_type,
                attachment.size_bytes,
                attachment_id,
                now,
            ),
        )


@router.get("/drafts", response_model=Draft | None, summary="Brouillon local d'une conversation")
def get_draft(
    account_id: str,
    contact_id: str | None = None,
) -> Draft | None:
    """Retourne le brouillon local courant, s'il existe.

    Le MVP conserve un seul brouillon par conversation et par compte. La clef
    logique est account_id + contact_id ; cela évite les fuites entre comptes.
    """
    with get_conn() as conn:
        draft_id = _existing_draft_id(
            conn,
            account_id=account_id,
            contact_id=contact_id,
        )
        if not draft_id:
            return None
        row = conn.execute(
            """
            SELECT id, account_id, contact_id, in_reply_to, to_emails, cc_emails,
                   subject, body_text, signature_active
            FROM drafts WHERE id = ?
            """,
            (draft_id,),
        ).fetchone()
    return _draft_row_to_model(dict(row)) if row else None


@router.post("/drafts", response_model=Draft, summary="Sauvegarder un brouillon local")
def save_draft(draft: Draft) -> Draft:
    """Upsert d'un brouillon local avec un seul brouillon par conversation."""
    if settings.mode != "local":
        raise HTTPException(501, "brouillons provider non implémentés hors mode local")
    with get_conn() as conn:
        _validate_draft_scope(conn, draft)
        # Le serveur ignore tout id fourni par le client : l'invariant MVP est
        # un seul brouillon par compte + conversation, pas un document libre.
        # L'index unique DB `idx_drafts_account_contact_unique` protège aussi
        # les écritures concurrentes ; on ne dépend donc pas d'un SELECT préalable.
        draft_id = f"draft-{uuid.uuid4().hex}"
        now = int(time.time())
        conn.execute(
            """
            INSERT INTO drafts(
                id, account_id, contact_id, in_reply_to, to_emails, cc_emails,
                subject, body_text, signature_active, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT DO UPDATE SET
                in_reply_to = excluded.in_reply_to,
                to_emails = excluded.to_emails,
                cc_emails = excluded.cc_emails,
                subject = excluded.subject,
                body_text = excluded.body_text,
                signature_active = excluded.signature_active,
                updated_at = excluded.updated_at
            """,
            (
                draft_id,
                draft.account_id,
                draft.contact_id,
                draft.in_reply_to,
                json.dumps([str(email) for email in draft.to_emails]),
                json.dumps([str(email) for email in draft.cc_emails]),
                draft.subject,
                draft.body_text,
                1 if draft.signature_active else 0,
                now,
            ),
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT id, account_id, contact_id, in_reply_to, to_emails, cc_emails,
                   subject, body_text, signature_active
            FROM drafts
            WHERE account_id = ?
              AND COALESCE(contact_id, '') = COALESCE(?, '')
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (draft.account_id, draft.contact_id),
        ).fetchone()
    return _draft_row_to_model(dict(row))


@router.delete("/drafts/{draft_id}", summary="Supprimer un brouillon local")
def delete_draft(
    draft_id: str,
    account_id: str,
    contact_id: str | None = None,
) -> dict[str, object]:
    with get_conn() as conn:
        cur = conn.execute(
            """
            DELETE FROM drafts
            WHERE id = ?
              AND account_id = ?
              AND COALESCE(contact_id, '') = COALESCE(?, '')
            """,
            (draft_id, account_id, contact_id),
        )
        conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(404, "brouillon introuvable")
    return {"ok": True, "deleted": True, "draft_id": draft_id}


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
        contact = _resolve_send_contact(conn, payload, now)
        account_id = payload.account_id or contact["account_id"]
        has_attachments = 1 if payload.attachments else 0
        conn.execute(
            """
            INSERT INTO messages(
                id, account_id, contact_id, provider_id, thread_id, direction,
                subject, snippet, body_text, body_html, from_email, from_name,
                to_emails, cc_emails, bcc_emails, received_at, is_read, is_starred,
                has_attachments, raw_headers, created_at
            ) VALUES (?, ?, ?, ?, ?, 'out', ?, ?, ?, NULL, ?, ?, ?, ?, ?, ?, 1, 0, ?, '', ?)
            """,
            (
                message_id,
                account_id,
                contact["id"],
                message_id,
                f"local-thread-{contact['id']}",
                payload.subject,
                body[:240],
                body,
                contact["account_email"],
                "PLI local",
                json.dumps([contact["email"]]),
                _json_email_list(payload.cc_emails),
                _json_email_list(payload.bcc_emails),
                now,
                has_attachments,
                now,
            ),
        )
        _store_local_attachment_metadata(
            conn,
            message_id=message_id,
            contact_id=contact["id"],
            attachments=payload.attachments,
            now=now,
        )
        conn.execute(
            """
            UPDATE contacts
            SET last_msg_at = ?,
                has_attachments = CASE WHEN ? = 1 THEN 1 ELSE has_attachments END
            WHERE id = ?
            """,
            (now, has_attachments, contact["id"]),
        )
        conn.commit()
        row = conn.execute(
            """
            SELECT id, contact_id, direction, subject, snippet, body_text,
                   received_at, has_attachments, is_read, cc_emails
            FROM messages WHERE id = ?
            """,
            (message_id,),
        ).fetchone()
    return _row_to_message(dict(row))
