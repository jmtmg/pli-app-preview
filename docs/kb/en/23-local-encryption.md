# Local mode encryption

## Tech used

**SQLCipher**: a SQLite extension that encrypts the entire `.db` file with AES-256-CBC + HMAC-SHA512 for integrity. No leaf table is ever on disk in plaintext.

**Attachments** live on disk (in `attachments/`), each file encrypted AES-256-GCM with a key derived from your master key.

## Master key

Derived from your **PLI Plus password** (PBKDF2-SHA256, 256 000 iterations, per-install unique salt). Never stored in clear.

The master key unlocks the DB at startup and stays **in RAM only** during use.

## If you forget your password

There's **no backdoor**. That's the point of end-to-end encryption. You can:

1. Reinstall PLI (fresh install = new password), reconnect OAuth → your emails return from Google/Microsoft, you only lose **contact notes + local rules + pins**
2. Try to remember (grab a coffee) 🙂

We **strongly** recommend a password manager (Bitwarden, 1Password, iCloud Keychain).

## Recovery phrase

No. Deliberately. Adding a recovery phrase = adding an attack vector. Local mode aims for **maximum confidentiality** — password management is on you.

## Integrity check

At launch, PLI checks the DB's HMAC. If the DB has been altered (disk corruption, external injection) → alert and write-lock. You can then restore from your backup.

## Audits

SQLCipher is open-source audited (Zetetic). The [SEC-001 blueprint](../../adr/ADR-001-security-baseline.md) details our parameter choices.
