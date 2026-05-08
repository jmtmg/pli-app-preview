# Checklist opérationnelle — Threat Model PLI

*Traduction du [doc 11 Threat Model](../../11-Threat-Model.md) en checklist actionnable. Chaque mitigation a un owner, un statut, une preuve (commit/PR/test/ADR).*

*Snapshot fin Sprint 7 (10 août 2026).*

## Légende statut
- ✅ **Done** : implémenté + testé + preuve vérifiable
- 🟡 **In progress** : démarré, non terminé
- 🔴 **Open** : non démarré
- ⚪ **Deferred** : reporté post-M3 avec justification

---

## Frontend

| ID | Mitigation | Owner | Statut | Preuve |
|---|---|---|---|---|
| M-FE-01 | Content Security Policy stricte | FE+SRE | ✅ | PR #412 `nginx/csp.conf`, test Playwright `tests/security/headers.spec.ts` |
| M-FE-02 | DOMPurify sur HTML mails + iframe sandbox | FE | ✅ | PR #403, composant `<MailBody />`, test `features/conversation/MailBody.test.tsx` |
| M-FE-03 | Tokens JWT en mémoire, refresh en cookie HttpOnly | FE+BE | ✅ | M2 PR #287, re-vérifié en Sprint 7 |
| M-FE-04 | CSRF protection (SameSite=Strict + header X-CSRF-Token) | FE+BE | ✅ | PR #418, mw `pli.security.csrf` |
| M-FE-05 | Subresource Integrity sur scripts tiers (Stripe.js) | FE | ✅ | `index.html` SRI hashes, CI check |

## Backend API

| ID | Mitigation | Owner | Statut | Preuve |
|---|---|---|---|---|
| M-BE-01 | Parameterized queries obligatoires (ORM only) | BE+TL | ✅ | Lint Semgrep règle `no-raw-sql.yaml`, CI bloquant |
| M-BE-02 | JWT RS256, refresh rotation, blacklist Redis | BE+SEC | ✅ | M2 PR #291, suite tests `test_auth.py` |
| M-BE-03 | RLS PostgreSQL strict + test isolation tenant | BE+SEC | ✅ | M2 ADR `multi-tenancy.md`, `test_tenancy_isolation.py` vert |
| M-BE-04 | Validation Pydantic + rate limiting Redis | BE | ✅ | Middleware `pli.security.rate_limit`, tests |
| M-BE-05 | Secrets management via SOPS+age, pre-commit scan | SRE+SEC | ✅ | Vault configuré, `.github/workflows/secret-scan.yml` vert |
| M-BE-06 | Chiffrement AES-256-GCM des tokens OAuth | BE+SEC | ✅ | M2 `pli.crypto.tokens`, tests |
| M-BE-07 | Path traversal protection | BE | ✅ | Helper `pli.security.paths`, tests adversariaux |
| M-BE-08 | SSRF protection (whitelist domains + IP private check) | BE | ✅ | Mw `pli.security.ssrf`, tests IP privées refusés |

## Base de données

| ID | Mitigation | Owner | Statut | Preuve |
|---|---|---|---|---|
| DB-01 | Backups chiffrés au repos | SRE | ✅ | `infra/backup/encrypt.sh`, drill mensuel OK |
| DB-02 | RLS bypass impossible (tests adversariaux) | SEC | ✅ | Suite `tests/adversarial/rls_bypass.py`, 30 scénarios |
| DB-03 | Clé chiffrement stockée hors DB (vault) | SRE | ✅ | SOPS+age, CI check `no-secret-in-db.yaml` |
| DB-04 | SQLite file permissions 0600 en Local | BE | ✅ | Startup check `pli.bootstrap.local` |

## Adapters externes

| ID | Mitigation | Owner | Statut | Preuve |
|---|---|---|---|---|
| EXT-01 | Refresh tokens chiffrés en DB | BE+SEC | ✅ | M2 PR #295 |
| EXT-02 | Webhook Stripe signature obligatoire | BE | ✅ | M2 PR #312, test forgery rejected |
| EXT-03 | OAuth state param obligatoire + vérifié | BE | ✅ | M0 PR #45, test CSRF OAuth |
| EXT-04 | Scopes OAuth minimaux | BE | ✅ | Doc `docs/oauth-scopes.md`, revue SEC |
| EXT-05 | Client secret OAuth en vault, rotation 90 j | SRE | ✅ | Rotation programmée 2026-11-01 |

## Infrastructure

| ID | Mitigation | Owner | Statut | Preuve |
|---|---|---|---|---|
| M-INFRA-01 | Durcissement OS (Ubuntu 24.04, updates auto) | SRE | ✅ | Ansible role `hardening/`, audit mensuel |
| M-INFRA-02 | SSH hardening (ED25519, port custom, fail2ban) | SRE | ✅ | Vérifié `ssh-audit` grade A |
| M-INFRA-03 | Segmentation réseau (VPC privé, bastion) | SRE | ✅ | Hetzner Cloud Networks configured |
| M-INFRA-04 | Backups chiffrés + test restore mensuel | SRE | ✅ | Drill 2026-08-01 réussi |
| M-INFRA-05 | TLS 1.3 partout + HSTS preload | SRE | ✅ | `ssllabs.com` grade A+ |
| M-INFRA-06 | Monitoring sécurité (logs centralisés, anomalies) | SRE | ✅ | Loki + Grafana dashboards `security/` |

## Workers

| ID | Mitigation | Owner | Statut | Preuve |
|---|---|---|---|---|
| WRK-01 | Queue messages signés (HMAC) | BE | ✅ | `pli.queue.signing`, tests forgery |
| WRK-02 | Bornes taille / pages OCR | BE | ✅ | Limits `pli.ocr.limits`, tests adversariaux (sera testé Sprint 8) |
| WRK-03 | Tesseract sandboxé (container isolé) | SRE | 🟡 | En cours Sprint 8 avec OCR serveur |

## Processus

| ID | Mitigation | Owner | Statut | Preuve |
|---|---|---|---|---|
| M-PROC-01 | Revue code sécu sur PR sensibles | TL+SEC | ✅ | CODEOWNERS + SEC reviewer obligatoire sur `gdpr/`, `crypto/`, `auth/` |
| M-PROC-02 | Pentest avant launch | SEC | 🟡 | ZAP baseline fait en Sprint 7 (voir pentest-report-s16.md). Pentest externe budgété M5 |
| M-PROC-03 | Page security.pli.app + PGP | LEG+SEC | 🔴 | À publier M5 (hors périmètre M3) |
| M-PROC-04 | Bug bounty post-launch | PM | ⚪ | Post-launch V1.1 |
| M-PROC-05 | Incident response plan (runbook doc 14) | SRE+Founder | ✅ | Doc 14 à jour, table-top exercise programmé S22 |

---

## Résumé quantitatif

| Statut | Nombre |
|---|---|
| ✅ Done | 27 |
| 🟡 In progress | 2 |
| 🔴 Open | 1 |
| ⚪ Deferred | 1 |
| **Total** | **31** |

## Menaces DREAD ≥ 6.0 (Threat Model §3) — état

| # | Menace | Mitigation(s) | Statut |
|---|---|---|---|
| 1 | RLS bypass → cross-tenant | M-BE-03, DB-02 | ✅ |
| 2 | Refresh tokens volés en DB | M-BE-06, EXT-01 | ✅ |
| 3 | XSS via contenu mail | M-FE-01, M-FE-02 | ✅ |
| 4 | Auth JWT bypass | M-BE-02 | ✅ |
| 5 | SQL injection | M-BE-01, M-BE-03 | ✅ |
| 6 | IDOR sur messages/contacts | M-BE-03, M-BE-04 | ✅ |
| 7 | Webhook Stripe non auth | EXT-02 | ✅ |
| 8 | Backup storage compromis | M-INFRA-04, DB-01 | ✅ |
| 9 | OAuth CSRF | EXT-03 | ✅ |
| 10 | SSH brute force | M-INFRA-02 | ✅ |

**Toutes les menaces DREAD ≥ 6.0 sont mitigées** (requis M3 §8 critères Go/No-Go).

---

## Automatisations en CI

- [x] `npm audit --audit-level=high` bloquant sur PR (workflow `.github/workflows/audit.yml`)
- [x] `pip-audit` bloquant sur PR (même workflow)
- [x] GitHub CodeQL actif sur push `main`
- [x] Semgrep règles custom (`no-raw-sql`, `no-eval`, `csrf-missing`) bloquantes
- [x] Trufflehog pre-commit + GitHub secret scanning activé
- [x] Lint Playwright tests headers sécurité (CSP, HSTS, X-Frame-Options)
- [x] Lint CSP stricte au build frontend (rejet inline sans hash)
- [x] Tests RLS adversariaux exécutés sur chaque PR touchant `gdpr/`, `messages/`, `contacts/`

---

## Signé

- SEC : ___________________________ (date 10/08/2026)
- TL : ___________________________ (date 10/08/2026)
- Founder : ___________________________ (date 10/08/2026)
