# Dispatch 2026-04-22 fin de journée — notification baseline

**Contexte** : D5 exécuté via manifeste md5 logique (cf. `docs/governance/tags/rebaseline-base-2026-04-22.md`).
**Empreinte** : `6a8d82bcbd292422f3ef87d0d6a30dce`.
**Action JM** : ouvrir chaque session ci-dessous, coller le bloc correspondant. Conserver ce fichier pour traçabilité.

---

## Message pour session M3 (Sprint 7 — Bêta fermée / Sécurité)

```
Baseline rebaseline-base-2026-04-22 posée (direction Mail).

Workspace OneDrive non git-init → substitut = manifeste md5 logique dans
pli-app/docs/governance/tags/rebaseline-base-2026-04-22.md.

Empreinte globale : 6a8d82bcbd292422f3ef87d0d6a30dce
Coverage : 72 pli/*.py + 24 tests/*.py + pyproject.toml + 8 ADRs (105 hashes).

Tu peux démarrer le re-baseline sécurité. Avant chaque campagne (pip-audit,
npm audit, trivy, Lighthouse si applicable), suis §7 du manifeste :
reconstituer manifestes locaux et diff contre le fichier de référence.

Si un seul hash diffère → suspendre la mesure + ouvrir ticket
P0-rebaseline-drift-<date>.

Deadline CLOSEOUT re-signé sur binaire intégré : 2026-05-14.
État du code de référence : Sprint 1 50/50 + M2 wire-up actif mode (b)
17→31 paths openapi, fix Fix C + extra pyproject.m2 mergés.

Consigne progression dans daily M3-2026-04-23.md.
```

---

## Message pour session M4 (Sprint 8-9 — KB + Tour + Onboarding)

```
Baseline rebaseline-base-2026-04-22 posée (direction Mail).

Workspace OneDrive non git-init → substitut = manifeste md5 logique dans
pli-app/docs/governance/tags/rebaseline-base-2026-04-22.md.

Empreinte globale : 6a8d82bcbd292422f3ef87d0d6a30dce

Tu peux démarrer le re-baseline perf/UX :
- NPS baseline (méthodologie que tu as posée hier)
- Retention J30 (cohorte post-baseline)
- Uptime measurement (point de départ 2026-04-22 00:00 UTC)

Avant chaque mesure, vérifier §7 du manifeste (diff md5). Si drift détecté
→ suspendre + ticket P0-rebaseline-drift-<date>.

Deadline : 2026-05-14 (aligné avec CLOSEOUT M3 re-signé).

Consigne progression dans daily M4-2026-04-23.md.
```

---

## Message pour session M5 (Sprint 10-11 — Launch public)

```
Info D5 : baseline rebaseline-base-2026-04-22 posée (direction Mail).

Mode substitut : manifeste md5 logique (workspace OneDrive non git-init).
Fichier : pli-app/docs/governance/tags/rebaseline-base-2026-04-22.md
Empreinte globale : 6a8d82bcbd292422f3ef87d0d6a30dce

Impact Sprint 11 §7/§8 : les pré-requis re-baseline que tu avais anticipés
sont levés → M3 et M4 débloqués aujourd'hui, deadline 2026-05-14.

Ta tâche de monitoring continue : vérifier dans tes dailies que M3+M4
postent leurs re-baselines dans la fenêtre D+21. Si drift à J+10 sans
retour, escalade direction.

Runbook §13 v1.1 reste la version de référence. ADR 0008 integration
freeze 2026-08-26 toujours non-négociable.
```

---

## Bonus — message M2 (T2.3 checkpoint)

Pour garder M2 actif sur son propre backlog (non lié D5 mais utile même timing) :

```
Bravo pour le fix Fix C + extra pyproject.m2 (validation croisée 50/50 M1).
Le daily 2026-04-23 est posé clean, accountability conftest consignée.

Prochaine étape T2.3 checkpoint (38/42 → 42/42) — rappel items :
- item 39 : coverage backend 80% min
- item 40 : CGU revue legal
- item 41 : politique privacy GDPR
- item 42 : mention rétractation 14j

Deadline 2026-05-14 (aligné avec fenêtre re-baseline M3/M4).
Consigne avancement dans daily M2-2026-04-24.md à partir de demain.
```

---

## Suivi

| Session | Envoyé ? | Accusé réception ? | Daily J+1 posté ? |
|---------|----------|--------------------|--------------------|
| M2 | ☐ | ☐ | ☐ |
| M3 | ☐ | ☐ | ☐ |
| M4 | ☐ | ☐ | ☐ |
| M5 | ☐ | ☐ | ☐ |

Cocher au fur et à mesure. Escalade si colonne 3 manque après J+2.
