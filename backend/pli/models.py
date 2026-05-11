"""Modèles de domaine PLI — Pydantic v2.

Ces modèles sont utilisés côté API (request/response) ET côté couche de sync
comme DTO entre provider et DB.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Account(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    provider: Literal["gmail", "microsoft"]
    email: EmailStr
    display_name: str | None = None
    signature: str | None = None
    avatar_color: str | None = None
    last_sync_at: datetime | None = None
    is_active: bool = True


class Contact(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    account_id: str
    email: EmailStr
    display_name: str | None = None
    company: str | None = None
    role: str | None = None
    phone: str | None = None
    notes: str | None = None
    is_muted: bool = False
    is_pinned: bool = False
    pinned_order: int | None = None
    kind: Literal["human", "notif"] = "human"
    last_msg_at: datetime | None = None
    unread_count: int = 0
    has_attachments: bool = False


class Attachment(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    mime_type: str | None = None
    size_bytes: int | None = None
    sha256: str | None = None


class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    account_id: str
    contact_id: str
    provider_id: str
    thread_id: str | None = None
    direction: Literal["in", "out"]
    subject: str | None = None
    snippet: str | None = None
    body_text: str | None = None
    body_html: str | None = None
    from_email: EmailStr
    from_name: str | None = None
    to_emails: list[EmailStr] = Field(default_factory=list)
    cc_emails: list[EmailStr] = Field(default_factory=list)
    bcc_emails: list[EmailStr] = Field(default_factory=list)
    received_at: datetime
    is_read: bool = False
    has_attachments: bool = False
    attachments: list[Attachment] = Field(default_factory=list)


class Draft(BaseModel):
    id: str | None = None
    account_id: str
    contact_id: str | None = None
    in_reply_to: str | None = None
    to_emails: list[EmailStr] = Field(default_factory=list)
    cc_emails: list[EmailStr] = Field(default_factory=list)
    subject: str | None = None
    body_text: str = ""
    signature_active: bool = True


# --- Responses communes ---


class ConversationListItem(BaseModel):
    """Item de la liste conversation (par contact)."""

    contact: Contact
    last_message_preview: str
    last_message_time: datetime
    unread_count: int
    is_pinned: bool
    has_attachments: bool


class SyncStatus(BaseModel):
    account_id: str
    kind: Literal["initial", "incremental"]
    started_at: datetime
    ended_at: datetime | None = None
    messages_imported: int = 0
    in_progress: bool = False
    error: str | None = None
