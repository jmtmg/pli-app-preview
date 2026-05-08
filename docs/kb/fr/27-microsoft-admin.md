# Microsoft 365 — restrictions admin

Dans une organisation Microsoft 365 / Azure AD, un administrateur peut bloquer les apps tierces. Si tu vois une erreur **"Need admin approval"** ou **AADSTS65001**, c'est ce cas.

## Message à transmettre à ton admin

> Bonjour,
>
> Je souhaite utiliser PLI, un client mail alternatif édité par JMJ Consulting (France). PLI demande les scopes OAuth suivants :
>
> - Mail.Read, Mail.Send, Mail.ReadWrite (accès boîte mail personnelle)
> - offline_access, openid, profile, email, User.Read
>
> L'app est **Publisher Verified** côté Microsoft. Vous pouvez l'autoriser depuis Azure AD :
>
> 1. [portal.azure.com](https://portal.azure.com) → Azure Active Directory → Enterprise applications → All applications → Rechercher "PLI"
> 2. Passer à **User consent allowed** OU accorder **Admin consent** global si vous préférez ne pas laisser chaque utilisateur consentir.
>
> Documentation PLI sécurité : https://pli.app/security
> Politique de confidentialité : https://pli.app/privacy
>
> Merci,

## Côté utilisateur pendant l'attente

Tu peux utiliser PLI avec un compte Gmail personnel en attendant, ou demander une exception temporaire (beaucoup d'admins accordent "per-user consent").

## Proxy / firewall entreprise

PLI communique avec :

- `graph.microsoft.com` (Microsoft Graph API)
- `login.microsoftonline.com` (OAuth)
- `api.pli.app` (backend PLI)
- `*.pli.app` (assets, docs)

Tous en HTTPS/443. À allowlister si ton proxy filtre agressivement.

## DLP / audit

PLI n'extrait pas les mails vers des pays hors UE. Audit log côté PLI (qui a accédé à quoi) disponible sur demande ([support](30-support.md)) pour les comptes entreprise.
