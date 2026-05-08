# Sprint 7 (S15-S16) — RGPD & Sécurité · Backlog

**Phase** : M3 · **Durée** : 2 semaines · **Démarrage** : 28 juillet 2026 · **Fin** : 10 août 2026
**Objectif sprint** : Livrer la conformité RGPD bout-en-bout (accès, portabilité, effacement), chiffrer les PJ Cloud et les backups, et clôturer le pentest automatisé sans finding Critical/High.
**Critère de sortie** : un utilisateur peut exporter puis supprimer son compte intégralement ; DPO signe attestation CNIL-ready ; rapport pentest publié.

---

## 1. User stories

### US-7.1 — Export RGPD (portabilité, art. 20) — **BE + FE**

**En tant qu'** utilisateur PLI
**Je veux** télécharger l'intégralité de mes données dans un format ouvert
**Afin de** exercer mon droit à la portabilité et/ou migrer vers un autre client mail.

**Critères d'acceptance** :
- `POST /gdpr/export` enqueue un job (Celery ou RQ), renvoie `{job_id, status}`
- `GET /gdpr/export/{job_id}` : statut (`pending|running|ready|expired`), URL présignée si ready (valide 24 h)
- Contenu ZIP :
  - `messages/<account>/<year>/<uuid>.eml` (un fichier EML par message, RFC 5322)
  - `contacts.vcf` (format vCard 4.0, tous contacts)
  - `metadata.json` (épinglages, filtres, paramètres, historique abo)
  - `README.txt` (explication du contenu, licence, mentions)
- Export chiffré au repos (S3 + SSE-KMS), lien présigné HTTPS-only
- SLA : < 7 j en théorie (art. 12 RGPD), en pratique < 1 h même pour boîtes 100k messages
- Traces d'audit : ligne `audit_log` (who, when, export_id)
- Tests E2E : parcours complet, contenu vérifié, ZIP ouvrable Thunderbird/Apple Mail

**Effort** : 2,5 j · **Priorité** : P0

---

### US-7.2 — Suppression de compte (effacement, art. 17) — **BE + FE**

**En tant qu'** utilisateur PLI
**Je veux** supprimer mon compte et mes données
**Afin de** exercer mon droit à l'effacement.

**Critères d'acceptance** :
- `POST /gdpr/delete` : confirmation par mot de passe + checkbox "je comprends que c'est définitif"
- Statut `scheduled_for_deletion` appliqué : user peut se reconnecter pendant 30 j pour annuler
- Après 30 j : job planifié (cron daily) purge :
  - lignes DB (`messages`, `contacts`, `attachments`, `accounts`, `sessions`, `users`)
  - objets stockage (PJ chiffrées, exports antérieurs)
  - caches Redis
  - logs techniques pseudonymisés (remplacer user_id par hash anonyme dans logs > 12 mois)
- Conservation limitée : factures (obligation comptable 10 ans), logs connexion LCEN (12 mois)
- Tokens OAuth révoqués côté provider (Gmail/Microsoft) avant purge
- Email de confirmation à J0 et J30 (purge effective)
- `DELETE /gdpr/cancel-deletion` : annulation pendant fenêtre 30 j
- Tests E2E : delete → cancel → delete final → vérif 0 ligne restante

**Effort** : 2,5 j · **Priorité** : P0

---

### US-7.3 — Page "Mes données" (accès, art. 15) — **FE + BE**

**En tant qu'** utilisateur
**Je veux** consulter depuis mes paramètres toutes les données que PLI détient sur moi
**Afin de** exercer mon droit d'accès.

**Critères d'acceptance** :
- Route `/settings/my-data`
- Sections : Identité, Comptes connectés, Volumétrie (nb messages/contacts/PJ), Historique connexions (30 derniers), Sous-traitants utilisés, Base légale par finalité
- Bouton "Télécharger export complet" (appelle US-7.1)
- Bouton "Supprimer mon compte" (appelle US-7.2, confirmation)
- Lien privacy policy + contact DPO (`dpo@pli.app`)
- A11y : structure semantic HTML, navigation clavier, lecteurs d'écran

**Effort** : 1,5 j · **Priorité** : P0

---

### US-7.4 — Mentions légales, CGU, politique de confidentialité — **LEG**

**En tant que** responsable de traitement
**Je veux** publier les documents obligatoires
**Afin de** être conforme LCEN + RGPD + droit de la consommation.

**Critères d'acceptance** :
- `legal/mentions-legales.md` (éditeur, hébergeur, contact)
- `legal/cgu.md` (CGV+CGU unifiés : objet, prix, résiliation, rétractation 14 j, responsabilité, juridiction)
- `legal/privacy-policy.md` (art. 13 RGPD : finalités, bases légales, destinataires, durées, droits, CNIL)
- `legal/subprocessors.md` (liste tenue à jour)
- Intégration dans l'app : routes `/legal/*`, liens footer + onboarding
- FR livré en S15, EN livré en S17 (Sprint 8)
- Relecture DPO externe (budget 200 € freelance RGPD) avant publication

**Effort** : 2 j (rédaction) + 0,5 j (intégration) · **Priorité** : P0

---

### US-7.5 — Chiffrement PJ au repos (Cloud) — **BE + SEC**

**En tant qu'** utilisateur Cloud
**Je veux** que mes PJ soient chiffrées au repos avec une clé que l'attaquant ne peut pas obtenir par simple dump DB
**Afin de** être protégé en cas de compromission du stockage.

**Critères d'acceptance** :
- Chiffrement AES-256-GCM par fichier, IV aléatoire 12 octets par attachment
- Clé maîtresse (KEK) dans vault (SOPS+age ou Infisical), clé de chiffrement (DEK) dérivée par attachment
- Wrapper transparent : `StorageAdapter.put()` chiffre avant upload, `.get()` déchiffre à la volée
- Rotation KEK possible (re-chiffrement background, sans downtime)
- Tests : dump S3 brut → fichier illisible ; flow complet upload→download → identique au source
- SEC signe revue : pas de clé en logs, pas de leak en erreur

**Effort** : 2 j · **Priorité** : P0

---

### US-7.6 — Pipeline backups chiffrés + test restore — **SRE**

**En tant qu'** équipe
**Nous voulons** des backups chiffrés restorables
**Afin de** résister à un scénario "backup volé" (Threat Model §5.2) et garantir la résilience.

**Critères d'acceptance** :
- Script `infra/backup/encrypt.sh` : `pg_dump | gzip | age -r <recipient>` → S3-compat
- Rotation 30 j (lifecycle policy S3)
- Script `infra/backup/restore-drill.sh` : download → décrypt → `psql` sur env éphémère → vérification cohérence
- Cron : backup quotidien 03h00 UTC ; drill mensuel automatique le 1er
- Stockage S3-compat séparé du provider DB (résilience)
- Monitoring : alerte Slack si backup échoue ou si drill échoue

**Effort** : 1,5 j · **Priorité** : P0

---

### US-7.7 — Checklist Threat Model opérationnelle — **SEC + TL**

**En tant que** Security Engineer
**Je veux** traduire le Threat Model (doc 11) en checklist actionnable contrôlée en CI
**Afin de** garantir que chaque mitigation a un propriétaire, un test, et un statut.

**Critères d'acceptance** :
- `security/threat-model-checklist.md` : une ligne par mitigation (M-FE-01 à M-PROC-05) avec `owner`, `status`, `evidence` (lien test/PR/ADR)
- Tests CI vérifient automatiquement : headers CSP, HSTS, X-Frame-Options (test Playwright)
- Dépendances auditées : `npm audit --audit-level=high` et `pip-audit` en CI bloquant
- Secret scanning : Trufflehog en pre-commit + GitHub Advanced Security
- Signé par founder à Checkpoint 3

**Effort** : 1 j · **Priorité** : P0

---

### US-7.8 — Pentest automatisé (ZAP + audit deps + CodeQL) — **SEC + QA**

**En tant que** Security Engineer
**Je veux** un pentest automatisé reproductible
**Afin de** détecter les failles basiques avant beta.

**Critères d'acceptance** :
- OWASP ZAP baseline scan sur staging (job Docker, rapport JSON+HTML)
- `npm audit` et `pip-audit` : 0 High/Critical ; Medium triés avec décision tracée
- GitHub CodeQL (ou Semgrep) activé sur repo, règles OWASP Top 10
- Rapport consolidé `security/pentest-report-s16.md` : findings, sévérité, mitigation, résiduel
- Tout finding Critical/High fixé avant fin S16
- Option : re-run ZAP après fixes pour valider

**Effort** : 1,5 j · **Priorité** : P0

---

### US-7.9 — Headers sécurité & CSP stricte — **FE + BE + SRE**

**En tant qu'** utilisateur
**Je veux** être protégé des attaques XSS, clickjacking, MITM
**Afin de** que même un contenu mail malveillant ne puisse pas voler mes données.

**Critères d'acceptance** :
- CSP stricte conforme Threat Model M-FE-01 (default-src 'self', pas d'inline script sans hash/nonce)
- HSTS avec `preload` (inclusion Chrome preload list)
- X-Frame-Options `DENY`, Referrer-Policy `strict-origin-when-cross-origin`, Permissions-Policy minimal
- SRI (Subresource Integrity) sur scripts tiers (Stripe.js)
- Rendu HTML mail dans iframe `sandbox="allow-same-origin"` + passage DOMPurify
- Test : `observatory.mozilla.org` grade A ou A+
- Test Playwright qui assert les headers sur pages clés

**Effort** : 1 j · **Priorité** : P0

---

### US-7.10 — Attestation DPO + revue DPAs — **LEG**

**En tant que** responsable de traitement
**Je veux** une attestation écrite que le traitement est CNIL-ready
**Afin de** sécuriser juridiquement le lancement beta.

**Critères d'acceptance** :
- DPO externe (ou LEG en interne si budget serré) relit DPIA (doc 12), signale écarts
- DPAs signés avec : Hetzner, Cloudflare, Stripe, SendGrid (ou Postmark), Sentry, Crisp, Plausible
- Registre sous-traitants publié sur `pli.app/subprocessors`
- Attestation signée archivée : `legal/attestation-cnil-ready-2026-08-10.pdf`

**Effort** : 0,5 j LEG + 200 € DPO externe · **Priorité** : P0

---

## 2. Plan des 10 jours ouvrés

| Jour | Focus principal | Ownership |
|---|---|---|
| J1 | Kickoff sprint, relance DPAs, scaffolding modules `gdpr/`, `crypto/`, `legal/` | Tous |
| J1-J2 | Rédaction mentions + CGU + privacy FR (US-7.4) | LEG |
| J2-J4 | Export GDPR (US-7.1) | BE + FE |
| J3-J5 | Suppression compte + cancel window (US-7.2) | BE + FE |
| J4-J5 | Chiffrement PJ AES-256-GCM (US-7.5) | BE + SEC |
| J4-J5 | Pipeline backups chiffrés + drill (US-7.6) | SRE |
| J5-J6 | Page "Mes données" (US-7.3) | FE |
| J6 | Integration CGU/mentions/privacy dans app, footer, onboarding | FE + LEG |
| J7 | Headers sécu + CSP + SRI + iframe sandbox (US-7.9) | FE + SRE |
| J8 | Checklist Threat Model opérationnelle (US-7.7) | SEC + TL |
| J8-J9 | Pentest automatisé + triage (US-7.8) | SEC + QA |
| J9 | Fixes des findings High/Critical éventuels | BE + FE selon zone |
| J9 | Attestation DPO + revue DPAs (US-7.10) | LEG |
| J10 | Review sprint, démo founder, retro, planning Sprint 8 | Tous |

---

## 3. Definition of Done Sprint 7

- [ ] Toutes les US P0 en `completed`
- [ ] Coverage ≥ 75 % sur `gdpr/`, `crypto/`, ≥ 70 % global
- [ ] Tests E2E `e2e/gdpr/export.spec.ts` et `delete-account.spec.ts` verts
- [ ] 0 finding Critical, 0 finding High ouverts sur pentest
- [ ] Grade `observatory.mozilla.org` ≥ A
- [ ] Mentions/CGU/privacy/subprocessors publiés FR (EN report S8)
- [ ] DPO attestation signée et archivée
- [ ] Drill de restore réussi sur backup chiffré
- [ ] Démo sprint au founder, feedback capturé

---

## 4. Hors scope (reporté Sprint 8 ou post-M3)

- Traductions EN complètes (Sprint 8)
- i18n switch UI (Sprint 8)
- OCR PJ serveur (Sprint 8)
- Performance / bundle size (Sprint 8)
- Responsive tablet/desktop (Sprint 8)
- 2FA (report M5 ou post-launch)
- Audit pentest externe payant (option M5, non obligatoire pour beta privée)

---

*Backlog rédigé par PM en coordination avec TL, SEC, LEG, à valider en sprint planning S15.*
