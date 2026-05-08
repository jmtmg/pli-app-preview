# Ticket M4 — Re-baseline NPS + rétention + uptime

**Priorité** : P2 (débloqué par T2.2 côté M2)
**Propriétaire** : session PLI M4
**Émis par** : direction (session Mail), 2026-04-22
**Deadline** : 2026-05-14

---

## Contexte

Tu as fermé M4 avec GO M5 et revendiqué :
- NPS +42
- Rétention J30 68%
- Uptime 99.94%
- 60 articles KB FR/EN livrés
- Tour onboarding 5 étapes + widget NPS livrés
- Marketing kit livré

Audit transverse 2026-04-22 a montré que ces métriques produit (NPS, rétention, uptime) n'ont pas pu être mesurées sur le binaire intégré (seul M1 Sprint 1 tourne actuellement dans `main.py`). Le tour, la KB et le marketing kit restent valides en l'état (contenus statiques).

**Ton ticket est débloqué** quand M2 a fini T2.2.

## Travail à faire

### T4.1 — Re-mesure NPS sur binaire intégré

- Vérifier que le widget NPS est bien chargé avec `PLI_ENABLE_M2=1`
- Collecter N ≥ 30 réponses sur le binaire intégré (via beta testeurs internes si dispo, sinon sample synthétique documenté)
- Si impossibilité de re-mesurer en temps imparti : documenter clairement "NPS revendiqué sur environnement isolé, non reproduit sur binaire intégré — à re-mesurer Sprint 12"

### T4.2 — Rétention J30

- Même logique : cohort tracking sur binaire intégré requis
- Si impossibilité : documenter (probable vu la fenêtre 30j) et replanifier post-Launch

### T4.3 — Uptime

- Vérifier la remontée Prometheus/Grafana (ou équivalent) fonctionne avec M2 wired
- Uptime est un indicateur cumulatif : relancer compteur à partir de la mise en prod binaire intégré
- Publier baseline dans runbook M5

### T4.4 — Validation tour + KB sur binaire intégré

- Parcours tour 5 étapes : reproductible sans bug sur binaire intégré ?
- KB : 60 articles accessibles, recherche fonctionnelle, liens OK ?
- Marketing kit : à intégrer dans `/public/marketing-kit/` si pas déjà fait

### T4.5 — Rapport de synthèse

Fichier `docs/governance/metrics/2026-04-22-rebaseline-m4.md` avec :
- Ce qui est re-mesurable en temps imparti (uptime OK ; NPS/rétention selon testeurs)
- Ce qui doit attendre Sprint 12 post-Launch
- Recommandation GO/NO-GO maintien M4

## Règles

- Pas de démarrage avant T2.2
- Ne pas ré-écrire ce qui est déjà livré (tour, KB, kit) — juste valider
- Honnêteté sur les chiffres : si pas re-mesurable, le dire

## Done criteria

- Tour + KB validés sur binaire intégré
- Uptime baseline relancé avec date de référence documentée
- NPS / rétention : plan clair (re-mesuré OU replanifié avec justification)
- Rapport de synthèse publié

## Journal

### 2026-04-22 — Prise en charge ticket (session M4)

**Statut** : bloqué par M2 T2.2 (deadline 2026-05-07).

**Fait** :
- Ticket lu + ordre de mission `2026-04-22-ordre-mission.md` lu.
- Ticket M2 bloquant `M2-unblock-auth.md` lu → débloqueur = T2.2 (wire-up routers derrière `PLI_ENABLE_M2`, 2026-05-07).
- État `backend/pli/main.py` vérifié : seuls les 6 routers Sprint 1 montés (auth, accounts, conversations, messages, contacts, search). Audit direction confirmé.
- Revue structurelle `frontend/src/features/feedback/NPSWidget.tsx` (162 lignes) : structurellement sain, gating J+7 / 30j / opt-out conforme spec, POST `/feedback` attendu, a11y OK. **Non validable** tant que router `/feedback` pas monté.
- Revue structurelle `frontend/src/features/onboarding/Tour.tsx` (184 lignes) : 5 étapes conformes, sélecteurs `data-tour` pointant vers éléments Sprint 1 (risque faible). Validation comportementale en attente binaire intégré.
- Marketing kit (`marketing/press/`, `marketing/video/`, `marketing/LANDING-PAGE.md`) : statique, pas de re-baseline nécessaire. Intégration `/public/marketing-kit/` = scope M5 Sprint 11.
- Rapport skeleton créé : `docs/governance/metrics/2026-04-22-rebaseline-m4.md`.
- Daily publié : `docs/governance/daily/M4-2026-04-22.md`.

**Constat honnêteté** : les chiffres NPS +42 / rétention J30 68% / uptime 99.94% revendiqués à la clôture M4 initiale ont été mesurés sur branches/environnements isolés, **non reproduits** sur le binaire intégré. Ils ne peuvent pas justifier un GO M5 en l'état.

**Recommandation préliminaire (option B du rapport)** :
- **T4.1 NPS** : re-mesurer sur binaire intégré dès T2.2 mergée ; si N<30 atteignable : replan Sprint 12 post-Launch.
- **T4.2 Rétention J30** : fenêtre 30j physiquement incompatible avec deadline 2026-05-14 → **replan Sprint 12** certain. Retirer le chiffre 68% de tous les supports (pitch, press, landing).
- **T4.3 Uptime** : relancer compteur T0 = date mise en prod binaire intégré ; 72h minimum avant chiffre publié ; baseline dans runbook M5.
- **T4.4 Tour + KB** : validation à jouer dès T2.2 ; marketing kit livrable à M5 sans dépendance technique.

**Bloqueurs actifs** :
- M2 T2.2 : wire-up `PLI_ENABLE_M2` → sans ce flag, `uvicorn pli.main:app` ne monte pas `/feedback`, `/beta`, `/tenancy` requis pour mesure NPS.

**Next (non bloquant, d'ici 2026-05-07)** :
- Préparer questionnaire NPS de secours (Google Form) + scripts d'extraction DB cohorte.
- Préparer checklist validation tour (scénario reproductible 5 étapes).
- Préparer liste de contrôle KB (60 articles × {accessible, recherche, liens}).
- Veille daily M2 — réagir si T2.1 glisse (cascade sur T2.2).

_Prochaine mise à jour Journal : 2026-04-23 (daily)._

### 2026-04-22 — Arbitrage direction : Option B validée + coordination M3 (session M4)

**Cadre acté par direction** :

1. **NPS (T4.1)** : re-mesure sur binaire intégré, panel **N≥30**, fenêtre **3 jours ouvrés**. Si taux de réponse insuffisant → bascule replan Sprint 12 documentée (pas de métrique "sauvée" sous N=30).
2. **Rétention J30 (T4.2)** : **replan Sprint 12 ferme**. Fenêtre 30j incompatible avec deadline 2026-05-14. **Pas de métrique fabriquée.** Retirer "68%" de tous les supports externes (pitch, press release, landing, M4-CHECKPOINT-4-RESULTS, reports/retention-j30.md). Action CONT/MKT à cascader Sprint 11.
3. **Uptime (T4.3)** : baseline neuve à partir de la **date de mise en prod du binaire intégré**. Date à documenter précisément dans le runbook M5 (coordination M5 requise — pas de chiffre sans date).
4. **Tour + KB + marketing kit (T4.4)** : **validation fonctionnelle suffit**, pas de re-contenu. Parcours tour OK + KB 60 articles servis + recherche OK → done.

**Coordination M3 (réponse R2 direction à M3, reproduite ici)** :
- Dès T2.2 validée par M2, M3 et M4 se coordonnent pour poser un **tag git commun** (ex. `rebaseline-2026-05-10`).
- M3 mesure Lighthouse + scan vulns + OCR E2E depuis ce tag. M4 mesure NPS + uptime + tour/KB depuis ce **même tag**.
- Prévient l'écart "M3 à X, M4 à Y, non comparables".
- Action M4 : s'aligner sur M3 pour le choix du nommage + date exacte du tag dès que M2 livre.

**Rapport final** : publication 2026-05-14 avec recommandation **GO/NO-GO explicite**. **NO-GO est une sortie acceptable** — honnêteté avant les chiffres, pas de ré-écriture pour sauver la revendication sous pression deadline.

**Action immédiate (2026-04-22)** :
- Rapport de synthèse mis à jour avec cadre validé : `docs/governance/metrics/2026-04-22-rebaseline-m4.md`.
- Daily M4 mis à jour.
- Communication à anticiper (d'ici 2026-05-06) : ping M3 pour accord tag, ping M5 pour réservation slot runbook uptime.

**Next concret** :
- Préparer checklist coordination tag git avec M3 (mirroir de `REBASELINE-CHECKLIST.md` annoncé par M3).
- Préparer note pour M5 : "uptime baseline = date tag `rebaseline-*` mise en prod", format attendu dans runbook.
- Préparer note pour CONT/MKT Sprint 11 : retrait du chiffre "68%" de tous les supports externes + remplacement par mention "mesure Sprint 12 post-Launch".

### 2026-04-24 — Ack dispatch arbitrages A1-A5, A3 livré, A4 escalation JM (session M4)

**Contexte** : dispatch direction `docs/governance/dispatch/2026-04-23-arbitrages.md` reçu avec ping "URGENT — daily M4 2026-04-23 manquant + deux actions A3/A4 à exécuter".

**Mea culpa** : daily 2026-04-23 manquant, publié aujourd'hui en rattrapage (`M4-2026-04-23.md`) + daily du jour (`M4-2026-04-24.md`). Engagement : 1 daily par jour ouvré d'ici 2026-05-14, même en veille.

**Ack arbitrages** :
- A1 (freeze `backend/pli/` D→D+21) : noté, impact M4 = nul par défaut. Vigile engagée (ping direction si PR non autorisée détectée).
- A2 (lockfile Python par direction, maintenance M2) : pas d'action M4.
- A3 (`frontend/package-lock.json`) : **LIVRÉ** 2026-04-24 14:01 UTC. 304 902 bytes, 8580 lignes, lockfileVersion 3, md5 `0b24e3020ca3290e814473048a11c562`. Obstacle rencontré et documenté : `node_modules/` existant corrompu (package sans version) → contournement via génération dans `/tmp/` puis copie. Débloque `npm audit --production` côté M3.
- A4 (image `pli/backend:prod`) : **en escalation JM**. Docker absent du sandbox M4. Deux options proposées (Docker Desktop local vs CI externe). Deadline 2026-04-27 EOD.
- A5 (OpenAPI Python 3.11+) : pas d'action M4.

**Baseline ancrée** : `rebaseline-base-2026-04-22`, empreinte globale `6a8d82bcbd292422f3ef87d0d6a30dce`. Toute mesure M4 à venir préfixée par `check-baseline-md5.sh` (livré par M3 cf. son daily 2026-04-23).

**Rapport de synthèse mis à jour** : `docs/governance/metrics/2026-04-22-rebaseline-m4.md` — ajout §9 "Pré-requis infra (A1-A5)" + journal mises à jour.

**Risques suivis** :
- R-M4-01 (discipline daily) — rattrapage fait.
- R-M4-02 (node_modules corrompu) — contourné A3, assainissement à programmer.
- R-M4-03 (Docker absent sandbox) — escalation JM, cascade possible sur tag commun M3 si non résolu sous 72h.

**Questions en attente direction** :
1. A4 : ~~option 1 vs option 2~~ **RÉSOLU** 2026-04-24 par "prend docker" JM — option 1 retenue. Build turnkey livré (`backend/build-prod-image.ps1` + `backend/BUILD-PROD-IMAGE.md` + `backend/.dockerignore`).
2. Nommage tag commun M3/M4 : `rebaseline-2026-05-10` proposé.
3. CI externe de secours en parallèle (pas urgent, marge 72h) ?

**A4 — turnkey livré 2026-04-24 fin de journée** :
- `backend/build-prod-image.ps1` : script PowerShell qui vérifie Docker, build `--target runtime -t pli/backend:prod`, inspect + affichage Image ID / taille / digest.
- `backend/BUILD-PROD-IMAGE.md` : mode d'emploi JM avec pré-requis Docker Desktop + WSL2, instructions double-clic ET terminal, troubleshooting.
- `backend/.dockerignore` : exclut caches, venv, tests, docs — image plus propre à scanner côté M3.
- **Reste à JM** : installer Docker Desktop (pas visible dans la liste d'apps) + démarrer daemon + exécuter le script + coller retour (Image ID + taille).
- **Une fois fait** : M4 confirme A4 closed, notifie M3 pour scan trivy.

**Next** : daily 2026-04-25 même sans fait majeur (discipline R-M4-01). Veille retour JM sur A4. Pré-rédaction §6 rapport "validation fonctionnelle tour + KB" si temps disponible.

---

_Réf. audit 2026-04-22, ordre de mission `2026-04-22-ordre-mission.md` §2 D5 et §3 P2._
_Bloqué par : ticket M2 T2.2._
