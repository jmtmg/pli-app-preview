# Rapport de rétention J30 — Beta M4

**Période mesurée** : J+30 après chaque batch (Batch 1 = 11 septembre 2026)
**Owner** : PM + BE (data)
**Status** : partiel à fin M4 (Batch 1 complet, 2-4 à J+7 au moment du snapshot) — mis à jour définitivement 4 octobre 2026 pour tous batches

## Définitions

- **Actif J+30** : user ayant au moins **1 session** dans les 7 jours précédant J+30 (window roulante)
- **Churné** : pas de session depuis J+15 (2 semaines consécutives d'inactivité)
- **Semi-actif** : session entre J+15 et J+23, pas depuis
- **Hautement actif** : ≥ 5 sessions / 7 derniers jours

## Rétention globale (tous batches) — snapshot au 4 oct 2026

| Batch | Taille | Date invit | J+30 | Actifs J+30 | Taux |
|---|---:|---|---|---:|---:|
| Batch 1 | 25 | 12 août | 11 sept | 17 | 68 % |
| Batch 2 | 24 | 19 août | 18 sept | 15 | 63 % |
| Batch 3 | 25 | 26 août | 25 sept | 17 | 68 % |
| Batch 4 | 24 | 2 sept | 2 oct | 14 | 58 % |
| **Total** | **98** | | | **63** | **64 %** |

**Rétention J+30 global : 64 %** (cible M4 : 50 % ✅ — dépassement de +14 pts)

## Intensité d'usage des J+30 actifs (n=63)

| Intensité | Nb users | % des actifs | % des invités |
|---|---:|---:|---:|
| Quotidien (≥ 5 j/7) | 28 | 44 % | 29 % |
| Régulier (2-4 j/7) | 21 | 33 % | 21 % |
| Occasionnel (1 j/7) | 14 | 22 % | 14 % |
| **Total actifs** | **63** | 100 % | **64 %** |

**Insight #1** : 29 % des invités deviennent des **power users quotidiens à J+30**. Benchmark SaaS productivity : 15-20 %. On est au-dessus.

## Segmentation churn (n=35 non-actifs J+30)

| Profil | Nb | Explications principales |
|---|---:|---|
| Admin MS bloqué | 4 | Ne sont jamais activés (churn J+1-J+7) |
| Non-activé tour | 6 | Signup + OAuth, mais abandon avant first send |
| Activé puis lâché | 14 | Usage initial OK, puis décroît progressivement |
| Semi-actif oscillant | 7 | Sessions sporadiques, ne franchit pas seuil actif |
| Churné silencieux | 4 | Utilisé 2-3 semaines puis disparu, pas de signal feedback |

## Courbe de rétention (Batch 1, observation granulaire)

```
J+1   ██████████████████████████ 22/25 = 88 %
J+7   ████████████████████████ 19/25 = 76 %
J+14  ███████████████████████ 18/25 = 72 %
J+21  ██████████████████████ 17/25 = 68 %
J+30  ██████████████████████ 17/25 = 68 %
```

Plateau clair entre J+21 et J+30 → les users qui restent 3 semaines restent durablement. Cohérent avec "product-market fit signal : habit formation en 3 semaines" (hypothèse Charles Duhigg).

## Rétention par segment

| Segment | n | Rétention J+30 |
|---|---:|---:|
| Non-tech | 6 | **83 %** (5/6) |
| Mixte (≥2 providers) | 22 | **68 %** (15/22) |
| Gmail only | 26 | **65 %** (17/26) |
| Microsoft only | 17 | **53 %** (9/17) |

**Insight #2** : corrélation forte entre adoption PLI et complexité d'usage. Les users avec **plusieurs comptes mail** restent le plus (besoin "hub unifié" servi). Les non-tech sont très fidèles (produit assumé simple).

**Insight #3** : segment MS only à 53 % rétention, très proche de la cible 50 %. Même pattern que NPS — à travailler en M5.

## Facteurs corrélés à la rétention J+30

Analyse multi-variée simple (régression logistique, coefficient non-normalisé) :

| Feature | Coefficient | Importance |
|---|---:|---|
| Tour complété | +1,42 | ⭐⭐⭐⭐⭐ |
| ≥ 2 comptes connectés | +0,89 | ⭐⭐⭐⭐ |
| Swipe ≥ 10 fois semaine 1 | +0,76 | ⭐⭐⭐⭐ |
| KB ouverte au moins 1 fois | +0,48 | ⭐⭐⭐ |
| Discord actif (post ≥ 1) | +0,31 | ⭐⭐ |
| NPS ≥ 7 à J+7 | +0,22 | ⭐⭐ |
| Admin MS bloquant | −2,10 | ⭐⭐⭐⭐⭐ (négatif) |

**Insight #4** : **Terminer le tour** est le meilleur prédicteur individuel de rétention J+30. Confirme la priorité M5 de soigner l'onboarding.

## Comparatif benchmark

- Benchmark SaaS productivity beta programs : **30-50 %** rétention J+30
- Benchmark email clients (historique Superhuman launch) : **45-55 %**
- PLI M4 : **64 %**

Lecture prudente : on est sur un échantillon opt-in motivé (waitlist proactive). Rétention réelle post-M5 launch sera probablement **10-20 pts plus basse**. Cible M5 (12 mois post-launch) : **40-45 %**.

## Fatigue NPS et autres signaux négatifs (contre-mesures à suivre)

- **Widget NPS dismiss** : 4 users l'ont dismiss (4 %). Cadence actuelle (apparaît J+7 puis cooldown 30j) semble bonne.
- **Feedback FAB** non cliqué : 40 % des actifs J+30 n'ont **jamais** utilisé le FAB. Normal (pas tous bug-reporters) mais à surveiller.
- **Email nurturing** (3 mails en 30 j post-signup) : open rate 52 %, click 18 %. À optimiser en M5 avec parcours personnalisé.

## Actions pour M5 découlant de l'analyse

1. **Onboarding** : tout passer en revue pour augmenter complétion tour à >90 % (actuellement 78 %)
2. **Multi-account incentive** : proposer explicitement "Ajoute un 2e compte" à J+3 (mail nurturing)
3. **Segment MS** : programme dédié (guide admin + case studies clients Workspace)
4. **Discord** : l'engagement communautaire augmente la rétention. Garder le serveur actif post-M5.
5. **Admin MS block** : ajouter question "ton admin autorise-t-il les apps OAuth tierces ?" dans formulaire waitlist pour pré-filtrer (et adresser cas dès l'invitation)

## Caveats méthodo

- Batch 4 mesuré à J+30 après fin beta (2 oct) — les utilisateurs se sont retrouvés dans un contexte "fin officielle" qui a pu artificiellement gonfler churn. Ajustement mental à faire : rétention Batch 4 potentiellement 5-10 pts plus haute si on avait prolongé beta.
- Small sample size (25/batch) → intervalles de confiance larges (±10 pts à 95 %). Ne pas sur-interpréter les deltas entre batches.
- "Actif" est une métrique d'ouverture d'app, pas d'usage qualifié (send/archive). Définir "power active" pour M5 (e.g. "≥ 10 actions/semaine").

## Annexes

- Raw data : [beta-retention-2026-10-04.csv](beta-retention-2026-10-04.csv)
- Query : voir `backend/pli/beta/activation.py` `retention()`
- Dashboard : [Grafana > Beta Overview > Retention panel](http://grafana.pli.internal/d/beta-overview)
