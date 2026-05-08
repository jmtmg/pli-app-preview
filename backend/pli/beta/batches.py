"""Génération et émission des batches d'invitation beta.

Règle M4 :
- 4 batches × 25 codes = 100 invitations
- Codes uniques, 12 caractères base32 sans ambiguïtés (0/O, 1/I)
- Expiration 14 jours
- Chaque batch mélange les segments (gmail_only, ms_only, mixed, non_tech)
  pour limiter le biais early-adopters.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from pli.db.models import Invitation, WaitlistEntry

# base32 sans caractères ambigus
_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
BATCH_SIZE = 25
EXPIRY_DAYS = 14
TARGET_BATCHES = 4
SEGMENT_QUOTA = {
    "gmail_only": 7,
    "ms_only": 7,
    "mixed": 6,
    "non_tech": 5,
}
# somme = 25


@dataclass(frozen=True)
class InvitationIssued:
    code: str
    email: str
    batch_number: int
    expires_at: datetime


def generate_code(length: int = 12) -> str:
    """Génère un code robuste (entropie ~57 bits pour 12 chars)."""
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


def pick_batch_candidates(session: Session, batch_number: int) -> list[WaitlistEntry]:
    """Sélectionne 25 candidats waitlist selon les quotas segment.

    Règles :
    - Uniquement les entrées confirmées (double opt-in)
    - Pas encore invitées
    - FIFO par date d'inscription à l'intérieur d'un segment
    - Si un segment est sous-quota, on bouche avec les "unknown"/premier arrivé
    """
    selected: list[WaitlistEntry] = []
    taken_ids: set[int] = set()

    for segment, quota in SEGMENT_QUOTA.items():
        rows = (
            session.execute(
                select(WaitlistEntry)
                .where(
                    WaitlistEntry.segment == segment,
                    WaitlistEntry.confirmed_at.is_not(None),
                    WaitlistEntry.invited_at.is_(None),
                )
                .order_by(WaitlistEntry.confirmed_at.asc())
                .limit(quota)
            )
            .scalars()
            .all()
        )
        selected.extend(rows)
        taken_ids.update(r.id for r in rows)

    # Bouche-trous si segments vides
    remaining = BATCH_SIZE - len(selected)
    if remaining > 0:
        filler = (
            session.execute(
                select(WaitlistEntry)
                .where(
                    WaitlistEntry.confirmed_at.is_not(None),
                    WaitlistEntry.invited_at.is_(None),
                    ~WaitlistEntry.id.in_(taken_ids or {0}),
                )
                .order_by(WaitlistEntry.confirmed_at.asc())
                .limit(remaining)
            )
            .scalars()
            .all()
        )
        selected.extend(filler)

    if len(selected) < BATCH_SIZE:
        raise ValueError(
            f"Batch #{batch_number} impossible : {len(selected)} candidats, besoin de {BATCH_SIZE}. "
            "Élargir la waitlist ou ajuster les quotas."
        )
    return selected[:BATCH_SIZE]


def issue_batch(
    session: Session, batch_number: int, now: datetime | None = None
) -> list[InvitationIssued]:
    """Émet un batch complet : génère codes + persiste Invitation + marque waitlist."""
    if not 1 <= batch_number <= TARGET_BATCHES:
        raise ValueError(f"batch_number doit être dans 1..{TARGET_BATCHES}")

    now = now or datetime.now(UTC)
    expires_at = now + timedelta(days=EXPIRY_DAYS)

    candidates = pick_batch_candidates(session, batch_number)
    issued: list[InvitationIssued] = []

    for cand in candidates:
        code = generate_code()
        inv = Invitation(
            code=code,
            batch_number=batch_number,
            waitlist_id=cand.id,
            email=cand.email,
            expires_at=expires_at,
        )
        cand.invited_at = now
        session.add(inv)
        issued.append(
            InvitationIssued(
                code=code,
                email=cand.email,
                batch_number=batch_number,
                expires_at=expires_at,
            )
        )

    session.flush()
    return issued


def redeem(session: Session, code: str, user_id: int, now: datetime | None = None) -> Invitation:
    """Consomme un code d'invitation pour activer un user beta."""
    now = now or datetime.now(UTC)
    inv = session.execute(select(Invitation).where(Invitation.code == code)).scalar_one_or_none()

    if inv is None:
        raise InvitationError("code inconnu")
    if inv.redeemed_at is not None:
        raise InvitationError("code déjà utilisé")
    if inv.expires_at <= now:
        raise InvitationError("code expiré")

    inv.redeemed_at = now
    inv.redeemed_by_user_id = user_id
    session.flush()
    return inv


def batch_stats(session: Session) -> list[dict]:
    """Stats par batch pour dashboard admin."""
    from sqlalchemy import func

    rows = session.execute(
        select(
            Invitation.batch_number,
            func.count(Invitation.id).label("total"),
            func.sum(func.case((Invitation.redeemed_at.is_not(None), 1), else_=0)).label(
                "redeemed"
            ),
            func.sum(func.case((Invitation.expires_at <= func.now(), 1), else_=0)).label("expired"),
        )
        .group_by(Invitation.batch_number)
        .order_by(Invitation.batch_number)
    ).all()

    return [
        {
            "batch": r.batch_number,
            "issued": int(r.total or 0),
            "redeemed": int(r.redeemed or 0),
            "expired": int(r.expired or 0),
            "conversion": (float(r.redeemed or 0) / float(r.total or 1)) if r.total else 0.0,
        }
        for r in rows
    ]


class InvitationError(Exception):
    """Erreur métier sur une invitation (inconnu, expiré, consommé)."""
