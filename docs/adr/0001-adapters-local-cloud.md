# ADR 0001 — Adapters Local vs Cloud

**Statut** : Accepté · **Date** : 2026-06-18 (S11-J2, après spike) · **Auteurs** : TL + BE
**Contexte** : M2 · **Supplante** : — · **Supplanté par** : —

## Contexte

PLI doit fonctionner selon deux modes :

- **Local** : SQLite chiffré, stockage fichier local, pas d'utilisateur PLI (l'OS est l'auth), 1 tenant = 1 machine.
- **Cloud** : PostgreSQL multi-tenant, stockage objet S3-compatible, auth PLI avec JWT, N tenants par instance.

Le code M1 est écrit en supposant implicitement le mode Local (chemins absolus `~/.pli/`, connexion sqlite3 directe, pas de notion de `user_id` dans les requêtes). Continuer ainsi mènerait à un enchevêtrement `if settings.mode == "cloud":` non maintenable.

## Décision

On introduit un **pattern adapters** avec une interface par domaine d'isolation, et deux implémentations concrètes (Local, Cloud) sélectionnées au démarrage via `settings.mode`.

### Domaines isolés

| Domaine | Interface | Local | Cloud |
|---|---|---|---|
| **Storage** (PJ) | `StorageAdapter` | disque chiffré `~/.pli/att/` | S3-compatible (R2/Scaleway) |
| **Database dialect** | SQLAlchemy URL | `sqlite:///` + SQLCipher | `postgresql+psycopg://` |
| **Full-text search** | `SearchAdapter` | FTS5 virtual table | `tsvector` + GIN index |
| **Auth principal** | `PrincipalResolver` | OS user → fixed tenant | JWT → tenant_id |
| **Settings store** | `SettingsStore` | fichier TOML local | table `user_settings` PG |
| **Crypto at rest** | `CryptoAdapter` | Keychain OS / DPAPI | KMS côté provider |

### Principe d'injection

Un `Container` (pli/adapters/container.py) construit les instances concrètes au démarrage et les injecte via FastAPI `Depends`. Aucun code métier ne lit `settings.mode` directement — seul le container le fait.

### Contrat minimal

Tous les adapters respectent :
1. Méthodes 100% async
2. Pas d'état mutable global
3. Exceptions métier typées (`StorageNotFound`, `TenantIsolationError`, etc.)
4. Tests avec double implémentation (Local + Cloud) sur chaque domaine

## Alternatives considérées

- **Flags `if mode == cloud:` inline** — rejeté : dette immédiate, tests impossibles à isoler.
- **Deux codebases séparées (`pli-local`, `pli-cloud`)** — rejeté : synchronisation des features devient cauchemardesque, le MVP n'est pas assez gros pour justifier.
- **Plugin system dynamique** — rejeté : overkill pour 2 variantes, bascule runtime pas nécessaire.

## Conséquences

**Positives** :
- Tests unitaires possibles sur chaque adapter avec double impl
- Passage Local ↔ Cloud testable en CI (même code exerce les deux chemins)
- Ajout futur d'un 3e mode (ex. enterprise on-prem) coûte un set d'adapters, pas une refonte

**Négatives** :
- Surcouche d'abstraction sur du code simple → compensée par le fait que les domaines concernés sont peu nombreux (6)
- Discipline requise : aucun appel `open(path)` / `psycopg.connect()` hors des adapters

## Plan d'implémentation (Sprint 5)

1. Scaffold `pli/adapters/` avec interfaces (J1)
2. Impl `StorageAdapter` local + S3 (US-5.8, J2-J3)
3. Bascule `db.py` vers SQLAlchemy + dialecte PG (US-5.2, J3-J5)
4. `PrincipalResolver` + `tenant_context` middleware (US-5.3, J5-J7)
5. `CryptoAdapter` basé sur la lib `cryptography` déjà présente (J8)
6. Retrait des derniers `settings.mode ==` hors container (J9)

## Validation

L'ADR est validée par TL + Founder avant démarrage refactor (feu vert J3 du Sprint 5).
