# Connect your Gmail account

## Prerequisites

- An active Gmail or Google Workspace account
- Active web session on Google (so OAuth flow doesn't ask you to re-login)

## Flow

1. PLI → **Settings → Accounts → Add account → Gmail**
2. Redirect to `accounts.google.com` (Google domain — check the URL)
3. Pick the account to connect
4. Screen "PLI wants to access your Gmail" — **Allow**
5. Back in PLI, initial sync starts

## Requested permissions

Only the minimum needed: read/send/modify labels on your emails. See [OAuth permissions](22-oauth-permissions.md) for the full list.

## Sync duration

- **< 5 k messages**: 1-2 min
- **5-50 k messages**: 5-15 min
- **> 50 k messages**: 30-60 min (background, you can use PLI right away)

## Workspace with admin restrictions

If your admin blocks third-party apps, you'll see `admin_policy_enforced`. Ask them to allow `client_id` (visible in the error). See [OAuth permissions](22-oauth-permissions.md).

## 2FA and App Passwords

Not needed. OAuth 2.0 handles it. Forget the old "app passwords" — PLI never asks for your Google password.

## Multiple Gmail accounts

Unlimited, even on the free plan. Each shows up in the side menu.

## Disconnecting

Settings → Accounts → **⋮ → Disconnect**. Instantly revokes the token on our side. To also revoke on Google: [myaccount.google.com/permissions](https://myaccount.google.com/permissions).
