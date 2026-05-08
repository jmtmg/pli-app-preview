# Search is slow

## What's normal

- **1-30 k messages**: < 200 ms, feels instant
- **30-200 k messages**: 200-600 ms, slightly delayed feel
- **> 200 k messages**: 600-1500 ms, "a bit long"

If you're beyond these orders of magnitude → problem, read on.

## Common causes

### Corrupted FTS5 index (Local)

Can happen after a disk crash or an interrupted update.

→ Settings → **Maintenance** → **Rebuild search index**. 2-15 min depending on volume. No impact on your data.

### Cold cache (Cloud)

On first hit after a long idle, the Postgres cache is cold. Wait 2-3 queries, it warms up.

### Too many stacked filters

"Humans + Unread + With attachment + date + term" = cartesian product. PLI simplifies but keeps search fast by simplifying. Try **one filter at a time** first.

### Query too broad

`a` or `de` → the DB must scan a lot. PLI blocks tokens < 3 chars by default, but think about narrowing.

## Accelerators

- **Advanced syntax**: `from:alice@acme.com subject:contract` → the index loves operators
- **Scope**: restrict to one account if you have several
- **Period**: `after:2025-01-01` divides the search area by N

## If you hit something really slow

[Support](30-support.md) with your exact query + approximate volume. Helps us prioritize optimization (we monitor pli_search_p95_seconds on the SRE side).
