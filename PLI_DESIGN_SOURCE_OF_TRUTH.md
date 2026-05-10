# PLI — Design source of truth Cowork

Statut : canon local créé depuis l’archive Cowork récupérée, à utiliser avant toute modification frontend.
Date : 2026-05-08

## Sources vérifiées

- Archive immuable : `/Users/jm/context-engine/recovered/pli-cowork-complete-2026-05-08/source-surface/PLI-Archive-Complete/`
- Spécification textuelle : `02-Documents-Projet/03-Wireframes.md`
- Prototype haute fidélité Cowork : `02-Documents-Projet/Mail/index.html`
- Transcript de livraison : `01-Echanges/Transcripts-Bruts/01-PLI-M1.jsonl`, ligne 75 environ

Le transcript confirme que Cowork avait livré un prototype front autonome d’environ 75 Ko / 1819 lignes, avec design system fidèle au document 03, écrans P0, interactions et responsive mobile/tablette/desktop.

## Intention produit

PLI est un client mail conversationnel : UX type WhatsApp, groupée par contact, où le contact prime sur le sujet.

Principes non négociables :

1. Mobile-first réel, pas desktop réduit.
2. Minimalisme obsessionnel : tout élément doit justifier sa présence.
3. Densité utile, décoration minimale.
4. Continuité conversationnelle : un flux chronologique par personne.
5. Actions réversibles, brouillon conservé, confirmations pour destruction.
6. Performance perçue : feedback immédiat, animations < 300 ms.
7. Accessibilité WCAG AA : contrastes, targets ≥ 44 px, clavier, VoiceOver/TalkBack.

## Design tokens à respecter

Mode sombre de référence :

- Fond : `#0b0b0c`
- Surface 1 : `#121214`
- Surface 2 : `#18181b`
- Pinned : `#131318`
- Border : `#242428`
- Texte : `#ededed`
- Texte secondaire : `#8b8b92`
- Texte faible : `#5c5c63`
- Accent bronze : `#c9a47d`
- Accent soft : `rgba(201,164,125,0.14)`
- Bulle entrante : `#1c1c20`
- Bulle sortante : `#2a2520`

Système :

- Police système native uniquement.
- Grille de base : 4 px.
- Header : 52 px sous safe area.
- Items de liste : environ 68 px.
- Avatar liste : 48 px.
- Targets tactiles : minimum 44 px.
- Motion iOS : `cubic-bezier(0.32, 0.72, 0, 1)`.
- Durées : 150 ms micro, 280 ms standard.

## Écrans P0 attendus

### Liste conversations

- Header compact : menu/drawer, compte actif, recherche, composer.
- Filtres pills : Humains, Notifs, Non lus, PJ.
- Conversations groupées par contact.
- Épinglées en tête sans titre “Épinglées”, uniquement fond subtil + icône 📌.
- Preview avec `↪` pour messages envoyés par moi.
- Badge non-lu bronze.
- Liste dense mais lisible.

### Conversation

- Header : retour, avatar/contact, nom + contexte court, menu ⋮.
- Flux chronologique WhatsApp-like.
- Sujet discret au-dessus des bulles quand pertinent.
- Bulles entrantes à gauche, sortantes à droite.
- Pièces jointes comme mini-card dans la bulle.
- Composer inline en bas : trombone, champ, bouton rond d’envoi.
- Meta composer discrète : sujet / signature active, pas de bruit.

### Fiche contact

- Avatar large 76 px.
- Nom + rôle/société.
- Actions rapides : appeler, message, archiver.
- Suggestion signature détectée si disponible.
- Champs email/téléphone/société/poste.
- Notes.
- Grille pièces jointes.

### Recherche

- Tap loupe → modal plein écran.
- Focus automatique.
- Résultats dès 2 caractères.
- Groupes : Contacts / Messages / Pièces jointes.
- Highlight du terme en accent.

### Drawer comptes

- Swipe bord gauche ou bouton menu.
- Comptes avec avatar, email, non-lus.
- Compte actif : fond accent soft + barre verticale.
- Actions : Ajouter compte, Contacts, Archives, Réglages.
- Footer : état sync + thème.

## Interactions attendues

- Swipe bilatéral liste : seuil ouverture 33 %, fermeture 15 %.
- Menu ⋮ en bottom sheet : épingler/désépingler, marquer non lu, silencieux, archiver.
- Long-press 500 ms pour réordonner les épinglées.
- `⌘K` / `Ctrl+K` recherche.
- `⌘N` / `Ctrl+N` nouveau message.
- `Esc` ferme modal/drawer/sheet.
- `⌘Enter` / `Ctrl+Enter` envoie.
- Toasts courts pour actions.
- Respect `prefers-reduced-motion`.

## Responsive

- Mobile `<768 px` : un écran à la fois, navigation push horizontale.
- Tablette `768–1024 px` : liste 360 px + conversation.
- Desktop `>1024 px` : drawer comptes 240 px + liste 360/380 px + conversation flex, fiche contact en drawer droit quand utile.

## Écarts connus du MVP local actuel

Le MVP local créé sur Mac mini est fonctionnel mais incomplet par rapport au design Cowork :

- Recherche globale modal câblée côté frontend pour le MVP ; contenu PJ/OCR et benchmark restent v1.
- Swipe bilatéral et menu bottom sheet implémentés pour les actions rapides MVP.
- Long-press drag-and-drop des épinglées non implémenté.
- Sujet du composer éditable via bottom sheet et brouillons locaux autosauvegardés, avec isolation par conversation et protection contre autosave obsolète ; CC/PJ/nouveau message restent à faire.
- Fiche contact encore simplifiée.
- Drawer desktop persistant à reprendre.
- Onboarding Local/Cloud/Démo non remis en avant dans le MVP local.

Ces écarts ne doivent pas être oubliés : ils deviennent la backlog UX prioritaire après validation du prototype téléphone.

## Règle d’implémentation

Avant toute modification UI, relire ce fichier, puis vérifier dans :

1. `03-Wireframes.md` pour la règle textuelle.
2. `Mail/index.html` pour le rendu / comportement haute fidélité.
3. Le MVP React actuel pour adapter sans casser les tests et le backend local.

Toute divergence volontaire doit être documentée dans `PLI_FINAL_FUNCTIONAL_STATUS.md` ou dans un diagnostic UX dédié.
