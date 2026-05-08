# Connecter un compte Microsoft

PLI supporte Outlook.com, Hotmail, Live, et les comptes Microsoft 365 (pro).

## Procédure

1. Dans PLI, **Réglages > Comptes > + Ajouter un compte > Microsoft**
2. Redirection vers `login.microsoftonline.com`
3. Connecte-toi, accepte les permissions :
   - `Mail.Read` — afficher les mails
   - `Mail.Send` — envoyer en ton nom
   - `Mail.ReadWrite` — archiver / marquer lu
   - `offline_access` — rafraîchir sans te redemander

## Compte professionnel (Microsoft 365)

Si ton compte appartient à une organisation (Microsoft 365 / Azure AD), il se peut que **l'admin doive consentir** à PLI avant toi. Dans ce cas :

- Tu vois un message "Autorisation administrateur requise"
- Envoie ce lien à ton admin : `https://login.microsoftonline.com/common/adminconsent?client_id=<PLI_CLIENT_ID>`
- Ou demande-lui d'activer "User consent for apps from verified publishers"

## Spécificités Microsoft

- La sync utilise **Microsoft Graph** (pas IMAP).
- La sync delta (incrémentale) utilise `deltaLink`. Très efficace même sur 50 000 messages.
- Les règles serveur-side Outlook ne sont **pas** synchronisées dans PLI (par design — PLI gère ses propres filtres).

Voir [Microsoft admin consent](27-microsoft-admin.md) si blocage.
