# Factures

## Où les trouver

Réglages → **Abonnement** → **Historique de facturation**. Tu vois toutes les factures émises, avec un bouton **Télécharger PDF** par ligne.

## Format

PDF A4, en français, mentions légales JMJ Consulting (siège, RCS, TVA intracommunautaire). Conforme facture électronique UE.

## Reçues par mail

Chaque paiement Stripe déclenche un mail avec PDF en PJ (envoyé à l'email principal du compte PLI). Si tu ne reçois pas → vérifier spam → sinon [support](30-support.md).

## Modifier les coordonnées (raison sociale, adresse, TVA)

Réglages → **Facturation** → **Coordonnées**. Tu peux basculer entre "Personne physique" et "Entreprise" (et renseigner un n° TVA intra, qui applique l'auto-liquidation si tu es dans l'UE hors France).

La modification s'applique aux **prochaines** factures, pas aux anciennes (principe comptable).

## Rectifier une facture passée

Erreur de coordonnées → [support](30-support.md) → avoir + nouvelle facture émis sous 48 h ouvrées.

## Paiement refusé

Stripe réessaye automatiquement sous 3-5 jours. Entre-temps, PLI reste actif (période de grâce 7 jours). Tu reçois un mail t'invitant à mettre à jour la CB.

Au-delà de 7 jours sans paiement → suspension lecture seule (comme une annulation), réactivation immédiate dès paiement.
