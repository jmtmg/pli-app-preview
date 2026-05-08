# M2 — Kickoff · Mode dual Local + Cloud & Paiement

**Phase** : M2 (semaines 11 → 14, 4 semaines)
**Démarrage** : 17 juin 2026 (après validation Go M1 / Checkpoint 1)
**Fin cible** : 15 juillet 2026
**Doc de référence** : [05-Roadmap.md](../../05-Roadmap.md) §3 — Phase M2
**Jalon suivant** : Checkpoint 2 (fin S14) — Go/No-Go M3

---

## 1. Objectif de M2

> **Basculer l'architecture en mode dual (Local only ↔ Cloud), livrer l'authentification PLI, intégrer Stripe bout-en-bout, et ouvrir un parcours onboarding permettant à un nouvel utilisateur de créer un compte, démarrer un trial 14 j, souscrire et piloter son abonnement.**

À la fin de M2, un utilisateur externe (non founder) doit pouvoir **s'inscrire, choisir Local ou Cloud, connecter un compte mail et payer** — c'est le Go/No-Go du Checkpoint 2 (S14).

M2 est court (4 semaines / 2 sprints) mais structurellement critique : il transforme le MVP mono-utilisateur en produit commercialisable.

---

## 2. Répartition de l'équipe d'agents

| Rôle | Agent | Périmètre M2 | Livrables clés |
|---|---|---|---|
| **Product Manager** | PM | Priorisation trial/paywall, pricing, validation acceptance | Backlog Sprints 5-6, pricing page copy, critères acceptance |
| **Tech Lead** | TL | ADR adapters Local/Cloud, revues PR refactor critique | ADR multi-tenancy, ADR adapters, code owner |
| **Backend Engineer** | BE | PostgreSQL, multi-tenant, auth PLI, JWT, Stripe, webhooks | `backend/pli/**` (adapters, auth, billing) |
| **Frontend Engineer** | FE | Onboarding, pricing, settings abonnement, paywall doux | `frontend/src/features/{onboarding,billing,auth}` |
| **QA / Test Engineer** | QA | Tests parcours trial→paid→cancel, fixtures multi-tenant | `**/tests/**`, scénarios Stripe CLI |
| **UX Designer** | UX | Onboarding wizard, pricing page, paywall modals | Maquettes onboarding + paywall (doc 03) |
| **SRE / DevOps** | SRE | Infra Cloud (PostgreSQL managé, stockage objet), déploiement staging Cloud | `docker-compose.yml`, `.github/workflows/`, IaC |
| **Security** | SEC | Isolation tenants, revue JWT/refresh, audit webhooks Stripe | Checklist multi-tenant, threat model delta |
| **Founder (JM)** | — | Décisions pricing, dogfooding signup, acceptance Go/No-Go | Signature Go M3 |

---

## 3. Découpage Sprint (4 semaines = 2 sprints de 2 semaines)

### Sprint 5 (S11-S12) — **Architecture dual**

Refondre l'architecture pour isoler proprement Local vs Cloud et poser les fondations multi-tenant.

- Refactor : pattern adapters, isolation Local vs Cloud (storage, crypto, auth, settings)
- PostgreSQL pour mode Cloud (migrations Alembic, dialecte paramétrique)
- Multi-tenancy : isolation stricte par `user_id` (RLS PostgreSQL OU contrainte applicative systématique + tests)
- Authentification PLI : inscription, login, reset password, vérification email
- Session JWT (access 15 min + refresh 30 j, rotation refresh token)
- Déploiement Cloud sur staging (app + PostgreSQL managé + stockage objet type S3/R2)

**Owner principal** : BE · **Support** : TL (ADR), SEC (isolation + JWT), SRE (infra Cloud)
**Critère de sortie** : un nouvel utilisateur peut s'inscrire sur staging, recevoir l'email de vérification, se connecter, et ses données sont strictement isolées des autres tenants (vérifié par test automatisé).

### Sprint 6 (S13-S14) — **Paiement & Onboarding**

Monétisation opérationnelle et parcours nouvel utilisateur complet.

- Intégration Stripe Checkout (plans mensuel + annuel)
- Webhooks Stripe → activation/désactivation plan (idempotence, resigning)
- Page pricing publique (`pli.app/pricing`) : comparatif plans, CTA trial
- Flow trial 14 j (création compte sans CB, rappel J-3 et J-1)
- Gestion abonnement utilisateur (settings : plan actuel, changer, annuler, factures)
- Emails transactionnels (SendGrid ou Postmark) : vérification, reset, trial reminder, facture
- Onboarding wizard : choix Local vs Cloud → connexion 1er compte mail → tour guidé rapide
- Paywall doux sur features premium (message explicatif + CTA upgrade, pas de mur dur)
- Mode Local activé par clé licence post-paiement PLI Plus

**Owner principal** : BE + FE en binôme · **Support** : PM (copy pricing + paywall), UX (wizard)
**Critère de sortie** : un utilisateur test (non founder) effectue le parcours complet signup → trial → upgrade paid → change plan → cancel, avec webhook Stripe confirmé en mode test, et reçoit les emails attendus à chaque étape.

---

## 4. Définition du "done" M2

Une tâche est done si tous les critères sont respectés :

1. Code mergé sur `main` (PR avec 1 reviewer, TL obligatoire sur refactor adapters et multi-tenancy)
2. Tests unitaires ≥ 70 % du module, tests **multi-tenant d'isolation obligatoires** sur toute route touchant des données utilisateur
3. Tests intégration Stripe (Stripe CLI en dev, webhooks signés) passants
4. Tests E2E parcours signup→trial→paid→cancel passants sur staging
5. Documentation inline + README section mise à jour (notamment : comment lancer Stripe CLI en local)
6. Déployé sur staging Cloud, validé manuellement
7. Métrique de succès (perf multi-tenant, facturation, parcours) mesurée et OK

---

## 5. Dépendances externes au démarrage M2

| Dépendance | État attendu à S11 | Action si bloqué |
|---|---|---|
| Compte Stripe activé, clés test + live | À valider en S10 | Bloquant hard : retarder Sprint 6 |
| Domaine `pli.app` + DNS configurable | Déjà en place M0 | — |
| Provider email transactionnel (SendGrid/Postmark) | Compte créé + validation DNS (SPF/DKIM) en S11 | Fallback sur second provider (mitigation roadmap) |
| PostgreSQL managé (Supabase, Neon, ou Hetzner) | Provisionné S11 | Fallback PostgreSQL auto-hébergé Docker |
| Stockage objet (S3 / R2 / Scaleway) | Provisionné S11 | Accepter stockage local temporaire staging |
| Page pricing légale validée (CGV, mentions) | Draft ready S13 | Impact Checkpoint 2 : ne pas ouvrir paiement sans CGV |
| Go M1 signé par founder | Prérequis absolu | Décalage M2 de 2 sem max |

---

## 6. Cadences et rituels

- **Daily async** (10 min, Slack/Discord) : une ligne par agent — fait hier, fait aujourd'hui, blockers
- **Mid-sprint sync** (milieu S11 et S13) : 30 min, point d'étape synchrone — M2 est court, on ne se permet pas de dériver 2 semaines
- **Review de sprint** (fin S12, S14) : démo au founder, métriques, feedback
- **Retro** (même cadence) : ce qui a marché, ce qui coince, actions
- **Planning sprint suivant** : enchaîné sur la retro
- **PR policy** : tout merge sur `main` passe par PR, 1 approval minimum, TL obligatoire sur refactor adapters/multi-tenant, SEC obligatoire sur auth/JWT/webhooks

---

## 7. Risques M2 identifiés & mitigations

| Risque | Prob. | Impact | Mitigation |
|---|---|---|---|
| Complexité refactor Local/Cloud sous-estimée | Haute | Haut | **Spike d'architecture en S11 (3 j)** avant d'attaquer le refactor, ADR validée par TL avant code |
| Fuite de données inter-tenant (isolation cassée) | Moyenne | Critique | Tests d'isolation systématiques (fixture 2 users, tentative lecture croisée), revue SEC obligatoire, feature flag désactivable |
| Webhooks Stripe non testables en local | Moyenne | Moyen | Stripe CLI en forwarding local, scénarios scriptés, staging avec vrai webhook endpoint |
| SPF/DKIM non validés à temps → emails en spam | Moyenne | Haut | Démarrer validation DNS en S11, provider secondaire de secours |
| CGV / mentions légales pas prêtes à S14 | Moyenne | Haut | Rédaction parallèle dès S11 (template avocat), blocage paiement conditionnel à leur publication |
| Dérive scope pricing / plans multiples | Moyenne | Moyen | PM cadre : **2 plans maximum** en M2 (Free trial + PLI Plus mensuel/annuel), tout autre plan reporté M3+ |
| Rotation refresh token casse sessions légitimes | Faible | Haut | Période de grâce 1 h, logs de rotation, tests E2E reconnexion |

---

## 8. Checkpoint fin M2 (S14) — Critères Go/No-Go

Le founder signe le Go M3 si tous ces critères sont validés :

- [ ] Un utilisateur test (non founder) effectue signup → vérif email → login → choix Local/Cloud → connexion 1er compte mail, sans assistance
- [ ] Parcours Stripe complet testé : trial 14 j → upgrade paid → change plan → cancel → réactivation
- [ ] Webhooks Stripe idempotents (rejouer 2× ne double pas la facturation)
- [ ] Isolation multi-tenant validée par test automatisé (0 fuite croisée)
- [ ] Emails transactionnels délivrés (taux inbox > 95 % sur test 20 adresses)
- [ ] Mode Local activable par clé licence post-paiement
- [ ] Performance maintenue vs M1 (aucune régression : recherche < 300 ms, liste < 300 ms)
- [ ] 0 bug bloquant ouvert, 0 vulnérabilité SEC critique ouverte
- [ ] CGV + politique de conf publiées sur pricing page
- [ ] Tests coverage ≥ 70 % sur modules `auth`, `billing`, `tenant`

Si un critère manque : décalage de 2 semaines max (buffer M2 prévu dans la roadmap §4).

---

## 9. Deltas structurels repo attendus à l'issue de M2

```
pli-app/
├── M1-KICKOFF.md
├── M2-KICKOFF.md                ← ce document
├── SPRINT-5-BACKLOG.md          ← backlog architecture dual
├── SPRINT-6-BACKLOG.md          ← backlog paiement & onboarding
├── backend/
│   ├── alembic/                 ← NEW migrations PostgreSQL
│   │   └── versions/
│   ├── pli/
│   │   ├── db.py                ← UPD abstraction dialecte SQLite/PG
│   │   ├── adapters/            ← NEW pattern adapters Local vs Cloud
│   │   │   ├── base.py
│   │   │   ├── local.py
│   │   │   └── cloud.py
│   │   ├── tenancy/             ← NEW isolation user_id, middleware
│   │   │   └── context.py
│   │   ├── auth/                ← NEW authentification PLI
│   │   │   ├── signup.py
│   │   │   ├── login.py
│   │   │   ├── password_reset.py
│   │   │   └── jwt.py
│   │   ├── billing/             ← NEW Stripe integration
│   │   │   ├── stripe_client.py
│   │   │   ├── webhooks.py
│   │   │   ├── plans.py
│   │   │   └── licenses.py
│   │   ├── emails/              ← NEW emails transactionnels
│   │   │   ├── provider.py
│   │   │   └── templates/
│   │   └── api/
│   │       ├── auth.py          ← UPD ajout routes signup/login/reset
│   │       ├── billing.py       ← NEW routes Stripe + abonnement
│   │       └── onboarding.py    ← NEW routes wizard
│   └── tests/
│       ├── test_tenancy_isolation.py  ← NEW critique
│       ├── test_auth_flow.py
│       ├── test_stripe_webhooks.py
│       └── test_onboarding.py
└── frontend/
    └── src/
        ├── features/
        │   ├── auth/            ← NEW signup, login, reset
        │   ├── onboarding/      ← NEW wizard Local/Cloud
        │   ├── billing/         ← NEW pricing page + settings abonnement
        │   └── paywall/         ← NEW modales upgrade
        └── pages/
            └── pricing.tsx      ← NEW route publique
```

---

## 10. Prochaines actions immédiates (J1 de M2)

1. **TL** : publier ADR `adapters-local-cloud.md` (issue du spike S11) + ADR `multi-tenancy.md`
2. **SRE** : provisionner PostgreSQL managé + stockage objet sur staging, ouvrir les secrets GitHub Actions
3. **BE** : démarrer spike architecture dual (3 j max), enchaîner migrations Alembic
4. **FE** : scaffold routes `/auth/*`, `/pricing`, `/onboarding`, `/settings/billing`
5. **SEC** : rédiger checklist isolation multi-tenant + checklist webhooks Stripe
6. **PM** : publier `SPRINT-5-BACKLOG.md`, assigner tickets, cadrer pricing (2 plans max)
7. **UX** : livrer maquettes onboarding wizard (3 écrans) et paywall doux (2 variantes) avant S13
8. **Founder** : valider ce kickoff, décider pricing final (tarif mensuel / annuel), ouvrir officiellement Sprint 5

---

*Kickoff établi le 22 avril 2026 par le Tech Lead, en coordination avec PM et founder. Revalidation obligatoire au Go M1 (17 juin 2026) avant démarrage effectif.*
