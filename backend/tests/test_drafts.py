from __future__ import annotations

import sqlite3

import pytest


def test_draft_upsert_get_and_clear_are_scoped_to_one_conversation(client):
    assert client.post("/demo/seed?reset=true").status_code == 200

    empty = client.get(
        "/messages/drafts",
        params={"account_id": "demo-account-gmail", "contact_id": "demo-contact-alice"},
    )
    assert empty.status_code == 200, empty.text
    assert empty.json() is None

    saved = client.post(
        "/messages/drafts",
        json={
            "account_id": "demo-account-gmail",
            "contact_id": "demo-contact-alice",
            "subject": "RE: Projet Alpha",
            "body_text": "Brouillon sauvegardé côté local.",
            "signature_active": True,
        },
    )
    assert saved.status_code == 200, saved.text
    first = saved.json()
    assert first["id"].startswith("draft-")
    assert first["contact_id"] == "demo-contact-alice"
    assert first["subject"] == "RE: Projet Alpha"
    assert first["body_text"] == "Brouillon sauvegardé côté local."
    assert first["signature_active"] is True

    updated = client.post(
        "/messages/drafts",
        json={
            "account_id": "demo-account-gmail",
            "contact_id": "demo-contact-alice",
            "subject": "RE: Projet Alpha — relu",
            "body_text": "Version deux du brouillon.",
            "signature_active": False,
        },
    )
    assert updated.status_code == 200, updated.text
    second = updated.json()
    assert second["id"] == first["id"]
    assert second["subject"] == "RE: Projet Alpha — relu"
    assert second["body_text"] == "Version deux du brouillon."
    assert second["signature_active"] is False

    other_conversation = client.get(
        "/messages/drafts",
        params={"account_id": "demo-account-gmail", "contact_id": "demo-contact-bob"},
    )
    assert other_conversation.status_code == 200, other_conversation.text
    assert other_conversation.json() is None

    loaded = client.get(
        "/messages/drafts",
        params={"account_id": "demo-account-gmail", "contact_id": "demo-contact-alice"},
    )
    assert loaded.status_code == 200, loaded.text
    assert loaded.json()["id"] == first["id"]
    assert loaded.json()["subject"] == "RE: Projet Alpha — relu"

    cleared_wrong_scope = client.delete(
        f"/messages/drafts/{first['id']}",
        params={"account_id": "wrong-account", "contact_id": "demo-contact-alice"},
    )
    assert cleared_wrong_scope.status_code == 404

    still_loaded = client.get(
        "/messages/drafts",
        params={"account_id": "demo-account-gmail", "contact_id": "demo-contact-alice"},
    )
    assert still_loaded.status_code == 200, still_loaded.text
    assert still_loaded.json()["id"] == first["id"]

    cleared = client.delete(
        f"/messages/drafts/{first['id']}",
        params={"account_id": "demo-account-gmail", "contact_id": "demo-contact-alice"},
    )
    assert cleared.status_code == 200, cleared.text
    assert cleared.json() == {"ok": True, "deleted": True, "draft_id": first["id"]}

    after_clear = client.get(
        "/messages/drafts",
        params={"account_id": "demo-account-gmail", "contact_id": "demo-contact-alice"},
    )
    assert after_clear.status_code == 200, after_clear.text
    assert after_clear.json() is None


def test_draft_server_keeps_one_draft_per_conversation_even_with_client_ids(client):
    assert client.post("/demo/seed?reset=true").status_code == 200

    first = client.post(
        "/messages/drafts",
        json={
            "id": "draft-client-forced-a",
            "account_id": "demo-account-gmail",
            "contact_id": "demo-contact-alice",
            "in_reply_to": "demo-msg-001",
            "subject": "RE: Premier",
            "body_text": "Premier brouillon.",
        },
    )
    assert first.status_code == 200, first.text
    first_body = first.json()
    assert first_body["id"] != "draft-client-forced-a"

    second = client.post(
        "/messages/drafts",
        json={
            "id": "draft-client-forced-b",
            "account_id": "demo-account-gmail",
            "contact_id": "demo-contact-alice",
            "in_reply_to": "demo-msg-002",
            "subject": "RE: Deuxième",
            "body_text": "Deuxième version.",
        },
    )
    assert second.status_code == 200, second.text
    second_body = second.json()
    assert second_body["id"] == first_body["id"]
    assert second_body["body_text"] == "Deuxième version."

    loaded = client.get(
        "/messages/drafts",
        params={"account_id": "demo-account-gmail", "contact_id": "demo-contact-alice"},
    )
    assert loaded.status_code == 200, loaded.text
    assert loaded.json()["id"] == first_body["id"]
    assert loaded.json()["subject"] == "RE: Deuxième"


def test_draft_schema_enforces_one_row_per_account_contact(client, isolated_settings):
    assert client.post("/demo/seed?reset=true").status_code == 200

    db_path = isolated_settings / "db.sqlite"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO drafts(id, account_id, contact_id, subject, body_text, signature_active)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "draft-schema-first",
                "demo-account-gmail",
                "demo-contact-alice",
                "RE: Premier",
                "Premier brouillon.",
                1,
            ),
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """
                INSERT INTO drafts(id, account_id, contact_id, subject, body_text, signature_active)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    "draft-schema-second",
                    "demo-account-gmail",
                    "demo-contact-alice",
                    "RE: Deuxième",
                    "Ne doit jamais créer une deuxième ligne.",
                    1,
                ),
            )
        row = conn.execute(
            """
            SELECT count(*) AS n
            FROM drafts
            WHERE account_id = ? AND contact_id = ?
            """,
            ("demo-account-gmail", "demo-contact-alice"),
        ).fetchone()
    assert row[0] == 1


def test_draft_rejects_cross_account_contact(client):
    assert client.post("/demo/seed?reset=true").status_code == 200

    saved = client.post(
        "/messages/drafts",
        json={
            "account_id": "wrong-account",
            "contact_id": "demo-contact-alice",
            "subject": "RE: Secret",
            "body_text": "Ne doit pas être accepté.",
        },
    )
    assert saved.status_code == 400
    assert "account_id" in saved.text
