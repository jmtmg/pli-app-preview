"""
API OCR (Sprint 8 — US-8.8).

Endpoints exposés :
- GET  /api/attachments/{id}/text       → texte OCRisé (si dispo)
- POST /api/attachments/{id}/ocr        → force la (re-)génération (rate-limited)
- GET  /api/attachments/{id}/ocr/status → état de la tâche

Toutes les routes sont scopées au `current_user` (filtre RLS au niveau
modèle + double-check applicatif pour défense en profondeur — cf.
incident pentest H-003 sur /gdpr/export/{id}).
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from pli.auth.deps import User, current_user
from pli.db.session import SessionDep
from pli.models.attachment import Attachment, AttachmentText
from pli.ratelimit import RateLimit
from pli.tasks import queue

router = APIRouter(prefix="/api/attachments", tags=["ocr"])

# Rate limit volontairement bas : OCR est CPU-intensif, on évite l'abus.
# 30 forces / heure / utilisateur = ~1 PJ toutes les 2 minutes, large.
ocr_force_limit = RateLimit(scope="ocr_force", limit=30, window_seconds=3600)


# ---------------------------------------------------------------------------
# Schemas Pydantic
# ---------------------------------------------------------------------------


class AttachmentTextOut(BaseModel):
    attachment_id: str
    text: str
    language: str = Field(description='Codes ISO séparés par virgule, ex "fr,en"')
    pages: int
    truncated: bool = Field(description="True si le PDF dépassait 50 pages")
    source: Literal["image", "pdf_text_layer", "pdf_raster"]


class OcrStatusOut(BaseModel):
    attachment_id: str
    state: Literal["not_started", "queued", "running", "done", "failed"]
    queued_at: str | None = None
    finished_at: str | None = None
    error: str | None = None


class OcrEnqueuedOut(BaseModel):
    attachment_id: str
    job_id: str
    state: Literal["queued"] = "queued"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_owned_attachment(att_id: str, user: User, session) -> Attachment:
    """Charge la PJ ou 404 — *jamais* 403 (anti-IDOR, leçon pentest)."""
    att = session.get(Attachment, att_id)
    if att is None or att.owner_user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="attachment_not_found",
        )
    return att


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/{att_id}/text", response_model=AttachmentTextOut)
def get_attachment_text(
    att_id: str,
    session: SessionDep,
    user: User = Depends(current_user),
) -> AttachmentTextOut:
    _get_owned_attachment(att_id, user, session)
    text = session.get(AttachmentText, att_id)
    if text is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="text_not_yet_extracted",
        )
    return AttachmentTextOut(
        attachment_id=att_id,
        text=text.text,
        language=text.language,
        pages=text.pages,
        truncated=text.truncated,
        source=text.source,
    )


@router.post(
    "/{att_id}/ocr",
    response_model=OcrEnqueuedOut,
    status_code=status.HTTP_202_ACCEPTED,
)
def force_ocr(
    att_id: str,
    session: SessionDep,
    user: User = Depends(current_user),
) -> OcrEnqueuedOut:
    """Force une (re-)extraction. Utile si un user signale un mauvais OCR.

    Le worker est idempotent : si `attachment_text` existe, il faut
    d'abord le supprimer. On le fait ici dans la transaction qui crée
    le job, pour éviter la fenêtre de course.
    """
    ocr_force_limit.check_or_raise(user.id)
    att = _get_owned_attachment(att_id, user, session)

    existing = session.get(AttachmentText, att_id)
    if existing is not None:
        session.delete(existing)
        session.flush()

    job = queue.enqueue("pli.ocr.worker.extract_text", att.id)
    return OcrEnqueuedOut(attachment_id=att.id, job_id=job.id)


@router.get("/{att_id}/ocr/status", response_model=OcrStatusOut)
def get_ocr_status(
    att_id: str,
    session: SessionDep,
    user: User = Depends(current_user),
) -> OcrStatusOut:
    _get_owned_attachment(att_id, user, session)

    text = session.get(AttachmentText, att_id)
    if text is not None:
        return OcrStatusOut(
            attachment_id=att_id,
            state="done",
            finished_at=text.created_at.isoformat() if text.created_at else None,
        )

    job_state = queue.get_state_for("pli.ocr.worker.extract_text", att_id)
    if job_state is None:
        return OcrStatusOut(attachment_id=att_id, state="not_started")
    return OcrStatusOut(
        attachment_id=att_id,
        state=job_state.state,  # "queued" | "running" | "failed"
        queued_at=job_state.queued_at.isoformat() if job_state.queued_at else None,
        error=job_state.error,
    )
