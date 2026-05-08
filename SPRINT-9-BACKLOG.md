# Sprint 9 — Ouverture beta (S19-S20)

**Période** : 12 août 2026 → 26 août 2026 (2 semaines)
**Objectif** : Inviter les 25 premiers beta users, fermer la boucle feedback, déclencher l'itération #1 sur signaux réels.
**Doc parent** : [M4-KICKOFF.md](./M4-KICKOFF.md)
**Owner sprint** : PM

---

## 1. Vue d'ensemble

| Métrique | Cible fin Sprint 9 |
|---|---|
| Beta users activés | ≥ 20 / 25 |
| Tickets Discord ouverts | ≥ 30 (signal d'usage) |
| Réponses NPS | ≥ 15 |
| Bugs bloquants résolus | 100 % |
| Release cadence tenue | 2 releases (S19-vendredi, S20-vendredi) |

---

## 2. User stories priorisées

Priorité : **P0** (bloquant ouverture), **P1** (critique sprint), **P2** (souhaitable).

### Waitlist & invitations

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-901 | En tant que visiteur pli.app, je peux m'inscrire sur la waitlist avec email + prénom + motivation (<200 car.) | P0 | FE + BE | 1 j |
| US-902 | En tant que founder, je peux générer un batch de 25 codes d'invitation depuis un script admin | P0 | BE | 0.5 j |
| US-903 | En tant que waitlister, je reçois un email avec mon code et un lien `pli.app/invited?code=...` | P0 | BE (email template) | 0.5 j |
| US-904 | En tant qu'invité, je saisis mon code lors du signup, ce qui m'active en plan beta (trial illimité jusqu'à J+90) | P0 | BE + FE | 1 j |
| US-905 | En tant qu'invité, si le code est expiré ou déjà utilisé, j'ai un message clair + CTA waitlist | P1 | FE | 0.25 j |
| US-906 | En tant que founder, je vois un dashboard admin des codes (générés / utilisés / expirés, segment) | P1 | BE | 0.5 j |

### Onboarding

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-910 | En tant que nouvel utilisateur connecté, je vois un tour produit 5 étapes au premier lancement, skippable | P0 | FE + UX | 2 j |
| US-911 | En tant qu'utilisateur, je peux relancer le tour depuis Settings > Aide | P2 | FE | 0.25 j |
| US-912 | En tant qu'utilisateur, je vois des tooltips contextuels sur : swipe actions, épinglage, filtres | P1 | FE + UX | 1 j |
| US-913 | En tant qu'utilisateur ayant complété le tour, je ne le revois jamais (sauf reset) | P0 | FE (persist prefs) | 0.25 j |

### Feedback in-app

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-920 | En tant qu'utilisateur actif depuis 7 j, je vois un widget NPS (0-10 + commentaire libre) déclenché max 1×/mois | P0 | FE + BE | 1.5 j |
| US-921 | En tant qu'utilisateur, je peux ouvrir un formulaire "Signaler un bug" ou "Suggestion" depuis un bouton flottant | P1 | FE + BE | 0.75 j |
| US-922 | En tant que founder, je vois un flux temps réel des submissions feedback (dashboard admin) | P1 | BE + FE | 0.75 j |
| US-923 | En tant qu'utilisateur, mes submissions sont anonymisées côté stockage (pas d'IP brute, hash user_id) | P0 | SEC + BE | 0.25 j |

### Observabilité & scaling

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-930 | En tant qu'oncall, je vois un dashboard Grafana "Beta overview" (users actifs, erreurs, p95 endpoints) | P0 | SRE | 1 j |
| US-931 | En tant qu'oncall, je reçois une alerte si erreur 5xx > 1% ou p95 > 600 ms pendant 5 min | P0 | SRE | 0.5 j |
| US-932 | En tant que founder, je vois la rétention J1/J7 par batch d'invitation | P1 | BE + SRE | 0.75 j |
| US-933 | En tant que founder, un load test à 100 users simultanés tourne en CI nightly sur staging | P1 | SRE | 1 j |

### Discord & animation

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-940 | Workspace Discord créé avec salons `#annonces`, `#bugs`, `#feedback`, `#feature-requests`, `#general` | P0 | CONT | 0.25 j |
| US-941 | Charte beta publiée (confidentialité, cadence feedback, ce qu'on attend des beta users) | P0 | CONT | 0.25 j |
| US-942 | Welcome bot Discord : auto-message DM avec KB top-5 + lien NPS à J+7 | P1 | CONT + BE (webhook) | 0.5 j |
| US-943 | 10 premiers articles KB FR+EN publiés et liés depuis Discord | P0 | CONT | 2 j |

### Itération #1 (fin S20)

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-950 | Triage 100% des tickets Discord + NPS ouverts (frequency × severity) | P0 | PM | continu |
| US-951 | Hot-fix top-3 bugs bloquants remontés batch #1 | P0 | BE + FE | 2 j (budget) |
| US-952 | Quick-win top-3 frictions UX remontées batch #1 | P0 | FE + UX | 1.5 j (budget) |
| US-953 | Rapport itération #1 publié : métriques + décisions + backlog impact | P0 | PM | 0.5 j |

---

## 3. Charge prévisionnelle vs capacité

| Agent | Charge estimée (j) | Capacité sprint (j) | Marge |
|---|---|---|---|
| BE | 6.5 | 9 | 2.5 |
| FE | 7.75 | 9 | 1.25 |
| UX | 1 | 3 | 2 |
| SRE | 3.25 | 4 | 0.75 |
| SEC | 0.25 + revues | 1 | 0.75 |
| CONT | 3 | 6 | 3 |
| PM | continu | 9 | — |

Marge ≈ 15 % sur BE/FE, conforme à la discipline "hot-fix budget réservé".

---

## 4. Définition de prêt (DoR) pour entrer dans le sprint

- Maquette UX validée (si FE)
- Critères d'acceptance explicites (formulation Given/When/Then)
- Estimation réalisée en planning poker async
- Dépendances externes identifiées (email provider, Discord ID, etc.)

---

## 5. Critères d'acceptance — US-920 (widget NPS) — exemple détaillé

**Given** un utilisateur connecté depuis ≥ 7 jours **And** qui ne s'est pas vu proposer de NPS dans les 30 derniers jours
**When** il ouvre l'app
**Then** un widget NPS apparaît en bas de l'écran (non bloquant)
**And** il peut noter 0-10 et ajouter un commentaire libre (500 car. max)
**And** il peut fermer sans répondre
**And** sa réponse est stockée avec `user_id_hash`, `score`, `comment`, `app_version`, `created_at`
**And** `PATCH /me/nps` renvoie 201, idempotent par session

**Non-goals** : pas de segmentation visible utilisateur, pas de relance si ignoré (attendre 30 j).

---

## 6. Backlog reporté / hors scope

| Item | Raison |
|---|---|
| Sentry session replay | Risque PII, reporté post-launch |
| NPS segmenté par cohort | Over-engineering pour M4, agrégat global suffit |
| A/B testing onboarding | Taille échantillon trop faible (25) |
| Référral program | Post-launch M5+ |
| Import iCloud mail | Hors scope M4 (pas dans PRD initial) |

---

*Backlog publié par PM le J1 de Sprint 9. Ré-arbitré chaque mid-sprint sync.*
