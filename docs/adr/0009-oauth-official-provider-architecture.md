# ADR 0009 — Architecture OAuth officielle Gmail/Microsoft

Statut: proposé pour v1 locale, à implémenter uniquement après décision humaine et secrets gérés hors Git.

## Contexte

PLI doit connecter des boîtes Gmail et Microsoft via OAuth officiel. Le MVP local actuel fonctionne avec données démo/locales; il ne doit pas prétendre que les vrais providers sont branchés tant que les credentials, consent screens, callbacks, chiffrement et tests de révocation ne sont pas validés.

Contraintes:

- aucun secret dans le repo;
- aucun token dans les réponses API publiques;
- aucune valeur OAuth dans logs ou messages agent;
- flux provider officiels uniquement;
- scopes minimaux et consentement incrémental si besoin futur;
- séparation claire Local MVP vs Cloud/M2-M4.

## Décision

1. Conserver `gmail` et `microsoft` comme slugs provider internes.
2. Exposer au frontend uniquement `AccountSummary` sans secret, token, cursor provider ni réponse brute OAuth.
3. Stocker les secrets client hors Git:
   - dev local: `.env` gitignoré ou 1Password;
   - prod future: vault/secret manager.
4. Stocker les tokens utilisateur uniquement chiffrés au repos côté backend.
5. Utiliser `state` anti-CSRF et PKCE pour les nouveaux flux.
6. Garder les endpoints UI d’ajout de compte (`/api/auth/gmail/start`, `/api/auth/microsoft/start`) comme promesse de flux officiel, mais ne pas déclarer le provider opérationnel tant que le runbook n’a pas été exécuté.

## Matrice scopes v1

Gmail:

- identité: `openid`, `email`, `profile`;
- lecture: `https://www.googleapis.com/auth/gmail.readonly`;
- actions: `https://www.googleapis.com/auth/gmail.modify`;
- envoi: `https://www.googleapis.com/auth/gmail.send`.

Microsoft Graph:

- identité: `openid`, `profile`, `email`, `User.Read`;
- refresh: `offline_access`;
- lecture: `Mail.Read`;
- actions: `Mail.ReadWrite`;
- envoi: `Mail.Send`.

Hors scope v1:

- Drive/Docs/Calendar/Photos;
- Files/Sites/Calendars/Contacts Microsoft;
- permissions application-wide non déléguées;
- accès admin global;
- extension de scopes sans information utilisateur.

## Callback URLs prévues

Local:

- Gmail: `http://localhost:8000/auth/gmail/callback`
- Microsoft: `http://localhost:8000/auth/microsoft/callback`

Prod future:

- HTTPS uniquement, domaine officiel, URL exacte déclarée chez chaque provider.

## Stockage et redaction

Champs DB sensibles envisagés:

- `oauth_access`
- `oauth_refresh`
- `oauth_expiry`
- `history_cursor` / delta provider

Règles:

- chiffrement avant écriture;
- pas de projection frontend;
- pas de logs en clair;
- scan secrets pré-commit obligatoire;
- rotation immédiate si fuite soupçonnée.

## Vérifications avant activation runtime

- Tests backend: callback refuse state absent/invalide/réutilisé.
- Tests backend: `GET /accounts` n’expose aucun token ni cursor.
- Tests backend: tokens persistés chiffrés.
- Tests provider avec compte de test dédié uniquement.
- Test révocation/déconnexion: suppression locale du token et appel provider si possible.
- Documentation utilisateur: scopes demandés, révocation, limites Local/Cloud.

## Conséquences

Positives:

- prépare OAuth réel sans secret;
- réduit risque de fuite;
- clarifie la promesse produit.

Négatives:

- pas de vraie connexion provider tant que les credentials officiels et revues providers ne sont pas faits;
- certains documents historiques M2-M4 restent aspirationnels et hors gate MVP local.

## Références

- `docs/runbooks/oauth-gmail-setup.md`
- `docs/runbooks/oauth-microsoft-setup.md`
- `docs/kb/fr/22-oauth-permissions.md`
- `docs/kb/en/22-oauth-permissions.md`
