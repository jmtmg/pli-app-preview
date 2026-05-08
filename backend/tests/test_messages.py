"""Tests BE — GET /messages/by-contact/{id} et POST /messages/{id}/read.

Couvre :
- 404 si contact inconnu
- tri ASC chronologique
- projection publique (pas de body_html, raw_headers, provider_id)
- body_snippet fallback sur body_text quand snippet vide
- limit borne a 500
- mark_read bascule + maj denormalized counter
"""

from __future__ import annotations

import time


def _seed_conv() -> None:
    """2 contacts, messages etales dans le temps, 1 avec body_text only."""
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
                                      kind, unread_count, last_msg_at)
               VALUES ('c-alice', 'A', 'alice@x.io', 'alice@x.io', 'human', 2, ?)""",
            (now + 10,),
        )
        conn.execute(
            """INSERT INTO contacts (id, account_id, email, email_normalized,
                                      kind, unread_count, last_msg_at)
               VALUES ('c-bob', 'A', 'bob@x.io', 'bob@x.io', 'human', 0, ?)""",
            (now + 5,),
        )
        # 3 messages Alice (ordre insere dans le desordre — le endpoint doit trier)
        msgs = [
            # (id, contact, direction, subject, snippet, body_text, received_at,
            #  has_att, is_read)
            ("m-a2", "c-alice", "out", "Re: hello", "reply", None, now + 8, 0, 1),
            ("m-a1", "c-alice", "in",  "hello",    "yo",    None, now + 5, 0, 0),
            ("m-a3", "c-alice", "in",  None,       None,    "Pas de snippet, juste du texte dans body_text a tronquer.", now + 10, 1, 0),
        ]
        for mid, cid, dir_, subj, sn, bt, rat, att, rd in msgs:
            conn.execute(
                """INSERT INTO messages (id, account_id, contact_id, provider_id,
                                         direction, subject, snippet, body_text,
                                         from_email, received_at, has_attachments,
                                         is_read, raw_headers)
                   VALUES (?, 'A', ?, ?, ?, ?, ?, ?, 'alice@x.io', ?, ?, ?, 'SECRET-HEADERS')""",
                (mid, cid, f"p-{mid}", dir_, subj, sn, bt, rat, att, rd),
            )
        conn.commit()


def test_messages_by_contact_404_if_unknown(client) -> None:  # type: ignore[no-untyped-def]
    r = client.get("/messages/by-contact/does-not-exist")
    assert r.status_code == 404


def test_messages_by_contact_chronological_order(client) -> None:  # type: ignore[no-untyped-def]
    _seed_conv()
    r = client.get("/messages/by-contact/c-alice")
    assert r.status_code == 200, r.text
    items = r.json()
    assert [m["id"] for m in items] == ["m-a1", "m-a2", "m-a3"]
    # sent_at est monotone croissant
    ts = [m["sent_at"] for m in items]
    assert ts == sorted(ts)


def test_messages_by_contact_projection_no_secrets(client) -> None:  # type: ignore[no-untyped-def]
    _seed_conv()
    r = client.get("/messages/by-contact/c-alice")
    text = r.text
    assert "SECRET-HEADERS" not in text
    item = r.json()[0]
    for forbidden in ("provider_id", "raw_headers", "body_html", "body_text", "account_id"):
        assert forbidden not in item, f"champ sensible expose : {forbidden}"


def test_messages_by_contact_snippet_fallback_to_body_text(client) -> None:  # type: ignore[no-untyped-def]
    _seed_conv()
    items = client.get("/messages/by-contact/c-alice").json()
    # m-a3 n'a pas de snippet → fallback body_text
    m3 = next(m for m in items if m["id"] == "m-a3")
    assert "body_text" in m3["body_snippet"].lower() or "tronquer" in m3["body_snippet"]


def test_messages_by_contact_limit_clamped(client) -> None:  # type: ignore[no-untyped-def]
    _seed_conv()
    r = client.get("/messages/by-contact/c-alice", params={"limit": 9999})
    assert r.status_code == 200  # ne crash pas


def test_messages_by_contact_empty_contact(client) -> None:  # type: ignore[no-untyped-def]
    _seed_conv()
    r = client.get("/messages/by-contact/c-bob")
    assert r.status_code == 200
    assert r.json() == []


# -------- mark_read --------


def test_mark_read_bascule_and_decrements_counter(client) -> None:  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    _seed_conv()
    r = client.post("/messages/m-a1/read", params={"read": True})
    assert r.status_code == 200, r.text
    payload = r.json()
    assert payload["changed"] is True
    with get_conn() as conn:
        (cnt,) = conn.execute(
            "SELECT unread_count FROM contacts WHERE id = 'c-alice'"
        ).fetchone()
    assert cnt == 1  # 2 - 1


def test_mark_read_idempotent(client) -> None:  # type: ignore[no-untyped-def]
    _seed_conv()
    # m-a2 est deja is_read=1
    r = client.post("/messages/m-a2/read", params={"read": True})
    assert r.json()["changed"] is False


def test_mark_read_404_on_unknown(client) -> None:  # type: ignore[no-untyped-def]
    r = client.post("/messages/does-not-exist/read")
    assert r.status_code == 404


def test_mark_unread_increments_counter(client) -> None:  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    _seed_conv()
    r = client.post("/messages/m-a2/read", params={"read": False})
    assert r.status_code == 200
    with get_conn() as conn:
        (cnt,) = conn.execute(
            "SELECT unread_count FROM contacts WHERE id = 'c-alice'"
        ).fetchone()
    assert cnt == 3  # 2 + 1


def test_mark_read_counter_never_negative(client) -> None:  # type: ignore[no-untyped-def]
    """Garde-fou : si le denormalized counter derive, on clamp a 0."""
    from pli.db import get_conn

    _seed_conv()
    # Force unread_count = 0 artificiellement
    with get_conn() as conn:
        conn.execute("UPDATE contacts SET unread_count = 0 WHERE id = 'c-alice'")
        conn.commit()
    # Marquer lu un message deja lu → changed=False, pas d'update
    # Mais marquer lu un message unread (m-a1) → delta -1 applique sur 0 → MAX(0, -1) = 0
    client.post("/messages/m-a1/read", params={"read": True})
    with get_conn() as conn:
        (cnt,) = conn.execute(
            "SELECT unread_count FROM contacts WHERE id = 'c-alice'"
        ).fetchone()
    assert cnt == 0
