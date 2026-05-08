# Connecter un compte Gmail

## Ce qui va se passer

Tu vas être redirigé vers Google. Tu te connectes (si pas déjà), tu vois la liste des permissions demandées par PLI, tu acceptes. Google renvoie PLI sur ton appareil avec un jeton d'accès.

## Permissions demandées

- **Lire tes mails** (scope `gmail.readonly`) — pour afficher
- **Envoyer en ton nom** (`gmail.send`) — pour les réponses
- **Modifier** (`gmail.modify`) — pour archiver / marquer lu

PLI ne demande jamais l'accès à ton Drive, tes contacts Google, ton calendrier ou Google Photos.

## Procédure

1. Depuis PLI, **Réglages > Comptes > + Ajouter un compte > Gmail**
2. Autorise PLI sur la page Google
3. PLI revient et démarre la première sync (30 j d'historique par défaut)
4. Selon le volume, compte 1 à 5 min

## Problèmes fréquents

- **"Cette application n'est pas vérifiée"** : tu vois parfois un avertissement Google. Clique **Paramètres avancés > Accéder à pli.app (non sécurisé)**. PLI est en cours de revue Google, le message disparaîtra.
- **Code d'erreur 403** : ton admin Google Workspace a restreint les apps tierces. Vois avec lui, ou connecte un compte personnel d'abord.

## Et ensuite

Une fois connecté, PLI vérifie les nouveaux messages toutes les 2 min. Pas besoin de rester ouvert. Voir aussi [La sync ne démarre pas](26-sync-gmail-ko.md).
