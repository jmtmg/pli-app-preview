"""API Waitlist publique (pli.app/waitlist)."""

from __future__ import annotations

import re
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from pli.db.models import WaitlistEntry
from pli.db.session import get_session
from pli.emails.provider import send_double_optin
from pli.security.rate_limit import rate_limit
from pli.security.tokens import sign_token, verify_token

router = APIRouter(prefix="/waitlist", tags=["waitlist"])

_SEGMENTS = {"gmail_only", "ms_only", "mixed", "non_tech", "unknown"}
_EMAIL_DOMAIN_RE = re.compile(r"@([a-z0-9.-]+\.[a-z]{2,})$", re.IGNORECASE)


class WaitlistIn(BaseModel):
    email: EmailStr
    first_name: str | None = Field(default=None, max_length=100)
    motivation: str | None = Field(default=None, max_length=280)
    source: str | None = Field(default=None, max_length=40)


class WaitlistOut(BaseModel):
    ok: bool
    message: str


def _guess_segment(email: str, motivation: str | None) -> str:
    m = _EMAIL_DOMAIN_RE.search(email)
    domain = m.group(1).lower() if m else ""
    text = (motivation or "").lower()
    gmail_like = {"gmail.com", "googlemail.com"}
    ms_like = {"outlook.com", "outlook.fr", "hotmail.com", "hotmail.fr", "live.com", "msn.com"}
    if domain in gmail_like and "outlook" not in text and "microsoft" not in text:
        return "gmail_only"
    if domain in ms_like and "gmail" not in text:
        return "ms_only"
    if "gmail" in text and ("outlook" in text or "microsoft" in text):
        return "mixed"
    return "unknown"


@router.post("", response_model=WaitlistOut, status_code=status.HTTP_201_CREATED)
@rate_limit("waitlist_post", limit=5, window_s=3600)
async def subscribe(
    payload: WaitlistIn,
    request: Request,
    session: Session = Depends(get_session),
) -> WaitlistOut:
    """Inscription waitlist avec double opt-in email."""
    existing = session.execute(
        select(WaitlistEntry).where(WaitlistEntry.email == payload.email)
    ).scalar_one_or_none()

    if existing is None:
        entry = WaitlistEntry(
            email=payload.email,
            first_name=payload.first_name,
            motivation=payload.motivation,
            source=payload.source,
            segment=_guess_segment(payload.email, payload.motivation),
        )
        session.add(entry)
        session.flush()
    else:
        entry = existing

    # Idempotent : si déjà confirmé, on ne relance pas l'email
    if entry.confirmed_at is None:
        token = sign_token({"wid": entry.id, "purpose": "waitlist_confirm"}, ttl_days=7)
        await send_double_optin(email=payload.email, first_name=payload.first_name, token=token)

    return WaitlistOut(
        ok=True,
        message="Merci — un email de confirmation vient d'arriver. Clique pour valider.",
    )


@router.get("/confirm/{token}", response_model=WaitlistOut)
async def confirm(token: str, session: Session = Depends(get_session)) -> WaitlistOut:
    """Confirmation double opt-in via lien email."""
    data = verify_token(token, expected_purpose="waitlist_confirm")
    if data is None:
        raise HTTPException(status_code=400, detail="lien invalide ou expiré")

    entry = session.get(WaitlistEntry, data["wid"])
    if entry is None:
        raise HTTPException(status_code=404, detail="inscription introuvable")

    if entry.confirmed_at is None:
        entry.confirmed_at = datetime.now(UTC)
        session.flush()

    return WaitlistOut(
        ok=True, message="Inscription confirmée. Tu recevras un code dès le prochain batch."
    )
