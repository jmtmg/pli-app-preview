# Rebaseline M3 — Rapport de synthèse

**Ticket** : `docs/governance/tickets/M3-rebaseline.md`
**Ordre de mission** : `docs/governance/2026-04-22-ordre-mission.md`
**Ouvert** : 2026-04-22 (session M3)
**Deadline** : 2026-05-14
**Statut** : **TRAME — en attente déblocage M2 T2.2**

---

## 1. Contexte et objet

L'audit transverse du 2026-04-22 a invalidé les chiffres produit revendiqués dans `M3-CLOSEOUT.md` (Lighthouse 0.93 perf / 0.98 best practices, 0 vulnérabilité Critical / High). La cause : `backend/pli/main.py` ne monte que les 6 routers Sprint 1, les modules M2-M5 n'étant pas câblés. Les métriques ont donc été prises sur un périmètre qui n'est pas le binaire cible.

Ce rapport porte les chiffres officiels M3 **après** re-baseline sur le binaire intégré (`PLI_ENABLE_M2=1`, tag git `rebaseline-YYYY-MM-DD` posé par direction). La décision Go M4 est suspendue tant que ce document n'est pas rempli et signé.

## 2. Prérequis d'ouverture de la mesure

Aucune mesure ne doit démarrer tant que les cinq conditions suivantes ne sont pas toutes vertes. Les garde-fous sont câblés dans `e2e/perf/run-lighthouse-integrated.sh` et `scripts/rebaseline/run-vuln-scans.sh` pour bloquer toute exécution hors cadre.

- M2 T2.1 fermé : `pytest --collect-only backend/tests/` retourne 0 erreur.
- M2 T2.2 fermé : `PLI_ENABLE_M2=1 uvicorn pli.main:app` démarre ; `/api/billing/ping` répond 200.
- Tag git `rebaseline-YYYY-MM-DD` posé par direction ; M3 et M4 ont checkout ce tag.
- Seed de base identique entre M3 et M4 (fixture partagée `docs/governance/metrics/seed/<tag>.sql.gz`).
- Image Docker `pli/backend:prod` construite depuis le tag (pas `pli/backend:dev`).

## 3. Tableau comparatif avant / après

Les colonnes « Avant (revendiqué) » reprennent les chiffres du CLOSEOUT suspendu. Les colonnes « Après (intégré) » restent vides jusqu'à mesure officielle. L'écart est calculé automatiquement dans le commit qui clôturera ce rapport.

### 3.1 Lighthouse par parcours

| Parcours | Métrique | Avant (revendiqué) | Après (intégré) | Écart | Statut gate |
|---|---|---|---|---|---|
| Login Gmail | Performance | 0.93 | _(à mesurer)_ | _(à calculer)_ | — |
| Login Gmail | Best practices | 0.98 | _(à mesurer)_ | _(à calculer)_ | — |
| Login Gmail | Accessibility | 0.98 | _(à mesurer)_ | _(à calculer)_ | — |
| Liste contacts | Performance | 0.93 | _(à mesurer)_ | _(à calculer)_ | — |
| Liste contacts | Best practices | 0.98 | _(à mesurer)_ | _(à calculer)_ | — |
| Conversation | Performance | 0.93 | _(à mesurer)_ | _(à calculer)_ | — |
| Conversation | Best practices | 0.98 | _(à mesurer)_ | _(à calculer)_ | — |
| Fiche contact | Performance | 0.93 | _(à mesurer)_ | _(à calculer)_ | — |
| Fiche contact | Best practices | 0.98 | _(à mesurer)_ | _(à calculer)_ | — |
| Billing portal | Performance | _(non mesuré — débloqué M2)_ | _(à mesurer)_ | n/a (nouvelle baseline) | — |
| Billing portal | Best practices | _(non mesuré — débloqué M2)_ | _(à mesurer)_ | n/a (nouvelle baseline) | — |

### 3.2 Core Web Vitals (médianes 3 runs)

| Parcours | LCP (ms) | CLS | INP (ms) | TBT (ms) |
|---|---|---|---|---|
| Login Gmail | _(à mesurer)_ | _(à mesurer)_ | _(à mesurer)_ | _(à mesurer)_ |
| Liste contacts | _(à mesurer)_ | _(à mesurer)_ | _(à mesurer)_ | _(à mesurer)_ |
| Conversation | _(à mesurer)_ | _(à mesurer)_ | _(à mesurer)_ | _(à mesurer)_ |
| Fiche contact | _(à mesurer)_ | _(à mesurer)_ | _(à mesurer)_ | _(à mesurer)_ |
| Billing portal | _(à mesurer)_ | _(à mesurer)_ | _(à mesurer)_ | _(à mesurer)_ |

Seuils absolus (échec si dépassé) : LCP ≤ 2500 ms, CLS ≤ 0.1, INP ≤ 200 ms, TBT ≤ 300 ms.

### 3.3 Scan vulnérabilités

| Outil | Périmètre | Avant (revendiqué) | Après (intégré) | Diff |
|---|---|---|---|---|
| pip-audit | `backend/requirements.lock` incluant deps M2 (stripe, cryptography bumpé, sqlalchemy) | 0 Critical / 0 High | _(à mesurer)_ | _(à documenter)_ |
| npm audit --production | `frontend/package-lock.json` | 0 Critical / 0 High | _(à mesurer)_ | _(à documenter)_ |
| trivy image `pli/backend:prod` | OS packages + deps Python embarquées | 0 Critical / 0 High | _(à mesurer)_ | _(à documenter)_ |

### 3.4 OCR E2E

| Cas de test | Attendu | Mesuré | Statut |
|---|---|---|---|
| PDF scanné 3 pages → extraction fra+eng | text > 50 chars, langue "fr", source "pdf_raster" | _(à mesurer)_ | — |
| Indexation FTS5 | hit dans `/api/search?q=facture&kind=attachments` | _(à mesurer)_ | — |
| Perf 5 pages PDF | médiane < 3 s sur worker 2 vCPU | _(à mesurer)_ | — |

## 4. Gate de clôture (arbitrages direction 2026-04-22)

**Performance et best practices** — seuil gradué :

- Régression ≤ 10 pts perf ET ≤ 5 pts best practices : clôture M3 valide, ticket perf tuning ouvert en file, Launch non bloqué.
- Régression > 10 pts perf OU > 5 pts best practices : clôture M3 bloquée, perf tuning obligatoire avant feu vert M4.

**Sécurité** — non négociable : 0 Critical / 0 High requis. Tout finding de ce niveau bloque la clôture, peu importe le reste.

**OCR E2E** — non négociable : chemin intégré doit passer (extraction + FTS5 + perf < 3 s). Sans ça, la bêta ne peut pas exposer l'OCR.

## 5. Décision finale

_(à remplir après mesure)_

- **Statut** : Go / No-Go / Go-conditionnel-avec-ticket
- **Signataire direction (session Mail)** : _(date + agent)_
- **Co-signature TL M3** : _(date + agent)_
- **Ticket perf tuning ouvert** (si applicable) : _(lien)_
- **Fenêtre Launch J0 impactée** : oui / non (avec justification)

## 6. Annexes et traçabilité

- Rapports Lighthouse HTML/JSON : `docs/governance/metrics/lighthouse-integrated/<timestamp>-*`
- Scans vulns JSON : `docs/governance/metrics/vuln-scans/<timestamp>/`
- SUMMARY vulns : `docs/governance/metrics/vuln-scans/<timestamp>/SUMMARY.md`
- E2E OCR run : `e2e/reports/integrated/<tag>/ocr.json`
- Seed DB : `docs/governance/metrics/seed/<tag>.sql.gz`
- Tag git de mesure : `rebaseline-YYYY-MM-DD`
- CLOSEOUT suspendu : `M3-CLOSEOUT.md` (en-tête de suspension)
