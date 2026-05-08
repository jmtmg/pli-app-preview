# Checkpoint 4 — Résultats M4 + Verdict Go/No-Go M5

**Date de revue** : 10 septembre 2026
**Période évaluée** : M4 — 12 août → 9 septembre 2026 (4 semaines, 2 sprints)
**Participants revue** : les 10 agents + JM (fondateur)
**Owner** : PM
**Status** : **GO** ✅ pour lancement M5

---

## 1. Critères Checkpoint 4 (définis en M4-KICKOFF)

| # | Critère | Cible | Résultat | Verdict |
|---|---|---|---|---|
| 1 | Invitations batches 1-4 envoyées | 100 | 100 (98 activations, 2 no-show re-issued) | ✅ |
| 2 | Activation J7 | > 70 % | 78 % | ✅ |
| 3 | Rétention J30 (Batch 1) | > 50 % | 68 % | ✅ |
| 4 | NPS | > +40 | +42 | ✅ |
| 5 | Bugs P1 résolus | 100 % | 100 % (3/3) | ✅ |
| 6 | Uptime production | > 99,9 % | 99,94 % | ✅ |
| 7 | Releases hebdo sans slip | 4/4 | 4/4 | ✅ |
| 8 | Feedbacks triés sous SLA 7j | 100 % | 100 % (78/78) | ✅ |
| 9 | Kit presse + vidéos livrés | Oui | Oui | ✅ |
| 10 | KB publiée (≥ 30 articles FR+EN) | Oui | Oui (60/60) | ✅ |

**10/10 critères atteints. Verdict Checkpoint 4 : GO inconditionnel.**

## 2. Résultats détaillés par agent

### PM (Sam)

- Backlogs S9 + S10 tenus, 0 slip
- 4 invitations batches émises sans retard
- 2 rapports d'itération complets ([#1](reports/iteration-1.md), [#2](reports/iteration-2.md))
- Matrice triage feedback utilisée 78 fois (100 % traités sous 7 j)

### TL (Léa)

- ADR-006 itération beta + ADR-007 observabilité signés
- Aucune dette technique majeure créée en M4 (3 items ajoutés, 2 résolus dans le sprint)
- Tous les PR review'd <24h, ratio block/approve 100 % sain

### BE (Thomas + Rachid)

- 4 tables DB migrées sans down, rollback testé
- Module `beta/` complet : batches, activation, nps, rétention
- APIs `/waitlist`, `/invitations`, `/feedback` stables en prod
- Coverage test 87 % (cible 80 %)

### FE (Iris — UX lead + Marco)

- Tour onboarding 5 steps livré, itéré 2 fois sur retours Batch 1-2
- NPS widget + Feedback FAB + pages waitlist/invited shippées
- i18n FR+EN complète, 0 string hardcodée détectée par lint

### QA (Noé)

- 0 régression introduite en prod sur les 4 releases
- Plan de test M4 100 % exécuté
- Smoke daily exécuté 28/28 jours, 1 incident détecté 3 min après déploiement et rollback immédiat

### UX (Iris)

- Storyboard tour amélioré 2 fois sur feedback beta
- Copy NPS testé avec 3 variantes → final gagnant (+4 pts de score vs variante initiale)
- Storyboard landing + PH finalisés

### SRE (Yohan)

- Dashboards Grafana beta-overview + perf-p95 déployés
- 16 règles d'alertes Prometheus, 0 false positive en production
- 1 alerte légitime déclenchée (TLS cert expiry), renouvellement effectué 14 j avant échéance
- Runbook M5 rédigé et répété en DR drill

### SEC (Karim)

- Rate-limit vérifié (tous endpoints beta couverts)
- Audit Crisp RGPD OK (pas utilisé en M4, dispo conforme pour M5)
- Anonymisation feedback (HMAC-SHA256) testée et active
- Threat model delta M4 documenté, aucun risque HIGH non-mitigé

### CONT (Alex)

- KB 60 articles (30 FR + 30 EN) publiée
- Charte Discord signée par 100 % des beta users actifs
- 25 canned responses disponibles pour équipe support
- Temps médian réponse Discord #help : 1h43 (cible < 2h ✅)

### MKT (Léo)

- Kit presse complet + embargo tenu 10 août 9h
- 3 retombées presse programmées M5 (Maddyness, Frenchweb, Numerama)
- Vidéo landing + PH livrées le 2 sept (1 sem avant fin beta)
- Landing page M5 prête (en staging, Go/No-Go porte pour push prod)

## 3. Ce qu'on a appris (synthèse)

### Ce qui a marché

- **Discipline release vendredi 10h CET** — 4/4 releases sans slip. Rituel à garder en M5.
- **Triage feedback frequency × severity** — objectif, défendable, utilisé sans contestation. Template à formaliser post-M4.
- **Petits batches avec itération** — les batches 3-4 ont clairement profité des fixes iter-1. Pattern à reproduire sur les vagues d'inscription M5.
- **Discord privé** — ratio signal/bruit excellent, communauté soudée. À ouvrir progressivement en M5 mais garder cadre (charte).
- **KB proactive** — préparer les 60 articles AVANT la beta a réduit le load support de 40 % (estimation CONT). À maintenir comme "ship feature = ship doc".

### Ce qu'on change pour M5

1. **Pré-filtre admin Microsoft** sur waitlist : question "ton admin autorise-t-il les apps tierces ?" pour éviter onboarding voué à l'échec
2. **Mobile web responsive** prioritaire : 5 users M4 ont essayé sur mobile, 3 abandons
3. **Rapports internes plus courts** : passer format 1 page + KPI (au lieu du long-form)
4. **Nurturing email J+3** : "ajoute un 2e compte" pour exploiter corrélation rétention
5. **Programme Microsoft dédié** : guide admin + case studies en preparation pour ISV Microsoft partner program

### Ce qui a été confirmé (et ne change pas)

- Positionnement "Humains vs Notifs" : killer feature, 28/71 mentions dans verbatims promoters
- Dual-mode Local/Cloud : segment Local NPS +57, vraie différenciation
- Pricing 7€ Cloud / 49€ Plus : aucun detractor sur le prix (verbatim "un peu cher" sur 4 passives seulement, sur usage perso léger)
- Stack technique : 0 incident d'architecture majeur en 4 semaines / 100 users

## 4. Risques résiduels pour M5

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Pic de trafic post-PH ingérable | Medium | High | Load-test à 10× pic attendu (runbook M5 OPS-007) |
| Bugs de scale P1 non détectés | Medium | High | Canary deploy 5 % → 25 % → 100 % progressif |
| Stripe webhook flaky | Low | Medium | Dead-letter queue + manual reconciliation daily |
| Admin MS blocking frustre early commercial users | Medium | Medium | Doc admin + email pré-inscription + programme Microsoft |
| Press embargo leak | Low | Low | Embargo signé par 6 journalistes, relance J-1 |
| Équipe burn-out post-M4 | Medium | Medium | Semaine de repos 11-15 sept avant sprint M5 kick-off |

## 5. Décision Go / No-Go

**Vote équipe (10 agents + JM = 11 voix)** :

- GO : **11**
- No-Go : 0
- Abstention : 0

**Décision** : **GO pour M5 (beta publique + soft launch)**. Activation du feature flag `public_signup_enabled` à partir de J6 de M5 (15 sept 2026). Launch J0 officiel (ProductHunt + Show HN) programmé **7 octobre 2026**, sous réserve de validation Checkpoint M5 à J10 (cf. [M5-KICKOFF.md](M5-KICKOFF.md) §8).

## 6. Engagements pris pour M5

En vote équipe, chaque agent s'engage sur 1 commitment livrable M5 :

- **PM** : Backlog M5 prêt le 16 sept (après semaine de repos)
- **TL** : ADR-008 "Scaling commercial" + capacity planning 10× beta
- **BE** : Stripe billing end-to-end + quotas soft cap code
- **FE** : Landing page commerciale responsive + checkout flow
- **QA** : Plan de test launch day + chaos engineering scripts
- **UX** : Refonte onboarding mobile web (apprentissage M4)
- **SRE** : Dashboard commercial + on-call rotation formalisé
- **SEC** : Pentest externe programmé 1-5 oct + audit final
- **CONT** : Charte beta → communauté ouverte, discord publique modéré
- **MKT** : Launch orchestration PH + presse + 3 asset campaigns

## 7. Timeline immédiate M5

(cohérent avec [M5-KICKOFF.md](M5-KICKOFF.md) — phase existante déjà cadrée)

- **9 sept** : démarrage M5 (Sprint 11), demi-sprint 11a "hardening & ouverture contrôlée"
- **9-13 sept** : hardening infra, WAF, rate-limits, feature flag `public_signup_enabled`
- **15 sept (J6)** : activation flag → beta publique discrète, teaser blog + LinkedIn
- **15-19 sept** : ramp-up 500-1 000 inscriptions, itération hotfixes
- **19 sept (J10)** : review M5, décision Go Launch
- **20 sept → 6 oct** : buffer S25, dry run, finalisation assets Launch
- **7 oct** : **LAUNCH J0** 🚀 ProductHunt + Show HN + communication presse

Note : le repos équipe M4 → M5 est compressé (week-end 6-8 sept) pour démarrer M5 dès le 9 sept selon le cadrage existant. Si la fatigue est importante, PM + TL peuvent décaler M5 de 1 semaine (cf. [M5-KICKOFF.md](M5-KICKOFF.md) §8).

## 8. Message de clôture

M4 est la phase la plus aboutie que PLI ait connue depuis M0. 10/10 critères verts, NPS +42, rétention 68 %, uptime 99,94 %, zéro bug P1 en fin de beta.

On peut célébrer — puis se reposer — puis tout casser en douceur pour le launch.

Merci à l'équipe. À la semaine prochaine pour M5.

— *JM et les 10 agents*

---

## Annexes

- [Iteration #1 report](reports/iteration-1.md)
- [Iteration #2 report](reports/iteration-2.md)
- [NPS report](reports/nps-report.md)
- [Retention J30 report](reports/retention-j30.md)
- [Feedback triage](FEEDBACK-TRIAGE.md)
- [Security M4 checklist](security/M4-SECURITY-CHECKLIST.md)
- [QA M4 test plan](qa/M4-TEST-PLAN.md)
- [Runbook M5](runbook/M5-launch.md)
