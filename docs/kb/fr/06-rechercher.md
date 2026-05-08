# Trouver un message

## Raccourci

- Mac : `Cmd+K`
- Windows/Linux : `Ctrl+K`
- Mobile : loupe en haut

## Ce que la recherche couvre

Contenu des messages (texte + HTML converti), sujet, expéditeur, destinataire, pièces jointes (nom + OCR si PLI Plus).

## Opérateurs

- `from:anne@x.com` — expéditeur
- `to:paul@y.com` — destinataire
- `has:attachment` — avec pièces jointes
- `before:2026-05-01` / `after:2026-05-01` — bornes temps
- `"phrase exacte"` — match littéral
- `-facture` — exclusion

Exemples :
```
contrat has:attachment from:cabinet.fr
"facture 2025" -brouillon
after:2026-06-01 TODO
```

## Astuce performance

La recherche utilise FTS5 (SQLite) et un index en RAM. Sur une base 10 000 messages, la première requête après démarrage peut prendre 300-500 ms (warm-up), les suivantes < 80 ms.

Si tu constates > 1 s systématiquement, voir [Recherche lente](29-recherche-lente.md).
