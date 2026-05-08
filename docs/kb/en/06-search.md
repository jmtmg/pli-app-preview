# Searching in your emails

PLI's search is fast — even on 500k messages. It runs on an FTS5 index (SQLite full-text search) built on top of your synced mail.

## Basic search

`Cmd/Ctrl + K` → type → Enter. Results ranked by relevance (BM25), most recent boosted.

## Advanced syntax

- `from:alice@acme.com` — specific sender
- `to:me` — addressed to you directly
- `subject:contract` — matches subject line
- `has:attachment` or `has:pdf` / `has:image`
- `after:2026-01-01 before:2026-06-30` — date range
- `is:unread` / `is:pinned` / `is:archived`
- `in:humans` / `in:notifs`

Combine with AND (default), OR, `-` for negation: `from:alice -subject:invoice`.

## Saved searches

Type your query → **Save this search** → it appears in the left rail. Updated live — no refresh needed.

## Scope

By default: all your connected accounts. Add `account:gmail_perso` to restrict.

## Limits

- Minimum 3 chars per token (to keep the index lean)
- Attachments indexed by name + OCR'd text content (Cloud + Plus Local)

## Rebuilding the index

If results feel stale: Settings → Maintenance → **Rebuild search index**. 2-15 min depending on volume. See [Search slow](29-search-slow.md).
