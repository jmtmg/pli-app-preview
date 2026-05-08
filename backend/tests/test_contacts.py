"""Tests BE — GET /contacts/{id} + PATCH /contacts/{id}."""

from __future__ import annotations

import time


def _seed_contact() -> None:
    from pli.db import get_conn

    now = int(time.time())
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO accounts (id, provider, email, is_active, created_at) "
            "VALUES ('A', 'gmail', 'me@x.io', 1, ?)",
            (now,),
        )
        conn.execute(
            """INSERT INTO contacts (id, account_id, email, email_normalized,
                                      display_name, company, role, phone, notes,
                                      kind, is_muted, is_pinned, pinned_order,
                                      unread_count, has_attachments, last_msg_at)
               VALUES ('c-alice', 'A', 'Alice@X.io', 'alice@x.io',
                       'Alice Martin', 'Acme', 'CTO', '0600', 'la dev',
                       'human', 0, 1, 2, 3, 1, ?)""",
            (now,),
        )
        # message + piece jointe
        conn.execute(
            """INSERT INTO messages (id, account_id, contact_id, provider_id,
                                     direction, from_email, received_at,
                                     has_attachments)
               VALUES ('m1', 'A', 'c-alice', 'p1', 'in', 'alice@x.io', ?, 1)""",
            (now,),
        )
        conn.execute(
            """INSERT INTO attachments (id, message_id, contact_id, filename,
                                         mime_type, size_bytes)
               VALUES ('att-1', 'm1', 'c-alice', 'cv.pdf', 'application/pdf', 40000)""",
        )
        conn.commit()


def test_get_contact_404(client) -> None:  # type: ignore[no-untyped-def]
    r = client.get("/contacts/nope")
    assert r.status_code == 404


def test_get_contact_happy_path(client) -> None:  # type: ignore[no-untyped-def]
    _seed_contact()
    r = client.get("/contacts/c-alice")
    assert r.status_code == 200, r.text
    c = r.json()
    assert c["id"] == "c-alice"
    assert c["display_name"] == "Alice Martin"
    assert c["company"] == "Acme"
    assert c["role"] == "CTO"
    assert c["phone"] == "0600"
    assert c["notes"] == "la dev"
    assert c["is_pinned"] is True
    assert c["pinned_order"] == 2
    assert c["unread_count"] == 3
    assert c["has_attachments"] is True
    assert c["kind"] == "human"
    # Projection : pas d'internals
    for forbidden in ("created_at", "email_normalized"):
        assert forbidden not in c
    # Attachments
    assert len(c["attachments"]) == 1
    att = c["attachments"][0]
    assert att["filename"] == "cv.pdf"
    assert att["size_bytes"] == 40000
    assert att["message_id"] == "m1"


def test_patch_contact_updates_fields(client) -> None:  # type: ignore[no-untyped-def]
    _seed_contact()
    r = client.patch("/contacts/c-alice", json={"display_name": "Alice M.", "notes": "nouvelle note"})
    assert r.status_code == 200, r.text
    # Re-GET pour verifier persistance
    c = client.get("/contacts/c-alice").json()
    assert c["display_name"] == "Alice M."
    assert c["notes"] == "nouvelle note"
    # Les autres champs intacts
    assert c["company"] == "Acme"


def test_patch_empty_body_400(client) -> None:  # type: ignore[no-untyped-def]
    _seed_contact()
    r = client.patch("/contacts/c-alice", json={})
    assert r.status_code == 400


def test_patch_unknown_404(client) -> None:  # type: ignore[no-untyped-def]
    r = client.patch("/contacts/nope", json={"display_name": "X"})
    assert r.status_code == 404


def test_patch_pinned_order_out_of_range(client) -> None:  # type: ignore[no-untyped-def]
    _seed_contact()
    r = client.patch("/contacts/c-alice", json={"pinned_order": 5})
    assert r.status_code == 400


def test_patch_toggle_mute(client) -> None:  # type: ignore[no-untyped-def]
    _seed_contact()
    r = client.patch("/contacts/c-alice", json={"is_muted": True})
    assert r.status_code == 200
    assert r.json()["is_muted"] is True
