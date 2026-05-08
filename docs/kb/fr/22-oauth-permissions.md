# Permissions OAuth (Gmail / Microsoft)

## Ce qu'on demande (Gmail)

Scopes Google sollicités :

- `gmail.readonly` → lire tes mails et labels
- `gmail.send` → envoyer depuis PLI (en utilisant ton adresse Gmail)
- `gmail.modify` → marquer lu, archiver, épingler (via labels)
- `openid email profile` → identifier ton compte

On **ne demande pas** :

- Accès Drive, Docs, Calendar, Contacts, Photos
- `gmail.settings.*` (on ne touche pas à tes filtres Gmail)
- `gmail.metadata` (version dégradée qu'on n'utilise pas)

## Ce qu'on demande (Microsoft Graph)

- `Mail.Read` → lire
- `Mail.Send` → envoyer
- `Mail.ReadWrite` → marquer / déplacer
- `offline_access` → refresh token (sinon tu devrais te reconnecter chaque heure)
- `openid profile email User.Read`

## Révocation

Tu peux révoquer à tout moment côté Google ou Microsoft :

- Google : [myaccount.google.com/permissions](https://myaccount.google.com/permissions) → PLI → "Supprimer l'accès"
- Microsoft : [myaccount.microsoft.com](https://myaccount.microsoft.com/) → Applications → PLI → Retirer

Côté PLI, Réglages → **Comptes** → **Déconnecter**. Fait la même chose + supprime notre refresh token de notre DB.

## Certification & audit

PLI a suivi la **vérification OAuth Google** (brand review + privacy policy check). Pour Microsoft, publication **Multi-Tenant + Publisher Verified**.

## Minimum de privilèges

On applique le principe du **minimum nécessaire**. Si une feature demande un nouveau scope, on t'avertit in-app avant d'élargir (consentement incrémental OAuth 2.0).
