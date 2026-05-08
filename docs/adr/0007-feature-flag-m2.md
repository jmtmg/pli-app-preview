# ADR 0007 — Feature flag `PLI_ENABLE_M2` (kill-switch rollout Local+Cloud+Paiement)

**Statut** : accepté
**Date** : 2026-04-22
**Auteurs** : session M2
**Contexte d'émission** : ticket `docs/governance/tickets/M2-unblock-auth.md` (P0 bloquant), ordre de mission `docs/governance/2026-04-22-ordre-mission.md` §2 D3.

---

## Contexte

L'audit transverse du 2026-04-22 a révélé un écart entre :

- ce qui était livré par la session M2 (Sprints 5 et 6) — billing Stripe, auth PLI, licensing Ed25519, emails, middleware tenant, adapters Local/Cloud ;
- et l'état de `pli/main.py` qui ne montait que les routers M1 (Sprint 1).

Conséquence directe :
- `pytest --collect-only backend/tests/` cassait sur `ModuleNotFoundError: pli.auth` (packaging incorrect, renommé en T2.1) ;
- les tests M2 qui collectent n'étaient de toute façon pas exécutés sur un binaire intégré ;
- M3 (beta/OCR), M4 (GDPR/KB) et M5 (launch) ne pouvaient pas re-baseliner parce que le binaire n'intégrait pas encore les couches M2.

Nous devons pouvoir **monter les routers M2 sans déstabiliser la démo M1** tant que la convergence n'est pas validée par la direction.

## Décision

Introduire un **feature flag binaire** `PLI_ENABLE_M2` dans `pli.config.Settings.enable_m2`, géré comme tous les autres settings (prefix `PLI_`, lecture `.env` / env vars). Par défaut **off**.

Dans `pli/main.py`, le montage des routers M2 et du middleware multi-tenant est gardé par ce flag :

```python
if settings.enable_m2:
    from .api import auth_pli, billing, licensing
    from .tenancy.context import TenantContextMiddleware
    app.add_middleware(TenantContextMiddleware)
    app.include_router(auth_pli.router, prefix="/auth", tags=["auth-pli"])
    app.include_router(billing.router,  prefix="/billing",  tags=["billing"])
    app.include_router(licensing.router, prefix="/licenses", tags=["licenses"])
```

Conséquences attendues :

| Contexte                | `PLI_ENABLE_M2` | Comportement                                          |
|-------------------------|-----------------|-------------------------------------------------------|
| démo M1 / prod launch   | `0` (défaut)    | Uniquement routers M1 — aucun régression Sprint 1.    |
| CI M2+ / dev M2         | `1`             | Tous les routers M2 + middleware tenant actifs.       |
| staging intégré         | `1`             | Cible de re-baseline M3/M4 après T2.2 (2026-05-07).   |
| prod post-launch (Plus) | `1`             | Activation définitive, puis retrait du flag (cf §5).  |

## Alternatives considérées

1. **Pas de flag — merge direct** — refusé : casse la démo M1 si une dépendance M2 pète. La direction exige une revue croisée (§4 ordre de mission) avant tout merge M2→main.
2. **Branche git dédiée `m2-integration`** — refusé : nous sommes déjà sur main convergé (decision D1), une branche vivante 3 semaines diverge vite et complique le re-baseline M3/M4 qui doit tester `main` tel quel.
3. **Flag par sub-router** (`PLI_ENABLE_BILLING`, `PLI_ENABLE_AUTH_PLI`, …) — refusé pour la phase intégration : trop de combinaisons à tester ; un seul booléen aligné sur la frontière M1↔M2 est suffisant.

## Plan de rollout

1. **2026-04-30** — T2.1 terminée (rename `auth_pli`→`auth` + stubs `dependencies.py`/`deps.py`) : collection pytest verte.
2. **2026-05-07** — T2.2 terminée (ce flag + wire-up) : `PLI_ENABLE_M2=1 pytest` vert ; OpenAPI expose `/billing/*`, `/licenses/*`, `/auth/signup`.
3. **2026-05-14** — T2.3 terminée (checkpoint 42/42) ; M3+M4 re-baseline sur binaire intégré avec flag on (D5).
4. **2026-05-18** — fin de l'integration sprint ; direction décide si flag on devient le défaut en staging.
5. **2026-08-26** — integration freeze (D4) : si le flag n'a généré aucun incident, **retrait du flag** programmé en Sprint 10 (branche `m2-cleanup`, ~3j de travail).

## Critères de retrait

Le flag disparaît quand **toutes** les conditions ci-dessous sont satisfaites :

- Deux sprints consécutifs avec `PLI_ENABLE_M2=1` en staging **sans** régression M1 déclarée par M3/M4 (audit croisé).
- Coverage tests M2 ≥ 80 % (item T2.3 du checkpoint).
- Stripe webhooks idempotents validés en conditions réelles (événements test sandbox + 1 paiement live dry-run chez chaque maintainer).
- Direction donne feu vert écrit dans un log daily `docs/governance/daily/mail-<date>.md`.

Retirer le flag = supprimer la branche `if settings.enable_m2:` dans `main.py` + supprimer `enable_m2` dans `config.py` + mettre à jour ce ADR en « Statut : retiré » avec pointeur sur le commit de cleanup.

## Rollback

Si un incident est détecté en staging ou en prod post-activation :

- `PLI_ENABLE_M2=0 && systemctl restart pli` (Fly.io : `fly secrets set PLI_ENABLE_M2=0 && fly deploy --strategy rolling`) remet l'app dans l'état Sprint 1 en < 60 s.
- Les données déjà écrites par les handlers M2 (comptes users, subscriptions Stripe) persistent en base mais ne sont plus exposées tant que le flag n'est pas rerouvert.
- La table `webhook_events` reste idempotente : après réactivation, Stripe redélivre les events manqués, on les absorbe sans double-effet.

## Conséquences

**Positives**
- Convergence possible dès que T2.2 est mergée, sans étape « big bang ».
- Kill-switch instantané en cas de régression M1 liée aux middlewares M2 (notamment `TenantContextMiddleware`).
- M3/M4 peuvent re-baseliner sur `main` avec `PLI_ENABLE_M2=1` sans bloquer le train M5 qui démarrera avec `=0`.

**Négatives**
- Dette technique temporaire : le flag doit disparaître avant le freeze (2026-08-26) — sinon il devient un « config fossile » dangereux.
- Duplication mineure de coverage : chaque suite test doit être lancée en CI une fois avec flag on, une fois avec flag off, pour garantir qu'aucune régression Sprint 1 n'est masquée.
- Documentation à maintenir : `README.md` et `docs/09-API-Contract.md` doivent signaler les routes conditionnées par le flag.

## Références

- Ticket P0 : `docs/governance/tickets/M2-unblock-auth.md`
- Ordre de mission : `docs/governance/2026-04-22-ordre-mission.md`
- ADR 0001 (adapters Local/Cloud), 0002 (multi-tenancy), 0003 (JWT), 0004 (Stripe), 0005 (emails), 0006 (licensing Ed25519)
- ADR 0008 (integration freeze) — fige la suppression du flag avant le 2026-08-26
