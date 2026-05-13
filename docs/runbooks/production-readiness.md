# PLI — Runbook production readiness

Statut : préparation non destructive. Ce document ne contient aucun secret et ne déclenche aucun déploiement. Les recommandations cloud-staging (Fly/Scaleway/Brevo ou alternatives) ne valent pas validation utilisateur : aucune ressource/provider/DNS/OAuth n'est considéré provisionné tant qu'une confirmation explicite et un smoke réel ne l'ont pas prouvé.

## Objectif

Fournir un chemin clair pour décider si PLI peut passer de l’état **MVP local/démo vérifié** vers une cible exposée :

- `local-v1` : application locale/distribuable, SQLite canonique, stockage local, aucun provider réel requis par défaut.
- `cloud-v1` : API + frontend HTTPS, PostgreSQL, stockage objet, emails transactionnels, OAuth Gmail/Microsoft officiel, secrets protégés.

## Règles de sécurité

- Ne jamais commiter `.env`, `.env.local`, tokens, OAuth client secrets, clés Stripe, DB URLs avec mot de passe, clés S3, clés Fernet, DSN privés.
- Ne jamais imprimer un secret dans Telegram, logs de CI, tickets, notes ou sorties de script.
- Utiliser uniquement des gestionnaires de secrets officiels : 1Password, Keychain, secret manager cloud, variables CI protégées, OAuth/app-password officiels.
- Tout déploiement, migration DB, restart, changement DNS ou rotation de secret nécessite une confirmation explicite.

## Preflight secret-safe

Depuis la racine du repo :

```bash
cd /Users/jm/context-engine/projects/pli-app

# Cible locale/staging — accepte HTTP localhost mais bloque debug/demo/secret par défaut.
# Génère d'abord un .env.local privé et gitignoré si nécessaire.
make local-v1-env
make local-v1-preflight

# Équivalent explicite du preflight local-v1 :
cd backend && .venv/bin/python scripts/prod_readiness_check.py \
  --target local-v1 \
  --env staging \
  --dotenv ../.env.local \
  --show-env-keys

# Cible cloud staging — doit rester bloquée avec le template tant que les
# fournisseurs/secrets officiels ne sont pas renseignés.
cd backend && .venv/bin/python scripts/prod_readiness_check.py \
  --target cloud-v1 \
  --env staging \
  --dotenv ../.env.staging.example

# Cible cloud staging réelle — ne pas utiliser --show-env-keys ; aucune valeur
# de .env.staging ne doit être affichée.
make cloud-staging-preflight

# Cible cloud production — doit échouer tant que les vrais secrets/URLs/infra ne sont pas fournis.
cd backend && .venv/bin/python scripts/prod_readiness_check.py \
  --target cloud-v1 \
  --env production \
  --dotenv ../.env.production
```

Le script retourne :

- exit `0` : aucun blocker statique détecté ;
- exit `2` : production bloquée ; lire les actions, pas les secrets ;
- les valeurs sensibles sont affichées uniquement comme `[SET]` / `[EMPTY]`.

## Gates applicatifs obligatoires

Avant une release `local-v1` ou une release cloud :

```bash
cd /Users/jm/context-engine/projects/pli-app
make test
make lint
make typecheck
cd frontend && npm run build
cd ..
# Cloud uniquement : prouver la syntaxe Compose et le build Docker dès qu'un hôte Docker est disponible.
docker compose config --quiet
docker build -f backend/Dockerfile .
git diff --check
```

À ajouter au gate de release : un scan de diff secret-safe avec l’outil validé du moment, en excluant `frontend/dist` et `frontend/node_modules`. À défaut d’un scanner dédié dans le repo, faire une revue manuelle du diff et refuser toute inclusion de `.env`, token, OAuth secret, DB URL, clé S3, clé Stripe ou connection string.

## Cible `local-v1`

Pré-requis :

- `PLI_MODE=local`
- `PLI_SECRET_KEY` réel, long, stocké hors repo
- `PLI_DEBUG=false`
- `PLI_DEMO=false` sauf build explicitement démo
- `PLI_DB_PATH` dédié à la release locale (généré en chemin absolu sous `.pli-local-v1/db.sqlite` par `make local-v1-env`)
- `PLI_ATTACHMENTS_DIR` dédié aux pièces jointes locales (généré sous `.pli-local-v1/attachments`, gitignoré)
- `PLI_SQLCIPHER_KEY` recommandé si stockage de mails réels

Go/no-go local :

- OK si les gates MVP passent, le preflight `local-v1` n’a aucun blocker, et la documentation n’annonce pas Gmail/Microsoft/Stripe réel.
- NO-GO si debug/demo actif, secret de développement, chemins de stockage absents, ou si l’UX promet un envoi provider réel non branché.

Rollback local :

- conserver l’archive de build précédente ;
- sauvegarder DB SQLite + répertoire PJ avant migration ;
- pouvoir restaurer le couple DB/PJ ensemble ;
- ne jamais migrer la DB utilisateur sans backup vérifié.

## Cible `cloud-v1`

Pré-requis infra :

- API publique HTTPS (`PLI_BASE_URL`) sans localhost/IP privée/hostname interne/notation IPv4 abrégée ;
- frontend public HTTPS (`PLI_APP_URL`) sans localhost/IP privée/hostname interne/notation IPv4 abrégée ;
- PostgreSQL non-localhost (`PLI_DATABASE_URL`) ;
- stockage objet S3-compatible (`PLI_S3_ENDPOINT_URL`, bucket, access key, secret key) avec endpoint HTTPS public ;
- clé de chiffrement cloud (`PLI_CLOUD_CRYPTO_KEY`) : clé Fernet valide générée hors logs avec `cryptography.fernet.Fernet.generate_key()` ;
- CORS limité aux origines frontend exactes (`PLI_CORS_ORIGINS` au format JSON list, par ex. `'["https://app.example.com"]'`) ;
- provider email réel : SMTP, SendGrid ou Postmark ;
- apps OAuth officielles Gmail + Microsoft avec redirect URI HTTPS ;
- logs/metrics/alerting ;
- backup PostgreSQL + stockage objet ;
- procédure de restore testée.

Pré-requis fonctionnels cloud :

- `PLI_MODE=cloud` ;
- `PLI_DEBUG=false`, `PLI_DEMO=false` ;
- pas de `localhost`, wildcard CORS, MailHog/memory email, MinIO dev credentials, Stripe test en production ;
- migrations DB testées en staging ;
- vraie politique de rétention/export/suppression si données personnelles réelles.

Go/no-go cloud :

- GO uniquement si le preflight `cloud-v1 --env production` sort `ready`, les gates applicatifs passent, staging a été smoke-testé, et les secrets sont fournis via secret manager.
- NO-GO si OAuth officiel, email transactionnel, DB, S3, CORS ou crypto sont incomplets.
- M2/Stripe doit rester désactivé tant que billing/tenant/RGPD n’est pas validé comme gate cloud.

Rollback cloud :

1. Identifier la version déployée précédente : image/tag/commit + migrations associées.
2. Avant migration : snapshot PostgreSQL + backup stockage objet + sauvegarde config runtime secret-safe.
3. Déployer en staging puis prod avec healthcheck.
4. En cas d’échec post-déploiement : repointer l’ancienne image/tag, restaurer variables runtime précédentes, vérifier `/health` et parcours critique.
5. Si migration destructive : rollback uniquement via restore DB validé ; ne pas improviser de downgrade SQL manuel.

## Smoke minimal après déploiement

Backend :

- `GET /health` → `status=ok`, mode attendu, DB OK ;
- seed/demo uniquement hors prod réelle ;
- endpoints comptes/conversations/messages ne renvoient jamais tokens, refresh tokens, client secrets, BCC publique, headers provider bruts.

Frontend :

- build servi sur HTTPS ;
- app shell charge sans erreur console critique ;
- drawer comptes, recherche, conversation, composer local répondent ;
- copy produit ne promet pas Gmail/Microsoft/Stripe tant que désactivés.

## Décision actuelle

- PLI est vérifié comme **MVP local/démo**.
- `cloud-staging` dispose maintenant d'un template secret-safe (`.env.staging.example`), d'un runbook (`docs/runbooks/cloud-staging.md`) et d'une cible `make cloud-staging-preflight` qui n'imprime pas les valeurs, mais aucun provider recommandé n'est provisionné/validé et le staging réel reste bloqué.
- La production cloud reste bloquée tant que les secrets officiels, OAuth, email, DB/S3, backups/restore et gates cloud ne sont pas fournis et validés.
- Le prochain pas sûr est : garder `local-v1` comme cible livrable, choisir les fournisseurs staging, puis exécuter le preflight `cloud-staging` avec `.env.staging` privé avant tout déploiement.
