# Registre des sous-traitants — PLI

*Dernière mise à jour : 10 août 2026*

Abscisse SAS tient à jour la liste exhaustive des sous-traitants traitant vos données personnelles. Tout changement majeur est notifié par email aux utilisateurs 30 jours avant sa prise d'effet.

## Sous-traitants actifs

| Sous-traitant | Rôle | Données traitées | Localisation | Transfert hors UE | DPA |
|---|---|---|---|---|---|
| **Hetzner Online GmbH** | Hébergement applicatif + BDD PostgreSQL | Toutes (chiffrées au repos) | Allemagne (UE) | Non | ✅ Signé 2026-06 |
| **Cloudflare, Inc.** | CDN, WAF, protection DDoS | Métadonnées requêtes HTTP, IPs | USA (Edge globale) | Oui — SCCs 2021 + chiffrement | ✅ Signé 2026-06 |
| **Stripe Payments Europe, Ltd.** | Traitement des paiements | Email, nom, token paiement (pas de CB) | Irlande (UE) — infra US | Oui — SCCs | ✅ Signé 2026-07 |
| **Postmark (Wildbit)** | Emails transactionnels | Email destinataire, contenu notifications | USA | Oui — SCCs | ✅ Signé 2026-07 |
| **Sentry** | Monitoring des erreurs | Logs techniques anonymisés | UE (instance self-hosted activée) | Non | ✅ Signé 2026-06 |
| **Crisp** | Support chat (PLI Cloud) | Email, messages support | France (UE) | Non | ✅ Signé 2026-07 |
| **Plausible Analytics** | Analytics opt-in anonymisées | Événements produit (no cookies, no PII) | UE (Allemagne) | Non | ✅ Signé 2026-06 |

## Sous-traitants identifiés mais non encore déployés

| Sous-traitant | Rôle prévu | Phase d'activation |
|---|---|---|
| OpenAI ou équivalent | Fonctionnalités IA (post V2) | Post-launch, sujet à consentement explicite |
| Apple / Google (App Stores) | Distribution apps natives | Post-launch V1.2 |

Ces sous-traitants sont inscrits à titre indicatif. Aucune donnée n'est transférée avant activation effective, qui fait l'objet d'une mise à jour de ce registre et d'une notification aux utilisateurs.

## Critères de sélection

Un sous-traitant n'est retenu qu'après :

1. Évaluation de sa conformité RGPD (DPA standard, localisation préférée UE)
2. Signature d'un Data Processing Agreement (DPA) incluant les clauses contractuelles types (SCCs) si transfert hors UE
3. Minimisation des données transférées (seulement le strict nécessaire)
4. Chiffrement en transit obligatoire, au repos si le sous-traitant stocke des données
5. Droit d'audit contractuel, droit de résiliation en cas de non-conformité

## Questions

Pour toute question sur ce registre ou sur les transferts de données : **dpo@pli.app**.
