from __future__ import annotations


def test_demo_seed_exposes_functional_mailbox(client):
    seeded = client.post("/demo/seed?reset=true")
    assert seeded.status_code == 200, seeded.text
    assert seeded.json()["accounts"] == 1
    assert seeded.json()["contacts"] == 3
    assert seeded.json()["messages"] == 4

    accounts = client.get("/accounts")
    assert accounts.status_code == 200, accounts.text
    assert accounts.json()[0]["email"] == "demo@pli-app.fr"

    conversations = client.get("/conversations?filter=all")
    assert conversations.status_code == 200, conversations.text
    body = conversations.json()
    assert len(body["items"]) == 3
    assert body["items"][0]["contact_id"] == "demo-contact-alice"


def test_local_composer_creates_outgoing_message(client):
    assert client.post("/demo/seed?reset=true").status_code == 200

    before = client.get("/messages/by-contact/demo-contact-alice")
    assert before.status_code == 200
    before_count = len(before.json())

    sent = client.post(
        "/messages/send",
        json={"contact_id": "demo-contact-alice", "body": "Message local envoyé depuis le MVP."},
    )
    assert sent.status_code == 200, sent.text
    sent_body = sent.json()
    assert sent_body["direction"] == "out"
    assert sent_body["body_snippet"] == "Message local envoyé depuis le MVP."

    after = client.get("/messages/by-contact/demo-contact-alice")
    assert after.status_code == 200
    assert len(after.json()) == before_count + 1
    assert after.json()[-1]["id"] == sent_body["id"]


def test_local_composer_rejects_cloud_mode(client, monkeypatch):
    assert client.post("/demo/seed?reset=true").status_code == 200

    from pli.config import settings

    monkeypatch.setattr(settings, "mode", "cloud")
    sent = client.post(
        "/messages/send",
        json={"contact_id": "demo-contact-alice", "body": "Message local envoyé depuis le MVP."},
    )

    assert sent.status_code == 501
