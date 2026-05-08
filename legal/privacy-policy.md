# Politique de confidentialité — PLI

*Version 1.0 — Dernière mise à jour : 10 août 2026*

Cette politique explique comment **Abscisse SAS** (ci-après « nous », « l'Éditeur ») traite vos données personnelles dans le cadre du service PLI. Elle est conforme au Règlement Général sur la Protection des Données (RGPD — Règlement UE 2016/679) et à la loi Informatique et Libertés modifiée.

## 1. Responsable de traitement

**Abscisse SAS**
[Adresse complète]
Contact : dpo@pli.app
Contact CNIL en cas de réclamation : www.cnil.fr

## 2. Ce que nous traitons et pourquoi

| Finalité | Données traitées | Base légale | Durée |
|---|---|---|---|
| **Gérer votre compte** | Email, mot de passe hashé, date d'inscription | Exécution du contrat (art. 6-1-b) | Durée du compte |
| **Accès à vos emails** | Tokens OAuth (chiffrés), metadata sync | Exécution du contrat | Durée du compte |
| **Consulter et envoyer vos emails** | Contenu des emails, pièces jointes | Exécution du contrat | Durée du compte |
| **Recherche plein texte** | Index FTS, texte OCR des PJ | Exécution du contrat | Durée du compte |
| **Gérer vos contacts** | Email, nom, société, notes contact | Exécution du contrat | Durée du compte |
| **Facturer votre abonnement** | Moyen de paiement (token Stripe), factures | Exécution du contrat | 10 ans (obligation comptable) |
| **Support utilisateur** | Messages support, diagnostics | Exécution du contrat | 2 ans après résolution |
| **Sécuriser le service** | Logs techniques, IP, user-agent | Intérêt légitime (art. 6-1-f) | 12 mois glissants |
| **Analytics produit** (opt-in) | Événements anonymisés | Consentement | 13 mois |

**Nous ne faisons PAS** : publicité, profilage commercial, revente de données, entraînement d'IA sur vos mails. Jamais.

## 3. Qui reçoit vos données

Nous utilisons un nombre limité de sous-traitants. La liste exhaustive, tenue à jour, est publiée sur `pli.app/subprocessors`. Principaux acteurs :

| Sous-traitant | Rôle | Localisation | Encadrement |
|---|---|---|---|
| Hetzner Online GmbH | Hébergement applicatif et BDD | Allemagne (UE) | DPA signé |
| Cloudflare, Inc. | CDN, WAF, anti-DDoS | USA | DPA + Clauses Contractuelles Types 2021 + chiffrement |
| Stripe Payments Europe | Paiements | Irlande (UE) — infra US | DPA + SCCs, données minimisées |
| Postmark / SendGrid | Emails transactionnels | UE / USA | DPA + SCCs si applicable |
| Sentry | Monitoring techniques | UE (option self-hosted activée) | DPA |
| Crisp | Support chat (PLI Cloud) | France (UE) | DPA |
| Plausible / PostHog self-hosted | Analytics anonymisés | UE / interne | DPA ou interne |

Nous informons les utilisateurs au moins 30 jours à l'avance en cas de changement majeur de sous-traitant.

## 4. Transferts hors Union Européenne

- **Cloudflare** (USA) : encadré par les Clauses Contractuelles Types 2021 (SCCs) de la Commission européenne, complétées par chiffrement TLS 1.3 et chiffrement au repos.
- **Stripe** : activité principale en Irlande, certaines données peuvent transiter par l'infrastructure US ; encadré par SCCs. Aucune donnée de contenu mail n'est transférée à Stripe (uniquement email + nom + token de paiement).

Aucun autre transfert hors UE n'a lieu.

## 5. Sécurité

Nous mettons en œuvre des mesures techniques et organisationnelles conformes à l'état de l'art :

- **Chiffrement en transit** : TLS 1.3 (1.2 en fallback), HSTS avec preload
- **Chiffrement au repos** : AES-256-GCM sur les pièces jointes Cloud, chiffrement de la base de données, chiffrement des backups
- **Tokens OAuth** : chiffrés en base avec une clé maîtresse stockée en coffre-fort séparé
- **Authentification** : Argon2id sur les mots de passe, JWT RS256 avec rotation des refresh tokens
- **Accès administratifs** : clés SSH ED25519 uniquement, bastion, MFA obligatoire pour les opérations sensibles
- **Isolation multi-tenants** : Row-Level Security PostgreSQL, tests automatiques d'isolation
- **Audits** : pentest automatisé avant chaque mise à jour majeure, audit dépendances hebdomadaire
- **Backups** : quotidiens, chiffrés, testés en restore mensuel
- **Monitoring et alertes** : détection d'anomalies, journaux centralisés

Notre modèle de menaces complet est documenté en interne et évalué selon les standards OWASP ASVS Niveau 2.

## 6. Durées de conservation

| Donnée | Conservation |
|---|---|
| Compte actif (profil, contenus mail, contacts) | Durée du compte |
| Compte supprimé | +30 jours (fenêtre d'annulation), puis purge complète |
| Factures | 10 ans (obligation comptable — art. L123-22 Code de commerce) |
| Logs de connexion (IP, timestamps) | 12 mois (LCEN art. 6-II) |
| Logs techniques généraux | 12 mois glissants |
| Backups chiffrés | 30 jours glissants |
| Tickets support résolus | 2 ans |
| Analytics anonymisés (opt-in) | 13 mois (recommandation CNIL) |

## 7. Vos droits

Vous disposez des droits suivants, exerçables à tout moment :

| Droit | Comment l'exercer | Délai de traitement |
|---|---|---|
| **Accès** (art. 15) | Paramètres → Mes données | Instantané |
| **Rectification** (art. 16) | Paramètres → champs modifiables OU support | ≤ 7 jours |
| **Effacement** (art. 17) | Paramètres → Supprimer mon compte | ≤ 30 jours |
| **Portabilité** (art. 20) | Paramètres → Exporter mes données (ZIP EML + vCard + JSON) | ≤ 7 jours |
| **Opposition** (art. 21) | Désactivation analytics OU email dpo@pli.app | ≤ 30 jours |
| **Limitation** (art. 18) | Email dpo@pli.app | ≤ 30 jours |
| **Retrait du consentement** | Paramètres (analytics) — sans conséquence sur le reste du Service | Instantané |

**Pour nous contacter** : dpo@pli.app. Nous vous répondrons dans un délai maximum de 30 jours, prolongeable à 90 jours pour les demandes complexes (avec information à vous au préalable).

**Réclamation** : vous pouvez à tout moment introduire une réclamation auprès de la CNIL (www.cnil.fr) ou de l'autorité de contrôle de votre État membre.

## 8. Cookies et traceurs

Le Service utilise un nombre limité de cookies :

| Cookie | Finalité | Durée | Type |
|---|---|---|---|
| `pli_refresh_token` | Maintenir la session (refresh JWT) | 30 j | Strictement nécessaire |
| `pli_csrf` | Protection CSRF | Session | Strictement nécessaire |
| `pli_locale` | Mémoriser la langue préférée | 1 an | Strictement nécessaire |
| `pli_analytics` | Analytics produit (anonymisé) | 13 mois | Optionnel, opt-in |

Seuls les cookies strictement nécessaires au fonctionnement sont déposés sans votre consentement, conformément à la recommandation CNIL.

## 9. Mineurs

Le Service n'est pas destiné aux personnes de moins de 15 ans. Nous ne collectons pas sciemment de données de mineurs de moins de 15 ans sans accord parental. Si nous apprenons qu'un compte a été créé par un mineur sans autorisation parentale, nous le supprimerons.

## 10. Sources des données (contacts indirects)

Dans le cadre du Service, nous traitons également des données de vos correspondants (leur email, leur nom) telles qu'elles figurent dans vos emails. Ces données n'ont pas été collectées directement auprès d'eux, mais sont nécessaires à la finalité du Service (afficher et gérer vos emails).

Nous ne les utilisons jamais à d'autres fins que celle-ci. Un correspondant peut nous contacter à dpo@pli.app pour exercer ses droits.

## 11. Notifications d'incident

En cas de violation de données personnelles susceptible d'engendrer un risque élevé pour vos droits et libertés, nous vous informerons dans un délai maximum de 72 heures après avoir pris connaissance de l'incident, conformément à l'article 34 RGPD, et notifierons la CNIL dans le même délai (art. 33 RGPD).

L'historique transparent des incidents est publié sur `pli.app/security-incidents`.

## 12. Modifications de cette politique

Nous pouvons mettre à jour cette politique. Toute modification substantielle sera notifiée par email au moins 30 jours avant son entrée en vigueur. L'historique des versions est conservé.

---

*Cette politique a été relue par un DPO externe et est maintenue à jour en continu. Pour toute question : dpo@pli.app.*
