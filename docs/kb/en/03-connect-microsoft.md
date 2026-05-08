# Connect your Microsoft 365 / Outlook account

## Prerequisites

- Microsoft 365 (personal, family or business) or Outlook.com account
- If you're on a company tenant, admin must allow the app (see [Microsoft admin restrictions](27-microsoft-admin.md))

## Flow

1. PLI → **Settings → Accounts → Add account → Microsoft**
2. Redirect to `login.microsoftonline.com`
3. Pick the account (personal `@outlook.com`, `@hotmail.com`, `@live.com`, or work `@company.com`)
4. Consent screen — **Accept**
5. First sync begins

## Personal vs work/school

- **Personal** (outlook.com/hotmail.com/live.com): works out of the box
- **Work/school**: may require admin approval — app is Publisher Verified, which helps

## Requested permissions

Only Microsoft Graph Mail scopes: Mail.Read, Mail.Send, Mail.ReadWrite, offline_access. Full details in [OAuth permissions](22-oauth-permissions.md).

## "Need admin approval"

Your tenant blocks user-granted consent. Give your admin the pre-written email in [Microsoft admin restrictions](27-microsoft-admin.md).

## Hybrid Exchange / on-prem

Exchange on-premises (no Graph) is not supported today — we're collecting feedback for a possible IMAP/EWS fallback.

## IMAP fallback

Not in V1. Vote in our roadmap board if you need it.
