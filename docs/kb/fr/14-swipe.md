# Swipe actions

## Seuils

PLI utilise **deux seuils** par direction :

- 15 % de la largeur écran → action légère
- 33 % → action définitive

Pourquoi deux : éviter les actions destructrices accidentelles sur un micro-swipe.

## Droite (archiver / lire)

- 15 % → marquer lu
- 33 % → archiver

## Gauche (non lu / silence)

- 15 % → marquer non lu
- 33 % → silence 7 j (snooze)

## Retour en arrière

Chaque action affiche un toast en bas "Archivé · Annuler". Tu as 5 secondes.

## Sensibilité

Trop sensible / trop rigide ? Signale via `#feedback` — on a des batches d'itération dédiés. Les seuils ont été ajustés après le batch #1 de la beta (voir [rapport itération #1](../../reports/iteration-1.md) si tu y as accès).

## Désactiver temporairement

Mode lecture (conversation ouverte plein écran) → pas de swipe sur la liste.
