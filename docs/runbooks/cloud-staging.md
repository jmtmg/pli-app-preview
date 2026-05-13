# PLI — cloud-staging secret-safe

Statut : artefact de préparation uniquement. Ne pas déployer, ne pas créer de DNS/ressource cloud, ne pas installer `flyctl`, ne pas manipuler de secret réel sans confirmation explicite.

## Sources lues

- parent local-v1 : `reports/local-v1-readiness-2026-05-13.md`, statut `ready` local avec preflight OK et aucun secret imprimé ;
- runbook existant : `docs/runbooks/production-readiness.md` ;
- configs statiques : `fly.toml`, `docker-compose.yml`, `backend/Dockerfile`, `README.md`, `.env.example`, `.env.local.example`.

## Artefacts staging

- Template secret-safe : `.env.staging.example`.
- Fichier runtime attendu : `.env.staging` privé, gitignoré, chmod `600`, rempli depuis 1Password/Keychain/secret manager/provider consoles uniquement.
- Commande de preflight réelle : `make cloud-staging-preflight`.
- Commande de preflight avec placeholders sûrs :

```bash
cd /Users/jm/context-engine/projects/pli-app
cd backend && .venv/bin/python scripts/prod_readiness_check.py \
  --target cloud-v1 \
  --env staging \
  --dotenv ../.env.staging.example
```

Résultat attendu avec le template non rempli : exit `2`, statut `blocked`, uniquement des codes/actions ; aucune valeur de variable n'est imprimée. Ne pas ajouter `--show-env-keys` pour la commande staging opérationnelle.

## Procédure de préparation locale, sans secret imprimé

```bash
cd /Users/jm/context-engine/projects/pli-app
cp .env.staging.example .env.staging
chmod 600 .env.staging
# Renseigner .env.staging depuis le gestionnaire de secrets, pas depuis l'historique shell.
make cloud-staging-preflight
```

`make cloud-staging-preflight` appelle le check backend sans `--show-env-keys`, donc les valeurs ne sont pas affichées même si `.env.staging` contient des secrets.

## Ressources à provisionner avant GO staging

### 1. HTTPS API

- Cible actuelle : app Fly `pli-staging`, région `cdg`, backend FastAPI sur port interne `8000`.
- Domaine prévu dans `fly.toml` : `https://staging.pli.app`.
- Healthcheck attendu : `GET /health`.
- À faire après approbation humaine : créer/valider app Fly, cert TLS, hostname, secrets runtime et rollback image/tag.

### 2. HTTPS frontend

- Le `backend/Dockerfile` et `fly.toml` actuels ne buildent que le backend ; aucun hosting frontend staging n'est encore défini dans le repo.
- Décision requise : même origine derrière reverse proxy ou hosting statique séparé (Cloudflare Pages/Vercel/Fly static/autre).
- Variables à maintenir cohérentes : `VITE_API_URL`, `VITE_PLI_MODE`, `PLI_APP_URL`, `PLI_CORS_ORIGINS`.

### 3. PostgreSQL staging

- Fournisseur à choisir : Fly Postgres, Neon, Supabase, Scaleway ou autre PostgreSQL managé.
- Secret attendu : `PLI_DATABASE_URL` réel, hors logs.
- Gates : migrations Alembic sur staging, backup avant migration, restore testé.

### 4. Stockage objet S3-compatible

- Fournisseur à choisir : Cloudflare R2, Scaleway Object Storage, AWS S3 ou équivalent.
- Bucket proposé : `pli-staging-attachments`, à créer/provisionner explicitement ; le template seul ne prouve pas son existence.
- Secrets attendus : `PLI_S3_ENDPOINT_URL`, `PLI_S3_ACCESS_KEY`, `PLI_S3_SECRET_KEY`, `PLI_S3_BUCKET`, `PLI_S3_REGION`.
- Gates : policy least-privilege, lifecycle/rétention, test upload/download/delete, backup ou réplication si requis.

### 5. Email transactionnel

- Fournisseur à choisir : SMTP réel, SendGrid ou Postmark.
- Secrets attendus selon provider : `PLI_EMAIL_API_KEY` ou `PLI_EMAIL_SMTP_*`, plus `PLI_EMAIL_FROM` validé.
- Gate : domaine sender validé SPF/DKIM/DMARC, email de vérification staging reçu, pas de MailHog/memory en staging exposé.

### 6. OAuth Gmail/Microsoft staging

- Gmail : app OAuth officielle staging avec redirect exact `https://staging.pli.app/auth/gmail/callback`.
- Microsoft : App Registration staging avec redirect exact `https://staging.pli.app/auth/microsoft/callback`.
- Secrets attendus : `PLI_GMAIL_CLIENT_ID`, `PLI_GMAIL_CLIENT_SECRET`, `PLI_MS_CLIENT_ID`, `PLI_MS_CLIENT_SECRET`, `PLI_MS_TENANT_ID`.
- Contrainte : ne pas modifier les apps OAuth réelles/prod ; créer ou configurer uniquement la cible staging approuvée.

### 7. CORS exact

- Valeur actuelle template : `PLI_CORS_ORIGINS='["https://staging.pli.app"]'`.
- Si frontend séparé : remplacer par l'origine frontend HTTPS exacte, sans wildcard, sans localhost.
- Smoke attendu : navigateur sans erreur CORS sur login, refresh, conversations, search, send.

### 8. Backups/restore

- PostgreSQL : snapshot avant migration, politique rétention staging, procédure restore documentée et testée.
- Objet : export/réplication/lifecycle cohérent avec données de staging.
- Config : sauvegarder la liste des noms de variables et versions déployées, jamais les valeurs.

### 9. Observabilité minimale

- Logs applicatifs consultables sans secret.
- Uptime check public `/health`.
- Alerting basique pour 5xx, DB unavailable, storage unavailable, email provider failure.
- `PLI_SENTRY_DSN` optionnel et traité comme secret/handle.

## Checks statiques à exécuter avant demande de création cloud

```bash
cd /Users/jm/context-engine/projects/pli-app
python3 - <<'PY'
import tomllib
for path in ("fly.toml",):
    with open(path, "rb") as f:
        tomllib.load(f)
print("fly.toml parse: ok")
PY

docker compose config --quiet
# Si Docker CLI/daemon est absent, ce check est reporté au premier hôte Docker disponible.
# Faire au minimum une validation YAML statique pour la préparation repo :
# python3 -c 'import yaml; yaml.safe_load(open("docker-compose.yml")); print("docker-compose.yml parse: ok")'
cd backend && .venv/bin/python scripts/prod_readiness_check.py --target cloud-v1 --env staging --dotenv ../.env.staging.example
make -n cloud-staging-preflight
git diff --check
```

Notes : `docker compose config --quiet` est une validation syntaxique sans daemon ; ne pas prétendre qu'un build Docker est prouvé tant que le daemon est indisponible. Le preflight template doit rester bloqué tant que les secrets/fournisseurs ne sont pas renseignés.

## Blockers humains restants

P0 — Choisir les fournisseurs staging : PostgreSQL, S3/object storage, email transactionnel, hosting frontend.

P0 — Autoriser ou non l'usage Fly pour `pli-staging`, création app/cert/secrets et domaine `staging.pli.app`.

P0 — Créer les apps OAuth Gmail/Microsoft staging et confirmer les redirects exacts.

P1 — Valider la stratégie frontend : même domaine que l'API ou domaine séparé ; mettre à jour `PLI_APP_URL`, `VITE_API_URL` et `PLI_CORS_ORIGINS` en conséquence.

P1 — Définir backup/restore staging et propriétaire de test restore.

P2 — Choisir observabilité/alerting minimal.
