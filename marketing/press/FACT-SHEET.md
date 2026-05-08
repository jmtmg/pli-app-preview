# PLI — Fiche produit presse

**Version** : v1.0 — 10 août 2026

## L'essentiel

| | |
|---|---|
| **Produit** | PLI, client mail alternatif |
| **Éditeur** | JMJ Consulting (France) |
| **Statut** | Beta privée 12 août → 9 septembre 2026 |
| **Commercial** | Mi-octobre 2026 |
| **Plateformes** | Web, macOS, Windows, Linux. Mobile prévu V1.2 |
| **Modes** | Cloud (UE) ou Local (chiffré device) |
| **Prix** | Cloud 7 €/mois · Plus 49 € perpétuel ou 5 €/mois |
| **Langues** | Français, English (V1) · ES, DE, IT, PT prévues V1.2 |
| **Site** | [pli.app](https://pli.app) |
| **Contact presse** | press@pli.app |

## Positionnement en une phrase

> Un client mail qui **sépare les humains des notifications**, tourne en **local ou en cloud européen**, et ne vend **jamais** tes données.

## Ce qui distingue PLI

- **Filtre Humains/Notifs algorithmique transparent** (pas de ML opaque)
- **Mode Local zero-knowledge** : chiffrement SQLCipher AES-256, pas de backdoor
- **Cloud 100 % UE** : Hetzner Falkenstein (Allemagne), conformité RGPD native
- **Pas de surveillance produit** : pas de pixel tracker, télémétrie opt-in
- **Export RGPD en 1 clic** (Article 20 conforme)
- **Recherche instantanée** : FTS5 SQLite, <200 ms sur 30 k messages
- **Interface minimaliste** : 5 écrans, 12 raccourcis clavier, pas de bloat
- **Raccourcis type Vim** (J/K navigation, bindings paramétrables)

## Ce que PLI n'est pas (et n'essaie pas d'être)

- Pas un calendrier
- Pas un outil collaboratif (Slack-like)
- Pas une "boîte unifiée" (PLI connecte Gmail et Microsoft Graph, pas IMAP legacy — pour l'instant)
- Pas une IA générative d'écriture (volontairement, pour V1)

## Chiffres clés beta (prévisionnel)

| Métrique | Cible M4 | Pourquoi |
|---|---|---|
| Invités batch | 100 | Profondeur sur feedback > volume |
| Activation J7 | > 70 % | Qualité onboarding |
| NPS cible | > 40 | Product-market fit signal |
| Rétention J30 | > 50 % | Utilité hebdo |
| Uptime serveur | > 99,9 % | Fondamentaux infra |
| MTTR P1 | < 30 min | Discipline ops |

## Équipe

10 personnes réparties :

- 1 PM
- 1 TL (tech lead)
- 2 BE (backend FastAPI/Postgres)
- 2 FE (React/TypeScript)
- 1 QA
- 1 UX
- 1 SRE
- 1 SEC
- 1 CONT (community/content)
- 1 MKT (growth/comms)

Basée à Paris. Statut : équipe équilibrée expérience/junior.

## Stack technique

- **Backend** : Python 3.12, FastAPI, SQLAlchemy, Alembic, PostgreSQL 15, Redis
- **Frontend** : React 18, TypeScript 5, Tailwind, Vite, i18next
- **Infra** : Docker, Kubernetes, Hetzner Cloud (EU), Terraform
- **Observabilité** : Prometheus, Grafana, Loki, Sentry
- **Sécurité** : OAuth 2.0 (Google + Microsoft), SQLCipher (local), Stripe

## Modèle économique

- **Cloud abonnement** : 7 €/mois ou 70 €/an
- **Local perpétuel** : 49 € (12 mois d'updates inclus)
- **Local abonnement** : 5 €/mois (updates à vie)
- **Engagement beta** : -50 % à vie sur le plan choisi au moment du switch commercial (M5)
- **Pas de free tier commercial** (la valeur est dans la qualité du pipe mail, pas dans un freemium cassé)

## Roadmap publique

- **M4 (août-sept 2026)** : Beta privée, 100 utilisateurs, 4 batches, 2 itérations.
- **M5 (sept-oct 2026)** : Launch commercial, ProductHunt, Hacker News.
- **V1.1 (Q4 2026)** : Règles perso, intégration calendriers (affichage), iOS beta.
- **V1.2 (Q1 2027)** : Android, 4 langues supplémentaires, IA optionnelle (résumé opt-in).

## Contacts

- **Interview fondateur** : press@pli.app → réponse sous 24 h ouvrées
- **Captures HD & vidéos** : [pli.app/press/assets](https://pli.app/press/assets)
- **Démo live** : [calendly.com/pli-press](https://calendly.com/pli-press) (créneaux 30 min)

## Mentions légales

PLI™ est une marque JMJ Consulting, SAS au capital de 10 000 €, RCS Paris 900 000 000, TVA intra FR00 000000000. Siège : 1 rue de la Paix, 75001 Paris, France.
