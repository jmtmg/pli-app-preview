# M4 — Checklist sécurité & conformité RGPD

**Propriétaire** : SEC · **Validé** : Founder · **Dépend de** : doc 11 (Threat Model), doc 12 (DPIA)
**Applicable du** : 12 août 2026 (J1 Sprint 9) **au** : 09 septembre 2026 (Checkpoint 4)

---

## 1. Rate-limiting — règles ferme

| Route | Limite | Fenêtre | Scope | Raison |
|---|---|---|---|---|
| `POST /waitlist` | 5 | 1 h | IP | Anti-spam bot |
| `GET /waitlist/confirm/{token}` | 20 | 1 h | IP | Brute-force prévention |
| `POST /invitations/redeem` | 10 | 1 h | user | Freiner brute-force code |
| `POST /feedback` | 3 | 1 h | user | Éviter spam intentionnel |
| `POST /feedback` (anonyme) | 3 | 1 h | IP | Idem sans user_id |
| `POST /auth/login` | 5 | 15 min | IP + email | Anti brute-force |
| `POST /auth/password_reset` | 3 | 1 h | email | Anti énumération |
| Global endpoints `/api/*` | 120 | 1 min | user/IP | Garde-fou DDoS léger |

**Implémentation** : middleware Redis + sliding window. Rejet : HTTP 429 + header `Retry-After`.

---

## 2. Anonymisation feedback — contrôle

Vérifications avant mise en prod des endpoints feedback/NPS :

- [ ] `user_id_hash` = `HMAC-SHA256(user_id, env_salt)` — audit code fait le 10/08
- [ ] `env_salt` présent dans secrets GitHub Actions pour staging **et** prod (rotatif 12 mois)
- [ ] Aucun champ PII additionnel (pas d'email, pas de nom) dans la table `feedback_submissions`
- [ ] Endpoint admin `/feedback/admin/nps` : require_admin + audit log de chaque accès
- [ ] Option `anonymous=true` → `user_id_hash=NULL` vérifié par test (`test_anonymous_feedback`)
- [ ] Logs applicatifs : aucun `user.email`, aucun body feedback brut (seulement id + kind + score agrégé)
- [ ] Rétention : 24 mois max (auto-purge), justifié dans la politique de conf.

---

## 3. Audit conformité RGPD — chat Crisp

Le chat Crisp étant un SaaS tiers, on doit valider :

- [ ] DPA Crisp signée (version ≥ juin 2026)
- [ ] Serveurs UE cochés dans Crisp Admin > Settings > Data Location
- [ ] Rétention conversations configurée à **90 jours** max
- [ ] Opt-in explicite utilisateur : bannière "Activer le chat" (pas chargé par défaut)
- [ ] Configuration anti-fingerprinting : IP + user-agent anonymisés côté Crisp
- [ ] Pas de transmission automatique de données hors contexte conversation (pas de sync contacts)
- [ ] Déclaration ajoutée dans `docs/legal/politique-confidentialite.md` §Sous-traitants
- [ ] Suppression compte user → purge conversation Crisp via API (job cron hebdo)

---

## 4. Audit endpoints nouveaux (M4)

Revue ligne à ligne des PR contenant :

| Endpoint | Review SEC | Checklist |
|---|---|---|
| `POST /waitlist` | ☑ (11 août) | input sanitization (email format), rate-limit, pas de retour d'erreur distinctif email existe/pas |
| `GET /waitlist/confirm/{token}` | ☑ | token HMAC 7 j, purpose locked, constant-time comparison |
| `POST /invitations/redeem` | ☑ | auth requise, brute-force protégé, code uppercase normalization, audit log |
| `POST /feedback` | ☑ | auth requise, rate-limit, message sanitizé (HTML escape côté affichage), score bornes |
| `POST /invitations/admin/issue` | ☑ | require_admin, audit log obligatoire, IP source loguée |
| Admin `/nps`, `/stats` | ☑ | require_admin, pas de user brut, export CSV audité |

---

## 5. Secrets & rotation

| Secret | Rotation | Propriétaire | État |
|---|---|---|---|
| `PLI_USER_HASH_SALT` | 12 mois | SEC | Tourné 21/07/2026 |
| `JWT_SECRET_KEY` | 6 mois | SEC | Tourné 10/07/2026 |
| `STRIPE_WEBHOOK_SECRET` | sur incident | BE + SEC | — |
| `POSTMARK_API_KEY` | 12 mois | SRE | Tourné 01/06/2026 |
| `DATABASE_URL` | sur incident | SRE | — |
| OAuth client secrets (Google, Microsoft) | 18 mois | BE + Founder | — |

Tous les secrets : GitHub Actions env secrets + Fly.io secrets (jamais dans le repo).

---

## 6. Logs & PII — revue finale

Contrôles automatisés (test CI) :

- [ ] Aucun header `Authorization` en logs structurés
- [ ] Aucune IP brute après 7 jours (rotation loki)
- [ ] Aucune occurrence de `@[a-z0-9.-]+\.[a-z]{2,}` dans logs applicatifs de production
- [ ] Aucune stack trace Sentry sans `data_masking_enabled`

---

## 7. Threat model delta M4

Nouveaux risques identifiés pour M4, à ajouter au doc 11 :

| Risque | Vecteur | Severity | Mitigation |
|---|---|---|---|
| Enum waitlist (détection "est-ce que X est inscrit ?") | réponse différente selon existence email | Moyen | Réponse identique + rate-limit strict |
| Brute-force code invitation (12 chars base32 ≈ 57 bits) | endpoint redeem | Faible | Rate-limit 10/h/user + expiration 14j |
| DoS sur endpoint feedback (beta users malveillants) | POST massif | Moyen | Rate-limit 3/h/user |
| Exfiltration NPS via endpoint admin | compte admin compromis | Haut | 2FA obligatoire sur comptes admin + audit log |
| Fuite de feedback libre contenant accidentellement PII tiers (email dans le message) | user tape par erreur | Faible | Pas de publication automatique, revue manuelle avant usage externe |

---

## 8. Sign-off

| Livrable | Date | Validateur |
|---|---|---|
| Rate-limit rules en prod | 11 août 2026 | SEC |
| Anonymisation feedback | 11 août 2026 | SEC + TL |
| Crisp DPA + config | 02 septembre 2026 (veille S21 release) | SEC + Founder |
| Threat model delta | 08 septembre 2026 | SEC + TL |
| Sign-off Go M5 | 09 septembre 2026 | SEC + Founder |

---

*Checklist M4 approuvée par SEC le 11 août 2026.*
