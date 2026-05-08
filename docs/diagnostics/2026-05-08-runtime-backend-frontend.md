# Diagnostic runtime backend/frontend PLI — 2026-05-08 17:52 CEST

Workspace : `/Users/jm/context-engine/projects/pli-app`

## Résumé

Le diagnostic initial a été transformé en tranche MVP locale fonctionnelle. Les causes racines historiques sont conservées ci-dessous, mais l’état courant est :

- backend local/démo : OK ;
- frontend MVP : OK ;
- `make test` : OK ;
- `make lint` : OK sur périmètre MVP ;
- `make typecheck` : OK sur périmètre MVP ;
- `npm run build` : OK ;
- smoke HTTP backend + frontend preview : OK ;
- suite backend complète M2/M3/M4 : encore non verte.

Aucun secret réel n’a été utilisé. Les données seedées sont fictives.

## Commandes vérifiées OK

```bash
cd /Users/jm/context-engine/projects/pli-app
make test
make lint
make typecheck
cd frontend && npm run build
```

Résultats observés :

- backend MVP : `98 passed, 3 skipped` ;
- frontend Vitest : `1 passed`, `6 tests passed` ;
- ruff MVP : `All checks passed` ;
- mypy MVP : `Success: no issues found in 9 source files` ;
- TypeScript MVP : `tsc --noEmit` OK ;
- Vite build : `93 modules transformed`, PWA générée.

## Smoke backend

Serveur lancé temporairement sur `127.0.0.1:18080` avec :

```bash
PLI_DEMO=true
PLI_DB_PATH=/Users/jm/context-engine/projects/pli-app/.pli-dev/smoke.sqlite
PLI_ATTACHMENTS_DIR=/Users/jm/context-engine/projects/pli-app/.pli-dev/smoke-att
```

Endpoints testés :

- `GET /health` : OK, mode `local`, 1 compte.
- `POST /demo/seed?reset=true` : OK, 1 compte, 3 contacts, 4 messages, 1 pièce jointe.
- `GET /accounts` : OK, compte fictif `demo@pli-app.fr`.
- `GET /conversations?filter=all` : OK, 3 conversations.
- `GET /messages/by-contact/demo-contact-alice` : OK, 2 messages.
- `POST /messages/send` : OK, création d’un message local sortant.

## Smoke frontend

Preview Vite lancé temporairement sur `127.0.0.1:18081` après build.

- `GET /` : HTTP `200 OK`.
- HTML servi : application `PLI`, assets Vite/PWA présents.

## Causes racines isolées pour le non-MVP

### Backend full suite

`make test-be-all` échoue encore en collection sur :

- `tests/test_beta_activation.py`
- `tests/test_beta_batches.py`
- `tests/test_beta_nps.py`
- `tests/test_gdpr.py`
- `tests/unit/ocr/test_worker.py`

Causes :

- `pli.db` est actuellement un fichier module (`backend/pli/db.py`), alors que les couches futures importent `pli.db.models` et `pli.db.session` ;
- `get_session` / `SessionDep` absents ;
- couches beta, GDPR, OCR et SQLAlchemy non intégrées au runtime local MVP.

### Backend typecheck complet

`make typecheck-all` reste non vert : les erreurs mypy concernent surtout les strates hors MVP : GDPR, tenancy, billing, OCR, providers, auth cloud, modèles attendus mais absents.

### Frontend legacy hors MVP

Le corpus récupéré contient des routes/pages auth/billing/onboarding/feedback non câblées avec dépendances et modules manquants. Le shell MVP limite donc explicitement le build à la surface conversationnelle locale.

### ESLint

Le repo récupéré installait ESLint 9 sans `eslint.config.js`. Pour ne pas bloquer la tranche MVP, `npm run lint` exécute temporairement `tsc --noEmit`. Une vraie flat config ESLint 9 reste à ajouter.

## Voir aussi

Rapport utilisateur complet : `/Users/jm/context-engine/projects/pli-app/PLI_FUNCTIONAL_MVP_STATUS.md`
