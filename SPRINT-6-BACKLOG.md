# Sprint 6 — Paiement, licences, onboarding payant (semaines 13-14)

> **Objectif sprint** · On passe de "plateforme multi-tenant qui fonctionne" à **"plateforme qui encaisse sans qu'on touche"**. Une personne doit pouvoir découvrir PLI → s'inscrire → payer → accéder à Plus en 3 minutes, et recevoir une licence Ed25519 si elle veut l'utiliser en mode Local offline.
>
> **Go condition sortie Sprint 6 / M2** · Un test manuel E2E (carte Stripe de test) boucle du `/pricing` jusqu'à la réception d'un email de facture et la bascule `users.plan = "plus_monthly"`, sans intervention.

## Équipe & responsabilités

| Rôle | Porteur | Focus du sprint |
|---|---|---|
| PM | Claude-PM | Suivi vélocité, démo Checkpoint 2, CGV + mentions légales |
| TL | Claude-TL | Arbitrages intégration Stripe, revues de code |
| BE | Claude-BE | Stripe Checkout, webhooks idempotents, emails, licences |
| FE | Claude-FE | Pages auth, pricing, onboarding wizard, settings billing, paywall |
| QA | Claude-QA | Tests webhooks idempotents, signature Ed25519, E2E Playwright |
| UX | Claude-UX | Copywriting pricing, microcopy paywall, flow onboarding |
| SRE | Claude-SRE | Secrets Fly.io (Stripe, license keys), runbook incidents paiement |
| SEC | Claude-SEC | Revue surface d'attaque webhooks, stockage licence, signature |
| Founder | Claude-Founder | Validation prix, positionnement CGV, décision trial period |

## User stories

### US-6.1 — Stripe Checkout opérationnel (8 pts) — BE

**En tant que** visiteur intéressé par PLI Plus
**Je veux** cliquer "Essayer Plus" depuis /pricing et me retrouver sur Checkout
**Afin de** m'abonner en 30 secondes sans friction.

**Critères d'acceptation** :
- [x] POST `/billing/checkout` → 200 `{url, session_id}`.
- [x] `customer_email` prérempli, `metadata.pli_user_id` + `metadata.pli_tenant_id` injectées.
- [x] `trial_period_days = PLI_STRIPE_TRIAL_DAYS` (14 par défaut).
- [x] Idempotency key `checkout:{user_id}:{plan}` — un user qui clique 2× ne crée pas 2 sessions.
- [x] `success_url` et `cancel_url` configurables (fallback sur `settings.app_url`).
- [x] 404 en mode local (feature-flag via `_require_cloud()`).

### US-6.2 — Webhooks Stripe idempotents (8 pts) — BE

**En tant que** système
**Je veux** que chaque event Stripe soit traité exactement une fois
**Afin d'**éviter les doublons d'email, les doubles licences, les plans incohérents.

**Critères d'acceptation** :
- [x] Table `webhook_events (event_id PK, event_type, received_at)` avec UNIQUE sur event_id.
- [x] Dispatcher insère d'abord l'event, dispatch uniquement si première occurrence.
- [x] Handlers gérés : `checkout.session.completed`, `customer.subscription.{created,updated,trial_will_end,deleted}`, `invoice.{paid,payment_succeeded,payment_failed}`.
- [x] `plan_from_subscription_status` dérive le plan PLI : trialing→plus_trial, active→plus_{monthly|yearly}, past_due→grace (on garde le plan), canceled/unpaid/incomplete→free.
- [x] Signature vérifiée via `construct_event()` + `PLI_STRIPE_WEBHOOK_SECRET`.
- [x] Un test simule 2 livraisons du même event → une seule exécution du handler.
- [x] Un test vérifie la matrice status×price → plan (6 cas).

### US-6.3 — Emails transactionnels (5 pts) — BE / UX

**En tant qu'** utilisateur
**Je veux** recevoir un email propre à chaque étape (vérification, reset, rappel essai, facture)
**Afin de** savoir où j'en suis.

**Critères d'acceptation** :
- [x] Interface `EmailProvider` + 4 implémentations : memory (tests), SMTP (MailHog dev), SendGrid, Postmark.
- [x] 4 templates fournis en HTML + texte : `verify`, `password_reset`, `trial_reminder`, `invoice`.
- [x] Chaque envoi loggue `outbound_emails (template, to, subject, provider_msg_id, status)`.
- [x] Audit log best-effort — une exception au log ne bloque jamais le flux métier.
- [x] Pluralisation correcte ("se termine demain" vs "dans 3 jours").
- [x] Tests `test_emails.py` couvrent les 4 templates + singulier/pluriel.

### US-6.4 — Licences PLI Plus offline (5 pts) — BE / SEC

**En tant qu'** utilisateur PLI Local
**Je veux** pouvoir utiliser PLI Plus sans connexion internet
**Afin de** travailler dans un avion ou derrière un firewall restrictif.

**Critères d'acceptation** :
- [x] Paire Ed25519 générée via `scripts/generate_license_keypair.py`.
- [x] POST `/licenses/issue` (cloud) émet un blob `{payload, sig}` si user a un abonnement actif.
- [x] POST `/licenses/activate` (local) vérifie la signature avec la clé publique embarquée, persiste dans `~/.pli/license.json` (chmod 0600).
- [x] GET `/licenses/status` (local) renvoie le plan courant offline.
- [x] Tests : roundtrip signing, rejet signature falsifiée, rejet payload falsifié (escalade), rejet email mismatch, rejet cross-keypair, expiration.
- [x] Le `user_hash` est un SHA-256 tronqué de l'email — pas de PII en clair dans la licence.

### US-6.5 — Pages auth (signup, login, reset, verify) (5 pts) — FE / UX

**En tant que** nouveau user
**Je veux** un parcours d'inscription simple, avec indicateur de force du mdp et vérification email
**Afin de** ne pas abandonner en route.

**Critères d'acceptation** :
- [x] Page Signup avec règles en live (≥12 chars, 1 maj, 1 chiffre, 1 symbole).
- [x] Page Login avec lien "Mot de passe oublié ?".
- [x] Page "Check your inbox" post-signup.
- [x] Page Verify — click sur le lien email → `POST /auth/verify`.
- [x] Pages RequestReset / ConfirmReset — affichent toujours le même message (silent on unknown email).
- [x] Store Zustand `authStore` avec `boot()` qui tente `/auth/refresh` au démarrage.
- [x] Client HTTP fait du retry automatique sur 401 via `/auth/refresh` (1 seule tentative).

### US-6.6 — Pricing + Checkout UX (3 pts) — FE / UX

**En tant que** visiteur
**Je veux** comprendre en < 30 s ce que vaut PLI Plus et combien ça coûte
**Afin de** prendre ma décision sans devoir ouvrir un ticket.

**Critères d'acceptation** :
- [x] Page `/pricing` avec toggle mensuel/annuel, badge "−17%" sur l'annuel.
- [x] Comparaison Free vs Plus en 2 colonnes, features en liste.
- [x] CTA "Essayer 14 jours" — si non loggué → signup, sinon → POST /billing/checkout → redirect Stripe.
- [x] Microcopy rassurant : "Paiements traités par Stripe. Aucun numéro de carte n'est stocké sur nos serveurs."

### US-6.7 — Settings → Billing + portail Stripe (3 pts) — FE

**En tant qu'** abonné
**Je veux** voir mon plan, changer de carte, télécharger mes factures
**Afin de** gérer ma facturation sans email à payments@.

**Critères d'acceptation** :
- [x] Page `/settings/billing` affiche plan courant, fin d'essai ou prochain prélèvement.
- [x] Bouton "Ouvrir le portail Stripe" → POST `/billing/portal` → redirect.
- [x] Toast de succès si `?status=success` dans l'URL (retour Checkout).
- [x] Si plan = free → gros CTA "Passer sur Plus".

### US-6.8 — Onboarding wizard 3-étapes (3 pts) — FE / UX

**En tant que** user qui vient de s'inscrire
**Je veux** être guidé pour connecter mon 1er compte email
**Afin de** voir la valeur de PLI avant d'oublier pourquoi je me suis inscrit.

**Critères d'acceptation** :
- [x] 3 étapes visibles en progress dots : Mode → Connect → Sync.
- [x] Étape 1 — explication Local vs Cloud (une seule visible selon le build).
- [x] Étape 2 — boutons Google / Microsoft OAuth.
- [x] Étape 3 — poll `/sync/status`, barre de progression, bouton "Ouvrir ma boîte" dès >= 10 messages.
- [x] State persistant dans localStorage — F5 ne perd pas la progression.

### US-6.9 — Paywall modal + feature flags côté frontend (2 pts) — FE / UX

**En tant qu'** utilisateur Free
**Je veux** comprendre *pourquoi* une action est bloquée et comment la débloquer
**Afin de** ne pas ressentir PLI comme un chantier incomplet.

**Critères d'acceptation** :
- [x] Hook `usePaywall()` — `check(reason)` retourne false + ouvre la modale si besoin Plus.
- [x] 6 raisons couvertes : `multiple_accounts`, `full_history`, `fts_search`, `rules`, `large_attachment`, `offline_license`.
- [x] Copy précis par raison — jamais "upgrade to continue", toujours dit quoi ça débloque.
- [x] Bouton principal : "Essayer 14 jours" (si Free) ou "Activer l'abonnement" (si trial).

### US-6.10 — Rétro + Checkpoint 2 Go/No-Go (2 pts) — PM

**En tant qu'** équipe
**Je veux** fermer M2 avec une grille Go/No-Go remplie
**Afin de** ne pas démarrer M3 (bêta-test) sur des bases fragiles.

**Critères d'acceptation** :
- [ ] `M2-CHECKPOINT.md` rempli — grille critères / statut / preuve.
- [ ] `M2-RETRO.md` rédigé — ce qui a marché / ce qu'on referait autrement / suites.
- [ ] `00-INDEX.md` mis à jour.
- [ ] Démo courte enregistrée : inscription → paiement carte test → bascule plan (2 min max).

## Planning

| Jour | Focus | Livrables |
|---|---|---|
| 1 | Stripe Checkout + plans.py | Route POST /billing/checkout, tests unitaires plans |
| 2 | Webhooks idempotents | Dispatcher, handlers, tests idempotence |
| 3 | Emails + templates | Provider + 4 templates + test_emails.py |
| 4 | Licences Ed25519 | local_key.py, api/licensing.py, test_licensing.py |
| 5 | Pages auth front | Signup, Login, Verify, Reset — authStore |
| 6 | Pricing + paywall | /pricing, PaywallModal, usePaywall |
| 7 | Settings billing + portail | /settings/billing |
| 8 | Onboarding wizard | 3 étapes + poll /sync/status |
| 9 | E2E manuel + playwright | cartes test Stripe → bascule plan |
| 10 | Rétro + CHECKPOINT | démo Founder, Go/No-Go |

## Risques Sprint 6

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Webhook Stripe mal signé → plan non basculé | Moyen | Critique | Test signature CI + alerte Sentry sur 400 du webhook |
| Email transactional provider down → user bloqué | Faible | Majeur | Fallback SMTP → SendGrid si PLI_EMAIL_PROVIDER_FALLBACK défini (post-M2) |
| Licence Ed25519 compromise (clé privée fuite) | Très faible | Critique | Rotation documentée, clé stockée uniquement dans secrets Fly.io |
| Onboarding trop long → abandon | Moyen | Moyen | Étape "Plus tard" sur Connect, sync en arrière-plan |
| Dérive CGV / droit rétractation 14j | Moyen | Majeur | CGV rédigées sur base template CNIL + relecture Founder |
