# Sprint 5 (S11-S12) — Architecture dual · Backlog

**Phase** : M2 · **Durée** : 2 semaines · **Démarrage** : 17 juin 2026 · **Fin** : 1er juillet 2026
**Objectif sprint** : Isolation propre Local vs Cloud via pattern adapters, PostgreSQL opérationnel en Cloud, multi-tenancy strict, authentification PLI + sessions JWT, déploiement staging Cloud.
**Critère de sortie** : un nouvel utilisateur s'inscrit sur staging, reçoit l'email de vérif, se connecte, et ses données sont isolées (vérifié par test automatisé).

---

## 1. User stories

### US-5.1 — Spike architecture adapters (3 j) — **BE + TL**

**En tant que** Tech Lead
**Je veux** valider le pattern adapters avant refactor massif
**Afin de** ne pas engager 8 j d'effort sur une approche qui ne tient pas

**Critères d'acceptance** :
- Prototype fonctionnel isolant `StorageAdapter`, `AuthAdapter`, `CryptoAdapter`, `SettingsAdapter`
- ADR `adapters-local-cloud.md` publiée (doc 07) : diagramme, trade-offs, alternatives écartées
- Démo au founder avant démarrage refactor
- Critères de bascule Local ↔ Cloud documentés (clé licence, signal utilisateur)

**Effort estimé** : 3 j · **Priorité** : P0 (bloque le reste du sprint)

---

### US-5.2 — Migrations PostgreSQL via Alembic — **BE + SRE**

**En tant que** Backend Engineer
**Je veux** un système de migration PG équivalent au schema SQLite actuel
**Afin de** pouvoir déployer le mode Cloud sans rupture fonctionnelle

**Critères d'acceptance** :
- Alembic initialisé, première migration = schéma complet M1
- Dialecte SQL paramétré (FTS5 sur SQLite, `tsvector` + GIN sur PostgreSQL)
- Tests backend passent sur SQLite ET PostgreSQL (matrix CI)
- `make db-migrate` fonctionne sur les deux dialectes
- README mis à jour avec setup PostgreSQL local

**Effort estimé** : 2 j · **Priorité** : P0

---

### US-5.3 — Multi-tenancy strict — **BE + SEC**

**En tant qu'** utilisateur Cloud
**Je veux** être certain que mes données ne sont jamais lisibles par un autre compte
**Afin de** faire confiance à PLI Cloud avec mes emails

**Critères d'acceptance** :
- Middleware FastAPI injectant `tenant_context` depuis JWT
- Toute requête SQL passe par un repository qui force `WHERE user_id = :tenant`
- Row-Level Security PostgreSQL activée en défense en profondeur (décision TL dans ADR `multi-tenancy.md`)
- **Test `test_tenancy_isolation.py`** : crée 2 users, insère données chez chacun, tente lecture croisée sur toutes les routes → doit toujours échouer avec 404
- Audit SEC signé (checklist complétée)

**Effort estimé** : 2,5 j · **Priorité** : P0 (sécurité critique)

---

### US-5.4 — Inscription + vérification email — **BE + FE**

**En tant que** nouveau visiteur
**Je veux** créer un compte PLI avec email + mot de passe
**Afin de** accéder au trial 14 j

**Critères d'acceptance** :
- `POST /auth/signup` : email, password (min 12 chars, zxcvbn ≥ 3), acceptation CGU
- Hash password avec Argon2id (paramètres OWASP 2025)
- Email de vérification envoyé (provider transactionnel, template simple)
- Lien de vérification valide 24 h, à usage unique
- Frontend : page `/signup`, état "vérifie ta boîte mail", page `/verify?token=`
- Erreurs parlantes (email déjà pris, mot de passe trop faible)

**Effort estimé** : 2 j · **Priorité** : P0

---

### US-5.5 — Login + sessions JWT — **BE + FE + SEC**

**En tant qu'** utilisateur vérifié
**Je veux** me connecter à PLI
**Afin de** accéder à mes emails

**Critères d'acceptance** :
- `POST /auth/login` → access token (15 min) + refresh token (30 j, httpOnly, SameSite=Lax)
- `POST /auth/refresh` → rotation refresh (ancien invalidé, nouveau émis)
- `POST /auth/logout` → invalide refresh côté serveur (table `revoked_tokens`)
- Throttling : 5 tentatives login/15 min/IP, sinon 429
- Frontend : page `/login`, redirection intelligente, gestion expiration silencieuse
- Revue SEC : JWT signés HS256 avec secret rotable, clock skew 30 s toléré

**Effort estimé** : 2 j · **Priorité** : P0

---

### US-5.6 — Reset password — **BE + FE**

**En tant qu'** utilisateur ayant oublié son mot de passe
**Je veux** recevoir un lien de réinitialisation
**Afin de** récupérer l'accès à mon compte

**Critères d'acceptance** :
- `POST /auth/password-reset/request` : email → envoi lien (ne révèle pas si l'email existe)
- Token de reset valide 1 h, à usage unique
- `POST /auth/password-reset/confirm` : nouveau password, mêmes contraintes que signup
- Toutes les sessions actives invalidées au reset
- Frontend : pages `/forgot`, `/reset?token=`

**Effort estimé** : 1 j · **Priorité** : P1

---

### US-5.7 — Déploiement staging Cloud — **SRE**

**En tant qu'** équipe
**Nous voulons** un environnement staging Cloud complet
**Afin de** valider les parcours end-to-end avant la prod

**Critères d'acceptance** :
- App FastAPI déployée (Fly.io ou Hetzner), scaling 0→1 OK
- PostgreSQL managé provisionné, migrations appliquées automatiquement au déploiement
- Stockage objet configuré (S3 compat : R2, Scaleway, ou MinIO), buckets `pli-staging-attachments`
- Secrets GitHub Actions injectés (DB_URL, JWT_SECRET, STRIPE_KEYS placeholder, EMAIL_API_KEY)
- Monitoring basique : Uptime Robot + logs centralisés (Better Stack, Grafana Cloud free, ou similaire)
- Domaine staging : `staging.pli.app` avec HTTPS auto

**Effort estimé** : 2 j · **Priorité** : P0

---

### US-5.8 — Adapters StorageAdapter concrets — **BE**

**En tant que** Backend Engineer
**Je veux** deux implémentations concrètes du `StorageAdapter`
**Afin de** stocker les pièces jointes selon le mode

**Critères d'acceptance** :
- `LocalStorageAdapter` : disque local chiffré (réutilise M1)
- `CloudStorageAdapter` : S3-compatible, chiffrement at-rest
- Interface commune (`put`, `get`, `delete`, `presigned_url`)
- Tests unitaires avec mock S3 (`moto`)
- Bascule transparente selon `config.mode`

**Effort estimé** : 1,5 j · **Priorité** : P1

---

## 2. Plan des 10 jours ouvrés

| Jour | Focus principal | Ownership |
|---|---|---|
| J1-J3 | Spike adapters (US-5.1) + kickoff sprint | BE, TL |
| J3 | ADR adapters validée, **feu vert refactor** | TL + founder |
| J3-J5 | Migrations Alembic (US-5.2) + scaffolding auth (US-5.4) | BE, FE |
| J4-J5 | Provisioning infra staging (US-5.7) en parallèle | SRE |
| J5-J7 | Multi-tenancy (US-5.3) + revue SEC | BE, SEC |
| J6-J8 | Signup / login / JWT (US-5.4, US-5.5) bout-en-bout | BE + FE |
| J8-J9 | Reset password (US-5.6) + adapters storage (US-5.8) | BE + FE |
| J9 | Déploiement staging complet, smoke tests | SRE + QA |
| J10 | Review sprint, démo, retro, planning Sprint 6 | Tous |

---

## 3. Definition of Done Sprint 5

- [ ] Toutes les US P0 en `completed`
- [ ] Coverage ≥ 70 % sur `auth/`, `tenancy/`, `adapters/`
- [ ] `test_tenancy_isolation.py` vert
- [ ] Staging Cloud accessible, signup/login/reset fonctionnels bout-en-bout
- [ ] ADR `adapters-local-cloud.md` et `multi-tenancy.md` mergées
- [ ] 0 vulnérabilité SEC haute ou critique ouverte
- [ ] Démo sprint enregistrée, feedback founder capturé

---

## 4. Hors scope (reporté Sprint 6)

- Stripe (Sprint 6)
- Pricing page publique (Sprint 6)
- Onboarding wizard UX (Sprint 6)
- 2FA / SSO (hors M2, report M3+ selon backlog produit)
- Suppression de compte RGPD (M3, doc 12)

---

*Backlog rédigé par PM en coordination avec TL, à valider en sprint planning S11.*
