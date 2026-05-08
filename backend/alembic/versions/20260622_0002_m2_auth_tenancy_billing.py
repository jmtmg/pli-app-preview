"""M2 — auth PLI, multi-tenancy, billing, emails, licences.

- Table `users` (compte PLI Cloud)
- Table `user_sessions` (refresh tokens avec rotation)
- Table `revoked_tokens` (liste de révocation)
- Table `email_verifications`, `password_resets`
- Table `user_settings` (clé-valeur par tenant)
- Table `subscriptions` (lien Stripe)
- Table `webhook_events` (idempotence)
- Table `licenses` (PLI Plus Local)
- Table `outbound_emails` (log des emails transactionnels envoyés)
- Row-Level Security activée sur toutes les tables `user_id`-owned (PG uniquement)

Revision ID: 0002_m2
Revises: 0001_initial_m1
Create Date: 2026-06-22
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0002_m2"
down_revision = "0001_initial_m1"
branch_labels = None
depends_on = None


def _is_sqlite() -> bool:
    return op.get_bind().dialect.name == "sqlite"


def upgrade() -> None:
    sqlite = _is_sqlite()
    id_type = "TEXT"
    bigint = "INTEGER" if sqlite else "BIGINT"
    jsonb = "TEXT" if sqlite else "JSONB"
    default_now = "(strftime('%s','now'))" if sqlite else "EXTRACT(EPOCH FROM now())::bigint"

    # --- users ---
    op.execute(f"""
        CREATE TABLE users (
            id                  {id_type} PRIMARY KEY,
            email               TEXT NOT NULL UNIQUE,
            password_hash       TEXT NOT NULL,
            is_verified         INTEGER NOT NULL DEFAULT 0,
            plan                TEXT NOT NULL DEFAULT 'free',
            trial_ends_at       {bigint},
            stripe_customer_id  TEXT UNIQUE,
            created_at          {bigint} NOT NULL DEFAULT {default_now},
            updated_at          {bigint} NOT NULL DEFAULT {default_now},
            deleted_at          {bigint}
        )
    """)

    # --- sessions (refresh tokens avec rotation) ---
    op.execute(f"""
        CREATE TABLE user_sessions (
            id                  {id_type} PRIMARY KEY,
            user_id             {id_type} NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            refresh_token_hash  TEXT NOT NULL UNIQUE,
            user_agent          TEXT,
            ip_address          TEXT,
            issued_at           {bigint} NOT NULL DEFAULT {default_now},
            expires_at          {bigint} NOT NULL,
            rotated_at          {bigint},
            revoked_at          {bigint}
        )
    """)
    op.create_index("idx_sessions_user", "user_sessions", ["user_id"])
    op.create_index("idx_sessions_expires", "user_sessions", ["expires_at"])

    op.execute(f"""
        CREATE TABLE revoked_access_jti (
            jti         TEXT PRIMARY KEY,
            revoked_at  {bigint} NOT NULL DEFAULT {default_now},
            expires_at  {bigint} NOT NULL
        )
    """)

    # --- email verifications ---
    op.execute(f"""
        CREATE TABLE email_verifications (
            token_hash  TEXT PRIMARY KEY,
            user_id     {id_type} NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at  {bigint} NOT NULL DEFAULT {default_now},
            expires_at  {bigint} NOT NULL,
            used_at     {bigint}
        )
    """)

    # --- password resets ---
    op.execute(f"""
        CREATE TABLE password_resets (
            token_hash  TEXT PRIMARY KEY,
            user_id     {id_type} NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            created_at  {bigint} NOT NULL DEFAULT {default_now},
            expires_at  {bigint} NOT NULL,
            used_at     {bigint}
        )
    """)

    # --- user_settings (store clé-valeur par tenant) ---
    op.execute(f"""
        CREATE TABLE user_settings (
            user_id {id_type} NOT NULL,
            key     TEXT NOT NULL,
            value   TEXT,
            PRIMARY KEY (user_id, key)
        )
    """)

    # --- subscriptions (liées Stripe) ---
    op.execute(f"""
        CREATE TABLE subscriptions (
            id                     {id_type} PRIMARY KEY,
            user_id                {id_type} NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            stripe_subscription_id TEXT UNIQUE,
            stripe_price_id        TEXT,
            plan                   TEXT NOT NULL,
            status                 TEXT NOT NULL,   -- trialing, active, past_due, canceled, incomplete
            current_period_start   {bigint},
            current_period_end     {bigint},
            cancel_at_period_end   INTEGER NOT NULL DEFAULT 0,
            trial_end              {bigint},
            created_at             {bigint} NOT NULL DEFAULT {default_now},
            updated_at             {bigint} NOT NULL DEFAULT {default_now}
        )
    """)
    op.create_index("idx_subscriptions_user", "subscriptions", ["user_id"])
    op.create_index("idx_subscriptions_status", "subscriptions", ["status"])

    # --- webhook_events (idempotence Stripe) ---
    op.execute(f"""
        CREATE TABLE webhook_events (
            id              TEXT PRIMARY KEY,   -- Stripe event id
            provider        TEXT NOT NULL,      -- 'stripe' | 'sendgrid' | ...
            event_type      TEXT NOT NULL,
            received_at     {bigint} NOT NULL DEFAULT {default_now},
            processed_at    {bigint},
            payload         {jsonb}
        )
    """)

    # --- licenses (PLI Plus Local activé par clé) ---
    op.execute(f"""
        CREATE TABLE licenses (
            key_hash            TEXT PRIMARY KEY,   -- SHA-256 de la clé émise
            user_id             {id_type},          -- NULL = clé orpheline
            issued_at           {bigint} NOT NULL DEFAULT {default_now},
            expires_at          {bigint},
            plan                TEXT NOT NULL,
            stripe_invoice_id   TEXT,
            revoked_at          {bigint}
        )
    """)

    # --- outbound emails (log + anti-replay) ---
    op.execute(f"""
        CREATE TABLE outbound_emails (
            id              {id_type} PRIMARY KEY,
            user_id         {id_type},
            to_email        TEXT NOT NULL,
            template        TEXT NOT NULL,
            subject         TEXT,
            provider_msg_id TEXT,
            status          TEXT NOT NULL,   -- queued, sent, failed, bounced, delivered
            sent_at         {bigint} NOT NULL DEFAULT {default_now},
            metadata        {jsonb}
        )
    """)
    op.create_index("idx_outbound_emails_user", "outbound_emails", ["user_id"])

    # --- Row-Level Security (PostgreSQL uniquement) ---
    if not sqlite:
        for t in ("accounts", "contacts", "messages", "attachments", "drafts",
                  "sync_log", "user_settings", "subscriptions"):
            op.execute(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY")
            op.execute(f"""
                CREATE POLICY {t}_tenant_isolation ON {t}
                  USING (user_id = current_setting('pli.current_tenant', true))
                  WITH CHECK (user_id = current_setting('pli.current_tenant', true))
            """)


def downgrade() -> None:
    sqlite = _is_sqlite()
    if not sqlite:
        for t in ("accounts", "contacts", "messages", "attachments", "drafts",
                  "sync_log", "user_settings", "subscriptions"):
            op.execute(f"DROP POLICY IF EXISTS {t}_tenant_isolation ON {t}")
            op.execute(f"ALTER TABLE {t} DISABLE ROW LEVEL SECURITY")
    for t in (
        "outbound_emails", "licenses", "webhook_events", "subscriptions",
        "user_settings", "password_resets", "email_verifications",
        "revoked_access_jti", "user_sessions", "users",
    ):
        cascade = "" if sqlite else " CASCADE"
        op.execute(f"DROP TABLE IF EXISTS {t}{cascade}")
