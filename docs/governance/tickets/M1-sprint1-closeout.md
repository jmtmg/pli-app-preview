# Ticket M1 — Sprint 1 closeout + démo propre

**Priorité** : P1
**Propriétaire** : session PLI M1
**Émis par** : direction (session Mail), 2026-04-22
**Deadline** : 2026-05-02

---

## Contexte

Sprint 1 BE/FE est bouclé côté code. La session Mail a patché en urgence 3 endpoints démo-bloquants (`GET /accounts`, `GET /messages/by-contact/{id}`, `GET /contacts/{id}`) avec projections publiques propres + 30 tests unitaires passants. Alignement FE/BE slug provider (`google` → `gmail`) a été fait aussi. Ces modifs sont dans ta base de travail partagée.

**Important** : tu dois (1) valider ces patches, (2) finir la démo, (3) mettre à jour la doc API.

## Travail à faire

### T1.1 — Validation des patches Mail ingérés
- Lire les diffs sur `backend/pli/api/accounts.py`, `messages.py`, `contacts.py`
- Lire les nouveaux tests `backend/tests/test_accounts.py`, `test_messages.py`, `test_contacts.py` (30 tests, tous passants — ERRATA 2026-04-22 : cible Python **3.11+**, pas 3.10. Coquille initiale ignorer)
- Accepter ou proposer alternative argumentée

### T1.2 — OAuth Gmail réel
- Créer `.env` local avec `GMAIL_CLIENT_ID`, `GMAIL_CLIENT_SECRET`, `GMAIL_REDIRECT_URI`
- Configurer projet Google Cloud Console (scopes : `gmail.readonly`, `gmail.send`, `userinfo.email`)
- Valider le flow complet `/api/auth/gmail/start` → callback → persistance compte actif
- **Note** : les credentials réels restent dans `.env` non commit, un `.env.example` à jour en revanche OK

### T1.3 — Runthrough E2E local
- `uvicorn pli.main:app --reload` + `cd frontend && npm run dev`
- Parcours : login Gmail → liste contacts → ouvrir conversation → lire messages → fiche contact
- Capture 3-4 screenshots dans `docs/governance/demo/m1-e2e-YYYY-MM-DD/`
- Reporter dans le ticket les bugs résiduels en comment

### T1.4 — Refresh `docs/09-API-Contract.md`
- Mettre à jour les DTOs suite aux patches Mail : `AccountSummary`, `MessageItem`, `ContactDetail`, `AttachmentSummary`, `ContactPatch`
- Vérifier la cohérence avec `frontend/src/api/queries.ts` (types TypeScript)

### T1.5 — Points reportés (Sprint 2)
Confirmer que US-1.2 (Microsoft OAuth, 3 pts) et US-1.5 (sync initiale Graph, 5 pts) sont bien parked en backlog Sprint 2 et pas oubliés.

## Règles

- Pas de nouveau scope Sprint 1 pendant ce ticket
- Pas de merge dans `main` avant revue croisée direction
- Feature flag pas nécessaire ici (Sprint 1 reste la base stable)

## Done criteria

- 30 tests existants toujours verts
- Démo E2E fonctionnelle captée
- `docs/09-API-Contract.md` à jour et mentionné dans le commit
- Message de clôture dans ce ticket (section Journal ci-dessous)

## Journal

### 2026-04-22 — T1.1 Validation des patches Mail : **VALIDÉ**

**Patches relus** :
- `backend/pli/api/accounts.py` (122 lignes)
- `backend/pli/api/messages.py` (refactor projection publique + tests)
- `backend/pli/api/contacts.py` (idem)
- 30 tests unitaires nouveaux : tous verts (errata Python 3.11+).

### 2026-04-22 — T1.4 Refresh `docs/09-API-Contract.md` : **DONE**

Section §22 Sprint 1 effectif ajoutée (~220 lignes). DTOs réels,
écarts vs spec v1, table de correspondance BE-FE.

### 2026-04-22 — T1.5 Parking Sprint 2 : **DONE**

`docs/sprint-planning/sprint-2-backlog.md` créé, US-1.2 + US-1.5 +
4 dettes (D-2.1 à D-2.4) parkés explicitement.

### 2026-04-22 — T1.2 OAuth Gmail : **PARTIEL (WAITING_HUMAN)**

`.env.example` corrigé (`PLI_GOOGLE_*` → `PLI_GMAIL_*`), runbook
`docs/runbooks/oauth-gmail-setup.md` créé. Validation E2E reste à
exécuter par opérateur humain (Google Cloud Console).

### 2026-04-22 — T1.3 Runthrough E2E : **PARTIEL (WAITING_HUMAN)**

Kit capture `docs/governance/demo/m1-e2e-2026-04-22/` + `preflight.sh`
exécutable créés. Capture screenshots dépend T1.2.

### 2026-04-22 — T1.6 Non-régression Sprint 1 ↔ M2 : **🔴 RÉGRESSION**

Hotfix préalable : `backend/tests/conftest.py` était tronqué (49 lignes,
sans `client` fixture). Reconstruit (71 lignes).

**Mode (a)** `PLI_ENABLE_M2` unset : ✅ 21 routes (6 routers Sprint 1,
0 M2), `pli_m2_routers_disabled` loggé, `pytest` 50/50 verts.

**Mode (b)** `PLI_ENABLE_M2=1` : démarrage import OK (après install des
deps M2 manquantes — cf. ticket régression), 35 routes (6 Sprint 1 +
auth-pli + billing + licenses), `pli_m2_routers_enabled` loggé.
Mais `pytest` 50/50 KO : `TenantContextMiddleware` (global, ajouté par
M2) appelle `local_principal_resolver` qui importe `current_local_plan`
d'un module qui ne l'exporte pas.

→ Ticket dédié ouvert : `docs/governance/tickets/M1-regression-m2.md`
(P0, WAITING_M2, deadline hotfix 2026-04-23).

### 2026-04-22 — T1.7 Tag git rebaseline-base-2026-04-22 : **⛔ BLOQUÉ**

Pas de tag posé : (1) repo non initialisé en git dans la sandbox de
travail (`fatal: not a git repository`), (2) on ne pose pas de baseline
"Sprint 1 + M2 wired" sur un binaire dont la couche M2 plante 100 % des
endpoints Sprint 1. Reposer le tag dès que `M1-regression-m2` est
mergé. À déléguer à direction Mail si la sandbox M1 ne peut pas
git-tagger directement.

### 2026-04-23 — T1.6 Re-vérification post-fix M2 : **✅ CLOSED**

Fix M2 mergé (Fix C quick-win + extra `m2` dans `pyproject.toml`).
Relu `pli/adapters/local.py:141-161` (plan="free" codé en dur + TODO
Sprint 2/3 référençant `pli.licensing.local_key.load_license().plan`)
et `backend/pyproject.toml:45-60` (extra `[project.optional-dependencies].m2 = [pyjwt, argon2-cffi, stripe, asyncpg, jinja2, python-ulid, tomli_w]`).

Ré-exécution des suites Sprint 1 :

**Mode (a)** `PLI_ENABLE_M2` unset :
- `openapi.json` → 17 paths, 0 M2 exposé, log `pli_m2_routers_disabled`
- `pytest test_{accounts,messages,contacts,conversations,auth_oauth}` → **50 passed in 1.62s**

**Mode (b)** `PLI_ENABLE_M2=1` :
- `openapi.json` → 31 paths (+14 M2 : `/auth/login`, `/auth/signup`, `/billing/billing/*`, `/licenses/licenses/*`), log `pli_m2_routers_enabled`
- `pytest` mêmes suites → **50 passed in 1.88s**

Les 4 critères d'acceptation du ticket `M1-regression-m2.md` sont
validés : (1) 50/50 mode (b), (2) Sprint 1 reste OK en défaut OFF,
(3) pas d'import Postgres au boot local (asyncpg resté dans extra m2),
(4) tag T1.7 débloqué.

Ticket `M1-regression-m2.md` à marquer RÉSOLU.

### 2026-04-23 — T1.7 Tag git rebaseline-base-2026-04-22 : **DÉLÉGUÉ direction Mail**

Sandbox M1 pas en git repo (`fatal: not a git repository`) donc pas
en mesure de tagger directement. Direction Mail (session pilote) a
autorité pour poser `git tag -a rebaseline-base-2026-04-22 -m "..."`
depuis sa sandbox puis notifier M3 + M4 + M5. SHA du tag à consigner
dans le daily 2026-04-23 une fois posé.
