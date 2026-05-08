"""Plans PLI — mapping vers les status Stripe et les price IDs."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from ..config import settings


class Plan(str, Enum):
    FREE = "free"
    PLUS_TRIAL = "plus_trial"
    PLUS_MONTHLY = "plus_monthly"
    PLUS_YEARLY = "plus_yearly"

    @property
    def is_paid(self) -> bool:
        return self in (Plan.PLUS_MONTHLY, Plan.PLUS_YEARLY)

    @property
    def is_plus(self) -> bool:
        return self != Plan.FREE


def get_plan_from_price_id(price_id: str | None) -> Plan:
    """Retourne le plan PLI correspondant à un Stripe Price ID."""
    if not price_id:
        return Plan.FREE
    if price_id == settings.stripe_price_monthly:
        return Plan.PLUS_MONTHLY
    if price_id == settings.stripe_price_yearly:
        return Plan.PLUS_YEARLY
    return Plan.FREE


StripeStatus = Literal[
    "trialing",
    "active",
    "past_due",
    "canceled",
    "unpaid",
    "incomplete",
    "incomplete_expired",
    "paused",
]


def plan_from_subscription_status(
    *,
    status: StripeStatus,
    price_id: str | None,
) -> Plan:
    """Dérive le plan PLI en fonction du status Stripe ET du price.

    Règle produit :
      - trialing        → plus_trial (même si price = yearly)
      - active          → plus_monthly OU plus_yearly
      - past_due        → on laisse encore les privilèges plus (grace period)
      - canceled/unpaid → free
      - incomplete*     → free (paiement jamais abouti)
    """
    if status == "trialing":
        return Plan.PLUS_TRIAL
    if status == "active" or status == "past_due":
        return get_plan_from_price_id(price_id)
    return Plan.FREE
