# Envoi de mail en erreur

## Symptômes

Tu cliques **Envoyer**, le mail reste dans l'onglet **Brouillons** ou passe dans **File d'envoi** sans partir.

## Diagnostic

Ouvre le brouillon concerné. En bas, tu vois le statut :

- 🟡 **En cours** : patience, envoi en cours (quelques secondes max)
- 🔴 **Échec** : clic sur le badge pour voir le code d'erreur

## Codes fréquents

### `quota_exceeded` (Gmail)

Gmail limite à **500 destinataires/jour** pour comptes personnels, **2 000** pour Workspace. Réinitialisation toutes les 24 h glissantes.

→ Attendre. Si récurrent, passer en Workspace (ou étaler sur plusieurs jours).

### `recipient_rejected`

Une adresse destinataire est invalide/fermée. PLI affiche laquelle. Corrige et renvoie.

### `message_too_large`

Gmail max 25 Mo total (corps + PJ). Microsoft max 20 Mo. Au-delà, PLI propose un **lien de téléchargement** (expire à 30 j, hébergé chez nous chiffré).

### `attachment_blocked`

Certaines extensions sont bloquées côté provider (`.exe`, `.js`, `.bat`). Zippe-les avant d'envoyer (Gmail bloque aussi les zip contenant du `.exe`).

### `smtp_auth_failed`

Ton token OAuth a expiré (rare, ça se renouvelle auto). → Reconnecter le compte dans Réglages.

### `rate_limited` (Microsoft)

Microsoft Graph limite à **30 messages/min**. Pour un envoi masse, PLI temporise automatiquement (ça peut prendre quelques minutes, pas d'erreur).

## File d'attente bloquée

Réglages → **Comptes** → **Vider la file d'envoi**. Attention : les mails non partis seront mis en brouillon, à toi de les renvoyer.

## Confirmation d'envoi

PLI ne fait pas de confirmation AR (Accusé Réception) standard — c'est un réglage côté destinataire et peu fiable. Si tu as besoin de confirmation légale (recommandé), passe par un service type Yousign / Registered Email.

## Rien ne marche

[Support](30-support.md) avec l'horodatage de la tentative et le code erreur.
