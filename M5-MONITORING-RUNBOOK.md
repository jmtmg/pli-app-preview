# M5 — Runbook Monitoring & Incident Response

**Phase** : M5 (9 → 23 sept 2026) · **Suite** : Launch S25 (J0 = 7 oct 2026)
**Owner** : SRE · **Backup** : TL · **Astreinte** : Founder (7j/7 pendant M5)
**Version** : 1.0 · **Dernière MAJ** : 8 sept 2026
**Public** : interne — à ne pas publier tel quel
**Complément** : voir [runbook/M5-launch.md](runbook/M5-launch.md) pour les procédures opérationnelles condensées (commandes précises, checklist J-7 → J+7 Launch). Le présent document est l'extension exhaustive : SLOs, playbooks détaillés, chaos testing, post-mortems, observabilité.

---

## 1. Objectif du runbook

Fournir à l'astreinte (founder principalement) un **guide opérationnel complet** pour :

- Monitorer PLI en temps réel pendant M5
- Détecter un incident en < 15 min (cible : < 5 min grâce à l'alerting)
- Diagnostiquer et contenir en < 30 min
- Résoudre ou rollback sans attendre le feu vert
- Communiquer à l'externe pendant et après l'incident

> **Principe N°1** : protéger l'utilisateur, pas l'image. Un post-mortem public vaut mieux qu'un silence suspect.

---

## 2. SLOs M5

| Métrique | SLO | Cible dépassement | Action |
|---|---|---|---|
| Uptime global (web + API) | ≥ 99,5 % | < 99 % sur 7j | Post-mortem + plan correctif |
| Latence p95 API | < 500 ms | > 1 s soutenu 10 min | P2 alerte |
| Latence p99 API | < 1 s | > 2 s soutenu 10 min | P2 alerte |
| Taux erreurs 5xx | < 0,5 % | > 1 % sur 5 min | P2 alerte |
| Erreurs 5xx critiques | 0 | > 5 % sur 5 min | P1 alerte |
| Queue sync backlog | < 100 | > 500 | P2 alerte |
| Webhook Stripe succès | > 99 % | < 95 % | P2 alerte |
| Email transactionnel inbox | > 95 % | < 90 % | P3 alerte |
| Quota Google OAuth | < 70 % | > 80 % | P3 alerte |
| Quota Microsoft Graph | < 70 % | > 80 % | P3 alerte |
| Downtime cumulé M5 | < 30 min | > 15 min | Gel ouverture |

---

## 3. Stack observabilité

| Composant | Outil | URL interne | Accès |
|---|---|---|---|
| Dashboards métier | Grafana Cloud (free) | grafana.pli.ops | SSO Google |
| Logs | Better Stack (ex Logtail) | betterstack.pli.ops | Magic link |
| Traces (APM) | Tempo / Grafana | grafana.pli.ops/tempo | SSO Google |
| Uptime externe | Better Stack Uptime + Uptime Robot (double) | — | — |
| Alerting | Better Stack On-Call + PagerDuty (free tier) | — | SMS + appel founder |
| Status page publique | Better Stack Status | status.pli.app | public |
| WAF / edge | Cloudflare | dash.cloudflare.com | 2FA founder |
| Error tracking | Sentry (free 5k events) | pli.sentry.io | SSO Google |

---

## 4. Dashboards de référence

### 4.1 `m5-funnel.json` — Signup funnel

**URL** : grafana.pli.ops/d/m5-funnel
**Panels** :
1. Signups dernière heure (big number + trend 7j)
2. Signups cumulés M5 (progression 0 → 1000)
3. Funnel visit → signup → email verified → login → 1er compte → trial actif (Sankey ou barres)
4. Taux conversion par étape (gauge)
5. Top sources de trafic (table, Plausible)
6. Géo signups (carte, Plausible)
7. Hit rate rate-limiter `/auth/signup` (graph)

**Consultation** : minimum 3×/jour (9h, 14h, 18h) pendant M5.

### 4.2 `m5-latency.json` — Latence & erreurs

**URL** : grafana.pli.ops/d/m5-latency
**Panels** :
1. Latence p50/p95/p99 par endpoint critique (multi-line)
2. Taux erreur 5xx (stacked area, par endpoint)
3. Taux erreur 4xx (idem)
4. Queue sync backlog (gauge + trend)
5. DB : connexions actives, waiting, slow queries > 1s
6. Redis : latence, ops/sec
7. Workers sync : running, succeeded, failed, retry

### 4.3 `m5-infra.json` — Infrastructure

**URL** : grafana.pli.ops/d/m5-infra
**Panels** :
1. CPU/mémoire par instance app (gauge)
2. Replicas alive / desired (timeseries)
3. Disque (%, IOPS, latence)
4. Quota Google OAuth (gauge rouge > 80 %)
5. Quota Microsoft Graph (idem)
6. Stripe webhooks : succès/échec par heure
7. Email provider : delivery rate, bounce rate

---

## 5. Alerting — Règles & routage

Fichier source : `ops/alerts/m5-alerts.yml`

### 5.1 Priorités

| Niveau | Canal | SLA acquittement | SLA résolution |
|---|---|---|---|
| **P1** | SMS + appel PagerDuty + Slack #incidents | < 5 min | < 30 min |
| **P2** | Slack #alerts + email | < 15 min | < 2 h |
| **P3** | Slack #alerts-low | < 1 h | < 24 h |

### 5.2 Règles P1 (SMS + appel)

| Règle | Trigger | Runbook section |
|---|---|---|
| `app_down` | Uptime external check KO 2× consécutifs | §6.1 |
| `db_down` | Erreurs DB connexion > 50 % sur 1 min | §6.2 |
| `5xx_spike_critical` | Taux 5xx > 5 % sur 5 min | §6.3 |
| `stripe_webhook_failure_critical` | > 10 % webhooks en erreur sur 10 min | §6.4 |
| `auth_broken` | Signup OU login > 50 % échec sur 3 min | §6.5 |
| `data_leak_suspected` | Test isolation tenant synthétique échoue | §6.6 — **gravité max** |

### 5.3 Règles P2

| Règle | Trigger | Runbook section |
|---|---|---|
| `latency_p95_high` | p95 > 1 s sur 10 min | §6.7 |
| `5xx_elevated` | Taux 5xx > 1 % sur 10 min | §6.3 |
| `sync_queue_backlog` | Queue > 500 sur 5 min | §6.8 |
| `worker_crashloop` | 3 crashes workers sync en 15 min | §6.9 |
| `rate_limit_abuse` | > 100 × limite `/auth/signup` sur 5 min | §6.10 |

### 5.4 Règles P3

| Règle | Trigger | Runbook section |
|---|---|---|
| `latency_p95_warn` | p95 > 500 ms sur 15 min | §6.7 |
| `email_inbox_low` | taux inbox < 95 % sur 1 h | §6.11 |
| `quota_google_warn` | quota > 80 % | §6.12 |
| `quota_ms_warn` | quota > 80 % | §6.12 |
| `disk_space_warn` | < 30 % libre | §6.13 |

---

## 6. Playbooks incident

> **Pour chaque playbook** : suivre les étapes dans l'ordre. Si blocage à une étape, escalader (cf. §8).

### 6.1 App down (P1)

**Symptômes** : site inaccessible, uptime externe KO, utilisateurs signalent.

1. **Communiquer** (< 5 min) : déclarer incident sur status page, tweet court si durée > 10 min (cf. social-teasers §4)
2. **Diagnostiquer** :
   - Cloudflare : statut origin, logs edge ?
   - Fly.io / Hetzner : statut des replicas (`fly status` ou dashboard)
   - DNS : résolution OK ? (`dig pli.app`)
3. **Contenir** :
   - Si replicas crashés : `fly apps restart pli-app`
   - Si DB down : cf. §6.2
   - Si infra provider en panne : confirmer via statuspage du provider, communiquer aux users
4. **Vérifier retour à la normale** : smoke test manuel signup → login + check dashboards
5. **Clore** : update status page "résolu", heure de fin, post-mortem dans 48 h

**Si non résolu en 20 min** → appel TL (backup), considérer rollback dernier déploiement (§7).

### 6.2 DB down (P1)

1. Vérifier dashboard DB (connexions, CPU, mémoire, disque)
2. Si DB managée (Supabase/Neon) : vérifier statuspage provider
3. Si auto-hébergée : SSH host, `systemctl status postgresql`
4. Si full disk : purge logs `pg_log`, snapshot d'urgence
5. Si connexions saturées : `pg_stat_activity` → kill long-running queries
6. Si corruption suspectée : **ne pas bidouiller**, activer read-only mode app, escalader TL

### 6.3 5xx spike (P1 si > 5 %, P2 si > 1 %)

1. Grafana → dashboard latency → identifier endpoint coupable
2. Sentry → regarder la dernière erreur répétée (souvent 1 stacktrace explique 80 %)
3. Logs Better Stack : filter `level=error`, dernière heure
4. Si cause claire et fix évident (< 10 lignes) : hotfix PR → deploy fast-track (TL approval)
5. Si cause pas claire : **rollback dernier déploiement** (§7)
6. Si rollback ne résout pas : feature flag kill switch sur l'endpoint coupable

### 6.4 Stripe webhooks en erreur (P1 si > 10 %)

1. Dashboard `m5-infra` → panel Stripe
2. Stripe dashboard : Developers → Webhooks → events failed
3. Si signature fail : vérifier secret en env (rotation récente ?)
4. Si 5xx de notre côté : cf. §6.3
5. **Important** : même en erreur webhook, Stripe retry. Pas de perte de transaction si on résout < 24 h.
6. Manuel : replay events depuis Stripe dashboard après fix

### 6.5 Auth broken (P1)

1. Vérifier endpoint `/health` et `/ready`
2. Redis up ? (JWT blocklist dépend de Redis)
3. Si JWT_SECRET rotated sans propagation : rollback deploy
4. Smoke test manuel signup sur compte jetable
5. Communiquer status page si > 5 min

### 6.6 Data leak inter-tenant suspecté (P1, gravité max)

> **Priorité absolue. Si seul risque évoqué, suspendre tout.**

1. **Immédiatement** : activer feature flag `read_only_mode=true` (app en lecture seule globale)
2. Prévenir TL + SEC par téléphone dans les 5 min
3. Collecter preuves : logs, requêtes incriminées, user_ids concernés
4. Vérifier périmètre : combien d'users, quelle période, quelles données
5. Si confirmé : notification CNIL sous 72 h (obligation RGPD)
6. Communication publique honnête sous 48 h, même partielle
7. Post-mortem public obligatoire

### 6.7 Latence p95 élevée (P2/P3)

1. Dashboard `m5-latency` → identifier endpoint lent
2. DB : slow query log → `EXPLAIN ANALYZE` sur les gros consommateurs
3. Redis saturé ? → ops/sec, mémoire
4. CPU app saturé ? → scaler horizontalement (`fly scale count 3`)
5. Si spike trafic légitime → autoscaler doit réagir, sinon manuel
6. Optimisation : créer ticket P1 dev, patch dans la journée

### 6.8 Sync queue backlog > 500 (P2)

1. Workers sync running ? (dashboard infra)
2. Si workers crashloop : cf. §6.9
3. Si quota Google/Microsoft : cf. §6.12
4. Scale workers : `fly scale count worker=3`
5. Si accumulation irrécupérable : pause nouveaux jobs, drain, reprendre

### 6.9 Worker sync crashloop (P2)

1. Logs workers : exception récurrente ?
2. Message précis : MIME mal formé, quota, timeout API externe ?
3. Si message isolé : skip + log + ticket → reprendre
4. Si pattern global : rollback code worker récent
5. Circuit breaker : activer si > 50 % requêtes API externe en erreur

### 6.10 Abus rate limiter (P2)

1. Logs rate limiter : top IP, top fingerprint
2. Si pattern bot / attaque : ban IP via WAF Cloudflare
3. Augmenter challenge CAPTCHA (mode "I'm under attack")
4. Si attaque ciblée : escalader SEC, potentiel incident public

### 6.11 Email inbox faible (P3)

1. Dashboard provider email (SendGrid/Postmark)
2. Spam rate par FAI (Gmail, Outlook, Yahoo)
3. SPF/DKIM/DMARC toujours verts ? (vérif `mxtoolbox.com`)
4. Volumétrie : on a dépassé le warm-up ?
5. Si bascule provider secondaire nécessaire : feature flag `email_provider=postmark|sendgrid`

### 6.12 Quota Google/Microsoft > 80 % (P3)

1. Dashboard quota
2. Demander augmentation quota au provider si possible (ticket)
3. Prioriser utilisateurs actifs dans sync (throttling intelligent)
4. Repousser sync initiale nouveaux comptes si quota critique
5. Communication users : "sync un peu plus lente que d'habitude" via banner

### 6.13 Disque < 30 % libre (P3)

1. `df -h` hosts
2. Purger logs anciens (`> 7 jours`)
3. Purger données orphelines (pièces jointes sans message)
4. Augmenter volume si tendance confirmée

---

## 7. Rollback — Procédure

### 7.1 Quand rollback ?

- Incident P1 non diagnostiqué en 15 min
- Incident P2 non résolu en 1 h
- Suspicion régression sur déploiement < 24 h

### 7.2 Comment rollback ?

**Backend** :
```bash
fly releases list -a pli-app
fly releases rollback <previous_version> -a pli-app
```

**Frontend** :
```bash
# Vercel
vercel rollback <deployment-url>
# Ou Cloudflare Pages
# Promote ancien deployment via dashboard
```

**DB schema (migration Alembic)** :
- `alembic downgrade -1` **UNIQUEMENT si downgrade testé**
- Sinon : ne pas rollback DB, adapter code app pour tolérer nouveau schema

### 7.3 Après rollback

- Vérifier retour SLOs
- Créer ticket P0 pour analyser cause
- Ne **pas redéployer** le commit coupable sans fix + test dédié
- Post-mortem

---

## 8. Escalation

| Moment | Action |
|---|---|
| P1 non résolu en 15 min | Appel TL (+33 X XX XX XX XX) |
| P1 non résolu en 30 min | Appel backup infra (support Fly.io / Hetzner) |
| Data leak confirmé | DPO → CNIL (72h) + avocat |
| Incident financier (Stripe) | Support Stripe + avocat |
| Incident média (article / tweet viral négatif) | Pause communication, consultation PM, brief founder |

**Contacts** (table privée, non diffusée dans ce doc public) : voir `ops/contacts-M5.md` (gitignored, 1Password shared note).

---

## 9. Communication externe pendant incident

**Principe** : transparence > discrétion. Un incident reconnu vaut mieux qu'un incident caché.

### 9.1 Décision de communication

| Gravité | Status page | Tweet/LinkedIn | Email users |
|---|---|---|---|
| P1 > 5 min | Oui, immédiat | Non si < 15 min | Non |
| P1 > 15 min | Oui | Oui (court factuel) | Non |
| P1 > 1 h | Oui | Oui | Oui, aux users impactés |
| P2 ressentie | Oui si signalée | Optionnel | Non |
| P3 | Non (sauf si dégradation longue) | Non | Non |

### 9.2 Templates (cf. social-teasers §4)

- Status page incident déclaré
- Tweet incident court
- Tweet résolution
- Email users post-incident (> 1h)
- Post-mortem public (< 48 h post-incident)

---

## 10. Post-mortem — Template

Tout incident > 10 min déclenche post-mortem. Publié sous 48 h.

```markdown
# Post-mortem — [Titre incident] — [Date]

## Résumé
- Début : [heure]
- Fin : [heure]
- Durée : [X] min
- Impact : [% users affectés, fonctionnalité touchée]

## Timeline
- HH:MM — [événement]
- HH:MM — [alerte déclenchée]
- HH:MM — [diagnostic]
- HH:MM — [contenu / rollback]
- HH:MM — [résolution confirmée]

## Cause racine
[Explication factuelle, sans jugement]

## Détection
- Comment on a su : [alerte / utilisateur / smoke test]
- Temps de détection : [X] min

## Ce qui a bien marché
- [1-3 points]

## Ce qui n'a pas marché
- [1-3 points]

## Actions correctives
- [ ] [Action 1] — owner — deadline
- [ ] [Action 2] — owner — deadline

## Communication
- [Liens vers status page, tweets, post public]
```

Publiés dans `/post-mortems/` et en lien sur status page.

---

## 11. Check-list quotidienne SRE M5

À faire **3 fois par jour** pendant M5 (9h, 14h, 18h CET) :

- [ ] Dashboards funnel / latency / infra — vue rapide, anomalies ?
- [ ] Alertes actives (Better Stack / PagerDuty) : tout acknowledgé ?
- [ ] Queue sync backlog sous seuil ?
- [ ] Quotas Google / Microsoft < 80 % ?
- [ ] Erreurs Sentry dernières 24 h : top 5 identifiées ?
- [ ] Smoke tests synthétiques verts ?
- [ ] Status page cohérente avec réalité ?
- [ ] Tickets ouverts P0/P1 : status ?
- [ ] Slack #alerts lu / trié ?

(Checklist aussi dans `M5-ONCALL-CHECKLIST.md`)

---

## 12. Exercices pré-ouverture (J1-J5)

Avant d'activer le flag `public_signup_enabled`, exécuter :

- [ ] **Chaos test 1** : kill 1 replica app → autoscaler rétablit en < 2 min, aucune 5xx utilisateur
- [ ] **Chaos test 2** : simuler DB timeout 5 min → circuit breaker en place, message utilisateur gracieux
- [ ] **Chaos test 3** : couper Redis 2 min → fallback sans crash (dégradé accepté)
- [ ] **Chaos test 4** : saturer workers sync → queue se draine après peak
- [ ] **Alerte test** : trigger manuel P1 → SMS + appel founder reçus sous 5 min
- [ ] **Alerte test** : trigger manuel P2 → Slack reçu < 15 min
- [ ] **Rollback test** : rollback backend sur staging → service restauré en < 3 min
- [ ] **Load test k6** : 500 signups/heure soutenu 1 h → p95 < 1 s, 0 erreur > 500
- [ ] **Smoke test E2E** : cron 15 min → 48 h consécutives vertes

Si un exercice échoue : **ne pas activer flag**. Corriger, re-tester.

---

## 13. Audit post-integration — Endpoints M2 (ajout 2026-04-22, T5.3 ticket `M5-freeze.md`)

> **Versioning §13** : v1.1 — validée direction 2026-04-22 sous réserve d'itération minor si M3/M4 ajoutent un chemin d'alerte pendant leur re-baseline (cible D5 2026-05-14). Dans ce cas : bump v1.1 → v1.2 et ajout d'un §13bis ou §14 dédié M3/M4. Traçabilité dans l'en-tête §0 du runbook.

### 13.1 Contexte

L'integration sprint 2026-04-27 → 2026-05-18 monte derrière `PLI_ENABLE_M2` les routers **billing (Stripe webhook)**, **emails transactionnels**, **licensing (Ed25519)** et **tenancy**. Les playbooks §6 de ce runbook couvraient partiellement Stripe (§6.4) et auth (§6.5) mais n'adressaient pas le reste du périmètre M2. Cet audit ajoute les playbooks manquants et 4 scénarios d'incident fictifs à exécuter en staging avant ouverture Beta publique.

> Nota : tant que M2 T2.1 (déblocage `pli.auth`) + T2.2 (wire-up flag) ne sont pas clos (deadlines 2026-04-30 et 2026-05-07), les playbooks §13.3-13.6 restent **tests-on-staging only**. Dès que `PLI_ENABLE_M2=1` démarre proprement sur CI, ils deviennent playbooks production.

### 13.2 Couverture M2 — mapping endpoint → playbook

| Endpoint M2 | Module | Playbook existant | Playbook ajouté §13 |
|---|---|---|---|
| `POST /api/billing/stripe/webhook` | `pli/billing` | §6.4 (Stripe webhooks en erreur) | §13.3 enrichit : file retry + replay + signature |
| `POST /api/emails/send` + workers outbound | `pli/emails` | — | §13.4 (bounce rate, SPF/DKIM/DMARC, Postmark/Resend) |
| `GET /api/licensing/verify`, `POST /api/licensing/issue` | `pli/licensing` | — | §13.5 (licence invalide, rotation clé Ed25519) |
| `*` tous endpoints tenant-scoped | `pli/tenancy` | §6.6 (leak inter-tenant) | §13.6 (isolation test actif, RLS check, header `X-Tenant`) |
| `POST /auth/*` + refresh | `pli/auth` | §6.5 | inchangé |

### 13.3 Playbook — Stripe webhook backlog / signature KO (P1/P2)

**Symptômes** : file Redis `stripe:webhook:queue` > 50 événements non traités, ou taux `signature_invalid` > 1 %.

1. Vérifier `GET /api/billing/health` → `stripe_webhook_ok=true`, `last_event_processed_ms < 30000`.
2. Inspecter logs `pli.billing.webhook` : filtrer `event.type` + `signature_valid`.
3. **Si signature invalide systématique** : rotation accidentelle du `STRIPE_WEBHOOK_SECRET`. Récupérer clé active depuis Stripe dashboard → `Developers > Webhooks > Signing secret`. Mettre à jour `PLI_STRIPE_WEBHOOK_SECRET` en secret manager. Rolling restart API.
4. **Si backlog sans erreur de signature** : scaler workers `billing-consumer` (x2), replay des événements non traités via `python -m pli.billing.cli replay --since <timestamp>`.
5. **Tolérance perte** : aucune. Chaque event `checkout.session.completed` déclenche provisioning licence → perte = client payé sans licence. Replay obligatoire, pas de skip.
6. Communication externe : si retard > 10 min sur `checkout.session.completed`, email automatique "Votre licence sera activée sous quelques minutes — merci de votre patience".

### 13.4 Playbook — Emails transactionnels en échec (P2/P3)

**Symptômes** : bounce rate > 5 % sur 1 h, ou `emails_outbound_queue_depth > 100`, ou alerte Postmark/Resend downgrade.

Endpoints concernés : emails signup confirmation, password reset, receipt Stripe, licence issuance, feedback acknowledgement.

1. Vérifier status page provider : Postmark (primaire), Resend (secondaire).
2. `GET /api/emails/health` → vérifier `provider_primary_ok`, `provider_secondary_ok`, `last_sent_ms`.
3. **Si primaire KO** : toggle ENV `PLI_EMAIL_PROVIDER=resend` à chaud (via feature_flags DB). Vérifier volumes côté Resend dashboard.
4. **Si bounce rate élevé** : dump 10 adresses bounced, vérifier format. Bug possible côté signup (saisie non validée).
5. **SPF/DKIM/DMARC** : `dig TXT mail.pli.app +short` doit matcher les records publiés. Si expire/drift → action SEC sous 1 h.
6. **Fenêtre de tolérance** : un email de confirmation signup peut attendre 5 min sans casser le funnel. Un email `password_reset` doit partir sous 2 min. Un email de receipt Stripe doit partir sous 15 min (non bloquant).
7. **Escalation SEC** : bounce rate > 15 % → suspicion liste polluée ou reputation IP → basculer IP secondaire.

### 13.5 Playbook — Licence invalide / rotation Ed25519 (P1)

**Symptômes** : spike sur `licensing_verify_failures`, ou clients Local en masse "Licence expirée ou invalide", ou alerte rotation clé imminente.

Contexte : licences Local sont signées hors-ligne Ed25519 — la clé privée est en HSM/KMS, la publique est embarquée dans le binaire client.

1. Vérifier `GET /api/licensing/health` → `current_kid`, `active_keys_count`, `next_rotation_ts`.
2. **Si `verify_failures` concerne un même `kid`** (key id) : clé rotate en production avant déploiement client. **Rollback immédiat** : réinjecter l'ancienne clé publique côté serveur (jointure `kid`), informer les clients via refresh licence silencieuse.
3. **Si `verify_failures` dispersé** : inspecter payload. Si `exp < now` → licences expirées (mode attendu). Si signature structure KO → corruption, incident SEC.
4. **Procédure rotation propre** (prévention) : cf. `docs/adr/0006-licences-offline-ed25519.md`. Rotation avec overlap ≥ 30 jours entre anciennes/nouvelles clés embarquées client. Ne jamais rotate sans bump client.
5. **Communication externe** : email dédié aux users Local concernés, jamais un tweet (sensible).
6. **Ne jamais** logger la clé privée, même tronquée. Audit automatique CI.

### 13.6 Playbook — Tenancy isolation suspect (P1 gravité max)

**Symptômes** : alerte `tenancy_cross_access` (cf. §5.2), ou user rapporte voir la donnée d'un autre.

Note : §6.6 couvre le scénario confirmé ; §13.6 couvre le **test actif préventif** et la vérification continue.

1. **Test continu** : un cron `smoke-tests/tenancy-isolation.py` exécute toutes les 15 min deux requêtes différentes depuis 2 tenants fictifs sur les endpoints scoped. Résultat attendu : aucune fuite de `account_id` / `message_id` / `contact_id`.
2. **Si échec du test** :
   - PagerDuty P1 immédiat, gravité max
   - Suivre §6.6 (kill switch inscription + lecture, read-only, audit)
3. **Check SQL à chaud** (sur copie snapshot, jamais prod) :
   ```sql
   SELECT tenant_id, COUNT(*) FROM messages GROUP BY tenant_id;
   -- Attendu : ligne par tenant, pas d'incohérence (messages orphelins = 0)
   SELECT COUNT(*) FROM messages m
    JOIN accounts a ON a.id = m.account_id
    WHERE m.tenant_id <> a.tenant_id;
   -- Attendu : 0. Toute ligne > 0 = leak potentiel.
   ```
4. **Middleware `X-Tenant` header** : chaque requête API authenticated pose le `tenant_id` issu du JWT. Toute requête sans header côté serveur = 401 (pas 403) : on ne trahit pas l'existence de tenant.
5. **RLS PostgreSQL** : policies attachées aux tables `messages`, `contacts`, `conversations`, `licenses`, `billing_events`. À re-vérifier après chaque migration.

### 13.7 Exercices d'incident fictif — à exécuter en staging avant ouverture Beta

À réaliser par QA + SRE en staging sur `release-v1` après le freeze 2026-08-26, avant bascule `public_signup_enabled=true`. **Ces drills remplacent la section §12 en y ajoutant les endpoints M2.**

| # | Endpoint M2 | Scénario fictif | Attendu | Owner |
|---|---|---|---|---|
| D1 | Stripe webhook | Injection d'un event avec signature corrompue (1 % du flux) | Alerte §5.3 sous 5 min, ligne audit log, pas d'impact users valides | SRE |
| D2 | Stripe webhook | Postmark/Resend down (simulation) + 50 events `checkout.session.completed` en 2 min | File Redis se remplit puis se draine < 10 min après restart provider, replay OK | SRE |
| D3 | Emails sortants | Provider Postmark down pendant 5 min | Bascule auto ENV → Resend via flag, 0 email perdu (queue retry) | SRE + SEC |
| D4 | Emails sortants | 50 adresses invalides en entrée signup | Bounce rate annoncé sous 10 min, bloqué côté form (pas de dépassement provider) | QA |
| D5 | Licence Ed25519 | Simulation `kid=v2` côté serveur avec clients sur `kid=v1` | Réponse d'API renvoie `signature_error, suggested_action=refresh`, client refresh transparent | BE + SEC |
| D6 | Licence Ed25519 | Audit log leak check : grep clé privée dans logs staging sur 7 jours | 0 match. Si match → correctif ligne de log immédiat. | SEC |
| D7 | Tenancy | Smoke test cross-tenant : user A tente `GET /messages/<id-du-tenant-B>` | 404 (pas 403, pas 200). Alerte déclenchée aussi. | QA |
| D8 | Tenancy | Migration Alembic qui oublie une policy RLS sur nouvelle table | CI bloque la migration (test dédié `test_rls_policies_present.py`) | QA + SEC |
| D9 | Billing + Licence (chaîne) | `checkout.session.completed` → issuance licence → email delivery | Latence E2E < 60 s sur p95, < 3 min sur p99. | QA + SRE |
| D10 | Tenancy + Emails | Un email de reset mot de passe ne doit jamais contenir d'info d'un autre tenant | Test unitaire ET E2E. 0 info cross-tenant. | SEC |

**Critère de passage Go Beta Publique M2** : D1 à D10 **tous verts** en staging. Tout échec bloque l'ouverture.

### 13.8 Références croisées

- `docs/adr/0004-stripe-integration.md` — décisions Stripe (PCI scope, webhook idempotency)
- `docs/adr/0005-emails-transactionnels.md` — providers, fallback, SPF/DKIM/DMARC
- `docs/adr/0006-licences-offline-ed25519.md` — rotation, distribution clé publique
- `docs/adr/0002-multi-tenancy.md` — RLS policies, middleware header
- `M5-SEC-CHECKLIST.md` §5 (tenancy) · §8 (Stripe) · §9 (emails) · §10 (licences) — contrôles SEC complémentaires

---

*Rédigé par SRE (agent) en coordination avec TL, SEC et founder. Revu et mis à jour à chaque incident M5.*
*Section §13 ajoutée 2026-04-22, audit post-integration — ticket `M5-freeze.md` T5.3.*
