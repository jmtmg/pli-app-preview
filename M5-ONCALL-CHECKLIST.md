# M5 — Checklist d'astreinte Founder

**Phase** : M5 (9 → 23 sept 2026)
**Usage** : checklist rapide à exécuter **3 fois par jour** en semaine, **1-2 fois par jour** week-end
**Format** : imprimable / copier-coller dans Notion ou Obsidian
**Philosophie** : tenir 14 jours sans burnout. Structurer l'astreinte pour ne pas "vivre" dans les dashboards.

---

## 1. Règle d'or founder M5

> **Je ne vis pas dans les dashboards. Je les regarde à heures fixes. Entre deux, je fais autre chose.**

- 3 slots d'astreinte active/jour : **9h, 14h, 18h** (max 20 min chaque)
- En dehors : PagerDuty me contacte si P1. Pas avant. Pas sans raison.
- Dimanche 20 sept : **pause complète** si métriques M5 vertes au vendredi 19 sept soir.
- Si je dépasse 10h/jour 2 jours de suite : **flag rouge**, réduire le périmètre, déléguer aux agents, reporter une itération.

---

## 2. Checklist matin — 9h00 CET (20 min max)

### État général (2 min)
- [ ] Ouvrir status page `status.pli.app` → tous composants verts ?
- [ ] Ouvrir PagerDuty → incidents actifs ? Alertes acquittées ?
- [ ] Slack `#alerts` → notifications nouvelles depuis 18h hier ?

### Métriques funnel (3 min)
- [ ] Dashboard Grafana `m5-funnel` → Signups cumulés M5 : ___ / 1000
- [ ] Signups dernière 24h : ___
- [ ] Taux conversion visit → signup : ___ % (cible ≥ 5 %)
- [ ] Taux trial actif : ___ % des signups (cible ≥ 60 %)
- [ ] Anomalie visible ? (pic, chute brutale)

### Performance (3 min)
- [ ] Dashboard `m5-latency` → p95 API actuelle : ___ ms (cible < 500)
- [ ] Taux 5xx 24h : ___ % (cible < 0,5 %)
- [ ] Queue sync backlog : ___ (cible < 100)
- [ ] Erreurs Sentry nouvelles : ___ (lire top 3 si > 10)

### Infrastructure (2 min)
- [ ] CPU / mémoire replicas : stable ?
- [ ] Quota Google : ___ % (cible < 70 %)
- [ ] Quota Microsoft : ___ % (cible < 70 %)
- [ ] Disque : > 30 % libre ?

### Endpoints M2 — audit express (3 min, ajout T5.3)
- [ ] `GET /api/billing/health` → `stripe_webhook_ok=true`, file `stripe:webhook:queue` < 10
- [ ] `GET /api/emails/health` → provider primaire OK, queue outbound < 20, bounce rate 24h < 2 %
- [ ] `GET /api/licensing/health` → `active_keys_count ≥ 2` (overlap OK), `verify_failures_24h` stable
- [ ] Smoke test `tenancy-isolation` (cron 15 min) — dernière exécution < 30 min, statut vert
- [ ] Alertes `§13.3`/`§13.4`/`§13.5`/`§13.6` du runbook : aucune active

### Re-baseline M3+M4 — veille quotidienne (2 min, ajout 2026-04-22 soir)

> Baseline technique : `rebaseline-base-2026-04-22` (empreinte md5 `6a8d82bcbd292422f3ef87d0d6a30dce`), `docs/governance/tags/rebaseline-base-2026-04-22.md`. M3/M4 débloqués 2026-04-22. Deadline dépôt re-baseline signée : **2026-05-14** (D+21). Seuil d'escalade si drift sans retour : **2026-05-02** (J+10).

- [ ] Daily M3 du jour posté dans `docs/governance/daily/m3-YYYY-MM-DD.md` ? Dernière campagne de mesure (Lighthouse, pip-audit, bandit, trivy) mentionnée ?
- [ ] Daily M4 du jour posté dans `docs/governance/daily/m4-YYYY-MM-DD.md` ? Dernière campagne de mesure (NPS, J30, uptime, funnel) mentionnée ?
- [ ] Si pas de daily M3 ou M4 à **J+3** sans raison documentée → ping direction dans le daily M5.
- [ ] Si aucun dépôt de re-baseline à **J+10 (2026-05-02)** → escalade direction via daily M5 + création ticket `docs/governance/tickets/M5-rebaseline-drift-2026-05-02.md`.
- [ ] Quand M3 dépose son rapport (`REBASELINE-CHECKLIST.md` signé) → cocher ici, propager gate §7 Sprint 11.
- [ ] Quand M4 dépose son rapport (perf/UX signé) → cocher ici, propager gate §7 Sprint 11 + débloquer chiffres durs drafts comms (remplacement `{placeholders}`).

### Feedback utilisateur (3 min)
- [ ] Widget feedback : ratio up/down 24h : ___ / ___ (cible > 4:1)
- [ ] Discord `#bugs` : nouveaux signalements ? → triage rapide
- [ ] Discord `#feedback` : retour important à noter ?
- [ ] Emails support : nouveaux ? (cible : répondre sous 4h en ouvré)

### Actions (5 min)
- [ ] Planifier les 2-3 priorités du jour (max)
- [ ] Répondre aux messages support / Discord urgents
- [ ] Si hotfix nécessaire : créer ticket + lancer PR

### Communication (2 min)
- [ ] Vérifier post LinkedIn programmé du jour (si applicable)
- [ ] Vérifier si article blog ou changelog prévu aujourd'hui

---

## 3. Checklist midi — 14h00 CET (15 min max)

### Pulse rapide
- [ ] Status page verte ?
- [ ] Alertes nouvelles depuis 9h ?
- [ ] Signups depuis 9h : ___ (tendance vs matin)
- [ ] p95 actuelle : ___ ms
- [ ] Feedback entrant : anomalie ?

### Triage
- [ ] Issues P1/P2 ouvertes : status ?
- [ ] Réponse aux messages Discord prioritaires (< 4h SLA)
- [ ] Si itération feedback prévue aujourd'hui : avancement ?

### Focus après-midi (5 min)
- [ ] Objectif clair pour l'après-midi (code / communication / review)
- [ ] Si pas d'incident : reprendre le plan sprint
- [ ] Si incident : suivre playbook, documenter

---

## 4. Checklist soir — 18h00 CET (20 min max)

### Debrief journée
- [ ] Signups cumulés M5 J-___ : ___
- [ ] Incidents déclenchés aujourd'hui : ___ (durée cumulée ___ min)
- [ ] Alertes déclenchées aujourd'hui : ___ (P1/P2/P3)
- [ ] Hotfixes déployés : ___
- [ ] Feedback significatif : ___ (synthèse 1-2 lignes)

### Notes journalières (5 min)
- [ ] Écrire 3-5 lignes dans `M5-journal.md` : ce qui s'est passé, décision, humeur
- [ ] Taguer ce qui mérite d'être dans le rapport de clôture

### Préparation J+1 (5 min)
- [ ] Priorités demain : 1-2 objectifs clairs
- [ ] Post comm programmé pour demain ? Relecture
- [ ] Agents : tâches à assigner avant la nuit

### Couper (5 min)
- [ ] Ne pas rester au-delà de 18h30 sauf P1 actif
- [ ] Téléphone sur PagerDuty only (pas Slack/notifs standard)
- [ ] Préparer dîner, faire autre chose, dormir

---

## 5. Checklist week-end

### Samedi matin — 10h00 (10 min)
- [ ] Status page verte ?
- [ ] Alertes depuis vendredi soir ?
- [ ] Signups depuis samedi : ___ (week-end souvent + lent, ok)
- [ ] Discord `#bugs` : urgences ? Répondre 1 ligne minimum si signalé

### Samedi après-midi — 16h00 (10 min)
- [ ] Idem matin
- [ ] Si tout vert : OFF jusqu'à dimanche matin

### Dimanche matin — 10h00 (10 min)
- [ ] Idem samedi matin
- [ ] Si métriques vertes J-1 → **pause complète jusqu'à lundi 9h**

### Dimanche après-midi (optionnel, 5 min)
- [ ] Check status page mobile rapide
- [ ] Pas d'action si vert

**Règle** : sur incident P1 weekend → suivre playbook. Hors P1 → ne pas intervenir, laisser mijoter jusqu'à lundi.

---

## 6. Seuils d'action immédiate (tout moment)

Même en dehors des checkpoints, intervenir immédiatement si :

| Déclencheur | Action immédiate |
|---|---|
| SMS PagerDuty P1 | Ouvrir playbook correspondant (runbook §6 ou §13) |
| Message Discord "je ne peux plus accéder" × 3 | Ouvrir status page + check |
| Tweet / LinkedIn avec "PLI bug" qui prend de l'engagement | Répondre factuellement, vérifier |
| Article presse / influenceur → pic trafic | Vérifier dashboard funnel + capacity |
| Email Stripe "webhook 500 repeated" | Check runbook §6.4 + §13.3 (backlog + signature) |
| Alerte `emails_outbound_queue_depth > 100` | Check runbook §13.4 (bascule provider) |
| Spike `licensing_verify_failures` | Check runbook §13.5 (rotation Ed25519) |
| Smoke test `tenancy-isolation` KO | Runbook §13.6 — **P1 gravité max** |
| Pas de daily M3 ou M4 depuis ≥ 3 jours calendaires | Ping direction dans daily M5 du jour |
| Baseline `rebaseline-base-2026-04-22` à J+10 sans dépôt M3/M4 | Escalade direction + création `M5-rebaseline-drift-<date>.md` |

---

## 7. Signes de fatigue à surveiller (auto-monitoring)

Chaque soir, s'auto-évaluer sur 3 points :

- **Sommeil dernière nuit** : < 6 h → risque jour suivant
- **Nombre d'heures actives sur PLI** : > 10 h/jour sur 2 jours → alerte
- **Qualité décisions** : "ai-je pris une décision que je regretterais demain ?" → oui → repos

**Si 2 des 3 sont rouges** :
- Prévenir TL/agents → délestage sur tâches non urgentes
- Reporter l'itération feedback de 24 h
- Dormir, repousser communication non critique

---

## 8. Interlocuteurs & canaux

| Besoin | Canal prioritaire | Délai attendu |
|---|---|---|
| Incident P1 | PagerDuty → SMS + appel | < 5 min ack |
| Hotfix code | Slack #dev + PR GitHub | < 30 min si dispo |
| Décision produit | Slack #product + PM | < 4h ouvré |
| Communication externe urgente | Slack #comms + PM | < 2h ouvré |
| Question utilisateur Discord | Discord direct | < 4h ouvré |
| Question utilisateur email | Email support | < 4h ouvré |
| Incident SEC grave | Téléphone TL direct | immédiat |

---

## 9. Post-M5 — décompression

Après J10 (22 septembre 2026, soir) :

- [ ] **J11-J12** : 2 jours OFF complets. Pas de dashboard, pas de Discord, pas de réponse.
- [ ] **J13 (25 sept)** : reprise douce, préparation Launch S25 (pas avant)
- [ ] Retrospective M5 formelle avec PM agent : ce qui a marché, ce qui a coincé, ce qui change pour Launch

**Sauf incident P1 en cours**, l'astreinte M5 **prend fin officiellement le 23 septembre à 18h00 CET**.

---

## 10. Mantras M5 (à relire chaque matin)

- Mon objectif n'est pas que tout soit parfait. C'est que rien ne casse gravement.
- Un utilisateur qui signale un bug est un allié. Un utilisateur silencieux qui part est une perte.
- Une réponse honnête courte vaut mieux qu'une réponse exhaustive 6 h plus tard.
- Le founder fatigué est un founder qui prend des décisions que le founder reposé regrette.
- Le Launch est dans 3 semaines. Je ne suis pas en course. Je suis en validation.

---

*Checklist établie par SRE agent + Founder. Adaptée quotidiennement selon observation réelle.*
