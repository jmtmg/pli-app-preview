# PLI cloud-staging live provisioning — 2026-05-13

Statut horodaté : 2026-05-13T16:27:57Z.

Ce rapport ne contient aucune valeur de secret. Les vérifications ci-dessous listent uniquement des noms de ressources, noms de variables/secrets, états et blocages.

## Provisionné / vérifié

- GitHub : repo `jmtmg/pli-app`, environnement `staging` existant.
- Fly : app `pli-staging` existante, owner `personal`, statut `pending`, aucun déploiement applicatif encore publié.
- Fly Postgres : app `pli-staging-db` déployée en `cdg`, machine primaire démarrée, checks Fly 3/3 passing.
  - Note risque : il s'agit de Fly Postgres non managé/support communautaire ; suffisant pour staging jetable si assumé, mais backup/restore reste obligatoire avant GO staging sérieux.
- Object storage : bucket Fly/Tigris `pli-staging-attachments`, statut `created`, public `false`.
- GitHub staging variables présentes : `PLI_BASE_URL`, `PLI_APP_URL`, `PLI_CORS_ORIGINS`, `PLI_EMAIL_FROM`, `PLI_EMAIL_SMTP_PORT`, `PLI_GMAIL_REDIRECT_URI`, `PLI_MS_REDIRECT_URI`, `PLI_MS_TENANT_ID`, `PLI_S3_ENDPOINT_URL`, `PLI_S3_BUCKET`, `PLI_S3_REGION`.
- GitHub staging secrets présentes : `FLY_API_TOKEN`, `PLI_SECRET_KEY`, `PLI_CLOUD_CRYPTO_KEY`, `PLI_DATABASE_URL`, `PLI_S3_ACCESS_KEY`, `PLI_S3_SECRET_KEY`.
- Fly secrets staged sur `pli-staging` : `PLI_SECRET_KEY`, `PLI_CLOUD_CRYPTO_KEY`, `PLI_DATABASE_URL`, `PLI_S3_*`, et alias AWS/Tigris associés. Ces secrets sont staged et pas encore déployés ; `fly secrets deploy` ou `fly deploy` sera nécessaire pour les rendre actifs.

## Durcissement repo appliqué pendant cette reprise

- Ajout d'une régression secret-safe : le preflight cloud-staging bloque désormais `smtp` sans sender et sans credentials SMTP.
- `backend/pli/prod_readiness.py` bloque maintenant :
  - `PLI_EMAIL_FROM` absent/factice/invalide pour tout provider email réel ;
  - `PLI_EMAIL_SMTP_USER` absent/factice quand `PLI_EMAIL_PROVIDER=smtp` ;
  - `PLI_EMAIL_SMTP_PASSWORD` absent/factice quand `PLI_EMAIL_PROVIDER=smtp`.
- Test ciblé exécuté : `backend/tests/test_prod_readiness.py` — 13 passed.

## Bloqué / manquant avant preflight et deploy staging

- Email transactionnel réel : choisir/confirmer `smtp`, `sendgrid` ou `postmark`, puis fournir via secret manager/1Password :
  - si `smtp` : `PLI_EMAIL_PROVIDER`, `PLI_EMAIL_SMTP_HOST`, `PLI_EMAIL_SMTP_USER`, `PLI_EMAIL_SMTP_PASSWORD`, `PLI_EMAIL_FROM` validé ;
  - si API : `PLI_EMAIL_PROVIDER`, `PLI_EMAIL_API_KEY`, `PLI_EMAIL_FROM` validé.
- OAuth Gmail staging : `PLI_GMAIL_CLIENT_ID` et `PLI_GMAIL_CLIENT_SECRET` manquants ; redirect attendu : `https://staging.pli.app/auth/gmail/callback`.
- OAuth Microsoft staging : `PLI_MS_CLIENT_ID` et `PLI_MS_CLIENT_SECRET` manquants ; redirect attendu : `https://staging.pli.app/auth/microsoft/callback`; tenant actuel attendu : `common` sauf choix contraire.
- 1Password côté Mac/Hermes : le service account voit le vault `Command Center Runtime` en lecture mais n'a pas la permission de créer un nouvel item. Il peut lire les items visibles une fois créés/partagés par Jm ou la Surface.
- Frontend staging : stratégie same-origin vs hosting séparé non encore prouvée par déploiement/smoke.
- DNS/certificat `staging.pli.app`, backups/restore, smoke OAuth/email/storage : non prouvés.

## Demande transmise à la Surface

Une mission no-secret a été préparée pour Claude Code Surface / session Surface afin de créer ou partager dans 1Password un item `PLI Staging Provider Secrets` visible par le vault/runtime Hermes, sans jamais publier les valeurs dans le bus, les logs ou Telegram.

## GO / NO-GO actuel

- GO : continuer la préparation repo et la collecte officielle de secrets.
- NO-GO : lancer le workflow `Deploy staging`, `fly deploy`, `fly secrets deploy`, migrations ou smoke réel tant que email + OAuth + DNS/cert + stratégie frontend + backups ne sont pas réglés et que `cloud-staging-preflight` n'est pas vert.
