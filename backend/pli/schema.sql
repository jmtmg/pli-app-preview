-- ============================================================
--  PLI — Schéma SQLite pour mode Local (cf. doc 08-Data-Model)
--  SQLCipher requis pour chiffrement au repos
--  FTS5 requis pour recherche plein texte
-- ============================================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA synchronous = NORMAL;
PRAGMA busy_timeout = 5000;

-- ---------------- Accounts ----------------
CREATE TABLE IF NOT EXISTS accounts (
    id              TEXT PRIMARY KEY,               -- ULID
    provider        TEXT NOT NULL CHECK(provider IN ('gmail','microsoft')),
    email           TEXT NOT NULL,
    display_name    TEXT,
    oauth_access    TEXT,                           -- chiffré côté app (Keychain/Keystore)
    oauth_refresh   TEXT,
    oauth_expiry    INTEGER,                        -- epoch seconds
    history_cursor  TEXT,                           -- historyId Gmail / deltaLink Graph
    signature       TEXT,
    avatar_color    TEXT,
    last_sync_at    INTEGER,
    last_error      TEXT,
    is_active       INTEGER NOT NULL DEFAULT 1,
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    UNIQUE(provider, email)
);

-- ---------------- Contacts ----------------
-- Un contact est agrégé par **adresse email normalisée**.
CREATE TABLE IF NOT EXISTS contacts (
    id              TEXT PRIMARY KEY,
    account_id      TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    email           TEXT NOT NULL,
    email_normalized TEXT NOT NULL,                 -- lowercased, +alias stripped
    display_name    TEXT,
    company         TEXT,
    role            TEXT,
    phone           TEXT,
    notes           TEXT,
    is_muted        INTEGER NOT NULL DEFAULT 0,
    is_pinned       INTEGER NOT NULL DEFAULT 0,
    pinned_order    INTEGER,                        -- rank 1..3 si épinglé
    is_archived     INTEGER NOT NULL DEFAULT 0,      -- archive locale reversible
    kind            TEXT NOT NULL DEFAULT 'human',  -- 'human' | 'notif'
    last_msg_at     INTEGER,                        -- pour tri liste
    unread_count    INTEGER NOT NULL DEFAULT 0,
    has_attachments INTEGER NOT NULL DEFAULT 0,
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    UNIQUE(account_id, email_normalized)
);

CREATE INDEX IF NOT EXISTS idx_contacts_account_last_msg
    ON contacts(account_id, last_msg_at DESC);
CREATE INDEX IF NOT EXISTS idx_contacts_pinned
    ON contacts(account_id, is_pinned, pinned_order);
CREATE INDEX IF NOT EXISTS idx_contacts_kind
    ON contacts(account_id, kind);

-- ---------------- Messages ----------------
CREATE TABLE IF NOT EXISTS messages (
    id              TEXT PRIMARY KEY,               -- ULID interne
    account_id      TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    contact_id      TEXT NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    provider_id     TEXT NOT NULL,                  -- Gmail messageId / Graph id
    thread_id       TEXT,                           -- optionnel (Gmail threadId)
    direction       TEXT NOT NULL CHECK(direction IN ('in','out')),
    subject         TEXT,
    snippet         TEXT,
    body_text       TEXT,
    body_html       TEXT,
    from_email      TEXT NOT NULL,
    from_name       TEXT,
    to_emails       TEXT,                           -- JSON array
    cc_emails       TEXT,                           -- JSON array
    bcc_emails      TEXT,                           -- JSON array local only, never returned in public projections
    received_at     INTEGER NOT NULL,
    is_read         INTEGER NOT NULL DEFAULT 0,
    is_starred      INTEGER NOT NULL DEFAULT 0,
    has_attachments INTEGER NOT NULL DEFAULT 0,
    raw_headers     TEXT,                           -- debug / audit
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now')),
    UNIQUE(account_id, provider_id)
);

CREATE INDEX IF NOT EXISTS idx_messages_contact_time
    ON messages(contact_id, received_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_account_time
    ON messages(account_id, received_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_unread
    ON messages(account_id, is_read, received_at DESC);

-- ---------------- Attachments ----------------
CREATE TABLE IF NOT EXISTS attachments (
    id              TEXT PRIMARY KEY,
    message_id      TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    contact_id      TEXT NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    filename        TEXT NOT NULL,
    mime_type       TEXT,
    size_bytes      INTEGER,
    sha256          TEXT,
    local_path      TEXT,                           -- sous ~/.pli/att/<sha256[:2]>/<sha256>
    provider_id     TEXT,                           -- attachmentId provider
    ocr_text        TEXT,                           -- rempli par worker OCR
    created_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

CREATE INDEX IF NOT EXISTS idx_attachments_message ON attachments(message_id);
CREATE INDEX IF NOT EXISTS idx_attachments_contact ON attachments(contact_id);
CREATE INDEX IF NOT EXISTS idx_attachments_sha     ON attachments(sha256);

-- ---------------- Drafts ----------------
CREATE TABLE IF NOT EXISTS drafts (
    id              TEXT PRIMARY KEY,
    account_id      TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    contact_id      TEXT REFERENCES contacts(id) ON DELETE SET NULL,
    in_reply_to     TEXT,                           -- message_id
    to_emails       TEXT,
    cc_emails       TEXT,
    subject         TEXT,
    body_text       TEXT,
    signature_active INTEGER NOT NULL DEFAULT 1,
    updated_at      INTEGER NOT NULL DEFAULT (strftime('%s','now'))
);

-- ---------------- Sync state ----------------
CREATE TABLE IF NOT EXISTS sync_log (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id      TEXT NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    kind            TEXT NOT NULL CHECK(kind IN ('initial','incremental')),
    started_at      INTEGER NOT NULL,
    ended_at        INTEGER,
    messages_imported INTEGER NOT NULL DEFAULT 0,
    error           TEXT
);

-- ---------------- FTS5 (Full-Text Search) ----------------
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(
    subject,
    body_text,
    from_name,
    from_email,
    content='messages',
    content_rowid='rowid',
    tokenize='unicode61 remove_diacritics 2'
);

-- Triggers FTS — maintien automatique de l'index
CREATE TRIGGER IF NOT EXISTS messages_fts_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, subject, body_text, from_name, from_email)
    VALUES (new.rowid, new.subject, new.body_text, new.from_name, new.from_email);
END;
CREATE TRIGGER IF NOT EXISTS messages_fts_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, subject, body_text, from_name, from_email)
    VALUES ('delete', old.rowid, old.subject, old.body_text, old.from_name, old.from_email);
END;
CREATE TRIGGER IF NOT EXISTS messages_fts_au AFTER UPDATE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, subject, body_text, from_name, from_email)
    VALUES ('delete', old.rowid, old.subject, old.body_text, old.from_name, old.from_email);
    INSERT INTO messages_fts(rowid, subject, body_text, from_name, from_email)
    VALUES (new.rowid, new.subject, new.body_text, new.from_name, new.from_email);
END;

-- Index PJ recherche (OCR)
CREATE VIRTUAL TABLE IF NOT EXISTS attachments_fts USING fts5(
    filename,
    ocr_text,
    content='attachments',
    content_rowid='rowid',
    tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER IF NOT EXISTS attachments_fts_ai AFTER INSERT ON attachments BEGIN
    INSERT INTO attachments_fts(rowid, filename, ocr_text)
    VALUES (new.rowid, new.filename, new.ocr_text);
END;
CREATE TRIGGER IF NOT EXISTS attachments_fts_ad AFTER DELETE ON attachments BEGIN
    INSERT INTO attachments_fts(attachments_fts, rowid, filename, ocr_text)
    VALUES ('delete', old.rowid, old.filename, old.ocr_text);
END;
CREATE TRIGGER IF NOT EXISTS attachments_fts_au AFTER UPDATE ON attachments BEGIN
    INSERT INTO attachments_fts(attachments_fts, rowid, filename, ocr_text)
    VALUES ('delete', old.rowid, old.filename, old.ocr_text);
    INSERT INTO attachments_fts(rowid, filename, ocr_text)
    VALUES (new.rowid, new.filename, new.ocr_text);
END;
