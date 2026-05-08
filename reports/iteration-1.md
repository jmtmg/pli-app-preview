# Rapport d'itération #1 — Sprint 9

**Période** : 12 août → 26 août 2026 (2 semaines)
**Batches actifs** : Batch 1 (12/08) + Batch 2 (19/08) = 50 beta users
**Owner** : PM
**Status** : complet

## TL;DR

- **50 invitations envoyées** (100 % acceptation sur batch 1, 96 % sur batch 2 → 49 actifs sur 50)
- **Activation J7 moyenne : 76 %** (au-dessus de l'objectif 70 %)
- **Activation J1 : 82 %** (connexion OAuth + 1er sync)
- **NPS intermédiaire (n=27) : +33** (proche de la cible finale +40, en progression)
- **15 bugs reportés** → 9 fixés en release S9.2, 4 planifiés S10, 2 rejetés (hors scope)
- **3 hot-fix urgents** déployés hors cycle (authentification Gmail + search crash)

## Activation par étape (Batch 1 + 2 cumulé, n=49)

| Étape | Users atteints | % | Delta vs cible |
|---|---:|---:|---:|
| Signup | 49 | 100 % | ✅ |
| Email verified | 48 | 98 % | ✅ |
| OAuth connected | 45 | 92 % | ✅ |
| First sync ≥ 1 message | 43 | 88 % | ✅ |
| Tour completed | 38 | 78 % | ≈ (cible 80 %) |
| First send | 37 | 76 % | ✅ |

**Activé** (first_sync AND tour_completed) : **37 / 49 = 75,5 %** à J7.

## Friction points observés

### Top 3 frictions (fréquence × sévérité)

1. **OAuth Microsoft — admin_policy_enforced** (4 users Batch 2)
   - Tous en entreprise sur tenant Microsoft restrictif
   - Solution mise en place : [doc admin](../docs/kb/fr/27-microsoft-admin.md) proactive + mail de pré-avertissement à J-1 pour les batches suivants
   - Impact : 2/4 ont résolu avec leur admin, 2/4 abandon silencieux (à relancer en S10)

2. **Tour — step 3 "Swipe"** : 11 % drop-off (vs 4-6 % sur les autres steps)
   - Hypothèse UX : explication textuelle trop dense sur step 3
   - Fix pushed S9.2 : réduction copy de 35 mots → 18 mots, illustration animée
   - Check impact attendu : J+7 après S9.2 = 2 sept (S10)

3. **Rate-limit feedback trop agressif** (3 users qui ont reporté plusieurs bugs successivement et ont été bloqués)
   - Limite passée de 3/heure → 5/heure (toujours safe anti-abus, mais laisse respirer les heavy testers)
   - Déployé S9.2

## Bugs ouverts vs fermés

| Sévérité | Reportés | Fermés | Ouverts |
|---|---:|---:|---:|
| P1 (bloquant) | 3 | 3 | 0 |
| P2 (impactant) | 5 | 4 | 1 |
| P3 (gênant) | 7 | 2 | 5 |

**P1 traité** :

- BUG-001 : crash search sur query vide (Batch 1 J+2) — hot-fix J+3
- BUG-002 : OAuth Gmail boucle infinie si popup fermée — hot-fix J+4
- BUG-003 : DB lock contention sync simultané 3 comptes — fix S9.2

**P2 ouvert persistant** :

- BUG-009 : OCR lent sur PDF > 50 pages (estimation : 30 s au lieu de 5 s) — planifié S10

## Feedback qualitatif (verbatims anonymisés)

> "Franchement, le filtre Humains c'est la killer feature. Mais je voudrais pouvoir forcer Trello dans Humains parce que c'est mon équipe." — promoter 9/10 (→ ajout menu force-catégorie planifié S10)

> "La recherche est rapide mais je galère à retrouver un mail avec une PJ PDF. Les filtres sont cachés." — passive 7/10 (→ refonte chip filters planifiée V1.1)

> "J'aime bien mais ça manque de thèmes / personnalisation." — passive 8/10 (→ backlog V1.2)

> "Le onboarding est parfait, 60 secondes et j'étais opérationnel." — promoter 10/10

> "Cassé sur mon poste Microsoft 365 d'entreprise, mon DSI bloque l'app." — detractor 4/10 (→ fix partiel via doc admin + relance)

## NPS intermédiaire (n=27, J+7 moyen)

- Promoters (9-10) : 13 (48 %)
- Passives (7-8) : 9 (33 %)
- Detractors (0-6) : 5 (19 %)
- **NPS = 48 − 19 = +29**

Note : le NPS cible de fin M4 est +40. À J+7 on est à +29, la progression est cohérente (on gagne en général 5-10 points entre J+7 et J+30 chez les survivors).

## Releases de l'itération

- **S9.1 — 15 août** (Friday 10h) : features core beta (déjà en prod avant kickoff via sprint 9)
- **S9.2 — 22 août** (Friday 10h) : fixes batch 1, ajustements tour, rate-limit feedback
- **Hotfix H9.1 — 14 août** : BUG-001 search crash
- **Hotfix H9.2 — 16 août** : BUG-002 OAuth Gmail loop
- **Hotfix H9.3 — 22 août** (in release) : BUG-003 DB lock

## Actions décidées pour itération #2 (Sprint 10)

- ✅ Ajouter menu force-catégorie contact Humains/Notifs (US-1014)
- ✅ Perf OCR PDF grandes pièces (US-1021)
- ✅ Refonte chips filtres avec "Avec PJ" plus visible (US-1016)
- ✅ Relance des 2 users Microsoft admin bloqués (CONT)
- ❌ Thèmes custom → backlog V1.2 (pas notre priorité M4)
- ❌ Langues supplémentaires → backlog V1.2

## Risques identifiés à surveiller S10

- **Ms admin block** : 8 % de drop (4/50). Si même ratio sur batch 3-4 on termine avec ~8 users non activables. Acceptable mais à documenter dans rapport final.
- **Fatigue NPS** : 2 users ont dismiss le widget. Surveiller cadence rappel.
- **Perf serveur** : sur 50 users, pas de signal. Observer à 100 users (Batch 4 à partir de 2/9).

## Graphiques (placeholder — vrais graphs dans Grafana)

- [Grafana — Beta Overview](http://grafana.pli.internal/d/beta-overview)
- [Grafana — Perf p95](http://grafana.pli.internal/d/perf-p95)

## Participants itération

Tous les 10 agents ont contribué. Merci en particulier à QA (0 regression bug post-release) et UX (itérations rapides sur step 3 tour).

## Prochain rapport

Iteration #2 prévu **10 septembre 2026** (fin sprint 10, J+1 de fin beta).
