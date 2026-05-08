# Ticket M5 — Integration freeze 2026-08-26 + Sprint 11 alignement

**Priorité** : P3 (en parallèle de l'integration sprint, pas bloquant)
**Propriétaire** : session PLI M5
**Émis par** : direction (session Mail), 2026-04-22
**Deadline** : 2026-05-07 (formalisation) puis continu jusqu'à J0

---

## Contexte

Tu prépares Launch J0 = 2026-10-07 avec Sprint 11, plan comms, runbook monitoring, checklist oncall, feedback plan, sec checklist, templates closure, blog, social teasers.

Audit transverse 2026-04-22 a identifié que la convergence M1-M5 sur un binaire intégré n'est pas faite. Pour éviter un merge big-bang tardif qui ferait déraper J0, direction impose :

- **Integration freeze fixé au 2026-08-26** (J0 − 6 semaines)
- Au-delà : seuls hotfix et patches de sécurité autorisés

Ton ticket est **non bloquant** — tu continues ton plan, en ajoutant cette contrainte.

## Travail à faire

### T5.1 — Ajout freeze 2026-08-26 dans Sprint 11

- Backlog Sprint 11 mis à jour avec jalon "Integration freeze" daté 2026-08-26
- Définir en détail ce que "freeze" signifie :
  - Gel `main`
  - Branche `release-v1` cut
  - Tout nouveau PR va dans `develop` et ne sera mergé qu'après Launch
  - Exceptions : hotfix P0/P1, patch sécu CVE Critical/High
- Publier dans `docs/sprint-planning/sprint-11-planning.md` (à créer si absent)

### T5.2 — Alignement plan comms sur binaire intégré

- Blog de Launch, social teasers, emails d'annonce : tous à relire et ajuster pour refléter le périmètre réel du binaire intégré, pas la somme théorique des modules M1-M5
- **Règle stricte** : pas d'envoi externe (aucun channel) avant feu vert direction post-integration-sprint
- Drafts restent dans `docs/governance/launch/drafts/` jusqu'à validation

### T5.3 — Runbook monitoring / oncall

- Runbook existant à auditer : est-ce qu'il couvre les nouveaux endpoints M2 (billing webhook Stripe, emails transactionnels, licensing, tenancy) ?
- Compléter la checklist oncall avec pager/alerting pour ces chemins
- Tester un scénario d'incident fictif par endpoint critique (Stripe webhook down, email bounce, licence invalide)

### T5.4 — Feedback plan + sec checklist

- Vérifier que le feedback plan capture les retours sur tout le périmètre intégré (pas seulement M1)
- La sec checklist doit couvrir M2 (Stripe PCI scope délimité, gestion des tokens Fernet, signatures Ed25519 licences)

### T5.5 — Communication interne aux 5 sessions

Poster daily dans `docs/governance/daily/m5-YYYY-MM-DD.md` — en particulier :
- Risques calendaires identifiés côté Launch
- Blockers éventuels des autres sessions qui menacent J0

## Règles

- Pas de communication externe (aucun canal) sans validation direction
- Pas de merge `main` pendant le freeze (sauf hotfix)
- Si un blocker menace le freeze, escalader IMMÉDIATEMENT via le ticket

## Done criteria (formalisation T5.1+T5.2 — Deadline 2026-05-07)

- Sprint 11 intègre la date freeze
- ADR ou note interne documente la politique freeze (exceptions, critères hotfix)
- Plan comms mis en conformité avec "pas d'envoi externe avant feu vert"

## Done criteria (continu jusqu'à J0)

- Daily status posté
- Runbook + checklist oncall alignés sur binaire intégré après T2.2
- Aucun leak externe prématuré

## Journal

### 2026-04-22 — Réception ticket + formalisation T5.1 + T5.2

**Session M5** reçoit le ticket et l'ordre de mission. Lecture : `docs/governance/tickets/M5-freeze.md`, `docs/governance/2026-04-22-ordre-mission.md`, `docs/governance/2026-04-22-sync-agenda.md`, `docs/governance/tickets/M2-unblock-auth.md`.

**Compris** :

- Integration freeze 2026-08-26 est non négociable (décision D4).
- M5 continue Sprint 11 en parallèle de l'integration sprint (T5 non bloquant).
- La P0 `pli.auth` appartient à M2 (ticket `M2-unblock-auth.md`, deadline 2026-04-30), pas à M5. M5 dépend de T2.1 + T2.2 mais ne les exécute pas.
- Règle stricte : aucun envoi externe avant feu vert direction post-integration-sprint.

**Livré T5.1** (formalisation, deadline 2026-05-07) :

- `docs/sprint-planning/sprint-11-planning.md` créé — mécanique Git `main` gelé / `release-v1` cut / `develop` accueille PR nouveaux, exceptions codifiées (hotfix P0/P1, CVE Critical/High, doc fixes), responsabilités par session, risques Sprint 11, checklists Go/No-Go.
- `docs/adr/0008-integration-freeze.md` créé — ADR décisionnelle formalisant D4, exit criteria freeze, alternatives écartées, dépendances (T2.1, T2.2, D5).
- `SPRINT-11-BACKLOG.md` mis à jour — bandeau freeze + jalons amonts intégrés dans le plan des 10 jours ouvrés.

**Livré T5.2** (formalisation, deadline 2026-05-07) :

- `docs/governance/launch/drafts/` créé, avec `README.md` règles du dossier, `blog-pourquoi-pli.md` (ex `blog/`), `social-teasers.md` (ex `marketing/`), `email-beta-ouverture.md` (nouveau, bilingue FR/EN).
- Tous les chiffres durs non re-baselinés (NPS +42, rétention 58 %, conversion 24 % issus de branches M3/M4 isolées d'avant-audit) remplacés par `{placeholders}` ou annotés "à remplir après D5". Drafts portent un bandeau `🚫 NE PAS PUBLIER` en tête et une checklist pré-publication.
- `docs/governance/launch/publications-log.md` créé — journal de feu vert direction avec workflow `draft → pending → approved → scheduled → published → retracted`, process §4, escalation §5.
- Fichiers origine `blog/blog-pourquoi-pli.md` et `marketing/social-teasers.md` remplacés par des redirections pointant vers `docs/governance/launch/drafts/`.
- `M5-COMMS-PLAN.md` mis à jour — bandeau règle freeze + pointage vers `publications-log.md` pour chaque ligne publiable.

**Livré T5.3** (continu jusqu'à J0, traité aujourd'hui) :

- `M5-MONITORING-RUNBOOK.md` §13 ajoutée — playbooks M2 complémentaires :
  - §13.3 Stripe webhook backlog + signature corrompue
  - §13.4 emails transactionnels bounce / provider failover / SPF/DKIM/DMARC
  - §13.5 licence Ed25519 invalide / rotation `kid`
  - §13.6 tenancy isolation test actif (smoke 15 min)
  - §13.7 **10 scénarios d'incident fictifs D1-D10** à exécuter en staging avant ouverture Beta (obligatoires au Go Beta Publique)
- `M5-ONCALL-CHECKLIST.md` mis à jour — bloc "Endpoints M2 — audit express" dans checklist matin (3 min) + 4 seuils d'action immédiate ajoutés (emails queue, licence verify failures, tenancy smoke KO, etc.).

**Livré T5.4** (continu, traité aujourd'hui) :

- `M5-FEEDBACK-PLAN.md` §2bis — taxonomie par module (M1 Core Mail, M2-auth/billing/emails/licensing/tenancy, M3 RGPD/OCR, M4 KB/Onboarding, M5 Infra) + règle d'équilibrage anti-biais M1, tagging automatique via contexte route, tagging manuel Discord/support.
- `M5-FEEDBACK-PLAN.md` §4.2 — bumps forcés P1/P0 pour classes à risque (auth session perdue, billing double débit, licence root, tenancy cross, RGPD export, password_reset email non délivré).
- `M5-SEC-CHECKLIST.md` v1.1 — §3.8 enrichi "PCI SAQ-A délimité" (CHD/SAD out of scope, tokens `cus_*/sub_*` scopés tenant, rotation secrets) + §3.8bis emails transactionnels (SPF/DKIM/DMARC, template `password_reset` signé HMAC) + §3.8ter licences Ed25519 (HSM/KMS, rotation 30j overlap, audit no-leak) + §3.8quater tokens Fernet (rotation trimestrielle, clé locale 0600, kms cloud, CI test no-plaintext).

**Livré T5.5** :

- `docs/governance/daily/m5-2026-04-22.md` créé — récap livrables du jour, risques calendaires Launch, 5 blockers remontés aux autres sessions (P0 M2 T2.1/T2.2 en priorité), demandes à direction (validation ADR + drafts), état astreinte.

**Ce qui reste ouvert** :

- [ ] Validation direction ADR 0008 + déplacement drafts : deadline 2026-05-07 — en attente OK écrit dans `publications-log.md` colonne Commentaire.
- [ ] Dépendance dure T2.1 M2 (2026-04-30) : à monitorer quotidiennement. Si glissade > 3 jours, escalation directe.
- [ ] Dépendance T2.2 M2 (2026-05-07) : prérequis à rendre D1-D10 (runbook §13.7) exécutables en staging.
- [ ] Re-baseline M3/M4 (2026-05-14) : chiffres durs drafts comms attendent cette étape pour passer `{placeholder}` → valeur réelle.
- [ ] Rédaction `docs/runbook/post-launch-hotfix.md` (process cherry-pick `develop → release-v1`) — cible : avant 2026-08-26.
- [ ] Budgéter la fenêtre post-freeze / pré-Sprint-11 (26 août → 8 sept) pour hardening hotfix — à intégrer au budget horaire Sprint 11 `sprint-11-planning.md §3`.

**Aucune communication externe effectuée** — règle respectée.

_M5, 2026-04-22, fin de journée._

### 2026-04-22 — Retour direction + propagation validations (soir)

Direction (session Mail) renvoie validations écrites sur les livrables M5 du jour. Synthèse :

- **ADR 0008 Integration freeze 2026-08-26** : validé tel quel, signé Direction — statut ADR bumpé "Accepté — signé 2026-04-22". Deadline formalisation 2026-05-07 respectée avec 15 jours d'avance.
- **Drafts comms (blog, social, email beta)** : validés en l'état côté contenu. Règle no-send confirmée opérationnelle dès 2026-04-22. Bundle blessing loggué dans `publications-log.md §3`. **Feu vert par ligne reste obligatoire** pour chaque publication (§2 du log, statut `draft → pending → approved`).
- **Sprint 11 planning** : validé, embarque le jalon freeze. Pied de page mis à jour "OK signé 2026-04-22".
- **Runbook §13 + oncall bloc M2** : validés **sous réserve** que M3/M4 n'ajoutent pas de chemin d'alerte pendant leur re-baseline. Cas échéant : bump minor (v1.1 → v1.2) + ajout §13bis ou §14. Note versioning ajoutée en tête du §13.
- **Monitoring M2** : direction confirme que T2.1 et T2.2 **code** côté M2 sont déjà faits. Reste la conformité gouvernance (Journal M2 + daily M2 en cours de clôture). Moi : je maintiens veille quotidienne, alerte si glissade > 3j.
- **Arbitrage R1 (GO M4 conditionnel re-baseline)** : intégré dans les gates Sprint 11. §7 Go/No-Go Beta publique : ligne GO M4 activation = re-baseline D5 signée. §8 Go/No-Go Launch : ajout "re-baseline M3+M4 signée avant J0", faute de quoi Launch re-basculé en Beta privée prolongée.

**Propagations écrites** :

- `docs/adr/0008-integration-freeze.md` — statut + date validation direction + deadline formalisation "respectée".
- `docs/governance/launch/publications-log.md` — note bundle 2026-04-22 + 2 lignes historique (bundle drafts + ADR 0008).
- `docs/sprint-planning/sprint-11-planning.md` — gates §7 enrichies (bundle drafts blessing + GO M4 conditionnel + D1-D10 staging), §8 ajout prérequis re-baseline signée, pied de page validation direction.
- `M5-MONITORING-RUNBOOK.md` — note versioning §13 (v1.1, bump conditionnel M3/M4).

**Posture** : posture exemplaire saluée par direction — je continue comme c'est.

**Reste ouvert** (deux items clos côté validation direction) :

- [x] ~~Validation direction ADR 0008 + déplacement drafts~~ — **clos 2026-04-22 soir**
- [ ] Dépendance M2 : T2.1 + T2.2 code OK, gouvernance M2 en cours de clôture. Veille quotidienne maintenue, alerte si glissade > 3 jours.
- [ ] Re-baseline M3/M4 (2026-05-14) — maintenant **prérequis dur** des gates Launch §8. Suivre R1 envoyé à M3.
- [ ] Rédaction `docs/runbook/post-launch-hotfix.md` — cible : avant 2026-08-26.
- [ ] Budgéter la fenêtre post-freeze / pré-Sprint-11 (26 août → 8 sept) pour hardening hotfix.
- [ ] Surveiller toute demande M3/M4 d'ajout de chemin d'alerte pendant leur re-baseline → déclencher bump §13 v1.2.

**Aucune communication externe effectuée** — règle no-send en vigueur dès aujourd'hui.

_M5, 2026-04-22, soir — validations reçues, propagation terminée._

### 2026-04-23 — Baseline D5 posée (ancrage technique re-baseline)

Direction Mail a posé le tag logique `rebaseline-base-2026-04-22` fin de journée 2026-04-22. Vu ce matin dans `docs/governance/tags/rebaseline-base-2026-04-22.md`. OneDrive n'étant pas git-init, le tag prend la forme d'un manifeste md5 de 72 fichiers `backend/pli/`, 24 tests, pyproject et 8 ADR. Empreinte globale `6a8d82bcbd292422f3ef87d0d6a30dce`.

**Conséquences pour M5** :

- Blocker amont levé : M3 et M4 **débloqués 2026-04-22**, peuvent lancer leurs campagnes de mesure dès maintenant.
- Gate §7/§8 Sprint 11 sur **re-baseline signée** reste dur — seule la précondition technique est satisfaite.
- Deadline dépôt re-baseline M3 + M4 : **2026-05-14** (D+21).
- Seuil d'escalade drift : **2026-05-02** (J+10) si aucune des deux sessions n'a déposé.
- Runbook §13 **v1.1** reste la version de référence (direction confirme).
- ADR 0008 integration freeze **2026-08-26 non négociable**.

**Propagations 2026-04-23** :

- `docs/sprint-planning/sprint-11-planning.md` — §7 gate GO M4 annoté "baseline technique posée, M3/M4 débloqués, reste dépôt signé D+21" ; §8 prérequis "re-baseline signée" ancré à l'empreinte md5 `6a8d82bc…`, escalade J+10 citée.
- `M5-ONCALL-CHECKLIST.md` — bloc "Re-baseline M3+M4 — veille quotidienne" ajouté à checklist matin 9h ; §6 seuils d'action immédiate enrichi (daily M3/M4 ≥ 3 j sans post → ping ; baseline à J+10 sans dépôt → escalade + ouverture ticket drift).
- `docs/governance/daily/m5-2026-04-23.md` — daily du jour créé avec tableau monitoring M3/M4, question à direction sur gel éventuel `backend/pli/` pendant fenêtre re-baseline.
- Mémoire `m5_launch_governance.md` (espace session) enrichie avec empreinte baseline + seuils D+21/J+10.

**Question posée à direction** (daily 2026-04-23 §Demandes) : pendant la fenêtre D → D+21, faut-il geler `backend/pli/` pour préserver l'intégrité du manifeste md5 ? Ou autoriser un bump d'empreinte documenté ? Réponse attendue avant la première mesure M3 ou M4.

**Reste ouvert** (inchangé sauf deux updates) :

- [x] ~~Baseline technique posée~~ — **clos 2026-04-22 par direction Mail**
- [ ] Dépôt re-baseline signée M3 (2026-05-14) — veille quotidienne active.
- [ ] Dépôt re-baseline signée M4 (2026-05-14) — veille quotidienne active.
- [ ] Gouvernance M2 (journal + daily) à surveiller.
- [ ] `docs/runbook/post-launch-hotfix.md` — cible 2026-08-26.
- [ ] Budget post-freeze / pré-Sprint-11 (26 août → 8 sept).
- [ ] Réponse direction sur gel `backend/pli/` pendant fenêtre re-baseline.

**Aucune communication externe effectuée** — règle no-send respectée.

_M5, 2026-04-23 matin — baseline propagée, monitoring D+21 armé._

---

_Réf. audit 2026-04-22, ordre de mission `2026-04-22-ordre-mission.md` §2 D4 et §3 P3._
_Réf. baseline `docs/governance/tags/rebaseline-base-2026-04-22.md` (empreinte md5 `6a8d82bcbd292422f3ef87d0d6a30dce`)._
