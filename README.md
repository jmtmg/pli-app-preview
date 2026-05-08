# PLI

Client email conversationnel groupé par contact (UX WhatsApp pour l'email).

- **Stack** : FastAPI (Python 3.11) · React 18 + TypeScript + Tailwind · SQLite+FTS5 / Postgres+RLS
- **Providers** : Gmail API · Microsoft Graph (OAuth 2.0)
- **Modes** : `local` (SQLite+SQLCipher, vie privée par défaut) · `cloud` (Postgres, multi-utilisateurs, Sprint 5+)

## Démarrage rapide (dev local)

```bash
# 1. cloner et configurer
cp .env.example .env
# renseigner PLI_GOOGLE_CLIENT_ID, PLI_MICROSOFT_CLIENT_ID, etc.

# 2. installer
make install

# 3. lancer backend + frontend en parallèle
make dev
```

Frontend disponible sur http://localhost:5173 — proxy transparent vers le backend sur :8000.

### Avec Docker

```bash
make docker-up
```

## Arborescence

```
pli-app/
├── backend/            FastAPI + Pydantic v2
│   ├── pli/
│   │   ├── api/        routes (auth, accounts, conversations, messages, search, contacts)
│   │   ├── providers/  adapters Gmail / Microsoft (Strategy pattern)
│   │   ├── sync/       normalisation + boucle de synchro
│   │   ├── adapters/   accès données (local SQLite, cloud Postgres)
│   │   ├── config.py   pydantic-settings
│   │   ├── db.py       init + healthcheck SQLite/SQLCipher
│   │   ├── schema.sql  tables + FTS5 + triggers
│   │   ├── models.py   DTOs Pydantic
│   │   └── main.py     FastAPI app + lifespan
│   ├── tests/          pytest (≥70 % couverture exigée en M1)
│   └── pyproject.toml
├── frontend/           React 18 + Vite + Tailwind + PWA
│   ├── src/
│   │   ├── api/        client HTTP + hooks TanStack Query
│   │   ├── features/
│   │   │   ├── list/           Liste conversations + filtres
│   │   │   ├── conversation/   Pane conversation + bulles + composer
│   │   │   ├── contact/        Fiche contact
│   │   │   └── drawer/         Drawer comptes
│   │   ├── components/  UI primitives (Header, FilterBar, Avatar, EmptyState)
│   │   ├── styles/      tokens.css + index.css
│   │   ├── App.tsx      shell 3 panes
│   │   └── main.tsx     root React
│   ├── index.html
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   └── package.json
├── docs/               docs M1 déplacés de PLI-Documentation
├── docker-compose.yml
├── Makefile
├── .env.example
└── SPRINT-1-BACKLOG.md
```

## Commandes

| Commande              | Action                                                  |
|-----------------------|---------------------------------------------------------|
| `make dev`            | Backend + frontend en parallèle                         |
| `make dev-be`         | Backend seul (uvicorn --reload)                         |
| `make dev-fe`         | Frontend seul (vite)                                    |
| `make test`           | pytest + vitest                                         |
| `make lint`           | ruff + eslint                                           |
| `make typecheck`      | mypy + tsc --noEmit                                     |
| `make fmt`            | ruff format + prettier                                  |
| `make docker-up`      | docker compose up                                       |
| `make clean`          | Vide caches + supprime la base SQLite locale            |

## Design system

Tokens CSS (voir `frontend/src/styles/tokens.css`) :
- Accent bronze `#c9a47d`
- Backgrounds : `#0b0b0c` → `#18181b` (élévations 0–2)
- Motion : `cubic-bezier(0.32,0.72,0,1)` — 150 ms micro / 280 ms std
- WCAG AA contraste minimum

Wireframes et spécifications complètes : `../docs/03-Wireframes.md`.

## Équipe

| Rôle          | Focus                                         |
|---------------|-----------------------------------------------|
| **PM**        | priorisation backlog, roadmap, stakeholders   |
| **TL**        | architecture, code review, arbitrages tech    |
| **BE**        | FastAPI, sync, providers, FTS5                |
| **FE**        | React, Tailwind, PWA, interactions            |
| **QA**        | test plan, Vitest+Playwright, pytest          |
| **UX**        | wireframes, tokens, parcours                  |
| **SRE**       | Docker, CI/CD, observabilité (Sprint 5+)      |
| **SEC**       | OAuth, RLS, chiffrement at-rest               |

## Roadmap

- **M1** (sem. 1–8) · MVP : sync + navigation + composer + recherche — _en cours_
- **M2** (sem. 9–12) · Attachments + pin + mute + mobile polish
- **M3** (sem. 13–16) · Mode cloud + RLS + multi-device
- **M4** (sem. 17–20) · Launch bêta

Voir `M1-KICKOFF.md` pour le détail du milestone actuel et `SPRINT-1-BACKLOG.md` pour les user stories en cours.

## Sécurité

- OAuth 2.0 avec `state` CSRF et PKCE (Sprint 2)
- Tokens stockés chiffrés (SQLCipher en local, `pgcrypto` en cloud)
- Aucun email exfiltré en dehors du poste en mode local
- `.env` toujours gitignoré — secrets Gmail/Microsoft ne doivent jamais finir dans git

## Licence

Propriétaire — tous droits réservés. Voir `LICENSE`.
