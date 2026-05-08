# ADR 0008 — Integration freeze 2026-08-26 (J0 − 6 semaines)

- **Statut** : Accepté — **signé Direction (session Mail) le 2026-04-22, validation écrite telle quelle, sans amendement**
- **Date proposition** : 2026-04-22
- **Date validation Direction** : 2026-04-22 (même jour, circuit court)
- **Décideur** : Direction (session Mail)
- **Propriétaires mise en œuvre** : TL (gatekeeping Git), session M5 (intégration Sprint 11 et comms), SEC (exception CVE)
- **Émis par** : session M5 pour formaliser la décision D4 de l'ordre de mission `2026-04-22-ordre-mission.md`
- **Deadline formalisation respectée** : 2026-05-07 (signé J-15)

---

## Contexte

L'audit transverse mené le 2026-04-22 a révélé que les modules M2-M5 sont scaffoldés mais ne sont pas wired dans `pli/main.py`. Les suites de tests M2+ ne collectent plus (`ModuleNotFoundError: pli.auth`). Les métriques revendiquées par M3/M4 n'ont pas été mesurées sur un binaire intégré. La convergence du binaire n'est pas faite.

Sans discipline de freeze, le risque est un merge big-bang tardif qui explose le Launch J0 (2026-10-07) : la somme des modules M1-M5 livrés à la dernière minute produit immanquablement des régressions non triagées, des dépendances tardives, et un Beta publique instable.

La direction a décidé, au sync 2026-04-22 (décision D4), d'imposer un **integration freeze au 2026-08-26**, soit J0 − 6 semaines. Cette ADR formalise la politique : portée, mécanique Git, exceptions, gatekeeping, exit criteria.

## Décision

### 1. Date et portée

- **Date effective freeze** : **mercredi 26 août 2026 à 18h00 CET**.
- **Fin du freeze** : Launch J0 = mercredi 7 octobre 2026.
- Portée : l'intégralité du monorepo `pli-app` — backend, frontend, docs techniques d'API, scripts CI, infrastructure as code, migrations DB. Seule la KB contenu FR/EN (`docs/kb/`) et les traductions UI sont hors portée pour les corrections de typo/lien.

### 2. Mécanique Git

Au moment du freeze, la branche `release-v1` est coupée depuis `main`. À partir de cet instant :

- **`main`** : gelé. Aucun push direct, aucun merge PR jusqu'à Launch. Protection GitHub `Require approvals from Direction + TL + session Mail` ET `Restrict who can push`.
- **`release-v1`** : branche de release. Cible exclusive du Launch J0. Merges limités aux exceptions §3. Tags `v1.0.0-rc.N` au fil des hotfix, `v1.0.0` posé le 2026-10-07 à J0-1 (testé staging) puis promu à J0.
- **`develop`** : accueille tout nouveau PR à partir du freeze. Sera re-mergée vers `main` après Launch (S26).

```
main       ────●───●───●───●─────────── (gel 26 août 18h00 CET)
                         │
release-v1               └──●─●─●──●─●── (cherry-pick exceptions uniquement)
                            │
develop    ─────────────────●─●─●──●──── (tout PR post-freeze)
```

### 3. Exceptions autorisées

Seules les catégories suivantes peuvent merger sur `release-v1` :

| Catégorie | Critère | SLA merge | Approbation requise |
|---|---|---|---|
| **Hotfix P0** | Incident bloquant (data loss, auth down, paiement impossible, fuite sécu active) | < 4 h ouvrées | Direction + TL + owner module |
| **Hotfix P1** | Régression user majeure (feature critique en erreur pour > 5 % users) | < 24 h ouvrées | Direction + TL |
| **Patch CVE Critical/High** | Vulnérabilité CVSS ≥ 7.0 dans dépendance runtime | < 48 h ouvrées | SEC + TL |
| **Correction doc/string user** | Typo, mauvaise traduction, URL cassée dans KB ou UI | Au fil de l'eau | CONT ou PM |

**Règles d'application** :

1. Tout correctif P0/P1/CVE est d'abord développé et mergé sur `develop`, puis **cherry-pick** vers `release-v1`. Pas de branche de hotfix directement sur `release-v1` (évite la divergence durable).
2. Chaque cherry-pick vers `release-v1` est tagué immédiatement après merge (`v1.0.0-rc.N+1`).
3. Un post-Launch merge `release-v1` → `main` est prévu pour S26 afin de réintégrer toute l'historique propre.

### 4. Hors périmètre (aller systématiquement sur `develop`, pas sur `release-v1`)

- Nouveau scope fonctionnel (features, pages, endpoints)
- Refacto ou dette technique (même "1 ligne")
- Optimisation performance (hors hotfix P1 établi)
- Nouvelle dépendance (sauf patch sécu intégré à une dép existante)
- Nouveau test ou suite de tests (hors test couvrant le hotfix lui-même)
- Ajout de télémétrie, logs additionnels (sauf instrumentation directe nécessaire à un hotfix)

### 5. Gatekeeping (automatisation)

- **GitHub branch protection** sur `main` : push bloqué, merge bloqué, statut `Direction + TL + Mail approve`.
- **GitHub branch protection** sur `release-v1` : merge nécessite label dans `{hotfix-p0, hotfix-p1, sec-patch, doc-fix}` + approval matrix par catégorie.
- **CI workflow `release.yml`** : rejette tout PR sur `release-v1` sans label d'exception.
- **CI workflow `post-freeze-reminder.yml`** : sur tout merge vers `develop` à partir du 26 août, commentaire auto "Cet hotfix doit-il être cherry-pick vers `release-v1` ? Si oui, ouvrir PR label hotfix-pX."
- **Dashboard Grafana "Freeze status"** : nombre de merges `release-v1` / jour. Alerte Slack si > 3/jour (possible dérive).

### 6. Communication externe

Pas d'envoi externe (blog, social, emails massifs) sur le produit intégré avant feu vert direction post-Sprint-11 Checkpoint 4. Tous les drafts sont stockés dans `docs/governance/launch/drafts/` (T5.2 du ticket `M5-freeze.md`) et ne sont publiés qu'à partir du jour de bascule de `public_signup_enabled` (Sprint 11 J6 = 2026-09-16) sur décision direction.

### 7. Exit criteria freeze

La branche `release-v1` passe en `v1.0.0` stable (et le freeze se termine par un Launch réussi) quand :

- Tous les critères Go Launch du Checkpoint 4 M5 sont verts (cf. `M5-KICKOFF.md §8`)
- Zéro P1 ouvert, < 5 P2 ouverts sur `release-v1`
- Uptime ≥ 99.9 % sur Beta publique (16 → 22 sept)
- NPS ≥ +30 sur échantillon ≥ 30 réponses
- Rapport clôture `closures/M5.md` signé Direction + TL + SEC + Founder

## Conséquences

### Positives

- Le binaire de Launch ne reçoit plus de nouveau scope à 6 semaines de J0 → chaque jour du freeze est consacré à fiabiliser.
- L'equipe de session M5 peut préparer Sprint 11 sur une cible stable : plus de mouvement imprévu des fondations.
- Les exceptions sont codifiées et auditables : toute PR sur `release-v1` porte un label qui explique sa raison d'être.
- Le risque de merge big-bang J0-1 est éliminé.

### Négatives

- Nouvelle feature discutée après le 26 août attend **minimum 11 semaines** (freeze 6 sem + Launch + stabilisation S26-S27) avant mise en prod.
- Double maintenance : tout bugfix doit exister sur `develop` ET être cherry-pick vers `release-v1`. Oublis possibles → mitigation via GitHub Action.
- Si un bug majeur est découvert côté M2-M5 après le freeze, il doit absolument remonter P0/P1 ou attendre Launch. Risque de pression sur la grille de priorité.

### Neutres

- La branche `develop` devient naturellement la cible des refactos post-Launch → avantage pour l'organisation V1.1, mais demande un catch-up `main` propre en S26.

## Alternatives écartées

- **Pas de freeze, trust le sprint** : rejeté. L'audit 2026-04-22 a montré qu'on ne peut pas trust un merge tardif de 4 sessions parallèles.
- **Freeze à J0-4 semaines (2026-09-09)** : rejeté. 4 semaines est insuffisant pour stabiliser + exposer la Beta + corriger 2 itérations sur feedback. L'équipe M5 a besoin du Sprint 11 complet sur binaire fixe.
- **Freeze par session (chacun gèle sa session à son rythme)** : rejeté. Impossible de mesurer uptime / NPS / vulns sur un binaire intégré si la base bouge sous les pieds.

## Dépendances

- Dépend de la résolution de l'incident `pli.auth` P0 par M2 (deadline 2026-04-30, cf. `docs/governance/tickets/M2-unblock-auth.md`). Sans T2.1 résolu, le binaire ne collecte pas ses tests → freeze sans sens.
- Dépend du wire-up M2 derrière `PLI_ENABLE_M2` (deadline 2026-05-07, D3). Sans ça, le binaire intégré ne démarre pas.
- Dépend de la re-baseline métriques M3/M4 (deadline 2026-05-14, D5) pour garantir que les chiffres du Checkpoint 4 M5 sont mesurés sur le binaire intégré.

## Références

- `docs/governance/2026-04-22-ordre-mission.md` — décision D4
- `docs/governance/2026-04-22-sync-agenda.md` — §D4 décision formulée au sync
- `docs/governance/tickets/M5-freeze.md` — ticket émetteur de cette ADR (T5.1)
- `docs/sprint-planning/sprint-11-planning.md` — note planning qui opérationnalise cette ADR
- `M5-KICKOFF.md` §8 — Checkpoints M5 et critères Go Launch
- `SPRINT-11-BACKLOG.md` — backlog qui s'exécute sur `release-v1`

---

_Rédigé par session M5, 2026-04-22._
_Validation direction attendue avant 2026-05-07._
