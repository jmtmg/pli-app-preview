"""Routes HTTP /billing — cloud uniquement."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field

from ..adapters.base import Principal
from ..billing.stripe_client import get_stripe_client
from ..billing.subscriptions import get_subscription_by_user
from ..billing.webhooks import handle_event
from ..config import settings
from ..tenancy.context import current_principal

router = APIRouter(prefix="/billing", tags=["billing"])


def _require_cloud() -> None:
    if settings.mode != "cloud":
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, "Billing disponible en mode Cloud uniquement"
        )


class CheckoutRequest(BaseModel):
    plan: str = Field(pattern="^(monthly|yearly)$")
    success_url: str | None = None
    cancel_url: str | None = None


class CheckoutResponse(BaseModel):
    url: str
    session_id: str


@router.post("/checkout", response_model=CheckoutResponse)
async def create_checkout(
    body: CheckoutRequest,
    principal: Annotated[Principal, Depends(current_principal)],
):
    _require_cloud()
    price_id = (
        settings.stripe_price_monthly if body.plan == "monthly" else settings.stripe_price_yearly
    )
    if not price_id:
        raise HTTPException(500, f"PLI_STRIPE_PRICE_{body.plan.upper()} non configuré")
    success_url = body.success_url or f"{settings.app_url}/settings/billing?status=success"
    cancel_url = body.cancel_url or f"{settings.app_url}/settings/billing?status=cancel"
    if not principal.email:
        raise HTTPException(400, "Email manquant sur le compte")
    session = get_stripe_client().create_checkout_session(
        user_id=principal.user_id,
        tenant_id=principal.tenant_id,
        email=principal.email,
        price_id=price_id,
        success_url=success_url,
        cancel_url=cancel_url,
        trial_days=settings.stripe_trial_days if settings.stripe_trial_days > 0 else None,
        idempotency_key=f"checkout:{principal.user_id}:{body.plan}",
    )
    return CheckoutResponse(url=session["url"], session_id=session["id"])


class PortalResponse(BaseModel):
    url: str


@router.post("/portal", response_model=PortalResponse)
async def open_portal(
    principal: Annotated[Principal, Depends(current_principal)],
):
    _require_cloud()
    sub = await get_subscription_by_user(principal.tenant_id, principal.user_id)
    if not sub or not sub.get("stripe_customer_id"):
        raise HTTPException(400, "Aucun abonnement actif")
    session = get_stripe_client().create_billing_portal_session(
        stripe_customer_id=sub["stripe_customer_id"],
        return_url=f"{settings.app_url}/settings/billing",
    )
    return PortalResponse(url=session["url"])


class SubscriptionResponse(BaseModel):
    plan: str
    status: str
    current_period_end: str | None
    trial_end: str | None
    cancel_at_period_end: bool


@router.get("/subscription", response_model=SubscriptionResponse | None)
async def get_my_subscription(
    principal: Annotated[Principal, Depends(current_principal)],
):
    _require_cloud()
    sub = await get_subscription_by_user(principal.tenant_id, principal.user_id)
    if not sub:
        return None
    return SubscriptionResponse(
        plan=sub["plan"],
        status=sub["status"],
        current_period_end=sub["current_period_end"].isoformat()
        if sub.get("current_period_end")
        else None,
        trial_end=sub["trial_end"].isoformat() if sub.get("trial_end") else None,
        cancel_at_period_end=bool(sub.get("cancel_at_period_end")),
    )


# ---------------------------------------------------------------------------
# Webhook Stripe — pas d'auth PLI, signature vérifiée par Stripe
# ---------------------------------------------------------------------------


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request):
    _require_cloud()
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature", "")
    if not sig:
        raise HTTPException(400, "Missing Stripe-Signature header")
    try:
        event = get_stripe_client().construct_event(payload=payload, sig_header=sig)
    except Exception as exc:  # ValueError OR SignatureVerificationError
        raise HTTPException(400, f"Invalid Stripe signature: {exc}") from exc
    await handle_event(event)
    return {"received": True}
