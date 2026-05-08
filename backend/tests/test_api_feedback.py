"""Tests API feedback (rate-limit, anonymisation, validation)."""

from __future__ import annotations


def test_submit_nps_happy_path(client, auth_headers):
    r = client.post(
        "/feedback",
        json={
            "kind": "nps",
            "score": 9,
            "message": "Super outil, RAS",
            "app_version": "0.9.0",
            "platform": "pwa-mobile",
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    assert r.json()["ok"] is True


def test_submit_nps_requires_score(client, auth_headers):
    r = client.post(
        "/feedback",
        json={"kind": "nps", "score": None},
        headers=auth_headers,
    )
    assert r.status_code == 400


def test_submit_bug_strips_score(client, auth_headers, db_session):
    from pli.db.models import FeedbackSubmission

    r = client.post(
        "/feedback",
        json={"kind": "bug", "score": 8, "message": "crash composer"},
        headers=auth_headers,
    )
    assert r.status_code == 201
    row = db_session.query(FeedbackSubmission).order_by(FeedbackSubmission.id.desc()).first()
    assert row.score is None  # nettoyé


def test_anonymous_feedback(client, auth_headers, db_session):
    from pli.db.models import FeedbackSubmission

    client.post(
        "/feedback",
        json={"kind": "suggestion", "message": "Raccourci clavier svp", "anonymous": True},
        headers=auth_headers,
    )
    row = db_session.query(FeedbackSubmission).order_by(FeedbackSubmission.id.desc()).first()
    assert row.user_id_hash is None


def test_rate_limit_3_per_hour(client, auth_headers):
    for _ in range(3):
        r = client.post("/feedback", json={"kind": "bug", "message": "x"}, headers=auth_headers)
        assert r.status_code == 201
    r = client.post("/feedback", json={"kind": "bug", "message": "x"}, headers=auth_headers)
    assert r.status_code == 429


def test_score_out_of_range_rejected(client, auth_headers):
    r = client.post(
        "/feedback",
        json={"kind": "nps", "score": 11},
        headers=auth_headers,
    )
    assert r.status_code == 422
