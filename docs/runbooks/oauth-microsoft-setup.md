# Runbook — OAuth Microsoft Graph officiel

Audience: opérateur humain. Ce runbook prépare le flux officiel Microsoft; il ne doit pas être exécuté par un agent autonome, car il implique un compte Azure/Microsoft Entra, un tenant et des choix de publication.

Objectif v1 locale: savoir exactement quoi configurer plus tard, sans introduire de secret dans le repo.

## 1. Pré-requis

- Accès à Microsoft Entra admin center ou Azure Portal.
- Décision de mode d’app:
  - dev/local: single tenant ou comptes personnels selon compte de test;
  - bêta/prod: multi-tenant uniquement après vérification publisher et revue sécurité.
- Backend PLI lancé localement sur `http://localhost:8000`.
- Frontend PLI local sur `http://localhost:5173`.

## 2. Créer l’app registration

1. Ouvrir Microsoft Entra admin center → Identity → Applications → App registrations → New registration.
2. Nom recommandé: `PLI dev`.
3. Supported account types:
   - dev contrôlée: `Accounts in this organizational directory only`;
   - bêta/prod: `Accounts in any organizational directory and personal Microsoft accounts`, seulement après décision de publication.
4. Redirect URI platform `Web`:
   - local: `http://localhost:8000/auth/microsoft/callback`.
   - prod future: domaine HTTPS officiel uniquement.

## 3. Scopes Microsoft Graph minimaux

Scopes délégués v1 envisagés:

- `openid`, `profile`, `email`, `User.Read` — identité du compte connecté.
- `offline_access` — refresh token officiel.
- `Mail.Read` — lecture et sync initiale/incrémentale.
- `Mail.ReadWrite` — marquer lu, déplacer/archiver, appliquer actions conversation.
- `Mail.Send` — envoi depuis le compte utilisateur.

Scopes explicitement hors v1:

- `Files.*`, `Sites.*`, `Calendars.*`, `Contacts.*`.
- Permissions application-wide non déléguées.
- Accès admin global.

## 4. Client secret / certificat

Dev local:

- Créer un client secret court-vivant uniquement dans Entra.
- Le copier dans un stockage local gitignoré ou 1Password.
- Ne jamais écrire la valeur dans Git, docs, issues, logs ou messages agent.

Prod future:

- Préférer certificat ou secret géré par vault.
- Rotation planifiée.
- Aucun secret dans image Docker ni frontend.

Variables attendues côté backend, à renseigner seulement hors Git:

- `PLI_MS_CLIENT_ID`
- `PLI_MS_CLIENT_SECRET`
- `PLI_MS_TENANT_ID` ou valeur `common` selon mode retenu
- `PLI_MS_REDIRECT_URI`

## 5. Validation locale future

Quand le code runtime sera branché:

1. Démarrer backend et frontend localement.
2. Ouvrir `/auth/microsoft/start`.
3. Vérifier redirection vers `login.microsoftonline.com`.
4. Accepter les scopes avec un compte de test.
5. Vérifier callback local puis présence du compte dans `GET /accounts`.
6. Vérifier que `GET /accounts` n’expose jamais de tokens, secret client, refresh token, delta link ou raw auth response.
7. Lancer sync de démonstration sur une boîte test uniquement.

## 6. Erreurs fréquentes

- `AADSTS50011 redirect_uri mismatch`: l’URI Entra ne correspond pas exactement au backend.
- `admin_policy_enforced`: tenant d’entreprise bloquant les apps tierces; demander consentement admin ou utiliser compte de test autorisé.
- `invalid_client`: mauvais client ID/secret, secret expiré, tenant incorrect.
- refresh impossible: `offline_access` absent ou mode app incompatible.

## 7. Règles de sécurité

- Fail closed si `state` OAuth inconnu, expiré ou réutilisé.
- PKCE obligatoire pour tout nouveau flux.
- Tokens chiffrés au repos.
- Logs redactés: jamais de `code`, `access_token`, `refresh_token`, `id_token`, client secret ou Authorization header.
- Révocation officielle documentée côté Microsoft + suppression locale PLI.

## Statut

Préparation documentaire uniquement. Aucun secret créé, aucun flux Microsoft réel branché par cette étape v1.
