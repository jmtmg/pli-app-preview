# Local vs Cloud mode

## Cloud (hosted by PLI)

PLI-hosted, EU servers (Hetzner Falkenstein, Germany). Your emails sync via IMAP/Graph to PLI, indexed, served across devices.

- ✅ Multi-device (web + desktop + mobile soon)
- ✅ Automatic backups, no upkeep
- ✅ Cross-device search, pins, snoozes
- ⚠️ Your metadata (not content, but headers) transit through our servers
- AES-256 encryption at rest server-side, HTTPS/TLS 1.3 in transit

## Local (PLI Plus)

App installed on your Mac / PC / Linux. All data stays on your machine. See [Local encryption](23-local-encryption.md).

- ✅ Nothing leaves your device (zero-knowledge)
- ✅ Works offline
- ✅ SQLCipher AES-256 encryption
- ⚠️ Single device (sharing your DB across devices = manual file copy)
- ⚠️ You own backups

## Which to pick

- **Individual, privacy-focused, 1 device** → Local
- **Multi-device, minimum friction** → Cloud
- **Unsure** → Start Cloud (14-day trial), switch to Local anytime

## Switching

- Cloud → Local: buy Plus license, export data, import into Local. See [Change plan](18-change-plan.md).
- Local → Cloud: subscribe Cloud, auto-import from local install.

## Cost

- Cloud: 7 €/month or 70 €/year
- Local: 49 € one-time or 5 €/month

Details: [Plans](17-plans.md).

## Beta

During M4 beta, **both modes are free** and unlocked for invited users.
