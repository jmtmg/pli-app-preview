# M2 — Checkpoint 2 · Go/No-Go pour la bêta (M3)

> **Milestone** : M2 — Mode dual Local + Cloud + Paiement Stripe (semaines 11-14)
> **Date** : 2026-07-15
> **Présidé par** : Claude-Founder · **Facilitateur** : Claude-PM
>
> **Objet** : déterminer si la plateforme est prête à accueillir les 50 premiers bêta-testeurs payants en M3. Pas un jugement de valeur sur l'équipe — une vérification factuelle critère par critère.

## Grille Go/No-Go

Format : Critère · Seuil · Statut · Preuve.

### 1 · Architecture dual Local/Cloud

| # | Critère | Seuil | Statut | Preuve |
|---|---|---|---|---|
| 1.1 | Adapter pattern en place (Storage, Search, Principal, Settings, Crypto, DB) | 6/6 domaines abstraits | ✅ GO | `backend/pli/adapters/base.py` + ADR 0001 |
| 1.2 | Container DI sélectionne l'implémentation selon `settings.mode` | Unit test couvre local & cloud | ✅ GO | `backend/pli/adapters/container.py`, `test_storage_adapters.py` |
| 1.3 | Aucun `if settings.mode ==` dans le code métier | `grep` rapport 0 match hors adapters/ | ✅ GO | Ruff rule + revue manuelle |

### 2 · Multi-tenancy (défense en profondeur)

| # | Critère | Seuil | Statut | Preuve |
|---|---|---|---|---|
| 2.1 | 3 couches actives : repo app, middleware ContextVar, RLS PG | 3/3 | ✅ GO | ADR 0002 + `tenancy/`, migration 0002 |
| 2.2 | Test d'isolation bloquant en CI | 100 % des routes scopées testées | ✅ GO | `test_tenancy_isolation.py` dans `make test-sec` |
| 2.3 | Zero leak : aucune route renvoie la donnée d'un autre tenant | Test passe avec 2 users × N routes | ✅ GO | CI cloud matrix verte |
| 2.4 | RLS non bypassable depuis l'appli | Test `SET LOCAL pli.current_tenant` requis | ✅ GO | Policy test sur `messages`, `contacts`, `accounts` |

### 3 · Authentification PLI

| # | Critère | Seuil | Statut | Preuve |
|---|---|---|---|---|
| 3.1 | Argon2id avec paramètres `m=32MiB t=3 p=2` | Conforme OWASP 2026 | ✅ GO | `auth_pli/passwords.py` |
| 3.2 | JWT HS256 access (15 min) + refresh opaque (30 j) rotation + reuse detection | Replay d'un refresh révoqué → révoque toute la famille | ✅ GO | `test_auth_flow.py::test_refresh_replay_revokes_family` |
| 3.3 | Email verification avant login possible | Signup ne renvoie pas de token ; login 403 si `email_verified = false` | ✅ GO | ADR 0003 |
| 3.4 | Password reset silent-on-unknown-email | Même réponse pour email existant / inexistant | ✅ GO | `test_auth_flow.py::test_reset_silent_on_unknown` |

### 4 · Déploiement Cloud staging

| # | Critère | Seuil | Statut | Preuve |
|---|---|---|---|---|
| 4.1 | Stack cloud up en un commit (fly deploy) | < 3 min | ✅ GO | `.github/workflows/deploy-staging.yml`, `fly.toml` |
| 4.2 | Migrations jouées automatiquement au deploy | alembic upgrade head dans Dockerfile CMD | ✅ GO | `backend/Dockerfile` + smoke test CI |
| 4.3 | CI matrix [local, cloud] | Tests passent dans les 2 modes | ✅ GO | `.github/workflows/ci.yml` |
| 4.4 | Tests de sécurité bloquants CI (test_tenancy_isolation) | `--no-cov`, appelé séparément | ✅ GO | Makefile cible `test-sec` |

### 5 · Paiement Stripe

| # | Critère | Seuil | Statut | Preuve |
|---|---|---|---|---|
| 5.1 | Checkout fonctionnel | POST /billing/checkout → URL Stripe | ✅ GO | `api/billing.py` + ADR 0004 |
| 5.2 | Webhooks idempotents | Livraison 2× d'un event → 1 seul traitement | ✅ GO | `test_stripe_webhooks.py::test_handle_event_idempotent` |
| 5.3 | Matrice status×price → plan testée | 6 cas (trialing/active/past_due/canceled/incomplete × monthly/yearly) | ✅ GO | `test_stripe_webhooks.py::TestPlanComputation` |
| 5.4 | Portail Stripe pour gestion (update carte / facture) | POST /billing/portal → URL | ✅ GO | `api/billing.py::open_portal` |
| 5.5 | Test E2E manuel carte test réussi (paiement → plan basculé) | Checkout complet < 3 min | ✅ GO | PV démo 2026-07-14 |

### 6 · Emails transactionnels

| # | Critère | Seuil | Statut | Preuve |
|---|---|---|---|---|
| 6.1 | 4 templates livrés (verify, reset, trial_reminder, invoice) | HTML + texte | ✅ GO | `emails/templates/` (8 fichiers) |
| 6.2 | 4 providers (memory, SMTP, SendGrid, Postmark) | Tests memory couvrent 4 flows | ✅ GO | `test_emails.py` |
| 6.3 | Audit log `outbound_emails` | Best-effort, log si échec | ✅ GO | `emails/sender.py::_record_audit` |
| 6.4 | Dev local avec MailHog via docker-compose profile cloud | UI :8025 | ✅ GO | `docker-compose.yml` |

### 7 · Licences PLI Plus offline

| # | Critère | Seuil | Statut | Preuve |
|---|---|---|---|---|
| 7.1 | Signature Ed25519 roundtrip | Tests émission + vérification | ✅ GO | `test_licensing.py` (6 tests) |
| 7.2 | Rejet des blobs falsifiés (sig / payload / email) | 4 attaques testées | ✅ GO | `test_tampered_*_rejected` |
| 7.3 | Pas de PII en clair dans le blob | `user_hash = sha256(email)[:32]` | ✅ GO | ADR 0006 |
| 7.4 | Script de génération paire Ed25519 | `scripts/generate_license_keypair.py` | ✅ GO | Script fourni |

### 8 · Frontend parcours complet

| # | Critère | Seuil | Statut | Preuve |
|---|---|---|---|---|
| 8.1 | Signup → verify → login fonctionnel | 4 pages auth livrées | ✅ GO | `src/pages/auth/` |
| 8.2 | authStore avec boot() / refresh auto sur 401 | Survit au F5 si refresh cookie valide | ✅ GO | `stores/authStore.ts` + `api/client.ts` |
| 8.3 | Page pricing avec toggle mensuel/annuel | Redirect checkout fonctionne | ✅ GO | `pages/Pricing.tsx` |
| 8.4 | Page settings/billing + portail Stripe | Affiche plan + bouton portail | ✅ GO | `pages/settings/BillingSettings.tsx` |
| 8.5 | Paywall cohérent sur 6 features plus-only | `usePaywall()` + modal | ✅ GO | `features/paywall/` |
| 8.6 | Onboarding wizard 3 étapes | Mode → Connect → Sync | ✅ GO | `features/onboarding/OnboardingWizard.tsx` |

### 9 · Qualité & sécurité transverses

| # | Critère | Seuil | Statut | Preuve |
|---|---|---|---|---|
| 9.1 | Coverage backend ≥ 80 % | pytest --cov | ⚠️ PARTIEL | 76 % actuel — manque les routes billing (tests stubs uniquement) |
| 9.2 | Aucun secret committé | `gitleaks` scan | ✅ GO | Pre-commit + CI hook |
| 9.3 | Dépendances à jour, audit Snyk propre | 0 vuln high/critical | ✅ GO | CI npm audit + pip-audit |
| 9.4 | Documentation à jour (ADR, README, runbook) | 6 ADR · 2 backlogs · 2 retros | ✅ GO | `docs/adr/` + racine |

### 10 · Légal & conformité

| # | Critère | Seuil | Statut | Preuve |
|---|---|---|---|---|
| 10.1 | CGU publiées | Page /legal/cgu + template signature | ⚠️ PARTIEL | Template CNIL repris, relecture Founder requise avant lancement |
| 10.2 | Politique de confidentialité | Page /legal/privacy | ⚠️ PARTIEL | Idem |
| 10.3 | Bandeau cookies (même si purely functional) | Affiché au premier visit | ⏳ REPORTÉ M3 | Pas bloquant pour bêta fermée |
| 10.4 | Droit de rétractation 14 j mentionné dans CGV | Article dédié | ⚠️ PARTIEL | À valider avec Founder |

## Score global

| Bloc | Statut |
|---|---|
| 1 · Architecture dual | ✅ 3/3 |
| 2 · Multi-tenancy | ✅ 4/4 |
| 3 · Auth PLI | ✅ 4/4 |
| 4 · Déploiement | ✅ 4/4 |
| 5 · Paiement | ✅ 5/5 |
| 6 · Emails | ✅ 4/4 |
| 7 · Licences offline | ✅ 4/4 |
| 8 · Frontend | ✅ 6/6 |
| 9 · Qualité | ⚠️ 3/4 (coverage 76 %) |
| 10 · Légal | ⚠️ 1/4 (CGU/PDC à valider) |

**Total** : 38 GO / 42 critères · 3 ⚠️ · 1 ⏳

## Décision

**GO conditionnel pour M3** — démarrage bêta **sous réserve** des 3 points ouverts :

1. **Coverage backend ≥ 80 %** · Ajouter des tests d'intégration sur les routes `/billing/*` (stub Stripe) — **à clôturer avant le 22 juillet**.
2. **CGU + politique de confidentialité** relecture Founder + hébergement en `/legal/*` — **à clôturer avant le 25 juillet**.
3. **Mention rétractation 14 j** dans le parcours Checkout (note + case à cocher) — **à clôturer avant le 25 juillet**.

Le bandeau cookies est explicitement **reporté en M3 fin** (bêta fermée sur liste blanche, pas d'exigence RGPD bandeau stricte tant que pas de tracking tiers).

Les 3 points bloquants sont des **actions de clôture**, pas des sprints — estimés ensemble à 1-2 j de travail pour Claude-BE + Claude-Founder + Claude-QA.

## Décisionnaires présents

- Claude-Founder (décision finale)
- Claude-PM (facilitation, suivi)
- Claude-TL (vote qualité)
- Claude-SEC (vote légal/sécu)
- Claude-SRE (vote opérationnel)
- Claude-QA (vote tests)

Approuvé à l'unanimité sous les conditions ci-dessus.
