# PLI — matrice secrets/OAuth cloud-staging, sans valeurs

Statut : préparation secret-safe uniquement. Ce document liste les noms exacts et les lieux officiels de stockage/import, sans valeur réelle, sans déploiement, sans DNS et sans modification de providers.

## Sources lues

- `PLI_FINAL_FUNCTIONAL_STATUS.md`
- `reports/cloud-staging-readiness-2026-05-13.md`
- `reports/cloud-production-go-no-go-2026-05-13.md`
- `docs/runbooks/cloud-staging.md`
- `docs/runbooks/production-readiness.md`
- `.env.staging.example`
- `.github/workflows/ci.yml`
- `.github/workflows/deploy-staging.yml`
- compléments OAuth déjà présents : `docs/runbooks/oauth-gmail-setup.md`, `docs/runbooks/oauth-microsoft-setup.md`, `docs/adr/0009-oauth-official-provider-architecture.md`

## Règles de sécurité

- Ne jamais lire, afficher, copier ou inventer les valeurs de `.env.staging`, secrets GitHub, Fly secrets, OAuth client secrets, DB URLs, clés S3, clés email ou tokens.
- Ne jamais utiliser `--show-env-keys` contre un `.env.staging` réel : il est secret-safe pour les clés sensibles, mais il peut imprimer des valeurs de config non marquées comme sensibles.
- Ne jamais passer `KEY=value` en argument shell pour un secret : privilégier UI provider, prompt sécurisé, stdin depuis un gestionnaire, ou import secret manager approuvé.
- `.env.staging` local, si nécessaire, doit rester gitignoré et en permissions `600`; il est un cache privé temporaire, pas la source de vérité.
- Toute création cloud, import secret, OAuth consent, changement DNS, déploiement, migration ou restart nécessite confirmation explicite.

## Hypothèses staging actuelles

- Backend API cible : Fly app `pli-staging`, région `cdg`, healthcheck `/health`.
- URL API proposée : `https://staging.pli.app`.
- Frontend cloud : non tranché. Deux modes possibles :
  - même origine : `PLI_APP_URL`, `VITE_API_URL` et `PLI_CORS_ORIGINS` pointent sur `https://staging.pli.app` ;
  - hosting séparé : `PLI_APP_URL` et `PLI_CORS_ORIGINS` doivent utiliser l'origine HTTPS exacte du frontend, tandis que `VITE_API_URL` reste l'URL HTTPS de l'API.
- `PLI_ENABLE_M2=false` reste la posture staging MVP tant que auth/billing/RGPD M2-M4 ne sont pas validés comme gate cloud.

## Légende stockage/import

- Fly runtime : valeurs disponibles à l'app Fly. Non-secrets dans `fly.toml [env]` ou variables app ; secrets via Fly secrets uniquement.
- GitHub Actions staging : environnement GitHub `staging`, avec `secrets.*` pour secrets et `vars.*` pour config non secrète.
- Provider console : console officielle du fournisseur, source primaire du credential ou de la ressource.
- Local handle : 1Password, Keychain, ou autre gestionnaire approuvé ; jamais un fichier commité.

## Matrice runtime, URLs et CORS

| Nom | Présence staging attendue | Stockage/import officiel | Notes |
|---|---|---|---|
| `PLI_MODE` | requis, `cloud` | `fly.toml [env]`, GitHub env job, `.env.staging` privé | Gate preflight `cloud-v1`. |
| `PLI_DEBUG` | requis, `false` | GitHub env job / Fly env | Bloquant si actif. |
| `PLI_DEMO` | requis, `false` | GitHub env job / Fly env | Bloquant si actif. |
| `PLI_ENABLE_M2` | requis, `false` pour MVP cloud | `fly.toml [env]`, GitHub env job | Si activé, Stripe/auth M2 deviennent bloquants. |
| `PLI_BASE_URL` | requis | `fly.toml [env]`, GitHub `vars.PLI_BASE_URL`, `.env.staging` privé | URL publique HTTPS de l'API. Actuel proposé : `https://staging.pli.app`. |
| `PLI_APP_URL` | requis | `fly.toml [env]`, GitHub `vars.PLI_APP_URL`, `.env.staging` privé | Origine frontend HTTPS exacte. À ajuster si frontend séparé. |
| `PLI_CORS_ORIGINS` | requis | `fly.toml [env]`, GitHub `vars.PLI_CORS_ORIGINS`, `.env.staging` privé | JSON list string, sans wildcard, sans localhost pour staging exposé. Même origine proposée : `["https://staging.pli.app"]`. |
| `VITE_API_URL` | requis pour build frontend staging | provider de hosting frontend / pipeline frontend, `.env.staging` si build local | Pas consommé par le backend Fly. Doit pointer vers l'API HTTPS. |
| `VITE_PLI_MODE` | requis pour build frontend staging | provider de hosting frontend / pipeline frontend, `.env.staging` si build local | Valeur attendue : `cloud`. |

## Matrice secrets applicatifs et crypto

| Nom | Présence staging attendue | Provider/source officielle | Stockage/import officiel | Notes |
|---|---|---|---|---|
| `PLI_SECRET_KEY` | requis, secret fort | généré dans un gestionnaire approuvé | Fly secrets, GitHub `secrets.PLI_SECRET_KEY`, Local handle | Jamais imprimé. Bloquant si absent/trop court/factice. |
| `PLI_CLOUD_CRYPTO_KEY` | requis, clé Fernet valide | généré dans un gestionnaire approuvé | Fly secrets, GitHub `secrets.PLI_CLOUD_CRYPTO_KEY`, Local handle | Sert au chiffrement cloud au repos. Ne pas générer dans un shell qui imprime dans logs. |
| `PLI_SENTRY_DSN` | optionnel | Sentry/project observabilité, si retenu | Fly secrets ou GitHub secret si considéré sensible ; sinon var protégée | Le template le liste, mais le deploy workflow ne le mappe pas actuellement. |

## Matrice PostgreSQL et stockage objet

| Nom | Présence staging attendue | Provider/source officielle | Stockage/import officiel | Notes |
|---|---|---|---|---|
| `PLI_DATABASE_URL` | requis | console PostgreSQL managé retenue : Fly Postgres, Neon, Supabase, Scaleway ou autre | Fly secrets, GitHub `secrets.PLI_DATABASE_URL`, Local handle | Contient un mot de passe. Migrations + backup/restore requis avant GO. |
| `PLI_S3_ENDPOINT_URL` | requis | console object storage retenue : Cloudflare R2, Scaleway, AWS S3 ou équivalent | GitHub `vars.PLI_S3_ENDPOINT_URL`; Fly env ou secret si endpoint privé | Le preflight vérifie la présence et la forme HTTPS publique pour cloud-v1 exposé. |
| `PLI_S3_ACCESS_KEY` | requis | console object storage, credential least-privilege | Fly secrets, GitHub `secrets.PLI_S3_ACCESS_KEY`, Local handle | Ne jamais exposer dans logs. |
| `PLI_S3_SECRET_KEY` | requis | console object storage, credential least-privilege | Fly secrets, GitHub `secrets.PLI_S3_SECRET_KEY`, Local handle | Secret critique. |
| `PLI_S3_BUCKET` | requis | console object storage | GitHub `vars.PLI_S3_BUCKET`; Fly env ou secret si politique interne | Bucket proposé : `pli-staging-attachments`, à créer explicitement. |
| `PLI_S3_REGION` | requis si provider l'exige ou si différent du défaut | console object storage | GitHub var / Fly env / `.env.staging` privé | Présent dans le template et mappé dans le workflow staging comme var non secrète ; valeur attendue selon provider (ex. `fr-par` si Scaleway confirmé). |

## Matrice email transactionnel

Choisir exactement un provider réel pour staging : `smtp`, `sendgrid` ou `postmark`. `memory` et MailHog ne sont pas acceptables pour un staging exposé.

| Nom | Présence staging attendue | Provider/source officielle | Stockage/import officiel | Notes |
|---|---|---|---|---|
| `PLI_EMAIL_PROVIDER` | requis | décision opérateur | GitHub `vars.PLI_EMAIL_PROVIDER`, Fly env | Valeurs attendues : `smtp`, `sendgrid` ou `postmark`. |
| `PLI_EMAIL_FROM` | requis opérationnel | provider email + domaine sender validé | GitHub var / Fly env | SPF/DKIM/DMARC à valider. Présent dans template et mappé comme var staging, mais le sender n'est pas provisionné/validé. |
| `PLI_EMAIL_API_KEY` | requis si `sendgrid` ou `postmark` | console SendGrid/Postmark | Fly secrets, GitHub `secrets.PLI_EMAIL_API_KEY`, Local handle | Non requis si SMTP pur. |
| `PLI_EMAIL_SMTP_HOST` | requis si `smtp` | console SMTP/provider | GitHub var / Fly env | Ne doit pas être local pour staging exposé. |
| `PLI_EMAIL_SMTP_PORT` | requis si `smtp` | console SMTP/provider | GitHub var / Fly env | Mappé comme var staging. |
| `PLI_EMAIL_SMTP_USER` | requis si `smtp` avec auth | console SMTP/provider | GitHub secret ou var protégée selon sensibilité | Mappé comme secret staging par défaut pour éviter exposition inutile. |
| `PLI_EMAIL_SMTP_PASSWORD` | requis si `smtp` avec auth | console SMTP/provider | Fly secrets, GitHub secret, Local handle | Mappé comme secret staging ; ne jamais afficher. |

## Matrice OAuth Gmail staging

Provider officiel : Google Cloud Console. L'app staging doit être une app OAuth officielle dédiée ou explicitement isolée de la prod. Activer Gmail API ; configurer consent screen et test users selon le runbook.

Redirect staging exact à déclarer côté Google :

```text
https://staging.pli.app/auth/gmail/callback
```

Scopes v1 documentés : `openid`, `email`, `profile`, `https://www.googleapis.com/auth/gmail.readonly`, `https://www.googleapis.com/auth/gmail.modify`, `https://www.googleapis.com/auth/gmail.send`.

| Nom | Présence staging attendue | Stockage/import officiel | Notes |
|---|---|---|---|
| `PLI_GMAIL_CLIENT_ID` | requis | GitHub `vars.PLI_GMAIL_CLIENT_ID`, Fly env ou Fly secret, Local handle | Identifiant non secret strict, mais à garder dans config protégée. |
| `PLI_GMAIL_CLIENT_SECRET` | requis | Fly secrets, GitHub `secrets.PLI_GMAIL_CLIENT_SECRET`, Local handle | Secret provider. Rotation côté Google si fuite suspectée. |
| `PLI_GMAIL_REDIRECT_URI` | requis | GitHub `vars.PLI_GMAIL_REDIRECT_URI`, Fly env | Doit être exactement l'URI déclarée dans Google Cloud Console. |

## Matrice OAuth Microsoft staging

Provider officiel : Microsoft Entra admin center / Azure Portal, App registrations. L'app staging doit être séparée ou clairement isolée de la prod.

Redirect staging exact à déclarer côté Microsoft :

```text
https://staging.pli.app/auth/microsoft/callback
```

Scopes v1 documentés : `openid`, `profile`, `email`, `User.Read`, `offline_access`, `Mail.Read`, `Mail.ReadWrite`, `Mail.Send`.

| Nom | Présence staging attendue | Stockage/import officiel | Notes |
|---|---|---|---|
| `PLI_MS_CLIENT_ID` | requis | GitHub `vars.PLI_MS_CLIENT_ID`, Fly env ou Fly secret, Local handle | Identifiant d'app registration. |
| `PLI_MS_CLIENT_SECRET` | requis | Fly secrets, GitHub `secrets.PLI_MS_CLIENT_SECRET`, Local handle | Secret/certificat provider. Rotation côté Entra si fuite suspectée. |
| `PLI_MS_REDIRECT_URI` | requis | GitHub `vars.PLI_MS_REDIRECT_URI`, Fly env | Doit être exactement l'URI déclarée dans Entra. |
| `PLI_MS_TENANT_ID` | requis | GitHub `vars.PLI_MS_TENANT_ID`, Fly env | `common` acceptable seulement si ce mode est décidé ; sinon tenant ID dédié. |

## Billing/Stripe : rester désactivé pour staging MVP

| Nom | Présence staging attendue | Stockage/import officiel | Notes |
|---|---|---|---|
| `PLI_STRIPE_SECRET_KEY` | absent/empty tant que `PLI_ENABLE_M2=false` | Stripe dashboard + secret manager seulement si M2 autorisé | Ne pas activer sans décision M2/cloud billing. |
| `PLI_STRIPE_WEBHOOK_SECRET` | absent/empty tant que `PLI_ENABLE_M2=false` | Stripe dashboard + secret manager seulement si M2 autorisé | Idem. |
| `PLI_STRIPE_PRICE_MONTHLY` | absent/empty tant que `PLI_ENABLE_M2=false` | Stripe dashboard / GitHub var si M2 autorisé | Idem. |
| `PLI_STRIPE_PRICE_YEARLY` | absent/empty tant que `PLI_ENABLE_M2=false` | Stripe dashboard / GitHub var si M2 autorisé | Idem. |
| `PLI_STRIPE_TRIAL_DAYS` | optionnel/default, non-gate tant que M2 off | GitHub var / Fly env si M2 autorisé | Template à 14 jours ; deploy workflow ne le mappe pas. |

## Sync knobs non secrets

| Nom | Présence staging attendue | Stockage/import officiel | Notes |
|---|---|---|---|
| `PLI_INITIAL_SYNC_DAYS` | optionnel/default | GitHub var / Fly env | Présent dans template, absent du deploy workflow actuel. |
| `PLI_INCREMENTAL_SYNC_INTERVAL_S` | optionnel/default | GitHub var / Fly env | Présent dans template, absent du deploy workflow actuel. |
| `PLI_SYNC_MAX_RETRIES` | optionnel/default | GitHub var / Fly env | Présent dans template, absent du deploy workflow actuel. |

## Token de déploiement GitHub Actions

| Nom | Présence staging attendue | Stockage/import officiel | Notes |
|---|---|---|---|
| `FLY_API_TOKEN` | requis uniquement pour le workflow `deploy-staging` | GitHub `secrets.FLY_API_TOKEN`, généré côté Fly avec scope minimal | Ce n'est pas un secret runtime PLI. Ne pas importer dans l'app Fly. |

## État du workflow `deploy-staging.yml`

Le workflow de déploiement backend mappe les clés runtime bloquantes principales pour l'étape preflight uniquement : mode/debug/demo/M2, app secret, DB, crypto cloud, S3 endpoint/région/access/secret/bucket, email provider/from/API key/SMTP host-port-user-password, URLs/CORS et OAuth Gmail/Microsoft. `FLY_API_TOKEN` est limité à l'étape de déploiement. L'action Fly est référencée par commit immuable plutôt que `master`, avec version `flyctl` explicite.

Points à trancher avant un staging réel :

- Frontend : `VITE_API_URL` et `VITE_PLI_MODE` ne sont pas utilisés par le workflow backend ; ils doivent être configurés dans le pipeline/hosting frontend retenu.
- Email : le workflow mappe les noms, mais le provider, le sender et les credentials SMTP/API ne sont pas provisionnés ni validés par l'utilisateur.
- S3 : `PLI_S3_REGION` est mappé, mais la valeur (`fr-par`, `eu-west-3`, etc.) dépend du fournisseur explicitement confirmé.
- Observabilité/sync : `PLI_SENTRY_DSN` et `PLI_INITIAL_SYNC_DAYS` / `PLI_INCREMENTAL_SYNC_INTERVAL_S` / `PLI_SYNC_MAX_RETRIES` sont présents dans le template mais non mappés dans le workflow ; les laisser par défaut ou les ajouter comme vars/secrets après décision.
- Stripe : les `PLI_STRIPE_*` ne doivent pas être mappés tant que `PLI_ENABLE_M2=false` reste la décision MVP.

## Commandes de preflight qui n'impriment aucune valeur

Toutes les commandes ci-dessous sont read-only côté repo/local, sauf mention explicite. Elles ne doivent pas être confondues avec un import ou un déploiement.

### Vérifier le dry-run Makefile et le template

```bash
cd /Users/jm/context-engine/projects/pli-app
make -n cloud-staging-preflight
cd backend && .venv/bin/python scripts/prod_readiness_check.py --target cloud-v1 --env staging --dotenv ../.env.staging.example
```

Résultat attendu avec le template : `status=blocked`, sans valeur imprimée. Les blockers attendus portent sur les noms de clés manquantes/factices seulement.

### Lister les noms attendus depuis le template, sans valeurs

```bash
cd /Users/jm/context-engine/projects/pli-app
python3 - <<'PY'
from pathlib import Path
for raw in Path('.env.staging.example').read_text(encoding='utf-8').splitlines():
    line = raw.strip()
    if line and not line.startswith('#') and '=' in line:
        print(line.split('=', 1)[0])
PY
```

### Vérifier un `.env.staging` privé sans afficher son contenu

```bash
cd /Users/jm/context-engine/projects/pli-app
test -f .env.staging && stat -f '%N mode=%Lp' .env.staging
make cloud-staging-preflight
```

`make cloud-staging-preflight` appelle `prod_readiness_check.py` sans `--show-env-keys`; il ne doit pas afficher les valeurs.

### Vérifier GitHub environment staging par noms uniquement

À exécuter seulement avec un `gh` authentifié et autorisé, sans afficher de valeurs :

```bash
gh secret list --repo jmtmg/pli-app --env staging --json name --jq '.[].name'
gh variable list --repo jmtmg/pli-app --env staging --json name --jq '.[].name'
```

### Vérifier Fly secrets par noms uniquement

À exécuter seulement après création approuvée de l'app `pli-staging`, sans déploiement :

```bash
flyctl secrets list --app pli-staging
```

## Import officiel, à ne pas exécuter sans approbation

- Local : créer/remplir `.env.staging` depuis 1Password/Keychain ou secret manager approuvé, puis `chmod 600 .env.staging`. Ne jamais afficher le fichier.
- GitHub Actions : créer les `secrets` et `vars` dans l'environnement `staging` via l'UI GitHub ou `gh` en mode prompt/stdin ; ne pas passer de secret en argument shell.
- Fly runtime : importer uniquement les secrets runtime approuvés via Fly secrets. Si un fichier d'import est utilisé, il doit être secrets-only, privé, gitignoré, et détruit/rotaté selon la procédure opérateur ; ne pas importer aveuglément les variables frontend.
- Provider consoles : créer OAuth, DB, object storage, email et éventuellement Sentry/Stripe dans leurs consoles officielles ; reporter seulement les noms de clés et décisions dans les tickets/docs.

## Blockers humains restants

- Choisir providers staging : PostgreSQL, object storage, email transactionnel, hosting frontend.
- Confirmer ou ajuster le domaine `staging.pli.app` et la stratégie frontend/CORS.
- Créer/configurer les apps OAuth Gmail/Microsoft staging avec les redirects exacts ci-dessus.
- Autoriser explicitement toute création Fly/GitHub secrets/provider console/import secret.
- Définir backup/restore staging et propriétaire du test restore.
