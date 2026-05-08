# Sprint 10 — Stabilisation & pré-lancement (S21-S22)

**Période** : 26 août 2026 → 9 septembre 2026 (2 semaines)
**Objectif** : Encaisser les batches #2, #3, #4, fixer les bugs consolidés, livrer la KB et les assets launch, clôturer le Checkpoint 4.
**Doc parent** : [M4-KICKOFF.md](./M4-KICKOFF.md)
**Owner sprint** : PM

---

## 1. Vue d'ensemble

| Métrique | Cible fin Sprint 10 |
|---|---|
| Beta users activés total | ≥ 60 / 100 |
| NPS global | ≥ 40 |
| Rétention J30 batch #1 | ≥ 50 % |
| Bugs majeurs ouverts | ≤ 5 |
| Bugs bloquants ouverts | 0 |
| KB FR + EN | ≥ 30 articles (60 fichiers) |
| Assets launch prêts | 100 % (press kit + 2 vidéos + 10 screenshots) |

---

## 2. User stories priorisées

### Itération #2 (batches cumulés 2, 3, 4)

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-1001 | Triage tous les tickets ouverts (issus Sprint 9 + batches 2-4) | P0 | PM | continu |
| US-1002 | Fix top-5 bugs majeurs consolidés | P0 | BE + FE | 3 j |
| US-1003 | Résorber top-5 frictions UX (swipe sensitivity, composer PJ, recherche UX…) | P0 | FE + UX | 2.5 j |
| US-1004 | Rapport itération #2 publié avec tendance vs itération #1 | P0 | PM | 0.5 j |

### Performance & scaling

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-1010 | Optimiser p95 `/conversations` sous 400 ms à 50 users simultanés | P0 | BE | 1.5 j |
| US-1011 | Optimiser cold-start PWA (LCP < 2,5 s) | P1 | FE | 1 j |
| US-1012 | Paralléliser sync Graph (Microsoft) sur comptes multiples | P1 | BE | 1 j |
| US-1013 | Ajouter cache Redis sur fiche contact (TTL 5 min) | P2 | BE | 0.75 j |

### Knowledge base & support

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-1020 | Publier 30 articles KB FR (getting-started, dépannage, facturation, RGPD, sécurité) | P0 | CONT | 3 j |
| US-1021 | Publier 30 articles KB EN (miroir FR) | P0 | CONT + traducteur | 2.5 j |
| US-1022 | Intégrer Crisp chat post-onboarding J+3 avec config RGPD stricte | P0 | FE + SEC | 1 j |
| US-1023 | Définir canned responses support (top-15 questions) | P0 | CONT | 0.5 j |
| US-1024 | Rédiger runbook M5 launch (astreinte, procédures incident, contacts) | P0 | SRE + Founder | 1 j |

### Assets lancement public (M5)

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-1030 | Shooting 10 screenshots haute-def (3 écrans clés × FR/EN + mobile/desktop) | P0 | MKT | 1 j |
| US-1031 | Vidéo landing page 45-60 s (storyboard → tournage → montage) | P0 | MKT + Founder voix | 3 j |
| US-1032 | Vidéo ProductHunt 60 s (format vertical + sous-titres intégrés) | P0 | MKT | 2 j |
| US-1033 | Press release FR + EN + fact sheet | P0 | MKT | 1 j |
| US-1034 | Landing pli.app mise à jour (verbatims beta, comparatif, CTA waitlist→signup) | P0 | FE + MKT | 1 j |
| US-1035 | Kit presse zip : logos, screenshots, bio founder, fact sheet, press release | P1 | MKT | 0.5 j |

### Checkpoint 4 & bascule M5

| # | Story | Priorité | Owner | Estimation |
|---|---|---|---|---|
| US-1040 | Calcul NPS final, rétention J30 batch #1, taux activation, taux paying intent | P0 | BE + PM | 0.5 j |
| US-1041 | Rédaction M4-CHECKPOINT-4-RESULTS.md avec verdict Go/No-Go | P0 | PM + Founder | 0.5 j |
| US-1042 | Préparation M5-KICKOFF.md (draft validé avec founder) | P0 | TL + PM | 0.5 j |
| US-1043 | 20 entretiens qualitatifs founder (1-to-1 30 min) avec verbatims exploitables | P0 | Founder + CONT (prise de notes) | continu |
| US-1044 | Survey "paying intent" envoyé à tous activés, compilé | P0 | CONT + BE | 0.5 j |

---

## 3. Charge prévisionnelle vs capacité

| Agent | Charge estimée (j) | Capacité sprint (j) | Marge |
|---|---|---|---|
| BE | 7.25 | 9 | 1.75 |
| FE | 6 | 9 | 3 |
| UX | 1.5 | 3 | 1.5 |
| SRE | 2 | 4 | 2 |
| SEC | 0.5 + revues | 1 | 0.5 |
| CONT | 7 | 9 | 2 |
| MKT | 8.5 | 9 | 0.5 |
| PM | continu | 9 | — |

MKT saturé : prévoir sous-traitance vidéo si retard J+3.

---

## 4. Jalons internes sprint

- **J3 (15 août)** : tous les batches envoyés (2 → 28/08, 3 → 31/08, 4 → 04/09)
- **J5 (29 août)** : KB FR terminée à 80 %
- **J7 (01 sept.)** : vidéos en montage
- **J10 (04 sept.)** : feature freeze — plus que des fixes
- **J13 (08 sept.)** : release stabilisée, soak prod 24 h
- **J14 (09 sept.)** : checkpoint 4 + décision Go/No-Go M5

---

## 5. Critères d'acceptance — US-1031 (vidéo landing) — exemple détaillé

**Given** le storyboard validé par founder (8 scènes, durée cible 50 s)
**When** la vidéo est livrée
**Then** durée 45-60 s, résolution 1920×1080 @ 30fps minimum
**And** voix off FR + piste EN séparée
**And** sous-titres EN+FR embarqués (SRT livré aussi)
**And** logo PLI en closing 2 s
**And** musique libre de droits (licence fournie)
**And** poids fichier MP4 < 20 Mo, WebM < 15 Mo
**And** 3 versions : master, web 720p, social 1080×1080

---

## 6. Backlog reporté post-M5

| Item | Raison |
|---|---|
| KB vidéo (tutoriels 2 min) | Scope KB texte suffisant pour launch |
| Multilingue ES/DE | M4/M5 focus FR+EN |
| App native iOS/Android | V1.2 roadmap |
| Templates de réponse IA | V2 roadmap |
| SSO Team | V3 (Enterprise) |

---

*Backlog publié par PM le J1 de Sprint 10. Mid-sprint sync le 02 septembre 2026.*
