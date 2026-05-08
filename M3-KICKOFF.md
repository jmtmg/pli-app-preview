# M3 — Kickoff · Conformité & Polish

**Phase** : M3 (semaines 15 → 18, 4 semaines)
**Démarrage** : 28 juillet 2026 (après validation Checkpoint 2 — M2)
**Fin cible** : 24 août 2026
**Doc de référence** : [05-Roadmap.md](../../05-Roadmap.md) §3 — Phase M3
**Documents liés** : [11-Threat-Model.md](../../11-Threat-Model.md), [12-DPIA.md](../../12-DPIA.md), [04-Cahier-des-charges.md](../../04-Cahier-des-charges.md)

---

## 1. Objectif de M3

> **Rendre PLI conforme RGPD bout-en-bout, durcir la sécurité, et livrer un produit poli (performance, accessibilité, internationalisation FR+EN) prêt à accueillir 100 bêta-testeurs en M4.**

À la fin de M3, PLI doit passer sans dette critique les trois filtres suivants :

1. **Conformité légale** : un utilisateur peut exporter ses données (portabilité), supprimer son compte (effacement), consulter ses données (accès). CNIL-ready.
2. **Sécurité** : toutes les menaces ≥ 6.0 du Threat Model (doc 11) sont mitigées et testées. Pentest automatisé passé sans finding High ouvert.
3. **Qualité produit** : Lighthouse > 90 toutes métriques, WCAG AA sans erreur critique, bascule FR/EN sans reload, responsive tablet + desktop.

C'est le **Go/No-Go du Checkpoint 3 (S18)** : sans validation de ces trois filtres, on ne démarre pas la beta privée.

---

## 2. Répartition de l'équipe d'agents

| Rôle | Agent | Périmètre M3 | Livrables clés |
|---|---|---|---|
| **Product Manager** | PM | Priorisation RGPD vs polish, arbitrage scope, acceptance | Backlog S7-S8, suivi Go/No-Go |
| **Tech Lead** | TL | Revue PR, décisions archi (i18n, OCR), standards perf | ADR i18n, ADR OCR, code owner |
| **Backend Engineer** | BE | Endpoints RGPD, chiffrement PJ, OCR server, optimisations API | `backend/pli/gdpr/**`, `crypto/**`, `ocr/**` |
| **Frontend Engineer** | FE | i18n, a11y, dark mode, responsive, optimisations bundle | `frontend/src/i18n/**`, `components/**` |
| **QA / Test Engineer** | QA | Tests RGPD end-to-end, audit a11y, tests perf, non-régression | `e2e/gdpr/**`, rapport Lighthouse + axe-core |
| **UX Designer** | UX | Audit a11y visuel, ajustements dark mode, split view desktop | Mises à jour doc 03 |
| **SRE / DevOps** | SRE | Chiffrement backups, monitoring RGPD (logs purge), CDN/cache | `infra/backup/**`, dashboards |
| **Security** | SEC | Pentest automatisé, revue chiffrement, checklist OWASP ASVS L2 | Rapport pentest, sign-off sécu |
| **Legal / DPO** | LEG | Rédaction mentions, CGU, politique conf, cohérence DPIA | `legal/mentions.md`, `cgu.md`, `privacy.md` |
| **Founder (JM)** | — | Décisions finales, signature CNIL-ready, dogfooding FR+EN | Signature Go/No-Go Checkpoint 3 |

---

## 3. Découpage Sprint (4 semaines = 2 sprints de 2 semaines)

### Sprint 7 (S15-S16) — **RGPD & Sécurité**

Livrer la conformité réglementaire et clore les vulnérabilités critiques avant polish.

- Mentions légales, CGU, politique de confidentialité (FR + EN, rédaction + intégration)
- Droit à l'effacement : endpoint + UI "Supprimer mon compte", purge programmée à 30 jours
- Droit à la portabilité : export ZIP (EML messages + vCard contacts + JSON metadata)
- Droit d'accès : page "Mes données" dans settings
- Chiffrement au repos des PJ en mode Cloud (AES-256-GCM, clé vault séparé)
- Revue du threat model (doc 11) → checklist opérationnelle, écarts documentés
- Pentest automatisé : OWASP ZAP + npm audit + pip-audit + CodeQL, triage findings
- Chiffrement des backups (pg_dump AES-256 avant upload S3-compat)

**Owner principal** : BE + LEG · **Support** : SEC (revue), SRE (backups), FE (page Mes données)
**Critère de sortie** : un utilisateur bêta peut exporter puis supprimer son compte intégralement ; 0 finding Critical/High ouvert sur le pentest automatisé ; DPO signe la conformité CNIL-ready.

### Sprint 8 (S17-S18) — **Polish & i18n**

Passer du "fonctionnel + légal" au "professionnel et accessible".

- Internationalisation FR + EN (i18next ou équivalent), switch sans reload
- Traduction exhaustive : app, emails transactionnels, pages marketing, docs support
- Optimisation bundle (code splitting, tree shaking, cibles : initial < 200 KB gzip)
- Optimisation performance : LCP < 2.5 s, CLS < 0.1, INP < 200 ms
- Accessibilité WCAG AA : audit axe-core + fixes + navigation clavier complète
- Mode sombre / clair peaufiné (contrast ratio ≥ 4.5:1 sur texte normal)
- Responsive tablet / desktop (split view 2-col tablet, 3-col desktop)
- OCR PJ : serveur (Tesseract + worker) pour Cloud, délégation desktop pour Local

**Owner principal** : FE + UX · **Support** : BE (OCR serveur, API cache), QA (audits)
**Critère de sortie** : Lighthouse > 90 partout sur pages principales, 0 erreur critique axe-core, bascule FR→EN sans reload, OCR d'un PDF de 5 pages < 3 s sur Cloud.

---

## 4. Définition du "done" M3

Une tâche est done si tous les critères sont respectés :

1. Code mergé sur `main` (PR avec 1 reviewer minimum, SEC ou LEG en plus sur touches sensibles)
2. Tests unitaires ≥ 70 % du module, integration / E2E pertinents passants
3. Documentation inline + README + docs 11/12 mis à jour si impact sécurité ou RGPD
4. Déployé sur staging, validé manuellement par QA
5. Métrique mesurée : perf (Lighthouse), a11y (axe-core), sécu (no new High), RGPD (parcours end-to-end testé)
6. Sign-off spécifique si applicable : SEC pour crypto / auth, LEG pour mentions / process RGPD

---

## 5. Dépendances externes au démarrage M3

| Dépendance | État attendu à S15 | Action si bloqué |
|---|---|---|
| Checkpoint 2 (M2) signé Go | Validé fin S14 (15 juillet) | Bloquant : pas de M3 sans M2 livré |
| Registre des sous-traitants (DPIA §1.5) | Draft publiable | LEG finalise en J1-J2 S15 |
| Clés de chiffrement vault (SOPS+age ou Doppler) | Provisionné M2 | Re-provision SRE en J1 |
| Certificats TLS staging + prod | Valides, auto-renew | SRE vérifie en J1 |
| Abscisse SAS immatriculée | En cours (DPIA §T0) | LEG gère en //, pas bloquant avant launch |
| Comptes sous-traitants (SendGrid, Sentry, Crisp, Plausible) DPAs signés | Signés en M2 | LEG relance en J1 sur les DPAs manquants |

---

## 6. Cadences et rituels

- **Daily async** (10 min, Slack/Discord) : une ligne par agent — fait hier, fait aujourd'hui, blockers
- **Review de sprint** (fin S16, S18) : démo au founder, métriques, feedback
- **Retro** (même cadence) : ce qui a bien marché, ce qui coince, actions
- **Planning sprint suivant** : enchaîné sur la retro
- **PR policy** : tout merge sur `main` passe par PR ; SEC review **obligatoire** sur `gdpr/`, `crypto/`, `auth/` ; LEG review obligatoire sur `legal/` et emails RGPD
- **Revue conformité hebdo** (30 min, LEG + founder + TL) : état des lieux mentions, DPIA, DPAs, écarts CNIL

---

## 7. Risques M3 identifiés & mitigations

| Risque | Prob. | Impact | Mitigation |
|---|---|---|---|
| Audit sécurité révèle faille majeure imprévue | Moyenne | **Critique** | Buffer 1 sem sur M3 (roadmap §4.3), scope reduction avant décalage planning |
| OCR trop lent sur mobile / bundle OCR trop lourd | Moyenne | Moyen | Fallback server-side Cloud (OK), délégation desktop Local ; accepter OCR async |
| Traductions EN approximatives (i18n) | Haute | Moyen | Pass de review par native speaker en fin S17 (50 € freelance, budget déjà prévu) |
| Tests RLS / isolation tenant échouent tardivement | Faible | **Critique** | Déjà testés M2 ; refaire suite complète en J3 S15 avant toute autre tâche |
| Règle CNIL interprétée à tort (ex: durée conservation, base légale) | Moyenne | Élevée | Relecture DPIA par DPO externe (budget LEG), sinon pause et clarification |
| Perf Lighthouse cassée par i18n (lazy loading locales mal configuré) | Moyenne | Moyen | Mesurer en continu via CI (`lighthouse-ci`), seuil bloquant merge à 85 |
| Mode sombre casse a11y (contrast insuffisant dans certains cas) | Haute | Moyen | Audit axe-core en dark mode explicitement (pas juste light), corriger au fil de l'eau |
| Retard législatif : Abscisse SAS pas immatriculée à temps pour beta | Faible | Élevé | Beta sous entité temporaire + notice, régularisation avant launch public M5 |

---

## 8. Checkpoint fin M3 (S18) — Critères Go/No-Go (Checkpoint 3)

Le founder signe le Go M4 (beta privée) si **tous** ces critères sont validés :

### Conformité RGPD
- [ ] Mentions légales, CGU, politique de conf publiées FR+EN sur pli.app
- [ ] Page "Mes données" opérationnelle (accès + téléchargement export en < 7 j)
- [ ] Suppression de compte testée end-to-end (UI → purge complète à 30 j)
- [ ] Export ZIP téléchargeable, contenu vérifié (EML + vCard + JSON), ouvrable dans Thunderbird
- [ ] Registre des sous-traitants publié sur `pli.app/subprocessors`
- [ ] DPAs signés avec tous les sous-traitants listés en DPIA §1.5
- [ ] DPO (ou LEG) signe une attestation CNIL-ready

### Sécurité
- [ ] 0 finding Critical, 0 finding High non-mitigée sur le pentest automatisé
- [ ] Toutes les menaces DREAD ≥ 6.0 (Threat Model §3) adressées et testées
- [ ] Chiffrement PJ en Cloud vérifié (dump DB seul ne permet pas lire contenu)
- [ ] Chiffrement backups vérifié (test restore mensuel en place)
- [ ] Secrets rotation testée (JWT, DB password, clé vault)
- [ ] Headers sécurité au top (CSP stricte, HSTS, X-Frame-Options, etc.) — observatory.mozilla.org grade A ou A+

### Qualité produit
- [ ] Lighthouse > 90 sur Performance / A11y / Best Practices / SEO sur 5 pages clés
- [ ] 0 erreur critique axe-core sur 5 pages clés
- [ ] Navigation clavier complète testée
- [ ] Bascule FR ↔ EN sans reload, 100 % strings traduites (pas de clé brute affichée)
- [ ] Responsive vérifié sur iPhone SE, iPhone 14, iPad, desktop 1440 / 1920
- [ ] Dark mode validé visuellement + a11y (contrasts)
- [ ] OCR serveur opérationnel : PDF 5 pages indexé < 3 s

### Global
- [ ] 0 bug bloquant ouvert
- [ ] Tests coverage ≥ 70 % sur modules critiques (gdpr, crypto, auth, i18n)
- [ ] Founder a testé en dogfooding sur son propre compte pendant ≥ 3 jours en FR puis EN

Si un critère manque : décalage de 1-2 semaines max (buffer prévu roadmap). Au-delà, revue scope avec founder pour couper du non-essentiel à la beta privée.

---

## 9. Structure du repo attendue à l'issue de M3

```
pli-app/
├── M1-KICKOFF.md
├── M3-KICKOFF.md                    ← ce document
├── SPRINT-7-BACKLOG.md              ← user stories S7 (RGPD & Sécurité)
├── SPRINT-8-BACKLOG.md              ← user stories S8 (Polish & i18n)
├── backend/
│   └── pli/
│       ├── gdpr/                    ← NOUVEAU M3
│       │   ├── export.py            ← génération ZIP EML + vCard + JSON
│       │   ├── deletion.py          ← scheduling purge 30j
│       │   └── api.py               ← endpoints /gdpr/export /gdpr/delete
│       ├── crypto/                  ← étendu M3
│       │   ├── attachments.py       ← chiffrement AES-256-GCM PJ Cloud
│       │   └── backups.py           ← pipeline chiffré pg_dump → S3
│       ├── ocr/                     ← NOUVEAU M3
│       │   ├── worker.py            ← Tesseract worker Cloud
│       │   └── api.py               ← POST /ocr
│       └── api/
│           └── gdpr.py              ← exposition endpoints GDPR
├── frontend/
│   └── src/
│       ├── i18n/                    ← NOUVEAU M3
│       │   ├── index.ts
│       │   ├── locales/
│       │   │   ├── fr.json
│       │   │   └── en.json
│       │   └── hooks.ts
│       ├── features/
│       │   └── settings/
│       │       ├── MyData.tsx       ← page RGPD "Mes données"
│       │       └── DeleteAccount.tsx
│       └── styles/
│           └── dark.css             ← mode sombre peaufiné
├── legal/                           ← NOUVEAU M3
│   ├── mentions-legales.md
│   ├── cgu.md
│   ├── privacy-policy.md
│   └── subprocessors.md
├── e2e/
│   └── gdpr/                        ← NOUVEAU M3
│       ├── export.spec.ts
│       └── delete-account.spec.ts
└── infra/
    └── backup/                      ← NOUVEAU M3
        ├── encrypt.sh
        └── restore-drill.sh
```

---

## 10. Prochaines actions immédiates (semaine 15, J1)

1. **PM** : publier `SPRINT-7-BACKLOG.md`, convoquer sprint planning S15
2. **LEG** : lancer rédaction mentions + CGU + privacy (FR en premier, EN en parallèle) ; relancer DPAs manquants
3. **SEC** : planifier pentest automatisé pour S16, préparer checklist ASVS L2
4. **BE** : scaffolder modules `gdpr/`, `crypto/attachments.py`, `crypto/backups.py`
5. **FE** : installer i18next, structurer arborescence `i18n/`, extraire strings existantes (script automatique)
6. **SRE** : vérifier vault, clés, certificats ; préparer pipeline backup chiffré
7. **QA** : rédiger plan de test RGPD end-to-end, monter suite Lighthouse-CI + axe-core dans la CI
8. **UX** : audit visuel dark mode + contrast, lister les écarts pour correction par FE en S17
9. **Founder** : valider ce kickoff, signer Go officiel M3, réserver créneau native-speaker EN pour S17

---

*Kickoff établi le 21 avril 2026 par le Tech Lead, en coordination avec PM, LEG, SEC et founder. Activation effective au démarrage S15 (28 juillet 2026), sous réserve validation Go/No-Go Checkpoint 2 (fin S14).*
