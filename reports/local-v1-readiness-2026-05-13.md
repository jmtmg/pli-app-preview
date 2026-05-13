# PLI local-v1 readiness — 2026-05-13

Statut : ready pour local-v1 local, sans déploiement, sans restart, sans secret imprimé.

## Changements local-v1 ajoutés

- `.env.example` et `.env.local.example` : exemples secret-safe pour cible locale, avec `PLI_CORS_ORIGINS` au format JSON list et sans credentials réels.
- `scripts/generate_local_v1_env.py` : génère `.env.local` privé, chmod 600, avec chemins absolus sous `.pli-local-v1/` et résumé redacted.
- `Makefile` : cibles `local-v1-env`, `local-v1-preflight`, `dev-local-v1`; le test du générateur est inclus dans `make test-be`, le script dans `make lint-be`.
- `.gitignore` : ignore `.pli-local-v1/`, conserve `.env.local` ignoré, autorise `.env.local.example`.
- `README.md` et `docs/runbooks/production-readiness.md` : quickstart local-v1 et preflight reproductibles ; `PLI_CORS_ORIGINS` documenté au format JSON list compatible `pydantic-settings`.
- `backend/tests/test_local_v1_env_generator.py` : garde-fous sur chemins locaux, debug/demo désactivés, permissions du `.env.local` généré.

## Runtime local préparé hors commit

- `.env.local` généré localement et ignoré par Git.
- Permissions vérifiées : `.env.local` en `600`, `.pli-local-v1/` et `.pli-local-v1/attachments` en `700`.
- Chemins runtime générés sous `.pli-local-v1/` : DB SQLite et pièces jointes restent hors commit.
- Aucune valeur secrète réelle n’est documentée ni imprimée ; les sorties de preflight affichent seulement la présence/absence redacted.

## Commandes exécutées

- `backend/.venv/bin/python -m pytest -q --no-cov tests/test_local_v1_env_generator.py` avant script : échec attendu RED, générateur absent.
- `backend/.venv/bin/python -m pytest -q --no-cov tests/test_local_v1_env_generator.py` après script : `2 passed`.
- `make local-v1-env` : `.env.local` créé, chemins runtime préparés, secrets redacted.
- `make local-v1-preflight` : `status=ready`, warning non bloquant `sqlcipher-key-missing`.
- Smoke import `pli.config` avec `.env.local` sourcé : échec initial sur format CORS string, corrigé en JSON list, puis `local-v1 settings smoke: ok`.
- `make test` : backend `122 passed, 3 skipped`; frontend `44 passed`.
- `make lint` : backend ruff OK ; frontend ESLint + tsc OK.
- `make typecheck` : backend mypy MVP OK ; frontend `tsc --noEmit` OK.
- `cd frontend && npm run build` : build Vite/PWA OK.
- `git diff --check` : OK.
- Scan high-confidence des fichiers modifiés/non suivis : `0` finding secret.

## Verdict

`local-v1` est ready pour exécution locale reproductible.

Blocker restant : aucun pour local-v1.

Warning restant : `PLI_SQLCIPHER_KEY` absent ; acceptable pour smoke local sans mails réels, à fournir via secret local/gestionnaire de secrets avant stockage d’emails réels chiffrés.

Hors périmètre maintenu : `cloud-v1` reste bloqué tant que les secrets/infra/OAuth/email/DB/S3/backups officiels ne sont pas fournis et validés.
