# PLI — Index de la documentation projet

> Point d'entrée unique pour se repérer dans `/pli-app/`. À chaque nouveau milestone, on ajoute une ligne dans le tableau correspondant — jamais plus.

## Milestones

| # | Milestone | Dates | Kickoff | Checkpoint | Rétro | Statut |
|---|---|---|---|---|---|---|
| M1 | Mail conversationnel (cœur) | S7-10 | [M1-KICKOFF.md](M1-KICKOFF.md) | — | — | ✅ Livré |
| M2 | **Mode dual Local+Cloud + Paiement** | **S11-14** | [M2-KICKOFF.md](M2-KICKOFF.md) | **[M2-CHECKPOINT.md](M2-CHECKPOINT.md)** | **[M2-RETRO.md](M2-RETRO.md)** | **✅ GO conditionnel** |
| M3 | Bêta fermée 50 testeurs | S15-18 | [M3-KICKOFF.md](M3-KICKOFF.md) | — | [M3-CLOSEOUT.md](M3-CLOSEOUT.md) | ✅ Livré |
| M4 | KB + tour produit + onboarding mature | S19-22 | [M4-KICKOFF.md](M4-KICKOFF.md) | — | — | ✅ Livré |
| M5 | Lancement public | S23-26 | [M5-KICKOFF.md](M5-KICKOFF.md) | — | — | 🟡 En cours |

## Backlogs sprint

| Sprint | Dates | Fichier |
|---|---|---|
| Sprint 1 | S1-2 | [SPRINT-1-BACKLOG.md](SPRINT-1-BACKLOG.md) |
| Sprint 2 | S3-4 | [SPRINT-2-BACKLOG.md](SPRINT-2-BACKLOG.md) |
| Sprint 3 | S5-6 | [SPRINT-3-BACKLOG.md](SPRINT-3-BACKLOG.md) |
| Sprint 4 | S7-8 | [SPRINT-4-BACKLOG.md](SPRINT-4-BACKLOG.md) |
| **Sprint 5** | **S11-12** | **[SPRINT-5-BACKLOG.md](SPRINT-5-BACKLOG.md)** |
| **Sprint 6** | **S13-14** | **[SPRINT-6-BACKLOG.md](SPRINT-6-BACKLOG.md)** |
| Sprint 7 | S15-16 | [SPRINT-7-BACKLOG.md](SPRINT-7-BACKLOG.md) |
| Sprint 8 | S17-18 | [SPRINT-8-BACKLOG.md](SPRINT-8-BACKLOG.md) |
| Sprint 9 | S19-20 | [SPRINT-9-BACKLOG.md](SPRINT-9-BACKLOG.md) |
| Sprint 10 | S21-22 | [SPRINT-10-BACKLOG.md](SPRINT-10-BACKLOG.md) |
| Sprint 11 | S23-24 | [SPRINT-11-BACKLOG.md](SPRINT-11-BACKLOG.md) |

## Architecture Decision Records (ADR)

| # | Titre | Statut | Date |
|---|---|---|---|
| 0001 | [Adapters Local/Cloud](docs/adr/0001-adapters-local-cloud.md) | Accepté | 2026-06-26 |
| 0002 | [Multi-tenancy 3 couches](docs/adr/0002-multi-tenancy.md) | Accepté | 2026-06-28 |
| 0003 | [JWT sessions + refresh rotation](docs/adr/0003-jwt-sessions.md) | Accepté | 2026-06-30 |
| **0004** | **[Stripe Checkout + webhooks idempotents](docs/adr/0004-stripe-integration.md)** | **Accepté** | **2026-07-08** |
| **0005** | **[Emails transactionnels](docs/adr/0005-emails-transactionnels.md)** | **Accepté** | **2026-07-09** |
| **0006** | **[Licences offline Ed25519](docs/adr/0006-licences-offline-ed25519.md)** | **Accepté** | **2026-07-10** |
| 006 | [Itération bêta](adr/ADR-006-iteration-beta.md) | Accepté | M3 |
| 007 | [Observabilité bêta](adr/ADR-007-observability-beta.md) | Accepté | M3 |

## Légal, sécurité, docs utilisateur

- **Légal** : [CGU](legal/cgu.md) · [Politique de confidentialité](legal/privacy-policy.md) · [Mentions légales](legal/mentions-legales.md) · [Sous-traitants](legal/subprocessors.md)
- **Sécurité** : [Threat model checklist](security/threat-model-checklist.md) · [Rapport pentest S16](security/pentest-report-s16.md) · [Checklist multi-tenancy](docs/sec-checklists/multi-tenancy.md)
- **KB utilisateur** : [Index KB](docs/kb/INDEX.md) — 30 articles × 2 langues
- **Ops** : [Runbook M5](runbook/M5-launch.md) · [Monitoring runbook](M5-MONITORING-RUNBOOK.md) · [On-call checklist](M5-ONCALL-CHECKLIST.md)

---

**Dernière mise à jour** : 2026-07-15 à la sortie du Checkpoint M2.
