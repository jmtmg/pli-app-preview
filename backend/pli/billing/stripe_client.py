"""Wrapper fin autour du SDK Stripe. Permet de stubber en test."""

from __future__ import annotations

from typing import Any

import structlog

from ..config import settings

log = structlog.get_logger()


class StripeClient:
    """Wrapper. L'appelant passe uniquement des arguments métier PLI."""

    def __init__(self, secret_key: str | None = None, webhook_secret: str | None = None) -> None:
        self._secret_key = secret_key
        self._webhook_secret = webhook_secret
        self._stripe: Any = None  # lazy import, allow local-mode tests without stripe installed

    def _require(self) -> Any:
        if self._stripe is None:
            import stripe  # type: ignore

            stripe.api_key = self._secret_key
            stripe.api_version = "2024-06-20"
            self._stripe = stripe
        if not self._secret_key:
            raise RuntimeError("PLI_STRIPE_SECRET_KEY manquante")
        return self._stripe

    # -------------------------------------------------------------- checkout

    def create_checkout_session(
        self,
        *,
        user_id: str,
        tenant_id: str,
        email: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
        trial_days: int | None = None,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        stripe = self._require()
        params: dict[str, Any] = {
            "mode": "subscription",
            "payment_method_types": ["card"],
            "customer_email": email,
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": success_url,
            "cancel_url": cancel_url,
            # Toutes les infos PLI côté metadata (jamais PII côté line_items)
            "metadata": {
                "pli_user_id": user_id,
                "pli_tenant_id": tenant_id,
            },
            "subscription_data": {
                "metadata": {
                    "pli_user_id": user_id,
                    "pli_tenant_id": tenant_id,
                },
            },
            "allow_promotion_codes": True,
        }
        if trial_days and trial_days > 0:
            params["subscription_data"]["trial_period_days"] = trial_days
        session = stripe.checkout.Session.create(
            **params,
            idempotency_key=idempotency_key,
        )
        log.info("stripe_checkout_created", user_id=user_id, session_id=session["id"])
        return session

    # -------------------------------------------------------------- portal

    def create_billing_portal_session(
        self,
        *,
        stripe_customer_id: str,
        return_url: str,
    ) -> dict[str, Any]:
        stripe = self._require()
        session = stripe.billing_portal.Session.create(
            customer=stripe_customer_id,
            return_url=return_url,
        )
        return session

    # -------------------------------------------------------------- webhook

    def construct_event(self, *, payload: bytes, sig_header: str) -> dict[str, Any]:
        """Vérifie la signature + parse l'event. Lève si invalide."""
        stripe = self._require()
        if not self._webhook_secret:
            raise RuntimeError("PLI_STRIPE_WEBHOOK_SECRET manquant")
        return stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=self._webhook_secret,
        )


_client: StripeClient | None = None


def get_stripe_client() -> StripeClient:
    global _client
    if _client is None:
        _client = StripeClient(
            secret_key=(
                settings.stripe_secret_key.get_secret_value()
                if settings.stripe_secret_key
                else None
            ),
            webhook_secret=(
                settings.stripe_webhook_secret.get_secret_value()
                if settings.stripe_webhook_secret
                else None
            ),
        )
    return _client


def reset_stripe_client_for_tests() -> None:
    global _client
    _client = None
