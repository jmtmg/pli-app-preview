# ADR 0006 — Licences PLI Plus hors-ligne signées Ed25519

- **Statut** : Accepté · 2026-07-10
- **Décideurs** : Claude-Founder (produit), Claude-BE, Claude-SEC
- **Lien Sprint** : Sprint 6, US-6.4

## Contexte

PLI Local doit pouvoir fonctionner **entièrement offline**, y compris pour des users Plus payants. Impossible d'exiger une connexion au serveur Cloud pour chaque démarrage de l'appli. Il faut donc un **artefact cryptographique** transporté avec l'appli, qui atteste "ce user a le droit d'utiliser Plus jusqu'à telle date".

Les exigences produit :

1. **Offline-first** — aucune requête réseau pour vérifier la licence à l'usage.
2. **Non-transférable** — rattaché à l'email utilisateur, pas juste à la machine.
3. **Expiration claire** — un abonnement annulé ne doit pas continuer à débloquer Plus indéfiniment.
4. **Révocable** — bonus si on peut révoquer a posteriori (via liste noire téléchargée si online).
5. **Pas de PII dans le blob** — si le fichier fuite, il ne doit pas révéler l'email en clair.

## Options envisagées

### Option A — Licence opaque + vérification serveur à chaque démarrage
Simple, mais viole (1) offline-first.

### Option B — Licence JWT (HMAC-SHA256, clé partagée)
La clé partagée doit être embarquée dans le binaire client → extraction triviale via désassemblage → possibilité de forger des licences. **Rejeté**.

### Option C — Licence JWT (RS256/ES256) — clé asymétrique
Clé publique embarquée, clé privée côté serveur. Solide, mais JWT pour un usage non-HTTP est overkill (champs `iss`/`aud`/`exp` mal calibrés pour ce cas).

### Option D — Blob custom signé Ed25519
Format minimal : `{payload_b64url, sig_b64url}`. Ed25519 = rapide à vérifier, clés courtes (32 o), librairie native `cryptography`.

## Décision

**Option D — Ed25519** avec format maison documenté.

### Schéma du payload

```json
{
  "user_hash":  "…32 hex chars…",   // sha256(email)[:32]
  "plan":       "plus_yearly",      // plus_trial|plus_monthly|plus_yearly
  "issued_at":  "2026-07-15T12:00:00+00:00",
  "expires_at": "2027-07-15T12:00:00+00:00",   // null si lifetime
  "version":    1
}
```

Le payload est sérialisé en JSON canonique (clés triées, pas d'espaces), base64-url-encodé, signé par la clé privée Ed25519 serveur.

### Côté serveur Cloud (émission)

Endpoint `POST /licenses/issue` (auth PLI requise) :
- Vérifie que l'utilisateur a un abonnement actif (`subscriptions.plan != free`).
- Calcule `user_hash = sha256(email)[:32]`.
- Sérialise + signe avec `PLI_LICENSE_SIGNING_KEY` (clé privée Ed25519 b64).
- Retourne `{payload, sig, version}`.

### Côté client Local (activation & vérification)

Endpoint `POST /licenses/activate` :
- Vérifie la signature avec la clé publique embarquée (`EMBEDDED_PUBLIC_KEY_B64`, ou `PLI_LICENSE_PUBLIC_KEY` en env pour les builds internes).
- Vérifie `user_hash` correspond à `sha256(email_user)` — lève si mismatch.
- Vérifie la version (`== LICENSE_VERSION`).
- Persiste `{payload, sig}` dans `~/.pli/license.json` (chmod 0600).

GET `/licenses/status` renvoie `{plan, issued_at, expires_at}` après re-vérif signature (chaque appel) pour détecter une altération sur disque.

### Pas de PII

`user_hash` = SHA-256 tronqué = **8 octets d'entropie effective** sur l'email. Assez pour empêcher la réattribution (pas de correspondance facile avec un email connu), pas assez pour faire exploser la taille de la licence. Si un blob fuite, on ne peut pas identifier la personne sans avoir déjà la liste des emails candidates.

### Rotation de clé

Script `scripts/generate_license_keypair.py` produit une nouvelle paire. Procédure de rotation :
1. Générer nouvelle paire sk', pk'.
2. Déployer `pk'` dans une nouvelle release client (pk et pk' cohabitent, verify tente les deux).
3. Après window d'adoption, émettre les nouvelles licences avec sk'.
4. Rotation sk → sk' côté serveur.
5. Décommissionner pk au passage d'une release majeure.

## Conséquences

**Positives** :
- Verify coûte ~ 100 µs Ed25519 — négligeable au boot.
- Blob complet tient en ~300 octets base64 → facile à transporter.
- `verify_license()` lève proprement `ValueError` avec message pour 5 cas : signature, version, payload malformé, email mismatch.
- Tests : 6 scénarios couverts (roundtrip, email mismatch, sig tamper, payload tamper, expiration, cross-keypair).

**Risques / contraintes** :
- **Fuite clé privée = compromis total**. Elle doit rester dans les secrets Fly.io uniquement, jamais en env var d'un dev, jamais dans un log. Monitoring : si `PLI_LICENSE_SIGNING_KEY` apparaît dans un log Sentry → alerte critique.
- **Pas de révocation online** en M2. Si on veut la révocation (abonnement remboursé), il faudra ajouter en M3 une CRL téléchargée au démarrage (quand online). Décalé hors scope M2.
- **Horloge machine** : l'expiration compare à `datetime.now()`. Un user qui retarde son horloge peut prolonger artificiellement sa licence. Acceptable : le coût d'un hack pour économiser 96 €/an est disproportionné, et le cas se détecte à la prochaine connexion.

## Plan de rollback

Impossible de "retirer" une licence émise. Si bug dans le format, livrer un nouveau client qui accepte l'ancien ET le nouveau format (champ `version` prévu pour ça).

## Lien avec le side Cloud

Côté Cloud, les licences sont aussi tracées dans la table `licenses` (user_id, plan, valid_until, status, stripe_subscription_id UNIQUE). La source de vérité reste `subscriptions.plan`. La table `licenses` est un miroir pour audit et pour l'endpoint `/licenses/issue`.
