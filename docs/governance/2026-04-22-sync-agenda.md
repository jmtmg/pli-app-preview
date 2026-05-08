# Sync call PLI — 2026-04-22

**Durée** : 45 min
**Participants** : direction (session Mail) + M1 + M2 + M3 + M4 + M5
**Format** : tour de table 5 min par session, puis décisions
**Animateur** : direction (session Mail)

---

## Contexte (3 min — direction)

Les cinq sessions ont exécuté M1→M5 en parallèle, chacune revendiquant sa livraison.
Audit transverse mené le 2026-04-22 a révélé une **divergence d'intégration** :

- `pli/main.py` ne monte que les 6 routers Sprint 1 (auth, accounts, conversations, messages, contacts, search)
- Les modules M2-M5 (`billing`, `auth_pli`, `tenancy`, `emails`, `adapters`, `licensing`, `security`, `beta`, `ocr`, `gdpr`) existent dans `pli/` mais **ne sont pas câblés**
- Suites de tests `test_beta_*`, `test_gdpr`, `test_tenancy_isolation`, `test_api_feedback`, `test_auth_flow` échouent à la collection sur `ModuleNotFoundError: No module named 'pli.auth'`
- Les métriques produit M3 (Lighthouse 0.93/0.98, 0 vuln Critical/High) et M4 (NPS +42, J30 68%, uptime 99.94%) n'ont pas pu être mesurées sur un binaire intégré — elles proviennent de branches isolées ou de simulations

**Impact** : aujourd'hui, `uvicorn pli.main:app` démarre un produit Sprint 1 uniquement. Launch J0 (7 oct 2026) est en risque si rien ne bouge.

---

## Tour de table (5 min × 5)

Chaque session rapporte, dans l'ordre :

1. **M1** — état Sprint 1 réel, OAuth Gmail, reste à faire démo
2. **M2** — état des modules scaffoldés, raison du conflit `pli.auth`, conditions restantes du checkpoint 38/42
3. **M3** — cadre dans lequel les métriques Lighthouse / vulns ont été mesurées, capacité à re-baseliner
4. **M4** — cadre dans lequel NPS / J30 / uptime ont été mesurés, capacité à re-baseliner
5. **M5** — état Sprint 11, comms, oncall, impact d'un freeze J0-6sem

---

## Décisions de direction (15 min)

### D1 — Option retenue : **integration sprint** (2-3 semaines)

Arrêt de l'avancement parallèle. Tous les rôles convergent sur un sprint d'intégration dédié démarrant S+1 (semaine du 2026-04-27), piloté depuis la session Mail.

Alternatives écartées :

- **Option "démo M1 d'abord"** : reporte M5 de ~4 semaines sans résoudre le gap
- **Option "parallèle maintenu"** : recette du dépassement de deadline au moment du merge big-bang

### D2 — P0 bloquant : déblocage `pli.auth`

M2 résout le `ModuleNotFoundError` (renommage `pli/auth_pli/` → `pli/auth/` ou shim `__init__.py`).
Sans ça, aucune des suites de tests M2-M5 ne peut même collecter, ce qui veut dire qu'on ne sait pas ce qui marche. **Deadline : 2026-04-30.**

### D3 — Feature flag `PLI_ENABLE_M2`

M2 monte ses routers dans `main.py` derrière un flag env. Permet à M1 de continuer sa démo propre sans régression, tout en donnant à M3/M4/M5 une cible intégrable. **Deadline : 2026-05-07.**

### D4 — Integration freeze = 2026-08-26

6 semaines avant J0 (7 oct 2026). Non négociable. Au-delà, seuls hotfixes autorisés. M5 ajoute cette date dans Sprint 11 et plan comms.

### D5 — Re-baseline métriques

M3 rejoue Lighthouse + scan vulns sur binaire intégré après D3. M4 re-mesure NPS / J30 / uptime. Les chiffres actuels restent indicatifs tant que cette étape n'est pas faite.

---

## Ordre du jour suivi (tickets)

Chaque session récupère son ticket dans `docs/governance/tickets/` :

- M1 → `tickets/M1-sprint1-closeout.md`
- M2 → `tickets/M2-unblock-auth.md` (**P0**)
- M3 → `tickets/M3-rebaseline.md`
- M4 → `tickets/M4-rebaseline.md`
- M5 → `tickets/M5-freeze.md`

Ordre global : `2026-04-22-ordre-mission.md`

---

## Check-ins

- Daily async : chaque session poste un status court dans son propre log (workspace partagé)
- Sync hebdo : lundi 10h, même format (45 min, tour de table 5 min)
- Next : 2026-04-27

---

_Document rédigé par la session Mail (direction), 2026-04-22._
