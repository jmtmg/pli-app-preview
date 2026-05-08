# Storage

## Cloud mode

Everything is stored **on our EU servers** (Hetzner Falkenstein, Germany). This is not a full mail vault: we keep **metadata + body + indexed attachments** to power PLI, but **the source of truth remains Gmail / Microsoft**. If you delete your PLI account, your emails stay at Google / Microsoft.

Cloud quota: **unlimited volume**, soft cap 50 GB attachments / account (above, we email you to understand your usage — no surprise billing).

## Local mode

Everything is in a **SQLCipher-encrypted (AES-256) SQLite DB** at:

- **macOS / Linux**: `~/.local/share/PLI/pli.db`
- **Windows**: `%APPDATA%\PLI\pli.db`
- **Mobile (future V1.2)**: app sandbox

Attachments live in a sibling `attachments/` folder, encrypted file-by-file.

Local quota: limited by device disk space. PLI warns when < 2 GB remain.

## Auto purge

- Cloud: none unless you request it explicitly, or you cancel (after 30-day grace).
- Local: none. You clean up (a **Archive > 6 months** button is available).

## Backup

Cloud: DB snapshots every 6 h, kept 14 days. Encrypted backups (AES-256) on offsite EU storage.

Local: **you back up** the `pli.db` file + `attachments/`. You can point Time Machine / Backblaze at them — works fine.
