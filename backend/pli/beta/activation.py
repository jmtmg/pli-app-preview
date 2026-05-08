"""Suivi des événements d'activation et calcul rétention J1/J7/J30.

Événements canoniques dans l'ordre idéal :
    signup → email_verified → oauth_connected → first_sync → tour_completed → first_send

Un user est considéré "activé" dès qu'il atteint `first_sync` ET `tour_completed`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from pli.db.models import ActivationEvent

ACTIVATION_EVENTS = (
    "signup",
    "email_verified",
    "oauth_connected",
    "first_sync",
    "tour_completed",
    "first_send",
)

ACTIVATED_THRESHOLD = {"first_sync", "tour_completed"}


@dataclass(frozen=True)
class RetentionSnapshot:
    batch_number: int
    cohort_size: int
    j1: float
    j7: float
    j30: float


def record(session: Session, user_id: int, event: str, batch_number: int | None = None) -> None:
    """Enregistre un événement d'activation, idempotent par (user_id, event)."""
    if event not in ACTIVATION_EVENTS:
        raise ValueError(f"Événement inconnu : {event}")

    existing = session.execute(
        select(ActivationEvent).where(
            ActivationEvent.user_id == user_id,
            ActivationEvent.event == event,
        )
    ).scalar_one_or_none()
    if existing is not None:
        return

    session.add(ActivationEvent(user_id=user_id, event=event, batch_number=batch_number))
    session.flush()


def is_activated(session: Session, user_id: int) -> bool:
    """Activé = first_sync + tour_completed."""
    rows = (
        session.execute(
            select(ActivationEvent.event).where(
                ActivationEvent.user_id == user_id,
                ActivationEvent.event.in_(ACTIVATED_THRESHOLD),
            )
        )
        .scalars()
        .all()
    )
    return ACTIVATED_THRESHOLD.issubset(set(rows))


def activation_funnel(session: Session, batch_number: int | None = None) -> dict[str, int]:
    """Funnel comptant les users ayant atteint chaque étape."""
    stmt = select(ActivationEvent.event, func.count(func.distinct(ActivationEvent.user_id)))
    if batch_number is not None:
        stmt = stmt.where(ActivationEvent.batch_number == batch_number)
    stmt = stmt.group_by(ActivationEvent.event)
    rows = session.execute(stmt).all()
    counts = {event: 0 for event in ACTIVATION_EVENTS}
    for event, n in rows:
        counts[event] = int(n)
    return counts


def retention(session: Session, batch_number: int) -> RetentionSnapshot:
    """Retour Rétention J1/J7/J30 pour un batch.

    Un user est "retenu à J+N" s'il a au moins un événement d'activation
    (autre que signup/email_verified) au-delà de J+N jours après son signup.
    """
    now = datetime.now(UTC)

    signups = session.execute(
        select(ActivationEvent.user_id, ActivationEvent.created_at).where(
            ActivationEvent.event == "signup",
            ActivationEvent.batch_number == batch_number,
        )
    ).all()

    cohort = {user_id: signup_at for user_id, signup_at in signups}
    cohort_size = len(cohort)
    if cohort_size == 0:
        return RetentionSnapshot(batch_number, 0, 0.0, 0.0, 0.0)

    # Events post-signup hors signup/email_verified
    actions = session.execute(
        select(ActivationEvent.user_id, ActivationEvent.created_at).where(
            ActivationEvent.batch_number == batch_number,
            ActivationEvent.event.notin_({"signup", "email_verified"}),
        )
    ).all()

    retained = {1: set(), 7: set(), 30: set()}
    for user_id, action_at in actions:
        signup_at = cohort.get(user_id)
        if signup_at is None:
            continue
        delta_days = (action_at - signup_at).total_seconds() / 86400
        for threshold in (1, 7, 30):
            if delta_days >= threshold and now - action_at <= timedelta(days=60):
                retained[threshold].add(user_id)

    return RetentionSnapshot(
        batch_number=batch_number,
        cohort_size=cohort_size,
        j1=len(retained[1]) / cohort_size,
        j7=len(retained[7]) / cohort_size,
        j30=len(retained[30]) / cohort_size,
    )
