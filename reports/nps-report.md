# Rapport NPS M4 — Beta privée PLI

**Période mesurée** : 12 août → 9 septembre 2026 (28 jours)
**Respondents** : 71 sur 98 beta users actifs (taux de réponse 72 %)
**Méthode** : widget in-app (cooldown 30 j, J+7 après signup minimum)
**Owner** : PM + UX
**Status** : final

## Résultat global

**NPS = +42**

Calcul :

- Promoters (9-10) : 40 / 71 = 56,3 %
- Passives (7-8) : 21 / 71 = 29,6 %
- Detractors (0-6) : 10 / 71 = 14,1 %
- Score = 56,3 − 14,1 = **+42,2**, arrondi **+42**

Cible fin M4 : **+40**. ✅ Atteint.

## Distribution des notes

```
10 ████████████████████████ 24 (34 %)  PROMOTERS
 9 ████████████████ 16 (23 %)          PROMOTERS
 8 ██████████████ 14 (20 %)            PASSIVES
 7 ███████ 7 (10 %)                    PASSIVES
 6 ████ 4 (6 %)                        DETRACTORS
 5 ██ 2 (3 %)                          DETRACTORS
 4 ██ 2 (3 %)                          DETRACTORS
 3 █ 1 (1 %)                           DETRACTORS
 2 ▪ 1 (1 %)                           DETRACTORS
 1 0                                    DETRACTORS
 0 0                                    DETRACTORS
```

**Note moyenne** : 8,17 / 10
**Médiane** : 9 / 10
**Mode** : 10 (24 respondents)

## Segmentation

### Par provider

| Segment | n | Promoters | Passives | Detractors | NPS |
|---|---:|---:|---:|---:|---:|
| Gmail only | 26 | 58 % (15) | 31 % (8) | 11 % (3) | **+47** |
| Microsoft only | 17 | 47 % (8) | 35 % (6) | 18 % (3) | **+29** |
| Mixte (≥2 providers) | 22 | 59 % (13) | 27 % (6) | 14 % (3) | **+45** |
| Non-technique | 6 | 67 % (4) | 17 % (1) | 16 % (1) | **+51** |

**Insight #1** : segment Microsoft-only le plus faible (+29). 2 des 3 detractors sont bloqués par admin tenant, 1 signale de la lenteur sur attachments via Graph.

**Action M5** : améliorer onboarding MS (guide admin dans invitation email), lobby interne pour push perfs Graph.

### Par mode (Cloud vs Local)

| Mode | n | NPS |
|---|---:|---:|
| Cloud (trial ou commercial) | 64 | **+41** |
| Local (Plus) | 7 | **+57** |

**Insight #2** : beta users en Local hyper satisfaits. Échantillon petit (7), mais 6/7 sont promoters. Signal fort sur positionnement Privacy pour M5.

### Par batch

| Batch | n répondants | NPS |
|---|---:|---:|
| Batch 1 (12/08) | 21 | +38 |
| Batch 2 (19/08) | 19 | +37 |
| Batch 3 (26/08) | 18 | +50 |
| Batch 4 (02/09) | 13 | +46 |

**Insight #3** : NPS croit avec les batches successifs. Hypothèse : bénéfice des fixes itération #1 + meilleure doc admin + buzz Discord sur les premiers promoters.

## Raisons citées (champ libre post-note)

### Top 5 raisons promoters (9-10) — n=40

1. **Filtre Humains/Notifs** (28 mentions) : "c'est THE killer feature"
2. **Vitesse & réactivité** (22 mentions) : recherche instant, UI fluide
3. **Privacy / local mode** (14 mentions) : "rare et précieux"
4. **Onboarding tour** (9 mentions) : "60 s et opérationnel"
5. **Design minimaliste** (8 mentions) : "pas de bloat"

### Top 5 raisons passives (7-8) — n=21

1. **Manque de mobile** (12 mentions) : "je voudrais PLI sur iPhone"
2. **Manque règles custom** (9 mentions) : "pas de rule-engine comme Sanebox"
3. **Thèmes limités** (6 mentions) : "juste dark/light, faudrait plus"
4. **Stripe pricing** (4 mentions) : "7€ c'est un peu cher pour un usage perso léger"
5. **Pas de Calendar** (3 mentions) : "manque une vue agenda intégrée"

### Top 5 raisons detractors (0-6) — n=10

1. **Admin Microsoft bloque** (4 detractors) : ne peuvent pas utiliser du tout
2. **Bug perf attachment Graph** (2 detractors) : liés au cas ci-dessus
3. **Sync Gmail interrompue** (1 detractor) : sporadique, investigation en cours
4. **Manque IMAP** (1 detractor) : email pro exotique, hors scope V1
5. **Opposition philosophique au cloud** (2 detractors) : voulaient Local gratuit (→ essai de switch vers 5€/mois proposé)

## Evolution NPS intra-beta

```
J+7   +29 (n=27, mid-iter-1)
J+14  +33 (n=52, fin iter-1)
J+21  +39 (n=67, mid-iter-2)
J+28  +42 (n=71, fin iter-2 = rapport actuel)
```

Progression nette de +13 points en 3 semaines. L'équipe a clairement capitalisé sur les feedbacks d'itération #1.

## Benchmarks externes (ordres de grandeur)

- NPS moyen SaaS B2B : **+30**
- NPS moyen outils productivity : **+25-35**
- NPS top-tier privacy-first (ex : Signal, ProtonMail) : **+50-60**
- NPS Superhuman (benchmark concurrent direct haut de gamme) : rapporté **+60** sur abonnés actifs

**Lecture** : +42 en beta fermée est excellent pour un produit 4 semaines d'usage. Objectif commercial M5 : **+50 à 12 mois post-launch**.

## Corrélations observées

- Users ayant complété le tour : NPS +47 (vs +28 pour ceux qui ont skippé)
- Users ayant utilisé le swipe ≥ 20 fois / semaine : NPS +52
- Users ayant connecté ≥ 2 comptes : NPS +45 vs +38 pour 1 compte
- Users ayant ouvert la KB au moins une fois : NPS +44 (neutre)

**Insight #4** : l'activation produit (tour complété + swipe fréquent) est le principal driver de satisfaction. Priorité M5 : double down sur le tour et rendre le swipe plus découvrable (tooltip J+1 ?).

## Recommandations

### Pour M5 (commercial launch)

1. **Garder le filtre Humains/Notifs au cœur du pitch** — c'est la raison #1 des promoters
2. **Résoudre le pain point MS admin** — pas négligeable, déjà 4/10 detractors viennent de là
3. **Prioriser mobile PWA** — plus gros item qualitatif des passives
4. **Communiquer sur Local** — score +57 chez Local users, segment à protéger

### Pour V1.1 (Q4 2026)

1. Règles custom light (if-then-else simples) — #2 passives
2. Plus de thèmes — facile, impact perçu fort
3. Amélioration perf attachments Microsoft Graph

### Pour V2 (2027)

1. Vue Calendar minimale
2. Multi-langue ES/DE/IT/PT
3. Client mobile natif iOS + Android

## Annexes

- Raw data : [beta-nps-raw-2026-09-09.csv](beta-nps-raw-2026-09-09.csv) (anonymisé user_hash)
- Query SQL : voir `backend/pli/beta/nps.py` `compute()`
- Dashboard Grafana : [Beta Overview > NPS panel](http://grafana.pli.internal/d/beta-overview)
