# Rebaseline M3 / M4 — Checklist de coordination

**Origine** : arbitrage direction 2026-04-22 sur Q2 daily M3 — M3 et M4 mesurent sur le même build figé pour éviter l'écart « M3 à X, M4 à Y, non comparables ».
**Propriétaires** : session M3 (perf + vulns + OCR), session M4 (NPS + J30 + uptime).
**Orchestrateur** : direction (session Mail).

---

## Protocole

Le protocole est volontairement séquentiel. Toute étape sautée doit être rejouée depuis le début — un build "presque identique" n'est pas recevable.

### Étape 1 — Préalable M2 (sous responsabilité M2)

- [ ] M2 T2.1 fermé : `pytest --collect-only backend/tests/` → 0 erreur.
- [ ] M2 T2.2 fermé : `PLI_ENABLE_M2=1 uvicorn pli.main:app` démarre sans erreur d'import.
- [ ] `/api/billing/ping` répond 200 (preuve wire-up billing).
- [ ] ADR `docs/adr/0007-feature-flag-m2.md` committé.
- [ ] M2 notifie direction via commentaire dans `tickets/M2-unblock-auth.md`.

### Étape 2 — Fixation du build (sous responsabilité direction)

- [ ] Direction review le merge M2 sur main (règle §4 ordre de mission : pas de merge sans revue croisée).
- [ ] Direction pose la baseline logique :
  - Workspace OneDrive non git-init → substitut = manifeste md5 dans `docs/governance/tags/rebaseline-<nom>.md`.
  - Empreinte globale `md5(concat(backend_md5.txt, adr_md5.txt))` fige l'état du code (Sprint 1 + M2 wired).
  - Baseline actuelle : `rebaseline-base-2026-04-22`, empreinte `6a8d82bcbd292422f3ef87d0d6a30dce` (2026-04-22).
  - Migration tag git planifiée non-bloquante (cf. §9 du manifeste).
- [ ] Direction build l'image Docker prod depuis le code couvert par la baseline : `docker build -t pli/backend:prod -f Dockerfile.prod .`.
- [ ] Direction génère la seed DB partagée : `pg_dump | gzip > docs/governance/metrics/seed/rebaseline-YYYY-MM-DD.sql.gz`.
- [ ] Direction annonce la baseline + la seed dans un post daily explicite (pas par email direct) pour laisser une trace auditable.

### Étape 3 — Mesure M3 (perf + vulns + OCR)

- [ ] M3 vérifie la baseline md5 : `./scripts/rebaseline/check-baseline-md5.sh` (attendu 105/105 hashes + empreinte globale `6a8d82bcbd292422f3ef87d0d6a30dce`). Les runners Lighthouse et vuln-scans appellent ce check en garde-fou — ne PAS les contourner.
- [ ] M3 restaure la seed partagée dans DB locale test.
- [ ] M3 lance `PLI_ENABLE_M2=1 uvicorn pli.main:app --port 8000`.
- [ ] M3 lance `npm run build && npm run preview -- --port 5173` côté frontend.
- [ ] M3 lance `./e2e/perf/run-lighthouse-integrated.sh`.
- [ ] M3 lance `./scripts/rebaseline/run-vuln-scans.sh --image=pli/backend:prod`.
- [ ] M3 lance `PLI_ENABLE_M2=1 npx playwright test e2e/ocr/integrated.spec.ts --grep=@integrated`.
- [ ] M3 remplit les sections 3.x du rapport `docs/governance/metrics/2026-04-22-rebaseline-m3.md`.
- [ ] M3 ne signe PAS la section 5 — direction signe après relecture croisée M4.

### Étape 4 — Mesure M4 (NPS + J30 + uptime)

- [ ] M4 vérifie la même baseline md5 (contrôle : empreinte globale identique à celle de M3, `6a8d82bcbd292422f3ef87d0d6a30dce` pour la baseline courante).
- [ ] M4 restaure la même seed partagée.
- [ ] M4 lance ses mesures NPS / J30 / uptime dans son protocole (ticket `M4-rebaseline.md`).
- [ ] M4 remplit son rapport `docs/governance/metrics/2026-04-22-rebaseline-m4.md`.

### Étape 5 — Clôture croisée

- [ ] Direction lit les deux rapports M3 et M4 en parallèle.
- [ ] Direction applique les gates :
  - Sécu (0 Critical / 0 High) : non négociable.
  - Perf gradué : ≤ 10 pts = Go avec ticket tuning ; > 10 pts = bloqué.
  - OCR E2E : non négociable.
  - Métriques M4 : seuils dans son ticket propre.
- [ ] Direction signe ou bloque la décision GO M4 (section 5 des rapports).
- [ ] Direction archive manifeste baseline + rapports + SUMMARY vulns dans `docs/governance/metrics/`.
- [ ] Direction communique la décision dans le daily du jour.

---

## Règles d'or

Ne pas mesurer sur un code non taggé. La baseline logique (manifeste md5 dans `docs/governance/tags/`) garantit qu'on sait reproduire exactement le build. Les garde-fous dans `run-lighthouse-integrated.sh` et `run-vuln-scans.sh` appellent `scripts/rebaseline/check-baseline-md5.sh` qui refait le calcul local et refuse le démarrage si un seul hash diffère de la référence.

Ne pas mesurer sur seed dérivée. Si on reconstruit la seed en local au lieu de restaurer celle de direction, on introduit une variable (volume, ordre d'insertion, comptes de test) qui casse la comparabilité M3/M4.

Ne pas commenter la suspension de GO M4. Tant que l'étape 5 n'a pas tourné, le CLOSEOUT reste suspendu. Pas de slack « on est bon, c'est juste admin » — direction tranche.

En cas de doute, remonter direction via commentaire sur le ticket rebaseline concerné. Pas de décision latérale M3 ↔ M4 sans direction.
