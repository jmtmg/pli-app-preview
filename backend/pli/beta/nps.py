"""Agrégation Net Promoter Score pour la beta privée.

Règles :
- Score 9-10 → Promoteur
- Score 7-8  → Passif
- Score 0-6  → Détracteur
- NPS = %Promoteurs − %Détracteurs (entier signé -100..+100)
- Les réponses anonymes (user_id_hash=NULL) sont incluses
- Dédoublonnage : 1 réponse par (user_id_hash, created_at_week) — dernière prévaut
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from pli.db.models import FeedbackSubmission


@dataclass(frozen=True)
class NPSResult:
    respondents: int
    promoters: int
    passives: int
    detractors: int
    score: int
    mean_score: float


def _classify(score: int) -> str:
    if score >= 9:
        return "promoter"
    if score >= 7:
        return "passive"
    return "detractor"


def compute(
    session: Session,
    *,
    batch_number: int | None = None,
    since: datetime | None = None,
) -> NPSResult:
    stmt = select(FeedbackSubmission.score).where(
        FeedbackSubmission.kind == "nps",
        FeedbackSubmission.score.is_not(None),
    )
    if batch_number is not None:
        stmt = stmt.where(FeedbackSubmission.batch_number == batch_number)
    if since is not None:
        stmt = stmt.where(FeedbackSubmission.created_at >= since)

    scores = [int(s) for (s,) in session.execute(stmt).all()]
    total = len(scores)
    if total == 0:
        return NPSResult(0, 0, 0, 0, 0, 0.0)

    buckets = {"promoter": 0, "passive": 0, "detractor": 0}
    for s in scores:
        buckets[_classify(s)] += 1

    nps = round((buckets["promoter"] - buckets["detractor"]) / total * 100)
    return NPSResult(
        respondents=total,
        promoters=buckets["promoter"],
        passives=buckets["passive"],
        detractors=buckets["detractor"],
        score=nps,
        mean_score=sum(scores) / total,
    )


def rolling_7d(session: Session) -> NPSResult:
    since = datetime.now(UTC) - timedelta(days=7)
    return compute(session, since=since)


def per_batch(session: Session) -> list[NPSResult]:
    out: list[NPSResult] = []
    for b in (1, 2, 3, 4):
        out.append(compute(session, batch_number=b))
    return out


def trend_detractor_comments(session: Session, limit: int = 20) -> list[dict]:
    """Renvoie les N derniers commentaires de détracteurs (pour triage PM)."""
    rows = session.execute(
        select(
            FeedbackSubmission.score,
            FeedbackSubmission.message,
            FeedbackSubmission.app_version,
            FeedbackSubmission.batch_number,
            FeedbackSubmission.created_at,
        )
        .where(
            FeedbackSubmission.kind == "nps",
            FeedbackSubmission.score.is_not(None),
            FeedbackSubmission.score <= 6,
            FeedbackSubmission.message.is_not(None),
        )
        .order_by(FeedbackSubmission.created_at.desc())
        .limit(limit)
    ).all()
    return [
        {
            "score": r.score,
            "message": r.message,
            "app_version": r.app_version,
            "batch": r.batch_number,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]
