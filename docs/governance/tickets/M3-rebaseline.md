# Ticket M3 — Re-baseline Lighthouse + scan vulns

**Priorité** : P2 (débloqué par T2.2 côté M2)
**Propriétaire** : session PLI M3
**Émis par** : direction (session Mail), 2026-04-22
**Deadline** : 2026-05-14

---

## Contexte

Tu as fermé la phase Bêta avec GO M4 et revendiqué :
- Lighthouse 0.93 (perf) / 0.98 (best practices)
- 0 vulnérabilité Critical/High (scans `pip-audit`, `npm audit`, `trivy`)

Audit transverse 2026-04-22 a montré que ces chiffres ont été mesurés alors que `pli/main.py` ne wire que les 6 routers Sprint 1 — donc pas le binaire cible complet. Soit les mesures ont été faites sur une branche isolée qui n'a pas été mergée, soit sur un binaire simplifié. Dans les deux cas, il faut re-baseliner.

**Ton ticket est débloqué** quand M2 a fini T2.2 (wire-up routers M2 derrière flag `PLI_ENABLE_M2`).

## Travail à faire

### T3.1 — Rejouer Lighthouse sur binaire intégré

- Avec `PLI_ENABLE_M2=1` + build FE prod (`npm run build && npm run preview`)
- Lighthouse CI sur parcours clefs :
  - Login Gmail
  - Liste contacts
  - Conversation
  - Fiche contact
  - Billing portal (nouveau, débloqué par M2)
- Target conservatrice : **≥ 0.90 perf, ≥ 0.95 best practices**
- Si régression > 5 pts vs chiffres revendiqués : ouvrir ticket suivant pour perf tuning avant de clôturer
- Sauvegarder rapport Lighthouse dans `docs/governance/metrics/2026-XX-lighthouse-integrated.html`

### T3.2 — Rejouer scan vulns

- `pip-audit` sur lockfile backend intégré (incluant deps M2 : `stripe`, `cryptography` bumpé, `sqlalchemy`, etc.)
- `npm audit --production` sur lockfile frontend
- `trivy fs` sur image Docker `prod`
- Target : **0 Critical / 0 High**. Si nouveau High apparaît, proposer patch dans le même ticket.

### T3.3 — OCR Tesseract sur chemin intégré

- Valider que le pipeline OCR (`pli/ocr/`) est bien chargé avec M2 wired
- Un test E2E : upload PDF scanné → extraction fra+eng → index FTS5

### T3.4 — Rapport de synthèse

Un fichier court `docs/governance/metrics/2026-04-22-rebaseline-m3.md` avec :
- Chiffres avant (revendiqués) / après (mesurés)
- Écarts éventuels et leur interprétation
- Recommandation GO / NO-GO maintien M3

## Règles

- Pas de démarrage avant T2.2 (M2 wire-up) — coordonner avec M2 avant de lancer
- Conserver les rapports Lighthouse HTML + JSON pour audit
- Si les chiffres s'effondrent : NE PAS masquer, remonter à direction

## Done criteria

- Rapports Lighthouse + scans vulns reproduits sur binaire intégré
- Rapport de synthèse publié
- Pipeline OCR validé E2E
- Recommandation GO/NO-GO documentée

## Journal

### 2026-04-22 — Ack ticket + prep work (session M3)

**Statut global** : bloqué par M2 T2.2. Aucune mesure officielle lancée.

**Constat du binaire intégré**. Relecture manuelle de `backend/pli/main.py` : seuls les 6 routers Sprint 1 (auth / accounts / conversations / messages / contacts / search) sont `include_router`. Les modules M2 (`billing`, `emails`, `licensing`, `tenancy`) et M3 (`gdpr`, `ocr`) sont présents dans l'arborescence mais pas montés. Diagnostic de l'audit 2026-04-22 reproduit, bon.

**Impact sur le CLOSEOUT signé la veille**. Les chiffres que j'ai revendiqués dans `M3-CLOSEOUT.md` (Lighthouse 0.93 perf / 0.98 best practices, 0 Critical / 0 High) ont été produits sur un périmètre qui n'est pas celui du binaire cible. Je considère que la décision GO pour M4 est **suspendue** jusqu'à re-baseline (T3.1–T3.4). Document laissé en l'état pour traçabilité ; note de suspension demandée à direction.

**Prep work livré (pas de mesure officielle)** :

- `e2e/perf/lighthouserc.integrated.cjs` — config Lighthouse CI dédiée au binaire intégré, 5 parcours incluant Billing portal (nouveau M2). Assertions : perf ≥ 0.90, best-practices ≥ 0.95, a11y ≥ 0.95 ; LCP ≤ 2500, CLS ≤ 0.1, INP ≤ 200, TBT ≤ 300.
- `e2e/perf/run-lighthouse-integrated.sh` — runner avec deux garde-fous : refuse `PLI_ENABLE_M2 != 1` et refuse si `/api/billing/ping` renvoie non-2xx. Objectif : impossible de re-mesurer par inadvertance sur le binaire Sprint-1-only.
- `scripts/rebaseline/run-vuln-scans.sh` + `scripts/rebaseline/summarize-scans.py` — pip-audit sur `backend/requirements.lock`, npm audit --production sur `frontend/`, trivy image `pli/backend:prod` sur `--severity CRITICAL,HIGH --ignore-unfixed`. Agrégateur Python avec exit 1 si Critical+High > 0 et synthèse Markdown direction.
- `e2e/ocr/integrated.spec.ts` — Playwright : upload PDF scanné 3 pages → enqueue OCR → poll status 10 s → vérif text + FTS5 hit. Skip automatique si `PLI_ENABLE_M2` absent.

**Tâches tracker** : #15 (rebaseline global, bloqué par #16+#17+#18), #16 Lighthouse config ✅, #17 scan vulns ✅, #18 E2E OCR ✅, #19 daily log ✅.

**Daily log** : `docs/governance/daily/M3-2026-04-22.md`.

**Dépendances suivies** :
- M2 T2.1 `pli.auth` (deadline 2026-04-30) — sans ça, pytest ne collecte pas.
- M2 T2.2 wire-up `PLI_ENABLE_M2` (deadline 2026-05-07) — sans ça, pas de re-baseline possible.

**Questions direction en attente** :
1. Suspendre formellement la décision GO M4 jusqu'à re-baseline terminée ?
2. Coordonner le jour de mesure avec M4 (même build, même seed) ou chacun de son côté ?
3. Si régression > 5 pts apparaît : clôture M3 avec ticket perf tuning en file, ou clôture M3 bloquée tant que perf tuning non fait ?

**À faire demain (2026-04-23)** : trame du rapport de synthèse T3.4, relecture `security/threat-model-checklist.md` pour identifier les contrôles qui présupposaient un binaire intégré, committer les fixtures OCR manquantes (`backend/tests/fixtures/ocr/invoice_scanned_3pages.pdf`).

### 2026-04-22 — Arbitrages direction sur les 3 questions

**Q1 — Suspension GO M4** : **OUI formel**. GO M4 conditionné à re-baseline M3+M4 sur binaire intégré. Pas de remise en cause du travail M4, seulement de son cadre de mesure. M5 sera prévenu via son daily.

**Q2 — Coordination M3/M4** : **même build figé**. Dès que M2 livre T2.2 validé, M3 et M4 se coordonnent pour poser un tag git commun (ex. `rebaseline-2026-05-10`) et mesurent toutes deux depuis ce tag. Prévient l'écart "M3 à X, M4 à Y, non comparables".

**Q3 — Régression Lighthouse** : seuil gradué.
- ≤ 10 pts perf ET ≤ 5 pts best practices : clôture M3 avec ticket perf tuning en file, Launch non bloqué.
- > 10 pts perf OU > 5 pts best practices : clôture M3 bloquée, perf tuning obligatoire avant feu vert.
- 0 Critical / 0 High reste non négociable (aucun gradient sécu).

Actions immédiates :
- Ajout en-tête de suspension dans `M3-CLOSEOUT.md` (pointer vers ticket re-baseline).
- Mise à jour du runner Lighthouse pour exiger un tag git `rebaseline-*` au checkout avant mesure (garde-fou coordination M3/M4).
- Rédaction trame `docs/governance/metrics/2026-04-22-rebaseline-m3.md` avec les 3 seuils Q3 câblés dans le gate final.
- Checklist de coordination M3/M4 posée dans `docs/governance/metrics/REBASELINE-CHECKLIST.md`.

### 2026-04-23 — §7 baseline validée + adaptation runners + blocage infra identifié

**Baseline de référence** : `rebaseline-base-2026-04-22` (manifeste md5 posé par direction en substitut de tag git, workspace OneDrive non git-init). Empreinte globale attendue `6a8d82bcbd292422f3ef87d0d6a30dce`.

**§7 joué en sandbox** :
- 105/105 hashes identiques (72 pli + 24 tests + 1 pyproject + 8 ADR).
- Empreinte globale locale = `6a8d82bcbd292422f3ef87d0d6a30dce` ✅.
- Pytest 50/50 mode (a) `PLI_ENABLE_M2` unset ✅.
- Pytest 50/50 mode (b) `PLI_ENABLE_M2=1` ✅.
- OpenAPI 17→31 paths non rejoué en sandbox (Python 3.10 vs requires-python ≥3.11) — repose sur les attestations M1 T1.6.

**Adaptation runners (substitut git → md5)** : le tag git est remplacé par un appel à `scripts/rebaseline/check-baseline-md5.sh` qui reconstitue les manifestes localement, diff contre le fichier `rebaseline-base-2026-04-22.md`, exit 1 si drift. Smoke tests : nominal OK, drift simulé → abort clair avec la procédure P0-rebaseline-drift rappelée, override `PLI_REBASELINE_ALLOW_UNTAGGED=1` préservé pour dry-run.

Fichiers touchés :
- `scripts/rebaseline/check-baseline-md5.sh` (nouveau)
- `scripts/rebaseline/run-vuln-scans.sh` (garde-fou remplacé)
- `e2e/perf/run-lighthouse-integrated.sh` (garde-fou remplacé)
- `docs/governance/metrics/REBASELINE-CHECKLIST.md` (étapes 2/3/4/règles d'or mises à jour)

**Tentative re-baseline sécurité (greenlit direction)** — bloquée par 3 prérequis infra manquants :
1. `backend/requirements.lock` absent (pyproject.toml seul) → pip-audit ne peut pas cibler un lockfile déterministe.
2. `frontend/package-lock.json` absent → npm audit n'a pas de lockfile à scanner.
3. Image `pli/backend:prod` non buildée + `trivy`/`docker` absents de la sandbox → trivy image non exécutable.

Décision : **ne pas publier de chiffres provisoires.** Un scan partiel casserait la comparabilité M3/M4. Escalade direction via daily 2026-04-23 avec 4 questions (outil lock Python, outil lock Node, Dockerfile.prod multi-stage vs target, qui builde l'image). Tant qu'arbitrage non reçu : attente + travaux parallèles (trame rapport synthèse 3.3, relecture threat-model 27 contrôles, fixtures OCR).

**Runway** : 21 jours calendaires restants avant deadline 2026-05-14. Chaque jour d'attente infra mange ce runway. R-M3-01 relevé au niveau "à surveiller".

**Daily log** : `docs/governance/daily/M3-2026-04-23.md`.

---

_Réf. audit 2026-04-22, ordre de mission `2026-04-22-ordre-mission.md` §2 D5 et §3 P2._
_Bloqué par : prérequis infra scan (requirements.lock, package-lock.json, image Docker prod)._
