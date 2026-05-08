# Chiffrement en mode Local

## Tech utilisée

**SQLCipher** : extension de SQLite qui chiffre l'intégralité du fichier `.db` en AES-256-CBC avec HMAC-SHA512 pour l'intégrité. Aucune feuille en clair sur le disque.

Les **pièces jointes** sont sur le disque (dossier `attachments/`), chaque fichier chiffré AES-256-GCM avec une clé dérivée de ta master key.

## Master key

Dérivée de ton **mot de passe PLI Plus** (PBKDF2-SHA256, 256 000 itérations, salt unique par install). Elle n'est jamais stockée en clair.

La master key déverrouille la DB au démarrage et reste **en RAM uniquement** pendant l'usage.

## Si tu oublies ton mot de passe

Il n'y a **pas de backdoor**. C'est le principe du chiffrement bout-en-bout. Tu peux :

1. Réinstaller PLI (nouvelle install = nouveau mot de passe) puis reconnecter OAuth → tes mails reviennent depuis Google/Microsoft, tu perds seulement tes **notes contact + règles locales + épinglages**
2. Tenter de te souvenir (prends un café) 🙂

On recommande donc **fortement** d'utiliser un gestionnaire de mots de passe (Bitwarden, 1Password, iCloud Keychain).

## Récupération par phrase mnémonique

Non. Volontairement. Ajouter une phrase de récupération = ajouter un vecteur d'attaque. Le mode Local vise le **maximum de confidentialité** — c'est à toi de gérer ton mot de passe.

## Contrôle d'intégrité

Au lancement, PLI vérifie HMAC de la DB. Si la DB a été altérée (corruption disque, tentative d'injection externe) → alerte et blocage écriture. Tu peux alors restaurer depuis ton backup.

## Audits

SQLCipher est audité open-source (Zetetic). Le [blueprint SEC-001](../../adr/ADR-001-security-baseline.md) détaille notre choix de paramètres.
