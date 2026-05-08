"""Tests unitaires du parser (normalisation email, classification)."""

from __future__ import annotations

from pli.sync.parser import Snippet, classify_kind, normalize_email


def test_normalize_email_lowercases_and_strips_alias():
    assert normalize_email("Foo.Bar+newsletter@Gmail.com") == "foo.bar@gmail.com"
    assert normalize_email("ALICE@EXAMPLE.COM") == "alice@example.com"


def test_normalize_email_handles_no_plus():
    assert normalize_email("hello@world.fr") == "hello@world.fr"


def test_classify_kind_identifies_notifications():
    assert classify_kind("no-reply@github.com") == "notif"
    assert classify_kind("notifications@linkedin.com") == "notif"
    assert classify_kind("mailer-daemon@gmail.com") == "notif"


def test_classify_kind_keeps_humans():
    assert classify_kind("tiphaine@lsfenergie.fr") == "human"
    assert classify_kind("jm@strate.design") == "human"


def test_snippet_truncates_and_collapses_whitespace():
    long = "Bonjour,\n\n   ceci est    un mail\navec\tdes espaces." * 10
    s = Snippet.from_body(long, max_len=60).text
    assert len(s) == 60
    assert "  " not in s  # collapsed

    assert Snippet.from_body(None).text == ""
    assert Snippet.from_body("").text == ""
