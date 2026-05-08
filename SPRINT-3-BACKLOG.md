# Sprint 3 · Composer + Envoi — Backlog

**Dates** : sem. 5–6 du M1
**Thème** : rédiger, sauvegarder un brouillon, envoyer — et voir le message partir en temps réel dans la conversation.
**Sortie de sprint** : démo « répondre à un contact depuis PLI, le message arrive effectivement dans la boîte destinataire ».

---

## User stories

### US-3.1 — Modèle Draft + stockage  (BE · 2 pts)
- [ ] Table `drafts(id, contact_id, account_id, subject, body, created_at, updated_at)` déjà présente — activer les routes.
- [ ] `POST /messages/drafts` crée ou met à jour le brouillon (upsert sur `contact_id`).
- [ ] `GET /messages/drafts?contact_id=` renvoie le draft courant ou 404.
- [ ] `DELETE /messages/drafts/{id}`.

**Owner** : BE.

---

### US-3.2 — Envoi via Gmail API  (BE · 4 pts)
- [ ] `POST /messages/send` accepte `{contact_id, body, subject?}`.
- [ ] Construction MIME (RFC 822) avec `In-Reply-To` et `References` si c'est une réponse dans un thread existant.
- [ ] Encode en base64url, appelle `users.messages.send`.
- [ ] Ajoute le message envoyé dans la DB avec `direction='out'`.
- [ ] Invalide le brouillon correspondant.

**Owner** : BE.

---

### US-3.3 — Envoi via Microsoft Graph  (BE · 4 pts)
- [ ] `POST /me/sendMail` avec payload `{message: {subject, body, toRecipients}}`.
- [ ] Si c'est une réponse : `POST /me/messages/{id}/reply`.
- [ ] Gestion erreurs 401 (refresh) → retry.
- [ ] Persistance DB.

**Owner** : BE.

---

### US-3.4 — Composer UI inline  (FE · 3 pts)
- [ ] Textarea auto-resize (1 → ~6 lignes, scroll ensuite).
- [ ] Méta-bar : "Sujet : <réponse> · De : <compte>".
- [ ] Bouton "Envoyer" (raccourci Cmd/Ctrl + Entrée).
- [ ] État disabled si corps vide ou envoi en cours.
- [ ] Optimistic update : la bulle `out` apparaît immédiatement avec opacité 0.6, devient opaque au succès.
- [ ] En cas d'erreur : toast rouge + le draft reste dans le composer.

**Owner** : FE.

---

### US-3.5 — Autosave brouillon  (FE · 2 pts)
- [ ] Débounce 1 s après dernière frappe + envoi toutes les 30 s max.
- [ ] Au changement de conversation, `POST /messages/drafts` appelé avant le démontage.
- [ ] Au retour sur la conversation, `GET /messages/drafts?contact_id=` repopule le composer.

**Owner** : FE.

---

### US-3.6 — Tests end-to-end Playwright  (QA · 3 pts)
- [ ] Ouvrir conversation → taper → envoyer → vérifier présence de la bulle out.
- [ ] Interrompre (fermer conversation) → revenir → draft restauré.
- [ ] Erreur réseau mockée → toast + draft préservé.

**Owner** : QA.

---

## DoD sprint
- [ ] Envoi fonctionnel sur les 2 providers.
- [ ] Autosave testée.
- [ ] CI verte.
- [ ] Couverture ≥ 75 % (BE) / ≥ 60 % (FE).
