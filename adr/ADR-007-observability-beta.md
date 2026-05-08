# ADR-007 — Observabilité et alerting pour la beta privée

**Statut** : Accepté
**Date** : 12 août 2026
**Auteur** : Tech Lead + SRE
**Contexte** : Phase M4 (Beta privée)

---

## 1. Contexte

En beta privée, nous passons de 1 user (founder, dogfooding) à 100 users externes qui peuvent utiliser PLI à n'importe quelle heure. Nous avons besoin :

- De savoir **en temps réel** si quelque chose casse
- De corréler erreurs et comportement utilisateur
- De ne pas déclencher d'alertes à 3h du matin pour un user isolé qui a un VPN exotique
- De respecter le RGPD (pas de logs PII)

L'équipe est composée de 1 humain + agents. L'astreinte est informelle. Les alertes doivent être **rares mais actionnables**.

---

## 2. Décision

### 2.1 Stack observabilité

| Couche | Outil | Raison |
|---|---|---|
| Métriques | Prometheus (self-hosted) + Grafana | Standard, bon contrôle, RGPD-safe |
| Logs | Loki + Grafana | Intégré à la stack, coût maîtrisé |
| Traces | OpenTelemetry → Tempo | Minimum viable, pas de sampling avancé en M4 |
| Erreurs frontend | Sentry (plan startup) | Best-in-class, config DPA signée |
| Uptime externe | Healthchecks.io + UptimeRobot | Double-sonde indépendante |
| Alerting | Alertmanager → PagerDuty (free tier) + Discord webhook | Hiérarchisation P1/P2/P3 |

### 2.2 Niveaux d'alerte

| Niveau | Signification | Notification |
|---|---|---|
| **P1 — bloquant** | Service indisponible, erreurs 5xx > 1 %, data loss suspecté | PagerDuty SMS + Discord `@oncall` + email founder |
| **P2 — dégradation** | p95 > 2× cible, taux erreurs 4xx anormal, file sync en retard | Discord `#alerts` + email founder (pas SMS) |
| **P3 — anomalie** | Écart comportemental, baisse NPS, usage d'une feature < seuil | Discord `#alerts`, pas de notification push |

### 2.3 Alertes P1 — liste exhaustive

1. **5xx rate** > 1 % sur 5 min → P1
2. **Disponibilité endpoint `/healthz`** < 99 % sur 2 min → P1
3. **DB connections** pool saturé > 90 % sur 3 min → P1
4. **Certificat TLS** expire < 7 j → P1
5. **Stripe webhook** échec de signature 3× consécutives → P1
6. **Sync Gmail/Microsoft** échec 100 % sur 1 provider pendant 10 min → P1
7. **Espace disque** < 10 % sur prod VM → P1
8. **Tâche backup DB** échoue 2× consécutives → P1

### 2.4 Alertes P2

1. p95 `/conversations` > 800 ms sur 10 min
2. p95 recherche > 600 ms sur 10 min
3. Erreur 4xx rate > 10 % (hors 401) sur 15 min
4. Queue de sync > 100 items en retard > 15 min
5. Emails transactionnels délai > 5 min
6. Rate-limit Gmail/Graph atteint sur ≥ 3 comptes simultanés

### 2.5 Règles de silence

- Fenêtre de maintenance programmée : silence explicite via Alertmanager
- Pas d'alerte P1 entre 23h-7h CET sauf bloquant confirmé (les alertes nocturnes doivent rester exceptionnelles sur 1 astreinte)
- Flap protection : 2 occurrences consécutives requises avant paging (évite le bruit sur déploiements)

### 2.6 Pas d'alertes sur

- Comportement utilisateur individuel (un user qui voit 1 erreur n'alerte pas)
- Features en feature-flag expérimental
- Logs verbeux de debug

---

## 3. Logs — règles RGPD

- **Aucune** IP utilisateur stockée en clair au-delà de 7 jours
- **Aucun** header `Authorization` logué
- **Aucun** corps de mail / sujet stocké dans les logs applicatifs
- `user_id` → hashé (sha256 + salt par env) dans les logs
- Rétention Loki : 30 jours (ingestion), 90 jours (archives chiffrées pour incidents)
- DPA signée avec Sentry (pas de replay activé, sampling des stack traces sans contenu)

---

## 4. Dashboards Grafana — panels obligatoires

### Dashboard "Beta Overview"

- Beta users activés cumul (compteur)
- Users actifs 24 h (jauge + historique 14 j)
- Répartition par batch
- NPS roulant 7 j
- Rétention J1 / J7 / J30 par cohorte batch

### Dashboard "Performance"

- p50 / p95 / p99 par endpoint clé (`/conversations`, `/search`, `/messages/:id`)
- Débit req/s
- Taux erreurs 4xx / 5xx
- Latence DB (query duration)

### Dashboard "Infra"

- CPU / RAM / disque par pod
- Connexions DB
- File sync longueur
- Stripe webhooks success rate

### Dashboard "Errors"

- Top 10 exceptions backend (Python)
- Top 10 erreurs frontend (Sentry)
- Erreurs par feature

---

## 5. Conséquences

### Positives

- Oncall réellement actionnable (pas de noise)
- Corrélation feedback ↔ métriques rapide
- Stack sous contrôle, coût mensuel estimé < 100 €
- Conformité RGPD vérifiée, DPIA (doc 12) mise à jour

### Négatives

- Pas de tracing distribué fin (mais architecture simple, acceptable)
- Sentry = SaaS externe (DPA couvre, mais dépendance)
- Pas d'APM premium type Datadog (coût)

---

## 6. Révision

Ré-évaluation à la fin de M4. Si charge M5 > 1000 users simultanés envisagée, envisager Datadog ou self-hosted APM (Elastic APM).

---

*Signé TL + SRE le 11 août 2026, validé Founder.*
