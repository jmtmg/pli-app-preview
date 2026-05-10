# PLI — Fonctionnalités demandées dans Cowork

Statut : canon local créé depuis l’archive Cowork récupérée, à utiliser avant toute planification ou implémentation fonctionnelle.
Date : 2026-05-08

## Sources vérifiées

Archive source préservée :

`/Users/jm/context-engine/recovered/pli-cowork-complete-2026-05-08/source-surface/PLI-Archive-Complete/`

Sources principales :

- `02-Documents-Projet/01-PRD.md` — périmètre fonctionnel résumé.
- `02-Documents-Projet/02-User-Stories.md` — 56 user stories actives : 43 P0, 13 P1.
- `02-Documents-Projet/03-Wireframes.md` — comportements UI/UX attendus.
- `02-Documents-Projet/05-Roadmap.md` — découpage M0→M5/Launch.
- `01-Echanges/Syntheses/06-Synthese-Mail-Direction-Pilotage.md` — demandes et arbitrages Direction.
- `01-Echanges/Syntheses/04-Synthese-PLI-M4.md` — features bêta/feedback/tour/KB/marketing.
- Transcripts bruts `01-Echanges/Transcripts-Bruts/*.jsonl` — prompts utilisateur directs : “crée PLI”, “lance M1/M2/M3/M4/M5”, “fais tout ce qui était attendu…”, “occupe toi de tout”, “checklist…”, “review complète…”.

## Demandes utilisateur Cowork à respecter

1. Créer PLI à partir des documents existants, en format **webapp**.
2. Organiser le travail avec une équipe d’agents et fournir le meilleur résultat possible.
3. Lancer et exécuter les phases M1, M2, M3, M4, M5 selon la roadmap.
4. Respecter la roadmap quand demandé, avec gouvernance et preuves.
5. Faire les actions dans le meilleur ordre, en autonomie.
6. Vérifier ce qui est fait / manque, y compris OAuth et périmètre M1→M5.
7. Produire une review complète des sessions et recommandations par session.
8. Créer une archive complète de tous les échanges et documents PLI.

## Fonctionnalités cœur P0/P1 demandées

### 1. Onboarding, modes Local / Cloud, comptes

- Choix initial entre PLI Local gratuit et PLI Cloud 14 jours gratuits.
- Création compte PLI Cloud : email + mot de passe, confirmation email.
- Téléchargement / installation PLI Local selon OS.
- Connexion premier compte mail Gmail ou Outlook/Microsoft via OAuth officiel.
- Ajout de comptes supplémentaires depuis le drawer.
- Gestion d’au moins 12 comptes, testée jusqu’à 15.
- Drawer comptes : avatars, emails, badges non-lus, compte actif évident.
- Comptes actifs/froids : sync parallèle pour actifs, sync manuelle/économe pour froids.
- Déconnexion compte : confirmation, révocation OAuth si possible, suppression locale des données associées.
- Isolation stricte par compte : pas de fuite recherche/contact/PJ/autocomplete entre comptes.

État MVP local actuel : partiel. Compte démo local + drawer + isolation de base existent. OAuth réel, compte Cloud, reset, déconnexion officielle et 12+ comptes restent à implémenter.

### 2. Sync mail et stockage

- Sync initiale Gmail : 30 derniers jours.
- Sync initiale Microsoft : 30 derniers jours.
- Sync incrémentale : Gmail `historyId`, Microsoft Graph `deltaLink`.
- Parsing MIME : headers, body, PJ.
- Retry/backoff erreurs sync.
- Stockage SQLite + FTS5 en Local.
- PostgreSQL + isolation tenant en Cloud.
- Chiffrement au repos, notamment PJ.

État MVP local actuel : partiel/démo. Backend SQLite local et seed démo fonctionnent ; vrais providers Gmail/Microsoft non branchés en production.

### 3. Liste conversationnelle

- Écran principal = conversations groupées par contact, pas par thread RFC.
- Tri récence décroissante hors épinglées.
- Chaque ligne : avatar, nom, société si connue, heure, aperçu, badge non-lu.
- Messages envoyés par moi préfixés par `↪` dans l’aperçu.
- Non-lus visuellement distincts.
- Filtres : Humains, Notifs, Non lus, Avec PJ.
- Humains par défaut ; Notifs = bruit automatique / noreply / newsletters.
- Recherche et filtres scoped au compte actif.

État MVP local actuel : largement présent pour la démo, mais `↪`, marquage lu/non-lu automatique et heuristiques complètes Humains/Notifs restent à durcir.

### 4. Conversation ouverte

- Tap sur une ligne → ouverture conversation en push horizontal mobile.
- Scroll positionné sur dernier message.
- Flux unique chronologique par adresse/contact.
- Bulles reçues à gauche, envoyées à droite.
- Sujet affiché discrètement au-dessus de chaque message pertinent.
- Séparateurs de jour entre dates différentes.
- Pièces jointes affichées comme mini-card dans la bulle.
- Retour liste par flèche ou swipe bord gauche.

État MVP local actuel : partiel. Bulles, sujet discret et composer existent ; séparateurs de jour, push iOS complet, PJ mini-cards complètes et swipe retour restent à faire.

### 5. Recherche

- Loupe header → modal plein écran.
- Focus automatique dans le champ.
- Résultats dès 2 caractères.
- Performance cible : < 200 ms p95 sur 50k messages.
- Résultats groupés : Contacts / Messages / Pièces jointes.
- Highlight accent bronze du terme recherché.
- Tap résultat → conversation/message/PJ correspondant.
- Recherche dans contenu des PJ : PDF texte, DOCX, XLSX, TXT.
- OCR asynchrone pour images/PDF scannés.
- Recherche limitée au compte actif au MVP.

État MVP local actuel : implémenté et vérifié pour le périmètre MVP : modal plein écran frontend, focus champ, résultats groupés contacts/messages/PJ, highlight bronze, raccourci `Cmd/Ctrl+K`, sélection vers conversation/message, et scope strict `account_id`. Recherche contenu PJ/OCR et benchmark 50k restent à faire pour v1 complète.

### 6. Épinglage, actions rapides, swipe

- Épingler/désépingler depuis menu 3 points et swipe.
- Maximum 3 épinglées par compte.
- Fond épinglé subtil + icône 📌.
- Compteur X/3 dans menu.
- Action Épingler grisée si limite atteinte.
- Désépingler replace la conversation à sa vraie position chronologique.
- Réordonner épinglées par long-press 500 ms + drag-and-drop.
- Swipe gauche ou droite révèle 4 actions : Épingler/Désépingler, Non lu, Silence, Archiver.
- Les deux directions montrent les mêmes actions.
- Seuil ouverture 33 %, fermeture instinctive 15–20 %.
- Un seul panneau swipe ouvert à la fois.

État MVP local actuel : swipe bilatéral, bottom sheet actions rapides, limite UX 3/3, non-lu, silence/réactiver, archiver et mutations backend locales sont implémentés et vérifiés. Long-press drag-and-drop des épinglées et polish final restent à faire.

### 7. Composer et envoi

- Réponse inline en bas, sans changer de vue.
- Champ expandable jusqu’à 100 px puis scroll interne.
- Sujet par défaut `RE: [dernier sujet]`, éditable via bottom sheet.
- Signature automatique par compte, indicateur `Sig. [nom]`, désactivable par message.
- CC toggle si le message original contient des personnes en copie ; reply simple par défaut.
- Nouveau message via icône crayon : De, À, Sujet, Corps.
- Auto-complétion contacts dans le champ À.
- Brouillons auto-sauvegardés toutes les 3 secondes, 1 par conversation.
- PJ au composer : trombone, sélecteur natif, tuiles preview, retrait, limite 25 Mo, plusieurs PJ.
- Envoi via Gmail API ou Microsoft Graph.

État MVP local actuel : composer local et envoi simulé OK ; sujet `RE:` éditable via bottom sheet, indicateur signature démo activable/désactivable et brouillon local autosauvegardé toutes les 3 s par conversation sont implémentés et vérifiés. L'invariant `1 brouillon par compte + conversation` est protégé par scope API et index unique SQLite ; l'UI bloque l'envoi pendant une autosave en vol pour éviter la résurrection de brouillons. Signature provider réelle, CC, nouveau message modal, PJ et vrai envoi provider restent à faire.

### 8. Fiche contact

- Accès fiche : avatar liste ou avatar header conversation.
- Fiche : avatar, nom, poste/société, email, téléphone, notes.
- Actions rapides : Appeler, Message, Archiver.
- Champs éditables.
- Grille PJ échangées : type, nom, date, viewer natif.
- Suggestion depuis signature : extraction nom/téléphone/adresse/société/poste/LinkedIn.
- Bandeau suggestion : Appliquer / Modifier / Ignorer.
- Historisation des anciennes valeurs, pas d’écrasement silencieux.

État MVP local actuel : fiche simplifiée présente ; édition, actions rapides, signature suggestion et PJ grid complète restent à faire.

### 9. Personnalisation / UX / accessibilité

- Thème auto clair/sombre, avec override manuel.
- Mobile-first réel ; PWA installable.
- Responsive : mobile 1 écran à la fois, tablette split, desktop 3 colonnes.
- i18n FR + EN complète.
- Accessibilité WCAG AA : axe-core, targets tactiles, labels ARIA, clavier complet.
- Raccourcis : `Cmd/Ctrl+K`, `Cmd/Ctrl+N`, `Esc`, flèches, `Cmd/Ctrl+Enter`.
- Performance : Lighthouse > 90, LCP < 2.5s, CLS < 0.1.

État MVP local actuel : thème dark/tokens, PWA/build et responsive basique présents. i18n complète, audits a11y, raccourcis et polish responsive sont à faire.

### 10. Paiement / business / plans

- Page pricing publique : Local gratuit, Plus 39€/an, Cloud 9€/mois ou 89€/an.
- Trial Cloud 14 jours sans carte bancaire.
- Compteur J-14/J-3 et modal fin trial.
- Trial expiré : lecture seule, export toujours possible, bascule Local proposée.
- Upgrade Local → PLI Plus via Stripe.
- Activation immédiate, facture email, rappel renouvellement.
- Settings abonnement : plan, date renouvellement, moyen paiement, factures, changer plan, annuler.
- Paywall doux : expliquer bénéfice, CTA, “Plus tard”, pas plus d’un paywall/session/feature.

État MVP local actuel : non implémenté, sauf docs/code récupérés partiels. À garder hors MVP local tant que Stripe/architecture Cloud non décidés.

### 11. RGPD / conformité / vie privée

- Mentions légales, CGU, politique confidentialité FR+EN.
- Bandeau cookies CNIL sans cookies tiers MVP.
- Droit à l’effacement : suppression compte, confirmation forte, désactivation immédiate, grâce 7 jours, suppression J+30, emails de confirmation.
- Portabilité : ZIP async avec EML, vCard, JSON metadata, PJ originales ; lien 7 jours ; export chiffré Cloud.
- Page “Mes données”.
- Registre traitements / DPIA.
- Télémétrie anonyme opt-in : OFF par défaut, jamais de contenu mail ni IP, dashboard “ce que nous collectons”.

État MVP local actuel : non terminé. Ne pas déclarer conforme tant que les flows ne sont pas intégrés et testés.

### 12. Support, aide, bêta, feedback

- Knowledge base publique : au moins 30 articles au lancement, FR+EN, recherche interne, feedback par article.
- Support email : formulaire sujet/description/diagnostic anonymisé, SLA 48h.
- Chat in-app pour PLI Cloud, SLA 24h, présence agent.
- Waitlist, invitations par batches de 25.
- Tour onboarding 5 étapes : liste conversationnelle, swipe, épingle, recherche, compte/drawer.
- Feedback in-app / NPS widget.
- Discord ou Slack privé pour beta users.
- Dashboards perf/erreurs/usage, monitoring renforcé.
- Kit marketing : landing, press kit, screenshots, vidéos/storyboards.

État MVP local actuel : plusieurs artefacts docs/code existent dans l’archive, mais intégration runtime MVP non complète.

## Priorité d’exécution recommandée maintenant

Après le prototype téléphone actuel, l’ordre le plus cohérent avec les demandes Cowork est :

1. Recherche globale frontend en modal plein écran, branchée au backend `/search`.
2. Swipe bilatéral + menu bottom sheet pour actions rapides.
3. Sujet éditable via bottom sheet + vrais brouillons locaux.
4. Fiche contact complète : édition + PJ grid.
5. Drawer comptes amélioré + statut sync + thème.
6. Nouveau message modal.
7. Préparation OAuth réel Gmail/Microsoft via flux officiel.
8. Ensuite seulement : Cloud/Stripe/RGPD complet.

## Règle de travail

Avant toute nouvelle feature PLI :

1. Vérifier cette note.
2. Vérifier `PLI_DESIGN_SOURCE_OF_TRUTH.md` pour le comportement UI attendu.
3. Classer la feature : `ACTIF_VERIFIE`, `PARTIEL_A_VERIFIER`, `FUTUR_PAS_MAINTENANT` ou `BLOQUE_SECRET/ARCHI`.
4. Ajouter ou modifier un test avant d’implémenter si le comportement change.
5. Ne pas brancher OAuth/Stripe/SMTP réels sans flux officiel et secrets protégés.
