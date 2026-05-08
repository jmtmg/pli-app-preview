# M5 — Kickoff · Beta publique & Soft Launch

**Phase** : M5 (semaines 23 → 24, 2 semaines)
**Démarrage** : 9 septembre 2026 (après validation Go M4 / Checkpoint 4)
**Fin cible** : 23 septembre 2026 (buffer S25 → Launch J0 = 7 oct 2026)
**Doc de référence** : [05-Roadmap.md](../../05-Roadmap.md) §3 — Phase M5
**Runbook opérationnel** : [runbook/M5-launch.md](runbook/M5-launch.md) (existant) + [M5-MONITORING-RUNBOOK.md](M5-MONITORING-RUNBOOK.md) (ce doc étendu)
**Jalon suivant** : Launch J0 = 7 octobre 2026 (S25) — annonce ProductHunt + Show HN

---

## 1. Objectif de M5

> **Ouvrir l'inscription publique sans invitation, absorber un ramp-up progressif de 500 à 1 000 nouveaux utilisateurs en 14 jours, valider le funnel de conversion en conditions réelles, et livrer M5 avec 0 incident majeur durable (< 30 min de downtime cumulé) — pour autoriser le Launch officiel en S25.**

M5 est une **phase de transition contrôlée** entre la beta privée (100 users triés) et le lancement public (ProductHunt / HN). Son rôle n'est pas d'ajouter des fonctionnalités mais de **durcir l'existant à l'échelle réelle**, de **tester le funnel d'acquisition** avec une communication maîtrisée, et de **prouver la stabilité opérationnelle 7j/7**.

À la fin de M5, le founder doit pouvoir signer le Go Launch avec :
- Infrastructure démontrée sous charge réelle
- Funnel signup → trial → paid mesuré et conforme aux hypothèses
- Aucun incident bloquant non résolu
- Astreinte 7j/7 rodée sans burnout

**M5 n'est pas un sprint feature.** C'est un sprint de stabilité, d'observabilité et de préparation au Launch.

---

## 2. Répartition de l'équipe d'agents

| Rôle | Agent | Périmètre M5 | Livrables clés |
|---|---|---|---|
| **Product Manager** | PM | Priorisation feedback, arbitrages scope, préparation Launch | [SPRINT-11-BACKLOG.md](SPRINT-11-BACKLOG.md), [M5-FEEDBACK-PLAN.md](M5-FEEDBACK-PLAN.md), [M5-COMMS-PLAN.md](M5-COMMS-PLAN.md) |
| **Tech Lead** | TL | Revues hotfixes, arbitrages techniques en incident, Go/No-Go Launch | ADR éventuels, approvals PR critiques |
| **Backend Engineer** | BE | Hotfixes, optimisations DB/API sous charge, flags d'ouverture | Patches perf, dashboards DB, rate limits configurables |
| **Frontend Engineer** | FE | Landing beta publique, in-app status, widget feedback, polish | `frontend/src/features/landing`, bannière status, widget NPS |
| **QA / Test Engineer** | QA | Tests de charge réels, monitoring synthétique, regression suite | Scénarios k6/Artillery, smoke tests cron 15 min |
| **UX Designer** | UX | Copy landing beta, onboarding tuning sur feedback, empty states | Variantes landing, micro-copy, empty/error states |
| **SRE / DevOps** | SRE | Monitoring ultra-renforcé, alerting, astreinte 7j/7, capacity | [M5-MONITORING-RUNBOOK.md](M5-MONITORING-RUNBOOK.md), [M5-ONCALL-CHECKLIST.md](M5-ONCALL-CHECKLIST.md), dashboards Grafana |
| **Security** | SEC | Hardening exposition publique, abuse, WAF, audit | [M5-SEC-CHECKLIST.md](M5-SEC-CHECKLIST.md), règles WAF/rate-limit |
| **Content / Support** | CONT | Réponses Discord/email, enrichissement KB, modération, canned responses | Articles KB nouveaux, réponses support < 4h |
| **Marketing** | MKT | Finalisation assets Launch S25, landing copy beta publique, press kit | Vidéo démo 90s, kit ProductHunt, press kit FR+EN |
| **Founder (JM)** | — | Article blog, teasers réseaux, décisions d'ouverture, Go Launch | [blog-pourquoi-pli.md](blog/blog-pourquoi-pli.md), interviews presse |

---

## 3. Découpage Sprint (2 semaines = 1 sprint)

M5 = **Sprint 11** uniquement. Organisation en deux demi-sprints pour cadencer l'ouverture.

### Demi-sprint 11a (J1-J5) — **Hardening & ouverture contrôlée**

Objectif : tout durcir avant d'ouvrir les vannes. Inscription publique activable mais **feature-flaggée**, derrière un rate limit strict.

- Landing beta publique (`pli.app`) : CTA "Essayer PLI 14 j", copy final, screenshots
- Feature flag `public_signup_enabled` (off par défaut, activation progressive)
- Rate limiting signup : 5 comptes/IP/24h, 50 comptes/heure/global (ajustable)
- Monitoring renforcé : dashboards Grafana (signup funnel, latence p95/p99, erreurs 5xx, queue sync)
- Alertes PagerDuty / Better Stack : P1 downtime, P2 erreurs > 1%, P3 latence p95 > 1s
- Widget feedback in-app : thumbs up/down + champ libre optionnel, NPS à J7
- Bannière "Beta publique" in-app (discrete, non bloquante)
- Tests de charge k6 sur staging : 500 signups/heure soutenus, 2000 signups peak
- Checklist sécurité SEC validée (WAF, bot protection, rate limits)
- Smoke tests synthétiques cron 15 min (signup test → login → sync mock)

**Owner principal** : SRE + SEC · **Support** : FE (landing), BE (rate limits, flags), QA (k6)
**Critère de sortie 11a (fin J5)** : feature flag `public_signup_enabled=true` activable ; smoke tests verts 48h consécutives ; alerting testé end-to-end sur incident simulé ; 0 vulnérabilité SEC haute ouverte.

### Demi-sprint 11b (J6-J10) — **Ramp-up public & itérations**

Objectif : ouvrir progressivement, observer, itérer, préparer le Launch.

- **J6 (mardi)** : activation flag `public_signup_enabled` à 08h00 CET, communication discrète (article blog founder, teaser LinkedIn)
- **J6-J7** : observation en temps réel, hotfixes immédiats si besoin
- **J8** : 1re itération produit sur feedback remonté (fix bugs friction majeurs, copy, empty states)
- **J9** : teaser réseaux élargi (X, Bluesky, Threads), post LinkedIn founder amplifié
- **J9-J10** : 2e itération, dernière batterie de hotfixes
- **J10 (vendredi)** : review M5, report de clôture, décision Go/No-Go Launch

En continu : astreinte informelle 7j/7 (founder), monitoring temps réel, réponse aux signalements beta, knowledge base enrichie sur friction observée.

**Owner principal** : Founder + PM · **Support** : tous les agents en mode réactif
**Critère de sortie 11b (fin J10)** : 500-1000 inscriptions ; 0 incident majeur durable (< 30 min cumulés) ; feedback ratio thumbs up/down > 4:1 ; funnel conversion trial→paid intent mesuré.

---

## 4. Définition du "done" M5

Une tâche est done si tous les critères sont respectés :

1. Code mergé sur `main` (PR avec 1 reviewer, TL obligatoire sur tout hotfix prod)
2. Déploiement prod validé par smoke tests synthétiques
3. Pas de régression détectée sur les métriques de base (latence p95, taux d'erreur)
4. Changement documenté dans `CHANGELOG.md` public et éventuellement communiqué aux beta users via widget in-app
5. Monitoring / alerting couvre la nouvelle surface (dashboard ou log pertinent)
6. Post-mortem rédigé si hotfix sur incident (même 5 lignes)

**Spécifique M5** : aucune feature nouvelle ne peut être mergée si elle ajoute un risque de régression non couvert par les tests synthétiques. Scope gelé hors hotfix.

---

## 5. Dépendances externes au démarrage M5

| Dépendance | État attendu à S23 | Action si bloqué |
|---|---|---|
| Go M4 signé par founder (Checkpoint 4) | Prérequis absolu | Décalage M5 de 2 sem max, sinon pivot scope |
| Stripe en mode live activé | Validé en M4 | Bloquant : rester en test mode impossible pour public |
| Provider email transactionnel : IP warming complet | Warm-up démarré M4 | Accepter taux inbox plus bas J1-J3, remontée progressive |
| Quota Google OAuth validé (app review) | Validé M3 | Bloquant hard |
| Quota Microsoft Graph validé | Validé M3 | Bloquant hard |
| CGV / politique conf / mentions publiées | En ligne depuis M3 | Bloquant hard : pas d'ouverture publique sans |
| Domaine `pli.app` + subdomains (`status.pli.app`, `blog.pli.app`) | En place | Config DNS vérifiée J-3 |
| Status page publique opérationnelle | Déployée J-2 | Fallback `status.pli.app` statique |
| Uptime Robot / Better Stack monitoring externe | Configuré M3, étendu M5 | Bloquant observabilité |
| Support chat Crisp (PLI Cloud) | Déployé M4 | Fallback email `support@pli.app` |

---

## 6. Cadences et rituels M5

M5 est court et sous pression, donc **cadence resserrée** par rapport aux phases précédentes :

- **Daily sync synchrone** (15 min, 9h00 CET) : point revue dashboards, incidents ouverts, priorités du jour
- **Mid-day check** (15 min, 14h00 CET) : revue métriques funnel, feedback entrant, arbitrages
- **Evening wrap** (10 min, 18h00 CET) : incidents clos, retro journalière, préparation J+1
- **Retro mid-sprint** (fin J5) : bilan hardening, décision d'ouverture J6
- **Review M5** (fin J10) : démo métriques, feedback synthèse, décision Go/No-Go Launch
- **Astreinte informelle 7j/7** : founder joignable (téléphone + Slack), PagerDuty sur incidents P1
- **PR policy renforcée** : tout merge nécessite **2 approvals** (TL + 1 autre) pour code prod pendant M5, exception hotfix critique (TL seul)

---

## 7. Risques M5 identifiés & mitigations

| Risque | Prob. | Impact | Mitigation |
|---|---|---|---|
| Pic de trafic inattendu sature infra | Moyenne | Critique | Autoscaling testé M4, rate limits en place, circuit breaker sur sync externe, communication "file d'attente" prête |
| Incident prolongé pendant astreinte seule | Moyenne | Critique | Playbook incident ultra-précis, rollback automatisable, contact TL agent backup |
| Feedback négatif viral sur un bug UX | Moyenne | Élevé | Widget feedback visible, réponse publique sous 2h, hotfix prioritaire, post-mortem public si besoin |
| Abus / inscriptions malveillantes | Élevée | Moyen | WAF Cloudflare, rate limits IP + fingerprint, vérif email obligatoire, ban rapide |
| IP email blacklistée (warm-up insuffisant) | Moyenne | Haut | Provider secondaire de secours (Postmark ↔ SendGrid), volumétrie progressive |
| Founder burnout sur 14j d'astreinte | Élevée | Élevé | Capacity réaliste, pas d'astreinte nuit sauf P1, **pause le week-end 2** si métriques vertes |
| Feedback contradictoire paralyse l'itération | Moyenne | Moyen | Priorisation fréquence × sévérité (cf. M5-FEEDBACK-PLAN), PM arbitre sous 24h |
| Quota Google/Microsoft dépassé sur ramp | Faible | Haut | Monitoring quota en temps réel, demande augmentation anticipée, throttling sync |
| Fuite de données inter-tenant révélée | Faible | Critique | Tests isolation en continu, feature flag kill switch, communication transparente |

---

## 8. Checkpoint Launch (fin M5, J10) — Critères Go/No-Go

Le founder signe le Go Launch si tous ces critères sont validés :

- [ ] 500 à 1 000 inscriptions publiques réalisées entre J6 et J10
- [ ] 0 incident P1 (downtime > 10 min) ; cumul downtime < 30 min sur 14 jours
- [ ] Funnel mesuré et conforme : taux visit→signup ≥ 5 %, signup→trial actif ≥ 60 %, trial→intent payant ≥ 15 % (survey)
- [ ] Ratio feedback thumbs up/down > 4:1
- [ ] NPS beta publique > 30 (cible 40 en survey J7)
- [ ] 0 vulnérabilité SEC haute/critique ouverte
- [ ] Aucun bug majeur (P1/P2) ouvert non résolu
- [ ] Status page verte 95 % du temps M5
- [ ] IP email : taux inbox > 95 % sur envois transactionnels
- [ ] Capacity infrastructure : **marge de 3×** le trafic moyen M5 validée par load test
- [ ] Assets Launch prêts : ProductHunt kit, "Show HN" draft, vidéo démo 90 s, posts LinkedIn programmés

Si un critère manque : décalage Launch de 1 à 2 semaines max. M5 est extensible à 4 semaines (cf. Roadmap §4.3).

---

## 9. Deltas structurels repo attendus à l'issue de M5

```
pli-app/
├── M1-KICKOFF.md
├── M2-KICKOFF.md
├── M3-KICKOFF.md
├── M4-KICKOFF.md
├── M5-KICKOFF.md                ← ce document
├── SPRINT-5-BACKLOG.md
├── SPRINT-6-BACKLOG.md
├── ...
├── SPRINT-11-BACKLOG.md         ← NEW backlog M5
├── M5-COMMS-PLAN.md             ← NEW plan communication M5
├── M5-MONITORING-RUNBOOK.md     ← NEW runbook SRE
├── M5-ONCALL-CHECKLIST.md       ← NEW astreinte founder
├── M5-FEEDBACK-PLAN.md          ← NEW collecte/priorisation
├── M5-SEC-CHECKLIST.md          ← NEW hardening exposition publique
├── M5-CLOSURE-TEMPLATE.md       ← NEW template rapport clôture / Go Launch
├── blog/
│   └── blog-pourquoi-pli.md     ← NEW article founder
├── marketing/
│   ├── social-teasers.md        ← NEW teasers LinkedIn/X/Bluesky/Threads
│   └── press-kit/               ← NEW (préparé pour Launch S25)
├── backend/
│   └── pli/
│       ├── billing/             ← UPD Stripe en mode live
│       ├── ratelimit/           ← NEW rate limiters configurables
│       └── feature_flags.py     ← UPD flag `public_signup_enabled`
├── frontend/
│   └── src/
│       ├── features/
│       │   ├── landing/         ← UPD variantes beta publique
│       │   └── feedback/        ← NEW widget thumbs + NPS
│       └── components/
│           └── BetaBanner.tsx   ← NEW bannière discrète
└── ops/
    ├── grafana/
    │   └── dashboards/
    │       ├── m5-funnel.json   ← NEW dashboard signup funnel
    │       └── m5-latency.json  ← NEW dashboard latence p95/p99
    ├── alerts/
    │   └── m5-alerts.yml        ← NEW règles alerting P1/P2/P3
    └── loadtest/
        └── k6-signup-rampup.js  ← NEW scénario k6
```

---

## 10. Prochaines actions immédiates (J1 de M5)

1. **Founder** : valider ce kickoff, finaliser article blog (relecture, SEO, intégration blog), programmer publications réseaux
2. **SRE** : déployer `M5-MONITORING-RUNBOOK.md`, créer les dashboards Grafana M5, configurer alertes PagerDuty P1/P2/P3
3. **SEC** : dérouler `M5-SEC-CHECKLIST.md`, activer WAF Cloudflare règles beta, vérifier rate limits en prod
4. **BE** : implémenter feature flag `public_signup_enabled` + rate limits configurables, smoke tests prod
5. **FE** : livrer landing beta publique (version A), widget feedback in-app, bannière "Beta publique"
6. **QA** : scripts k6 de charge, smoke tests synthétiques 15 min en prod, regression suite
7. **PM** : publier `SPRINT-11-BACKLOG.md`, cadrer cadence daily/midi/soir, ouvrir canal feedback (Discord public)
8. **UX** : relecture copy landing + empty states + messages d'erreur publics, cohérence ton "beta publique confiante mais humble"
9. **TL** : ouverture PR template "hotfix prod M5", critères approval renforcés, disponibilité astreinte backup

---

## 11. Engagements mutuels

L'équipe d'agents s'engage collectivement à :

- **Répondre à tout signalement utilisateur sous 4 h** en heures ouvrées, 12 h en week-end (via canal feedback)
- **Publier un post-mortem public** sur toute interruption de service > 10 min
- **Ne fermer aucune tâche M5 sans ticket de suivi** pour ce qui est décalé à Launch ou V1.1
- **Tenir à jour la status page** en temps réel (pas de délai >15 min sur incident déclaré)
- **Protéger le founder** : pas de décision engageante le week-end 2 si métriques vertes

---

*Kickoff établi le 8 septembre 2026 par le Tech Lead, en coordination avec PM, SRE et founder. Revalidation obligatoire au Go M4 (9 septembre 2026) avant activation du feature flag `public_signup_enabled`.*
