# Gmail sync in error

## Quick check

Settings → **Accounts** → status of Gmail account:

- 🟢 **Active**: all good
- 🟡 **Pending**: sync running (Gmail API quota ≠ instant)
- 🔴 **Error**: click for detail

## Common errors

### `invalid_grant` or `token_expired`

Your OAuth consent has been revoked (at Google) or your Google password changed with rotating 2FA.

→ **Fix**: Settings → Accounts → **Reconnect**. Quick re-consent.

### `quota_exceeded`

Gmail rate-limits at 250 units/sec per user. Normal syncs are well under. With 500 k messages we shift to **exponential backoff** — takes longer but still completes (hours).

→ Nothing to do, let it run. You can close PLI, sync resumes at next launch.

### `rate_limit_exceeded`

Short-term version of quota. PLI honours `Retry-After` headers. Be patient.

### `insufficient_permission`

Your Google Workspace admin restricted the app. Contact them and share [this link](27-microsoft-admin.md) — same principle on the Google side: marketplace/admin/app-access.

### `connection_refused` / `network_error`

Your network blocks googleapis.com. Often seen behind corporate proxies. Test on 4G to confirm, then see [27-microsoft-admin](27-microsoft-admin.md) (identical principles).

## Reset the sync

If really stuck, Settings → Accounts → **Full resync**. ⚠️ Re-downloads everything, 30-60 min depending on volume, no impact on Gmail itself.

## Still broken

[Support](30-support.md) with the error screenshot + your user-id (Settings → About → Copy diagnostic info). We have server-side logs and can trace the cause.
