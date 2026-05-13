# PLI cloud-production GO/NO-GO — 2026-05-13

Statut : NO-GO / blocked pour cloud-production.

Cette décision est non destructive côté cloud : aucun déploiement, DNS, migration DB distante, restart distant, installation cloud, lecture ou impression de secret réel n'a été effectué. Une installation locale Docker/Compose/Buildx/Colima a été faite sur le Mac mini pour prouver build + smoke en environnement local isolé.

## Verdict production

Verdict : `blocked`.

La production cloud ne doit pas être déclarée ready aujourd'hui. Les artefacts repo débloquent une préparation contrôlée `local-v1` puis `cloud-staging`, mais il manque encore les preuves obligatoires pour un GO production : preflight `cloud-v1 --env production` ready avec secrets via gestionnaire, gates applicatifs à jour, staging réel smoke-testé, backup/restore validés et confirmations humaines sur fournisseurs/domaines/OAuth/hosting.

## Preuves utilisées

### Parents Kanban

- `t_070b1811` local-v1 : `ready`; preflight local-v1 OK ; `.env.local` et `.pli-local-v1/` générés hors commit et gitignorés ; tests/lint/typecheck/build verts ; rapport `reports/local-v1-readiness-2026-05-13.md` ; blocker local restant : aucun ; warning : `PLI_SQLCIPHER_KEY` seulement si stockage de mails réels.
- `t_5448ca11` cloud-staging : artefacts secret-safe prêts ; `.env.staging.example`, `docs/runbooks/cloud-staging.md`, `reports/cloud-staging-readiness-2026-05-13.md`, cible `make cloud-staging-preflight` ; placeholder preflight volontairement `blocked`; aucun secret/cloud/deploy effectué.

### Vérifications relancées pendant cette synthèse

- `git status --short --branch` : branche `chore/pli-local-cloud-readiness`, changements de smoke Docker prêts à commit.
- `git diff --check` : OK.
- `make local-v1-preflight` : `status=ready`, warning non bloquant `sqlcipher-key-missing`.
- `make cloud-staging-preflight` : bloqué volontairement tant que `.env.staging` privé n'existe pas et que les providers/secrets ne sont pas renseignés.
- `make test-be` : `123 passed, 3 skipped`.
- `make lint-be` : ruff OK.
- `make typecheck` : backend mypy MVP OK + frontend `tsc --noEmit` OK.
- `make test-fe` : `44 passed`.
- `make lint-fe` : ESLint + `tsc --noEmit` OK.
- `cd frontend && npm run build` : build Vite/PWA OK.
- `docker-compose.yml` : YAML parse OK ; `fly.toml` : TOML parse OK.
- `docker compose -f docker-compose.yml config` : OK.
- `docker build -f backend/Dockerfile -t pli-backend:local-readiness .` : OK.
- Smoke compose cloud local : `/health` `status=ok`, `mode=cloud`, `db.ok=true`, stack arrêtée ensuite.
- Smoke image Docker `pli-backend:local-readiness` : `/health` `status=ok`, `mode=cloud`, `db.ok=true`.

## Ce qui est débloqué par le repo

- `local-v1` est livrable comme cible locale reproductible, sans comptes externes réels par défaut.
- Le repo contient un preflight secret-safe pour `local-v1` et `cloud-v1`.
- Le chemin `cloud-staging` est documenté et actionnable : template `.env.staging.example`, runbook, checklist ressources, commande `make cloud-staging-preflight` qui n'affiche pas les valeurs.
- `fly.toml` décrit une cible backend staging Fly `pli-staging` avec `PLI_MODE=cloud`, `PLI_ENABLE_M2=false`, healthcheck `/health` et secrets listés uniquement par noms.
- Le runbook `docs/runbooks/production-readiness.md` fixe déjà les gates : tests, lint, typecheck, build frontend, preflight, smoke, rollback.

## Ce qui bloque encore cloud-production

### P0 — bloquants absolus avant tout GO production

1. Pas de preuve de preflight production ready : la commande production reste `blocked` tant que `.env.production`/secret manager ne fournit pas les valeurs officielles.
2. Fournisseurs/ressources production non confirmés : PostgreSQL managé, S3/object storage, email transactionnel, domaine/cert HTTPS API, domaine/hosting frontend.
3. OAuth officiel non prouvé : apps Gmail et Microsoft production, client IDs/secrets stockés via secret manager, redirects HTTPS exacts.
4. Staging réel non smoke-testé : les artefacts staging existent, mais aucun déploiement staging avec vrais providers n'a été autorisé ni vérifié.
5. Backup/restore non validé : snapshot PostgreSQL, backup objet, restore testé et responsable d'exécution restent à confirmer.
6. Secret import non réalisé : aucune preuve d'import via Fly secrets / secret manager cloud / 1Password/Keychain, et aucune valeur ne doit transiter par shell history ou logs.

### P1 — risques à lever avant release candidate production

- Frontend cloud non tranché : même origine derrière reverse proxy vs hosting statique séparé ; impact direct sur `PLI_APP_URL`, `VITE_API_URL`, `PLI_CORS_ORIGINS`.
- Runtime Docker local maintenant prouvé ; il reste à prouver le build/déploiement dans la plateforme staging retenue avec secrets manager officiel.
- DNS/certificats production non vérifiés publiquement.
- Observabilité minimale à brancher : uptime `/health`, alertes 5xx, DB/storage/email, logs sans secrets.
- Politique CORS production à verrouiller sur origines HTTPS exactes, sans wildcard ni localhost.
- `PLI_ENABLE_M2=false` doit rester explicitement assumé pour la première prod cloud MVP ; billing/auth cloud avancés ne doivent pas être exposés tant que M2-M4 ne sont pas validés.

### P2 — durcissement recommandé après premier staging vert

- Automatiser le gate secret-scan dédié sur diff/release.
- Tagger image/commit/artefacts de release et conserver une matrice de versions déployées.
- Ajouter un rapport smoke staging/prod horodaté après chaque déploiement.
- Formaliser un runbook incident court : rollback image, restore DB/objet, désactivation OAuth/email, communication utilisateur.

## Séquence GO si l'utilisateur fournit/autorise les éléments manquants

### Phase 0 — décisions humaines préalables

L'utilisateur doit confirmer :

- fournisseur PostgreSQL production et staging ;
- fournisseur S3/object storage et noms de buckets ;
- fournisseur email transactionnel et domaine sender ;
- Fly ou autre plateforme pour API production ;
- stratégie frontend : même domaine/API ou hosting séparé ;
- domaines finaux staging/prod et propriétaire DNS/certificats ;
- apps OAuth Gmail/Microsoft staging puis production ;
- propriétaire backup/restore et fenêtre de maintenance.

### Phase 1 — staging secret-safe

1. Créer les ressources staging approuvées : DB, bucket, email, OAuth apps, domaine/cert, frontend.
2. Importer les secrets staging via gestionnaire officiel uniquement.
3. Préparer `.env.staging` local privé si nécessaire (`chmod 600`, gitignoré), sans afficher de valeurs.
4. Exécuter :

```bash
cd /Users/jm/context-engine/projects/pli-app
make cloud-staging-preflight
make test
make lint
make typecheck
cd frontend && npm run build
cd ..
git diff --check
```

Gate attendu : `make cloud-staging-preflight` doit sortir `ready`. Si `blocked`, ne pas déployer.

### Phase 2 — déploiement staging et smoke

1. Construire et déployer staging uniquement après preflight ready.
2. Appliquer migrations staging avec snapshot préalable.
3. Vérifier `/health` public : status OK, mode cloud, DB OK.
4. Smoke navigateur : app shell HTTPS, pas d'erreur console critique, pas d'erreur CORS.
5. Smoke API contrôlé : comptes/conversations/messages/search sans fuite de tokens/secrets.
6. Smoke storage : upload/download/delete d'un objet de test.
7. Smoke email : email transactionnel de test reçu sur adresse contrôlée.
8. Smoke OAuth : parcours Gmail/Microsoft staging avec comptes de test et redirects exacts.
9. Documenter résultats dans un rapport staging horodaté.

### Phase 3 — pré-prod production

1. Geler commit/image/tag release candidate.
2. Créer ressources production approuvées.
3. Importer secrets production via secret manager uniquement.
4. Exécuter le preflight production, sans `--show-env-keys` :

```bash
cd /Users/jm/context-engine/projects/pli-app/backend
.venv/bin/python scripts/prod_readiness_check.py \
  --target cloud-v1 \
  --env production \
  --dotenv ../.env.production
```

Gate attendu : `status=ready`. Sans ce résultat, verdict production reste NO-GO.

### Phase 4 — backup, déploiement prod, smoke

1. Snapshot PostgreSQL production avant migration.
2. Backup/export stockage objet ou vérification de réplication/lifecycle.
3. Sauvegarde secret-safe de la configuration : noms de variables, versions, checksums publics, jamais les valeurs.
4. Déploiement prod avec image/tag gelé.
5. Healthcheck `/health` puis smoke minimal : frontend HTTPS, CORS, auth OAuth, parcours message local/cloud attendu, email transactionnel, storage, logs sans secret.
6. Monitoring renforcé au minimum 30–60 minutes après ouverture.

## Rollback / restore

Rollback applicatif :

- conserver l'image/tag/commit précédent ;
- si smoke post-déploiement échoue avant migration destructive, repointer l'ancienne image/tag et restaurer variables runtime précédentes via secret manager ;
- vérifier `/health`, frontend et parcours critique après rollback.

Rollback données :

- snapshot PostgreSQL avant toute migration ;
- backup objet cohérent avec la DB ;
- si migration destructive ou incohérence DB/objet, rollback uniquement via restore testé, pas par downgrade SQL improvisé ;
- valider la paire DB + objets restaurée sur environnement isolé avant réouverture.

## Décision finale

- GO `local-v1` : oui, selon les preuves parentales et le preflight relancé.
- GO `cloud-staging` : pas encore pour déploiement réel ; préparation repo OK, exécution bloquée par décisions/secrets/providers.
- GO `cloud-production` : non. Production reste bloquée jusqu'à preuves cumulées : staging réel vert, preflight production `ready`, secrets via manager, backups/restore testés, gates applicatifs verts et confirmations utilisateur.
