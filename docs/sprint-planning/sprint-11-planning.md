# Sprint 11 — Note de sprint planning

**Date planning** : 2026-08-27 (J+1 post freeze, à tenir)
**Durée sprint** : 9 septembre → 23 septembre 2026 (10 jours ouvrés)
**Animateurs** : PM + TL · **Présents** : BE, FE, QA, SRE, SEC, UX, CONT, MKT, Founder
**Document source backlog** : `SPRINT-11-BACKLOG.md`
**Statut** : en préparation — à valider au kickoff J1 (9 sept)
**Jalon amont non négociable** : **Integration freeze 2026-08-26** (cf. ordre de mission 2026-04-22 §2 D4 et `docs/adr/0008-integration-freeze.md`)

---

## 1. Rappel objectif sprint

Durcir le binaire intégré pour exposition publique, ouvrir progressivement l'inscription sans invitation, atteindre 500-1000 nouveaux users avec 0 incident majeur durable, valider le funnel de conversion et préparer le Launch S25 (J0 = 2026-10-07).

**Critère de sortie Sprint 11** : tous les critères Go Launch du Checkpoint 4 (`M5-KICKOFF.md §8`) validés ; dossier `closures/M5.md` signé.

---

## 2. Integration freeze — 2026-08-26

### 2.1 Définition

À partir du **mercredi 26 août 2026 à 18h00 CET**, l'intégralité du périmètre M1-M5 est figée sur une branche `release-v1` coupée depuis `main`. Cette coupe est une décision direction actée au sync 2026-04-22 (décision D4). Elle est **non négociable** hors cas prévu ci-dessous.

Le freeze porte sur le binaire intégré, pas uniquement sur les sessions M5. Toutes les sessions (M1, M2, M3, M4, M5) sont concernées.

### 2.2 Mécanique Git

```
main   ────●───●───●───●──────── (gelé 18h00 CET 26 août)
                     │
release-v1           └──●───●───●──── (cherry-pick hotfix/sec uniquement)
                        │
develop     ────────────●───●───●──── (tout PR nouveau depuis 26 août)
```

- **`main`** : gelé. Dernier commit accepté = 26 août 18h00 CET. Plus aucun merge direct jusqu'à Launch (2026-10-07).
- **`release-v1`** : branche de release, coupée depuis `main` à 18h00 CET. C'est la cible du Launch J0. Seuls les hotfix P0/P1 et patches sécu CVE Critical/High y sont mergés, par cherry-pick depuis `develop` après revue croisée direction + TL.
- **`develop`** : branche d'accueil pour tout nouveau PR à partir du 26 août 18h00 CET. Ces PR ne seront intégrés à `main` qu'**après Launch** (S26+).
- Les tags sont posés sur `release-v1` (`v1.0.0-rc.1`, `v1.0.0-rc.2`, …, `v1.0.0` à J0).

### 2.3 Exceptions autorisées

Seules les catégories suivantes peuvent cibler `release-v1` entre le 26 août et le 7 octobre :

| Catégorie | Critère | SLA merge | Approbation |
|---|---|---|---|
| **Hotfix P0** | Incident bloquant (perte de données, auth cassée, paiement impossible, fuite sécu active) | < 4 h ouvrées | Direction + TL + propriétaire module |
| **Hotfix P1** | Régression utilisateur majeure (feature critique en erreur pour > 5 % des users) | < 24 h ouvrées | Direction + TL |
| **Patch CVE Critical / High** | Vulnérabilité CVSS ≥ 7.0 dans dépendance runtime | < 48 h ouvrées | SEC + TL |
| **Correction doc / string utilisateur** | Typo, mauvaise traduction, URL cassée dans KB ou UI | Au fil de l'eau | CONT ou PM |

Toute autre modification (**nouveau scope, refacto, optimisation perf, nouvelles features, tests non-sec**) va obligatoirement dans `develop` et sera mergée après Launch. Aucune exception.

### 2.4 Gatekeeping

- La branche `main` est protégée GitHub : "Restrict pushes that create matching branches" + "Require approvals from Direction + TL + session Mail".
- La branche `release-v1` est protégée GitHub : "Require approvals from Direction + TL + SEC (si patch sécu)".
- Workflow CI dédié `release.yml` : sur `release-v1`, rejette tout PR dont le label n'est pas dans `{hotfix-p0, hotfix-p1, sec-patch, doc-fix}`.
- Dashboard "Freeze status" dans Grafana : affiche nombre de merges sur `release-v1` par jour, gros chiffre rouge si > 3.

### 2.5 Responsabilités par session pendant le freeze

| Session | Responsabilité |
|---|---|
| M1 (Mail) | Direction, arbitrage exceptions, revue de chaque PR hotfix |
| M2 (Local+Cloud+Paiement) | Disponible pour hotfix Stripe/billing/auth. Backlog M2 reprend sur `develop` après Launch. |
| M3 (Bêta/OCR/Sécu) | Patch CVE + audit dépendances hebdo (voir `M5-SEC-CHECKLIST.md`). Sécu du binaire intégré = priorité. |
| M4 (KB/Onboarding) | Correction KB/UI strings uniquement. Nouveau contenu → `develop`. |
| M5 (Launch) | Pilotage Sprint 11 + comms + oncall. Pas de code hors hotfix. |

---

## 3. Capacité & charge

La capacité Sprint 11 est calculée **hors hotfix** — on protège 25 % du temps de chaque rôle pour absorber les exceptions freeze et les incidents Beta.

| Rôle | Capacité théorique (pts) | Chargé (pts) | Écart | Tampon hotfix |
|---|---|---|---|---|
| BE  | 10 | 8 | −20 % | 25 % |
| FE  | 10 | 7 | −30 % | 25 % |
| SRE | 10 | 9 | −10 % | 25 % |
| SEC | 5  | 4 | −20 % | 25 % |
| QA  | 8  | 6 | −25 % | 25 % |
| UX  | 4  | 3 | −25 % | 25 % |
| PM  | 10 | 8 | −20 % | 25 % |
| CONT | 5 | 4 | −20 % | 25 % |
| MKT | 4  | 3 | −25 % | 25 % |
| Founder | 10 | 8 | −20 % | 25 % |

**Décision PM + TL** : priorité absolue à la stabilité (zéro P1 non résolu à J10) avant l'exhaustivité fonctionnelle. Si un choix se pose entre livrer US-11.X et absorber un hotfix, l'hotfix gagne.

---

## 4. Ordre d'attaque (dépendances)

Rappel visuel (détail dans `SPRINT-11-BACKLOG.md §5 — Dépendances inter-US`) :

```
J1  ─► US-11.10 (hardening SEC)   │ SRE+SEC, bloquant ouverture
J1  ─► US-11.7  (alerting P1/P2/P3) │ SRE, bloquant ouverture
J2  ─► US-11.1  (flag signup)     │ BE+TL, prérequis ouverture flag
J2  ─► US-11.2  (rate limits)     │ BE+SEC
J2  ─► US-11.3  (landing)         │ FE+UX+Founder
J2  ─► US-11.5  (bannière)        │ FE
J3  ─► US-11.6  (dashboards)      │ SRE
J3  ─► US-11.4  (widget feedback) │ FE+BE+PM, API côté BE J3 puis FE J4
J3  ─► US-11.9  (smoke tests)     │ QA
J4  ─► US-11.11 (status page)     │ SRE
J4  ─► US-11.12 (Discord)         │ PM+Founder
J5  ─► US-11.8  (k6 load)         │ QA+SRE — Checkpoint 11a Go/No-Go
J6  ─► ACTIVATION FLAG 08h00 CET + Blog + Teaser LinkedIn
J7  ─► Observation + hotfix
J8  ─► US-11.13 (itération #1)
J9  ─► Teaser X/Bluesky/Threads élargi
J10 ─► US-11.14 (itération #2) + US-11.15 (clôture) + Go/No-Go Launch
```

---

## 5. Arbitrages tech (TL)

| Sujet | Décision | Rationale |
|---|---|---|
| Config `public_signup_enabled` | Table `feature_flags`, lecture in-memory cache TTL 30 s, invalidation par SSE | Bascule on/off < 30 s sans redeploy, survit kill switch |
| Rate limits storage | Redis (cluster managé), token bucket Lua atomique | Évite course condition, cohérent multi-instance FastAPI |
| Widget feedback payload | `{ context: string, rating: int|null, comment: string|null, contact_ok: bool }`, limite 4 ko | Taille raisonnable, compatible NPS 0-10 + thumbs |
| Landing i18n | FR + EN uniquement. ES/DE reporté V1.2 (cf. `SPRINT-11-BACKLOG.md §4`) | Focus |
| Status page | Hébergée sur `status.pli.app` (Vercel ou Better Stack Status) | Sort du périmètre app : ne tombe pas avec l'app |
| Discord public | Canal `#pli-beta`, modération par rotation CONT + Founder | Règle `/tos` épinglée |
| Bannière beta in-app | CSS variable, **pas de feature flag** — suit l'env (`dev`, `staging`, `prod-beta`, `prod-launch`) | Erreur humaine éliminée |

---

## 6. Risques Sprint 11 + mitigations

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| Hotfix P0 consomme > 25 % de la capacité | moyen | fort | Tampon déjà réservé. Si dépassement, on décroche les US P2 (identifiées dans le backlog). |
| Stripe webhook down pendant ramp-up | faible | fort | Chaos test J5 (voir `M5-MONITORING-RUNBOOK.md §6.1`). Fallback : file de retry + page "Paiement bientôt rétabli". |
| Pic charge inattendu (article presse viral) | faible | moyen | k6 validé à 3× capacity. Auto-scale Cloudflare + pool DB `pgbouncer`. Kill switch flag signup en 30 s. |
| Feedback volume > capacité traitement (widget + Discord) | moyen | moyen | Rôle CONT dédié triage J7-J10. Issues top 5 → itération #1 / #2. |
| CVE Critical publié sur dépendance FastAPI/Stripe/React | faible | fort | Hebdo `pip-audit` + `npm audit` dans CI. Patch process documenté §2.3. |
| Désynchro communication : blog publié avant feu vert direction | faible | fort | Tous les drafts dans `docs/governance/launch/drafts/`. Aucune publication automatisée. Checklist CONT §7.2 de `M5-COMMS-PLAN.md`. |
| Incident sur `main` découvert après freeze | moyen | variable | Processus hotfix §2.3. Cherry-pick vers `release-v1`, pas de remerge vers `main`. |
| Oubli de cherry-pick → `release-v1` diverge de `main` sur un correctif | moyen | moyen | CI rappelle au merge sur `develop` "Cet hotfix doit-il être cherry-pick vers `release-v1` ?" (GitHub Action label-based). |

---

## 7. Checklist Go / No-Go Beta publique (J6 — mer 16 sept 08h00 CET)

- [ ] US-11.1 à US-11.12 en `completed`
- [ ] k6 load test validé 3× capacity avec p95 latence < 800 ms
- [ ] Smoke tests synthétiques verts depuis 48 h
- [ ] Alerting P1/P2/P3 testé en chaos, pages reçues < 2 min
- [ ] Status page live, affiche "Opérationnel"
- [ ] WAF + Turnstile + honeypot actifs
- [ ] Dashboards Grafana M5 peuplés avec données staging
- [ ] Discord public ouvert, ToS épinglés, modération CONT + Founder en rotation
- [ ] Blog draft + 3 posts LinkedIn + thread X/Bluesky/Threads validés direction (drafts dans `docs/governance/launch/drafts/`) — **bundle contenu signé 2026-04-22, feu vert par ligne toujours requis dans `publications-log.md`**
- [ ] Kill switch flag signup testé off → on → off en staging
- [ ] PagerDuty Founder opérationnel, PIN fonctionnel
- [ ] **GO M4 prononcé** — périmètre KB/Onboarding activé uniquement si re-baseline M3/M4 sur binaire intégré signée (D5, deadline 2026-05-14). Arbitrage direction 2026-04-22 (R1 envoyé à M3). Si re-baseline non livrée → périmètre M4 reste désactivé et gates §8 Launch sont resserrés en conséquence.
  - **État 2026-04-22 soir** : baseline technique `rebaseline-base-2026-04-22` posée (manifeste md5, empreinte globale `6a8d82bcbd292422f3ef87d0d6a30dce`, cf. `docs/governance/tags/rebaseline-base-2026-04-22.md`). M3 et M4 **débloqués** — ils peuvent lancer leurs campagnes de mesure dès maintenant. Le blocker amont est levé. Il reste le dépôt signé des re-baselines par M3 et M4 eux-mêmes d'ici **2026-05-14** (D+21).
- [ ] Scénarios D1-D10 (`M5-MONITORING-RUNBOOK.md §13.7`) tous exécutés en staging, statut vert sur les 10

---

## 8. Checklist Go / No-Go Launch (J10 — mar 22 sept)

Validée au stand-up Launch (cf. `M5-KICKOFF.md §8` Checkpoint 4 — 11 points) + `M5-CLOSURE-TEMPLATE.md`.

Prérequis durs pour Launch :

- [ ] ≥ 500 inscriptions publiques en Beta sur 7 jours
- [ ] NPS ≥ +30 (échantillon ≥ 30 réponses)
- [ ] Uptime ≥ 99.9 % sur la fenêtre Beta
- [ ] 0 P1 ouvert, < 5 P2 ouverts
- [ ] 2 itérations feedback déployées avec changelog public
- [ ] Rapport clôture `closures/M5.md` signé Direction + TL + SEC + Founder
- [ ] **Re-baseline M3 + M4 sur binaire intégré signée** avant J0 (prérequis issu de R1 2026-04-22). Sans re-baseline signée : Launch re-basculé en `Beta privée prolongée` et gate Launch refusé.
  - **Ancrage** : baseline technique `rebaseline-base-2026-04-22` (empreinte md5 `6a8d82bcbd292422f3ef87d0d6a30dce`). Fenêtre de re-baseline M3+M4 : 2026-04-22 → 2026-05-14 (D+21). Escalade direction si drift à J+10 (2026-05-02) sans poste de re-baseline par M3 ou M4.

---

## 9. Livrables annexes attendus en Sprint 11

- `closures/M5.md` (rapport clôture) — cible J10
- `docs/governance/launch/publications-log.md` (log des envois externes effectifs, post feu vert) — live à partir de J6
- `CHANGELOG.md` release notes `v1.0.0-rc.1` à `v1.0.0`
- `docs/runbook/post-launch-hotfix.md` — processus cherry-pick `develop` → `release-v1` formalisé à J+2 post freeze

---

_Rédigé par session M5 — 2026-04-22 (formalisation T5.1 du ticket `M5-freeze.md`)._
_**Validation direction : OK signé 2026-04-22** (circuit court, J-15 sur deadline 2026-05-07). Embarque jalon freeze non négociable + gate M4 conditionnel re-baseline D5._
