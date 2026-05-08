# M5 — Checklist sécurité · Exposition publique

**Phase** : M5 (9 → 23 sept 2026)
**Owner** : SEC agent · **Approbations requises** : SEC + TL + Founder avant activation flag `public_signup_enabled`
**Version** : 1.1 (MàJ 2026-04-22, T5.4 ticket `M5-freeze.md` — couverture explicite du périmètre intégré M1-M5 sur `release-v1`)
**Référence** : doc 11 (Threat Model), doc 12 (DPIA), M5-KICKOFF §7 (Risques), ordre de mission `docs/governance/2026-04-22-ordre-mission.md`
**Périmètre** : binaire intégré **post integration-sprint** (flag `PLI_ENABLE_M2=1` sur `release-v1`). Les contrôles §3.8 à §3.8quater couvrent Stripe PCI scope, emails transactionnels SPF/DKIM/DMARC, licences Ed25519, tokens Fernet.

---

## 1. Objectif

L'exposition publique en M5 **étend fortement la surface d'attaque** par rapport à la beta privée (100 users triés) :

- Endpoints `/auth/signup`, `/auth/login`, `/auth/password-reset/request` exposés sans filtrage par invitation
- Risque d'abus : scripts bot de création massive, credential stuffing, énumération d'emails
- Risque de saturation : attaque volumétrique applicative
- Risque d'exfiltration : exploitation d'une faille dans un endpoint authentifié avec comptes de test
- Responsabilité augmentée : données de vrais utilisateurs payants à risque légal plus élevé

**Cette checklist doit être intégralement validée avant d'activer le flag d'ouverture publique.**

---

## 2. Rappel des principes de défense

| Principe | Traduction M5 |
|---|---|
| Défense en profondeur | WAF edge + rate limit app + validations entrée + isolation DB |
| Moindre privilège | JWT scope minimal, pas de super-user dans la DB applicative |
| Fail secure | Tous les défauts = deny (403/404), pas de fallback permissif |
| Observabilité sécurité | Audit logs sur endpoints sensibles, alertes sur patterns anormaux |
| Transparence utilisateur | Documentation publique des mesures RGPD, status page, CGU claires |

---

## 3. Checklist opérationnelle

### 3.1 Protection edge (Cloudflare)

- [ ] Mode SSL : Full (strict), certificats origin à jour
- [ ] HSTS activé, preload opt-in en post-Launch
- [ ] OWASP Core Rule Set activé, mode "block" sur score ≥ 15
- [ ] Règle WAF : block `User-Agent` connus des scrapers (pattern ciblé, pas trop large)
- [ ] Bot Fight Mode : activé sur endpoints critiques (`/auth/signup`, `/auth/password-reset/request`)
- [ ] Rate limiting Cloudflare : sur-couche applicative
  - [ ] `/auth/signup` : 10 req/min/IP au edge
  - [ ] `/auth/login` : 20 req/min/IP au edge
  - [ ] `/auth/password-reset/request` : 5 req/min/IP
- [ ] Geo-blocking (optionnel, configurable) : pays hors scope (CN, RU par défaut ? — décision founder)
- [ ] Cloudflare Turnstile (CAPTCHA) intégré sur :
  - [ ] `/auth/signup`
  - [ ] `/auth/password-reset/request`
  - [ ] `/waitlist/subscribe` (si applicable)
- [ ] "Under Attack Mode" : procédure d'activation documentée, bouton 1-clic dans runbook

### 3.2 Rate limiting applicatif (Redis token bucket)

- [ ] `/auth/signup` : 5 / 24h / IP, 50 / h / global
- [ ] `/auth/login` : 10 / 15 min / IP, 30 / 15 min / compte
- [ ] `/auth/password-reset/request` : 3 / h / IP, 3 / h / email
- [ ] `/auth/password-reset/confirm` : 10 / h / IP
- [ ] `/feedback` : 10 / min / user
- [ ] API authenticated general : 100 / min / user
- [ ] API sync endpoints : limites dédiées (cf. providers)
- [ ] Config DB `rate_limits` rechargée à chaud (TTL 30 s)
- [ ] Dashboard Grafana hits vs limits visible
- [ ] Alerte P2 si > 100 × limite dépassée sur 5 min

### 3.3 Validation & sanitization des entrées

- [ ] Pydantic models strict sur tous les payloads signup/login/reset
- [ ] Longueur max email : 254 car., password : 128 car.
- [ ] Password strength : zxcvbn ≥ 3 côté serveur (pas juste client)
- [ ] Honeypot field invisible sur formulaires signup/waitlist (block si rempli)
- [ ] Encodage HTML/XML sortant systématique (OWASP ESAPI-like)
- [ ] CSP stricte : default-src 'self', script-src 'self' nonce=..., pas d'unsafe-inline
- [ ] Pas de reflet paramètres URL non échappés dans les pages
- [ ] Validation server-side de tout ce qui est validé côté client

### 3.4 Authentification & sessions

- [ ] Argon2id avec paramètres OWASP 2025 (m=64MB, t=3, p=2)
- [ ] Salt unique par user (géré par lib argon2)
- [ ] Password breach check : API HIBP k-anonymity au signup (bloque si breach)
- [ ] JWT access token : 15 min TTL, HS256 avec secret 64+ char, clock skew 30 s
- [ ] JWT refresh token : 30 j TTL, httpOnly, Secure, SameSite=Lax
- [ ] Rotation refresh token à chaque refresh, ancien ajouté `revoked_tokens`
- [ ] Détection réutilisation refresh révoqué → invalidation session entière + alerte
- [ ] Endpoint `/auth/logout` invalide toutes les sessions de l'user (option "tous les appareils")
- [ ] Notification email (opt-in) sur nouvelle connexion depuis IP inconnue
- [ ] 2FA TOTP : **pas requis en M5** (reporté M3 bis / post-Launch), mais endpoints préparés
- [ ] Throttling login : 5 tentatives / 15 min / IP → 429 + CAPTCHA obligatoire
- [ ] Anti-timing attack : comparaison constant-time sur login (éviter révélation email existant)

### 3.5 Isolation multi-tenant (M2 durci)

- [ ] Middleware `tenant_context` injecté depuis JWT à chaque requête authed
- [ ] Repositories forcent `WHERE user_id = :tenant` systématiquement
- [ ] Row-Level Security PostgreSQL activé comme défense en profondeur
- [ ] Test `test_tenancy_isolation.py` exécuté à chaque déploiement (part du smoke test)
- [ ] Test synthétique en prod : compte A tente lecture compte B toutes les 15 min → doit échouer
- [ ] Alerte P1 si test synthétique isolation échoue (cf. runbook §6.6)
- [ ] Revue code : aucune query SQL raw sans filtre tenant

### 3.6 Protection données au repos & en transit

- [ ] TLS 1.3 partout, HSTS + preload
- [ ] PostgreSQL : chiffrement at-rest activé (provider managed ou LUKS)
- [ ] S3 objets : server-side encryption activée (SSE-S3 ou SSE-KMS)
- [ ] Secrets applicatifs : gestion via Fly secrets / Vault / 1Password, rotation documentée
- [ ] Logs : pas de PII en clair (emails masqués, no password ni token)
- [ ] Backups chiffrés, testés en restore (test mensuel)
- [ ] Mode Local : SQLite + SQLCipher, clé dérivée password user

### 3.7 Anti-abus et abus comportemental

- [ ] Vérif email obligatoire avant usage fonctionnel (déjà M2, durci : trial ne démarre qu'après vérif)
- [ ] Détection patterns suspects :
  - [ ] Multiples signups même IP en < 1 min
  - [ ] Emails avec patterns jetables (domaines disposables tracés, alerte)
  - [ ] Formulaires remplis en < 2 s (bot probable)
- [ ] Endpoint admin ban : `POST /admin/ban` (IP CIDR, email pattern, user_id)
- [ ] Audit log enrichi : `/admin/*` actions, `/billing/*`, `/auth/*`, changements sensibles
- [ ] Retention audit logs : 12 mois minimum, séparés du log applicatif

### 3.8 Paiement (Stripe live) — **PCI scope délimité (MàJ T5.4)**

- [ ] Mode **live** activé uniquement pour compte Stripe validé KYC
- [ ] Webhooks Stripe signés, vérification `stripe.Webhook.construct_event`
- [ ] Idempotence : table `processed_stripe_events` avec event_id, rejoindre si déjà traité
- [ ] Pas de stockage CB côté PLI (Stripe Checkout hosted page)
- [ ] Pas de champ carte dans la DB PLI, même chiffré
- [ ] 3DS activé (Stripe Radar rules par défaut + règles sur patterns fraud)
- [ ] Dashboard Stripe Radar surveillé quotidiennement M5

**Périmètre PCI DSS — délimitation explicite (binaire intégré M2)** :

- [ ] **PLI est PCI DSS SAQ-A** : confirmation écrite dans `docs/adr/0004-stripe-integration.md`. SAQ-A = commerçant qui délègue **entièrement** la capture, le stockage et le traitement des PAN à Stripe, via iframe / redirect Checkout. Pas de champ carte sur nos pages.
- [ ] **Aucune donnée titulaire carte (CHD)** ne transite par nos serveurs ou notre domaine. Confirmation par audit Wireshark du trafic Checkout (exercice SEC avant J5).
- [ ] **Aucune donnée sensible d'authentification (SAD)** — CVV, piste magnétique, PIN — n'est demandée, reçue ou stockée.
- [ ] Tokens Stripe (`pi_*`, `cus_*`, `sub_*`) stockés DB en clair (ce ne sont pas des CHD) mais **scopés par tenant** (FK sur `tenant_id`).
- [ ] `STRIPE_SECRET_KEY` et `STRIPE_WEBHOOK_SECRET` stockés en secret manager (jamais en repo, jamais en ENV committed). Rotation prévue post-Launch.
- [ ] Dépendance stripe SDK à jour en CI, patch immédiat si CVE.
- [ ] Tests chaos Stripe couverts runbook §13.3 (signature KO, backlog) et exercices D1-D2 (§13.7).

### 3.8bis Emails transactionnels (M2 — ajout T5.4)

- [ ] Provider primaire Postmark, secondaire Resend. Clés API en secret manager, scopes restreints à envoi transactionnel.
- [ ] **SPF** : `v=spf1 include:servers.postmarkapp.com include:amazonses.com -all` publié sur `mail.pli.app`. Vérif `dig TXT mail.pli.app` avant chaque vague.
- [ ] **DKIM** : clé publique DKIM publiée, rotation selon recos Postmark. Signature vérifiable sur mails sortants (test auto `ses-headers-check`).
- [ ] **DMARC** : `v=DMARC1; p=quarantine; rua=mailto:dmarc@pli.app` actif. Rapports DMARC consultés hebdo (PM/SEC), fail unauthorized > 1 % déclenche revue.
- [ ] **Pas de contenu utilisateur quelconque** (ex. contenu d'email du user) dans un email transactionnel — risque fuite par forwarding accidentel. Seulement données transactionnelles.
- [ ] Template `password_reset` : lien signé HMAC, usage unique, TTL 30 min, révocation au premier usage. Testé D8 (tenancy) : pas de leak cross-tenant dans le corps.
- [ ] Bounce rate global < 2 % sur 7 jours glissants. > 5 % → alerte §13.4 runbook.
- [ ] Liste de distribution signups jamais exportable depuis l'admin sans double signature direction + SEC.

### 3.8ter Licences Local Ed25519 (M2 — ajout T5.4)

- [ ] **Clé privée Ed25519** en HSM/KMS (AWS KMS ou équivalent FIPS 140-2 L2+). Jamais exportable. Jamais dans un log, même tronquée. Audit automatique CI `grep -ri 'ed25519-priv\|BEGIN.*PRIVATE KEY' logs/` → 0 match requis.
- [ ] **Clé publique Ed25519** embarquée dans le binaire client (desktop PWA/Tauri futur, app Local) via constante compilée. Distribution par release signée.
- [ ] **Rotation** avec overlap ≥ 30 jours : la table `licensing_keys` gère `kid`, `public_key`, `active_from`, `active_until`. Le serveur accepte toute licence signée par une clé `active_from ≤ now ≤ active_until`.
- [ ] Licence contient : `user_id`, `plan`, `issued_at`, `expires_at`, `kid`. Signée sur concaténation canonique. Pas de donnée perso additionnelle (minimal).
- [ ] Endpoint `GET /api/licensing/verify` : rate limité, pas d'oracle (réponse uniforme, pas de message détaillé "signature invalide vs expirée" côté user — ça passe seulement côté log serveur).
- [ ] Exercice **D5 + D6** (runbook §13.7) passés en staging avant ouverture Beta.
- [ ] ADR `docs/adr/0006-licences-offline-ed25519.md` revu par SEC avant 2026-08-26 (freeze).

### 3.8quater Tokens Fernet applicatifs (Gmail/MS refresh tokens — MàJ T5.4)

- [ ] Tokens OAuth refresh Gmail / Microsoft chiffrés en DB par **Fernet** via `LocalCryptoAdapter` (cf. `docs/adr/0003-jwt-sessions.md` et note Sprint 1 planning §4).
- [ ] Clé Fernet rotation prévue : 2 clés simultanées (`FERNET_KEY_CURRENT`, `FERNET_KEY_PREVIOUS`) pour déchiffrage rétro. Rotation trimestrielle post-Launch.
- [ ] Clés Fernet en secret manager, jamais en ENV committed.
- [ ] En mode Local : clé Fernet dans `~/.pli/crypto.key` permissions `0600`, jamais transmise au serveur.
- [ ] En mode Cloud : clé Fernet dans KMS, déchiffrement à la volée, jamais loguée. `cloud_crypto_key` manquant → refus de démarrage du process (circuit breaker).
- [ ] Audit automatique CI : `pytest backend/tests/test_crypto_no_plaintext_tokens.py` vérifie qu'aucun `refresh_token` n'est stocké en clair dans la DB.

### 3.9 RGPD opérationnel (M3 durci)

- [ ] Mentions légales + CGU + politique conf publiées et lues à signup (case obligatoire)
- [ ] Droit à l'effacement : endpoint user `/settings/delete-account`, exécution < 30 j
- [ ] Droit à la portabilité : endpoint `/settings/export` → ZIP EML + vCard + JSON
- [ ] Registre de traitement tenu à jour (doc 12 DPIA)
- [ ] DPO email opérationnel : `dpo@pli.app` (= founder en pratique)
- [ ] Processus notification CNIL en 72 h prêt (template + procédure)
- [ ] Cookies : bannière minimale (essentiels + analytics anonymisés type Plausible = OK sans consent)
- [ ] Pas de tracker tiers côté marketing (pas de Google Analytics, Facebook Pixel, etc.)

### 3.10 Observabilité sécurité

- [ ] Sentry : alertes sur exceptions dans modules `auth/`, `billing/`, `admin/`
- [ ] Logs SIEM (Better Stack) : queries sauvegardées :
  - [ ] "5xx en rafale"
  - [ ] "Login failed > 3 par compte en 5 min"
  - [ ] "Webhook Stripe signature invalide"
  - [ ] "Admin action hors horaires ouvrés" (alerte stricte)
  - [ ] "Pattern `' OR 1=1`, `<script>`, `../../` dans query params" (SQLi / XSS / path traversal)
- [ ] Alertes Slack #security sur queries ci-dessus
- [ ] Review hebdo des top events Sentry / SIEM par SEC agent

### 3.11 Gestion de vulnérabilités

- [ ] Dependabot / Renovate actif sur repo, auto-merge patches mineurs
- [ ] CVE watch : outil `pip-audit` / `npm audit` en CI, échec si HIGH+ non remédiée
- [ ] Page `/security.txt` conforme RFC 9116 : contact, politique, disclosure
- [ ] Programme de disclosure responsable (pas de bug bounty en M5, mais contact clair)
- [ ] Scan images Docker (Trivy ou similaire) en CI, HIGH+ bloquant

### 3.12 Chaos & résilience

- [ ] Test de chaos exécuté avant ouverture (cf. Runbook §12)
- [ ] Kill switch feature flag `read_only_mode` testé en staging
- [ ] Procédure rollback testée (cf. Runbook §7)
- [ ] Snapshot DB avant chaque déploiement M5
- [ ] Restauration partielle testée dans les 24 h précédant ouverture

---

## 4. Revue pré-ouverture (J5)

Jalon formel à exécuter **le 15 septembre 2026 (J5)** avant activation du flag. Tous les points ci-dessus doivent être cochés.

**Participants** : SEC agent, TL, SRE, Founder.
**Format** : 1 h, revue point par point.
**Décision** : Go / No-Go ouverture.
**Si No-Go** : repousser activation de 48 h max, issues critiques traitées.

---

## 5. Revue hebdomadaire M5

Les vendredis J5 et J10, SEC agent publie un **security digest** court :

- Nombre de tentatives login bloquées
- Nombre IP bannies
- Incidents SEC observés (0 idéal)
- Top anomalies SIEM
- Vulnérabilités dependencies remédiées / ouvertes
- Recommandations pour la semaine suivante

---

## 6. Plan de réponse incident SEC

### Niveau 1 — Anomalie isolée
- Ex. 1 IP tentant 50 signups → ban IP, aucune communication
- Owner : SEC agent, autonome

### Niveau 2 — Attaque volumétrique
- Ex. scan massif formulaires, DDoS applicatif
- Owner : SEC agent + SRE
- Actions : durcir WAF, mode "under attack" Cloudflare si besoin, pas de communication publique sauf impact user

### Niveau 3 — Exfiltration suspectée
- Ex. requêtes anormales cross-tenant détectées, signalement user "j'ai vu les mails d'un autre"
- Owner : TL + SEC agent + Founder
- Actions : activation `read_only_mode`, préservation des preuves, investigation, consultation DPO
- Communication : notification CNIL sous 72 h si confirmé, communication publique dans 48 h max

### Niveau 4 — Fuite confirmée
- Ex. dump trouvé en ligne, accès admin compromis
- Owner : Founder (assisté)
- Actions : gel complet, rotation secrets, notification utilisateurs impactés, CNIL, avocat
- Communication : transparente, factuelle, sans spéculation

---

## 7. Engagements externes

- [ ] Page `/security` publiée : principes, mesures en place, contact disclosure
- [ ] Page `/legal/privacy` conforme RGPD, relue par conseil juridique
- [ ] Badge SSL Labs A+ visible (auto-check mensuel)
- [ ] Pas d'assertion marketing sécurité non fondée ("inviolable", "100 % sécurisé", etc.)

---

## 8. Notes SEC pour M5

- **La sécurité absolue n'existe pas.** Notre objectif : réduire le risque à un niveau acceptable, détecter vite, réagir bien, communiquer honnêtement.
- **Les incidents arriveront.** Ce qui compte : temps détection, temps résolution, qualité du post-mortem.
- **L'utilisateur est un allié, pas un risque.** Respecter sa vie privée, minimiser sa friction, être transparent sur les collectes.
- **Le founder ne fait pas la sécurité seul.** Les agents SEC/SRE/TL ont autorité pour bloquer un déploiement. Ce pouvoir est respecté.

---

*Checklist rédigée par SEC agent. Revue et signée par TL, SRE et Founder le 15 septembre 2026 avant activation flag.*
