"""M1 initial — schéma dual SQLite / PostgreSQL.

La version SQLite est identique à schema.sql existant (M1).
La version PostgreSQL applique le même schéma avec dialecte adapté :
- INTEGER epoch → BIGINT
- TEXT → TEXT (compatible)
- UNIQUE / CHECK constraints identiques
- FTS5 remplacé par tsvector + index GIN
- user_id NOT NULL partout (ajouté ici mais nullable pour compat Local)

Revision ID: 0001_initial_m1
Revises:
Create Date: 2026-06-19
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial_m1"
down_revision = None
branch_labels = None
depends_on = None


def _is_sqlite() -> bool:
    return op.get_bind().dialect.name == "sqlite"


def upgrade() -> None:
    if _is_sqlite():
        # SQLite : délégué au schema.sql existant, déjà appliqué par init_db()
        # On matérialise quand même la version pour Alembic.
        return
    # ---- PostgreSQL (mode Cloud) ----
    op.execute("""
        CREATE TABLE accounts (
            id              TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL,
            provider        TEXT NOT NULL CHECK(provider IN ('gmail','microsoft')),
            email           TEXT NOT NULL,
            display_name    TEXT,
            oauth_access    TEXT,
            oauth_refresh   TEXT,
            oauth_expiry    BIGINT,
            history_cursor  TEXT,
            signature       TEXT,
            avatar_color    TEXT,
            last_sync_at    BIGINT,
            last_error      TEXT,
            is_active       INTEGER NOT NULL DEFAULT 1,
            created_at      BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM now())::bigint,
            UNIQUE(provider, email, user_id)
        )
    """)
    op.create_index("idx_accounts_user", "accounts", ["user_id"])

    op.execute("""
        CREATE TABLE contacts (
            id              TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL,
            account_id      TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            email           TEXT NOT NULL,
            email_normalized TEXT NOT NULL,
            display_name    TEXT,
            company         TEXT,
            role            TEXT,
            phone           TEXT,
            notes           TEXT,
            is_muted        INTEGER NOT NULL DEFAULT 0,
            is_pinned       INTEGER NOT NULL DEFAULT 0,
            pinned_order    INTEGER,
            kind            TEXT NOT NULL DEFAULT 'human',
            last_msg_at     BIGINT,
            unread_count    INTEGER NOT NULL DEFAULT 0,
            has_attachments INTEGER NOT NULL DEFAULT 0,
            created_at      BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM now())::bigint,
            UNIQUE(account_id, email_normalized)
        )
    """)
    op.create_index("idx_contacts_user", "contacts", ["user_id"])
    op.create_index(
        "idx_contacts_account_last_msg",
        "contacts",
        ["account_id", sa.text("last_msg_at DESC")],
    )
    op.create_index("idx_contacts_pinned", "contacts", ["user_id", "is_pinned", "pinned_order"])

    op.execute("""
        CREATE TABLE messages (
            id              TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL,
            account_id      TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            contact_id      TEXT NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
            provider_id     TEXT NOT NULL,
            thread_id       TEXT,
            direction       TEXT NOT NULL CHECK(direction IN ('in','out')),
            subject         TEXT,
            snippet         TEXT,
            body_text       TEXT,
            body_html       TEXT,
            from_email      TEXT NOT NULL,
            from_name       TEXT,
            to_emails       JSONB,
            cc_emails       JSONB,
            received_at     BIGINT NOT NULL,
            is_read         INTEGER NOT NULL DEFAULT 0,
            is_starred      INTEGER NOT NULL DEFAULT 0,
            has_attachments INTEGER NOT NULL DEFAULT 0,
            raw_headers     JSONB,
            fts             tsvector,
            created_at      BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM now())::bigint,
            UNIQUE(account_id, provider_id)
        )
    """)
    op.create_index("idx_messages_user", "messages", ["user_id"])
    op.create_index("idx_messages_contact_time", "messages",
                    ["contact_id", sa.text("received_at DESC")])
    op.create_index("idx_messages_unread", "messages",
                    ["user_id", "is_read", sa.text("received_at DESC")])
    op.execute("CREATE INDEX idx_messages_fts ON messages USING GIN(fts)")

    op.execute("""
        CREATE OR REPLACE FUNCTION messages_fts_refresh() RETURNS trigger AS $$
        BEGIN
          NEW.fts :=
              setweight(to_tsvector('simple', coalesce(NEW.subject, '')), 'A')
            || setweight(to_tsvector('simple', coalesce(NEW.from_name, '') || ' ' || coalesce(NEW.from_email, '')), 'B')
            || setweight(to_tsvector('simple', coalesce(NEW.body_text, '')), 'C');
          RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER messages_fts_trigger BEFORE INSERT OR UPDATE
        ON messages FOR EACH ROW EXECUTE FUNCTION messages_fts_refresh();
    """)

    op.execute("""
        CREATE TABLE attachments (
            id              TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL,
            message_id      TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
            contact_id      TEXT NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
            filename        TEXT NOT NULL,
            mime_type       TEXT,
            size_bytes      BIGINT,
            sha256          TEXT,
            storage_key     TEXT,
            provider_id     TEXT,
            ocr_text        TEXT,
            created_at      BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM now())::bigint
        )
    """)
    op.create_index("idx_attachments_user", "attachments", ["user_id"])
    op.create_index("idx_attachments_message", "attachments", ["message_id"])

    op.execute("""
        CREATE TABLE drafts (
            id              TEXT PRIMARY KEY,
            user_id         TEXT NOT NULL,
            account_id      TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            contact_id      TEXT,
            in_reply_to     TEXT,
            to_emails       JSONB,
            cc_emails       JSONB,
            subject         TEXT,
            body_text       TEXT,
            signature_active INTEGER NOT NULL DEFAULT 1,
            updated_at      BIGINT NOT NULL DEFAULT EXTRACT(EPOCH FROM now())::bigint
        )
    """)
    op.create_index("idx_drafts_user", "drafts", ["user_id"])

    op.execute("""
        CREATE TABLE sync_log (
            id              BIGSERIAL PRIMARY KEY,
            user_id         TEXT NOT NULL,
            account_id      TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
            kind            TEXT NOT NULL CHECK(kind IN ('initial','incremental')),
            started_at      BIGINT NOT NULL,
            ended_at        BIGINT,
            messages_imported INTEGER NOT NULL DEFAULT 0,
            error           TEXT
        )
    """)
    op.create_index("idx_sync_log_user", "sync_log", ["user_id"])


def downgrade() -> None:
    if _is_sqlite():
        return
    for t in ("sync_log", "drafts", "attachments", "messages", "contacts", "accounts"):
        op.execute(f"DROP TABLE IF EXISTS {t} CASCADE")
    op.execute("DROP FUNCTION IF EXISTS messages_fts_refresh() CASCADE")
