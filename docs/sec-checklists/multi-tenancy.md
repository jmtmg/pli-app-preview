# Checklist SEC — Isolation multi-tenant (M2)

Validée par **SEC** avant merge du Sprint 5.

## Couche 1 — Applicative

- [x] Toutes les classes `*Repository` héritent de `TenantScopedRepository`
- [x] Aucun `import sqlite3` ou `import asyncpg` direct hors de `pli/db.py` et `pli/adapters/*`
- [x] `grep -R "FROM messages\|FROM contacts\|FROM accounts\|FROM attachments\|FROM drafts" backend/pli/` ne renvoie que des requêtes contenant `WHERE user_id`
- [x] Tests `test_repository_refuses_sql_without_user_id` passent

## Couche 2 — Middleware

- [x] `TenantContextMiddleware` enregistré sur l'app FastAPI (cf. main.py)
- [x] Liste `PUBLIC_PATHS` revue : aucun endpoint sensible
- [x] Test `test_no_token_no_access` passe sur toutes les routes protégées
- [x] Le `ContextVar` `_current_tenant` est correctement reset à la fin du middleware

## Couche 3 — RLS PostgreSQL

- [x] `ALTER TABLE … ENABLE ROW LEVEL SECURITY` appliqué sur les 8 tables `user_id`-owned
- [x] Policy `t_tenant_isolation` créée avec `USING` et `WITH CHECK`
- [x] `set_config('pli.current_tenant', $1, true)` injecté dans `get_pg_conn(tenant_id)`
- [x] Test `test_rls_blocks_query_without_set_config` passe en mode cloud
- [x] Le rôle DB applicatif n'est PAS superuser ni propriétaire (le superuser bypass RLS)

## Tests d'isolation cross-tenant

- [x] `test_tenancy_isolation.py` couvre toutes les routes API listées dans `09-API-Contract.md`
- [x] Lancé en CI sur chaque PR avec marker `@pytest.mark.security`
- [x] Échec = block merge

## Audit log

- [x] Toute exception `TenantIsolationError` est loggée niveau WARNING avec contexte (path, tenant_attendu, tenant_obtenu) — alerte si > 5/heure (sentry rule)
- [x] Une route `/admin/audit/tenant-violations` (réservée founder) liste les incidents

## Signature

- **Date** : 2026-06-30 (fin Sprint 5)
- **SEC reviewer** : SEC agent (revue confiée à un agent spécialisé)
- **Status** : ✅ Validée — feu vert merge multi-tenancy
