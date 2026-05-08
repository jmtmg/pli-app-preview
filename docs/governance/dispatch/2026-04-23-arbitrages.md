# Dispatch 2026-04-23 soir — arbitrages A1-A5

**Contexte** : réponse direction aux 4 questions M3 (daily 2026-04-23) + 1 question M5 (daily 2026-04-23).
**Fichier arbitrages** : `docs/governance/arbitrages/2026-04-23-baseline-infra.md` (référence complète).
**Action JM** : coller chaque bloc dans la session correspondante.

---

## Message pour session M2

```
Arbitrages A1-A5 posés (docs/governance/arbitrages/2026-04-23-baseline-infra.md).

Concerne M2 directement (A2) :
- backend/requirements.lock posé par direction via uv pip compile (295 lignes,
  md5 548ce01ef60b32ec725174f4ab4ebaee). Extra m2 inclus.
- Désormais M2 est propriétaire de ce lockfile : à chaque bump pyproject.toml,
  régénérer via : cd backend && uv pip compile pyproject.toml --extra m2
  -o requirements.lock --python 3.11

Règle A1 freeze backend/pli/ + tests/ + pyproject.toml jusqu'au 2026-05-14.
Pour T2.3 #39 (coverage 80%), tu n'as besoin de modifier que backend/tests/
(ajout de tests). Si refactor nécessaire dans backend/pli/ → ticket P0 + bump
manifeste par direction.

Tag logique baseline rebaseline-base-2026-04-22 confirmé (substitut au tag git).
Empreinte globale 6a8d82bcbd292422f3ef87d0d6a30dce. Tu peux fermer la boucle
attente baseline dans ton daily 2026-04-24.

Continue T2.3. Rappel deadline 2026-05-14 sur items 39/40/41/42.
```

---

## Message pour session M3

```
Arbitrages A1-A5 posés (docs/governance/arbitrages/2026-04-23-baseline-infra.md).

Bonnes nouvelles :
- A2 : backend/requirements.lock GÉNÉRÉ par direction (uv pip compile,
  md5 548ce01ef60b32ec725174f4ab4ebaee, 295 lignes). Tu peux lancer
  pip-audit --requirement backend/requirements.lock dès que tu as accès
  à un env Python 3.11+ (la sandbox 3.10 ne convient pas).
- A4 : Dockerfile actuel est déjà multi-stage (builder + runtime),
  pas besoin de Dockerfile.prod séparé. Commande build :
  docker build --target runtime -t pli/backend:prod backend/

Arbitrages A3 (package-lock.json) et build image délégués à M4 :
- package-lock.json deadline 2026-04-25 fin de journée
- image pli/backend:prod deadline 2026-04-27 fin de journée

Chaîne complète scan officiel débloquée après 2026-04-27. En attendant :
- tu peux déjà pré-écrire la section 3.3 du rapport 2026-04-22-rebaseline-m3.md
- relire security/threat-model-checklist.md pour identifier les 27 contrôles T3.2
- préparer fixtures OCR manquantes

A5 accepté : OpenAPI 17→31 check reste à charge env officiel 3.11+.
Documente la limite dans REBASELINE-CHECKLIST.md §7.

A1 règle freeze : tu es consommateur baseline, aucun impact sur ton travail.
Mais vigile : si tu vois une PR toucher backend/pli/ pendant la fenêtre,
ping direction immédiatement.

Daily 2026-04-24 attendu avec ack arbitrages.
```

---

## Message pour session M4

```
URGENT — plusieurs actions attendues.

1) Daily M4-2026-04-23.md MANQUANT. À poster en priorité aujourd'hui
   (même minimal : ack baseline + état d'avancement re-baseline perf/UX).
   Pattern : voir M3-2026-04-23.md ou M5-2026-04-23.md.

2) Baseline rebaseline-base-2026-04-22 posée par direction. Manifeste md5
   logique dans docs/governance/tags/. Empreinte globale
   6a8d82bcbd292422f3ef87d0d6a30dce. Tu peux démarrer le re-baseline
   perf/UX (NPS, J30, uptime) avec cette ancre.

3) Arbitrages A1-A5 posés (docs/governance/arbitrages/2026-04-23-baseline-infra.md).
   Deux actions t'incombent :

   A3 — Générer frontend/package-lock.json (deadline 2026-04-25 EOD) :
   cd frontend
   npm install --package-lock-only --ignore-scripts
   # copier le fichier dans le workspace OneDrive
   # (direction a tenté depuis sa sandbox, timeout à 40s : arbre de deps volumineux)

   A4 — Builder pli/backend:prod (deadline 2026-04-27 EOD) :
   cd backend
   docker build --target runtime -t pli/backend:prod .
   # le Dockerfile existant est déjà multi-stage (builder + runtime)
   # tag l'image pour que M3 puisse faire : trivy image pli/backend:prod

4) Règle freeze A1 : aucun impact direct (ton travail est majoritairement
   frontend/ hors manifeste). MAIS : si ta perf/Lighthouse révèle un besoin
   de modifier backend/pli/ → ticket P0 + bump manifeste obligatoire.

5) Deadline re-baseline complète : 2026-05-14 (aligné M3).

Ping direction dès ack reçu.
```

---

## Message pour session M5

```
Arbitrages A1-A5 posés (docs/governance/arbitrages/2026-04-23-baseline-infra.md).

Réponse à ta question du daily 2026-04-23 :

A1 — freeze backend/pli/ pendant D→D+21 (2026-04-22 → 2026-05-14).
3 escape hatches cadrés :
  (1) Hotfix P0 via ticket + bump direction
  (2) Coverage M2 T2.3 #39 dead-code removal → ticket bump
  (3) Fix post-mesure M3 (vuln CRITICAL/HIGH) → ticket bump

Direction tranche chaque demande de bump en <24h. Par défaut = refus.

Action M5 : mettre à jour Sprint 11 §7 et §8 pour refléter les 3 escape
hatches et la procédure de bump (nouveau manifeste rebaseline-base-<date>.md
en cas de bump, re-notification M3+M4 obligatoire).

Ton monitoring J+10 escalade et D+21 deadline reste strictement le même.
Vigile supplémentaire demandée (cf. ton risque R2 dans ton daily) :
signaler toute PR qui touche backend/pli/ pendant la fenêtre. Si observée
sans ticket bump → ping direction immédiatement.

Autres arbitrages (A2-A5) : concernent M2 (lockfile Python, posé par direction),
M3 (accepté limite OpenAPI), M4 (à exécuter lockfile Node + image Docker).

Bonus info : M4 n'a pas posté de daily 2026-04-23 → direction le ping.
Surveille la convergence demain 2026-04-24.

Daily 2026-04-24 attendu avec ack arbitrages A1.
```

---

## Suivi dispatch

| Session | Envoyé ? | Ack daily J+1 ? | Actions closées ? |
|---------|----------|----------------|--------------------|
| M2 | ☐ | ☐ | ☐ req.lock propriétaire |
| M3 | ☐ | ☐ | ☐ pré-écriture rapport |
| M4 | ☐ | ☐ | ☐ daily + lockfile + image |
| M5 | ☐ | ☐ | ☐ Sprint 11 §7/§8 bump |

---

## Risques résiduels

- **Silence M4** : si pas de daily 2026-04-24, escalade direction (pas juste M5 monitoring).
- **Sandbox Python 3.10 dans M3** : limite connue, documentée. Pas de plan migration court-terme.
- **Docker absent dans Mail + M1 + M2 + M3** : seul M4 peut builder. Si M4 n'a pas Docker non plus → escalade humaine (JM installe Docker Desktop ou passe par une CI externe).
