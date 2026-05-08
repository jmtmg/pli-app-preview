# Email send failing

## Symptoms

You click **Send**, the mail stays in **Drafts** or sits in **Outbox** without leaving.

## Diagnosis

Open the draft. At the bottom, status shows:

- 🟡 **In progress**: be patient, sending (seconds max)
- 🔴 **Failed**: click the badge for error code

## Common codes

### `quota_exceeded` (Gmail)

Gmail caps at **500 recipients/day** for personal accounts, **2 000** for Workspace. Reset on a rolling 24 h.

→ Wait. If recurring, upgrade to Workspace (or spread over days).

### `recipient_rejected`

A recipient address is invalid/closed. PLI shows which one. Fix and resend.

### `message_too_large`

Gmail max 25 MB total (body + attachments). Microsoft max 20 MB. Above, PLI offers a **download link** (expires at 30 days, hosted by us, encrypted).

### `attachment_blocked`

Some extensions are blocked on the provider side (`.exe`, `.js`, `.bat`). Zip them before sending (Gmail also blocks zips containing `.exe`).

### `smtp_auth_failed`

Your OAuth token expired (rare, auto-renews). → Reconnect the account in Settings.

### `rate_limited` (Microsoft)

Microsoft Graph caps at **30 messages/min**. For bulk sends, PLI automatically throttles (can take minutes, no error).

## Queue stuck

Settings → **Accounts** → **Clear outbox**. Warning: unsent messages go back to drafts, resend them yourself.

## Delivery confirmation

PLI doesn't do standard read receipts — it's a recipient-side setting and unreliable. For legal confirmation (registered mail), use a service like Yousign / Registered Email.

## Nothing works

[Support](30-support.md) with the attempt timestamp and the error code.
