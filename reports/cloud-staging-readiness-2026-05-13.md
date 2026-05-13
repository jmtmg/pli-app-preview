# PLI cloud-staging readiness — 2026-05-13

Statut : prepared / blocked-on-human-providers. Aucun déploiement cloud, DNS, restart distant, install `flyctl`, création cloud ou manipulation de secret réel n'a été effectué. Mise à jour locale : Docker/Compose/Buildx/Colima ont été installés sur le Mac mini pour prouver les gates Docker en environnement local isolé ; la stack compose cloud locale a été arrêtée après smoke.

## Artefacts ajoutés ou modifiés

- `.env.staging.example` : template cloud-staging secret-safe, volontairement incomplet pour rester bloqué tant que les secrets/fournisseurs officiels ne sont pas fournis.
- `docs/runbooks/cloud-staging.md` : checklist exécutable ressources staging, procédure preflight, décisions humaines restantes.
- `Makefile` : cible `cloud-staging-preflight` qui lit `.env.staging` et appelle le readiness check sans `--show-env-keys`.
- `README.md` : section cloud-staging et commande exacte.
- `docs/runbooks/production-readiness.md` : ajout du flux cloud-staging et suppression de `--show-env-keys` pour les commandes cloud.
- `fly.toml` : `PLI_ENABLE_M2=false` explicite et commentaires secrets durcis vers secret manager / import approuvé.
- `.gitignore` : autorise `.env.staging.example`, continue d'ignorer `.env.staging` via `.env.*`.
- `backend/Dockerfile` : installation des dépendances cloud `m2` dans l'image runtime pour que le driver PostgreSQL/Alembic soit présent.
- `docker-compose.yml` : montage README requis par `backend/pyproject.toml`, cloud-app installée en `.[m2,dev]`, URL Postgres locale overrideable par variable d'environnement.
- `backend/pli/main.py` : le lifespan cloud initialise et ferme explicitement le pool asyncpg.

## Commande preflight staging

Commande réelle, après copie/remplissage secret manager :

```bash
cd /Users/jm/context-engine/projects/pli-app
make cloud-staging-preflight
```

Commande vérifiée avec placeholders sûrs :

```bash
cd /Users/jm/context-engine/projects/pli-app/backend
.venv/bin/python scripts/prod_readiness_check.py --target cloud-v1 --env staging --dotenv ../.env.staging.example
```

Résultat : `status=blocked`, `preflight exit=2`, sans valeurs imprimées. Blockers détectés avec le template : secret applicatif, PostgreSQL, clé crypto cloud, S3 endpoint/access/secret, email provider, OAuth Gmail, OAuth Microsoft. Info : `m2-disabled` attendu.

## Checks statiques et smoke local exécutés

- `tomllib.load(open('fly.toml','rb'))` : OK.
- Parse YAML `docker-compose.yml` via PyYAML : OK ; services détectés `backend, cloud-app, frontend, mailhog, minio, minio-init, postgres, stripe-cli`.
- `fly.toml` → `build.dockerfile=backend/Dockerfile` existe : OK.
- `fly.toml` env statique : `PLI_MODE=cloud`, `PLI_ENABLE_M2=false` : OK.
- `backend/Dockerfile` marqueurs statiques : `USER pli`, `HEALTHCHECK`, `alembic -c alembic.ini upgrade head`, `uvicorn pli.main:app` présents.
- `docker compose -f docker-compose.yml config` : OK après installation locale Docker/Compose.
- `docker build -f backend/Dockerfile -t pli-backend:local-readiness .` : OK avec dépendances `m2`.
- Smoke compose cloud local avec Postgres + MinIO + MailHog + clé Fernet éphémère : `/health` retourne `status=ok`, `mode=cloud`, `db.ok=true`, `users=0`.
- Smoke image `pli-backend:local-readiness` sur réseau compose local : `/health` retourne `status=ok`, `mode=cloud`, `db.ok=true`, `users=0`.
- `make -n cloud-staging-preflight` : OK, cible résolue et n'utilise pas `--show-env-keys`.
- `git check-ignore -v .env.staging` : ignoré par `.gitignore:83:.env.*`.
- `git check-ignore -v .env.staging.example` : autorisé par `.gitignore:86:!.env.staging.example`.
- `git diff --check` : OK.
- Scan high-confidence des fichiers touchés, sans afficher de lignes : `0 findings`.

## Ressources staging à provisionner

- HTTPS API : app Fly `pli-staging`, région `cdg`, domaine/cert `https://staging.pli.app`, `/health`.
- HTTPS frontend : non défini par le `fly.toml` backend actuel ; choisir même origine/reverse proxy ou hosting statique séparé.
- PostgreSQL staging managé : fournisseur à choisir, `PLI_DATABASE_URL` via secret manager, migrations/backup/restore.
- S3/object storage : fournisseur à choisir, bucket proposé `pli-staging-attachments`, credentials least-privilege.
- Email transactionnel : SMTP réel, SendGrid ou Postmark à choisir, sender SPF/DKIM/DMARC.
- OAuth Gmail/Microsoft staging : apps officielles staging, redirects exacts `https://staging.pli.app/auth/gmail/callback` et `https://staging.pli.app/auth/microsoft/callback`.
- CORS : origine frontend HTTPS exacte, au format JSON list string, sans wildcard/localhost.
- Backups/restore : PostgreSQL + objet, restore testé.
- Observabilité : uptime `/health`, logs, alerting 5xx/DB/storage/email.

## Blockers humains restants

P0 : choisir fournisseurs staging PostgreSQL, S3/object storage, email transactionnel et hosting frontend.

P0 : confirmer l'usage Fly pour `pli-staging`, le domaine `staging.pli.app`, les certificats et l'import de secrets.

P0 : créer/configurer les apps OAuth Gmail/Microsoft staging avec redirects exacts.

P1 : décider frontend même domaine vs domaine séparé ; ajuster `PLI_APP_URL`, `VITE_API_URL`, `PLI_CORS_ORIGINS`.

P1 : valider backup/restore staging et propriétaire du test restore.
