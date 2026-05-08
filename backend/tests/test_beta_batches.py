"""Tests des batches d'invitation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from pli.beta import batches
from pli.beta.batches import InvitationError


def test_generate_code_unique_and_alphabet():
    codes = {batches.generate_code() for _ in range(500)}
    assert len(codes) == 500, "collisions générées → entropie insuffisante"
    assert all(len(c) == 12 for c in codes)
    # pas de caractères ambigus
    forbidden = set("0O1Il")
    assert not any(ch in forbidden for c in codes for ch in c)


def test_issue_batch_respects_quota(db_session, waitlist_factory):
    # 30 gmail, 30 ms, 25 mixed, 15 non_tech (assez pour quotas)
    waitlist_factory(segment="gmail_only", count=30, confirmed=True)
    waitlist_factory(segment="ms_only", count=30, confirmed=True)
    waitlist_factory(segment="mixed", count=25, confirmed=True)
    waitlist_factory(segment="non_tech", count=15, confirmed=True)

    issued = batches.issue_batch(db_session, batch_number=1)

    assert len(issued) == 25
    # Tous les codes uniques
    assert len({i.code for i in issued}) == 25
    # Tous expirent à +14j
    assert all(i.expires_at > datetime.now(UTC) + timedelta(days=13) for i in issued)


def test_issue_batch_raises_if_waitlist_too_small(db_session, waitlist_factory):
    waitlist_factory(segment="gmail_only", count=5, confirmed=True)

    with pytest.raises(ValueError, match="Batch #1 impossible"):
        batches.issue_batch(db_session, batch_number=1)


def test_issue_batch_ignores_non_confirmed(db_session, waitlist_factory):
    waitlist_factory(segment="gmail_only", count=30, confirmed=False)

    with pytest.raises(ValueError):
        batches.issue_batch(db_session, batch_number=1)


def test_redeem_happy_path(db_session, waitlist_factory, user_factory):
    waitlist_factory(segment="gmail_only", count=30, confirmed=True)
    waitlist_factory(segment="ms_only", count=30, confirmed=True)
    waitlist_factory(segment="mixed", count=25, confirmed=True)
    waitlist_factory(segment="non_tech", count=15, confirmed=True)
    issued = batches.issue_batch(db_session, batch_number=1)

    user = user_factory()
    inv = batches.redeem(db_session, code=issued[0].code, user_id=user.id)

    assert inv.redeemed_by_user_id == user.id
    assert inv.redeemed_at is not None


def test_redeem_rejects_reuse(db_session, waitlist_factory, user_factory):
    waitlist_factory(segment="gmail_only", count=30, confirmed=True)
    waitlist_factory(segment="ms_only", count=30, confirmed=True)
    waitlist_factory(segment="mixed", count=25, confirmed=True)
    waitlist_factory(segment="non_tech", count=15, confirmed=True)
    issued = batches.issue_batch(db_session, batch_number=1)

    user_a = user_factory()
    user_b = user_factory()
    batches.redeem(db_session, code=issued[0].code, user_id=user_a.id)

    with pytest.raises(InvitationError, match="déjà utilisé"):
        batches.redeem(db_session, code=issued[0].code, user_id=user_b.id)


def test_redeem_rejects_expired(db_session, waitlist_factory, user_factory):
    waitlist_factory(segment="gmail_only", count=30, confirmed=True)
    waitlist_factory(segment="ms_only", count=30, confirmed=True)
    waitlist_factory(segment="mixed", count=25, confirmed=True)
    waitlist_factory(segment="non_tech", count=15, confirmed=True)
    issued = batches.issue_batch(
        db_session, batch_number=1, now=datetime.now(UTC) - timedelta(days=20)
    )

    user = user_factory()
    with pytest.raises(InvitationError, match="expiré"):
        batches.redeem(db_session, code=issued[0].code, user_id=user.id)


def test_redeem_unknown_code(db_session, user_factory):
    user = user_factory()
    with pytest.raises(InvitationError, match="inconnu"):
        batches.redeem(db_session, code="ZZZZZZZZZZZZ", user_id=user.id)


def test_batch_stats(db_session, waitlist_factory, user_factory):
    waitlist_factory(segment="gmail_only", count=30, confirmed=True)
    waitlist_factory(segment="ms_only", count=30, confirmed=True)
    waitlist_factory(segment="mixed", count=25, confirmed=True)
    waitlist_factory(segment="non_tech", count=15, confirmed=True)
    issued = batches.issue_batch(db_session, batch_number=1)

    batches.redeem(db_session, code=issued[0].code, user_id=user_factory().id)
    batches.redeem(db_session, code=issued[1].code, user_id=user_factory().id)

    stats = batches.batch_stats(db_session)
    assert any(s["batch"] == 1 and s["issued"] == 25 and s["redeemed"] == 2 for s in stats)
