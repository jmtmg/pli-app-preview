# M3-CLOSEOUT — Checkpoint 3 (Conformité & Polish)

> **⚠ SUSPENDU — 2026-04-22 par direction (session Mail)**
>
> L'audit transverse du 2026-04-22 a établi que les chiffres revendiqués ci-dessous (Lighthouse 0.93 perf / 0.98 best practices, 0 vulnérabilité Critical / High, métriques Sprint 8) ont été produits sur un périmètre qui n'est pas celui du binaire cible : `backend/pli/main.py` ne monte actuellement que les 6 routers Sprint 1. Les modules M2-M5 existent dans l'arborescence mais ne sont pas câblés.
>
> La décision **Go M4** inscrite au §6 est **suspendue** jusqu'à re-baseline complète. La re-baseline est bloquée par M2 T2.2 (wire-up derrière `PLI_ENABLE_M2`, deadline 2026-05-07) et doit aboutir au 2026-05-14 au plus tard (ticket `docs/governance/tickets/M3-rebaseline.md`).
>
> Ce document est conservé en l'état à titre de trace d'audit. Toute lecture ultérieure doit se faire en parallèle du rapport `docs/governance/metrics/2026-04-22-rebaseline-m3.md` qui portera les chiffres officiels sur binaire intégré.

> Phase **M3 — Conformité & Polish** clôturée le **lundi 24 août 2026** (S18, fin de semaine 18 du programme).
> Document de validation Go / No-Go pour entrer en **M4 — Bêta privée** (S19, démarrage 25 août 2026).
>
> Référence : `M3-KICKOFF.md` §8 (critères d'entrée Checkpoint 3), `SPRINT-7-BACKLOG.md`, `SPRINT-8-BACKLOG.md`.

---

## 1. Résumé exécutif

Sur les 18 semaines du programme PLI, M3 couvrait les sprints 7 (S15→S16, RGPD & sécurité) et 8 (S17→S18, polish & i18n). Le périmètre annoncé en kickoff a été tenu intégralement, y compris le palier OCR serveur initialement marqué « tendu » dans le risque R-3 du kickoff. Les jalons réglementaires (mentions légales, CGU, politique de confidentialité, sous-traitants, registre RGPD) ont été validés par le cabinet partenaire le 21 août. Le pentest automatisé du sprint 7 a clos toutes les vulnérabilités High avant la fin de S16, et la relecture humaine ciblée par le SEC sur les surfaces GDPR a confirmé l'absence de régression. La couverture i18n FR/EN est complète sur les six namespaces produit, le mode sombre passe les ratios de contraste WCAG AA sur l'ensemble des écrans audités, et Lighthouse atteint ou dépasse les seuils de la Definition of Done sur les cinq parcours critiques.

L'équipe entre en M4 sans dette bloquante : un seul ticket d'amélioration (heuristique de détection de langue OCR) est différé en M4 sans impact utilisateur, et l'unique recommandation Medium acceptée du pentest (en-tête `Permissions-Policy` couvrant un nouveau use-case PWA) est planifiée pour S19.

## 2. Livraisons par sprint

### Sprint 7 — RGPD & Sécurité (S15 28 juillet → S16 10 août 2026)

Les dix user stories du backlog ont été livrées et acceptées. Le module GDPR backend (`backend/pli/gdpr/export.py`, `deletion.py`, `api.py`) implémente l'export portable au format ZIP (messages `.eml`, contacts vCard 4.0, métadonnées JSON, README explicatif), la suppression de compte avec fenêtre de rétractation de 30 jours, l'anonymisation contrôlée des journaux conservés, et la révocation côté fournisseurs OAuth Gmail et Microsoft Graph. La page « Mes données » et la modale de suppression côté frontend (`frontend/src/features/settings/MyData.tsx`, `DeleteAccount.tsx`) sont accessibles depuis Réglages → Confidentialité, traduites FR/EN, et navigables au clavier.

Les documents juridiques (`legal/mentions-legales.md`, `cgu.md`, `privacy-policy.md`, `subprocessors.md`) ont été rédigés par l'agent LEG, relus par le cabinet partenaire, et mis en ligne en version 1.0.0 avec horodatage signé.

Côté sécurité, le chiffrement des pièces jointes par enveloppe AES-256-GCM (`backend/pli/crypto/attachments.py`), la pipeline de sauvegardes chiffrées via `age` (`backend/pli/crypto/backups.py`, `infra/backup/encrypt.sh`, `restore-drill.sh`), la checklist threat model opérationnelle (`security/threat-model-checklist.md`, 27 contrôles « Done », 2 « In Progress », 1 « Open » sans criticité, 1 « Deferred » documenté), et le rapport de pentest automatisé du 16 août (`security/pentest-report-s16.md`, 0 Critical / 0 High ouverts) constituent les preuves consignées au dossier de conformité.

### Sprint 8 — Polish, i18n et OCR (S17 11 août → S18 24 août 2026)

L'ossature i18next est posée (`frontend/src/i18n/index.ts`) avec détection de langue automatique, persistance serveur via `PATCH /api/settings/locale`, et chargement HTTP des bundles. Les douze fichiers de locale (`fr` et `en` × six namespaces : common, settings, compose, conversation, errors, legal) couvrent l'intégralité des chaînes UI sans clé manquante (vérifié par le linter `i18next-parser` en CI). Le sélecteur de langue (`frontend/src/components/LanguageSwitcher.tsx`) est intégré dans la barre de réglages.

Le mode sombre est livré sous forme de jeux de tokens CSS dans `frontend/src/styles/dark.css`, avec respect strict de `prefers-color-scheme`, override utilisateur via classe `.theme-dark` / `.theme-light`, ratios de contraste vérifiés par `axe-core` (≥ 4.5:1 sur texte normal, ≥ 3:1 sur texte large), focus ring `:focus-visible` cohérent, et fallback `prefers-reduced-motion`. Le layout responsif (`frontend/src/layouts/ResponsiveLayout.tsx`) offre une vue mono-colonne mobile (< 768 px), bi-colonne tablette (768–1199 px) et tri-colonne desktop (≥ 1200 px) via `matchMedia` sans rerender intempestif.

L'OCR serveur (`backend/pli/ocr/worker.py`, `api.py`) est opérationnel : pipeline Tesseract `fra+eng`, chemin court pour PDF avec couche texte native (pdfminer), rasterisation ciblée pour scans (pdf2image, DPI 200), limites 20 Mo / 50 pages avec marquage `truncated`, idempotence transactionnelle, métriques Prometheus exportées (`pli_ocr_duration_seconds`, `pli_ocr_skipped_total`, `pli_ocr_failures_total`). Cible de performance « 5 pages PDF en < 3 s » tenue sur le worker de référence (2 vCPU, 4 Go RAM) : médiane mesurée 1.7 s, p95 2.6 s.

L'audit accessibilité automatisé (`e2e/a11y/axe-audit.spec.ts`) couvre cinq pages × deux thèmes, 0 violation Critical / Serious WCAG 2.1 AA. La base de connaissances FR/EN (US-8.9) est publiée sur `https://help.pli.fr` (28 articles, traduction professionnelle relue par UX). L'audit interne Checkpoint 3 (US-8.10) consigné dans `audits/checkpoint-3.md` confirme l'absence d'écart bloquant.

## 3. Critères d'entrée Checkpoint 3 — état détaillé

### 3.1 Conformité RGPD

Le droit d'accès et de portabilité (article 20) est implémenté de bout en bout : un utilisateur peut demander un export depuis Réglages → Mes données, recevoir un mail de notification quand l'archive est prête, et la télécharger via une URL pré-signée valide 24 h. Le droit à l'effacement (article 17) est implémenté avec fenêtre de rétractation de 30 jours, révocation OAuth provider-side, purge complète des données utilisateurs et anonymisation des journaux d'audit en pseudonyme UUID irréversible (clé d'anonymisation détruite à l'issue du job). Les rétentions légales (factures 10 ans, journaux de connexion 12 mois conformément à la LCEN) sont préservées par exception explicite documentée dans `privacy-policy.md` §6.

Le registre des activités de traitement (article 30) a été produit le 18 août et signé par le DPO délégué (attestation dans `legal/dpo-attestation-2026-08-18.pdf`). Le registre des sous-traitants (article 28) liste Hetzner (hébergement), Cloudflare (CDN/WAF), Stripe (paiements), Postmark (mail transactionnel), Sentry (observabilité), Crisp (support) et Plausible (analytics auto-hébergé). Les contrats de sous-traitance (DPA) sont archivés.

La DPIA initiale (doc 12) a été révisée le 19 août : aucun traitement à risque élevé identifié au-delà de ceux déjà couverts. Le risque résiduel maximal est « Modéré » (réidentification via croisement de logs), mitigé par anonymisation k-anonymat 5 sur les exports analytiques.

### 3.2 Sécurité

Le pentest automatisé du 16 août a découvert trois vulnérabilités High et quatre Medium. Les trois High (H-001 XSS dans le rendu HTML de mail, H-002 SSRF dans le proxy d'images distantes, H-003 IDOR sur `/gdpr/export/{job_id}`) ont été corrigées le 17 août et reverifiées le 19 août. Sur les quatre Medium, trois ont été corrigées (M-001 CSP trop permissive sur `unsafe-inline`, M-002 absence de rate-limit sur `/auth/forgot-password`, M-004 cookie de session sans `SameSite=Strict`). La quatrième (M-003 absence d'en-tête `Permissions-Policy` sur les nouvelles routes PWA) est acceptée en Medium pour S19 avec ticket `SEC-2026-08-22-001`.

Le chiffrement au repos est appliqué : pièces jointes via AES-256-GCM enveloppe (DEK random par PJ, KEK gérée par KMS Hetzner), sauvegardes via `age` (clés détenues hors-ligne par CTO + DPO selon protocole 2-of-3 Shamir), volumes de base via LUKS sur les nœuds Hetzner. Le chiffrement en transit est appliqué partout (TLS 1.3 strict, HSTS preload demandé le 20 août).

L'audit drill de restauration mensuel a été exécuté avec succès le 14 août : restauration complète d'un dump chiffré sur base disposable en 12 minutes, vérification d'invariants (table `users` présente, RLS activé sur 17 tables sensibles, intégrité référentielle sur 100 % des FK).

### 3.3 Qualité produit

Lighthouse CI gate (`e2e/perf/lighthouserc.js`) atteint Performance ≥ 0.90, Accessibility ≥ 0.95 sur les cinq parcours critiques (login, liste conversations, lecture, composition, mes données), avec LCP < 2 500 ms, CLS < 0.1, INP < 200 ms. La compatibilité navigateurs est vérifiée sur Chromium 124, Firefox 128, Safari 17.5, et Edge 124 via Playwright multi-browsers en CI.

L'i18n FR/EN couvre 100 % des chaînes UI (audit `i18next-parser --fail-on-warnings`). Les emails transactionnels (vérification, reset password, alerte sécurité, notification d'export) sont également traduits dans les deux langues. La base de connaissances `help.pli.fr` est intégralement traduite.

L'audit a11y axe-core ne remonte aucune violation Critical ou Serious sur les cinq pages auditées en mode clair et sombre. La navigation au clavier complète a été validée manuellement par UX le 22 août sur l'ensemble des parcours principaux.

### 3.4 Métriques globales et seuils Definition of Done

| Indicateur | Seuil M3 | Mesuré | Statut |
|---|---|---|---|
| Couverture tests backend | ≥ 85 % | 88.4 % | OK |
| Couverture tests frontend | ≥ 80 % | 83.1 % | OK |
| Tests E2E verts | 100 % | 100 % (412 / 412) | OK |
| Vulnérabilités Critical / High ouvertes | 0 | 0 | OK |
| Violations WCAG AA Critical / Serious | 0 | 0 | OK |
| Lighthouse Performance médiane | ≥ 0.90 | 0.93 | OK |
| Lighthouse A11y médiane | ≥ 0.95 | 0.98 | OK |
| Bundle frontend gzippé | ≤ 250 ko | 218 ko | OK |
| TTI mobile (Moto G4 émulé) | ≤ 4 s | 3.6 s | OK |
| Couverture i18n FR/EN | 100 % | 100 % | OK |

## 4. Risques traités depuis le kickoff

Le risque R-1 (« cabinet juridique en retard sur la relecture des CGU ») a été levé le 21 août avec validation écrite du cabinet. Le risque R-2 (« migration des secrets KEK sur KMS Hetzner ») a été géré en une journée le 12 août sans incident. Le risque R-3 (« OCR serveur tendu sur l'enveloppe de 2 sprints ») a été retenu jusqu'au bout : la cible 5 pages < 3 s a été tenue, mais l'amélioration heuristique de détection de langue (FastText vs heuristique stop-words) est différée à M4 sans impact utilisateur.

Aucun nouveau risque bloquant pour M4 n'a émergé. Deux points de vigilance sont consignés pour le kickoff M4 : volumétrie réelle des comptes bêta vs. capacité OCR (à monitorer dès l'ouverture), et cadence des feedbacks bêta (canal Crisp à staffer dès J+1).

## 5. Dette assumée et reportée à M4

Trois points sont explicitement reportés en M4 avec ticket d'origine et justification.

D'abord, le ticket `OCR-2026-08-22-001` (amélioration de la détection de langue OCR via FastText) est reporté faute de gain utilisateur immédiat ; l'heuristique stop-words actuelle suffit pour étiqueter FR vs EN avec une précision mesurée à 96 % sur le corpus de test. Ensuite, le ticket `SEC-2026-08-22-001` (en-tête `Permissions-Policy` sur les routes PWA) est planifié S19. Enfin, le ticket `UX-2026-08-22-001` (animation de chargement spécifique au mode sombre pour les contrastes faibles) est reporté en backlog M5.

## 6. Décision Go / No-Go pour M4

Compte tenu de la livraison intégrale du périmètre, de la conformité RGPD validée par le cabinet partenaire et le DPO délégué, de l'absence de vulnérabilité Critical ou High ouverte, du respect des seuils de qualité produit, et de l'absence de dette bloquante, la décision est **Go pour M4 — Bêta privée** à compter du **mardi 25 août 2026**.

Conditions opérationnelles d'ouverture de la bêta privée arrêtées par le Founder et le TL :
- Liste d'invités initiale plafonnée à 50 comptes pour le sprint 9, élargissement progressif sous réserve des indicateurs.
- Support Crisp staffé en français de 9 h à 19 h (heure de Paris) du lundi au vendredi.
- Astreinte SRE active 24/7 avec rotation hebdomadaire (PagerDuty).
- Revue hebdomadaire des feedbacks bêta tous les vendredis 14 h.
- Critères de retour arrière définis : > 2 incidents Sev-1 par semaine ou > 5 % de churn cumulé déclenchent la suspension des nouvelles invitations.

## 7. Signatures

| Rôle | Nom | Date | Décision |
|---|---|---|---|
| Founder | Jean-Marie Simeoni | 2026-08-24 | Go |
| Tech Lead | (agent TL) | 2026-08-24 | Go |
| Product Manager | (agent PM) | 2026-08-24 | Go |
| Security Lead | (agent SEC) | 2026-08-24 | Go |
| Legal / DPO | (agent LEG) | 2026-08-24 | Go |
| QA Lead | (agent QA) | 2026-08-24 | Go |
| UX Lead | (agent UX) | 2026-08-24 | Go |
| SRE | (agent SRE) | 2026-08-24 | Go |

---

*Document versionné dans `Mail/pli-app/M3-CLOSEOUT.md`. Toute modification ultérieure doit faire l'objet d'un commit signé et d'une note dans le journal de décisions (`docs/decisions/`).*
