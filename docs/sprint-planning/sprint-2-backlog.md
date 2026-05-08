# Sprint 2 — Backlog parking (PLI Mail / M1)

**Créé** : 2026-04-22 (clôture Sprint 1, ticket M1-T1.5)
**Owner backlog** : M1 (mail conversationnel)
**Statut** : pré-planning — à figer au sync direction lundi 2026-04-27

---

## Objectif de ce document

Garantir qu'aucune User Story planifiée pour Sprint 1 mais reportée par
décision de plan (cf. `sprint-1-planning.md` §2) ne soit oubliée.
Ce fichier est l'**unique source de vérité du parking M1 vers Sprint 2** —
sa validation est requise pour la clôture du ticket
`M1-sprint1-closeout.md` T1.5.

---

## Items reportés depuis Sprint 1 — confirmés P0 Sprint 2

### US-1.2 — Microsoft OAuth (BE, 3 pts)

**Origine** : Sprint 1 P2 glissable, non livré (BE concentré sur Gmail
+ patches démo).

**Scope** :
- Flow `/auth/microsoft/start` → consent (scopes `Mail.Read`, `Mail.Send`,
  `User.Read`)
- Échange code → tokens, normalisation email lowercase, upsert account
- Stockage tokens chiffrés Fernet (réutilise `pli/crypto/oauth.py`)
- Tests miroir de `test_auth_oauth.py` (scopes attendus, state CSRF,
  invalid_state, token_exchange_failed, refresh_token preservation)

**Fichiers existants** :
- `backend/pli/providers/microsoft.py` (scaffold OAuth déjà présent)
- `backend/pli/api/auth.py` (router supporte déjà `provider="microsoft"`)
- `.env.example` : variables `PLI_MS_*` déjà déclarées

**Critères "Done"** :
- Tests `test_auth_oauth_microsoft.py` créés (≈ 8 tests miroir Gmail)
- Runbook `docs/runbooks/oauth-microsoft-setup.md` créé (Azure AD App
  registration, redirect URI, test users)
- Capture E2E parcours `/auth/microsoft/start` → connected dans
  `docs/governance/demo/m1-e2e-sprint2/`

### US-1.5 — Sync initiale Graph (BE, 5 pts)

**Origine** : Sprint 1 P2 glissable, dépend de US-1.2 livrée.

**Scope** :
- `MicrosoftProvider.list_initial_messages(access_token, since)` —
  Graph API `/me/messages?$filter=receivedDateTime ge ...`
- `MicrosoftProvider.list_incremental(access_token, cursor)` — delta link
  `/me/mailFolders('Inbox')/messages/delta`
- Parsing message → `RawMessage` (réutilise `sync/parser.py` mutualisé)
- Téléchargement attachments via `/me/messages/{id}/attachments/{att-id}/$value`

**Risques identifiés** (cf. `sprint-1-planning.md` §3) :
- Format MIME différent de Gmail RFC 822 → DTO `RawMessage` partagé
  validé Sprint 1, à re-vérifier avec Outlook
- Throttling Graph (4 req/s/user) — backoff exponentiel à câbler

**Critères "Done"** :
- Tests `test_sync_microsoft.py` (≈ 10 tests miroir `test_sync_gmail.py`)
- 1 compte Outlook réel sync'd avec ≥ 50 messages, attachments OK
- Métrique : durée sync initiale `< 5 min` pour 30 jours / ~500 messages

---

## Dette identifiée Sprint 1 → à traiter Sprint 2

### D-2.1 — FE `Contact` enrichir le type TS

**Source** : ticket M1-T1.4 §22.7 (table de correspondance BE-FE).

`frontend/src/api/queries.ts::Contact` ne déclare pas encore les champs
`is_pinned`, `kind`, `unread_count`, `is_muted`, `pinned_order`,
`has_attachments`, `phone` que le BE renvoie déjà via `ContactDetail`.

**Effort** : 0.5 pt FE.
**Bloquant** : non, mais empêche de surfacer les badges dans `ContactSheet`.

### D-2.2 — Unicité `pinned_order` par compte (CHECK SQL)

**Source** : ticket M1-T1.4 §22.5 (note BE-FE).

Le BE valide `pinned_order ∈ [1,3]` mais n'impose pas l'unicité par
`account_id`. Le drag&drop FE Sprint 2 va naturellement créer des
collisions.

**Action** : ADR + migration `alembic` ajoutant
`UNIQUE(account_id, pinned_order) WHERE pinned_order IS NOT NULL`.

**Effort** : 1 pt BE + 1 pt FE (gestion 409 Conflict).

### D-2.3 — Promotion routes vers `/v1/...`

**Source** : ticket M1-T1.4 §22.8 checklist promotion v1.

Plan : Sprint 4 (cf. checklist), pas Sprint 2. Mentionné ici pour mémoire.

### D-2.4 — Daily logs governance

**Source** : ordre de mission 2026-04-22 §4.

`docs/governance/daily/<session>-<date>.md` est obligatoire. M1 doit
adopter ce format. Premier daily M1 attendu **2026-04-23**.

---

## Items hors-scope Sprint 2 (mentionnés pour traçabilité)

- **US-1.3** Auth Cloud (signup/login/JWT) — owner M2, non M1
- **US-1.4** Stripe checkout — owner M2 (dépend de US-1.3)
- **US-3.x** OCR pièces jointes — owner M3
- **US-4.x** Tour produit — owner M4

---

## Dépendances inter-sessions

- US-1.2/1.5 dépendent de **M2 D2** (résolution `ModuleNotFoundError:
  pli.auth`, deadline 2026-04-30) seulement si Microsoft OAuth réutilise
  des helpers de `pli.auth`. **À vérifier** au sync 2026-04-27.
- Aucun item M1 ne bloque M3/M4 cette sprint.

---

## Validation T1.5 — réponse explicite au ticket

> **Q (ticket M1-T1.5)** : Confirmer que US-1.2 (Microsoft OAuth, 3 pts)
> et US-1.5 (sync initiale Graph, 5 pts) sont bien parked en backlog
> Sprint 2 et pas oubliés.
>
> **R (M1, 2026-04-22)** : ✅ **Confirmé.** Les deux US sont parked dans
> ce document avec scope, critères "Done", risques, fichiers existants.
> Le report est cohérent avec :
> 1. La décision de plan documentée dans `sprint-1-planning.md` §2
> 2. La rétro Sprint 1 (`docs/retros/sprint-1-retro.md` §3)
> 3. L'action item #4 de la rétro ("PM confirme au Daily J2") — exécutée
>    par ce document.

---

_Ce backlog devient figé après validation au sync direction lundi
2026-04-27 10h. Toute modification ultérieure doit faire l'objet d'un
commentaire dans le ticket M1 correspondant._
