# Démo E2E — M1 Sprint 1 closeout (2026-04-22)

**Owner** : session M1
**Ticket** : `docs/governance/tickets/M1-sprint1-closeout.md` T1.3
**Pré-requis** : T1.2 OAuth Gmail validé (cf.
`docs/runbooks/oauth-gmail-setup.md`)

---

## But

Capturer un parcours utilisateur E2E complet du produit Sprint 1, qui
prouve que tout le chemin (login Gmail → liste contacts → conversation →
fiche contact) fonctionne sur un binaire intégré, pas seulement en tests
unitaires.

## Pré-flight check (script)

Avant de lancer la démo, exécuter `./preflight.sh` (à créer ci-dessous).

Vérifications :
- Python 3.11+ disponible
- Node 20+ disponible
- Ports 8000 et 5173 libres
- `.env` rempli avec `PLI_GMAIL_CLIENT_ID` non vide
- DB SQLite vierge (recommandé pour démo "from scratch")

## Procédure de capture

Capture **4 screenshots** numérotés `01-...png` à `04-...png`. Format PNG,
résolution mini 1280x800, fenêtre navigateur visible (pas de fullscreen
qui masque la barre d'URL).

### 01-login-gmail.png

**État** : page d'accueil PLI, premier lancement, drawer ouvert, bouton
"Connecter un compte Gmail" visible.

**Action préparatoire** :
```bash
rm -f ~/.pli/db.sqlite                      # base vierge
cd backend && uvicorn pli.main:app --reload --port 8000 &
cd ../frontend && npm run dev               # → http://localhost:5173
open http://localhost:5173                  # ou xdg-open / start
```

**Quoi capturer** : l'EmptyState avec CTA "Connecter Gmail".

### 02-list-contacts.png

**État** : sync Gmail terminée (≥ 30s après callback), liste de
conversations affichée à gauche, au moins 5 contacts visibles, badges
unread visibles.

**Action préparatoire** : suivre le flow OAuth Gmail complet (cf.
runbook). Attendre ≈ 30s après le redirect `?connected=...` que la sync
initiale se termine. Refresh la page si la liste reste vide.

**Quoi capturer** :
- Drawer compte gauche avec email connecté + badge unread global
- Liste des conversations avec avatars colorés
- Au moins 1 contact "human" et 1 contact "notif" si le inbox réel en
  contient

### 03-conversation.png

**État** : conversation ouverte sur un contact réel avec ≥ 3 messages,
ordre chronologique ASC (plus ancien en haut).

**Action** : cliquer sur n'importe quel contact dans la liste.

**Quoi capturer** :
- Header conversation (nom + email du contact)
- Bulles messages alternées in/out avec snippets
- Timestamps lisibles
- Indicateur "lu/non-lu" sur les messages

### 04-contact-sheet.png

**État** : fiche contact ouverte (panneau latéral droit ou modal).

**Action** : cliquer sur l'avatar/nom du contact dans le header
conversation.

**Quoi capturer** :
- `display_name`, email, `company`, `role` si renseignés
- Section "Pièces jointes récentes" si le contact en a
- Boutons éditer / mute / pin

## Bugs à reporter dans le ticket

Pour chaque anomalie observée pendant le runthrough, ajouter un
commentaire dans `docs/governance/tickets/M1-sprint1-closeout.md` au
format :

```
**Bug E2E-NN** (gravité: low|med|high)
- Étape : 02-list-contacts
- Symptôme : ...
- Reproductible : oui/non
- Workaround : ...
- Fix : ticket Sprint 2 #XX (ou hotfix Sprint 1 si gravité high)
```

## Done criteria T1.3

- [ ] `preflight.sh` passe sans warning
- [ ] 4 screenshots `01-`, `02-`, `03-`, `04-` présents dans ce dossier
- [ ] Au moins 1 commentaire ticket avec verdict "OK" ou liste de bugs
- [ ] Si bugs : tickets Sprint 2 créés et liés depuis le ticket M1

---

_Préparé par session M1, 2026-04-22. Exécution attendue après T1.2
(opérateur humain pour Google Cloud Console)._
