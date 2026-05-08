# Local ou Cloud : que choisir ?

PLI propose deux modes. Tu peux démarrer en Cloud (trial) et basculer en Local plus tard sans perdre tes données.

## PLI Cloud (par défaut)

- Tes mails sont stockés sur nos serveurs **en Union Européenne** (Hetzner Nuremberg / Helsinki).
- Chiffrement au repos (AES-256), chiffrement en transit (TLS 1.3).
- Tu accèdes à PLI depuis n'importe quel appareil.
- Trial 14 j gratuit, puis PLI Cloud 7 €/mois ou 70 €/an.
- **Conformité RGPD intégrale** : export, effacement, portabilité.

À choisir si tu veux : multi-appareils, pas d'installation, zéro tracas.

## PLI Local (PLI Plus)

- Tes mails sont **stockés uniquement sur ta machine**, base SQLite chiffrée (SQLCipher).
- Pas de synchro entre appareils (par design — si tu veux sync, prends Cloud).
- Tu gardes les clés Oauth (elles restent aussi en local chiffré).
- Achat unique 49 € (licence perpétuelle) ou 5 €/mois.
- Tu peux travailler totalement hors ligne.

À choisir si tu veux : maîtrise complète de tes données, aucun serveur tiers, un seul appareil principal.

## Comment basculer

**Réglages > Compte > Changer de mode**. PLI te guide pour l'export/import. Pas de perte de données, pas de re-sync complète (on transfère le cache).

En cas de doute : reste en Cloud, tu verras à l'usage.
