# Runbook — Launch M5 (Beta publique puis Go-live)

**Version** : 1.0 · **Propriétaire** : SRE · **Validé** : Founder + TL
**Période d'applicabilité** : 09 septembre 2026 → 07 octobre 2026 (M5 + 1 semaine post-launch)

---

## 1. Astreinte informelle 7j/7

- **Oncall principal** : Founder (JM)
- **Backup oncall** : TL (agent)
- **Horaires surveillance accrue** : 8h-22h CET (fenêtres de pic d'usage)
- **Nuit** : alertes P1 uniquement, pas de P2

### Canaux

- Notification **P1** : PagerDuty (SMS + call) + Discord `#alerts` + email `founder@pli.app`
- Notification **P2** : Discord `#alerts` uniquement
- Notification **P3** : Discord `#alerts`, pas de push

### Response time SLO

| Sévérité | Ack | Mitigation | Résolution |
|---|---|---|---|
| P1 | < 5 min (jour) / < 15 min (nuit) | < 30 min | < 2 h |
| P2 | < 30 min | < 2 h | < 24 h |
| P3 | < 4 h | — | Next sprint |

---

## 2. Procédures incident les plus probables

### 2.1 5xx rate > 1%

```bash
# 1. Confirmer dans Grafana > Performance p95
# 2. Voir stack trace Sentry
# 3. Identifier le commit de release
git log --oneline -10
# 4. Rollback si release < 2h
kubectl rollout undo deployment/pli-backend
# ou
fly deploy --image <previous-sha>
```

Communication beta : message Discord `#annonces` dans les 15 min même sans root cause.

### 2.2 Sync Gmail/Microsoft down

1. Vérifier status.google.com / status.office.com
2. Vérifier quotas OAuth dans la console Cloud
3. Si quota atteint : demander augmentation + activer backoff plus agressif (feature flag `sync.aggressive_backoff`)
4. Pas de panic — sync reprend automatiquement, pas de perte de données

### 2.3 DB connections saturé

```bash
# Inspection
psql $DATABASE_URL -c "select count(*) from pg_stat_activity;"
psql $DATABASE_URL -c "select pid, state, wait_event, query from pg_stat_activity where state != 'idle';"

# Kill queries longues
psql $DATABASE_URL -c "select pg_terminate_backend(<pid>);"

# Augmentation pool app (si sous-dimensionné)
# éditer config + redéployer
```

### 2.4 Stripe webhook en échec

1. Vérifier la signature : clé `STRIPE_WEBHOOK_SECRET` dans secrets envs
2. Vérifier Stripe Dashboard > Developers > Webhooks > logs
3. Rejouer les évènements depuis Stripe Dashboard si échec transient
4. Si signature invalide en cascade : révoquer + recréer endpoint webhook

### 2.5 Alerte disk space

```bash
# 1. Identifier gros consommateurs
df -h
du -sh /var/log/* | sort -h
# 2. Rotation logs aggressive
journalctl --vacuum-time=3d
# 3. Si persiste : snapshot + upgrade disque Hetzner
```

### 2.6 Certificat TLS expire < 7j

Renouvellement Let's Encrypt auto via cert-manager. Si échec :
```bash
kubectl logs -n cert-manager deploy/cert-manager-controller
# Si blocant : certbot manuel
certbot renew --force-renewal -d pli.app -d *.pli.app
```

---

## 3. Checklist launch day (J-7 → J0)

### J-7 (02 octobre 2026)

- [ ] Load test 500 users simultanés sur staging → cible p95 < 500 ms
- [ ] Backup DB vérifié (restore dry-run sur env restore)
- [ ] Certificats TLS expire > 30 j
- [ ] Secrets tournés si nécessaire (AGE > 90 j)
- [ ] Quotas OAuth Google / Microsoft augmentés demande envoyée
- [ ] Status page publique créée (statuspage.io ou self-hosted)
- [ ] Kit presse envoyé à 5 journalistes tech FR ciblés

### J-3 (04 octobre 2026)

- [ ] Feature freeze complet (plus aucun merge feature)
- [ ] Release finale déployée en staging + soak 48 h
- [ ] Assets ProductHunt + Hacker News finalisés
- [ ] Teaser LinkedIn programmé (dimanche 20h CET)

### J-1 (06 octobre 2026)

- [ ] Release finale en prod + soak 24 h
- [ ] Monitoring : dashboards Beta Overview, Perf, Errors vérifiés
- [ ] Alertmanager : route SMS testée
- [ ] Status page : sous-statut "opérationnel" sur tous composants
- [ ] Founder : coup de fil support 1 ami beta user (témoin)

### J0 (07 octobre 2026)

- [ ] 06h CET — bascule Stripe live
- [ ] 07h CET — publication ProductHunt
- [ ] 08h CET — post Hacker News Show HN
- [ ] 09h CET — annonce LinkedIn founder
- [ ] 10h CET — newsletter beta users (témoins, appel au partage)
- [ ] Support : 1 founder + 1 CONT agent en mode reactive
- [ ] Fréquence check dashboards : toutes les 30 min

### J+1 à J+7

- [ ] Check quotidien des métriques launch : signups, conversion, NPS
- [ ] Réponse < 2 h à toute mention presse / ProductHunt / HN
- [ ] Patch releases autorisées (seuil bas), pas de feature
- [ ] Rétrospective launch à J+7

---

## 4. Numéros d'urgence

| Rôle | Contact | Quand |
|---|---|---|
| Founder | +33 X XX XX XX XX (SMS PagerDuty) | P1 always |
| TL (agent) | Discord `@tl` ou `tl@pli.app` | P1 backup, P2 primaire |
| Hébergeur (Hetzner) | support@hetzner.com + ticket console | P1 infra |
| Stripe support | dashboard.stripe.com > Help | P1 paiement |
| Avocat RGPD | me@cabinet-xxx.fr (sous contrat) | Breach données |

---

## 5. Comms publiques en cas d'incident

### Modèle message Discord `#annonces`

> 🛑 **Incident en cours** : {description courte, neutre}
> **Début détecté** : {heure}
> **Impact** : {ce qui est cassé}
> **Statut** : Enquête · Identification · Correction · Fermé
> **Mise à jour** : toutes les 30 min
> **Status page** : status.pli.app

### Modèle tweet / LinkedIn

> On rencontre un incident sur {composant}. On est dessus. Détails et mises à jour sur status.pli.app. Merci de votre patience.

### Règle dorée

> **Pas de blame, pas de hype, pas de promesse de timing qu'on ne tiendra pas.** Communiquer souvent, brièvement, honnêtement.

---

## 6. Post-mortem

Tout incident P1 déclenche un post-mortem blameless sous 48 h, publié dans `docs/post-mortems/YYYY-MM-DD-<slug>.md`, comportant :

- Timeline (minute par minute)
- Root cause (5 whys)
- Impact (users, durée, données)
- Ce qui a bien marché
- Ce qu'on change dans les 30 jours

---

*Runbook approuvé par SRE + Founder le 08 septembre 2026. Révisé après chaque incident P1.*
