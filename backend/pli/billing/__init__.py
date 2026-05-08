"""Billing — Stripe Checkout + webhooks idempotents (cloud mode only).

L'intégralité du module est no-op en mode local : les endpoints /billing/*
répondent 404 si settings.mode != "cloud".
"""

from .plans import Plan, get_plan_from_price_id, plan_from_subscription_status
from .stripe_client import StripeClient, get_stripe_client

__all__ = [
    "Plan",
    "StripeClient",
    "get_plan_from_price_id",
    "get_stripe_client",
    "plan_from_subscription_status",
]
