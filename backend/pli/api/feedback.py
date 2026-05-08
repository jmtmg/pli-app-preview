"""API Feedback in-app — NPS + signalements qualitatifs.

PII / RGPD :
- Pas d'IP stockée
- user_id haché (sha256 + salt env) avant persistance
- Option "anonymous=true" → user_id_hash=NULL
- Rate-limit 3 submissions / heure / user
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from pli.auth.dependencies import current_user, require_admin
from pli.beta import nps
from pli.db.models import FeedbackSubmission, User
from pli.db.session import get_session
from pli.security.hashing import user_hash
from pli.security.rate_limit import rate_limit

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackIn(BaseModel):
    kind: Literal["nps", "bug", "suggestion", "other"]
    score: int | None = Field(default=None, ge=0, le=10)
    message: str | None = Field(default=None, max_length=2000)
    app_version: str | None = Field(default=None, max_length=20)
    platform: Literal["pwa-mobile", "pwa-desktop"] | None = None
    anonymous: bool = False


class FeedbackOut(BaseModel):
    ok: bool
    id: int


@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
@rate_limit("feedback_post", limit=3, window_s=3600)
async def submit(
    payload: FeedbackIn,
    request: Request,
    user: User = Depends(current_user),
    session: Session = Depends(get_session),
) -> FeedbackOut:
    # Garde-fou : NPS → score obligatoire
    if payload.kind == "nps" and payload.score is None:
        raise HTTPException(status_code=400, detail="score requis pour kind=nps")
    if payload.kind != "nps" and payload.score is not None:
        payload.score = None

    # Compute days since signup
    days_since = (datetime.now(UTC) - user.created_at).days if user.created_at else None

    submission = FeedbackSubmission(
        user_id_hash=None if payload.anonymous else user_hash(user.id),
        kind=payload.kind,
        score=payload.score,
        message=payload.message,
        app_version=payload.app_version,
        platform=payload.platform,
        days_since_signup=days_since,
        batch_number=user.batch_number,
    )
    session.add(submission)
    session.flush()

    return FeedbackOut(ok=True, id=submission.id)


@router.get("/admin/nps", dependencies=[Depends(require_admin)])
async def admin_nps(session: Session = Depends(get_session)) -> dict:
    global_nps = nps.compute(session)
    rolling = nps.rolling_7d(session)
    by_batch = nps.per_batch(session)
    return {
        "global": global_nps.__dict__,
        "rolling_7d": rolling.__dict__,
        "by_batch": [r.__dict__ for r in by_batch],
        "detractor_comments": nps.trend_detractor_comments(session, limit=20),
    }
