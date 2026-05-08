"""Tests US-1.6 — endpoint GET /conversations.

Couvre :
- Tri par (is_pinned DESC, pinned_order ASC, last_msg_at DESC)
- Filtres : humans / notifs / unread / attachments / all
- Filtre par account_id
- Pagination cursor opaque stable (ne duplique pas, ne saute pas)
- Cursor invalide → 400
"""

from __future__ import annotations

import time

import pytest

# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------


@pytest.fixture
def seeded_db(isolated_settings):  # type: ignore[no-untyped-def]
    """Seed 2 comptes + 5 contacts varies pour tester l'endpoint.

    Layout :
      acct A  ├─ alice   (human, unread=2, has_att=1, pinned=1, last=+5)
              ├─ bob     (human, unread=0, has_att=0, last=+4)
              ├─ noreply (notif, last=+3)
      acct B  ├─ carol   (human, unread=1, last=+2)
              └─ dave    (human, unread=0, last=+1)
    """
    from pli.db import get_conn

    now = int(time.time())

    with get_conn() as conn:
        # 2 comptes
        conn.execute(
            "INSERT INTO accounts (id, provider, email, is_active) "
            "VALUES ('A', 'gmail', 'me-a@example.com', 1)"
        )
        conn.execute(
            "INSERT INTO accounts (id, provider, email, is_active) "
            "VALUES ('B', 'gmail', 'me-b@example.com', 1)"
        )
        # Contacts avec last_msg_at croissant (cursor test)
        rows = [
            # (id, account, email, display, kind, is_pinned, pinned_order,
            #  unread, has_att, last_at)
            ("c-alice", "A", "alice@x.com", "Alice", "human", 1, 1, 2, 1, now + 5),
            ("c-bob", "A", "bob@x.com", "Bob", "human", 0, None, 0, 0, now + 4),
            ("c-nore", "A", "noreply@svc.io", None, "notif", 0, None, 0, 0, now + 3),
            ("c-carol", "B", "carol@y.io", "Carol", "human", 0, None, 1, 0, now + 2),
            ("c-dave", "B", "dave@y.io", "Dave", "human", 0, None, 0, 0, now + 1),
        ]
        for cid, acct, email, disp, kind, pin, order, unread, att, lat in rows:
            conn.execute(
                """INSERT INTO contacts (
                    id, account_id, email, email_normalized, display_name,
                    kind, is_pinned, pinned_order, unread_count, has_attachments,
                    last_msg_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (cid, acct, email, email.lower(), disp, kind, pin, order, unread, att, lat),
            )
        # Ajoute un message pour chaque contact pour que last_preview != NULL
        for row in rows:
            cid, acct, email, lat = row[0], row[1], row[2], row[9]
            conn.execute(
                """INSERT INTO messages (
                    id, account_id, contact_id, provider_id, direction,
                    subject, snippet, from_email, received_at
                ) VALUES (?, ?, ?, ?, 'in', ?, ?, ?, ?)""",
                (f"m-{cid}", acct, cid, f"p-{cid}", f"sujet {cid}", f"preview {cid}", email, lat),
            )
        conn.commit()
    return rows


# --------------------------------------------------------------------------
# Tri et filtres
# --------------------------------------------------------------------------


def test_default_filter_humans_excludes_notifs(client, seeded_db):  # type: ignore[no-untyped-def]
    r = client.get("/conversations")
    assert r.status_code == 200
    data = r.json()
    ids = [it["contact_id"] for it in data["items"]]
    assert "c-nore" not in ids
    # 4 humans au total
    assert len(ids) == 4


def test_pinned_comes_first_regardless_of_last_msg_at(client, seeded_db):  # type: ignore[no-untyped-def]
    # Alice est pinned mais pas la plus recente (Dave a last_msg_at=now+1 < Alice+5)
    # → elle DOIT etre en tete meme avec filter=all
    r = client.get("/conversations?filter=all")
    ids = [it["contact_id"] for it in r.json()["items"]]
    assert ids[0] == "c-alice"
    # Apres le pinned, tri DESC par last_msg_at → bob, nore, carol, dave
    assert ids[1:] == ["c-bob", "c-nore", "c-carol", "c-dave"]


def test_filter_notifs_returns_only_notifs(client, seeded_db):  # type: ignore[no-untyped-def]
    r = client.get("/conversations?filter=notifs")
    ids = [it["contact_id"] for it in r.json()["items"]]
    assert ids == ["c-nore"]


def test_filter_unread_returns_only_with_unread(client, seeded_db):  # type: ignore[no-untyped-def]
    r = client.get("/conversations?filter=unread")
    ids = [it["contact_id"] for it in r.json()["items"]]
    assert set(ids) == {"c-alice", "c-carol"}


def test_filter_attachments_returns_only_with_att(client, seeded_db):  # type: ignore[no-untyped-def]
    r = client.get("/conversations?filter=attachments")
    ids = [it["contact_id"] for it in r.json()["items"]]
    assert ids == ["c-alice"]


def test_filter_account_id_scopes_results(client, seeded_db):  # type: ignore[no-untyped-def]
    r = client.get("/conversations?account_id=B&filter=all")
    ids = [it["contact_id"] for it in r.json()["items"]]
    assert set(ids) == {"c-carol", "c-dave"}


# --------------------------------------------------------------------------
# Pagination cursor
# --------------------------------------------------------------------------


def test_pagination_returns_next_cursor_when_more_results(client, seeded_db):  # type: ignore[no-untyped-def]
    # limit=2 → sur 4 humans, on doit obtenir un next_cursor
    r = client.get("/conversations?limit=2")
    data = r.json()
    assert len(data["items"]) == 2
    assert data["next_cursor"] is not None


def test_pagination_cursor_fetches_next_page_without_duplicate(client, seeded_db):  # type: ignore[no-untyped-def]
    # Tri : Alice (pinned), Bob, Carol, Dave
    page1 = client.get("/conversations?filter=all&limit=2").json()
    assert [it["contact_id"] for it in page1["items"]] == ["c-alice", "c-bob"]
    cursor = page1["next_cursor"]
    assert cursor is not None

    page2 = client.get(f"/conversations?filter=all&limit=2&cursor={cursor}").json()
    ids2 = [it["contact_id"] for it in page2["items"]]
    # Le pinned (Alice) n'apparait plus → bon comportement ("page suivante")
    assert "c-alice" not in ids2
    assert "c-bob" not in ids2
    # On doit avoir nore (last=+3) puis carol (last=+2)
    assert ids2 == ["c-nore", "c-carol"]


def test_pagination_last_page_has_null_cursor(client, seeded_db):  # type: ignore[no-untyped-def]
    # 5 items au total avec filter=all → limite 10 renvoie tout + cursor=null
    r = client.get("/conversations?filter=all&limit=10").json()
    assert r["next_cursor"] is None
    assert len(r["items"]) == 5


def test_invalid_cursor_returns_400(client, seeded_db):  # type: ignore[no-untyped-def]
    r = client.get("/conversations?cursor=not@valid@base64")
    assert r.status_code == 400


# --------------------------------------------------------------------------
# Payload shape
# --------------------------------------------------------------------------


def test_response_includes_last_preview_and_iso_timestamp(client, seeded_db):  # type: ignore[no-untyped-def]
    r = client.get("/conversations?filter=humans&limit=1").json()
    item = r["items"][0]
    assert item["last_preview"] == "preview c-alice"
    # last_msg_at serialise en ISO avec timezone
    assert item["last_msg_at"] is not None
    assert "T" in item["last_msg_at"]


# --------------------------------------------------------------------------
# Actions rapides liste : pin / non-lu / silence / archive
# --------------------------------------------------------------------------


def test_pin_limit_is_scoped_to_account(client, seeded_db):  # type: ignore[no-untyped-def]
    """3 épinglées dans B ne doivent pas bloquer Épingler dans A."""
    from pli.db import get_conn

    with get_conn() as conn:
        conn.execute("UPDATE contacts SET is_pinned = 1, pinned_order = 1 WHERE id = 'c-carol'")
        conn.execute("UPDATE contacts SET is_pinned = 1, pinned_order = 2 WHERE id = 'c-dave'")
        conn.commit()

    r = client.post("/conversations/c-bob/pin")

    assert r.status_code == 200
    assert r.json() == {"ok": True, "contact_id": "c-bob"}
    with get_conn() as conn:
        row = conn.execute(
            "SELECT is_pinned, pinned_order FROM contacts WHERE id = 'c-bob'"
        ).fetchone()
    assert row["is_pinned"] == 1
    assert row["pinned_order"] == 2


def test_mark_conversation_unread_marks_latest_incoming_message(client, seeded_db):  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    with get_conn() as conn:
        conn.execute("UPDATE messages SET is_read = 1 WHERE id = 'm-c-bob'")
        conn.execute("UPDATE contacts SET unread_count = 0 WHERE id = 'c-bob'")
        conn.commit()

    r = client.post("/conversations/c-bob/mark-unread")

    assert r.status_code == 200
    assert r.json() == {"ok": True, "contact_id": "c-bob", "unread_count": 1}
    with get_conn() as conn:
        message = conn.execute("SELECT is_read FROM messages WHERE id = 'm-c-bob'").fetchone()
        contact = conn.execute("SELECT unread_count FROM contacts WHERE id = 'c-bob'").fetchone()
    assert message["is_read"] == 0
    assert contact["unread_count"] == 1


def test_archive_hides_conversation_from_default_lists(client, seeded_db):  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    r = client.post("/conversations/c-bob/archive")

    assert r.status_code == 200
    assert r.json() == {"ok": True, "contact_id": "c-bob", "archived": True}
    ids = [it["contact_id"] for it in client.get("/conversations?account_id=A&filter=all").json()["items"]]
    assert "c-bob" not in ids
    with get_conn() as conn:
        archived = conn.execute("SELECT is_archived FROM contacts WHERE id = 'c-bob'").fetchone()["is_archived"]
    assert archived == 1
