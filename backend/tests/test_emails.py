"""Tests emails transactionnels — MemoryEmailProvider capture les envois."""

from __future__ import annotations

from datetime import UTC

import pytest

from pli.emails.provider import MemoryEmailProvider, get_email_provider, reset_provider_for_tests
from pli.emails.sender import (
    send_invoice_email,
    send_password_reset_email,
    send_trial_reminder_email,
    send_verification_email,
)


@pytest.fixture(autouse=True)
def _reset_provider(monkeypatch):
    from pli.config import settings

    monkeypatch.setattr(settings, "email_provider", "memory")
    reset_provider_for_tests()
    yield
    reset_provider_for_tests()


@pytest.fixture
def outbox() -> MemoryEmailProvider:
    return get_email_provider()  # type: ignore[return-value]


@pytest.mark.asyncio
async def test_send_verification_email(outbox: MemoryEmailProvider):
    msg_id = await send_verification_email(to="alice@example.com", token="tok123")
    assert msg_id and msg_id.startswith("mem-")
    assert len(outbox.outbox) == 1
    sent = outbox.outbox[0]
    assert sent.to == "alice@example.com"
    assert sent.template == "verify"
    assert "tok123" in sent.context["verify_url"]


@pytest.mark.asyncio
async def test_send_password_reset_email(outbox: MemoryEmailProvider):
    await send_password_reset_email(to="bob@example.com", token="reset456")
    assert len(outbox.outbox) == 1
    assert outbox.outbox[0].template == "password_reset"
    assert "reset456" in outbox.outbox[0].context["reset_url"]


@pytest.mark.asyncio
async def test_send_trial_reminder_singular(outbox: MemoryEmailProvider):
    await send_trial_reminder_email(to="carol@example.com", days_left=1)
    assert "demain" in outbox.outbox[0].subject


@pytest.mark.asyncio
async def test_send_trial_reminder_plural(outbox: MemoryEmailProvider):
    await send_trial_reminder_email(to="carol@example.com", days_left=3)
    assert "3 jours" in outbox.outbox[0].subject


@pytest.mark.asyncio
async def test_send_invoice_email(outbox: MemoryEmailProvider):
    from datetime import datetime

    await send_invoice_email(
        to="dan@example.com",
        plan="PLI Plus — annuel",
        amount="95,88 €",
        paid_at=datetime(2026, 7, 15, tzinfo=UTC),
        invoice_number="INV-2026-0042",
        invoice_url="https://pay.example.com/inv/42",
        next_charge_at=datetime(2027, 7, 15, tzinfo=UTC),
    )
    sent = outbox.outbox[0]
    assert sent.template == "invoice"
    assert "INV-2026-0042" in sent.subject
    assert sent.context["amount"] == "95,88 €"
