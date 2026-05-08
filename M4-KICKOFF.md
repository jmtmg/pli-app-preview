# M4 — Kickoff · Beta privée (100 invités)

**Phase** : M4 (semaines 19 → 22, 4 semaines)
**Démarrage** : 12 août 2026 (après validation Go M3 / Checkpoint 3)
**Fin cible** : 9 septembre 2026
**Doc de référence** : [05-Roadmap.md](../../05-Roadmap.md) §3 — Phase M4
**Jalon suivant** : Checkpoint 4 (fin S22) — Go/No-Go M5 (Beta publique)

---

## 1. Objectif de M4

> **Ouvrir une beta privée à 100 utilisateurs invités par batches de 25, mettre en place la boucle de feedback, itérer deux fois sur les frictions réelles remontées, stabiliser l'exploitation, et finaliser les assets & le support nécessaires pour basculer en beta publique.**

À la fin de M4, PLI doit démontrer sa **désirabilité et sa fiabilité sur utilisateurs réels externes** — c'est le Go/No-Go du Checkpoint 4 (S22) avant l'ouverture publique M5.

M4 est la première phase **centrée utilisateur** : le code ralentit, l'écoute accélère. Tout nouveau développement est conditionné à un signal beta, pas à l'intuition interne.

---

## 2. Répartition de l'équipe d'agents

| Rôle | Agent | Périmètre M4 | Livrables clés |
|---|---|---|---|
| **Product Manager** | PM | Pilotage backlog feedback, priorisation frequency × severity, animation beta | Backlog Sprints 9-10, template NPS, tri feedback hebdo |
| **Tech Lead** | TL | Arbitrage entre hot-fix et refactor, garde-fou dette, revues PR critiques | ADR "itération beta", code owner sur fixes majeurs |
| **Backend Engineer** | BE | Fixes backend remontés, endpoints feedback, résilience scaling | `backend/pli/**` (patches ciblés, endpoints `/feedback`, `/nps`) |
| **Frontend Engineer** | FE | Onboarding 5 étapes, formulaire NPS in-app, fixes UX friction | `frontend/src/features/{onboarding,feedback}` |
| **QA / Test Engineer** | QA | Plans de reproduction bugs beta, régression release, smoke daily staging/prod | `e2e/beta/**`, scénarios de reproduction |
| **UX Designer** | UX | Tour produit 5 écrans, copy onboarding, redesign frictions identifiées | Maquettes tour + variantes copy (doc 03) |
| **SRE / DevOps** | SRE | Monitoring renforcé, alertes temps réel, scaling horizontal Cloud | Dashboards Grafana, alertes PagerDuty/Healthchecks, runbook beta |
| **Security** | SEC | Revue endpoints feedback (PII), rate-limit invitations, anti-abuse | Checklist rate-limit, audit logs sécurité beta |
| **Content / Support** | CONT | Knowledge base FR+EN (30+ articles), réponses support, animation Discord | `docs/kb/**`, trombi Crisp, scripts canned responses |
| **Marketing** | MKT | Assets launch M5 (screenshots, vidéos, landing updates, pitch press) | `marketing/assets/**`, kit presse v1 |
| **Founder (JM)** | — | Accueil beta users en 1-to-1, arbitrages scope, acceptance Go/No-Go | 20 entretiens qualitatifs, signature Go M5 |

---

## 3. Découpage Sprint (4 semaines = 2 sprints de 2 semaines)

### Sprint 9 (S19-S20) — **Ouverture beta**

Passer du produit conforme au produit vivant entre des mains extérieures.

- Waitlist publique depuis `pli.app` (landing avec formulaire, double opt-in email)
- Mécanique d'invitation par batches de 25 (codes uniques, expiration 14 j, tracking activation)
- Onboarding optimisé : tour produit en 5 étapes (skippable, persistant), tooltips contextuels sur 3 parcours clés
- Monitoring renforcé : dashboards Grafana (perf endpoints, erreurs, usage par feature), alerting temps réel (PagerDuty / Healthchecks)
- Formulaire feedback in-app : widget NPS déclenché à J+7 d'usage + champ libre qualitatif
- Canal Discord privé beta (ou Slack privé si préférence founder) avec salons `#annonces`, `#bugs`, `#feedback`, `#feature-requests`
- Iteration #1 sur feedback : hot-fixes bugs bloquants + quick wins UX identifiés sur le 1er batch

**Owner principal** : FE (onboarding + widget) + SRE (monitoring) · **Support** : PM (grilles feedback), SEC (rate-limit invit.), CONT (animation Discord)
**Critère de sortie** : 25 premiers beta users invités, activés, avec au moins 10 retours qualitatifs triés et priorisés ; dashboards verts ; 0 incident de sécurité.

### Sprint 10 (S21-S22) — **Stabilisation & prélancement**

Consolider, itérer à nouveau, préparer l'ouverture publique.

- Iteration #2 sur feedback (agrégat des 4 batches de 25)
- Fix de tous les bugs majeurs remontés (critère sortie : 0 bloquant, ≤ 5 majeurs ouverts)
- Optimisations perf basées métriques réelles (p95 endpoints, LCP, cold-start PWA)
- Knowledge base finalisée : **30+ articles FR + EN** (setup, troubleshooting, sécurité, facturation, RGPD)
- Chat in-app (Crisp) intégré pour PLI Cloud — déclencheur post-onboarding J+3
- Préparation lancement public : screenshots haute-def, 2 vidéos produit (landing + ProductHunt), mise à jour landing `pli.app`, kit presse v1, checklist launch day

**Owner principal** : BE + FE en binôme sur fixes · **Support** : CONT (KB), MKT (assets), SRE (scaling), PM (arbitrages scope)
**Critère de sortie** : les 100 beta users ont vécu l'expérience complète, NPS calculé, rétention J30 mesurée, KB publiée, assets launch prêts, runbook M5 validé.

---

## 4. Définition du "done" M4

Une tâche est done si tous les critères sont respectés :

1. Code mergé sur `main` (PR avec 1 reviewer, TL obligatoire sur tout fix touchant auth/tenancy/billing)
2. Tests unitaires ≥ 70 % du module touché, régression ajoutée pour chaque bug remonté beta
3. Tests E2E / smoke staging verts avant déploiement prod
4. Documentation inline + KB publique mise à jour si le fix change un comportement utilisateur visible
5. Déployé sur staging → soak 24 h → prod
6. Métrique d'impact du fix mesurée post-déploiement (taux d'erreur, NPS delta, usage feature)
7. Communication beta users : changelog interne Discord à chaque release (cadence hebdo minimum)

---

## 5. Dépendances externes au démarrage M4

| Dépendance | État attendu à S19 | Action si bloqué |
|---|---|---|
| Go M3 signé par founder (audit RGPD OK, i18n, accessibilité) | Prérequis absolu | Décalage M4 de 2 sem max (buffer roadmap) |
| 100-200 candidats waitlist qualifiés | Constitués dès S17 en //, relance M3 | Abaisser seuil à 50 users invités + prolonger la phase d'1 sem |
| Crisp (ou équivalent) compte activé + snippet installable | Validé S18 | Fallback : formulaire contact + email support manuel |
| Infra Cloud capable d'absorber 100+ users simultanés | Load test réalisé S18 | Scaling vertical d'urgence + feature flag de délestage |
| Provider email transactionnel : réputation IP warmée | M2 | Chauffe IP secondaire déclenchée |
| Discord / Slack workspace privé créé | S18 | — |
| CGV / politique de conf à jour avec mention beta | S18 | Bloquant soft : ouvrir beta en mode "preview" sans clause commerciale |

---

## 6. Cadences et rituels

- **Daily async** (10 min, Discord) : une ligne par agent — fait hier, fait aujourd'hui, blockers ; **+ veille feedback** (3 items remontés la veille)
- **Beta triage** (3× / semaine, 20 min) : PM + TL + CONT passent en revue les nouveaux tickets Discord / NPS, décident hot-fix vs backlog vs wontfix
- **Founder calls beta** (2× / semaine, 30 min) : 1-to-1 avec un beta user, notes partagées
- **Mid-sprint sync** (milieu S19 et S21) : 30 min synchrones, réajustement scope
- **Review de sprint** (fin S20, S22) : démo au founder + métriques NPS/rétention/bugs, feedback
- **Retro** : focus "qu'a-t-on appris des utilisateurs", pas seulement "process"
- **Planning sprint suivant** : enchaîné sur la retro
- **PR policy** : 1 approval minimum, TL obligatoire sur auth/billing/tenancy, SEC obligatoire sur endpoints PII (feedback, NPS)
- **Release cadence** : hebdo minimum (vendredi matin), patch intermédiaire autorisé pour bug bloquant

---

## 7. Risques M4 identifiés & mitigations

| Risque | Prob. | Impact | Mitigation |
|---|---|---|---|
| Feedback contradictoire / trop divergent | Haute | Moyen | Grille **frequency × severity**, refus poli des demandes < 3 occurrences, transparence publique sur les arbitrages |
| Perf se dégrade à 50+ users simultanés Cloud | Moyenne | Haut | Load test pré-M4, scaling horizontal prêt (Docker swarm / Fly.io autoscale), alertes à 70 % CPU/mem, feature flag de délestage |
| Biais d'échantillon (waitlist = early adopters techno) | Haute | Moyen | Inviter batches diversifiés (25 Gmail-only, 25 Microsoft-only, 25 mixtes, 25 non-tech via réseau JMJ), tracker segment par segment |
| Emails transactionnels tombent en spam chez un provider | Moyenne | Haut | Monitoring IP reputation (PostmarkApp), fallback provider chauffé, DMARC strict activé |
| Bug critique en beta sans test de régression | Moyenne | Haut | Toute résolution d'un bug beta exige un test de régression (règle DoD n°2) |
| Dérive scope "nouvelle feature" en pleine beta | Haute | Moyen | PM gèle le backlog features — seuls **fix + UX friction** sont autorisés en M4, toute feature nouvelle va en backlog post-launch |
| Fuite de PII via le formulaire feedback | Faible | Critique | Endpoint feedback: rate-limit, pas de log PII brut, anonymisation avant stockage, revue SEC obligatoire |
| Founder débordé par 1-to-1 + scope | Haute | Haut | Plafond 2 calls beta / semaine, CONT prend le relais sur le support quotidien |
| Crisp / chat intégré non-conforme RGPD par défaut | Moyenne | Haut | Configurer rétention 90 j max, localisation UE, opt-in explicite utilisateur |

---

## 8. Checkpoint fin M4 (S22) — Critères Go/No-Go M5

Le founder signe le Go M5 si **tous** ces critères sont validés :

- [ ] 100 beta users invités, **≥ 60 activés** (onboarding terminé, ≥ 1 compte mail connecté)
- [ ] **NPS > 40** sur au moins 30 répondants (score vérifiable statistiquement)
- [ ] **Rétention J30 > 50 %** sur le 1er batch (S19)
- [ ] **0 bug bloquant** ouvert, **< 5 bugs majeurs** ouverts
- [ ] **Taux de conversion beta → paying intent > 20 %** (via survey "achèteriez-vous si on ouvre la commercialisation demain ?")
- [ ] Aucun incident de sécurité ouvert, aucune vulnérabilité critique non patchée
- [ ] Performance stable : p95 endpoint `/conversations` < 400 ms, recherche < 300 ms, LCP < 2,5 s à 50 users simultanés
- [ ] Knowledge base ≥ 30 articles FR + EN publiés et consultables sans login
- [ ] Runbook M5 rédigé et validé (astreinte 7j/7 2 semaines)
- [ ] Assets launch prêts : 2 vidéos produit, 10 screenshots haute-def, kit presse, landing `pli.app` à jour
- [ ] Au moins **5 verbatims positifs exploitables** (autorisés par les beta users) pour la communication M5

Si un critère manque : décalage de 2 semaines maximum. Si NPS < 40 ou rétention < 40 %, la roadmap prévoit un **pivot possible** sur positionnement / pricing / scope — pas un simple délai.

---

## 9. Deltas structurels repo attendus à l'issue de M4

```
pli-app/
├── M1-KICKOFF.md
├── M2-KICKOFF.md
├── M3-KICKOFF.md
├── M4-KICKOFF.md                 ← ce document
├── SPRINT-9-BACKLOG.md           ← backlog ouverture beta
├── SPRINT-10-BACKLOG.md          ← backlog stabilisation
├── backend/
│   ├── pli/
│   │   ├── api/
│   │   │   ├── feedback.py       ← NEW endpoint NPS + qualitatif (rate-limit, anonymisation)
│   │   │   ├── invitations.py    ← NEW codes invit. batches de 25
│   │   │   └── waitlist.py       ← NEW formulaire pli.app
│   │   ├── beta/
│   │   │   ├── batches.py        ← NEW logique batches 25
│   │   │   ├── activation.py     ← NEW tracking activation
│   │   │   └── nps.py            ← NEW calcul agrégé
│   │   └── observability/
│   │       ├── metrics.py        ← UPD métriques beta (activation, NPS, rétention)
│   │       └── alerts.py         ← NEW règles alerting prod
│   └── tests/
│       ├── test_invitations.py
│       ├── test_feedback.py
│       └── test_nps_aggregation.py
├── frontend/
│   └── src/
│       ├── features/
│       │   ├── onboarding/       ← UPD tour produit 5 étapes
│       │   ├── feedback/         ← NEW widget NPS + formulaire libre
│       │   └── invitations/      ← NEW saisie code invit.
│       └── pages/
│           ├── waitlist.tsx      ← NEW route publique
│           └── invited.tsx       ← NEW redemption code
├── infra/
│   ├── grafana/
│   │   └── dashboards/
│   │       ├── beta-usage.json   ← NEW
│   │       ├── perf-p95.json     ← NEW
│   │       └── errors.json       ← UPD
│   └── alerts/
│       └── beta-rules.yaml       ← NEW seuils PagerDuty
├── docs/
│   └── kb/                       ← NEW 30+ articles FR/EN
│       ├── fr/
│       │   ├── getting-started.md
│       │   ├── connecter-gmail.md
│       │   ├── connecter-microsoft.md
│       │   ├── facturation.md
│       │   ├── rgpd-export.md
│       │   └── …
│       └── en/
│           └── …
├── marketing/
│   └── assets/
│       ├── screenshots/          ← NEW 10+ haute-def
│       ├── videos/               ← NEW 2 vidéos (landing, ProductHunt)
│       └── press-kit/            ← NEW kit presse v1
└── runbook/
    └── M5-launch.md              ← NEW astreinte & procédures
```

---

## 10. Prochaines actions immédiates (J1 de M4)

1. **Founder** : valider ce kickoff, confirmer Go M3, signer l'ouverture officielle du Sprint 9 ; arrêter la liste des 100 invités (4 batches × 25, segments diversifiés)
2. **PM** : publier `SPRINT-9-BACKLOG.md`, cadrer la grille de triage feedback (frequency × severity), caler le template NPS (7 j post-activation)
3. **SRE** : finaliser dashboards Grafana + règles d'alertes, lancer un load test 100 users simultanés en staging avant S19
4. **SEC** : livrer la checklist rate-limit invitations + feedback, valider l'anonymisation PII et la conformité RGPD du chat Crisp
5. **CONT** : ouvrir le workspace Discord privé, publier la charte beta, préparer les 10 premiers articles KB prioritaires (setup + dépannage)
6. **FE** : scaffolder les routes `/waitlist`, `/invited`, widget NPS, tour onboarding 5 étapes (intégrer maquettes UX)
7. **BE** : implémenter endpoints `invitations`, `waitlist`, `feedback` + tests ; brancher métriques d'activation
8. **UX** : livrer maquettes tour produit (5 écrans) + widget NPS avant J+3
9. **MKT** : démarrer shooting screenshots + planification 2 vidéos (storyboards avant S21)
10. **QA** : préparer le scénario smoke daily (signup → onboarding → sync → recherche → envoi → feedback), script activation batch

---

*Kickoff établi le 22 avril 2026 par le Tech Lead, en coordination avec PM, Founder, CONT et MKT. Revalidation obligatoire au Go M3 (12 août 2026) avant démarrage effectif.*
