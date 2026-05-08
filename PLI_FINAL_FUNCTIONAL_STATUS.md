# PLI — statut final fonctionnel local

Date : 2026-05-08 18:22 CEST
Workspace : `/Users/jm/context-engine/projects/pli-app`
Archive source préservée : `/Users/jm/context-engine/recovered/pli-cowork-complete-2026-05-08/source-surface/PLI-Archive-Complete/`
Base de départ : `3051bef feat: add local functional MVP slice`
Commit de cette tranche : `HEAD` (`chore: finalize PLI local functional status`; hash exact vérifié avec `git rev-parse --short HEAD` après commit)

## Verdict

PLI est fonctionnel en **MVP local/démo**, sans utiliser de secrets ni de comptes externes réels.

Ce qui est terminé et vérifié :

- backend FastAPI local/démo démarre ;
- seed démo déterministe OK ;
- comptes, conversations, messages, recherche/contact/attachments de démo OK ;
- adresse de test locale créée et seedée : `test.pli@demo-pli.com` ;
- composer local `POST /messages/send` OK ;
- frontend React/Vite MVP buildable et servable ;
- tests/lint/typecheck MVP verts ;
- ESLint 9 flat config restauré (le lint frontend n’est plus seulement `tsc --noEmit`) ;
- `npm audit fix` non forcé appliqué : vulnérabilités high supprimées ;
- strates backend futures M2-M4 isolées par commandes explicites (`test-be-future`, `typecheck-future`) et documentées.

Ce qui n’est **pas** terminé : `make test-be-all`, `make typecheck-all`, OAuth réel Gmail/Microsoft, Stripe/billing réel, RGPD/OCR/beta complets. Ces éléments sont bloqués par une décision d’architecture DB/session et/ou par des flows officiels/secrets à fournir. Je ne les déclare donc pas « finis ».

## Commandes vérifiées OK

Toutes les commandes ci-dessous ont été relancées après les modifications finales.

```bash
cd /Users/jm/context-engine/projects/pli-app
make test
make lint
make typecheck
cd frontend && npm run build
```

Résultats :

- `make test` :
  - backend MVP : `98 passed, 3 skipped in 0.65s` ;
  - frontend Vitest : `1 passed`, `6 tests passed`.
- `make lint` :
  - backend ruff : `All checks passed!` ;
  - frontend : `eslint . && tsc --noEmit` OK, sans warning final.
- `make typecheck` :
  - backend mypy MVP : `Success: no issues found in 9 source files` ;
  - frontend TypeScript : `tsc --noEmit` OK.
- `cd frontend && npm run build` :
  - `vite v5.4.21` ;
  - `93 modules transformed` ;
  - PWA générée (`dist/sw.js`, `dist/workbox-9c191d2f.js`).

## Smoke local vérifié

### Backend

Serveur temporaire lancé sur `127.0.0.1:18080` avec :

```bash
PLI_DEMO=true
PLI_DB_PATH=/Users/jm/context-engine/projects/pli-app/.diagnostics/backend/smoke-final.sqlite
PLI_ATTACHMENTS_DIR=/Users/jm/context-engine/projects/pli-app/.diagnostics/backend/smoke-final-att
backend/.venv/bin/python -m uvicorn pli.main:app --host 127.0.0.1 --port 18080
```

Endpoints validés :

- `GET /health` → HTTP 200, `status: ok`, `mode: local`, `accounts: 1` ;
- `POST /demo/seed?reset=true` → HTTP 200, `accounts: 1`, `contacts: 4`, `messages: 5`, `attachments: 1` ;
- `GET /accounts` → HTTP 200, 1 compte `demo-account-gmail` ;
- `GET /conversations?filter=all` → HTTP 200, 4 conversations, dont `test.pli@demo-pli.com` ;
- `GET /messages/by-contact/demo-contact-alice` → HTTP 200, 2 messages seedés ;
- `POST /messages/send` → HTTP 200, message sortant local `local-out-*` créé.

### Frontend

Preview temporaire lancé sur `127.0.0.1:18081` après build :

- `GET /` → HTTP 200 ;
- HTML contient `PLI` et les assets Vite (`/assets/...`).

Les serveurs temporaires ont été stoppés. Les ports `18080` et `18081` ne sont plus en écoute.

## Qualité frontend / audit npm

Actions :

- ajout `frontend/eslint.config.js` en flat config ESLint 9 ;
- ajout dev deps `typescript-eslint` et `globals` ;
- `frontend/package.json` : `lint` vaut maintenant `eslint . && tsc --noEmit` ;
- suppression des warnings ESLint trouvés dans le corpus frontend récupéré ;
- `npm audit fix` non forcé appliqué.

État audit :

```bash
cd frontend && npm audit --audit-level=moderate
```

Résultat final : `6 moderate severity vulnerabilities` restantes, toutes liées à `vite <=6.4.1` / `esbuild <=0.24.2` via Vite/Vitest/vite-plugin-pwa. La correction proposée par npm exige `npm audit fix --force` vers `vite@8.0.11`, changement majeur. Je ne l’ai pas forcée pour éviter une migration destructive non validée du toolchain Vite/PWA ; build, tests, lint et typecheck restent verts.

## Strates backend futures isolées

Commandes ajoutées :

```bash
make test-be-future
make typecheck-future
```

Elles isolent les suites récupérées non-MVP : auth, tenancy, feedback, Stripe/billing, beta, GDPR, OCR. Elles restent rouges par conception tant que la strate M2-M4 n’est pas réintégrée proprement.

État historique complet :

```bash
make test-be-all      # KO: 5 erreurs de collection initiales
make typecheck-all    # KO: 144 erreurs mypy dans 37 fichiers
```

Causes racines :

- `backend/pli/db.py` est un module SQLite local MVP ; les strates futures importent `pli.db.models` et `pli.db.session` comme si `pli.db` était un package SQLAlchemy ;
- `get_session`, `SessionDep`, `get_db`, `Session` absents ;
- modèles attendus absents ou incompatibles : `User`, `AuditLog`, `ExportJob`, `RefreshToken`, `ActivationEvent`, `Invitation`, `WaitlistEntry`, `FeedbackSubmission`, `AttachmentText`, etc. ;
- fixtures pytest futures absentes : `db_session`, `user_factory`, `waitlist_factory`, `feedback_factory`, `make_attachment`, `auth_headers`, `mail_outbox`, `verified_user`, `storage_mock`, `freezer`, etc. ;
- tables SQLite MVP absentes pour auth/billing/RGPD/OCR : `users`, refresh tokens/sessions, feedback, exports, `attachment_text` ;
- des tests auth/tenancy attendent un client async et des routes M2-M4 non branchées dans le runtime local MVP.

Diagnostic détaillé : `docs/diagnostics/2026-05-08-full-suite-stratification.md`.

## Comment lancer la démo locale

Depuis la racine :

```bash
cd /Users/jm/context-engine/projects/pli-app
make demo
```

Cela lance :

- backend : `http://127.0.0.1:8000` ;
- frontend : `http://127.0.0.1:5173` ;
- base locale : `.pli-dev/db.sqlite` ;
- pièces jointes locales : `.pli-dev/att` ;
- données démo activées par `PLI_DEMO=true`.

## Blocage humain / décision produit

Pour pouvoir dire que « tout PLI » est terminé, il faut une décision explicite :

1. garder `pli/db.py` SQLite local comme architecture MVP et déplacer officiellement beta/GDPR/OCR/auth/billing en backlog non-gate ; ou
2. migrer vers un package `pli/db/` avec `models.py`, `session.py`, SQLAlchemy, migrations, fixtures pytest et adaptation runtime local/cloud.

Ensuite seulement il sera réaliste de rendre verts `make test-be-all` et `make typecheck-all` sans maquiller les tests historiques.

Les flows externes Gmail/Microsoft/Stripe ne peuvent pas être finalisés sans credentials/flows officiels. Aucun secret réel n’a été affiché, copié, stocké ou inventé pendant cette exécution.
