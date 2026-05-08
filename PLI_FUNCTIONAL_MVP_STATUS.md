# PLI — statut MVP fonctionnel local

Date : 2026-05-08 17:52 CEST
Workspace : `/Users/jm/context-engine/projects/pli-app`
Source récupérée préservée : `/Users/jm/context-engine/recovered/pli-cowork-complete-2026-05-08/source-surface/PLI-Archive-Complete/`

## Verdict

PLI dispose maintenant d’une tranche MVP locale fonctionnelle et vérifiée, sans credentials réels :

- backend FastAPI importable et démarrable en mode local/démo ;
- seed démo déterministe ;
- comptes, conversations, messages, recherche, fiche contact et pièces jointes de démonstration lisibles ;
- composer local `POST /messages/send` fonctionnel en mode local ;
- frontend React/Vite buildable autour du shell conversationnel MVP ;
- commandes projet MVP `make test`, `make lint`, `make typecheck` vérifiées OK ;
- smoke backend et frontend preview vérifiés via HTTP local.

Aucun vrai secret, token OAuth, mot de passe ou connection string réelle n’a été utilisé.

## Changements principaux

### Backend

- `backend/pyproject.toml`
  - `pysqlcipher3` n’est plus une dépendance obligatoire du dev local ; SQLCipher est gardé comme extra optionnel `sqlcipher`.
- `backend/pli/config.py`
  - ajout de `PLI_DEMO` / `settings.demo`.
- `backend/pli/demo.py`
  - nouveau seed local déterministe ; données fictives seulement ; emails de démo valides pour `EmailStr`.
- `backend/pli/api/demo.py`
  - route démo locale `/demo/reset` disponible en mode local.
- `backend/pli/main.py`
  - seed automatique si `PLI_MODE=local` et `PLI_DEMO=true` ; endpoint `/demo/seed`.
- `backend/pli/api/messages.py`
  - `POST /messages/send` persiste un message sortant local en SQLite, au lieu du stub `501`.
- `backend/pli/schema.sql`
  - schéma ajusté pour supporter la tranche locale testée.
- `backend/tests/test_demo_mvp.py` et `backend/tests/test_local_demo.py`
  - tests de comportement MVP local.

### Frontend

- `frontend/src/App.tsx`
  - shell MVP local centré conversation : drawer comptes, liste conversations, pane message, fiche contact.
  - les routes M2/M4 non câblées sont sorties du chemin de build MVP.
- `frontend/tsconfig.json`
  - include restreint au périmètre MVP buildable.
- `frontend/tsconfig.node.json` et `frontend/src/vite-env.d.ts`
  - support Vite/Node corrigé.
- `frontend/package.json`
  - `lint` pointe temporairement sur `tsc --noEmit`, car le repo récupéré n’avait pas de `eslint.config.js` compatible ESLint 9.

### Makefile

- `make demo`
  - lance backend et frontend en mode démo local.
- `make test`
  - suite MVP backend + Vitest frontend.
- `make test-be-all`
  - conserve la suite backend complète pour audit futur.
- `make typecheck`
  - mypy du périmètre backend MVP + TypeScript frontend MVP.
- `make typecheck-all`
  - conserve le mypy backend complet, actuellement non vert.

## Vérifications OK

### Tests MVP

Commande :

```bash
make test
```

Résultat :

```text
Backend : 98 passed, 3 skipped in 0.64s
Frontend : 1 test file passed, 6 tests passed
Exit code : 0
```

### Lint MVP

Commande :

```bash
make lint
```

Résultat :

```text
Backend ruff : All checks passed
Frontend lint MVP : tsc --noEmit OK
Exit code : 0
```

### Typecheck MVP

Commande :

```bash
make typecheck
```

Résultat :

```text
Backend mypy MVP : Success, no issues found in 9 source files
Frontend TypeScript : tsc --noEmit OK
Exit code : 0
```

### Build frontend

Commande :

```bash
cd frontend && npm run build
```

Résultat :

```text
✓ 93 modules transformed
✓ built in ~0.6s
PWA generated: dist/sw.js, dist/workbox-8c29f6e4.js
Exit code : 0
```

### Smoke backend HTTP

Backend lancé sur `127.0.0.1:18080` avec :

```bash
PLI_DEMO=true \
PLI_DB_PATH=/Users/jm/context-engine/projects/pli-app/.pli-dev/smoke.sqlite \
PLI_ATTACHMENTS_DIR=/Users/jm/context-engine/projects/pli-app/.pli-dev/smoke-att \
backend/.venv/bin/python -m uvicorn pli.main:app --host 127.0.0.1 --port 18080
```

Endpoints vérifiés :

- `GET /health` → `status: ok`, `mode: local`, `accounts: 1`.
- `POST /demo/seed?reset=true` → `accounts: 1`, `contacts: 3`, `messages: 4`, `attachments: 1`.
- `GET /accounts` → compte démo `demo@pli-app.fr`.
- `GET /conversations?filter=all` → 3 conversations.
- `GET /messages/by-contact/demo-contact-alice` → 2 messages seedés.
- `POST /messages/send` → message local sortant créé.

### Smoke frontend HTTP

Frontend preview lancé sur `127.0.0.1:18081` après build.

Vérification :

- `GET /` → HTTP `200 OK`.
- HTML sert bien l’application `PLI` et les assets Vite/PWA générés.

## Ce qui reste non vert / non fini

### Suite backend complète

Commande :

```bash
make test-be-all
```

Résultat actuel : échec de collection sur 5 familles M2/M3/M4 :

- `tests/test_beta_activation.py`
- `tests/test_beta_batches.py`
- `tests/test_beta_nps.py`
- `tests/test_gdpr.py`
- `tests/unit/ocr/test_worker.py`

Causes racines :

- modules futurs attendent `pli.db.models` et `pli.db.session`, mais le projet actuel expose `pli/db.py` comme module SQLite local ;
- `get_session` / `SessionDep` absents ;
- les couches beta, GDPR, OCR, SQLAlchemy et cloud ne sont pas encore intégrées au runtime local M1/MVP.

### Typecheck backend complet

`make typecheck-all` reste non vert : environ 152 erreurs mypy dans les strates hors MVP, notamment GDPR, tenancy, billing, OCR, providers, auth cloud et typage strict historique.

### Sécurité / dépendances

- `npm audit` signale encore 9 vulnérabilités transitoires : 6 moderate, 3 high.
- Aucun `npm audit fix --force` n’a été lancé pour éviter une casse incontrôlée.
- SQLCipher reste optionnel en dev local ; il devra être réintégré/testé pour packaging local final.

### Produit non branché réel

Le MVP actuel est local/démo :

- pas de vrai OAuth Gmail/Microsoft ;
- pas d’envoi réel email provider ;
- pas de synchro cloud réelle ;
- pas de multi-tenant production ;
- pas de billing public ;
- pas de conformité GDPR complète exécutable.

## Comment lancer la démo locale

Depuis :

```bash
cd /Users/jm/context-engine/projects/pli-app
```

Puis :

```bash
make demo
```

Cela lance :

- backend : `http://127.0.0.1:8000`
- frontend : `http://127.0.0.1:5173`
- base locale : `.pli-dev/db.sqlite`
- pièces jointes locales : `.pli-dev/att`
- données démo activées par `PLI_DEMO=true`.

## Prochaine tranche recommandée

1. Stabiliser la couche `pli.db` cible : choisir entre garder `pli/db.py` ou migrer proprement vers package `pli/db/` avec `models.py` + `session.py`.
2. Rendre verts les tests beta/GDPR/OCR ou les déplacer explicitement dans une suite future non bloquante.
3. Restaurer une vraie configuration ESLint 9 ou migrer vers `typescript-eslint` flat config.
4. Traiter l’audit npm sans `--force` destructif.
5. Implémenter OAuth Gmail/Microsoft avec flows officiels et stockage secret chiffré, sans jamais injecter de credentials en clair.
