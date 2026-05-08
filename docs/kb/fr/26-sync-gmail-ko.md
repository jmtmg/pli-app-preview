# Sync Gmail en erreur

## Diagnostic rapide

Réglages → **Comptes** → statut du compte Gmail :

- 🟢 **Actif** : tout va bien
- 🟡 **En attente** : sync en cours (quota API Gmail ≠ instantané)
- 🔴 **Erreur** : clic pour détail

## Erreurs fréquentes

### `invalid_grant` ou `token_expired`

Ton consentement OAuth a été révoqué (côté Google) ou ton mot de passe Google a changé avec 2FA rotative.

→ **Solution** : Réglages → Comptes → **Reconnecter**. Tu re-passes par le consentement Google, c'est rapide.

### `quota_exceeded`

Gmail rate-limite à 250 unités/seconde par utilisateur. En pratique, sync normale bien en-dessous. Si tu as 500 k mails, on passe en **mode backoff exponentiel** : ça prend plus longtemps mais ça finit par passer (quelques heures).

→ Rien à faire, laisser tourner. Tu peux fermer PLI, la sync reprend au prochain démarrage.

### `rate_limit_exceeded`

Même idée que quota mais court terme. PLI respecte les `Retry-After` headers. Patience.

### `insufficient_permission`

Ton admin Google Workspace a restreint l'app. Contacte-le et donne-lui [ce lien](27-microsoft-admin.md) (la doc Microsoft, même principe côté Google : marketplace/admin/app-access).

### `connection_refused` / `network_error`

Ton réseau bloque googleapis.com. Fréquent en entreprise derrière proxy. Tester depuis 4G pour confirmer, ensuite voir [27-microsoft-admin](27-microsoft-admin.md) (principes identiques).

## Réinitialiser la sync

Si vraiment bloqué, Réglages → Comptes → **Re-synchroniser complètement**. ⚠️ Ça retélécharge tout, peut prendre 30-60 min selon volume, pas d'impact sur Gmail lui-même.

## Toujours KO

[Support](30-support.md) avec capture d'écran de l'erreur + ton user-id (Réglages → About → Copier les infos diagnostic). On a nos logs côté serveur, on peut remonter à la cause.
