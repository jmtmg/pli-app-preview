"""Routes HTTP /licenses — émission (cloud) + activation (local).

- POST /licenses/issue   (cloud)  : body { email } → { payload, sig }
  L'appelant doit être authentifié ET avoir un abonnement plus actif.

- POST /licenses/activate (local) : body { payload, sig } → { plan, expires_at }
  Vérifie la signature contre la clé publique embarquée et persiste
  dans ~/.pli/license.json. Aucun contact réseau requis.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr

from ..adapters.base import Principal
from ..billing.subscriptions import get_subscription_by_user
from ..config import settings
from ..licensing.local_key import (
    LICENSE_VERSION,
    issue_local_license,
    load_license,
    save_license,
    verify_license,
)
from ..tenancy.context import current_principal

router = APIRouter(prefix="/licenses", tags=["licenses"])


# ---------------------------------------------------------------------------
# Cloud — émission d'une licence offline
# ---------------------------------------------------------------------------


class IssueRequest(BaseModel):
    email: EmailStr


class IssueResponse(BaseModel):
    payload: str
    sig: str
    version: int = LICENSE_VERSION


@router.post("/issue", response_model=IssueResponse)
async def issue_license(
    body: IssueRequest,
    principal: Annotated[Principal, Depends(current_principal)],
):
    if settings.mode != "cloud":
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    if not settings.license_signing_key:
        raise HTTPException(500, "PLI_LICENSE_SIGNING_KEY non configurée")

    # L'abonnement doit être actif (ou trial) pour qu'on émette une licence
    sub = await get_subscription_by_user(principal.tenant_id, principal.user_id)
    if not sub or sub["plan"] == "free":
        raise HTTPException(403, "Aucun abonnement PLI Plus actif")

    blob = issue_local_license(
        email=body.email,
        plan=sub["plan"],
        valid_until=sub.get("current_period_end"),
        signing_key_b64=settings.license_signing_key.get_secret_value(),
    )
    return IssueResponse(**blob)


# ---------------------------------------------------------------------------
# Local — activation offline
# ---------------------------------------------------------------------------


class ActivateRequest(BaseModel):
    payload: str
    sig: str
    email: EmailStr | None = None  # vérification optionnelle


class ActivateResponse(BaseModel):
    plan: str
    issued_at: str
    expires_at: str | None


# Clé publique embarquée (générée lors du build — ici fallback settings)
EMBEDDED_PUBLIC_KEY_B64 = ""  # TODO: remplir au build via env PLI_LICENSE_PUBLIC_KEY


@router.post("/activate", response_model=ActivateResponse)
async def activate_license(body: ActivateRequest):
    if settings.mode != "local":
        raise HTTPException(status.HTTP_404_NOT_FOUND)

    import os

    public_key = EMBEDDED_PUBLIC_KEY_B64 or os.environ.get("PLI_LICENSE_PUBLIC_KEY", "")
    if not public_key:
        raise HTTPException(500, "Clé publique de licence non configurée")

    try:
        lic = verify_license(
            {"payload": body.payload, "sig": body.sig},
            public_key_b64=public_key,
            expected_email=str(body.email) if body.email else None,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    if lic.is_expired():
        raise HTTPException(400, "Cette licence est expirée")

    save_license({"payload": body.payload, "sig": body.sig})
    return ActivateResponse(
        plan=lic.plan,
        issued_at=lic.issued_at,
        expires_at=lic.expires_at,
    )


@router.get("/status", response_model=ActivateResponse | None)
async def license_status():
    """Renvoie l'état courant de la licence locale."""
    if settings.mode != "local":
        return None
    blob = load_license()
    if not blob:
        return None
    import os

    public_key = EMBEDDED_PUBLIC_KEY_B64 or os.environ.get("PLI_LICENSE_PUBLIC_KEY", "")
    if not public_key:
        return None
    try:
        lic = verify_license(blob, public_key_b64=public_key)
    except ValueError:
        return None
    return ActivateResponse(
        plan=lic.plan,
        issued_at=lic.issued_at,
        expires_at=lic.expires_at,
    )
