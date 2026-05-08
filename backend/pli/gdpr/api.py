"""HTTP endpoints exposing GDPR rights (access, portability, deletion)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from pli.auth import current_user
from pli.db import Session, get_db
from pli.gdpr import (
    cancel_account_deletion,
    enqueue_export,
    get_export_status,
    schedule_account_deletion,
)
from pli.gdpr.deletion import (
    NotScheduledError,
    WrongPasswordError,
    get_deletion_state,
)
from pli.models import Account, AuditLog, Contact, Message, User

router = APIRouter(prefix="/gdpr", tags=["gdpr"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class ExportResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    expires_at: datetime | None = None
    download_url: str | None = None
    size_bytes: int | None = None


class DeletionRequest(BaseModel):
    password_confirmation: str = Field(..., min_length=1)
    i_understand_this_is_permanent: bool = Field(..., description="must be true")


class DeletionResponse(BaseModel):
    scheduled: bool
    purge_at: datetime | None = None
    scheduled_at: datetime | None = None


class MyDataResponse(BaseModel):
    user_id: str
    email: str
    locale: str
    plan: str
    created_at: datetime
    accounts: list[dict]
    volumetrie: dict
    legal_bases: list[dict]
    subprocessors_url: str
    dpo_contact: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/export",
    response_model=ExportResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Demander un export RGPD (art. 20 — portabilité)",
)
def request_export(user: User = Depends(current_user), db: Session = Depends(get_db)):
    view = enqueue_export(user.id, session=db)
    return ExportResponse(**view.__dict__)


@router.get(
    "/export/{job_id}",
    response_model=ExportResponse,
    summary="Statut d'un job d'export",
)
def export_status(
    job_id: uuid.UUID,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    view = get_export_status(user.id, job_id, session=db)
    if view is None:
        raise HTTPException(status_code=404, detail="export introuvable")
    return ExportResponse(**view.__dict__)


@router.post(
    "/delete",
    response_model=DeletionResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Programmer la suppression du compte (art. 17 — effacement)",
)
def schedule_deletion(
    payload: DeletionRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    if not payload.i_understand_this_is_permanent:
        raise HTTPException(
            status_code=400,
            detail="vous devez confirmer que la suppression est définitive",
        )
    try:
        state = schedule_account_deletion(
            user.id,
            password_confirmation=payload.password_confirmation,
            session=db,
        )
    except WrongPasswordError:
        # Intentionally generic to avoid oracles.
        raise HTTPException(status_code=400, detail="impossible de vérifier votre identité")
    return DeletionResponse(
        scheduled=state.scheduled,
        purge_at=state.purge_at,
        scheduled_at=state.scheduled_at,
    )


@router.delete(
    "/cancel-deletion",
    response_model=DeletionResponse,
    summary="Annuler une suppression programmée (dans la fenêtre 30 jours)",
)
def cancel_deletion(user: User = Depends(current_user), db: Session = Depends(get_db)):
    try:
        state = cancel_account_deletion(user.id, session=db)
    except NotScheduledError:
        raise HTTPException(status_code=404, detail="aucune suppression programmée")
    return DeletionResponse(
        scheduled=state.scheduled, purge_at=state.purge_at, scheduled_at=state.scheduled_at
    )


@router.get(
    "/my-data",
    response_model=MyDataResponse,
    summary="Accès aux données (art. 15)",
)
def my_data(user: User = Depends(current_user), db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.user_id == user.id).all()
    nb_messages = (
        db.query(Message)
        .join(Account, Message.account_id == Account.id)
        .filter(Account.user_id == user.id)
        .count()
    )
    nb_contacts = db.query(Contact).filter(Contact.user_id == user.id).count()
    deletion_state = get_deletion_state(user.id, session=db)

    db.add(
        AuditLog(
            user_id=user.id,
            action="gdpr.access.viewed",
            resource_id=str(user.id),
            created_at=datetime.now(UTC),
        )
    )
    db.commit()

    return MyDataResponse(
        user_id=str(user.id),
        email=user.email,
        locale=user.locale or "fr",
        plan=user.plan,
        created_at=user.created_at,
        accounts=[
            {
                "id": str(a.id),
                "provider": a.provider,
                "email": a.email,
                "connected_at": a.created_at,
            }
            for a in accounts
        ],
        volumetrie={
            "nb_accounts": len(accounts),
            "nb_messages": nb_messages,
            "nb_contacts": nb_contacts,
            "deletion": {
                "scheduled": deletion_state.scheduled,
                "purge_at": deletion_state.purge_at,
            },
        },
        legal_bases=[
            {
                "finalite": "Gestion du compte et du service",
                "base": "Exécution du contrat (art. 6-1-b RGPD)",
            },
            {"finalite": "Sécurité du service", "base": "Intérêt légitime (art. 6-1-f RGPD)"},
            {"finalite": "Facturation", "base": "Exécution du contrat (art. 6-1-b RGPD)"},
            {"finalite": "Analytics produit", "base": "Consentement (art. 6-1-a RGPD) — opt-in"},
        ],
        subprocessors_url="https://pli.app/subprocessors",
        dpo_contact="dpo@pli.app",
    )
