/**
 * Lighthouse CI — seuils bloquants sur PR pour PLI.
 *
 * Exécuté dans `.github/workflows/perf.yml` sur chaque PR touchant le frontend.
 */

module.exports = {
  ci: {
    collect: {
      url: [
        "https://staging.pli.app/list",
        "https://staging.pli.app/conversation/sample-id",
        "https://staging.pli.app/compose",
        "https://staging.pli.app/settings/my-data",
        "https://staging.pli.app/login",
      ],
      numberOfRuns: 3,
      settings: {
        preset: "mobile",
        throttlingMethod: "simulate",
        onlyCategories: ["performance", "accessibility", "best-practices", "seo"],
      },
    },
    assert: {
      assertions: {
        "categories:performance": ["error", { minScore: 0.9 }],
        "categories:accessibility": ["error", { minScore: 0.95 }],
        "categories:best-practices": ["error", { minScore: 0.95 }],
        "categories:seo": ["error", { minScore: 0.9 }],
        "largest-contentful-paint": ["error", { maxNumericValue: 2500 }],
        "cumulative-layout-shift": ["error", { maxNumericValue: 0.1 }],
        "interaction-to-next-paint": ["error", { maxNumericValue: 200 }],
        "total-blocking-time": ["warn", { maxNumericValue: 300 }],
      },
    },
    upload: {
      target: "temporary-public-storage",
    },
  },
};
