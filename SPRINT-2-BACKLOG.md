# Sprint 2 · Navigation + Sync incrémentale — Backlog

**Dates** : sem. 3–4 du M1
**Thème** : pane conversation lisible, fiche contact, sync incrémentale fiable, pièces jointes téléchargeables.
**Sortie de sprint** : démo « ouvrir une conversation, lire l'historique, voir la fiche contact, télécharger une PJ — pendant qu'une nouvelle synchro tombe en arrière-plan ».

---

## User stories

### US-2.1 — Endpoint `GET /messages/by-contact/{contact_id}`  (BE · 2 pts)
- [ ] Retourne tous les messages d'un contact, triés par `sent_at ASC`.
- [ ] Champs : `id, direction, subject, body_snippet, sent_at, has_attachments, is_read`.
- [ ] Marque automatique `is_read = 1` côté serveur après réponse (idempotent).
- [ ] Pagination cursor-based si > 200 messages (rare en M1).

**Owner** : BE.

---

### US-2.2 — Pane conversation : bulles in/out + séparateurs jour  (FE · 3 pts)
- [ ] Rendu des `MessageBubble` avec direction `in` (gauche, `bubble-in`) et `out` (droite, `bubble-out`).
- [ ] Sujet affiché uniquement si différent de la bulle précédente.
- [ ] Séparateurs jour ("Aujourd'hui", "Hier", "Lundi 14 avril") entre groupes.
- [ ] Scroll automatique vers le bas à l'ouverture.
- [ ] Bouton retour visible sur mobile uniquement.

**Owner** : FE · **Dépendances** : US-2.1.

---

### US-2.3 — Sync incrémentale Gmail (`historyId`)  (BE · 5 pts)
- [ ] Stockage du dernier `historyId` connu par compte.
- [ ] `users.history.list` toutes les 60 s (configurable via `PLI_SYNC_INCREMENTAL_INTERVAL_S`).
- [ ] Application des deltas : nouveaux messages, suppressions, changements de labels.
- [ ] Si `historyId` expiré (404), bascule auto vers une resync partielle (24h).
- [ ] Test : fixture historyList → 5 nouveaux messages insérés, 1 supprimé, 1 marqué lu.

**Owner** : BE.

---

### US-2.4 — Sync incrémentale Microsoft (`deltaLink`)  (BE · 5 pts)
- [ ] Persistance du `deltaLink` retourné en fin de chaque cycle.
- [ ] `GET {deltaLink}` toutes les 60 s.
- [ ] Gestion `@odata.nextLink` durant le drain.
- [ ] Si 410 Gone → resync partielle 24h.

**Owner** : BE.

---

### US-2.5 — Endpoint `GET /contacts/{id}` enrichi  (BE · 2 pts)
- [ ] Retourne `email, display_name, company, role, notes` + `attachments[]` (50 dernières PJ).
- [ ] `PATCH /contacts/{id}` permet de mettre à jour `display_name, company, role, notes`.
- [ ] Validations : longueur < 200, sanitize HTML.

**Owner** : BE.

---

### US-2.6 — Fiche contact UI  (FE · 3 pts)
- [ ] `ContactSheet` rendu en 3e colonne sur xl, en sheet bottom sur md/mobile.
- [ ] Onglets « Conversations » (placeholder pour M1) et « Pièces jointes ».
- [ ] Liste des PJ avec icône, nom, taille humanisée, lien de download.
- [ ] Édition inline `display_name` + `company` (optimistic update).

**Owner** : FE · **Dépendances** : US-2.5.

---

### US-2.7 — Téléchargement de pièces jointes  (BE+FE · 3 pts)
- [ ] `GET /attachments/{id}/download` stream le fichier (mode local : depuis `~/.pli/att/`).
- [ ] Headers : `Content-Disposition: attachment; filename=…`, `Content-Type` correct.
- [ ] Téléchargement à la volée si pas encore en cache local (Gmail `messages.attachments.get`, Graph `/me/messages/{id}/attachments/{aid}`).
- [ ] FE : clic sur la PJ → download natif navigateur.

**Owner** : BE + FE.

---

### US-2.8 — Tests d'intégration sync  (QA · 3 pts)
- [ ] Fixtures JSON Gmail (initial 100 msgs, history +5/-1).
- [ ] Fixtures JSON Graph (delta initial 100, delta +3).
- [ ] Tests end-to-end avec `pytest-asyncio` + httpx mocks.
- [ ] Couverture sync ≥ 80 %.

**Owner** : QA + BE.

---

## Hors-scope (Sprint 3+)

- Composer + envoi → Sprint 3
- Recherche FTS5 exposée → Sprint 4
- Pin/mute UI → Sprint 4
- Swipe actions → Sprint 4

---

## DoD sprint
- [ ] Démo : ouverture conversation, lecture, téléchargement PJ, sync incrémentale visible.
- [ ] Couverture backend ≥ 75 %.
- [ ] CI verte.
- [ ] Retro consignée.
