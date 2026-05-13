# PLI cloud-staging readiness — 2026-05-13

Statut : prepared / blocked-on-human-providers. Aucun déploiement, DNS, restart, install `flyctl`, création cloud ou manipulation de secret réel n'a été effectué.

## Artefacts ajoutés ou modifiés

- `.env.staging.example` : template cloud-staging secret-safe, volontairement incomplet pour rester bloqué tant que les secrets/fournisseurs officiels ne sont pas fournis.
- `docs/runbooks/cloud-staging.md` : checklist exécutable ressources staging, procédure preflight, décisions humaines restantes.
- `Makefile` : cible `cloud-staging-preflight` qui lit `.env.staging` et appelle le readiness check sans `--show-env-keys`.
- `README.md` : section cloud-staging et commande exacte.
- `docs/runbooks/production-readiness.md` : ajout du flux cloud-staging et suppression de `--show-env-keys` pour les commandes cloud.
- `fly.toml` : `PLI_ENABLE_M2=false` explicite et commentaires secrets durcis vers secret manager / import approuvé.
- `.gitignore` : autorise `.env.staging.example`, continue d'ignorer `.env.staging` via `.env.*`.

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

## Checks statiques exécutés

- `tomllib.load(open('fly.toml','rb'))` : OK.
- Parse YAML `docker-compose.yml` via PyYAML : OK ; services détectés `backend, cloud-app, frontend, mailhog, minio, minio-init, postgres, stripe-cli`.
- `fly.toml` → `build.dockerfile=backend/Dockerfile` existe : OK.
- `fly.toml` env statique : `PLI_MODE=cloud`, `PLI_ENABLE_M2=false` : OK.
- `backend/Dockerfile` marqueurs statiques : `USER pli`, `HEALTHCHECK`, `alembic -c alembic.ini upgrade head`, `uvicorn pli.main:app` présents.
- `docker compose config --quiet` : non exécuté, Docker CLI absent dans cette session (`docker: command not found`) ; aucun build Docker prouvé.
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
