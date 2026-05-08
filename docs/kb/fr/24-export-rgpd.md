# Export RGPD

## Ton droit

Article 20 du RGPD : **droit à la portabilité**. Tu peux récupérer toutes les données que PLI détient sur toi, dans un format structuré et réutilisable.

## Comment exporter

Réglages → **Confidentialité** → **Exporter mes données**.

Deux options :

1. **Export complet** (recommandé) : JSON + fichiers mail `.eml` + PJ natives, le tout zippé. Taille attendue : 1-10 Go selon usage.
2. **Export métadonnées uniquement** : JSON sans mails ni PJ. Pour les utilisateurs qui veulent juste vérifier ce qu'on a sur eux.

## Délai

- Cloud : zip prêt sous 24 h (email de téléchargement, lien valable 7 j, HTTPS).
- Local : immédiat, dans un dossier de ton choix.

## Contenu du zip

```
pli_export_<date>/
├── manifest.json          # inventaire + hash SHA-256 des fichiers
├── account.json           # tes infos compte (email, prefs, abonnement)
├── contacts.json          # fiches contacts (noms, notes, domaines)
├── threads/
│   ├── thread_<id>/
│   │   ├── thread.json    # métadonnées conversation
│   │   ├── msg_001.eml    # mail 1 format RFC 822
│   │   └── attachments/   # PJ natives
│   └── ...
└── activity_log.json      # historique actions (archive, pin, swipe)
```

## Réimport

- Dans PLI : oui (bouton **Importer un export PLI** dans Confidentialité)
- Ailleurs : les `.eml` sont standard → Thunderbird, Apple Mail, Outlook acceptent

## Suppression après export

Export ≠ suppression. Pour supprimer ton compte, voir [Supprimer compte](25-supprimer-compte.md).

## Auditabilité

Chaque export génère une entrée dans `activity_log.json` (horodatage, checksums). Tu peux vérifier que rien n'a été altéré.
