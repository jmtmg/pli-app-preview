# Sprint 4 · Recherche + Pin/Mute + Polish — Backlog

**Dates** : sem. 7–8 du M1
**Thème** : recherche FTS5 fluide, swipe actions bidirectionnelles, PWA installable. Clôture du M1 et go/no-go pour M2.
**Sortie de sprint** : démo « tout le parcours utilisateur final + démo PWA installable iOS/Android ».

---

## User stories

### US-4.1 — Endpoint `GET /search?q=`  (BE · 3 pts)
- [ ] Tokenize `q` en mots ; chaque mot suffixé `*` pour le prefix matching FTS5.
- [ ] Trois requêtes parallèles : contacts (LIKE sur `email`/`display_name`), messages (FTS5 via `messages_fts`), attachments (FTS5 via `attachments_fts`).
- [ ] Réponse `{ contacts: [...], messages: [...], attachments: [...] }`, max 20 chacun.
- [ ] Latence p95 < 100 ms sur 10 000 messages (mesurer avec pytest-benchmark).

**Owner** : BE.

---

### US-4.2 — UI recherche  (FE · 3 pts)
- [ ] Input recherche dans le `Header` déclenche un drawer de résultats (overlay sur la liste).
- [ ] Trois sections : Contacts, Messages, Pièces jointes — labels clairs même quand vide.
- [ ] Highlight des termes matchés (surlignage `accent-soft`).
- [ ] Clic sur résultat → ouvre la conversation/contact correspondant.
- [ ] Debounce 200 ms.

**Owner** : FE.

---

### US-4.3 — Pin/Unpin/Mute  (BE+FE · 3 pts)
- [ ] BE : routes `POST /conversations/{id}/pin`, `/unpin`, `/mute` déjà scaffoldées — finaliser logique max 3 épinglés.
- [ ] FE : menu contextuel sur long-press (mobile) ou clic droit (desktop).
- [ ] Animation : la conversation glisse en haut de la liste après pin (200 ms cubic-bezier).
- [ ] Indicateurs visuels : 📌 + barre verticale accent à gauche.

**Owner** : BE + FE.

---

### US-4.4 — Swipe actions bidirectionnelles  (FE · 5 pts)
- [ ] `@use-gesture/react` sur `ConversationRow`.
- [ ] Swipe gauche → Archiver (seuil 33 % de la largeur, action immédiate).
- [ ] Swipe droite → Marquer non-lu / Lu (seuil 15 %, toggle).
- [ ] Background coloré selon direction (rouge archive / accent unread).
- [ ] Annulation possible : toast 5 s avec bouton "Annuler".
- [ ] Tests : Playwright + simulation gestures.

**Owner** : FE.

---

### US-4.5 — PWA installable  (FE · 3 pts)
- [ ] `vite-plugin-pwa` configuré avec manifest (icônes 192/512, theme `#0b0b0c`, name "PLI").
- [ ] Service worker : cache statique + runtime cache pour `/api/conversations` (max 1 min).
- [ ] Tests Lighthouse PWA ≥ 90.
- [ ] Installation testée sur iOS Safari et Android Chrome.

**Owner** : FE.

---

### US-4.6 — Performances + accessibilité  (FE+UX · 3 pts)
- [ ] Liste virtualisée si > 100 conversations (`@tanstack/react-virtual`).
- [ ] Lighthouse Performance ≥ 90 (mobile).
- [ ] Audit a11y avec axe : 0 erreur critique.
- [ ] Vérification contraste WCAG AA sur tous les états (dark + light).

**Owner** : FE + UX.

---

### US-4.7 — Documentation utilisateur + démo  (PM · 2 pts)
- [ ] Rédaction d'un guide utilisateur (`docs/guide-utilisateur.md`) : connexion, navigation, recherche, raccourcis.
- [ ] Screencast 5 min de la démo M1 (à diffuser aux stakeholders).
- [ ] Page `/about` dans l'app avec versions, licences, support.

**Owner** : PM + UX.

---

## DoD sprint + DoD M1
- [ ] Toutes les US M1 (Sprint 1→4) livrées.
- [ ] Couverture backend ≥ 80 %, frontend ≥ 65 %.
- [ ] Lighthouse PWA + Perf + a11y ≥ 90.
- [ ] Démo M1 enregistrée et présentée.
- [ ] Go/No-Go M2 voté en comité.
- [ ] Retro M1 complète (3 sprints + 1 milestone).
