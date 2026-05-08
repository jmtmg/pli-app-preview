"""API Invitations — consommation d'un code pour activer un user beta."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from pli.auth.dependencies import current_user, require_admin
from pli.beta import batches
from pli.beta.batches import InvitationError
from pli.billing.plans import grant_beta_plan
from pli.db.models import User
from pli.db.session import get_session
from pli.security.rate_limit import rate_limit

router = APIRouter(prefix="/invitations", tags=["invitations"])


class RedeemIn(BaseModel):
    code: str = Field(min_length=8, max_length=32)


class RedeemOut(BaseModel):
    ok: bool
    batch_number: int
    plan_granted: str


@router.post("/redeem", response_model=RedeemOut)
@rate_limit("invitations_redeem", limit=10, window_s=3600)
async def redeem(
    payload: RedeemIn,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
) -> RedeemOut:
    """L'utilisateur connecté consomme son code et passe en plan 'beta' (trial étendu J+90)."""
    try:
        inv = batches.redeem(session, code=payload.code.strip().upper(), user_id=user.id)
    except InvitationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    grant_beta_plan(session, user_id=user.id, source_batch=inv.batch_number)
    return RedeemOut(ok=True, batch_number=inv.batch_number, plan_granted="beta")


class IssueBatchIn(BaseModel):
    batch_number: int = Field(ge=1, le=4)


class IssueBatchOut(BaseModel):
    ok: bool
    issued: int
    batch_number: int


@router.post("/admin/issue", response_model=IssueBatchOut, dependencies=[Depends(require_admin)])
async def admin_issue_batch(
    payload: IssueBatchIn,
    session: Session = Depends(get_session),
) -> IssueBatchOut:
    """Admin-only : déclenche l'émission d'un batch."""
    issued = batches.issue_batch(session, batch_number=payload.batch_number)
    # Envoi email asynchrone hors de cette route (queue Arq / Celery)
    return IssueBatchOut(ok=True, issued=len(issued), batch_number=payload.batch_number)


@router.get("/admin/stats", dependencies=[Depends(require_admin)])
async def admin_stats(session: Session = Depends(get_session)) -> list[dict]:
    return batches.batch_stats(session)
