"""Tests du dispatcher webhook Stripe — idempotence + plan computation.

On stubbe complètement le SDK Stripe (les events sont fabriqués à la main)
et on remplace `_record_event` pour simuler la dé-duplication sans PG.
"""

from __future__ import annotations

import pytest

from pli.billing.plans import Plan, plan_from_subscription_status

# ---------------------------------------------------------------------------
# plans.py — unités pures
# ---------------------------------------------------------------------------


class TestPlanComputation:
    def test_trialing_always_trial(self, monkeypatch):
        from pli.config import settings

        monkeypatch.setattr(settings, "stripe_price_yearly", "price_year")
        assert (
            plan_from_subscription_status(status="trialing", price_id="price_year")
            == Plan.PLUS_TRIAL
        )

    def test_active_monthly(self, monkeypatch):
        from pli.config import settings

        monkeypatch.setattr(settings, "stripe_price_monthly", "price_m")
        monkeypatch.setattr(settings, "stripe_price_yearly", "price_y")
        assert (
            plan_from_subscription_status(status="active", price_id="price_m") == Plan.PLUS_MONTHLY
        )

    def test_active_yearly(self, monkeypatch):
        from pli.config import settings

        monkeypatch.setattr(settings, "stripe_price_monthly", "price_m")
        monkeypatch.setattr(settings, "stripe_price_yearly", "price_y")
        assert (
            plan_from_subscription_status(status="active", price_id="price_y") == Plan.PLUS_YEARLY
        )

    def test_past_due_keeps_plan(self, monkeypatch):
        from pli.config import settings

        monkeypatch.setattr(settings, "stripe_price_monthly", "price_m")
        # Grace period: on ne rétrograde pas immédiatement
        assert (
            plan_from_subscription_status(status="past_due", price_id="price_m")
            == Plan.PLUS_MONTHLY
        )

    def test_canceled_free(self):
        assert plan_from_subscription_status(status="canceled", price_id="price_m") == Plan.FREE

    def test_incomplete_free(self):
        assert plan_from_subscription_status(status="incomplete", price_id="price_m") == Plan.FREE


# ---------------------------------------------------------------------------
# webhooks.py — dispatcher idempotent
# ---------------------------------------------------------------------------


class FakeEventStore:
    def __init__(self) -> None:
        self.seen: set[str] = set()
        self.handled: list[str] = []

    async def record(self, event_id: str, event_type: str) -> bool:
        if event_id in self.seen:
            return False
        self.seen.add(event_id)
        return True


@pytest.fixture
def store(monkeypatch):
    s = FakeEventStore()
    from pli.billing import webhooks

    monkeypatch.setattr(webhooks, "_record_event", s.record)
    return s


@pytest.fixture
def no_handlers(monkeypatch):
    """Neutralise les handlers métier — on teste que la plomberie."""
    from pli.billing import webhooks

    async def noop(_event):
        return None

    monkeypatch.setitem(webhooks._HANDLERS, "checkout.session.completed", noop)
    monkeypatch.setitem(webhooks._HANDLERS, "customer.subscription.updated", noop)


def _event(event_id: str, event_type: str, obj: dict | None = None) -> dict:
    return {
        "id": event_id,
        "type": event_type,
        "data": {"object": obj or {}},
    }


@pytest.mark.asyncio
async def test_handle_event_idempotent(store, no_handlers):
    from pli.billing.webhooks import handle_event

    evt = _event(
        "evt_1",
        "checkout.session.completed",
        {"id": "cs_1", "metadata": {"pli_tenant_id": "t", "pli_user_id": "u"}},
    )
    await handle_event(evt)
    await handle_event(evt)  # 2e passage = no-op
    assert store.seen == {"evt_1"}


@pytest.mark.asyncio
async def test_unknown_event_type_is_ignored(store):
    from pli.billing.webhooks import handle_event

    evt = _event("evt_x", "unknown.type")
    await handle_event(evt)  # ne lève pas
    assert "evt_x" in store.seen
