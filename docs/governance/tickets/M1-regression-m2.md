# Ticket M1 — Régression Sprint 1 ↔ wire-up M2 (`PLI_ENABLE_M2=1`)

**Priorité** : P0 (bloque la baseline coordonnée M3/M4)
**Émis par** : session M1, 2026-04-22, dans le cadre de T1.6 du
`M1-sprint1-closeout.md`
**Propriétaire pressenti** : session M2 (auteur du wire-up)
**Direction** : Mail (à notifier au sync hebdo si pas mergé sous 24 h)
**Deadline hotfix** : 2026-04-23 fin de journée (cohérent avec deadline T1.7)

---

## TL;DR

Avec `PLI_ENABLE_M2=1`, **100 % des endpoints Sprint 1 retournent
`401 auth_failed`** parce que `TenantContextMiddleware` (ajouté global
par M2 dans `pli/main.py:116`) appelle `local_principal_resolver`
(`pli/adapters/local.py:135`) qui importe une fonction inexistante :

```
ImportError: cannot import name 'current_local_plan'
              from 'pli.billing.licenses'
              (/.../pli/billing/licenses.py)
```

Le kill-switch `PLI_ENABLE_M2` protège donc bien la baseline Sprint 1
en mode défaut (off → 50/50 tests verts), mais le mode (b) demandé par
le ticket T1.6 ("Sprint 1 toujours 100 % avec M2 enabled") est
définitivement KO tant que ce contrat d'import n'est pas réparé.

## Reproduction

```bash
cd backend
pip install -e .
pip install pyjwt stripe python-ulid argon2-cffi asyncpg jinja2 tomli_w
PYTHONPATH=. PLI_ENABLE_M2=1 python -c "
from pli.main import app
from fastapi.testclient import TestClient
c = TestClient(app)
print(c.get('/accounts').status_code, c.get('/accounts').json())
"
# → 401 {'detail': "auth_failed:cannot import name 'current_local_plan' ..."}

PYTHONPATH=. PLI_ENABLE_M2=1 pytest tests/test_accounts.py \
    tests/test_messages.py tests/test_contacts.py \
    tests/test_conversations.py tests/test_auth_oauth.py \
    -p no:cacheprovider --no-cov -q
# → 50 failed in 8.58s
```

Comparaison mode (a), `PLI_ENABLE_M2` unset :

```bash
PYTHONPATH=. pytest <mêmes suites> -p no:cacheprovider --no-cov -q
# → 50 passed in 3.24s
```

## Cause racine

`pli/adapters/local.py:135-145` :

```python
async def local_principal_resolver(request) -> Principal:
    """En local, le principal est fixe. Le `plan` dépend de la clé licence
    enregistrée (cf. billing/licenses.py)."""
    from ..billing.licenses import current_local_plan   # ← n'existe pas

    return Principal(
        tenant_id=LOCAL_TENANT_ID,
        user_id=LOCAL_TENANT_ID,
        plan=current_local_plan(),
        email=None,
    )
```

`pli/billing/licenses.py` (65 lignes) n'exporte que :
- `issue_license_for_subscription(...)`
- `get_active_license(...)`

Aucune occurrence de `current_local_plan` dans le repo (vérifié par
`grep -r current_local_plan pli/`). Le commentaire de la ligne 137
("cf. billing/licenses.py") induit en erreur : la doc-string de
`licenses.py` précise au contraire que **les licences locales sont gérées
dans `pli.licensing.local`** (qui n'expose pas non plus
`current_local_plan` mais a `load_license()` + `LocalLicense.plan`).

## Hypothèses de fix (au choix de M2)

### Fix A — implémenter `current_local_plan` dans `pli.billing.licenses`

```python
# pli/billing/licenses.py
def current_local_plan() -> str:
    """Lit la licence locale (Ed25519) et renvoie son plan, sinon 'free'."""
    from ..licensing.local_key import load_license, verify_license
    blob = load_license()
    if blob is None:
        return "free"
    try:
        lic = verify_license(blob, public_key=...)  # cf. config
        return lic.plan
    except Exception:
        return "free"
```

Avantage : conforme au commentaire actuel + un seul module appelé.
Inconvénient : crée un couplage `billing` → `licensing` qui n'existait
pas (jusque-là `billing` ne dépendait que de Postgres + Stripe).

### Fix B — déplacer l'import vers `pli.licensing.local_key`

```python
# pli/adapters/local.py:137
from ..licensing.local_key import current_local_plan
```

Et exposer `current_local_plan()` dans `local_key.py`. Plus propre
sémantiquement (les licences locales vivent déjà là).

### Fix C — quick-win : default plan `"free"` pour le local

```python
# pli/adapters/local.py:135
async def local_principal_resolver(request) -> Principal:
    return Principal(
        tenant_id=LOCAL_TENANT_ID,
        user_id=LOCAL_TENANT_ID,
        plan="free",   # TODO M2 : brancher sur licence locale signée
        email=None,
    )
```

À retenir si M2 a déjà beaucoup d'autres priorités : débloque
immédiatement Sprint 1, laisse le détail licence pour Sprint 2/3.

## Critères d'acceptation

1. `PLI_ENABLE_M2=1 pytest tests/test_{accounts,messages,contacts,conversations,auth_oauth}.py`
   passe à 50/50.
2. `PLI_ENABLE_M2=1` toujours non requis pour Sprint 1 (le défaut OFF
   reste la version stable).
3. Pas de nouvelle dépendance Postgres ajoutée au boot mode local
   (régression silencieuse à éviter).
4. Tag `rebaseline-base-2026-04-22` (T1.7) re-postable derrière le fix.

## Dépendances M2 manquantes dans `pyproject.toml`

Bonus, pour faire booter l'app en mode (b) il a aussi fallu installer à
la main : `pyjwt`, `stripe`, `python-ulid`, `argon2-cffi`, `asyncpg`,
`jinja2`, `tomli_w`. À ajouter dans `backend/pyproject.toml` (ou dans un
extra `[project.optional-dependencies]` `m2 = [...]`) — sinon le tag
rebaseline ne sera utile à personne tant que `pip install -e .` ne suffit
pas.

## Journal

### 2026-04-22 — Ouverture (session M1)

Détection pendant T1.6 (non-régression Sprint 1 ↔ M2). 50/50 tests
verts en mode (a), 50/50 KO en mode (b). Ticket ouvert, daily mis à
jour, T1.7 (tag git) suspendu. WAITING_M2.

### 2026-04-23 — RÉSOLU (re-vérification M1)

Fix M2 mergé. Re-relu code (`pli/adapters/local.py:141-161`,
`pyproject.toml:45-60`) et ré-exécuté les deux modes :
- Mode (a) `PLI_ENABLE_M2` unset : 50/50 pytest verts, 17 paths
  openapi (0 M2), `pli_m2_routers_disabled`.
- Mode (b) `PLI_ENABLE_M2=1` : 50/50 pytest verts, 31 paths openapi
  (+14 M2), `pli_m2_routers_enabled`.

Critères #1-4 validés. Ticket clos. T1.7 (tag rebaseline) débloqué et
délégué à direction Mail (sandbox M1 pas en git repo).
