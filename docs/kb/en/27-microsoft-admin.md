# Microsoft 365 — admin restrictions

In a Microsoft 365 / Azure AD organization, an administrator can block third-party apps. If you see an error **"Need admin approval"** or **AADSTS65001**, that's the case.

## Message to forward to your admin

> Hi,
>
> I'd like to use PLI, an alternative mail client from JMJ Consulting (France). PLI requests the following OAuth scopes:
>
> - Mail.Read, Mail.Send, Mail.ReadWrite (personal mailbox access)
> - offline_access, openid, profile, email, User.Read
>
> The app is **Publisher Verified** on Microsoft. You can authorize it from Azure AD:
>
> 1. [portal.azure.com](https://portal.azure.com) → Azure Active Directory → Enterprise applications → All applications → Search "PLI"
> 2. Set to **User consent allowed** OR grant global **Admin consent** if you prefer not to let each user consent.
>
> PLI security documentation: https://pli.app/security
> Privacy policy: https://pli.app/privacy
>
> Thanks,

## On the user side while waiting

You can use PLI with a personal Gmail account in the meantime, or ask for a temporary exception (many admins grant "per-user consent").

## Corporate proxy / firewall

PLI talks to:

- `graph.microsoft.com` (Microsoft Graph API)
- `login.microsoftonline.com` (OAuth)
- `api.pli.app` (PLI backend)
- `*.pli.app` (assets, docs)

All HTTPS/443. Allowlist if your proxy filters aggressively.

## DLP / audit

PLI does not export emails to countries outside the EU. A PLI-side audit log (who accessed what) is available on request ([support](30-support.md)) for enterprise accounts.
