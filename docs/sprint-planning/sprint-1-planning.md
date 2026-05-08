# Sprint 1 — Note de sprint planning

**Date planning** : 22 avril 2026 (J1 M1)
**Durée sprint** : 22 avril → 6 mai 2026 (10 jours ouvrés)
**Animateurs** : PM + TL · **Présents** : BE, FE, QA, SRE, SEC, UX, Founder
**Document source** : `SPRINT-1-BACKLOG.md`
**Statut** : validé — go implémentation

---

## 1. Rappel objectif sprint

Démo vendredi 2 mai : connecter Gmail ou Outlook depuis le Drawer → sync initiale ≥ 1000 messages → liste des conversations groupée par contact, filtres Humains/Notifs actifs. DoD global : CI verte, couverture backend ≥ 70 %, zéro warning lint.

## 2. Capacité & arbitrage surcharge BE

Capacité théorique affichée au backlog :

| Rôle | Capacité (pts) | Chargé (pts) | Écart |
|---|---|---|---|
| BE  | 15 | 20 | **+33 %** |
| FE  | 10 | 5  | −50 % |
| SRE | 5  | 3  | −40 % |

**Décision PM + TL** : on confirme l'ordre de priorité qui protège la démo, pas l'exhaustivité.

- **P0 non négociable (12 pts BE)** : US-1.1 (Gmail OAuth), US-1.3 (schéma DB), US-1.4 (sync initiale Gmail), US-1.6 (endpoint `/conversations`).
- **P1 démo-critique (5 pts FE, 3 pts SRE)** : US-1.7 (liste), US-1.8 (drawer), US-1.9 (health + logs JSON), US-1.10 (CI).
- **P2 glissable** : US-1.2 (Microsoft OAuth, 3 pts BE), US-1.5 (sync initiale Graph, 5 pts BE). Si BE trop serré J6, on livre Gmail seul à la démo et on reprend Microsoft en ouverture de Sprint 2. Décision ferme au Daily de J5 (mer. 30 avril).

FE (sous-chargé) peut prendre **40 % de son temps résiduel en support** : début du squelette `ContactSheet` (Sprint 2), CSS tokens, tests E2E squelette. Arbitré par TL au daily de J4.

## 3. Ordre d'attaque (dépendances)

```
J1-J2  ─► US-1.3 (schéma DB)     │ BE, débloque tout le reste
J1-J3  ─► US-1.1 (Gmail OAuth)   │ BE, en parallèle de US-1.3
J2-J3  ─► US-1.9 (health/logs)   │ SRE, indépendant
J3-J5  ─► US-1.10 (CI)           │ SRE, sur base US-1.3 mergée
J3-J6  ─► US-1.4 (sync Gmail)    │ BE, dépend US-1.1 + US-1.3
J4-J7  ─► US-1.6 (/conversations)│ BE, dépend US-1.3 + début US-1.4
J5-J7  ─► US-1.7 (liste FE)      │ FE, dépend US-1.6 (mocks avant)
J7-J9  ─► US-1.2 (MS OAuth)      │ BE si capacité — sinon report
J7-J9  ─► US-1.8 (drawer FE)     │ FE, dépend US-1.7
J8-J9  ─► US-1.5 (sync MS)       │ BE si capacité — sinon report
J10    ─► Gel code, démo, retro
```

## 4. Arbitrages tech (TL)

| Sujet | Décision | Rationale |
|---|---|---|
| Nommage provider Gmail | Aligner sur **`gmail`** (schema.sql + `provider_name`). Renommer `google_*` → `gmail_*` dans `config.py` et côté Google Cloud Console (redirect URI `/auth/gmail/callback`). Backlog US-1.1 corrigé en conséquence. | Source de vérité = schéma DB (`CHECK provider IN ('gmail','microsoft')`). Éviter deux vocabulaires. |
| Chiffrement tokens OAuth | Fernet via `LocalCryptoAdapter` (déjà scaffoldé), clé `~/.pli/crypto.key` (0600). SQLCipher reste la couche at-rest DB. | Double couche : fichier DB chiffré + tokens chiffrés en colonne → survit à une fuite de fichier db sans clé crypto. |
| State CSRF | In-memory `_STATE_STORE` pour Sprint 1 (mode local, 1 process). ADR ouverte pour signed-cookie en M3. | Simplicité ; pas de redéploiement attendu avant fin M1. |
| ID account | `secrets.token_urlsafe(16)` en Sprint 1 (ULID vrai en M2 avec lib `python-ulid`). | Pas de dep à ajouter, conformité "TEXT PRIMARY KEY" du schéma. |
| Avatar color | Tirage aléatoire parmi palette bronze (6 variantes tokenisées côté FE). | Cohérence design system, déterministe via `hash(email)` pour stabilité. |
| Bug `/health` | `healthcheck()` est async mais pas awaité dans `main.py:61`. Ajout US incidente **US-1.9bis** (0,5 pt SRE) : awaiter + retourner `version`. | Production-grade dès J2. |

## 5. Risques confirmés + mitigations

| Risque (du backlog) | Probabilité | Impact | Mitigation activée Sprint 1 |
|---|---|---|---|
| Quota Gmail 250 u/s | moyen | fort | `asyncio.Semaphore(5)` + tenacity backoff, benchmarké US-1.4 |
| Tokens en clair si SQLCipher indispo | faible | fort | Fernet applicatif (cf. §4), WARN structlog, refus démarrage en `mode=cloud` si `cloud_crypto_key` manquant |
| RFC 822 Gmail vs Graph | moyen | moyen | DTO commun `RawMessage`, parser mutualisé `sync/parser.py` |
| Poste dev sans Python 3.11 | élevé | faible | `docker-compose up` documenté README |
| **(nouveau)** Scopes Google rejetés (OAuth Console pas validé) | moyen | fort | Demande de **consent screen internal** créée en J1 par Founder ; scopes restreints `gmail.readonly` + `gmail.send` d'abord, `gmail.modify` ajouté J4 si OK |
| **(nouveau)** Refresh token non retourné par Google si re-consent non forcé | moyen | moyen | `prompt=consent` + `access_type=offline` vérifiés en intégration, test dédié QA |

## 6. Checklist Go / No-Go démo J10 (vendredi 2 mai)

- [ ] Compte Gmail réel connecté en < 20 s depuis `/` → drawer → "+ Ajouter"
- [ ] Sync initiale ≥ 1000 messages sans crash, en < 4 min
- [ ] Liste conversations peuplée, filtres Humains/Notifs visibles et fonctionnels
- [ ] Trois comptes de démo préparés (1× Gmail perso, 1× Workspace, 1× Outlook si US-1.2 livré)
- [ ] Screencast 3 min enregistré
- [ ] Rétro tenue, 3 actions max consignées

## 7. Livrables annexes attendus en Sprint 1

- ADR-008 _State CSRF in-memory Sprint 1, migration signed-cookie M3_ — ouvert par TL J1
- Test plan QA Sprint 1 (`docs/qa/sprint-1-testplan.md`) — J3 QA
- `.env.example` à jour avec `PLI_GMAIL_CLIENT_ID`, `PLI_GMAIL_CLIENT_SECRET`, `PLI_GMAIL_REDIRECT_URI`, `PLI_MS_*` — J1 SRE
- Guide interne "Créer une app OAuth Google" (screenshots) — J1 Founder

## 8. Signatures

- **PM** : priorisation validée, P2 glissable acté
- **TL** : arbitrages tech §4 validés, ADR-008 à ouvrir J1
- **SEC** : double chiffrement tokens validé, scopes Gmail revus
- **SRE** : plan CI J3-J5 compatible capacité
- **QA** : test plan à rédiger J3
- **Founder** : Go — démarrage immédiat US-1.1 + US-1.3

---

*Note rédigée en ouverture de Sprint 1. Relecture prévue au daily J5 (30 avril) pour confirmer ou infléchir le périmètre P2.*
