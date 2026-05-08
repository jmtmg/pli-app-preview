"""Tests US-1.3 — validation du schéma SQLite (tables, index, FTS5, triggers).

Objectif :
- Garantir qu'`init_db_local()` crée toutes les tables / index / virtual tables /
  triggers attendus par le reste du backend.
- Les détails du schéma (colonnes, contraintes) sont pilotés par
  `pli/schema.sql` → on ne les re-teste pas ici en exhaustif ; on vérifie que
  les invariants exploités par les routers (`accounts.email` UNIQUE, FTS5 en
  sync avec `messages`, etc.) fonctionnent.
"""

from __future__ import annotations

import sqlite3

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXPECTED_TABLES = {
    "accounts",
    "contacts",
    "messages",
    "attachments",
    "drafts",
    "sync_log",
}

EXPECTED_VIRTUAL_TABLES = {
    "messages_fts",
    "attachments_fts",
}

EXPECTED_INDEXES = {
    "idx_contacts_account_last_msg",
    "idx_contacts_pinned",
    "idx_contacts_kind",
    "idx_messages_contact_time",
    "idx_messages_account_time",
    "idx_messages_unread",
    "idx_attachments_message",
    "idx_attachments_contact",
    "idx_attachments_sha",
}

EXPECTED_TRIGGERS = {
    "messages_fts_ai",
    "messages_fts_ad",
    "messages_fts_au",
}


def _list_objects(conn: sqlite3.Connection, obj_type: str) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = ? AND name NOT LIKE 'sqlite_%'",
        (obj_type,),
    ).fetchall()
    return {row["name"] for row in rows}


# ---------------------------------------------------------------------------
# Init — structures présentes
# ---------------------------------------------------------------------------


def test_init_db_creates_all_tables(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    with get_conn() as conn:
        tables = _list_objects(conn, "table")
    # Les tables virtuelles FTS5 créent aussi des tables internes (messages_fts_data, etc.)
    # → on vérifie que toutes celles attendues sont présentes, sans exiger l'égalité stricte.
    assert EXPECTED_TABLES.issubset(tables), f"Manque: {EXPECTED_TABLES - tables}"


def test_init_db_creates_fts5_virtual_tables(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    with get_conn() as conn:
        tables = _list_objects(conn, "table")
    assert EXPECTED_VIRTUAL_TABLES.issubset(tables), (
        f"FTS5 virtual tables manquantes: {EXPECTED_VIRTUAL_TABLES - tables}"
    )


def test_init_db_creates_expected_indexes(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    with get_conn() as conn:
        indexes = _list_objects(conn, "index")
    assert EXPECTED_INDEXES.issubset(indexes), f"Index manquants: {EXPECTED_INDEXES - indexes}"


def test_init_db_creates_fts_triggers(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    with get_conn() as conn:
        triggers = _list_objects(conn, "trigger")
    assert EXPECTED_TRIGGERS.issubset(triggers), (
        f"Triggers FTS manquants: {EXPECTED_TRIGGERS - triggers}"
    )


def test_init_db_is_idempotent(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    """Appeler init_db_local() deux fois ne doit rien casser (IF NOT EXISTS)."""
    from pli.db import get_conn, init_db_local

    init_db_local()  # 2e init → ne doit pas lever
    init_db_local()  # 3e init
    with get_conn() as conn:
        tables = _list_objects(conn, "table")
    assert EXPECTED_TABLES.issubset(tables)


# ---------------------------------------------------------------------------
# Pragmas & contraintes actives
# ---------------------------------------------------------------------------


def test_foreign_keys_enforced(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    """ON DELETE CASCADE ne fonctionne que si foreign_keys=ON."""
    from pli.db import get_conn

    with get_conn() as conn:
        fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk == 1


def test_account_provider_check_constraint(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    """Un provider hors liste doit être rejeté par la CHECK."""
    from pli.db import get_conn

    with get_conn() as conn, pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO accounts (id, provider, email) VALUES (?, ?, ?)",
            ("a1", "yahoo", "x@y.com"),
        )


def test_account_email_unique_per_provider(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    """UNIQUE(provider, email) → 2 comptes gmail avec le même email refusé."""
    from pli.db import get_conn

    with get_conn() as conn:
        conn.execute(
            "INSERT INTO accounts (id, provider, email) VALUES (?, ?, ?)",
            ("a1", "gmail", "dup@example.com"),
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO accounts (id, provider, email) VALUES (?, ?, ?)",
                ("a2", "gmail", "dup@example.com"),
            )
        # Même email sur un autre provider → OK
        conn.execute(
            "INSERT INTO accounts (id, provider, email) VALUES (?, ?, ?)",
            ("a3", "microsoft", "dup@example.com"),
        )
        conn.commit()


def test_messages_unique_provider_id_per_account(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    """UNIQUE(account_id, provider_id) → dédup à l'insertion (utilisé par sync)."""
    from pli.db import get_conn

    with get_conn() as conn:
        conn.execute("INSERT INTO accounts (id, provider, email) VALUES ('a1', 'gmail', 'a@b.c')")
        conn.execute(
            "INSERT INTO contacts (id, account_id, email, email_normalized) "
            "VALUES ('c1', 'a1', 'x@y.z', 'x@y.z')"
        )
        conn.execute(
            "INSERT INTO messages (id, account_id, contact_id, provider_id, "
            "direction, from_email, received_at) "
            "VALUES ('m1', 'a1', 'c1', 'gmail-msg-1', 'in', 'x@y.z', 1)"
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO messages (id, account_id, contact_id, provider_id, "
                "direction, from_email, received_at) "
                "VALUES ('m2', 'a1', 'c1', 'gmail-msg-1', 'in', 'x@y.z', 2)"
            )


def test_cascade_delete_account_removes_children(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    """Supprimer un account doit cascader sur contacts, messages, attachments."""
    from pli.db import get_conn

    with get_conn() as conn:
        conn.execute("INSERT INTO accounts (id, provider, email) VALUES ('a1', 'gmail', 'a@b.c')")
        conn.execute(
            "INSERT INTO contacts (id, account_id, email, email_normalized) "
            "VALUES ('c1', 'a1', 'x@y.z', 'x@y.z')"
        )
        conn.execute(
            "INSERT INTO messages (id, account_id, contact_id, provider_id, "
            "direction, from_email, received_at) "
            "VALUES ('m1', 'a1', 'c1', 'g1', 'in', 'x@y.z', 1)"
        )
        conn.execute(
            "INSERT INTO attachments (id, message_id, contact_id, filename) "
            "VALUES ('at1', 'm1', 'c1', 'doc.pdf')"
        )
        conn.commit()
        conn.execute("DELETE FROM accounts WHERE id = 'a1'")
        conn.commit()

        assert conn.execute("SELECT count(*) FROM contacts").fetchone()[0] == 0
        assert conn.execute("SELECT count(*) FROM messages").fetchone()[0] == 0
        assert conn.execute("SELECT count(*) FROM attachments").fetchone()[0] == 0


# ---------------------------------------------------------------------------
# FTS5 — maintien automatique via triggers
# ---------------------------------------------------------------------------


def test_fts_insert_trigger_indexes_new_message(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    """INSERT INTO messages → doit peupler messages_fts automatiquement."""
    from pli.db import get_conn

    with get_conn() as conn:
        conn.execute("INSERT INTO accounts (id, provider, email) VALUES ('a1', 'gmail', 'a@b.c')")
        conn.execute(
            "INSERT INTO contacts (id, account_id, email, email_normalized) "
            "VALUES ('c1', 'a1', 'alice@example.com', 'alice@example.com')"
        )
        conn.execute(
            "INSERT INTO messages (id, account_id, contact_id, provider_id, "
            "direction, subject, body_text, from_email, from_name, received_at) "
            "VALUES ('m1', 'a1', 'c1', 'g1', 'in', "
            "'Réunion mensuelle', 'Bonjour, voici l''ordre du jour...', "
            "'alice@example.com', 'Alice Wonderland', 1)"
        )
        conn.commit()

        # Recherche FTS5 → trouve le message via le trigger AI
        hits = conn.execute(
            "SELECT rowid FROM messages_fts WHERE messages_fts MATCH ?",
            ("reunion",),  # remove_diacritics=2 → "réunion" → "reunion"
        ).fetchall()
        assert len(hits) == 1

        hits2 = conn.execute(
            "SELECT rowid FROM messages_fts WHERE messages_fts MATCH ?",
            ("Wonderland",),
        ).fetchall()
        assert len(hits2) == 1


def test_fts_update_trigger_reindexes(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    """UPDATE messages.subject → l'ancien subject ne matche plus, le nouveau oui."""
    from pli.db import get_conn

    with get_conn() as conn:
        conn.execute("INSERT INTO accounts (id, provider, email) VALUES ('a1', 'gmail', 'a@b.c')")
        conn.execute(
            "INSERT INTO contacts (id, account_id, email, email_normalized) "
            "VALUES ('c1', 'a1', 'x@y.z', 'x@y.z')"
        )
        conn.execute(
            "INSERT INTO messages (id, account_id, contact_id, provider_id, "
            "direction, subject, body_text, from_email, received_at) "
            "VALUES ('m1', 'a1', 'c1', 'g1', 'in', 'original', 'body', 'x@y.z', 1)"
        )
        conn.execute("UPDATE messages SET subject = 'modifie' WHERE id = 'm1'")
        conn.commit()

        old = conn.execute(
            "SELECT count(*) FROM messages_fts WHERE messages_fts MATCH ?",
            ("original",),
        ).fetchone()[0]
        new = conn.execute(
            "SELECT count(*) FROM messages_fts WHERE messages_fts MATCH ?",
            ("modifie",),
        ).fetchone()[0]
        assert old == 0
        assert new == 1


def test_fts_delete_trigger_cleans_index(isolated_settings) -> None:  # type: ignore[no-untyped-def]
    from pli.db import get_conn

    with get_conn() as conn:
        conn.execute("INSERT INTO accounts (id, provider, email) VALUES ('a1', 'gmail', 'a@b.c')")
        conn.execute(
            "INSERT INTO contacts (id, account_id, email, email_normalized) "
            "VALUES ('c1', 'a1', 'x@y.z', 'x@y.z')"
        )
        conn.execute(
            "INSERT INTO messages (id, account_id, contact_id, provider_id, "
            "direction, subject, body_text, from_email, received_at) "
            "VALUES ('m1', 'a1', 'c1', 'g1', 'in', 'unique_token_zz', 'b', 'x@y.z', 1)"
        )
        conn.execute("DELETE FROM messages WHERE id = 'm1'")
        conn.commit()

        n = conn.execute(
            "SELECT count(*) FROM messages_fts WHERE messages_fts MATCH ?",
            ("unique_token_zz",),
        ).fetchone()[0]
        assert n == 0
