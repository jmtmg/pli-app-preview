# PLI — Planner v1

Date: 2026-05-12 14:20 CEST
Workspace: `/Users/jm/context-engine/projects/pli-app`
Statut: planner actif pour la suite v1 locale, après validation du MVP local et du prototype vocal STRATE.

## Sources lues avant planification

- `PLI_DESIGN_SOURCE_OF_TRUTH.md`
- `PLI_FEATURE_REQUESTS_SOURCE_OF_TRUTH.md`
- `PLI_FINAL_FUNCTIONAL_STATUS.md`
- `Makefile`
- Frontend actuel: `frontend/src/App.tsx`, `frontend/src/features/drawer/Drawer.tsx`, `frontend/src/api/queries.ts`
- Backend compte: `backend/pli/api/accounts.py`

## Règles non négociables

- Ne pas brancher OAuth Gmail/Microsoft réel sans flux officiel et secrets protégés.
- Ne pas déclarer Cloud/Stripe/RGPD/OCR terminés tant que les strates futures restent isolées.
- TDD pour chaque changement de comportement.
- Codex prioritaire backend/API ; Claude prioritaire frontend/UX ; cross-review avant commit.
- Garder `make test`, `make lint`, `make typecheck`, `frontend build`, `git diff --check` comme gates MVP.

## État vérifié maintenant

Déjà terminé et documenté dans le MVP local:

1. Recherche globale modal plein écran branchée `/search`.
2. Swipe bilatéral + bottom sheet actions rapides.
3. Sujet éditable + brouillons locaux autosauvegardés.
4. Fiche contact MVP enrichie.
5. Nouveau message modal local avec CC/CCI/PJ métadonnées.
6. Étude open source email réalisée.

Écarts v1 encore prioritaires:

1. Drawer comptes amélioré + statut sync + thème.
2. CC de réponse inline selon message original.
3. Préviews natives PJ côté UI locale.
4. Signature provider locale réelle ou au moins modèle de signature par compte.
5. Préparation OAuth officielle Gmail/Microsoft en runbook + architecture, sans secrets.
6. Décision architecture backend: garder SQLite MVP ou migrer vers package `pli/db/` SQLAlchemy pour M2-M4.

## Plan v1 recommandé

### Étape 1 — Drawer comptes v1, statut sync et thème MVP local

Objectif: rapprocher le drawer de la source Cowork sans OAuth réel.

Scope:

- Extraire une vue testable du drawer (`DrawerView`) qui reçoit des comptes déjà chargés.
- Afficher compte actif avec fond accent soft + barre verticale accent.
- Remplacer `Tous les comptes` comme état par défaut si pas de compte explicitement choisi, sans élargir les recherches sensibles à terme.
- Afficher statut sync lisible par compte depuis `last_sync_at`:
  - jamais synchronisé;
  - synchronisé récemment;
  - date/heure courte sinon.
- Footer: état sync global + toggle thème visuel MVP local (`Sombre` / `Clair`) sans persistance provider ni refonte tokens complète.
- Garder `Ajouter un compte Google/Microsoft` comme liens officiels existants, sans secrets.

Tests attendus:

- `frontend/src/features/drawer/Drawer.test.tsx` rend:
  - compte actif avec `aria-current` et barre active;
  - unread badge;
  - libellé provider humain (`Google`, `Microsoft`);
  - statut sync dérivé de `last_sync_at`;
  - footer `Sync à jour` / `Jamais synchronisé`;
  - toggle thème présent.

Gates étape 1:

```bash
cd frontend && npm run test -- --run src/features/drawer/Drawer.test.tsx
make test
make lint
make typecheck
cd frontend && npm run build
git diff --check
```

### Étape 2 — Réponse inline: CC selon message original

Objectif: si le dernier message contient CC, proposer le toggle CC dans le composer inline.

- Backend: exposer CC minimal ou metadata message si déjà stockée.
- Frontend: préremplir CC visible seulement si pertinent.
- Tests: modèle composer + projection API.

### Étape 3 — Préviews PJ locales

Objectif: rendre les pièces jointes déjà persistées plus utiles sans upload provider.

- Mini-preview type image/pdf/text quand metadata suffisante.
- Viewer local MVP ou état “aperçu indisponible” explicite.
- Tests render + accessibilité.

### Étape 4 — Signatures par compte MVP local

Objectif: sortir du simple toggle démo.

- Ajouter modèle local de signature par compte.
- UI réglage minimal dans drawer/footer ou modal compte.
- Tests scope account.

### Étape 5 — OAuth officiel, architecture seulement

Objectif: préparer, pas brancher en secret.

- Runbooks Gmail/Microsoft officiels.
- Matrice scopes OAuth minimaux.
- Décision stockage tokens chiffrés/local/cloud.
- Aucun secret dans repo.

### Étape 6 — Décision backend M2-M4

Objectif: rendre explicite le choix qui bloque `make test-be-all` et `make typecheck-all`.

Options:

- A. SQLite MVP canonique + futures gardés hors gate.
- B. Migration `pli/db/` SQLAlchemy + fixtures M2-M4.

Livrable: ADR + plan de migration si option B.

## Definition of done v1 locale

- Le drawer et le shell mobile/desktop sont alignés Cowork pour une démo claire.
- Aucune promesse d’OAuth/Cloud/Stripe/RGPD sans implémentation réelle.
- Gates MVP verts et statut mis à jour dans `PLI_FINAL_FUNCTIONAL_STATUS.md`.
- Toute divergence volontaire est documentée.
