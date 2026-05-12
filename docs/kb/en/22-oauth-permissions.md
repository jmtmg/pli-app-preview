# OAuth permissions (Gmail / Microsoft)

## What we ask for (Gmail)

Google scopes requested:

- `gmail.readonly` → read your mail and labels
- `gmail.send` → send from PLI (using your Gmail address)
- `gmail.modify` → mark as read, archive, pin (via labels)
- `openid email profile` → identify your account

We **do not** request:

- Drive, Docs, Calendar, Contacts, Photos access
- `gmail.settings.*` (we don't touch your Gmail filters)
- `gmail.metadata` (a degraded version we don't use)

## What we ask for (Microsoft Graph)

- `Mail.Read` → read
- `Mail.Send` → send
- `Mail.ReadWrite` → mark / move
- `offline_access` → refresh token (otherwise you'd reconnect hourly)
- `openid profile email User.Read`

## Revocation

You can revoke anytime on the Google or Microsoft side:

- Google: [myaccount.google.com/permissions](https://myaccount.google.com/permissions) → PLI → "Remove access"
- Microsoft: [myaccount.microsoft.com](https://myaccount.microsoft.com/) → Applications → PLI → Remove

In PLI, Settings → **Accounts** → **Disconnect** does the same + wipes our refresh token from our DB.

## Certification & audit

For a real beta/prod release, PLI must complete the appropriate provider reviews before claiming verified status: Google OAuth verification (brand review + privacy policy depending on scopes) and Microsoft Multi-Tenant + Publisher Verified if multi-tenant mode is retained.

## Least privilege

We apply the **least necessary** principle. If a feature needs a new scope, we warn you in-app before broadening (OAuth 2.0 incremental consent).
