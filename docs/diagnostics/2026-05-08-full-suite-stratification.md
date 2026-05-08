# PLI — stratification suites backend futures et qualité frontend

Date : 2026-05-08 18:16 CEST
Workspace : `/Users/jm/context-engine/projects/pli-app`
Base investiguée : `3051bef feat: add local functional MVP slice`

## Synthèse

Le MVP local reste fonctionnel. La vague finale a reproduit les gates complets et confirme que les strates M2-M4 récupérées ne sont pas intégrables proprement sans décision d’architecture DB/session et sans compléter les flows produit associés. Elles sont désormais nommées par commandes dédiées pour rester visibles, sans les faire passer pour des gates du produit local.

## Reproduction initiale

Commandes lancées depuis la racine du repo :

```bash
make test-be-all
make typecheck-all
make lint
make typecheck
make test
cd frontend && npm audit --audit-level=moderate
cd frontend && npm run build
```

Résultats observés :

- `make test` : OK (`98 passed, 3 skipped` backend MVP ; Vitest frontend `6 passed`).
- `make lint` : OK après restauration ESLint 9 flat config (`eslint . && tsc --noEmit`).
- `make typecheck` : OK.
- `cd frontend && npm run build` : OK (`vite v5.4.21`, `93 modules transformed`).
- `make test-be-all` : KO en collection sur les imports historiques `pli.db.models`, `pli.db.session`, `get_session`.
- `make typecheck-all` : KO (144 erreurs mypy initiales sur 37 fichiers, ramenées à 125 erreurs dans la cible future isolée car elle ne mélange plus les modules MVP déjà typés).
- `npm audit --audit-level=moderate` : KO mais réduit de `9 vulnérabilités (6 moderate, 3 high)` à `6 moderate` via `npm audit fix` non forcé.

## Causes racines backend

### 1. Collision d’architecture `pli.db`

Le runtime local actuel expose `backend/pli/db.py` comme module SQLite synchrone MVP. Les strates futures beta/GDPR/OCR importent au contraire :

- `from pli.db.models import ActivationEvent`, `Invitation`, `WaitlistEntry`, `FeedbackSubmission` ;
- `from pli.db.session import SessionDep`, `session_scope` ;
- `from pli.db import get_session`, `Session`, `get_db`.

Python ne peut pas résoudre `pli.db.models` ou `pli.db.session` tant que `pli.db` est un module fichier et non un package. Ajouter un shim ad hoc masquerait le vrai problème : les modèles SQLAlchemy, les fixtures, les migrations et la session lifecycle M2-M4 ne sont pas présents dans la source récupérée courante.

### 2. Le full historique contient plus que les 5 erreurs de collection visibles

En ignorant temporairement les 5 fichiers qui bloquent la collection (`test_beta_*`, `test_gdpr.py`, `tests/unit/ocr/test_worker.py`), pytest révèle ensuite d’autres strates futures non câblées :

- fixtures absentes : `db_session`, `user_factory`, `waitlist_factory`, `feedback_factory`, `make_attachment`, `make_attachment_with_text`, `auth_headers`, `mail_outbox`, `verified_user`, `client_other_user`, `fake_queue`, `storage_mock`, `freezer` ;
- tables absentes dans le schéma SQLite MVP : `users`, sessions/refresh tokens, feedback, exports, attachment_text ;
- routes M2-M4 désactivées dans `pli.main` ou non branchées en local : auth PLI, feedback, OCR API, billing/subscription, RGPD ;
- `tests/test_tenancy_isolation.py` mélange client async attendu et fixture `TestClient` synchrone du MVP, et contient un `skipif` qui référence `settings` sans import.

Résultat de cette sonde : `116 passed, 3 skipped, 4 failed, 27 errors` après exclusion temporaire des 5 fichiers de collection.

### 3. Typecheck complet

`make typecheck-all` échoue sur les familles hors MVP : auth, beta, billing, GDPR, OCR, providers, tenancy, adapters/cloud, crypto backups/attachments. Les erreurs ne sont pas uniquement cosmétiques : elles pointent vers des attributs de modèles absents (`User`, `AuditLog`, `ExportJob`, `RefreshToken`, `Account.user_id`, `Message.raw_source`, etc.) et des signatures API incompatibles.

## Isolation explicite ajoutée

Les commandes existantes gardent leur signification :

```bash
make test          # gate MVP local backend + frontend
make lint          # ruff MVP + ESLint 9 flat config + TypeScript MVP
make typecheck     # mypy MVP + TypeScript MVP
make test-be-all   # suite backend historique complète, encore rouge
make typecheck-all # mypy backend complet, encore rouge
```

Deux commandes de diagnostic explicites ont été ajoutées :

```bash
make test-be-future
make typecheck-future
```

Elles rejouent uniquement les strates récupérées non-MVP : auth, tenancy, feedback, Stripe/billing, beta, GDPR et OCR. Elles sont attendues rouges tant que l’architecture DB/session M2-M4 n’est pas décidée et implémentée proprement.

## Qualité frontend

Actions réalisées :

- ajout `frontend/eslint.config.js` en flat config ESLint 9 (`@eslint/js`, `typescript-eslint`, `globals`) ;
- `frontend/package.json` : `lint` exécute maintenant `eslint . && tsc --noEmit` au lieu du fallback temporaire `tsc --noEmit` seul ;
- `npm audit fix` non forcé appliqué : suppression des vulnérabilités `serialize-javascript` high via mise à jour transitive du lockfile ;
- ajout des dev deps nécessaires à ESLint TS (`typescript-eslint`, `globals`).

État restant `npm audit` : 6 vulnérabilités `moderate` liées à `vite <=6.4.1` / `esbuild <=0.24.2` via Vite/Vitest/vite-plugin-pwa. La correction npm proposée exige `npm audit fix --force` vers `vite@8.0.11`, changement majeur. Je ne l’ai pas forcée dans cette exécution pour éviter une migration destructive non demandée du toolchain Vite/PWA ; le build et les tests restent verts avec Vite 5.

## Décision humaine restante

Pour rendre vraiment verts `make test-be-all` et `make typecheck-all`, il faut choisir et implémenter une des deux directions :

1. **Conserver le MVP local SQLite module `pli/db.py`** et déplacer/archiver officiellement les strates M2-M4 comme backlog non-gate ; ou
2. **Migrer vers une architecture package `pli/db/` SQLAlchemy** avec `models.py`, `session.py`, migrations, fixtures pytest et adaptation du runtime local/cloud.

Sans cette décision, prétendre que beta/GDPR/OCR/auth/billing sont terminés serait incorrect. Les fonctionnalités externes Gmail/Microsoft/Stripe restent volontairement mockées/locales tant que des flows officiels et secrets réels ne sont pas fournis.
