# Filtres Humains / Notifs / Tous

La distinction **Humains / Notifications** est un principe-clé de PLI.

## Comment PLI classe

Algorithmiquement (pas de ML sensible — c'est une heuristique transparente) :

- Expéditeur avec nom générique (`noreply@`, `notifications@`, `updates@`) → Notifs
- Domaine connu d'envoi massif (Mailgun, SendGrid, etc.) + absence de salutation personnalisée → Notifs
- List-Unsubscribe header présent → Notifs
- Sinon → Humains

Tu peux **forcer la catégorie** d'un expéditeur via le menu ⋯ sur sa fiche contact.

## Règle dorée

Tu passes sur **Humains** en priorité. Les Notifs sont consultables quand tu as du temps, pas pour être interrompu.

## Filtre complémentaires

- **Non lus** : uniquement ce qui est à lire
- **Avec PJ** : messages avec attachements
- **Tous** : tout, sans filtre

## Combiner

Les filtres se cumulent : "Humains + Non lus + Avec PJ" est valide et utile pour un rattrapage le lundi matin.

## Règles perso (V1.2)

Règles avancées ("tout ce qui vient de @client.com → épinglé") : pas en V1. Arrivées prévues V1.2 sur feedback utilisateurs.
