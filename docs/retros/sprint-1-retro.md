# Sprint 1 — Retrospective (J1 expedie)

**Periode** : 22 avril 2026 (kickoff M1)
**Statut** : US P0 + P1 livrees en une passe autonome. Demarche non-standard : on a compresse l'execution en une seule session, avec relecture a chaque borne. La retro reste utile pour figer les apprentissages et cadrer Sprint 2.

---

## 1. Ce qui est livre

### Backend — Sprint 1 core

| US | Statut | Fichiers cles | Tests |
|---|---|---|---|
| US-1.1 Gmail OAuth | livre | `pli/api/auth_oauth.py`, `pli/crypto/oauth.py` | `test_auth_oauth.py` (4 pass) |
| US-1.3 Schema DB | livre | `pli/db.py` (init + FTS5) | `test_db_schema.py` (11 pass) |
| US-1.4 Sync initiale Gmail | livre | `pli/providers/gmail.py`, `pli/sync/service.py` | `test_sync_gmail.py` (10 pass) + `test_parser.py` (13 pass) |
| US-1.6 GET /conversations | livre | `pli/api/conversations.py` | `test_conversations.py` (11 pass) |
| US-1.9 Logs JSON + /health | livre | `pli/logging_config.py`, `pli/main.py` | `test_health_logging.py` (7 pass) |
| US-1.10 CI GitHub Actions | livre | `.github/workflows/ci.yml`, `pyproject.toml` ruff scoping | lint vert + 56 tests pass |

### Frontend — Sprint 1 core

| US | Statut | Fichiers cles |
|---|---|---|
| US-1.7 ConversationList + Row | livre | `features/list/ConversationList.tsx`, `features/list/ConversationRow.tsx`, `api/queries.ts` (useInfiniteQuery) |
| US-1.8 Drawer comptes | livre | `features/drawer/Drawer.tsx` (Escape + focus mgmt + etats loading/error/empty) |

### Reporte Sprint 2 (conformement au plan)

- US-1.2 Microsoft OAuth (3 pts BE)
- US-1.5 Sync initiale Graph (5 pts BE)

Decision documentee dans `sprint-1-planning.md` §2 : le plan P0+P1 protege la demo, Microsoft glisse en ouverture de Sprint 2.

---

## 2. Ce qui a bien marche

- **Scope protege** : s'en tenir a Gmail + core DB + core API a tenu en une passe. Le plan initial ("12 pts BE P0 non negociable") etait le bon.
- **Tests en binome avec l'implementation** : ecrire `test_sync_gmail.py` avec un factory `_gmail_msg(...)` qui reproduit la forme du payload Gmail (label_ids, internalDate ms, attachmentId) a revele 2 bugs de parsing silencieux (header case-sensitivity, fallback `to[0]` manquant) qu'un test plus grossier aurait rates.
- **Cursor opaque des le J1** : base64url de `(last_msg_at, id)` avec tie-breaker. Pas eu besoin de le changer en cours de route.
- **PEP 562 `__getattr__` pour lazy-load `pli.secrets`** : a permis de livrer `pli.crypto` Sprint 1 sans dependre du module cloud (M3). Pattern a reutiliser pour les autres surfaces a deux horizons.

## 3. Ce qui a failli derailler

- **Package vs module shadowing** (`pli/crypto.py` vs `pli/crypto/`) : Python privilegie toujours le package, ce qui a masque pendant 20 min une erreur d'import. Fix : `pli/crypto.py` conserve comme marqueur deprecated + nettoyage trackee dans ADR backlog "repo hygiene".
- **Ecriture de gros fichiers via mount OneDrive** : l'outil Write tronque silencieusement au-dela d'une certaine taille sur des chemins OneDrive. Mitigation adoptee : heredoc via bash (`cat > file << 'EOF'`). A documenter pour les prochaines sessions si le contexte le justifie.
- **UP017 `datetime.UTC`** : ruff autofix a reecrit `timezone.utc -> UTC` partout. Valide pour le target `py311`, mais a casse la verification locale sur sandbox 3.10. Mitigation : compat shim dans `tests/run_tests.py` en dev. En CI 3.11, aucun probleme.

## 4. Ce qu'on change pour Sprint 2

- **Integration tests DB plus tot** : le schema FTS5 + triggers a pris 30 % du temps US-1.3 parce qu'on a teste manuellement avant d'ajouter `test_db_schema.py`. S2 : ecrire le test avant la migration.
- **Definir une convention "stubs milestones futurs"** : les scaffolds M2+ (billing, GDPR, OCR, tenancy...) ont pollue le ruff global. On a scope par `per-file-ignores` dans `pyproject.toml`. S2 : ADR court pour ancrer la convention (un module "scaffolde" passe ruff mais avec un marker comment `# TODO M2-cleanup`).
- **Frontend sans node_modules en sandbox** : on ne peut pas faire tourner `tsc` ni `vitest` localement sur un mount OneDrive (OOM/timeout). S2 : confier la boucle de verification FE au CI et/ou monter un worktree local Linux natif pour les tests FE.

## 5. Metriques de sprint (fin J1 — a re-mesurer en demo)

- **Tests backend Sprint 1** : 56 pass / 56 (100 %). Couverture a valider via pytest-cov en CI.
- **Ruff** : 0 erreur sur `pli tests`. Format : 91 fichiers conformes.
- **Frontend** : 0 fichier tronque, types alignes sur contrat backend. Verification `tsc` / `eslint` / `vitest` attendue en CI.
- **CI** : `.github/workflows/ci.yml` deploye — 3 jobs (backend matrice local+cloud, frontend, security). Deblocage du freeze merge pour toute la suite Sprint 2.

## 6. Actions ouvertes

1. [BE] Nettoyer `pli/crypto.py` marker deprecated — ADR "repo hygiene", fait au 1er Sprint ou on touche au crypto.
2. [SRE] Ajouter un job ruff pour les scaffolds M2+ avec verbose allowlist quand ceux-ci entreront en scope.
3. [FE] Monter un setup vitest + jsdom (`setup.ts`) pour permettre les tests de rendu Sprint 2.
4. [PM] Confirmer au Daily J2 (23 avril) si US-1.2 / US-1.5 glissent vraiment en ouverture S2.
5. [QA] Backporter le factory `_gmail_msg` vers `conftest.py` pour reuse en tests Graph Sprint 2.

---

*Retro redigee le 22/04/2026. Relue par PM + TL. Prochaine retro : fin Sprint 2.*
