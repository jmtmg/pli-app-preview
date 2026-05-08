# Rapport de synthèse — Re-baseline métriques M4

**Ticket** : `docs/governance/tickets/M4-rebaseline.md`
**Propriétaire** : session PLI M4
**Statut** : **SKELETON — cadre Option B validé direction, baseline ancrée, A3 livré, A4 en escalation, en attente T2.2 (2026-05-07)**
**Deadline ticket** : 2026-05-14
**Baseline de mesure** : `rebaseline-base-2026-04-22` — empreinte globale `6a8d82bcbd292422f3ef87d0d6a30dce` (cf. `docs/governance/tags/rebaseline-base-2026-04-22.md`)
**Dernière mise à jour** : 2026-04-24

---

## 1. Résumé exécutif

> À compléter après re-baseline effective. Version préliminaire ci-dessous, remplacée dès T2.2 mergé.

**Chiffres revendiqués à la clôture M4 initiale (environnement isolé, NON reproduits sur binaire intégré)** :

| Métrique | Valeur revendiquée | Environnement | Re-mesurable avant 2026-05-14 ? |
|----------|-------------------|---------------|--------------------------------|
| NPS | +42 | Branche feature isolée | **Partiel** — dépend livraison M2 T2.2 + N≥30 testeurs |
| Rétention J30 | 68% | Simulation cohort synthétique | **NON** — fenêtre 30j incompatible avec deadline |
| Uptime | 99.94% | Environnement staging isolé | **NON réutilisable** — baseline à relancer |

**Recommandation préliminaire** : **NO-GO revendication maintenue**. Re-qualifier les chiffres dès binaire intégré disponible, replanifier NPS officiel et rétention J30 en Sprint 12 post-Launch.

**Cadre validé direction (2026-04-22, Option B)** :
- NPS : re-mesure sur binaire intégré, panel N≥30, fenêtre 3j. Si taux de réponse insuffisant → bascule replan Sprint 12, documenté.
- Rétention J30 : replan Sprint 12 ferme. Pas de métrique fabriquée. Retirer "68%" de tous les supports externes.
- Uptime : baseline neuve à partir de la date de mise en prod du binaire intégré (date précise à documenter dans runbook M5, coordination M5).
- Tour + KB + marketing kit : validation fonctionnelle suffit, pas de re-contenu.
- **Coordination M3/M4** : même build figé. Dès T2.2 validé, tag git commun (ex. `rebaseline-2026-05-10`), M3 et M4 mesurent depuis ce tag (réponse R2 direction à M3, reproduite ici).
- Rapport final 2026-05-14 avec GO/NO-GO explicite. **NO-GO possible** — honnêteté avant les chiffres.

## 2. Contexte

L'audit transverse du 2026-04-22 a établi que les routers M2-M5 ne sont pas montés dans `pli/main.py` (seuls les 6 routers Sprint 1 tournent). Les métriques M4 revendiquées (NPS +42, rétention 68%, uptime 99.94%) ont été mesurées sur des environnements isolés non représentatifs du produit intégré :

- NPS : collecté sur une branche de dev avec un panel restreint (beta interne ~12 répondants, agrégé avec 18 réponses synthétiques — source non canonique).
- Rétention J30 : simulation sur data générée, pas de cohorte réelle.
- Uptime : staging interne isolé, sans les routes M2+ (billing, emails, licensing) qui élargiront la surface d'erreur.

Ces chiffres **ne peuvent pas être conservés tels quels** pour justifier un GO M5 sur le binaire intégré.

## 3. T4.1 — NPS sur binaire intégré

**Statut** : bloqué T2.2.

### Protocole prévu (à exécuter dès `PLI_ENABLE_M2=1` stable)

1. Démarrer `PLI_ENABLE_M2=1 uvicorn pli.main:app` et valider :
   - Route `POST /feedback` exposée (cf. module `pli/api/feedback.py` — à confirmer M2 wire).
   - `NPSWidget.tsx` charge prefs via `/me/prefs` sans erreur réseau.
2. Recruter panel : 10 beta testeurs internes (équipe + proches) + 20 via liste bêta existante (si widget déclenchable manuellement).
3. Seuil minimum d'acceptation : **N ≥ 30**. Sous ce seuil : publier résultat avec intervalle de confiance large + recommandation re-mesure Sprint 12.
4. Fenêtre de collecte : 3 jours ouvrés (2026-05-08 → 2026-05-12).
5. Segment NPS par tier (free / pro / team si déjà différenciables sur binaire intégré — sinon : global).

### Fallback si N < 30 ou M2 en retard

- Documenter honnêtement : "NPS revendiqué sur environnement isolé, non reproduit sur binaire intégré."
- Replanifier mesure officielle **Sprint 12 post-Launch** (2026-10-14 → 2026-10-28), sample ≥ 100 sur utilisateurs réels.

**Valeur retenue pour GO M5** : non disponible tant que T4.1 pas clos.

## 4. T4.2 — Rétention J30

**Statut** : **impossible en temps imparti** (confirmé dès émission ticket).

### Justification

Une rétention J30 requiert :

- Une cohorte d'inscription à T0.
- 30 jours de suivi d'activité.

Avec T2.2 attendu au 2026-05-07 et deadline ticket 2026-05-14 (7 jours), la fenêtre est physiquement insuffisante.

### Recommandation

- **Replan Sprint 12 post-Launch** (cohorte Launch J0 = 2026-10-07 → mesure J30 = 2026-11-06).
- D'ici là, surveiller DAU/MAU et retention J7 comme indicateurs intermédiaires sur beta testeurs (facultatif).
- **Ne pas conserver le chiffre 68%** dans la documentation produit : le remplacer par "mesure à venir Sprint 12" partout (pitch deck, press, landing).

## 5. T4.3 — Uptime

**Statut** : bloqué T2.2 ; baseline à relancer.

### Action

1. Une fois `PLI_ENABLE_M2=1` mergé, relancer compteur uptime à T0 = date mise en prod binaire intégré.
2. Vérifier remontée Prometheus/Grafana (ou équivalent — à confirmer avec SRE) fonctionne avec les routers M2 wired (billing, emails, licensing élargissent la surface `/metrics`).
3. Publier baseline uptime dans le runbook M5 (`docs/runbooks/m5-oncall.md` — à créer si absent, propriétaire M5).

### Risque

L'ajout des routers M2 élargit la surface d'erreur. Attendre **au moins 72h** d'observation avant de publier un chiffre — toute revendication anticipée serait non significative.

## 6. T4.4 — Validation tour + KB + marketing kit

**Statut partiel** : revue structurelle OK (front M4 inchangé), validation comportementale bloquée.

### Tour onboarding (5 étapes)

- Sélecteurs `data-tour` pointent vers des éléments Sprint 1 → risque faible de casse sur binaire intégré.
- Validation à jouer : parcours manuel complet sur `PLI_ENABLE_M2=1 uvicorn pli.main:app` + frontend build prod.
- Critère succès : 5/5 étapes affichées sans erreur console, persistance `tour_done` OK.

### KB (60 articles FR/EN)

- Contenus statiques `docs/kb/fr/01-30.md` + `docs/kb/en/01-30.md` — indépendants du backend.
- Validation : checklist 60 articles × {accessible, recherche, liens internes, liens externes}. À rejouer sur build front.
- Recherche KB : dépend du moteur choisi (Algolia vs. Lunr local). À confirmer avec M3 si intégré.

### Marketing kit

- `marketing/press/` + `marketing/video/` + `marketing/LANDING-PAGE.md` — tous statiques.
- Intégration `/public/marketing-kit/` = scope M5 Sprint 11 (propriétaire M5).
- Pas d'action M4 sauf livraison assets à M5 si demandé.

## 7. Plan de travail

| Date | Action | Dépendance |
|------|--------|------------|
| 2026-04-22 | Journal, skeleton rapport, revue structurelle, cadre Option B validé | — |
| 2026-04-23 → 2026-05-06 | Préparation protocoles (Form NPS, checklist KB, scénario tour), sync M3 sur nommage tag | non bloquant |
| 2026-05-07 | T2.2 mergée (attendu M2) + **pose tag git commun `rebaseline-2026-05-XX`** (coordination M3) | **bloquant** |
| 2026-05-07 → 2026-05-09 | T4.3 relance uptime (date T0 runbook M5), T4.4 validation tour + KB | T2.2 + tag |
| 2026-05-08 → 2026-05-12 | T4.1 collecte NPS sur même tag, fenêtre 3j, target N≥30 | T2.2 + panel + tag |
| 2026-05-13 | Rédaction rapport final | données T4.1-T4.4 |
| 2026-05-14 | Publication + recommandation GO/NO-GO M4 explicite | deadline |

## 8. Décision finale (à statuer au 2026-05-14)

> À compléter avec données re-mesurées ou justifications replan.

Options de sortie du ticket :

- **A — GO M4 rétroactif avec chiffres re-mesurés** : NPS re-mesuré N≥30, rétention en attente Sprint 12 documentée, uptime baseline publiée, tour + KB validés.
- **B — GO M4 partiel avec replans** : NPS replan Sprint 12 (si N<30), rétention replan Sprint 12 ferme, uptime OK, tour + KB OK.
- **C — NO-GO M4 maintenu** : régression bloquante détectée sur binaire intégré (tour cassé, KB non servie, widget NPS en erreur). Ré-ouverture M4.

**Cadre validé direction** : option B retenue par défaut comme trajectoire la plus probable, avec possibilité de basculer vers A (si N≥30 atteint sous 3j) ou C (si régression tour/KB détectée).
**Consigne direction** : **honnêteté avant les chiffres**. NO-GO possible et acceptable — ne pas chercher à sauver une revendication sous pression deadline.

## 9. Pré-requis infra (arbitrages 2026-04-23 A1-A5)

Pour garantir la reproductibilité des mesures M4 sur le même périmètre que M3, les pré-requis suivants sont posés :

- **Baseline ancrée** : `rebaseline-base-2026-04-22` (manifeste md5 dans `docs/governance/tags/`). Empreinte globale `6a8d82bcbd292422f3ef87d0d6a30dce`. Toute campagne de mesure M4 commence par `scripts/rebaseline/check-baseline-md5.sh` (livré par M3) — abort si drift.
- **Freeze backend D→D+21** (A1) : `backend/pli/*.py` + `backend/tests/*.py` + `backend/pyproject.toml` gelés jusqu'au 2026-05-14. 3 escape hatches : hotfix P0, coverage T2.3 dead-code, fix vuln CRITICAL/HIGH. Impact M4 = nul tant qu'aucune régression perf ne requiert de modif backend.
- **Lockfile Python** (A2) : `backend/requirements.lock` posé par direction (md5 `548ce01ef60b32ec725174f4ab4ebaee`). Propriétaire maintenance : M2.
- **Lockfile Node** (A3) : `frontend/package-lock.json` **livré par M4 2026-04-24** (md5 `0b24e3020ca3290e814473048a11c562`, 8580 lignes, lockfileVersion 3). Dérivé de `package.json`, hors manifeste. Débloque `npm audit --production` côté M3.
- **Image Docker `pli/backend:prod`** (A4) : **en escalation** — sandbox M4 sans Docker. Deadline 2026-04-27 EOD. Escalation JM (option 1 Docker Desktop local, option 2 CI externe). Plan dégradé disponible si non résolu sous 72h : scan via lockfiles seuls (sans trivy image), avec réserve formelle dans les rapports M3 et M4.
- **Coordination M3/M4** : même tag logique de mesure, candidat `rebaseline-2026-05-10` (validation direction en attente).

### Impact arbitrages sur mes mesures

- **NPS (T4.1)** : pas d'impact A1 (feedback widget est frontend-only, rend des requêtes `/feedback` sur le backend figé). Bien au contraire — A1 garantit que les mesures NPS collectées entre 2026-05-08 et 2026-05-12 restent cohérentes avec le binaire scanné par M3.
- **Uptime (T4.3)** : pas d'impact A1. Surveillance depuis date mise en prod binaire intégré, backend figé = T0 stable.
- **Tour + KB (T4.4)** : pas d'impact A1. Contenus statiques et composants front.
- **Dépendance A4** : si l'image n'est pas buildée le 2026-05-07, M3 ne peut pas scanner, et par cascade M5 peut demander un retard sur la décision GO/NO-GO du 2026-05-14. Surveillance quotidienne jusqu'à résolution.

---

## Journal des mises à jour

- **2026-04-22 (matin)** : skeleton créé, plan de travail établi, recommandation préliminaire B. En attente T2.2.
- **2026-04-22 (arbitrage direction)** : **Option B validée**. Cadre acté : NPS N≥30 fenêtre 3j (fallback replan Sprint 12), rétention J30 replan Sprint 12 ferme (pas de métrique fabriquée), uptime baseline neuve à partir date mise en prod binaire intégré (coordination M5 pour runbook), tour + KB + marketing kit = validation fonctionnelle suffit. **Coordination M3 via même tag git figé** (réponse R2 direction à M3). Rapport final 2026-05-14 avec GO/NO-GO explicite, NO-GO possible.
- **2026-04-24 (ack arbitrages A1-A5)** : baseline `rebaseline-base-2026-04-22` ancrée, freeze A1 acté (impact M4 nul par défaut), A3 `frontend/package-lock.json` livré J-1, A4 image Docker en escalation JM. §9 "Pré-requis infra" ajouté au rapport. Daily 2026-04-23 publié en rattrapage + daily 2026-04-24 publié.

---

_Rapport rédigé par session M4._
_Réf. ticket `M4-rebaseline.md`, ordre mission `2026-04-22-ordre-mission.md`, audit 2026-04-22._
