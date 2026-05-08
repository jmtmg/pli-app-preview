"""Tests MVP local demo — slice vérifiable sans credentials réels."""

from __future__ import annotations


def test_local_demo_reset_seeds_backend_read_slice(client) -> None:  # type: ignore[no-untyped-def]
    """Seed local démo puis vérifie health + conversations/messages/search/contact."""
    r = client.post("/demo/reset")
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload["mode"] == "local"
    assert payload["seeded"] is True
    assert payload["counts"] == {"accounts": 1, "contacts": 4, "messages": 5, "attachments": 1}
    assert "token" not in r.text.lower()
    assert "secret" not in r.text.lower()

    health = client.get("/health").json()
    assert health["accounts"]["active"] == 1
    assert health["accounts"]["last_sync_at"] is not None

    conversations = client.get("/conversations?filter=all").json()
    ids = [item["contact_id"] for item in conversations["items"]]
    assert ids[0] == "demo-contact-alice"
    assert set(ids) == {
        "demo-contact-alice",
        "demo-contact-banque",
        "demo-contact-legal",
        "demo-contact-test",
    }
    assert conversations["items"][0]["is_pinned"] is True
    assert "frontend" in conversations["items"][0]["last_preview"]

    messages = client.get("/messages/by-contact/demo-contact-alice").json()
    assert [message["id"] for message in messages] == ["demo-msg-001", "demo-msg-002"]
    assert "MVP local" in messages[0]["body_snippet"]

    contact = client.get("/contacts/demo-contact-alice").json()
    assert contact["display_name"] == "Alice Martin"
    assert contact["company"] == "JMJ Consulting"
    assert contact["attachments"][0]["filename"] == "mvp-local-demo.pdf"

    contact_search = client.get(
        "/search", params={"q": "JMJ", "account_id": "demo-account-gmail"}
    ).json()
    assert any(result["id"] == "demo-contact-alice" for result in contact_search["contacts"])

    mvp_search = client.get(
        "/search", params={"q": "MVP", "account_id": "demo-account-gmail"}
    ).json()
    assert any(result["id"] == "demo-msg-001" for result in mvp_search["messages"])
    assert any(result["filename"] == "mvp-local-demo.pdf" for result in mvp_search["attachments"])

    test_search = client.get(
        "/search", params={"q": "test.pli", "account_id": "demo-account-gmail"}
    ).json()
    assert any(result["email"] == "test.pli@demo-pli.com" for result in test_search["contacts"])


def test_local_demo_reset_is_idempotent(client) -> None:  # type: ignore[no-untyped-def]
    first = client.post("/demo/reset")
    second = client.post("/demo/reset")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["counts"] == second.json()["counts"]
    assert len(client.get("/conversations?filter=all").json()["items"]) == 4


def test_search_is_scoped_to_requested_account(client) -> None:  # type: ignore[no-untyped-def]
    """La recherche MVP ne doit jamais fuiter des résultats d'un autre compte."""
    client.post("/demo/reset")

    from pli.db import get_conn

    with get_conn() as conn:
        conn.execute(
            """INSERT INTO accounts(id, provider, email, display_name, avatar_color, last_sync_at)
               VALUES (?, 'gmail', ?, ?, '#444444', 1778270000)""",
            ("other-account", "other@example.com", "Autre compte"),
        )
        conn.execute(
            """INSERT INTO contacts(id, account_id, email, email_normalized, display_name,
                                      company, kind, last_msg_at, unread_count)
               VALUES (?, ?, ?, ?, ?, ?, 'human', 1778270000, 1)""",
            (
                "other-contact-hidden",
                "other-account",
                "hidden@example.com",
                "hidden@example.com",
                "Hidden Other",
                "Other Co",
            ),
        )
        conn.execute(
            """INSERT INTO messages(id, account_id, contact_id, provider_id, direction,
                                      subject, snippet, body_text, from_email, received_at)
               VALUES (?, ?, ?, ?, 'in', ?, ?, ?, ?, 1778270000)""",
            (
                "other-message-hidden",
                "other-account",
                "other-contact-hidden",
                "other-provider-hidden",
                "Hidden account result",
                "NeedleOtherAccount",
                "NeedleOtherAccount should not leak to demo account search",
                "hidden@example.com",
            ),
        )
        conn.commit()

    scoped = client.get(
        "/search",
        params={"q": "NeedleOtherAccount", "account_id": "demo-account-gmail"},
    ).json()
    assert scoped == {"contacts": [], "messages": [], "attachments": []}

    other = client.get(
        "/search",
        params={"q": "NeedleOtherAccount", "account_id": "other-account"},
    ).json()
    assert any(result["id"] == "other-message-hidden" for result in other["messages"])


def test_search_requires_account_id(client) -> None:  # type: ignore[no-untyped-def]
    client.post("/demo/reset")

    response = client.get("/search", params={"q": "test.pli"})

    assert response.status_code == 422


def test_local_demo_reset_rejects_cloud_mode(client, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from pli.config import settings

    monkeypatch.setattr(settings, "mode", "cloud")
    r = client.post("/demo/reset")
    assert r.status_code == 404
