# Ordre de mission — Integration sprint PLI

**Date** : 2026-04-22
**Émetteur** : session Mail (direction)
**Destinataires** : sessions M1, M2, M3, M4, M5
**Statut** : actif — à effet immédiat

---

## 1. Contexte

L'audit transverse mené ce jour a mis en évidence une divergence entre les livraisons revendiquées par les sessions M2-M5 et l'état effectif du binaire :

- Seuls les routers Sprint 1 (M1) sont wired dans `pli/main.py`
- Les modules M2-M5 sont scaffoldés mais non montés
- Les suites de tests M2+ ne collectent plus (`ModuleNotFoundError: pli.auth`)
- Les métriques M3/M4 n'ont pas été mesurées sur le binaire intégré

Cette situation met en risque le Launch J0 (2026-10-07).

## 2. Décisions

| ID | Décision | Propriétaire | Deadline |
|----|----------|--------------|----------|
| D1 | Integration sprint 2-3 semaines, exécuté en convergence | direction | 2026-04-27 → 2026-05-18 |
| D2 | Résolution `ModuleNotFoundError: pli.auth` (P0) | M2 | 2026-04-30 |
| D3 | Wire-up M2 derrière flag `PLI_ENABLE_M2` | M2 | 2026-05-07 |
| D4 | Integration freeze fixé au 2026-08-26 (J0-6sem) | M5 | intégré Sprint 11 |
| D5 | Re-baseline métriques produit après D3 | M3 + M4 | 2026-05-14 |

## 3. Priorités

### P0 — Bloquant démo & suite
- M2 : déblocage `pli.auth` (cf. ticket `M2-unblock-auth.md`)

### P1 — Démo M1 + intégration
- M1 : clôture Sprint 1, OAuth Gmail réel, runthrough E2E, refresh `docs/09-API-Contract.md`
- M2 : wire-up routers derrière flag

### P2 — Re-baseline
- M3 : Lighthouse + scan vulns sur binaire intégré
- M4 : NPS / J30 / uptime sur binaire intégré

### P3 — Préparation Launch
- M5 : ajout freeze, alignement comms/oncall sur binaire intégré, Sprint 11

## 4. Règles de convergence

- **Aucun nouveau scope M3/M4** tant que D2+D3 ne sont pas fermées
- **Aucun merge M2-M5** dans `main` sans revue croisée par direction
- **Feature flags** obligatoires pour tout router non Sprint-1 tant que les tests ne collectent pas proprement
- **Logs daily** obligatoires de chaque session dans `docs/governance/daily/<session>-<date>.md`
- **Integration freeze** au 2026-08-26 : au-delà, seuls hotfix + patch de sécurité autorisés

## 5. Rôles

| Session | Rôle | Focus integration sprint |
|---------|------|--------------------------|
| Mail | Direction / pilotage | Arbitrage, sync hebdo, lecture des logs daily, revue tickets |
| M1 | Mail conversationnel | Démo propre, docs API à jour |
| M2 | Local+Cloud+Paiement | P0 auth + wire-up, ADR update si besoin |
| M3 | Bêta / OCR / sécu | Re-baseline métriques, cross-check sécu |
| M4 | KB / Tour / Onboarding | Re-baseline UX, pas de nouveau contenu |
| M5 | Launch | Freeze, comms, Sprint 11, runbook oncall |

## 6. Escalation

Tout blocage > 24h doit être remonté via un commentaire dans le ticket concerné (dossier `docs/governance/tickets/`). La direction tranche sous 24h ouvrées.

## 7. Communication vers l'extérieur

Pas de communication externe (blog, social, emails) sur le produit intégré tant que l'integration sprint n'est pas clos. M5 continue la préparation des assets mais n'envoie rien avant feu vert direction.

---

_Signé : session Mail — direction, 2026-04-22._
_Réf. audit : revue du 2026-04-22 (transcript session Mail)._
_Prochaine revue : sync hebdo lundi 2026-04-27 10h._

---

## Errata 2026-04-22 (15:30)

Correction de la direction suite au flag remonté par M1 dans son daily :

Les tickets M1-sprint1-closeout.md et M2-unblock-auth.md mentionnaient initialement "sandbox 3.10". C'était une erreur de rédaction : le code PLI cible **Python 3.11+** (dépendances, syntaxe, walrus, match-case étendu). Les tickets ont été corrigés en place.

À retenir pour toutes les sessions : **CI et dev local en 3.11+**, pas de test de compat 3.10 attendu.

---

## 8. Hygiène OneDrive — règle transverse (ajoutée 2026-04-22 soir)

**Contexte** : pendant le sprint d'intégration du 2026-04-22, M1 et M2 ont identifié un pattern systémique de troncature silencieuse de fichiers critiques sur le workspace OneDrive partagé. Au moins 3 fichiers tronqués repérés :

- `backend/tests/conftest.py` (49 / 71 lignes — fixture `client` disparue)
- `backend/pli/adapters/local.py` (191 / 227 lignes — SyntaxError au boot)
- `backend/pli/adapters/crypto/local.py` (LocalCryptoAdapter partiel)

La cause probable est le comportement asynchrone OneDrive qui commit des écrits partiels sans flush complet, aggravé par les écritures via outils natifs (Edit/Write) sur fichiers longs.

**Règle** : toute session qui écrit un fichier critique (> 100 lignes, ou dans `conftest.py`, `main.py`, `adapters/`, `security/`, `auth/`, `billing/`) doit :

1. **Préférer bash heredoc** (`cat > file << 'EOF' ... EOF`) pour les écritures complètes de fichiers > 100 lignes. Les outils Edit/Write natifs peuvent échouer silencieusement sur OneDrive.
2. **Vérifier post-write** par :
   - `wc -l <file>` cross-checké contre la longueur attendue
   - `python -m py_compile <file>` pour les fichiers Python (détecte la troncature via SyntaxError)
   - `pytest --collect-only` pour les fichiers de tests / fixtures
3. **Ne pas déclarer "DONE"** un livrable sans l'un de ces checks — la "réussite apparente" du tool call ne garantit pas l'état final sur disque.
4. **Signaler** tout cas de troncature détecté dans le daily log + éventuellement via une ligne "hygiène OneDrive" dans `docs/governance/daily/<session>-<date>.md`.

Cette règle s'applique à toutes les sessions (M1-M5 + direction) à effet immédiat. Elle sera retirée quand un mécanisme d'écriture fiable (CI git-first, montage local hors OneDrive, write-through explicite) sera en place.

**Propriétaire règle** : direction (session Mail). Révision : 2026-05-07 au plus tard.

---

## 9. Baseline `rebaseline-base-2026-04-22` — manifeste md5 logique (ajoutée 2026-04-22 soir)

**Contexte** : le workspace OneDrive `pli-app/` n'est pas un repo git (pas de `.git`). La commande `git tag -a rebaseline-base-2026-04-22` n'est donc pas exécutable depuis les sandboxes M1-M5 ni direction Mail. Pour débloquer D5 (baseline coordonnée M3/M4/M5) sans attendre l'initialisation du repo, un manifeste md5 logique est posé comme substitut fonctionnel.

**Fichier de référence** : `docs/governance/tags/rebaseline-base-2026-04-22.md` (276 lignes, 105 hashes).

**Empreinte globale** : `6a8d82bcbd292422f3ef87d0d6a30dce` (md5 de la concat des manifestes backend + ADR).

**Portée** :
- 72 fichiers `backend/pli/*.py`
- 24 fichiers `backend/tests/*.py`
- `backend/pyproject.toml` (incluant extra `[project.optional-dependencies].m2`)
- 8 ADRs (0001 à 0008)

**Empreintes pytest de référence** (critères d'acceptation absolus avant toute mesure) :
- mode (a) `PLI_ENABLE_M2` unset : 50/50 pytest, 17 paths openapi, log `pli_m2_routers_disabled`
- mode (b) `PLI_ENABLE_M2=1` : 50/50 pytest, 31 paths openapi (+14 M2), log `pli_m2_routers_enabled`

**Règle pour M3 et M4** : avant chaque campagne de mesure (sécurité, perf, UX), suivre la procédure §7 du fichier manifeste (`md5sum` + `diff`). Si un seul hash diffère OU si pytest dévie de 50/50, suspendre la mesure et ouvrir ticket `P0-rebaseline-drift-<date>`.

**Migration vers vrai tag git** : tâche différée, non-bloquante. Quand le repo sera initialisé, poser `git tag -a rebaseline-base-2026-04-22` en préservant l'empreinte `6a8d82bcbd292422f3ef87d0d6a30dce` dans le message de tag pour assurer la continuité.

**Propriétaire** : direction (session Mail). Révision : quand repo git actif.
