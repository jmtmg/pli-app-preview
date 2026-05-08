# Sprint 8 (S17-S18) — Polish & i18n · Backlog

**Phase** : M3 · **Durée** : 2 semaines · **Démarrage** : 11 août 2026 · **Fin** : 24 août 2026
**Objectif sprint** : Livrer un produit professionnel, accessible, international (FR+EN), performant (Lighthouse > 90), responsive, avec OCR serveur opérationnel.
**Critère de sortie** : tous les critères de Checkpoint 3 (Go/No-Go M4) validés.

---

## 1. User stories

### US-8.1 — Scaffolding i18next + extraction strings — **FE + TL**

**En tant qu'** utilisateur EN
**Je veux** que l'app supporte plusieurs langues
**Afin de** utiliser PLI dans ma langue préférée.

**Critères d'acceptance** :
- `i18next` + `react-i18next` installés, provider configuré dans `main.tsx`
- Structure `frontend/src/i18n/locales/{fr,en}/{common,settings,compose,errors}.json`
- Script d'extraction automatique (`i18next-parser`) scanne le code et génère les clés manquantes
- Hook `useT()` standard pour tous les composants
- Bascule FR ↔ EN sans reload (via state global + `i18n.changeLanguage`)
- Détection locale navigateur au premier chargement, préférence user stockée serveur-side
- Fallback FR si clé manquante
- ADR `frontend-i18n.md` : décision i18next vs format.js, structure namespaces

**Effort** : 1,5 j · **Priorité** : P0 (bloque US-8.2 et US-8.3)

---

### US-8.2 — Traduction complète UI (FR + EN) — **FE + LEG**

**En tant qu'** utilisateur
**Je veux** que 100 % des textes soient traduits
**Afin de** ne jamais voir de clé brute ou de phrase non traduite.

**Critères d'acceptance** :
- Toutes les strings app extraites dans locales/
- FR traduit à 100 % (référence)
- EN traduit à 100 % par Claude (draft) puis revue par native speaker freelance (budget 50 € prévu)
- Plurals gérés (`t('messages', {count})`)
- Variables injectées (`t('greeting', {name})`)
- Dates, nombres : formatage locale (`Intl.DateTimeFormat`, `Intl.NumberFormat`)
- Test CI : `ci/check-missing-translations.ts` échoue s'il manque une clé en EN par rapport à FR

**Effort** : 2 j · **Priorité** : P0

---

### US-8.3 — Traduction EN des legal docs + emails transactionnels — **LEG + BE**

**En tant qu'** utilisateur EN
**Je veux** accéder aux mentions, CGU, privacy policy en anglais
**Afin de** comprendre mes droits.

**Critères d'acceptance** :
- `legal/mentions-legales.en.md`, `legal/cgu.en.md`, `legal/privacy-policy.en.md`, `legal/subprocessors.en.md`
- Templates emails transactionnels (vérif, reset password, suppression confirmée, facture) en FR + EN
- Routing selon `user.locale` côté serveur
- Relue par native speaker FR→EN (cumul budget US-8.2)

**Effort** : 1 j · **Priorité** : P0

---

### US-8.4 — Accessibilité WCAG AA — **FE + UX + QA**

**En tant qu'** utilisateur en situation de handicap
**Je veux** une app utilisable au clavier et au lecteur d'écran
**Afin de** pouvoir utiliser PLI comme tout le monde.

**Critères d'acceptance** :
- Audit axe-core intégré en CI (job dédié, bloquant sur erreurs critiques)
- 0 erreur critique sur les 5 pages-clés : `/list`, `/conversation/:id`, `/compose`, `/settings/my-data`, `/login`
- Navigation clavier complète (Tab, Shift-Tab, Esc, flèches dans listes)
- Tous les `<button>` ont un libellé accessible (aria-label ou texte)
- Focus visible sur tous les éléments interactifs (outline custom respectant design tokens)
- Structure sémantique : `<main>`, `<nav>`, `<aside>`, `<h1-h6>` hiérarchie
- Alt text sur toutes les images (y compris PJ preview)
- Contrastes ≥ 4.5:1 sur texte normal, ≥ 3:1 sur texte large (testé light + dark)
- Testé avec VoiceOver (macOS) et NVDA (Windows) sur un parcours complet

**Effort** : 2 j · **Priorité** : P0

---

### US-8.5 — Optimisation performance + Lighthouse > 90 — **FE + SRE**

**En tant qu'** utilisateur
**Je veux** une app rapide qui charge vite même sur 4G lent
**Afin de** ne pas attendre pour consulter mes mails.

**Critères d'acceptance** :
- Code splitting par route (React.lazy + Suspense)
- Tree shaking vérifié (bundle analyzer), cibles : initial < 200 KB gzip, largest chunk < 100 KB
- Images : WebP/AVIF via `picture`, lazy loading attribute
- Fonts : WOFF2, `font-display: swap`, subsetting FR+EN
- Service worker avec cache strategy adaptée (cache-first assets, network-first API)
- LCP < 2.5 s sur staging en 4G simulé (Chrome DevTools throttling)
- CLS < 0.1, INP < 200 ms
- Lighthouse CI intégré, seuils bloquants : Perf ≥ 90, A11y ≥ 95, Best Practices ≥ 95, SEO ≥ 90
- Rapport `perf-report-s18.md` avant/après

**Effort** : 2 j · **Priorité** : P0

---

### US-8.6 — Mode sombre / clair peaufiné — **UX + FE**

**En tant qu'** utilisateur
**Je veux** un mode sombre agréable et respectueux de mes yeux
**Afin de** utiliser PLI le soir sans fatigue visuelle.

**Critères d'acceptance** :
- Tokens design `light` et `dark` dans `tokens.css` (cohérents avec doc 03)
- Bascule auto (prefers-color-scheme) + override user
- Tous les composants testés en light ET dark (screenshot regression via Storybook + Chromatic ou équivalent manuel)
- Contrastes vérifiés (inclus dans US-8.4)
- Transitions fluides (200 ms) sans flash de contenu

**Effort** : 1 j · **Priorité** : P0

---

### US-8.7 — Responsive tablet + desktop (split view) — **FE + UX**

**En tant qu'** utilisateur sur tablette ou desktop
**Je veux** profiter de l'espace écran (split view, 3 colonnes)
**Afin de** voir la liste et la conversation côte à côte.

**Critères d'acceptance** :
- Breakpoints : mobile < 768, tablet 768–1199, desktop ≥ 1200
- Tablet : 2 colonnes (liste + conversation), sheet contact
- Desktop : 3 colonnes (drawer comptes fixe + liste + conversation), fiche contact en drawer droit
- Navigation clavier respectée (raccourcis : `J/K` down/up, `C` compose, `/` search — doc 03)
- Tests : iPhone SE, iPhone 14, iPad, iPad Pro, 1440×900, 1920×1080, 2560×1440

**Effort** : 1,5 j · **Priorité** : P1

---

### US-8.8 — OCR serveur Tesseract (Cloud) — **BE + SRE**

**En tant qu'** utilisateur Cloud
**Je veux** que le contenu de mes PJ PDF/image soit indexé
**Afin de** pouvoir rechercher dans les factures et documents scannés.

**Critères d'acceptance** :
- Worker Celery/RQ dédié OCR (`pli.ocr.worker`)
- Pipeline : upload PJ → queue OCR async → Tesseract (FR+EN lang packs) → text → indexation FTS5/tsvector
- Bornes : PJ > 20 Mo ou PDF > 50 pages = skip (timeout + alerte log)
- Performance cible : PDF 5 pages < 3 s sur worker 2 vCPU
- Erreurs gérées gracieusement (PJ corrompue → log + skip, pas de crash)
- Mode Local : OCR désactivé par défaut (délégation desktop futur), option manuelle via button "Indexer cette PJ"
- Tests : PDF texte (vérifie OCR skip si déjà text layer), PDF image scannée, image PNG

**Effort** : 2 j · **Priorité** : P1

---

### US-8.9 — Knowledge base FR + EN (bases) — **PM + LEG**

**En tant qu'** utilisateur
**Je veux** trouver des réponses à mes questions courantes
**Afin de** ne pas avoir à contacter le support.

**Critères d'acceptance** :
- 10 articles FR + EN (post M3, cible 30+ en M4) : onboarding, OAuth Gmail, OAuth Microsoft, Local vs Cloud, pricing, RGPD, export, suppression, sécurité, FAQ
- Hébergés sur `help.pli.app` (Docusaurus, MkDocs, ou équivalent)
- Search intégrée
- Lien depuis footer + settings

**Effort** : 1 j · **Priorité** : P1

---

### US-8.10 — Audit final + validation Checkpoint 3 — **TL + Founder + QA**

**En tant que** founder
**Je veux** valider que tous les critères du Checkpoint 3 sont verts
**Afin de** signer le Go pour M4 (beta privée).

**Critères d'acceptance** :
- Checklist kickoff §8 parcourue, chaque case cochée ou justifiée
- Rapport `M3-CLOSEOUT.md` rédigé
- Démo au founder de chaque critère
- Signature Go officielle, date, commit SHA référencé

**Effort** : 0,5 j · **Priorité** : P0

---

## 2. Plan des 10 jours ouvrés

| Jour | Focus principal | Ownership |
|---|---|---|
| J1 | Kickoff sprint, scaffolding i18next (US-8.1) | FE + TL |
| J1-J2 | Extraction strings + structure locales (US-8.1, US-8.2) | FE |
| J2-J4 | Traduction FR complète + draft EN (US-8.2, US-8.3) | FE + LEG |
| J4 | Relecture EN native speaker (asynchrone, parallèle) | externe |
| J3-J5 | OCR serveur Tesseract (US-8.8) | BE + SRE |
| J4-J6 | Audit axe-core + fixes a11y (US-8.4) | FE + UX + QA |
| J5-J6 | Mode sombre peaufiné (US-8.6) | UX + FE |
| J6-J7 | Responsive tablet + desktop (US-8.7) | FE + UX |
| J7-J8 | Performance + bundle size + Lighthouse (US-8.5) | FE + SRE |
| J8 | Knowledge base v1 (US-8.9) | PM + LEG |
| J9 | Intégration finale EN (revue reçue), corrections | FE + LEG |
| J9-J10 | Audit final Checkpoint 3 + demo + closeout (US-8.10) | TL + Founder + QA |

---

## 3. Definition of Done Sprint 8

- [ ] Toutes les US P0 en `completed`, P1 ≥ 80 %
- [ ] Lighthouse CI : Perf ≥ 90, A11y ≥ 95 sur 5 pages clés
- [ ] axe-core : 0 erreur critique
- [ ] i18n : 0 clé manquante en EN, test CI vert
- [ ] Bascule FR/EN validée sans reload
- [ ] OCR PDF 5 pages < 3 s (mesuré)
- [ ] Responsive testé sur 6 viewports listés
- [ ] Mode sombre validé a11y
- [ ] Rapport `M3-CLOSEOUT.md` rédigé et signé founder
- [ ] Démo sprint + retro + feedback capturé

---

## 4. Hors scope (reporté M4 ou post-launch)

- Applications natives iOS/Android (post-launch V1.2)
- Desktop Tauri (post-launch V1.2)
- Langues additionnelles ES/DE (post-launch si traction)
- Raccourcis clavier avancés (M4 ou post-launch)
- Knowledge base 30+ articles (complété en M4)
- Chat in-app Crisp (M4)

---

*Backlog rédigé par PM en coordination avec TL, UX, LEG, à valider en sprint planning S17.*
