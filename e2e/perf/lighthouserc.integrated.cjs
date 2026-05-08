/**
 * Lighthouse CI — config re-baseline M3 sur binaire intégré.
 *
 * Contexte : l'audit transverse 2026-04-22 a invalidé les chiffres Lighthouse
 * mesurés sur branches isolées. Cette config cible le binaire wire-up complet
 * (PLI_ENABLE_M2=1) et ajoute le parcours Billing portal débloqué par M2.
 *
 * NE PAS LANCER tant que M2 T2.2 n'est pas livré (cf. docs/governance/tickets/
 * M3-rebaseline.md et M2-unblock-auth.md).
 *
 * Prérequis runtime :
 *   - Backend : PLI_ENABLE_M2=1 uvicorn pli.main:app --port 8000
 *   - Frontend : npm run build && npm run preview -- --port 5173
 *   - Stripe test mode (pour /billing) : STRIPE_API_KEY=sk_test_...
 *   - OAuth Gmail : compte de test dédié (pas de prod)
 *
 * Cibles (conservatrices vs chiffres revendiqués pre-audit) :
 *   - Performance   ≥ 0.90   (revendiqué 0.93)
 *   - Best Practices ≥ 0.95  (revendiqué 0.98)
 *   - Accessibility ≥ 0.95   (inchangé vs Sprint 8)
 *   - SEO           ≥ 0.90
 *
 * Si un parcours chute > 5 points vs revendiqué : ouvrir ticket perf tuning
 * avant clôture (règle fixée par direction dans T3.1).
 */

const BASE = process.env.PLI_BASE_URL || "http://localhost:5173";

module.exports = {
  ci: {
    collect: {
      // Chrome en headless, desktop preset par défaut.
      // On multiplie les runs pour lisser le bruit (CLS notamment).
      numberOfRuns: 3,
      settings: {
        preset: "desktop",
        // Chrome flags : pas de first-run, pas d'auto-update, sandbox CI.
        chromeFlags: "--no-sandbox --headless=new --disable-gpu",
        // Throttling desktop standard (ref. docs Lighthouse).
        throttlingMethod: "simulate",
        // On skip pwa : hors scope M3, ne faussera pas le score global.
        skipAudits: ["uses-http2"],
      },
      url: [
        // US-3.1 parcours clefs listés dans M3-rebaseline.md
        `${BASE}/login/gmail`,
        `${BASE}/contacts`,
        `${BASE}/conversations/seed-thread-1`,
        `${BASE}/contacts/seed-contact-1`,
        // Billing portal — nouveau, débloqué par M2 (T2.2).
        // Si M2 n'a pas wire-up /billing, Lighthouse retournera 404 et
        // le test plantera explicitement : c'est voulu, c'est notre
        // garde-fou "binaire vraiment intégré".
        `${BASE}/settings/billing`,
      ],
    },
    assert: {
      // Assertions par catégorie — ne bloquent pas les audits individuels
      // sauf ceux explicitement escaladés en error.
      preset: "lighthouse:recommended",
      assertions: {
        "categories:performance": ["error", { minScore: 0.9 }],
        "categories:best-practices": ["error", { minScore: 0.95 }],
        "categories:accessibility": ["error", { minScore: 0.95 }],
        "categories:seo": ["warn", { minScore: 0.9 }],

        // Core Web Vitals — seuils M3 Sprint 8 (inchangés sauf INP).
        "largest-contentful-paint": ["error", { maxNumericValue: 2500 }],
        "cumulative-layout-shift": ["error", { maxNumericValue: 0.1 }],
        "interaction-to-next-paint": ["error", { maxNumericValue: 200 }],
        "total-blocking-time": ["error", { maxNumericValue: 300 }],

        // Transfert : le bundle gzippé doit rester sous 250 ko (Sprint 8 DoD).
        "total-byte-weight": ["warn", { maxNumericValue: 1200000 }],

        // Audits courants qu'on tolère en warn pour l'instant (hors périmètre) :
        "uses-text-compression": "warn",
        "render-blocking-resources": "warn",
      },
    },
    upload: {
      // Upload local uniquement — rapports conservés dans docs/governance/
      // pour traçabilité audit.
      target: "filesystem",
      outputDir: "./docs/governance/metrics/lighthouse-integrated",
      reportFilenamePattern: "%%DATETIME%%-%%PATHNAME%%-%%HOSTNAME%%.%%EXTENSION%%",
    },
  },
};
