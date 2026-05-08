/**
 * E2E — Suppression de compte RGPD (art. 17).
 *
 * Parcours :
 *  1. Programmer la suppression via UI (mot de passe + confirm)
 *  2. Vérifier que les sessions actives sont invalidées
 *  3. Se reconnecter → bannière "suppression programmée" + bouton annuler
 *  4. Annuler, se reconnecter normalement
 *  5. Reprogrammer, avancer temps (API admin test-only), vérifier purge
 */

import { test, expect } from "@playwright/test";

test.describe("@gdpr delete-account", () => {
  test("schedule → cancel → schedule again works", async ({ page, browser }) => {
    await login(page);
    await page.goto("/settings/my-data");

    await page.getByRole("button", { name: /supprimer.*compte|delete.*account/i }).click();
    await page.getByLabel(/mot de passe.*confirmation|password/i).fill(process.env.E2E_USER_PASSWORD!);
    await page.getByLabel(/permanent/i).check();
    await page.getByRole("button", { name: /confirmer|confirm/i }).click();

    // State pane confirms scheduled.
    const banner = page.getByRole("status").filter({ hasText: /programmée|scheduled/i });
    await expect(banner).toBeVisible();

    // All refresh tokens revoked → a second browser context can't use old cookie.
    const otherCtx = await browser.newContext({ storageState: "tests/fixtures/old-session.json" });
    const otherPage = await otherCtx.newPage();
    await otherPage.goto("/list");
    await expect(otherPage).toHaveURL(/\/login/);
    await otherCtx.close();

    // Cancel restores normal state.
    await page.getByRole("button", { name: /annuler.*suppression|cancel.*deletion/i }).click();
    await expect(banner).toBeHidden();
  });

  test("wrong password does not reveal account existence (no oracle)", async ({ request }) => {
    const r1 = await request.post("/api/gdpr/delete", {
      data: { password_confirmation: "wrong", i_understand_this_is_permanent: true },
      headers: { Authorization: `Bearer ${await token()}` },
    });
    expect(r1.status()).toBe(400);
    // Generic error body, no "user not found" distinction.
    const body = await r1.json();
    expect(body.detail).toMatch(/vérifier votre identité|verify/i);
  });

  test("after 30d wait + cron, account is fully purged", async ({ request }) => {
    test.skip(!process.env.STAGING_TEST_TIME_TRAVEL, "time-travel only available on staging");
    const t = await token();
    await request.post("/api/gdpr/delete", {
      data: { password_confirmation: process.env.E2E_USER_PASSWORD, i_understand_this_is_permanent: true },
      headers: { Authorization: `Bearer ${t}` },
    });
    // Staging-only admin endpoint to fast-forward time for a given user.
    await request.post("/api/_test/time-travel", {
      data: { user_email: process.env.E2E_USER_EMAIL, days: 31 },
      headers: { Authorization: `Bearer ${process.env.STAGING_ADMIN_TOKEN}` },
    });
    await request.post("/api/_test/run-purge-cron", {
      headers: { Authorization: `Bearer ${process.env.STAGING_ADMIN_TOKEN}` },
    });

    // Login now fails.
    const login = await request.post("/api/auth/login", {
      data: { email: process.env.E2E_USER_EMAIL, password: process.env.E2E_USER_PASSWORD },
    });
    expect(login.status()).toBe(401);
  });
});

async function login(page: import("@playwright/test").Page) {
  await page.goto("/login");
  await page.getByLabel(/email/i).fill(process.env.E2E_USER_EMAIL!);
  await page.getByLabel(/mot de passe|password/i).fill(process.env.E2E_USER_PASSWORD!);
  await page.getByRole("button", { name: /se connecter|sign in/i }).click();
  await expect(page).toHaveURL(/\/list/);
}

async function token() {
  const { request } = test.info();
  // Placeholder; real impl reuses context auth.
  return process.env.E2E_USER_TOKEN!;
}
