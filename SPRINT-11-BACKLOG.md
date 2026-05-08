# Sprint 11 (S23-S24) — Beta publique & Ramp-up · Backlog

**Phase** : M5 · **Durée** : 2 semaines · **Démarrage** : 9 septembre 2026 · **Fin** : 23 septembre 2026
**Objectif sprint** : Durcir l'existant pour exposition publique, ouvrir progressivement l'inscription sans invitation, atteindre 500-1000 nouveaux users avec 0 incident majeur durable, valider le funnel de conversion et préparer le Launch S25.
**Critère de sortie** : tous les critères Go Launch du Checkpoint 4 (cf. M5-KICKOFF.md §8) validés.

> **⚠️ Integration freeze — 2026-08-26 (J0 − 6 semaines)**
> Ce sprint s'exécute **après** l'integration freeze (cf. ordre de mission 2026-04-22, décision D4).
> Sprint 11 démarre 14 jours après la coupe de `release-v1`. Aucun scope nouveau en dehors des hotfix P0/P1 et des patches sécu CVE Critical/High.
> Détails freeze : voir `docs/sprint-planning/sprint-11-planning.md` §2 et `docs/adr/0008-integration-freeze.md`.

---

## 1. User stories

### US-11.1 — Feature flag `public_signup_enabled` — **BE + TL**

**En tant qu'** équipe
**Nous voulons** pouvoir ouvrir ou fermer l'inscription publique en un clic
**Afin de** maîtriser le ramp-up et couper en cas d'incident

**Critères d'acceptance** :
- Flag stocké en DB (table `feature_flags`, valeur typed `boolean`), rechargé sans redeploy
- Commande admin CLI `pli flags set public_signup_enabled true|false` + audit log
- Endpoint `POST /auth/signup` renvoie 403 "Inscription bientôt ouverte" si flag off (page d'attente)
- Frontend : landing affiche CTA "S'inscrire" si flag on, formulaire waitlist si flag off
- Test E2E flag on → inscription OK ; flag off → page d'attente
- Propagation flag en < 30 s (polling ou SSE)

**Effort estimé** : 1 j · **Priorité** : P0 (prérequis ouverture)

---

### US-11.2 — Rate limits publics configurables — **BE + SEC**

**En tant que** SRE / SEC
**Je veux** des rate limits agressifs mais tunables sans redeploy
**Afin de** protéger l'infra et prévenir l'abus

**Critères d'acceptance** :
- Rate limiter Redis token bucket, clés par IP, par fingerprint, par user
- Règles par défaut M5 :
  - `/auth/signup` : 5 IP/24h, 50/heure/global (ajustable)
  - `/auth/login` : 10 IP/15min
  - `/auth/password-reset/request` : 3 IP/heure
  - API authenticated : 100 req/min/user
- Config DB `rate_limits` rechargée à chaud (TTL 30 s)
- Headers standards `X-RateLimit-*` + `Retry-After`
- Dashboard Grafana : hits vs limits, top offenders
- Alerte si > 100 × limite dépassée sur 5 min (possible attaque)

**Effort estimé** : 1,5 j · **Priorité** : P0

---

### US-11.3 — Landing beta publique — **FE + UX + Founder**

**En tant que** visiteur
**Je veux** comprendre PLI en 30 secondes et savoir si la beta est ouverte
**Afin de** décider d'essayer

**Critères d'acceptance** :
- Route `/` : landing publique, hero + 3 sections (problème, solution, différenciation Local)
- Bannière "Beta publique · 14 j gratuits, sans CB" si flag on, "Inscription bientôt ouverte" sinon
- CTA principal : "Essayer PLI 14 j" (vert-accent)
- Screenshots responsives (mobile first), animations sobres (Framer Motion)
- SEO : title/meta/OG, schema.org, sitemap.xml, robots.txt
- Perf : LCP < 1.8 s, CLS < 0.05, bundle < 120 Ko gzipped
- Accessibilité : Lighthouse > 95
- Copy validé par UX + founder (ton : confiant, humble, pas de hype)
- Version FR + EN via i18n existant (M3)

**Effort estimé** : 2 j · **Priorité** : P0

---

### US-11.4 — Widget feedback in-app (thumbs + NPS) — **FE + BE + PM**

**En tant qu'** utilisateur beta
**Je veux** signaler rapidement si quelque chose est bien ou pas
**Afin d'** aider l'équipe à améliorer sans quitter l'app

**Critères d'acceptance** :
- Bouton flottant discret bas-droit, icône 👍/👎 neutre par défaut
- Click ouvre sheet : pouce haut/bas + champ texte optionnel (max 500 car.) + screenshot opt-in
- Enregistrement : `feedback` table (user_id, sentiment, text, url, user_agent, viewport, created_at)
- NPS survey modal à J7 post-signup (1 seule fois, pas invasif)
- Dashboard interne `/admin/feedback` : ratio up/down, stream temps réel, tags auto
- Export CSV pour analyse
- Message confirmation "Merci, reçu ✓" + close auto 2 s
- Respect préférence "ne plus afficher" sauvée par user

**Effort estimé** : 2 j · **Priorité** : P0

---

### US-11.5 — Bannière "Beta publique" in-app — **FE**

**En tant qu'** utilisateur
**Je veux** savoir que je suis sur une beta
**Afin d'** ajuster mes attentes et signaler les bugs avec indulgence

**Critères d'acceptance** :
- Bandeau haut non bloquant, couleur accent discrète, texte "Beta publique — merci de nous aider à améliorer PLI"
- Lien "Signaler un problème" → ouvre widget feedback
- Dismissable, persistant dans préférences user
- Ne s'affiche plus après Launch (feature flag `show_beta_banner`)

**Effort estimé** : 0,5 j · **Priorité** : P1

---

### US-11.6 — Dashboards Grafana M5 — **SRE**

**En tant que** SRE / Founder
**Je veux** voir en un clin d'œil la santé et le funnel M5
**Afin de** piloter le ramp-up et réagir vite

**Critères d'acceptance** :
- Dashboard `m5-funnel.json` :
  - Compteur signups / heure et total M5
  - Funnel visit → signup → email verified → login → 1er compte connecté → trial actif
  - Taux de conversion par étape, trend vs J-1
- Dashboard `m5-latency.json` :
  - Latence p50 / p95 / p99 par endpoint critique (signup, login, list conv, sync, search)
  - Erreurs 5xx, 4xx (split), queue sync backlog
- Dashboard `m5-infra.json` :
  - CPU, mémoire, DB connexions, replicas alive, IOPS
  - Quota Google / Microsoft en temps réel (barres colorées)
- Dashboards partagés publiquement en read-only pour transparence (optionnel, décision founder)

**Effort estimé** : 1,5 j · **Priorité** : P0

---

### US-11.7 — Alerting P1/P2/P3 — **SRE + SEC**

**En tant que** SRE en astreinte
**Je veux** être alerté·e rapidement sur les bons seuils
**Afin d'** intervenir avant dégradation ressentie utilisateur

**Critères d'acceptance** :
- Règles alerting définies dans `ops/alerts/m5-alerts.yml` :
  - **P1 (SMS + appel)** : downtime > 2 min, erreur 5xx > 5 % sur 5 min, DB down, webhook Stripe en erreur > 10 %
  - **P2 (Slack + email)** : latence p95 > 1 s sur 10 min, erreurs > 1 % sur 10 min, queue sync > 500
  - **P3 (Slack)** : latence p95 > 500 ms sur 15 min, erreur inbox email > 5 %, rate limit hit anormal
- PagerDuty (ou Better Stack On-Call) configuré, escalation : Founder → 10 min → agent TL backup
- Test d'alerte simulé (incident chaos : kill 1 replica) validé avant ouverture flag
- Runbook lié à chaque alerte : cf. `M5-MONITORING-RUNBOOK.md`

**Effort estimé** : 1 j · **Priorité** : P0

---

### US-11.8 — Tests de charge k6 — **QA + SRE**

**En tant qu'** équipe
**Nous voulons** prouver que l'infra tient 3× le trafic M5 anticipé
**Afin de** partir sereins au Launch

**Critères d'acceptance** :
- Scénario `k6-signup-rampup.js` : 0 → 500 signups/heure en 30 min, plateau 1h, 2000 peak 15 min
- Scénario `k6-browse-typical.js` : 200 VUs actifs (liste, conv, recherche)
- Exécution sur staging ISO-prod (même specs DB)
- Critères de succès : p95 < 1 s, p99 < 2 s, 0 erreur > 500, sync queue drain < 30 s après peak
- Rapport publié dans `ops/loadtest/reports/`
- Si échec : ticket P0 optimisation avant ouverture

**Effort estimé** : 1,5 j · **Priorité** : P0

---

### US-11.9 — Smoke tests synthétiques prod — **QA**

**En tant qu'** équipe
**Nous voulons** détecter une panne prod en < 15 min
**Afin de** ne pas dépendre du signalement utilisateur

**Critères d'acceptance** :
- Cron 15 min sur Better Stack (ou GitHub Actions) : scénario E2E "signup test user → vérif email → login → lecture inbox mock → signal → cleanup"
- Compte test dédié (`synthetic-m5@pli.app`), quota isolé, cleanup auto
- Alerte P1 si 2 échecs consécutifs
- Endpoints `/health` (liveness) et `/ready` (readiness avec DB + quota) indépendants
- Status page alimentée par ces résultats

**Effort estimé** : 1 j · **Priorité** : P0

---

### US-11.10 — Hardening SEC exposition publique — **SEC + SRE**

**En tant que** SEC
**Je veux** couvrir les risques d'abus spécifiques à l'exposition publique
**Afin de** prévenir attaques et usages malicieux

**Critères d'acceptance** :
- WAF Cloudflare : règles OWASP core activées, règle "bot fight" en mode challenge, geo-block pays non ciblés (configurable)
- Rate limits au niveau edge (Cloudflare) en sus des rate limits app
- CAPTCHA Cloudflare Turnstile sur `/auth/signup` et `/auth/password-reset/request`
- Honeypot field anti-bot sur formulaires
- Vérif email obligatoire avant usage fonctionnel (déjà en place M2, durci ici)
- Ban rapide : endpoint admin `POST /admin/ban` (IP + email pattern)
- Audit logs exhaustifs sur endpoints sensibles (auth, billing, admin)
- Revue Checklist SEC `M5-SEC-CHECKLIST.md` cochée à 100 % avant flag on

**Effort estimé** : 1,5 j · **Priorité** : P0

---

### US-11.11 — Status page publique — **SRE**

**En tant qu'** utilisateur
**Je veux** voir l'état de PLI en temps réel si j'ai un doute
**Afin de** ne pas perdre confiance sur un incident ponctuel

**Critères d'acceptance** :
- `status.pli.app` avec provider (Better Stack Status, Statuspage, ou HTML statique auto-généré)
- Composants : Web app, API, Sync Gmail, Sync Microsoft, Paiement, Email transactionnel
- Historique incidents 90 j, uptime 30 j par composant
- Incidents déclarables manuellement par founder en < 3 min
- Subscribe email + RSS pour utilisateurs
- Lien visible dans footer app et page erreur

**Effort estimé** : 0,5 j · **Priorité** : P1

---

### US-11.12 — Canal feedback Discord public — **PM + Founder**

**En tant qu'** utilisateur beta
**Je veux** échanger avec l'équipe et les autres users
**Afin de** me sentir écouté·e et découvrir des astuces

**Critères d'acceptance** :
- Serveur Discord `pli.app/discord` ouvert, salons : #annonces, #bugs, #feedback, #feature-requests, #off-topic
- Règles de modération claires, lien CGU
- Réponse d'un agent sous 4 h en heures ouvrées (PM ou founder)
- Lien dans widget feedback et bannière beta
- Bot welcome + bot auto-cross-post des annonces blog

**Effort estimé** : 0,5 j · **Priorité** : P1

---

### US-11.13 — Itération #1 sur feedback (J8) — **Tous**

**En tant qu'** équipe
**Nous voulons** corriger rapidement les frictions remontées
**Afin de** montrer notre réactivité et améliorer la rétention

**Critères d'acceptance** :
- J7 soir : revue feedback (cf. M5-FEEDBACK-PLAN), priorisation par fréquence × sévérité
- J8 : top 3-5 issues traitées (bug, copy, UX) et déployées en prod
- Communication : changelog public + post Discord "ce qu'on a amélioré aujourd'hui"
- 0 régression introduite (vérifiée par smoke tests)

**Effort estimé** : 1 j · **Priorité** : P0

---

### US-11.14 — Itération #2 sur feedback (J10) — **Tous**

**En tant qu'** équipe
**Nous voulons** une dernière passe avant Launch

**Critères d'acceptance** :
- J9 soir : revue feedback cumulée
- J10 matin : top 3 issues traitées
- J10 après-midi : freeze code, focus check Launch
- Changelog consolidé publié

**Effort estimé** : 0,5 j · **Priorité** : P1

---

### US-11.15 — Rapport de clôture M5 / Go Launch — **PM + Founder + TL**

**En tant que** founder
**Je veux** une synthèse claire pour signer Go / No-Go Launch
**Afin de** ne pas prendre la décision à chaud

**Critères d'acceptance** :
- Rempli depuis template `M5-CLOSURE-TEMPLATE.md`
- Sections : métriques atteintes vs cibles, incidents et post-mortems, feedback synthèse, bugs non résolus, capacity réelle, décision Launch
- Signatures : PM, TL, SRE, SEC, Founder
- Archivé dans `pli-app/closures/M5.md`

**Effort estimé** : 0,5 j · **Priorité** : P0

---

## 2. Plan des 10 jours ouvrés

**Jalons hors sprint (rappel chronologique) :**

| Date | Jalon | Responsable |
|---|---|---|
| **Mer 26 août 2026** | **Integration freeze · Gel `main` · Cut branche `release-v1`** | TL + direction |
| Mer 26 août → Mar 8 sept | Hardening post-freeze sur `release-v1` : hotfix P0/P1 + CVE Critical/High uniquement | Tous |
| **Mer 9 sept 2026** | **J1 Sprint 11 — démarrage Beta publique** | M5 |
| Mar 22 sept | J10 Sprint 11 — Go/No-Go Launch | Tous |
| Mer 7 oct 2026 | **J0 Launch** (S25) | Founder + Tous |

**Sprint 11 (Beta publique) :**

| Jour | Date (2026) | Focus principal | Ownership |
|---|---|---|---|
| J1 | Mer 9 sept | Kickoff, déploiement runbook SRE, alertes P1/P2/P3, WAF Cloudflare | SRE, SEC |
| J2 | Jeu 10 sept | Feature flag + rate limits + bannière beta + landing FR/EN | BE, FE, UX |
| J3 | Ven 11 sept | Dashboards Grafana M5, smoke tests cron, widget feedback (BE API) | SRE, QA, BE |
| J4 | Lun 14 sept | Widget feedback (FE), status page publique, Discord public | FE, PM, SRE |
| J5 | Mar 15 sept | **Tests de charge k6**, Checkpoint 11a (Go/No-Go ouverture) | QA, SRE + tous |
| J6 | **Mer 16 sept** | **Activation flag `public_signup_enabled=true` 08h00 CET** + article blog + teaser LinkedIn | Founder + Tous en réactif |
| J7 | Jeu 17 sept | Observation, hotfixes, 1re NPS à J+1 des early signers | Tous |
| J8 | Ven 18 sept | **Itération #1** : top 3-5 issues résolues | Tous |
| — | Sam-Dim 19-20 | Astreinte P1 uniquement, pause légère si vert | Founder + PagerDuty |
| J9 | Lun 21 sept | Teaser élargi X/Bluesky/Threads, observation ramp-up | Founder, PM |
| J10 | Mar 22 sept | **Itération #2**, freeze, rapport clôture, **Go/No-Go Launch** | Tous |
| — | Mer 23 sept | Fin M5, préparation finale Launch S25 (non-code) | Tous |

---

## 3. Definition of Done Sprint 11

- [ ] Toutes les US P0 en `completed`
- [ ] Flag `public_signup_enabled` activable en prod, testé on/off
- [ ] Rate limits opérationnels, dashboard hits visible
- [ ] Landing beta publique live en FR + EN
- [ ] Widget feedback collecte des entrées (min 50 feedbacks cumulés en M5)
- [ ] 3 dashboards Grafana M5 en place
- [ ] Alerting P1/P2/P3 testé en chaos et validé
- [ ] Tests de charge réussis (3× capacity validée)
- [ ] Smoke tests synthétiques verts 48h avant ouverture
- [ ] Status page publique live
- [ ] Canal Discord actif, modération opérationnelle
- [ ] WAF + CAPTCHA + honeypot en place
- [ ] 500-1000 inscriptions publiques réalisées
- [ ] 0 P1 non résolu, < 5 P2 ouverts au J10
- [ ] 2 itérations feedback déployées avec changelog public
- [ ] Rapport de clôture `closures/M5.md` signé

---

## 4. Hors scope (reporté V1.1 ou post-Launch)

- Apps natives iOS / Android (V1.2)
- Desktop natif Tauri (V1.2)
- Langues additionnelles ES/DE (V1.2 si traction)
- IA assistant / suggestions réponses (V2)
- Team / collaboration (V3)
- SSO / audit logs Enterprise (V3)
- Nouvelles intégrations provider mail (hors Gmail / Microsoft)
- Refactor backend perf significatif (hors hotfix)
- Nouvelle offre tarifaire (hors paliers Plus existants)

---

## 5. Dépendances inter-US

```
US-11.1 (flag) ─────┐
US-11.2 (rate lim) ─┤
US-11.10 (SEC) ─────┼──► US-11.5 (bannière) ──► J5 Go/No-Go ouverture ──► J6 Activation
US-11.6 (dashboards)┤                                                          │
US-11.7 (alerting) ─┤                                                          │
US-11.8 (load test)─┤                                                          │
US-11.9 (smoke) ────┘                                                          │
US-11.3 (landing) ──────────────────────────────────────────────────────────► │
US-11.4 (feedback) ─────────────────────────────────────────────────────────► │
US-11.11 (status) ──────────────────────────────────────────────────────────► │
US-11.12 (Discord) ─────────────────────────────────────────────────────────► │
                                                                                │
                                                                                ▼
                                                                  US-11.13 ── J8
                                                                  US-11.14 ── J10
                                                                  US-11.15 ── J10
```

---

## 6. Budget horaire Sprint 11

Capacité théorique : 22h × 2 sem = 44h (cf. Roadmap §6). Répartition :

| Poste | Heures | Commentaire |
|---|---|---|
| Pré-ouverture (hardening J1-J5) | 22h | 50 % — le plus gros de l'effort code |
| Post-ouverture (itérations J6-J10) | 12h | 27 % — réactif, hotfixes |
| Communication (article, teasers, Discord) | 4h | 9 % — essentiellement J1-J6 |
| Review / rapports / décisions | 4h | 9 % |
| Buffer incidents / imprévus | 2h | 5 % |

Effort des agents (démultiplication IA) non inclus mais supervisé dans ce budget.

---

*Backlog rédigé par PM en coordination avec TL, SRE, SEC et founder. À valider en sprint planning J1 M5.*
