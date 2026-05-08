"""Tests de l'agrégation NPS."""

from __future__ import annotations

from pli.beta import nps


def test_compute_empty(db_session):
    result = nps.compute(db_session)
    assert result.respondents == 0
    assert result.score == 0


def test_compute_all_promoters(db_session, feedback_factory):
    feedback_factory(kind="nps", score=10, count=5)
    feedback_factory(kind="nps", score=9, count=5)

    result = nps.compute(db_session)
    assert result.respondents == 10
    assert result.promoters == 10
    assert result.score == 100


def test_compute_mixed(db_session, feedback_factory):
    feedback_factory(kind="nps", score=10, count=6)  # 6 promoteurs
    feedback_factory(kind="nps", score=8, count=2)  # 2 passifs
    feedback_factory(kind="nps", score=4, count=2)  # 2 détracteurs

    result = nps.compute(db_session)
    assert result.respondents == 10
    assert result.promoters == 6
    assert result.passives == 2
    assert result.detractors == 2
    assert result.score == 40  # (6-2)/10 * 100


def test_ignore_non_nps(db_session, feedback_factory):
    feedback_factory(kind="nps", score=10, count=5)
    feedback_factory(kind="bug", score=None, count=20)  # ne doit pas compter

    result = nps.compute(db_session)
    assert result.respondents == 5


def test_classify_boundaries():
    from pli.beta.nps import _classify

    assert _classify(0) == "detractor"
    assert _classify(6) == "detractor"
    assert _classify(7) == "passive"
    assert _classify(8) == "passive"
    assert _classify(9) == "promoter"
    assert _classify(10) == "promoter"


def test_per_batch(db_session, feedback_factory):
    feedback_factory(kind="nps", score=10, count=10, batch_number=1)
    feedback_factory(kind="nps", score=3, count=10, batch_number=2)

    results = nps.per_batch(db_session)
    b1 = next(r for i, r in enumerate(results, start=1) if i == 1)
    b2 = next(r for i, r in enumerate(results, start=1) if i == 2)
    assert b1.score == 100
    assert b2.score == -100
