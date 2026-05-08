"""Tests MVP local demo — slice vérifiable sans credentials réels."""

from __future__ import annotations


def test_local_demo_reset_seeds_backend_read_slice(client) -> None:  # type: ignore[no-untyped-def]
    """Seed local démo puis vérifie health + conversations/messages/search/contact."""
    r = client.post("/demo/reset")
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload["mode"] == "local"
    assert payload["seeded"] is True
    assert payload["counts"] == {"accounts": 1, "contacts": 3, "messages": 4, "attachments": 1}
    assert "token" not in r.text.lower()
    assert "secret" not in r.text.lower()

    health = client.get("/health").json()
    assert health["accounts"]["active"] == 1
    assert health["accounts"]["last_sync_at"] is not None

    conversations = client.get("/conversations?filter=all").json()
    ids = [item["contact_id"] for item in conversations["items"]]
    assert ids[0] == "demo-contact-alice"
    assert set(ids) == {"demo-contact-alice", "demo-contact-banque", "demo-contact-legal"}
    assert conversations["items"][0]["is_pinned"] is True
    assert "frontend" in conversations["items"][0]["last_preview"]

    messages = client.get("/messages/by-contact/demo-contact-alice").json()
    assert [message["id"] for message in messages] == ["demo-msg-001", "demo-msg-002"]
    assert "MVP local" in messages[0]["body_snippet"]

    contact = client.get("/contacts/demo-contact-alice").json()
    assert contact["display_name"] == "Alice Martin"
    assert contact["company"] == "JMJ Consulting"
    assert contact["attachments"][0]["filename"] == "mvp-local-demo.pdf"

    contact_search = client.get("/search", params={"q": "JMJ"}).json()
    assert any(result["id"] == "demo-contact-alice" for result in contact_search["contacts"])

    mvp_search = client.get("/search", params={"q": "MVP"}).json()
    assert any(result["id"] == "demo-msg-001" for result in mvp_search["messages"])
    assert any(result["filename"] == "mvp-local-demo.pdf" for result in mvp_search["attachments"])


def test_local_demo_reset_is_idempotent(client) -> None:  # type: ignore[no-untyped-def]
    first = client.post("/demo/reset")
    second = client.post("/demo/reset")
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["counts"] == second.json()["counts"]
    assert len(client.get("/conversations?filter=all").json()["items"]) == 3


def test_local_demo_reset_rejects_cloud_mode(client, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    from pli.config import settings

    monkeypatch.setattr(settings, "mode", "cloud")
    r = client.post("/demo/reset")
    assert r.status_code == 404
