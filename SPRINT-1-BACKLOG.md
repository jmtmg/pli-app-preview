# Sprint 1 · Sync + Fondations — Backlog

**Dates** : sem. 1–2 du M1 (2 semaines, 10 jours ouvrés)
**Thème** : brancher OAuth Gmail/Microsoft, réussir une synchro initiale, persister en SQLite, rendre la liste en lecture.
**Sortie de sprint** : démo « connecter Gmail ou Outlook → voir la liste de conversations peuplée en temps réel ».

---

## Objectifs du sprint (DoD global)

À la fin de ce sprint, il est possible de :

1. Lancer `make dev` sur un poste neuf et accéder au frontend sur http://localhost:5173.
2. Connecter un compte Google OU Microsoft depuis le Drawer (OAuth complet, tokens stockés chiffrés).
3. Déclencher une synchro initiale qui ingère 1 000+ messages sans planter.
4. Voir la liste des conversations groupées par contact, triée par `last_msg_at DESC`, filtres Humains/Notifs fonctionnels.
5. Couverture backend ≥ 70 %, aucun warning lint, CI verte.

---

## User stories

### US-1.1 — Connexion d'un compte Google  (BE · 3 pts)

**En tant qu'**utilisateur, **je veux** cliquer sur « + Ajouter un compte Google » et autoriser PLI via ma boîte Gmail, **afin de** démarrer la synchro.

**Critères d'acceptance**
- [ ] `GET /auth/google/start` redirige vers l'écran de consent Google avec les scopes `gmail.readonly`, `gmail.send`, `gmail.modify`, `userinfo.email`.
- [ ] Le paramètre `state` est vérifié à la callback (défense CSRF).
- [ ] `GET /auth/google/callback?code=…&state=…` échange le code, fetch `userinfo`, upsert la ligne `accounts` avec tokens chiffrés.
- [ ] Le refresh_token est bien persisté (scope `access_type=offline` + `prompt=consent`).
- [ ] En cas d'échec d'échange, l'utilisateur voit un message clair et peut relancer.

**Owner** : BE · **Dépendances** : — · **Risques** : scopes rejetés par Google → répéter la demande OAuth dans l'outil interne avant merge.

---

### US-1.2 — Connexion d'un compte Microsoft  (BE · 3 pts)

**En tant qu'**utilisateur, **je veux** connecter un compte Outlook/Microsoft 365 **afin de** synchroniser ces emails aussi.

**Critères d'acceptance**
- [ ] `GET /auth/microsoft/start` redirige vers `login.microsoftonline.com/common/oauth2/v2.0/authorize` avec scopes `Mail.Read Mail.ReadWrite Mail.Send User.Read offline_access`.
- [ ] `GET /auth/microsoft/callback` échange le code et persiste les tokens (refresh inclus).
- [ ] Cas multi-tenant géré via l'autorité `/common`.

**Owner** : BE · **Dépendances** : US-1.1 (structure state + stockage token commun).

---

### US-1.3 — Schéma SQLite + FTS5 initialisés  (BE · 2 pts)

**En tant qu'**équipe, **nous voulons** que la base SQLite se créé avec son schéma et ses index au premier démarrage, **afin de** ne pas avoir à jouer de migrations manuelles.

**Critères d'acceptance**
- [ ] `init_db()` crée toutes les tables (`accounts`, `contacts`, `messages`, `attachments`, `drafts`, `sync_log`) si elles n'existent pas.
- [ ] Index `idx_msg_last_ts`, `idx_msg_unread`, `idx_contact_last`, `idx_contact_pinned` posés.
- [ ] FTS5 virtuelles `messages_fts` et `attachments_fts` + triggers AI/AD/AU.
- [ ] Si SQLCipher est dispo, la base est ouverte avec `PRAGMA key = …`. Sinon fallback SQLite plein texte avec log WARN.
- [ ] `GET /health` renvoie `{ "db": "ok", "mode": "local" }`.

**Owner** : BE · **Dépendances** : —.

---

### US-1.4 — Synchro initiale Gmail  (BE · 5 pts)

**En tant qu'**utilisateur venant de connecter mon compte Gmail, **je veux** que PLI ingère automatiquement mes 1 000 derniers messages, **afin de** pouvoir commencer à naviguer.

**Critères d'acceptance**
- [ ] `POST /accounts/{id}/sync?kind=initial` lance une tâche en arrière-plan (BackgroundTasks).
- [ ] Le provider Gmail parcourt `users.messages.list` avec pagination, puis `users.messages.get` en batch de 50.
- [ ] Chaque message parsé (`mail-parser`) est dédupliqué par `message_id` RFC 5322.
- [ ] Le contact est créé/réutilisé via `normalize_email()` (lowercase, strip +alias, trim).
- [ ] Snippet calculé (max 140 chars, whitespace collapsé).
- [ ] Erreurs transitoires gérées par tenacity (4 essais, 2–30 s backoff).
- [ ] `sync_log` contient une ligne `started_at`/`ended_at`/`status` par run.
- [ ] Test d'intégration : fixture de 50 messages JSON → 50 lignes `messages` + contacts dédupliqués.

**Owner** : BE · **Dépendances** : US-1.1, US-1.3 · **Risques** : quota 250 units/s Gmail — implémenter `asyncio.Semaphore(5)` + backoff exponentiel.

---

### US-1.5 — Synchro initiale Microsoft Graph  (BE · 5 pts)

Analogue à US-1.4 pour Microsoft Graph : `/me/messages?$top=100&$orderby=receivedDateTime desc`, paginer via `@odata.nextLink`, extraire le `deltaLink` final pour la future incrémentale.

**Owner** : BE · **Dépendances** : US-1.2, US-1.3, US-1.4 (pour le code partagé de parsing/dédup).

---

### US-1.6 — Endpoint `GET /conversations`  (BE · 2 pts)

**En tant que** frontend, **j'ai besoin** d'une liste de conversations filtrable et paginée, **afin de** peupler la colonne principale.

**Critères d'acceptance**
- [ ] `GET /conversations?account_id=&filter=humans|notifs|unread|attachments&cursor=&limit=50` retourne un tableau de `ConversationListItem`.
- [ ] Tri : `is_pinned DESC, pinned_order ASC NULLS LAST, last_msg_at DESC`.
- [ ] Le filtre `humans` exclut `kind='notif'` ; `notifs` l'inclut exclusivement ; `unread` exige `unread_count > 0` ; `attachments` exige `has_attachments = 1`.
- [ ] Cursor opaque encodant `(last_msg_at, id)` pour stabilité.
- [ ] Tests : 3 fixtures de contacts (épinglé, humain, notif) → ordre respecté selon filtre.

**Owner** : BE · **Dépendances** : US-1.3, US-1.4.

---

### US-1.7 — Rendu de la liste des conversations  (FE · 3 pts)

**En tant qu'**utilisateur, **je veux** voir mes conversations groupées par contact, triées par date décroissante, **afin d'**identifier rapidement qui m'a écrit.

**Critères d'acceptance**
- [ ] `ConversationList` consomme `useConversations(accountId, filter)`.
- [ ] Rendu d'une `ConversationRow` : avatar (initiales), nom + société, aperçu, horodatage relatif (HH:mm / Hier / jour sem. / jj mmm), badge non-lu si >0, 📎 si PJ, 📌 si épinglé.
- [ ] États : loading (placeholder), empty (EmptyState avec copy adaptée au filtre), erreur (toast).
- [ ] Clic sur une ligne → `onSelect(contact_id)` remonte au shell.
- [ ] Performance : 500 lignes scrollables sans jank perçu (pas de virtualization encore, mesurer en M2).
- [ ] Accessibilité : `<button>` focusable, contraste WCAG AA vérifié.

**Owner** : FE · **Dépendances** : US-1.6.

---

### US-1.8 — Drawer de bascule de compte  (FE · 2 pts)

**En tant qu'**utilisateur avec plusieurs comptes, **je veux** basculer entre eux depuis un drawer latéral, **afin de** filtrer la liste sur un compte particulier.

**Critères d'acceptance**
- [ ] Drawer avec backdrop semi-transparent (cubic-bezier(0.32,0.72,0,1), 200 ms).
- [ ] Liste des comptes via `useAccounts()` avec avatar + email + compteur non-lus.
- [ ] « Tous les comptes » remet `accountId = null`.
- [ ] Bouton « + Ajouter un compte Google/Microsoft » → `window.location.href = /api/auth/{provider}/start`.
- [ ] Fermeture au clic sur backdrop ou `Escape`.
- [ ] Test Playwright : ouverture → sélection → liste filtrée.

**Owner** : FE · **Dépendances** : US-1.7.

---

### US-1.9 — Healthcheck + observabilité de base  (SRE · 1 pt)

**En tant que** développeur, **je veux** un endpoint `/health` et des logs JSON structurés, **afin de** diagnostiquer rapidement.

**Critères d'acceptance**
- [ ] `GET /health` retourne `{ "status": "ok", "mode": "local|cloud", "db": "ok", "version": "0.1.0" }`.
- [ ] `structlog` configuré en JSON avec niveaux `INFO`/`WARN`/`ERROR`.
- [ ] Chaque requête HTTP logguée avec `method`, `path`, `status`, `duration_ms`.
- [ ] Erreurs de sync loguées avec `account_id`, `kind`, `attempt`.

**Owner** : SRE · **Dépendances** : —.

---

### US-1.10 — CI GitHub Actions  (SRE · 2 pts)

**En tant qu'**équipe, **nous voulons** qu'à chaque PR : lint + typecheck + tests passent, **afin de** ne jamais merger du code cassé.

**Critères d'acceptance**
- [ ] Workflow `.github/workflows/ci.yml` sur push + PR.
- [ ] Jobs parallèles : `backend` (python 3.11, ruff, mypy, pytest --cov) et `frontend` (node 20, eslint, tsc, vitest).
- [ ] Seuil `--cov-fail-under=70` sur le backend.
- [ ] Artefacts : rapport couverture HTML + junit.xml.
- [ ] Temps total < 5 min (cache pip + npm).

**Owner** : SRE · **Dépendances** : —.

---

## Hors-scope (reporté à Sprint 2+)

- Synchro incrémentale (historyId / deltaLink) → Sprint 2
- Composer + envoi → Sprint 3
- Recherche FTS5 exposée UI → Sprint 4
- Pièces jointes téléchargeables → Sprint 2
- Swipe actions bidirectionnelles → Sprint 4 (le squelette `ConversationRow` est déjà prêt)
- Fiche contact détaillée → Sprint 2
- PWA offline → Sprint 4
- Multi-tenant cloud → M3

---

## Capacité

| Rôle | Capacité (pts) | Story points alloués |
|------|----------------|---------------------|
| BE   | 15             | 20 (US-1.1/1.2/1.3/1.4/1.5/1.6) — **surcharge 33 %** |
| FE   | 10             | 5 (US-1.7/1.8) |
| SRE  | 5              | 3 (US-1.9/1.10) |

> ⚠️ Risque identifié : BE est surchargé. Arbitrage PM + TL : si la sync Microsoft (US-1.5) glisse, on livre quand même la démo avec Gmail seul (US-1.4) et on reprend US-1.5 en ouverture de Sprint 2.

---

## Rituels du sprint

- **Daily** : 10h, 10 min max. Tour de table : hier / aujourd'hui / bloquants.
- **Grooming** : mardi S2, 1h. Affiner les stories de Sprint 2 (sync incrémentale + attachments).
- **Review + Démo** : vendredi S2 après-midi. Démo live connect + synchro.
- **Retro** : vendredi S2 fin de journée. Format start/stop/continue.

---

## Risques

| Risque                                             | Probabilité | Impact | Mitigation                                                   |
|----------------------------------------------------|-------------|--------|--------------------------------------------------------------|
| Quota Gmail (250 unités/sec) bloquant la synchro   | moyen       | fort   | `asyncio.Semaphore(5)`, tenacity backoff, tests de charge    |
| Tokens stockés en clair si SQLCipher indispo       | faible      | fort   | Fallback documenté, WARN explicite, refus en mode prod       |
| Variation de format RFC 822 entre Gmail et Graph   | moyen       | moyen  | Normaliser via `mail-parser` + DTO commun `RawMessage`       |
| Nouveau poste dev sans Python 3.11                 | élevé       | faible | `docker-compose` documenté dans README comme chemin alt      |

---

## Definition of Done (sprint)

- [ ] Toutes les US critiques (US-1.1/1.3/1.4/1.6/1.7/1.9/1.10) livrées et mergées.
- [ ] Démo enregistrée (screencast 3 min) — sync Gmail + navigation liste.
- [ ] CI verte sur `main`.
- [ ] Couverture backend ≥ 70 %.
- [ ] Zéro warning lint/typecheck.
- [ ] README à jour, `.env.example` documenté.
- [ ] Retro tenue, actions consignées dans `docs/retros/sprint-1.md`.
