# M1 — Kickoff · Core MVP

**Phase** : M1 (semaines 3 → 10, 8 semaines)
**Démarrage** : 22 avril 2026 (après validation M0)
**Fin cible** : 17 juin 2026
**Doc de référence** : [05-Roadmap.md](../05-Roadmap.md) §3 — Phase M1

---

## 1. Objectif de M1

> **Livrer une version fonctionnelle en mode Local only pour 1 utilisateur, toutes les features P0 cœur en place, sync Gmail + Microsoft, parcours complets (liste → conversation → composer → envoi → recherche).**

À la fin de M1, le founder doit pouvoir **remplacer Gmail par PLI** pour un compte en dogfooding léger — c'est le Go/No-Go du Checkpoint 1 (S10).

---

## 2. Répartition de l'équipe d'agents

| Rôle | Agent | Périmètre M1 | Livrables clés |
|---|---|---|---|
| **Product Manager** | PM | Priorisation, arbitrages scope, validation acceptance | Backlog Sprint 1-4, critères acceptance |
| **Tech Lead** | TL | Architecture code, revues PR, définition standards | Code owner, ADR mises à jour |
| **Backend Engineer** | BE | FastAPI, providers Gmail/Microsoft, sync, API REST | `backend/pli/**` |
| **Frontend Engineer** | FE | React+TS+Tailwind, PWA, UX | `frontend/src/**` |
| **QA / Test Engineer** | QA | Tests unit + integration + E2E | `**/tests/**`, `e2e/**` |
| **UX Designer** | UX | Itérations wireframes si friction identifiée | Mises à jour doc 03 |
| **SRE / DevOps** | SRE | Dev env, CI, déploiement staging | `docker-compose.yml`, `.github/workflows/` |
| **Security** | SEC | Review OAuth, token storage, chiffrement | Threat model → checklist |
| **Founder (JM)** | — | Décisions, dogfooding, acceptance finale | Signature Go/No-Go |

---

## 3. Découpage Sprint (8 semaines = 4 sprints de 2 semaines)

### Sprint 1 (S3-S4) — **Synchronisation**

Bâtir l'assise : récupérer et stocker les mails.

- Sync initiale Gmail (30j messages)
- Sync initiale Microsoft (30j messages)
- Parsing MIME, extraction headers + body (HTML/plain)
- Stockage SQLite : tables `accounts`, `messages`, `contacts`, `attachments`
- Sync incrémentale (`historyId` Gmail, `deltaLink` Graph)
- Gestion erreurs sync (retry exponentiel, circuit breaker)

**Owner principal** : BE · **Support** : SRE (env), SEC (token storage)
**Critère de sortie** : `POST /accounts/{id}/sync` importe 100+ messages, relance incrémentale ≤ 5 s.

### Sprint 2 (S5-S6) — **Navigation & Lecture**

Rendre les données visibles et navigables.

- Liste conversations (regroupement par adresse contact)
- Filtres Humains / Notifs / Non lus / Avec PJ
- Vue conversation (bulles, sujets, PJ)
- Fiche contact basique (fields + PJ grid)
- Drawer comptes avec switch actif

**Owner principal** : FE · **Support** : BE (API conversations/contacts)
**Critère de sortie** : l'utilisateur scrolle sa liste, ouvre une conversation, voit les bulles correctement groupées.

### Sprint 3 (S7-S8) — **Composer & Envoi**

Passer du client lecture seule au client plein.

- Composer réponse (champ expandable)
- Édition sujet via bottom sheet
- Signature par compte
- Envoi via Gmail API / Microsoft Graph
- Brouillons auto-sauvegardés (idle 2 s)
- Nouveau message (modal)
- Pièces jointes au composer (sélecteur + preview + upload)

**Owner principal** : FE+BE en binôme
**Critère de sortie** : envoi réel d'un mail vers une boîte externe, réception confirmée.

### Sprint 4 (S9-S10) — **Recherche & Actions**

Compléter les parcours et la vélocité d'usage.

- Indexation FTS5 (contenu messages + contacts)
- Recherche modal plein écran, résultats groupés
- Épinglage (max 3, fond subtil, icône)
- Drag-and-drop réordonnement épinglées
- Menu 3 points (bottom sheet actions)
- Swipe bilatéral (4 actions, seuils 33 % / 15 %)
- Archivage, marquer non lu, silence

**Owner principal** : FE · **Support** : BE (FTS5, API search)
**Critère de sortie** : recherche < 300 ms sur 10k messages, swipe fluide mobile.

---

## 4. Définition du "done" M1

Une tâche est done si tous les critères sont respectés :

1. Code mergé sur `main` (PR avec 1 reviewer)
2. Tests unitaires ≥ 70 % du module
3. Tests intégration / E2E pertinents passants
4. Documentation inline + README section mise à jour
5. Déployé sur staging, validé manuellement
6. Métrique de succès (perf, UX, fonctionnel) mesurée et OK

---

## 5. Dépendances externes au démarrage M1

| Dépendance | État attendu à S3 | Action si bloqué |
|---|---|---|
| OAuth Google Cloud app validée (scopes `gmail.readonly`, `send`, `modify`) | Validée depuis M0 | Continuer en mode dev/test, validation en parallèle |
| OAuth Microsoft Azure app enregistrée | Validée depuis M0 | Idem |
| Repo GitHub privé `abscisse/pli` | Créé M0 | — |
| CI/CD GitHub Actions minimale | Verte M0 | Bloquant : pas de merge sans CI |
| Env staging (Hetzner VM ou fly.io) | Déployé M0 | Décaler S1 pour rattrapage |

---

## 6. Cadences et rituels

- **Daily async** (10 min, Slack/Discord) : une ligne par agent — fait hier, fait aujourd'hui, blockers
- **Review de sprint** (fin S4, S6, S8, S10) : démo au founder, métriques, feedback
- **Retro** (même cadence) : ce qui a bien marché, ce qui coince, actions
- **Planning sprint suivant** : enchaîné sur la retro
- **PR policy** : tout merge sur `main` passe par PR, 1 approval minimum

---

## 7. Risques M1 identifiés & mitigations

| Risque | Prob. | Impact | Mitigation |
|---|---|---|---|
| MIME parsing HTML casse sur emails exotiques | Haute | Moyen | Lib robuste (`mailparser`, `beautifulsoup4` fallback), corpus de tests réels |
| Performance FTS5 dégradée > 10k messages | Moyenne | Haut | Index composites, pagination curseur, batch indexing async |
| Gestes tactiles web moins fluides qu'espéré | Moyenne | Moyen | Spike S5 sur `react-use-gesture`, fallback React Native Web si bloquant |
| Quotas Gmail API atteints en dogfooding | Moyenne | Moyen | Backoff + cache, demande augmentation quota en S5 |
| OAuth refresh token expire pendant sync longue | Faible | Haut | Refresh préventif à 80 % TTL, retry idempotent |

---

## 8. Checkpoint fin M1 (S10) — Critères Go/No-Go

Le founder signe le Go M2 si tous ces critères sont validés :

- [ ] Sync stable sur 1 compte Gmail + 1 compte Microsoft (≥ 7 jours sans incident)
- [ ] Navigation fluide (liste → conversation < 300 ms)
- [ ] Composer fonctionnel (envoi réel testé)
- [ ] Recherche < 300 ms sur 10k messages
- [ ] Épinglage, swipe, menu 3 points opérationnels
- [ ] 0 bug bloquant ouvert
- [ ] Tests coverage ≥ 70 % modules critiques (sync, API, composer)
- [ ] Le founder utilise PLI en dogfooding léger pendant ≥ 3 jours

Si un critère manque : décalage de 2 semaines max (buffer prévu dans la roadmap).

---

## 9. Structure du repo à l'issue de M0

```
pli-app/
├── M1-KICKOFF.md            ← ce document
├── README.md                ← setup développeur
├── SPRINT-1-BACKLOG.md      ← user stories Sprint 1
├── Makefile                 ← commandes usuelles
├── docker-compose.yml       ← env de dev
├── .env.example             ← variables à configurer
├── .gitignore
├── backend/
│   ├── pyproject.toml
│   ├── pli/
│   │   ├── __init__.py
│   │   ├── main.py          ← FastAPI entrypoint
│   │   ├── config.py
│   │   ├── db.py            ← SQLite + SQLCipher
│   │   ├── schema.sql       ← schema + FTS5
│   │   ├── models.py        ← pydantic models
│   │   ├── providers/
│   │   │   ├── base.py      ← interface MailProvider
│   │   │   ├── gmail.py
│   │   │   └── microsoft.py
│   │   ├── sync/
│   │   │   ├── service.py   ← orchestration
│   │   │   └── parser.py    ← MIME / Graph message → domain
│   │   └── api/
│   │       ├── auth.py      ← OAuth callback
│   │       ├── accounts.py
│   │       ├── conversations.py
│   │       ├── messages.py
│   │       ├── contacts.py
│   │       └── search.py
│   └── tests/
│       ├── test_parser.py
│       └── test_sync.py
└── frontend/
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── index.html
    ├── public/
    │   └── manifest.webmanifest
    └── src/
        ├── main.tsx
        ├── App.tsx
        ├── api/client.ts
        ├── components/
        ├── features/
        │   ├── list/
        │   ├── conversation/
        │   ├── contact/
        │   └── drawer/
        └── styles/
            └── tokens.css   ← design tokens cf. doc 03
```

---

## 10. Prochaines actions immédiates

1. **SRE** : déployer la structure, initialiser `git init` + premier commit
2. **BE** : vérifier `make backend-dev` démarre FastAPI + SQLite
3. **FE** : vérifier `make frontend-dev` démarre Vite
4. **PM** : publier `SPRINT-1-BACKLOG.md` et assigner les tickets
5. **Founder** : valider ce kickoff, ouvrir Sprint 1 officiellement

---

*Kickoff établi le 22 avril 2026 par le Tech Lead, en coordination avec PM et founder.*
