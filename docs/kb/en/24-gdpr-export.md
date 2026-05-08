# GDPR export

## Your right

GDPR Article 20: **right to data portability**. You can recover all data PLI holds on you, in a structured and reusable format.

## How to export

Settings → **Privacy** → **Export my data**.

Two options:

1. **Full export** (recommended): JSON + `.eml` mail files + native attachments, zipped. Expected size: 1-10 GB depending on usage.
2. **Metadata only export**: JSON without emails or attachments. For users who just want to check what we have on them.

## Delay

- Cloud: zip ready within 24 h (download email, link valid 7 days, HTTPS).
- Local: immediate, in a folder of your choice.

## Zip contents

```
pli_export_<date>/
├── manifest.json          # inventory + SHA-256 file hashes
├── account.json           # your account info (email, prefs, subscription)
├── contacts.json          # contact cards (names, notes, domains)
├── threads/
│   ├── thread_<id>/
│   │   ├── thread.json    # conversation metadata
│   │   ├── msg_001.eml    # mail 1 RFC 822 format
│   │   └── attachments/   # native attachments
│   └── ...
└── activity_log.json      # action history (archive, pin, swipe)
```

## Reimport

- In PLI: yes (button **Import a PLI export** in Privacy)
- Elsewhere: `.eml` is standard → Thunderbird, Apple Mail, Outlook accept it

## Deletion after export

Export ≠ deletion. To delete your account, see [Delete account](25-delete-account.md).

## Auditability

Each export generates an entry in `activity_log.json` (timestamp, checksums). You can verify nothing was tampered with.
