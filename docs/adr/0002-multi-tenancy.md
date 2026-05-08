# ADR 0002 — Multi-tenancy strict

**Statut** : Accepté · **Date** : 2026-06-25 (Sprint 5, S12) · **Auteurs** : TL + SEC
**Contexte** : M2 Cloud · **Supplante** : — · **Supplanté par** : —

## Contexte

En mode Cloud, plusieurs utilisateurs partagent la même base PostgreSQL. Un incident d'isolation (un user lit les messages d'un autre) serait :
- une violation RGPD critique (exposition de correspondance privée),
- un bug qui peut survivre indéfiniment dans le code sans détection, si non testé frontalement.

## Décision

**Défense en profondeur à trois couches**, chacune suffisante pour bloquer une fuite, combinées pour maximiser la probabilité qu'au moins une détecte l'erreur.

### Couche 1 — Contrainte applicative (le repository)

Aucun module métier n'écrit de SQL brut. Toute requête passe par un `TenantScopedRepository` qui :

- Prend `tenant_id` en paramètre constructeur.
- Ajoute systématiquement `WHERE user_id = :tenant_id` à chaque `SELECT/UPDATE/DELETE`.
- Lève `TenantIsolationError` si une requête est construite sans ce filtre.
- Est instancié par un `Depends(get_repo)` qui récupère le tenant depuis le `Principal`.

### Couche 2 — Middleware de contexte

Un `TenantContextMiddleware` FastAPI :

- Résout le `Principal` via l'adapter, pour toute route nécessitant l'auth.
- Stocke `tenant_id` dans un `ContextVar` accessible partout.
- En PG, exécute `SELECT set_config('pli.current_tenant', $1, true)` au début de la connexion.

### Couche 3 — Row-Level Security PostgreSQL

Chaque table `user_id`-owned a une policy :

```sql
CREATE POLICY t_tenant_isolation ON t
    USING (user_id = current_setting('pli.current_tenant', true))
    WITH CHECK (user_id = current_setting('pli.current_tenant', true));
```

Si le middleware oublie un `set_config`, PG refuse la lecture/écriture. Si le
repo oublie son `WHERE`, PG retourne 0 ligne (USING) ou rejette l'INSERT (WITH CHECK).

## Alternatives considérées

- **Une base par tenant** — rejeté : explosion du nombre de DBs (Neon, Supabase facturent à la DB), migrations cauchemardesques.
- **Seulement applicatif** — rejeté : une erreur dans une requête ad-hoc suffit à fuiter.
- **Seulement RLS** — rejeté : un développeur qui oublie `SET LOCAL` rend la RLS inopérante silencieusement.

## Tests obligatoires

`tests/test_tenancy_isolation.py` exécute pour chaque route du CRUD utilisateur :

1. Crée tenants `A` et `B` avec des données distinctes.
2. Authentifié comme `A`, tente : GET/POST/PUT/DELETE sur les ressources de `B`.
3. Attend : `404 Not Found` ou `403` — jamais `200`.
4. Exécuté en CI sur chaque PR, blocant si échec.

## Conséquences

**Positives** : triple sécurité, incidents quasi-impossibles sans effondrement des trois couches simultanément.
**Négatives** : légère surcharge perf (`set_config` par requête, mais négligeable sur PG), boilerplate dans les repos (mitigé par base class).

## Validation

SEC signe la checklist (cf. `docs/sec-checklists/multi-tenancy.md`).
