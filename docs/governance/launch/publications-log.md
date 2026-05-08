# Journal des publications externes M5 / Launch

**Créé** : 2026-04-22 (ticket `M5-freeze.md` T5.2)
**Tenu par** : CONT + PM, contresigné Founder + direction

---

## 1. Règle d'or

**Aucune publication externe sans entrée préalable dans ce journal avec feu vert écrit.**

Le "feu vert direction" se matérialise par une ligne validée `statut=approved` dans le tableau ci-dessous, signée (initiales) par la direction. Tant que la ligne est `statut=pending` ou `statut=draft`, **rien ne part** sur aucun canal.

En cas de doute, **par défaut : ne pas publier.** Passer par le Discord interne d'abord.

> **Note 2026-04-22 — Validation bundle contenu drafts** : Direction a validé **en l'état** le contenu des trois drafts (`blog-pourquoi-pli.md`, `social-teasers.md`, `email-beta-ouverture.md`). Les drafts sont gelés côté contenu tant que la re-baseline M3/M4 (D5, 2026-05-14) n'a pas produit les chiffres réels à substituer aux `{placeholders}`. **Le feu vert bundle ne dispense pas du feu vert par ligne de publication** : chaque entrée du §2 ci-dessous reste à `draft` jusqu'à ce que CONT la passe en `pending` puis que direction signe `approved` à la date cible.

---

## 2. Tableau des publications

| ID | Date cible | Plateforme | Type | Source draft | Statut | Signature direction | URL live |
|---|---|---|---|---|---|---|---|
| S-01 | TBD (≥ Sprint 11 J-3) | LinkedIn | Post teasing | `drafts/social-teasers.md` §S-01 | draft | — | — |
| B-01 | TBD (Sprint 11 J6) | Blog pli.app | Article ouverture | `drafts/blog-pourquoi-pli.md` | draft | — | — |
| S-02 | TBD (Sprint 11 J6) | LinkedIn | Post ouverture | `drafts/social-teasers.md` §S-02 | draft | — | — |
| S-03 | TBD (Sprint 11 J7) | LinkedIn | Métriques J+1 | `drafts/social-teasers.md` §S-03 | draft | — | — |
| S-04 | TBD (Sprint 11 J8) | LinkedIn | Itération #1 | `drafts/social-teasers.md` §S-04 | draft | — | — |
| S-05 | TBD (Sprint 11 J9) | X/Bluesky/Threads | Thread bilan | `drafts/social-teasers.md` §S-05 | draft | — | — |
| S-06 | TBD (Sprint 11 J9) | LinkedIn | Bilan 5 j | `drafts/social-teasers.md` §S-06 | draft | — | — |
| S-07 | TBD (Sprint 11 J10) | LinkedIn | Rapport clôture | `drafts/social-teasers.md` §S-07 | draft | — | — |
| E-01 | TBD (Sprint 11 J6) | Email list annonce | Email ouverture beta | `drafts/email-beta-ouverture.md` | draft | — | — |

**Valeurs de `statut`** : `draft` → `pending` (CONT a soumis pour validation) → `approved` (direction a signé) → `scheduled` (post programmé) → `published` (publication effective avec URL live) → `retracted` (rappelé, avec raison).

---

## 3. Historique des modifications

| Date | Action | Auteur | Commentaire |
|---|---|---|---|
| 2026-04-22 | Création du journal | Session M5 | Formalisation T5.2 ticket M5-freeze.md. Tous les drafts existants intégrés avec statut `draft`. |
| 2026-04-22 | Validation bundle drafts (contenu) | Direction (session Mail) | Validés en l'état : blog, social, email beta. Règle no-send confirmée opérationnelle dès 2026-04-22. Feu vert par ligne toujours requis. |
| 2026-04-22 | Validation ADR 0008 | Direction (session Mail) | Signée telle quelle, freeze 2026-08-26 entériné. Voir `docs/adr/0008-integration-freeze.md`. |

---

## 4. Process d'approbation

1. **CONT** finalise un draft dans `docs/governance/launch/drafts/`, coche sa checklist interne, et passe le statut à `pending` dans ce tableau.
2. **Direction (session Mail)** relit. Si OK, signe par ses initiales + passe à `approved`. Si non, écrit les corrections en commentaire du PR et reste à `pending`.
3. **CONT ou Founder** programme la publication et passe à `scheduled`.
4. **Au moment de la publication effective**, l'URL live est ajoutée et le statut passe à `published`.
5. **En cas de rappel** (erreur, incident, contre-indication), le post est retiré de la plateforme et le statut passe à `retracted` avec la raison documentée.

---

## 5. Escalation

- Publication non autorisée détectée → **incident P1 de gouvernance**. Le founder ou la direction retire le post et ouvre une note dans `docs/governance/daily/` sous 2 heures ouvrées.
- Désaccord éditorial → tranchage direction sous 24 h ouvrées.

---

_Référence : ordre de mission `docs/governance/2026-04-22-ordre-mission.md` §7. Ticket émetteur : `docs/governance/tickets/M5-freeze.md` T5.2._
