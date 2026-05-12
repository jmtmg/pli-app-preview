# PLI — statut final fonctionnel local

Date : 2026-05-08 18:22 CEST
Workspace : `/Users/jm/context-engine/worktrees/pli-app-codex-composer-local`
Archive source préservée : `/Users/jm/context-engine/recovered/pli-cowork-complete-2026-05-08/source-surface/PLI-Archive-Complete/`
Base de départ : `3051bef feat: add local functional MVP slice`
Commit de cette tranche courante : non créé dans ce sandbox ; `git add` ne peut pas écrire l’index du worktree situé sous `/Users/jm/context-engine/projects/pli-app/.git/worktrees/pli-app-codex-composer-local/` (`Operation not permitted`). Les changements sont laissés non commités.

## Verdict

PLI est fonctionnel en **MVP local/démo**, sans utiliser de secrets ni de comptes externes réels.

## Addendum W1 — swipe/actions rapides

Date : 2026-05-08 23:22 CEST

Nouvelle tranche implémentée et vérifiée :

- swipe bilatéral sur chaque ligne de conversation, avec mêmes actions à gauche et à droite, ouverture à 33 % et fermeture instinctive autour de 18 % ;
- menu `⋯` en bottom sheet mobile-first pour Épingler/Désépingler, Non lu, Silence/Réactiver, Archiver ;
- un seul panneau swipe ouvert à la fois, fermeture par `Esc`, toast court après action ;
- limite UX `3/3` épinglées et `Épingler` désactivé quand le compte a déjà 3 conversations épinglées ;
- backend local complété pour `mark-unread`, `archive`, mute validé et pin limité par compte ;
- migration SQLite locale idempotente pour `contacts.is_archived` afin de préserver les bases démo existantes.

Commandes vérifiées pour cette tranche : `make test` (`103 passed, 3 skipped` backend ; `16 tests passed` frontend), `make lint`, `make typecheck`, `cd frontend && npm run build`, `git diff --check`, scan diff secrets.

## Addendum W1 — brouillons locaux et sujet éditable

Date : 2026-05-10 CEST

Nouvelle tranche implémentée et vérifiée :

- API locale de brouillons : `GET /messages/drafts`, `POST /messages/drafts`, `DELETE /messages/drafts/{id}` ;
- un seul brouillon par compte + conversation, avec garde anti-fuite `account_id` / `contact_id` et index unique SQLite pour protéger aussi les écritures concurrentes ;
- composer mobile : sujet `RE:` déduit du dernier sujet, éditable via bottom sheet ;
- autosauvegarde locale toutes les 3 secondes quand le corps ou le sujet édité change, avec garde de génération pour éviter les sauvegardes obsolètes ;
- reprise du brouillon à la réouverture de la conversation ;
- toggle signature démo activable/désactivable (indicateur MVP, pas encore signature provider réelle) ;
- suppression du brouillon après envoi local simulé, avec suppression scopée au compte/contact et envoi bloqué pendant une sauvegarde en vol ;
- Makefile MVP mis à jour pour inclure `tests/test_drafts.py` dans `make test` et `make lint`.

Commandes vérifiées pour cette tranche : `make test` (`107 passed, 3 skipped` backend ; `22 tests passed` frontend), `make lint`, `make typecheck`, `cd frontend && npm run build`. Smoke runtime : backend `/health` OK, sauvegarde/lecture/suppression HTTP des brouillons OK, doublon client concurrent protégé côté DB, navigateur sans erreur console.

## Addendum W1 — fiche contact complète MVP

Date : 2026-05-10 CEST

Nouvelle tranche implémentée et vérifiée :

- fiche contact alignée Cowork MVP : avatar 76 px, nom, rôle/société, email, téléphone et notes visibles ;
- actions rapides locales `Appeler`, `Message`, `Archiver` sans OAuth ni extraction de signature réelle ;
- édition locale des champs `display_name`, `role`, `company`, `phone`, `notes` via le PATCH contact existant ;
- grille de pièces jointes lisible avec type, nom, taille, date et action `Ouvrir` ;
- états vides/accessibilité : téléphone/notes/PJ manquants explicites, labels ARIA, cibles 44 px ;
- API contact enrichie pour exposer `attachments.created_at` à la grille PJ.

Commandes vérifiées pour cette tranche : `make test` (`107 passed, 3 skipped` backend ; `28 tests passed` frontend), `make lint`, `make typecheck`, `cd frontend && npm run build`, smoke téléphone PATCH/readback sur contact démo, test FE `tel:` ciblé, `git diff --check`, scan diff secrets.

## Addendum V1 — nouveau message modal local

Date : 2026-05-11 CEST

Nouvelle tranche implémentée et vérifiée :

- bouton crayon et raccourci `Cmd/Ctrl+N` ouvrent un modal `Nouveau message` ;
- modal local avec champs `De`, `À`, `Cc`, `Cci`, `Sujet`, `Corps`, suggestions contacts et aide `Cmd/Ctrl + Enter` ;
- champs avancés `Cc/Cci` repliables, validation frontend des listes email et validation backend Pydantic via `EmailStr` ;
- pièces jointes locales MVP dans le modal : sélection native multi-fichiers, chips nom/taille, validation 25 Mo par fichier et retrait côté UI ;
- backend local accepte uniquement des métadonnées de pièces jointes (`filename`, `mime_type`, `size_bytes`) et les persiste dans `attachments` sans `sha256`, sans `local_path` et sans contenu fichier ;
- `POST /messages/send` accepte désormais `to_email + account_id` en mode local, crée un contact local si nécessaire ou réutilise un contact existant via `email_normalized` ;
- `POST /messages/send` accepte aussi `cc_emails`, `bcc_emails` et `attachments` ; les CCI sont stockées localement mais restent absentes des projections publiques de messages ;
- le message sortant reste marqué `local-out-*`, sans OAuth, sans upload provider et sans envoi Gmail/Microsoft réel.

Commandes vérifiées pour cette tranche : `make test` (`112 passed, 3 skipped` backend ; `39 tests passed` frontend), `make lint`, `make typecheck`, `cd frontend && npm run build`, `git diff --check`, scan diff secrets. Smoke local : `/health`, seed démo et `POST /messages/send` avec CC/CCI/PJ métadonnées validés sans contenu fichier.

## Addendum Planner v1 — drawer comptes, statut sync et thème MVP local

Date : 2026-05-12 CEST

Nouvelle tranche planifiée et implémentée :

- planner v1 créé dans `docs/planner/PLI_PLANNER_V1.md` pour ordonner la suite locale PLI après recherche/swipe/drafts/contact/nouveau message ;
- étape 1 lancée et livrée : drawer comptes v1 amélioré, extraction `DrawerView` testable, statut sync par compte et résumé global ;
- compte actif plus explicite avec fond accent soft, barre verticale et `aria-current` ;
- providers affichés en libellés humains (`Google`, `Microsoft`) sans brancher de nouveau flux OAuth réel ;
- statuts sync non trompeurs : `Jamais synchronisé`, `Synchronisé récemment`, `Dernière sync ...`, `Sync partielle`, `Dernière sync ancienne` ;
- drawer fermé retiré du tab order via `inert`, `aria-hidden` et `tabindex=-1`, avec focus trap clavier quand ouvert ;
- toggle thème local MVP (`Sombre`/`Clair`) exposé comme `role="switch"`, stocké uniquement en `localStorage` non sensible.

Commandes vérifiées pour cette tranche : `make test` (`112 passed, 3 skipped` backend ; `42 tests passed` frontend), `make lint`, `make typecheck`, `cd frontend && npm run build`, `git diff --check`, scan diff secrets/dangerous-code. Revue indépendante finale UX/a11y et sécurité/scope/tests : OK, aucun blocker.

Ce qui est terminé et vérifié :

- backend FastAPI local/démo démarre ;
- seed démo déterministe OK ;
- comptes, conversations, messages, recherche/contact/attachments de démo OK ;
- adresse de test locale créée et seedée : `test.pli@demo-pli.com` ;
- composer local `POST /messages/send` fonctionnel ;
- frontend React/Vite MVP buildable et servable ;
- design Cowork pris en compte via `PLI_DESIGN_SOURCE_OF_TRUTH.md` et première passe UI alignée mobile-first ;
- recherche globale frontend câblée sur `/search`, limitée au compte actif, avec modal mobile, raccourci `Cmd/Ctrl+K`, résultats contacts/messages/PJ et highlight ;
- swipe bilatéral + bottom sheet actions rapides implémentés pour Épingler/Non lu/Silence/Archiver ;
- composer enrichi MVP : sujet `RE:` éditable via bottom sheet, signature démo toggle, brouillon local autosauvegardé toutes les 3 secondes et repris par conversation ;
- fiche contact complète MVP : avatar large, infos visibles, actions Appeler/Message/Archiver, édition locale via PATCH et grille PJ lisible ;
- nouveau message modal local : `De`, `À`, `Cc`, `Cci`, `Sujet`, `Corps`, suggestions contacts, pièces jointes en métadonnées locales, envoi local par contact existant ou nouveau destinataire email ;
- tests/lint/typecheck MVP verts ;
- ESLint 9 flat config restauré (le lint frontend n’est plus seulement `tsc --noEmit`) ;
- `npm audit fix` non forcé appliqué : vulnérabilités high supprimées ;
- `make typecheck` utilise une config `backend/mypy-mvp.ini` pour garder le gate MVP strict sur les fichiers actifs sans faire échouer la tranche sur les imports M2-M4 historiques ;
- strates backend futures M2-M4 isolées par commandes explicites (`test-be-future`, `typecheck-future`) et documentées.

Ce qui n’est **pas** terminé : `make test-be-all`, `make typecheck-all`, OAuth réel Gmail/Microsoft, upload/envoi provider réel des pièces jointes, previews natives de PJ, Stripe/billing réel, RGPD/OCR/beta complets. Ces éléments sont bloqués par une décision d’architecture DB/session et/ou par des flows officiels/secrets à fournir. Je ne les déclare donc pas « finis ».

## Commandes vérifiées OK

Toutes les commandes ci-dessous ont été relancées après les modifications finales.

```bash
cd /Users/jm/context-engine/worktrees/pli-app-codex-composer-local
make test
make lint
make typecheck
cd frontend && npm run build
```

Résultats :

- `make test` :
  - backend MVP : `112 passed, 3 skipped` ;
  - frontend Vitest : `7 files passed`, `39 tests passed`.
- `make lint` :
  - backend ruff : `All checks passed!` ;
  - frontend : `eslint . && tsc --noEmit` OK, sans warning final.
- `make typecheck` :
  - backend mypy MVP : `Success: no issues found in 9 source files` ;
  - frontend TypeScript : `tsc --noEmit` OK.
- `cd frontend && npm run build` :
  - `vite v5.4.21` ;
  - `106 modules transformed` ;
  - PWA générée (`dist/sw.js`, `dist/workbox-9c191d2f.js`).

## Smoke local vérifié

### Backend

Le bind HTTP `127.0.0.1:18080` est refusé dans ce sandbox (`operation not permitted`). Le smoke runtime a donc été exécuté via `FastAPI TestClient`, en important explicitement le code du worktree avec `PYTHONPATH=backend`, sur une base SQLite temporaire sous `.diagnostics/backend/`.

Endpoints validés :

- `GET /health` → HTTP 200, `status: ok`, `mode: local`, `accounts: 1` ;
- `POST /demo/seed?reset=true` → HTTP 200, `accounts: 1`, `contacts: 4`, `messages: 5`, `attachments: 1` ;
- `POST /messages/send` avec `to_email`, `cc_emails`, `bcc_emails` et une pièce jointe metadata → HTTP 200, message sortant local `local-out-*`, `has_attachments: true` ;
- vérification SQLite : `cc_emails` et `bcc_emails` persistés, `attachments.filename/size_bytes` persistés, `sha256` et `local_path` restent `NULL` ;
- vérification projection publique : aucune adresse CCI et aucun champ `bcc` dans la réponse JSON de `/messages/send`.

### Frontend

Runtime navigateur non relancé dans ce sandbox faute de port local disponible ; le build Vite/PWA est vérifié et les tests React/Vitest du modal couvrent le rendu `Cc/Cci`, chips de pièces jointes, validation et désactivation de l’envoi.

## Design Cowork pris en compte

Source canon locale ajoutée : `PLI_DESIGN_SOURCE_OF_TRUTH.md`.

Elle synthétise les demandes et artefacts Cowork vérifiés :

- `02-Documents-Projet/03-Wireframes.md` ;
- `02-Documents-Projet/Mail/index.html` ;
- transcript de livraison M1 (`01-Echanges/Transcripts-Bruts/01-PLI-M1.jsonl`, ligne ~75).

Première passe appliquée au frontend React : header mobile 52 px, chrome minimal, bouton menu + compte + recherche + composer, composer inline plus proche wireframe avec trombone/champ/bouton rond, sujet discret `↳`, suppression d’un email personnel de démonstration dans l’UI, tokens action/motion alignés.

Écarts UI restants volontairement visibles : long-press drag-and-drop des épinglées, drawer desktop persistant, extraction signature réelle, previews natives de PJ et upload/envoi provider réel.

## Qualité frontend / audit npm

Actions :

- ajout `frontend/eslint.config.js` en flat config ESLint 9 ;
- ajout dev deps `typescript-eslint` et `globals` ;
- `frontend/package.json` : `lint` vaut maintenant `eslint . && tsc --noEmit` ;
- suppression des warnings ESLint trouvés dans le corpus frontend récupéré ;
- `npm audit fix` non forcé appliqué.

État audit :

```bash
cd frontend && npm audit --audit-level=moderate
```

Résultat final : `6 moderate severity vulnerabilities` restantes, toutes liées à `vite <=6.4.1` / `esbuild <=0.24.2` via Vite/Vitest/vite-plugin-pwa. La correction proposée par npm exige `npm audit fix --force` vers `vite@8.0.11`, changement majeur. Je ne l’ai pas forcée pour éviter une migration destructive non validée du toolchain Vite/PWA ; build, tests, lint et typecheck restent verts.

## Strates backend futures isolées

Commandes ajoutées :

```bash
make test-be-future
make typecheck-future
```

Elles isolent les suites récupérées non-MVP : auth, tenancy, feedback, Stripe/billing, beta, GDPR, OCR. Elles restent rouges par conception tant que la strate M2-M4 n’est pas réintégrée proprement.

État historique complet :

```bash
make test-be-all      # KO: 5 erreurs de collection initiales
make typecheck-all    # KO: 144 erreurs mypy dans 37 fichiers
```

Causes racines :

- `backend/pli/db.py` est un module SQLite local MVP ; les strates futures importent `pli.db.models` et `pli.db.session` comme si `pli.db` était un package SQLAlchemy ;
- `get_session`, `SessionDep`, `get_db`, `Session` absents ;
- modèles attendus absents ou incompatibles : `User`, `AuditLog`, `ExportJob`, `RefreshToken`, `ActivationEvent`, `Invitation`, `WaitlistEntry`, `FeedbackSubmission`, `AttachmentText`, etc. ;
- fixtures pytest futures absentes : `db_session`, `user_factory`, `waitlist_factory`, `feedback_factory`, `make_attachment`, `auth_headers`, `mail_outbox`, `verified_user`, `storage_mock`, `freezer`, etc. ;
- tables SQLite MVP absentes pour auth/billing/RGPD/OCR : `users`, refresh tokens/sessions, feedback, exports, `attachment_text` ;
- des tests auth/tenancy attendent un client async et des routes M2-M4 non branchées dans le runtime local MVP.

Diagnostic détaillé : `docs/diagnostics/2026-05-08-full-suite-stratification.md`.

## Comment lancer la démo locale

Depuis la racine :

```bash
cd /Users/jm/context-engine/worktrees/pli-app-codex-composer-local
make demo
```

Cela lance :

- backend : `http://127.0.0.1:8000` ;
- frontend : `http://127.0.0.1:5173` ;
- base locale : `.pli-dev/db.sqlite` ;
- pièces jointes locales : `.pli-dev/att` ;
- données démo activées par `PLI_DEMO=true`.

## Blocage humain / décision produit

Pour pouvoir dire que « tout PLI » est terminé, il faut une décision explicite :

1. garder `pli/db.py` SQLite local comme architecture MVP et déplacer officiellement beta/GDPR/OCR/auth/billing en backlog non-gate ; ou
2. migrer vers un package `pli/db/` avec `models.py`, `session.py`, SQLAlchemy, migrations, fixtures pytest et adaptation runtime local/cloud.

Ensuite seulement il sera réaliste de rendre verts `make test-be-all` et `make typecheck-all` sans maquiller les tests historiques.

Les flows externes Gmail/Microsoft/Stripe ne peuvent pas être finalisés sans credentials/flows officiels. Aucun secret réel n’a été affiché, copié, stocké ou inventé pendant cette exécution.
