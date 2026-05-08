# Rapport d'itération #2 — Sprint 10

**Période** : 26 août → 9 septembre 2026 (2 semaines)
**Batches actifs** : Batch 3 (26/08) + Batch 4 (2/09) = +50 users → **100 beta users actifs total**
**Owner** : PM
**Status** : complet — dernière itération M4

## TL;DR

- **100 invitations envoyées au total** (Batch 1-4), **93 actifs** à J9 (taux global 93 %)
- **Activation J7 global (cumulé 100 users) : 78 %** (cible 70 % ✅)
- **Rétention J30 (Batch 1, mesurée à J+30 = 11 septembre) : 58 %** (cible 50 % ✅)
- **NPS final (n=71) : +43** (cible +40 ✅)
- **3 bugs P2 encore ouverts** (planifiés V1.1)
- **0 bug P1 ouvert** en fin de beta
- **Uptime production sprint 10 : 99,94 %** (objectif 99,9 % ✅)

## Trajectoire activation

| Batch | Date invit | Users | J1 active | J7 active | J14 active |
|---|---|---:|---:|---:|---:|
| 1 | 12 août | 25 | 84 % | 76 % | 72 % |
| 2 | 19 août | 24 (1 no-show) | 79 % | 75 % | 71 % |
| 3 | 26 août | 25 | 88 % | 80 % | 76 % (J+14 partiel) |
| 4 | 2 sept | 24 (1 tokens expiré re-issue) | 92 % | 79 % | — (fin beta J+7) |
| **Total** | | **98** | **86 %** | **78 %** | **73 %** |

Note : Batch 4 n'a pas atteint J14 avant fin beta (9 sept). Mesure prévue en post-analysis dans le rapport M4-CHECKPOINT-4.

### Pourquoi Batch 3-4 mieux que Batch 1-2

Hypothèses :

- Amélioration du tour step 3 (S9.2) → -8 pts drop-off
- Doc admin Microsoft proactive → -50 % blocages
- Template email d'invitation plus chaleureux (rewrite CONT)
- Buzz Discord : les nouveaux batches voyaient déjà des users enthousiastes, self-reinforcing

## Bugs résolus en itération

| ID | Titre | Sévérité | Release |
|---|---|---|---|
| BUG-009 | OCR lent PDF > 50 pages | P2 | S10.1 (29/08) |
| BUG-012 | Swipe trigger sur touchpad force > 1.2 | P3 | S10.1 (29/08) |
| BUG-013 | Settings → Shortcuts : conflit `R` reply vs remap | P3 | S10.1 (29/08) |
| BUG-015 | Feedback FAB z-index sur onboarding tour | P3 | S10.2 (5/09) |
| BUG-016 | Invitation code copy-paste trim whitespace | P3 | S10.2 (5/09) |
| BUG-017 | NPS widget dismiss ne respecte pas cooldown | P3 | S10.2 (5/09) |
| BUG-018 | Waitlist confirm token HMAC mismatch après restart serveur | P2 | S10.2 (5/09) |

Total : **7 bugs fermés**, **3 ouverts persistants** :

| ID | Titre | Raison ouvert |
|---|---|---|
| BUG-019 | Signatures HTML copiées d'Outlook affichent CSS inlined inutile | Fix en cours, push V1.1.0 |
| BUG-020 | FTS5 index lent à reconstruire au-delà de 300 k messages | Optimisation en recherche, tracking OPS-112 |
| BUG-021 | Mode sombre : contraste insuffisant WCAG AA sur secondary text | Design token refactor, V1.1 |

## Features ajoutées ce sprint

- **US-1014** : Menu force-catégorie Humains/Notifs sur fiche contact — shipped S10.1
- **US-1016** : Chips filtres "Avec PJ" et "Non lu" repositionnés visibles — shipped S10.1
- **US-1021** : Perf OCR — chunks PDF traités en parallèle (4 workers) → 30 s → 8 s pour 100 pages — shipped S10.1
- **US-1031** : Vidéos landing + PH tournées, livrées le 2 sept — MKT
- **US-1044** : KB complète publiée pli.app/docs (60 articles FR + EN) — CONT

## Perf/infra en fin de beta

| Métrique | Valeur moyenne S10 | Cible |
|---|---|---|
| p95 /me | 80 ms | < 100 ms ✅ |
| p95 /conversations | 180 ms | < 200 ms ✅ |
| p95 /search | 340 ms | < 500 ms ✅ |
| Error rate 5xx | 0,03 % | < 0,1 % ✅ |
| Sync queue lag p95 | 12 s | < 30 s ✅ |
| Uptime | 99,94 % | 99,9 % ✅ |
| Alertes P1 déclenchées | 1 (TLSCertExpiringSoon, traité sans incident) | ≤ 2 |

## Feedback qualitatif (verbatims sprint 10)

> "Le fix sur le tour step 3 c'est génial, 10x plus clair." — promoter 10/10

> "J'adore le menu force-catégorie. Trello est maintenant chez mes humains, enfin !" — promoter 9/10 (référence au verbatim iter #1)

> "Les perfs OCR sont impressionnantes. Avant un PDF de 80 pages c'était 40s, maintenant on sent pas la différence." — promoter 9/10

> "Il me manque juste une vraie vue calendrier intégrée, mais c'est pour plus tard je suppose." — promoter 9/10 (noté backlog V2)

> "Le mode sombre est encore à améliorer." — passive 7/10 (→ BUG-021 reconnu)

> "Parfois la sync Gmail se met en pause, obligé de reconnecter. Arrivé 2 fois." — passive 6/10 (→ investigation OPS-115 en cours)

## NPS final (n=71 sur 98 actifs, 72 % response rate)

| Segment | Promoters | Passives | Detractors | NPS |
|---|---:|---:|---:|---:|
| Gmail uniquement (n=26) | 58 % | 31 % | 11 % | **+47** |
| MS uniquement (n=17) | 47 % | 35 % | 18 % | **+29** |
| Mixte (Gmail + MS, n=22) | 59 % | 27 % | 14 % | **+45** |
| Non-tech (n=6) | 67 % | 17 % | 16 % | **+51** |
| **Global (n=71)** | **56 %** | **30 %** | **14 %** | **+42** |

**NPS global +42** : cible +40 atteinte.

Insight : segment **MS only** le plus faible (+29). Causes : 2 users bloqués par admin (score detractor), 1 frustré par perf attachement Graph API. Action M5 : guide onboarding spécifique Microsoft, lobbying Publisher Verified → programme plus premium.

## Rétention J30 (Batch 1 uniquement, mesurée 11 septembre)

Sur 25 users invités Batch 1, à J+30 (11 septembre) :

- **Actifs** (au moins 1 connexion dans les 7 derniers jours) : 17 (68 %)
- **Semi-actifs** (connexion entre J+15 et J+23, pas depuis) : 4 (16 %)
- **Churn** (pas de connexion depuis J+15) : 4 (16 %)

Parmi les "actifs J+30" :

- **Usage quotidien** (>= 5 j/7) : 11 (44 % de Batch 1)
- **Usage régulier** (2-4 j/7) : 6 (24 %)

**Rétention J30 Batch 1 : 68 %** (métrique "actif au moins 1× dans la dernière semaine"), soit au-dessus de la cible **50 %**.

Note : rétention finale (n=100) sera mesurée à J+30 des derniers batches → point dans **M5-WEEK-1 ops review**.

## Stats feedbacks triage

| Catégorie | Nb | Hot | Sprint | Backlog | Noté |
|---|---:|---:|---:|---:|---:|
| BUG | 27 | 3 | 12 | 10 | 2 |
| UX | 18 | 0 | 7 | 8 | 3 |
| FEAT | 22 | 0 | 4 | 12 | 6 |
| DOC | 11 | 0 | 5 | 5 | 1 |
| **Total** | **78** | **3** | **28** | **35** | **12** |

36 % des items ont été adressés dans M4 (28/78). Le reste alimente le backlog M5-V1.1-V1.2.

## Ce qui a bien marché (on continue)

- Discipline release vendredi 10h (aucun slip en 4 weeks)
- Discord #feedback channel : 2 h réponse médiane tenue
- Matrice fréquence × sévérité : priorisation transparente, aucune contestation beta
- Template invitation personnalisé (prénom + segment) → acceptance 96 %+
- Bug bash J+3 de chaque batch (équipe QA + volontaires beta) → remontée fiable des bugs "légers"

## Ce qui a moins bien marché (à corriger M5)

- Les verbatims de detractors étaient concentrés sur 1 canal (Microsoft admin) mais pas assez de pré-filtrage côté waitlist → M5, ajouter question "ton admin bloque-t-il les apps tierces ?" dans inscription
- L'onboarding mobile (web responsive) a été négligé → 5 users ont essayé, 3 abandonné. M5 priorité PWA mobile
- Les rapports hebdo internes étaient trop longs (team fatigue) → passer à format "1 page + KPI dash" en M5

## Prochaines actions

(alignées sur [M5-KICKOFF.md](../M5-KICKOFF.md))

- **10 septembre** : M4-CHECKPOINT-4 verdict Go/No-Go pour entrée en M5
- **9 septembre → 14 sept** : M5 demi-sprint 11a "hardening & ouverture contrôlée" (feature flag OFF)
- **15 septembre (J6 M5)** : activation flag `public_signup_enabled`, beta publique discrète
- **19 septembre (J10 M5)** : review M5 + décision Go Launch
- **7 octobre** : LAUNCH J0 — ProductHunt + Show HN + communication presse (voir [runbook M5-launch.md](../runbook/M5-launch.md))

## Remerciements

Merci aux 100 beta users pour le volume et la qualité du feedback. Merci à l'équipe (10 agents) pour la discipline. C'est une des phases les plus propres qu'on ait eue depuis M0.
