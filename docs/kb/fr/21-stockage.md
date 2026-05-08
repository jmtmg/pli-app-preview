# Stockage

## Mode Cloud

Tout est stocké **sur nos serveurs EU** (Hetzner Falkenstein, Allemagne). Ce n'est pas un coffre mail complet : on garde les **métadonnées + corps + PJ indexées** pour que PLI fonctionne, mais **la source de vérité reste Gmail / Microsoft**. Si tu supprimes ton compte PLI, tes mails restent chez Google / Microsoft.

Quota Cloud : **illimité en volume**, soft cap 50 Go PJ / compte (au-delà, on t'envoie un mail pour comprendre ton usage — pas de facturation surprise).

## Mode Local

Tout est dans une base **SQLite chiffrée (SQLCipher, AES-256)** sous :

- **macOS / Linux** : `~/.local/share/PLI/pli.db`
- **Windows** : `%APPDATA%\PLI\pli.db`
- **Mobile (futur V1.2)** : sandbox app

Les PJ sont dans un dossier `attachments/` à côté, chiffrées fichier par fichier.

Quota Local : limité par l'espace disque de ton appareil. PLI alerte quand il reste <2 Go.

## Purge automatique

- Mode Cloud : aucune purge sauf si tu le demandes explicitement ou si tu annules (après 30 j de grâce).
- Mode Local : aucune purge. C'est à toi de nettoyer (bouton **Archiver > 6 mois** disponible).

## Sauvegarde

Cloud : snapshots DB toutes les 6 h, conservés 14 j. Backups chiffrés (AES-256) sur stockage offsite EU.

Local : **à toi de backuper** le fichier `pli.db` + `attachments/`. Tu peux pointer Time Machine / Backblaze dessus, ça marche.
