"""Endpoints fiche contact — lecture + mise a jour manuelle.

GET /contacts/{id}
    Retourne un contact avec ses dernieres pieces jointes (24 max).
    Projection publique, pas de champs internes (created_at, email_normalized).

PATCH /contacts/{id}
    Mise a jour partielle des metadonnees editables par l'utilisateur
    (display_name, company, role, phone, notes, is_pinned, is_muted).
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr

from ..db import get_conn

router = APIRouter()


class AttachmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    message_id: str
    filename: str
    mime_type: str | None = None
    size_bytes: int | None = None
    created_at: int | None = None


class ContactDetail(BaseModel):
    """Projection publique d'un contact pour la fiche laterale."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    account_id: str
    email: EmailStr
    display_name: str | None = None
    company: str | None = None
    role: str | None = None
    phone: str | None = None
    notes: str | None = None
    kind: Literal["human", "notif"] = "human"
    is_muted: bool = False
    is_pinned: bool = False
    pinned_order: int | None = None
    unread_count: int = 0
    has_attachments: bool = False
    attachments: list[AttachmentSummary] = []


class ContactPatch(BaseModel):
    display_name: str | None = None
    company: str | None = None
    role: str | None = None
    phone: str | None = None
    notes: str | None = None
    is_muted: bool | None = None
    is_pinned: bool | None = None
    pinned_order: int | None = None


@router.get("/{contact_id}", response_model=ContactDetail, summary="Fiche contact")
def get_contact(contact_id: str) -> ContactDetail:
    with get_conn() as conn:
        row = conn.execute(
            """SELECT id, account_id, email, display_name, company, role, phone,
                      notes, kind, is_muted, is_pinned, pinned_order,
                      unread_count, has_attachments
               FROM contacts WHERE id = ?""",
            (contact_id,),
        ).fetchone()
        if not row:
            raise HTTPException(404, "contact introuvable")
        atts = conn.execute(
            """SELECT id, message_id, filename, mime_type, size_bytes, created_at
               FROM attachments WHERE contact_id = ?
               ORDER BY created_at DESC LIMIT 24""",
            (contact_id,),
        ).fetchall()
    data = dict(row)
    data["attachments"] = [AttachmentSummary(**dict(a)) for a in atts]
    return ContactDetail(**data)


@router.patch("/{contact_id}", response_model=ContactDetail, summary="Mettre a jour un contact")
def update_contact(contact_id: str, patch: ContactPatch) -> ContactDetail:
    fields = {k: v for k, v in patch.model_dump().items() if v is not None}
    if not fields:
        raise HTTPException(400, "aucun champ a modifier")
    # Pin rules : max 3 contacts epingles par compte, pinned_order dans [1..3].
    if "pinned_order" in fields and fields["pinned_order"] is not None:
        order = int(fields["pinned_order"])
        if order < 1 or order > 3:
            raise HTTPException(400, "pinned_order doit etre entre 1 et 3")
    sets = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values()) + [contact_id]
    with get_conn() as conn:
        cur = conn.execute(f"UPDATE contacts SET {sets} WHERE id = ?", values)
        if cur.rowcount == 0:
            raise HTTPException(404, "contact introuvable")
        conn.commit()
    # Retourne la fiche a jour pour que le FE se resynchronise sans refetch.
    return get_contact(contact_id)
