/**
 * E2E — Audit d'accessibilité axe-core sur 5 pages-clés.
 *
 * Cible : 0 erreur critique WCAG AA sur chaque page, light + dark.
 */

import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const PAGES = [
  { route: "/list", name: "conversation-list" },
  { route: "/conversation/sample-id", name: "conversation-view" },
  { route: "/compose", name: "composer" },
  { route: "/settings/my-data", name: "my-data" },
  { route: "/login", name: "login", authed: false },
];

const THEMES: Array<"light" | "dark"> = ["light", "dark"];

for (const p of PAGES) {
  for (const theme of THEMES) {
    test(`@a11y ${p.name} (${theme}) has 0 critical issue`, async ({ page }) => {
      if (p.authed !== false) await loginFixture(page);
      await page.emulateMedia({ colorScheme: theme });
      await page.goto(p.route);
      await page.waitForLoadState("networkidle");

      const result = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag21aa"])
        .analyze();

      const critical = result.violations.filter((v) => v.impact === "critical");
      if (critical.length) {
        for (const v of critical) {
          console.error(`[${p.name}/${theme}] ${v.id}: ${v.help}`);
          console.error(`  ${v.helpUrl}`);
          v.nodes.slice(0, 3).forEach((n) => console.error(`    ${n.html.slice(0, 120)}`));
        }
      }
      expect(critical).toEqual([]);
    });
  }
}

async function loginFixture(page: import("@playwright/test").Page) {
  await page.goto("/login");
  await page.getByLabel(/email/i).fill(process.env.E2E_USER_EMAIL!);
  await page.getByLabel(/mot de passe|password/i).fill(process.env.E2E_USER_PASSWORD!);
  await page.getByRole("button", { name: /se connecter|sign in/i }).click();
  await page.waitForURL(/\/list/);
}
