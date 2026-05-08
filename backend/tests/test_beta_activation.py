"""Tests du tracking d'activation et rétention."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from pli.beta import activation


def test_record_idempotent(db_session, user_factory):
    user = user_factory()
    activation.record(db_session, user.id, "signup", batch_number=1)
    activation.record(db_session, user.id, "signup", batch_number=1)  # dedup

    funnel = activation.activation_funnel(db_session, batch_number=1)
    assert funnel["signup"] == 1


def test_record_invalid_event(db_session, user_factory):
    user = user_factory()
    with pytest.raises(ValueError, match="Événement inconnu"):
        activation.record(db_session, user.id, "unknown_event")


def test_is_activated_requires_both_events(db_session, user_factory):
    user = user_factory()
    activation.record(db_session, user.id, "signup")
    activation.record(db_session, user.id, "first_sync")
    assert activation.is_activated(db_session, user.id) is False

    activation.record(db_session, user.id, "tour_completed")
    assert activation.is_activated(db_session, user.id) is True


def test_activation_funnel_counts_distinct_users(db_session, user_factory):
    for _ in range(10):
        u = user_factory()
        activation.record(db_session, u.id, "signup", batch_number=1)
    for _ in range(6):
        u = user_factory()
        activation.record(db_session, u.id, "signup", batch_number=1)
        activation.record(db_session, u.id, "first_sync", batch_number=1)

    funnel = activation.activation_funnel(db_session, batch_number=1)
    assert funnel["signup"] == 16
    assert funnel["first_sync"] == 6


def test_retention_computes_ratios(db_session, user_factory, time_travel):
    """10 users signup J0, 7 reviennent à J1, 5 à J7, 3 à J30."""
    signup_t = datetime.now(UTC) - timedelta(days=35)

    users = [user_factory(created_at=signup_t) for _ in range(10)]
    for u in users:
        activation.record(db_session, u.id, "signup", batch_number=1)
        # back-date for the test
        _backdate_event(db_session, user_id=u.id, event="signup", at=signup_t)

    # J1 retention : 7 users
    for u in users[:7]:
        _backdate_event_via_record(
            db_session, u, "first_sync", at=signup_t + timedelta(days=1), batch_number=1
        )
    # J7 retention : 5 users
    for u in users[:5]:
        _backdate_event_via_record(
            db_session, u, "oauth_connected", at=signup_t + timedelta(days=7), batch_number=1
        )
    # J30 retention : 3 users
    for u in users[:3]:
        _backdate_event_via_record(
            db_session, u, "first_send", at=signup_t + timedelta(days=30), batch_number=1
        )

    snap = activation.retention(db_session, batch_number=1)
    assert snap.cohort_size == 10
    assert round(snap.j1, 1) == 0.7
    assert round(snap.j7, 1) == 0.5
    assert round(snap.j30, 1) == 0.3


# --- helpers ---


def _backdate_event(db_session, user_id: int, event: str, at):
    from pli.db.models import ActivationEvent

    row = db_session.query(ActivationEvent).filter_by(user_id=user_id, event=event).one()
    row.created_at = at
    db_session.flush()


def _backdate_event_via_record(db_session, user, event: str, at, batch_number: int):
    activation.record(db_session, user.id, event, batch_number=batch_number)
    _backdate_event(db_session, user_id=user.id, event=event, at=at)
