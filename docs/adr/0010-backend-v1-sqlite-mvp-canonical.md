# ADR 0010 — Backend v1 locale: SQLite MVP canonique, SQLAlchemy M2-M4 en migration future

Statut: accepté pour la v1 locale.

## Contexte

Le corpus PLI récupéré contient deux strates backend différentes:

1. Runtime local MVP actuellement fonctionnel:
   - `backend/pli/db.py` module SQLite synchrone;
   - schéma local, seed démo, API accounts/contacts/conversations/messages/search;
   - gates MVP verts via `make test`, `make lint`, `make typecheck`.

2. Strates futures M2-M4 récupérées:
   - imports attendus `pli.db.models`, `pli.db.session`, `get_session`, `SessionDep`;
   - routes auth cloud, billing, RGPD, OCR, beta/feedback;
   - modèles/fixtures/tables attendus non présents ou non branchés au runtime local.

Le diagnostic `docs/diagnostics/2026-05-08-full-suite-stratification.md` montre que `make test-be-all` et `make typecheck-all` ne peuvent pas devenir verts sans choix d’architecture DB/session.

## Décision

Pour la v1 locale, PLI garde le runtime SQLite MVP comme canonique.

Conséquences directes:

- `make test`, `make lint`, `make typecheck`, `npm run build` restent les gates obligatoires v1 locale.
- `make test-be-all` et `make typecheck-all` restent des diagnostics historiques/futurs, pas des gates v1.
- Les strates M2-M4 restent visibles via `make test-be-future` et `make typecheck-future`.
- Aucun shim opportuniste `pli.db.models` ne sera ajouté tant que la migration SQLAlchemy n’est pas réellement planifiée.

## Raisons

- Le MVP local est déjà utile et testable.
- Forcer SQLAlchemy maintenant mélangerait Local MVP, Cloud, RGPD, billing et OCR dans une seule tranche trop risquée.
- Un shim partiel ferait passer des imports sans fournir les invariants importants: sessions, migrations, tenants, fixtures, tables et lifecycle transactionnel.
- La v1 demandée ici vise une démo locale honnête, pas une fausse complétude M2-M4.

## Gates v1 locale

Obligatoires avant commit/release v1 locale:

```bash
make test
make lint
make typecheck
cd frontend && npm run build
git diff --check
```

Plus:

- scan secrets sur le diff;
- revue indépendante frontend/UX;
- revue indépendante backend/sécurité/scope.

## Diagnostics futurs non bloquants

À conserver visibles:

```bash
make test-be-all
make typecheck-all
make test-be-future
make typecheck-future
```

Statut attendu pour l’instant: rouge ou partiellement rouge tant que la migration M2-M4 n’est pas ouverte.

## Plan de migration future vers SQLAlchemy/PostgreSQL

Si on choisit plus tard l’option B:

1. Créer un package `backend/pli/db/` en remplaçant proprement `db.py`.
2. Introduire `models.py`, `session.py`, `migrations/` et fixtures pytest.
3. Migrer les endpoints MVP SQLite un par un avec tests de non-régression.
4. Ajouter une matrice SQLite Local + PostgreSQL Cloud.
5. Réactiver progressivement les familles futures:
   - auth/session;
   - tenancy;
   - OCR/PJ;
   - GDPR export/delete;
   - billing/Stripe;
   - beta/feedback.
6. Ne déclarer `make test-be-all` gate obligatoire qu’après passage vert documenté.

## Invariants à préserver pendant migration

- Recherche/contact/messages/PJ restent scopés par compte/tenant.
- Aucun token OAuth ou secret n’est projeté au frontend.
- Local continue à fonctionner sans Cloud, Stripe ou provider réel.
- Les migrations ne détruisent pas de données locales sans sauvegarde/export.

## Références

- `docs/diagnostics/2026-05-08-full-suite-stratification.md`
- `docs/diagnostics/2026-05-08-runtime-backend-frontend.md`
- `Makefile`
- `docs/planner/PLI_PLANNER_V1.md`
