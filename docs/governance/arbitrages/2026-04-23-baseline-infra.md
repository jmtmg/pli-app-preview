# Arbitrages direction — 2026-04-23

**Contexte** : daily M3-2026-04-23 remonte 4 prérequis infra bloquants pour le scan sécurité officiel. Daily m5-2026-04-23 remonte 1 question stratégique sur la stabilité de la baseline pendant la fenêtre D→D+21. Arbitrages ci-dessous, valables immédiatement.

---

## A1 — Fenêtre de stabilité baseline (réponse à question M5)

**Question M5** : pendant D→D+21 (2026-04-22 → 2026-05-14), faut-il geler `backend/pli/` pour préserver l'intégrité du manifeste md5, ou autoriser les modifs avec bump d'empreinte ?

**Décision** : **freeze `backend/pli/` pendant la fenêtre D→D+21**, avec 3 escape hatches cadrés.

### Règle de freeze

- **Gelés** : tous les fichiers listés dans `docs/governance/tags/rebaseline-base-2026-04-22.md` §3-§6 (72 `backend/pli/*.py` + 24 `backend/tests/*.py` + `pyproject.toml` + 8 ADRs).
- **Autorisés sans bump** : tout fichier hors manifeste (`frontend/`, `docs/governance/`, `docs/adr/0009+`, `scripts/`, `e2e/`, nouveaux fichiers racine). Ces modifs ne cassent pas la reproductibilité des mesures M3/M4 car elles ne couvrent pas le périmètre scanné.
- **Autorisés avec bump** (3 cas exhaustifs) :
  1. **Hotfix P0** : incident prod/dev bloquant ouvert par ticket `P0-*.md`. Post-merge, direction pose un nouveau manifeste `rebaseline-base-<date>.md` et notifie M3+M4 qui relancent leurs mesures depuis zéro.
  2. **Coverage M2 T2.3 #39** : si le passage à 80% révèle du dead code à supprimer dans `backend/pli/`, c'est un ticket P0-like → même procédure bump.
  3. **Fix post-mesure M3** : si un scan sécurité remonte une vuln CRITICAL/HIGH devant être fixée avant 2026-05-14, M3 ouvre ticket, direction arbitre fix → bump → re-scan.

### Propriétaire

Direction (session Mail) tranche chaque demande de bump en <24h via ticket dédié. Par défaut = refus (le freeze est l'option sûre).

### Rappel aux sessions

- **M1** : Sprint 1 CLOSED, aucun travail code prévu dans la fenêtre. Pas d'impact.
- **M2** : T2.3 coverage 80% (item 39) touche **uniquement `backend/tests/`** en ajout (nouveaux `test_*.py`), **pas `backend/pli/`**. Si refactor nécessaire pour testabilité → ticket bump.
- **M3** : consommateur baseline (mesure), pas d'écriture.
- **M4** : travail majoritairement `frontend/` + docs → aucun impact. Perf/Lighthouse peut scanner le binaire actuel sans bump.
- **M5** : gouvernance seule, aucun impact.

Effet immédiat : **aucune PR ne doit modifier `backend/pli/*.py` ni `backend/tests/*.py` ni `backend/pyproject.toml` jusqu'au 2026-05-14 sans ticket P0 explicite**.

---

## A2 — Outillage lock Python (Q1 M3)

**Question M3** : `pip-compile` (pip-tools) vs `uv pip compile` pour générer `backend/requirements.lock` ?

**Décision** : **`uv pip compile`**.

**Justification** :
- `uv` est installé dans la sandbox direction (`/usr/local/bin/uv`) et dans les sandboxes M2/M3.
- Reproductibilité stricte (même algo de résolution, même Python target).
- 5-10× plus rapide que `pip-compile` sur gros dépendances.
- Format output identique à pip-tools (lisible, commentable), grep-able.
- Pas de binding runtime à `pip-tools` (qui est un outil séparé à maintenir).

### Action déjà exécutée (direction, 2026-04-23 18:27)

`backend/requirements.lock` **posé** par direction :

```
cd backend
uv pip compile pyproject.toml --extra m2 -o requirements.lock --python 3.11
```

Résultat :
- 295 lignes, 6764 bytes
- md5 : `548ce01ef60b32ec725174f4ab4ebaee`
- Couvre `pli-backend` (base) + extra `m2` (pyjwt, argon2-cffi, stripe, asyncpg, jinja2, python-ulid, tomli_w)
- Python target : 3.11 (cohérent avec Dockerfile)

### Status baseline

Le fichier `backend/requirements.lock` n'est **pas** ajouté au manifeste `rebaseline-base-2026-04-22.md` : il est **dérivé** de `pyproject.toml` (déjà dans le manifeste). Si `pyproject.toml` change (bump empreinte), M2 doit régénérer `requirements.lock` via la même commande.

Propriétaire maintenance : **M2** (possède `pyproject.toml`).

### Déblocage M3

`pip-audit --requirement backend/requirements.lock` est désormais exécutable. Reste à M3 à lancer depuis env Python 3.11+ (hors sandbox 3.10 actuelle).

---

## A3 — Outillage lock Node (Q2 M3)

**Question M3** : `npm ci` + `package-lock.json` vs `pnpm`/`yarn` ?

**Décision** : **`npm` + `package-lock.json`**.

**Justification** :
- Alignement avec `npm audit --production` déjà codé dans `scripts/rebaseline/run-vuln-scans.sh`.
- Zéro migration nécessaire.
- npm 10.x fourni par Node 22 LTS, aligné avec target CI.

### Action à exécuter

**Propriétaire** : **M4** (frontend owner). Commande :

```bash
cd frontend
npm install --package-lock-only --ignore-scripts
git add package-lock.json
# ou équivalent hors-git tant que repo non initialisé
```

**Note** : direction a tenté depuis sa sandbox mais timeout à 40s (arbre de deps volumineux). M4 doit le faire depuis un env Node local avec réseau stable.

**Délai souhaité** : **2026-04-25 fin de journée** (débloque M3 `npm audit`).

**Status baseline** : même logique que `requirements.lock` — fichier dérivé de `package.json`, pas ajouté au manifeste.

---

## A4 — Image Docker `pli/backend:prod` (Q3 + Q4 M3)

**Question M3** : Dockerfile.prod séparé vs multi-stage `--target prod` ? Et qui builde ?

**Décision** : **multi-stage avec `--target runtime`** (le Dockerfile existant est déjà multi-stage : `builder` + `runtime`). Pas de Dockerfile.prod séparé nécessaire.

**Vérifié par direction** (cf. `backend/Dockerfile` lignes 1 + 9) :
- Stage `builder` : installe pli-backend depuis pyproject.toml
- Stage `runtime` : python:3.11-slim, libpq5, curl, user `pli`, healthcheck
- **Pas d'outils debug** dans le stage runtime → scannable en prod sans bruit

**Commande** :
```bash
cd backend
docker build --target runtime -t pli/backend:prod .
```

### Propriétaire build

**Décision** : **M4** (owner perf/build, cohérent avec son benchmark Lighthouse sur l'image intégrée).

**Justification alternative rejetée** : direction peut buildé en théorie, mais sandbox Mail n'a **pas Docker**. M1/M2/M3 non plus. M4 est la session la mieux placée (infra frontend + perf bench déjà sur son backlog).

**Délai souhaité** : **2026-04-27 fin de journée** (après Q3/Q2 débloqués).

### Process restauration seed

La directive §2 de `REBASELINE-CHECKLIST.md` ("direction restaure la seed") reste cohérente mais séquencée **après** que M4 ait buildé et tagué l'image. Direction fournit la seed via fichier JSON/SQL dans `backend/tests/fixtures/seed-rebaseline-2026-04-22.sql` ou équivalent — à préciser dans un arbitrage séparé si M4 a besoin.

---

## A5 — R-M3-04 OpenAPI 17→31 paths (clarification M3)

**Question implicite M3** : la vérification OpenAPI nécessite Python 3.11+, incompatible sandbox 3.10. Proposition M3 : `check-baseline-md5.sh` fait md5 + pytest, et OpenAPI reste à la charge de l'env officiel.

**Décision** : **accepté tel quel**.

Rationale : l'env officiel de publication des mesures M3 (CI GitHub Actions ou sandbox locale M3 avec Python 3.11 installé) peut vérifier l'OpenAPI. La sandbox Linux Python 3.10 est un env secondaire de vérif md5/pytest uniquement.

**Action** : M3 documente cette limite dans `docs/governance/metrics/REBASELINE-CHECKLIST.md` §7 (étapes reproductibles en env officiel 3.11+ vs env dégradé 3.10). Pas de blocage.

---

## Synthèse actions par session

| Session | Action | Deadline |
|---------|--------|----------|
| M2 | Acter que `backend/requirements.lock` est posé par direction. Nouvelle tâche : maintenir le lockfile à chaque bump pyproject.toml. | 2026-04-24 daily |
| M3 | Acter arbitrages A1-A5. Lancer `pip-audit --requirement backend/requirements.lock` dès env Python 3.11 disponible. Attendre M4 pour `package-lock.json` puis `npm audit`. Attendre M4 pour image Docker puis trivy. | bloqué jusqu'à 2026-04-27 |
| M4 | Générer `frontend/package-lock.json` via `npm install --package-lock-only`. Builder `pli/backend:prod` via `docker build --target runtime`. Poster daily 2026-04-23 (manquant). | 2026-04-25 pour lockfile, 2026-04-27 pour image |
| M5 | Acter règle freeze A1. Mettre à jour Sprint 11 §7/§8 avec les 3 escape hatches. Monitoring quotidien inchangé (seuils J+10 et D+21). | 2026-04-24 daily |

---

## Changelog baseline

Aucun bump du manifeste `rebaseline-base-2026-04-22`. Empreinte globale `6a8d82bcbd292422f3ef87d0d6a30dce` inchangée.

Nouveaux fichiers hors-manifeste (ajoutés 2026-04-23) :
- `backend/requirements.lock` (dérivé de pyproject.toml, par direction)

À venir hors-manifeste :
- `frontend/package-lock.json` (par M4, deadline 2026-04-25)

Rédigé par direction (session Mail), 2026-04-23 fin de journée.
