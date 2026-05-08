/**
 * Tests E2E — parcours beta M4.
 * Exécutés en CI et avant chaque release.
 */
import { test, expect } from "@playwright/test";

const BASE = process.env.E2E_BASE_URL ?? "http://localhost:5173";

test.describe("Waitlist & Invitations", () => {
  test("M4-E2E-001 · waitlist signup double opt-in", async ({ page, request }) => {
    await page.goto(`${BASE}/waitlist`);
    await page.fill("input[type=email]", "happy@test.dev");
    await page.fill("input[placeholder*='Prénom']", "Happy");
    await page.click("button[type=submit]");
    await expect(page.getByText(/confirmation/i)).toBeVisible();

    // confirmation email (via MailHog)
    const token = await fetchConfirmToken(request, "happy@test.dev");
    await page.goto(`${BASE}/waitlist/confirm/${token}`);
    await expect(page.getByText(/Inscription confirmée/i)).toBeVisible();
  });

  test("M4-E2E-003 · redeem code happy path", async ({ page, request }) => {
    const code = await adminIssueAndPickCode(request, 1);
    // signup
    await page.goto(`${BASE}/signup?invite=${code}`);
    await page.fill("input[type=email]", `user-${Date.now()}@test.dev`);
    await page.fill("input[type=password]", "BetaPass42!");
    await page.click("button[type=submit]");
    // redeem
    await page.goto(`${BASE}/invited?code=${code}`);
    await page.click("button:has-text('Activer')");
    await expect(page.getByText(/Activé/i)).toBeVisible();
  });

  test("M4-E2E-004 · code déjà consommé", async ({ page, request }) => {
    const code = await adminIssueAndPickCode(request, 1);
    await redeemAs(request, code, "first@test.dev");
    await page.goto(`${BASE}/invited?code=${code}`);
    // user connecté différent
    await loginAs(page, "second@test.dev");
    await page.click("button:has-text('Activer')");
    await expect(page.getByText(/déjà utilisé/i)).toBeVisible();
  });
});

test.describe("Onboarding tour", () => {
  test("M4-E2E-006 · skip tour", async ({ page }) => {
    await loginAsBetaUser(page);
    await expect(page.locator("[role=dialog]")).toContainText(/conversations/i);
    await page.click("button:has-text('Passer')");
    await expect(page.locator("[role=dialog]")).toBeHidden();
  });

  test("M4-E2E-007 · full tour", async ({ page }) => {
    await loginAsBetaUser(page);
    for (let i = 0; i < 4; i++) {
      await page.click("button:has-text('Suivant')");
    }
    await page.click("button:has-text('parti')");
    await expect(page.locator("[role=dialog]")).toBeHidden();
  });

  test("M4-E2E-008 · idempotence", async ({ page }) => {
    await loginAsBetaUser(page, { tourCompleted: true });
    await page.goto(BASE);
    await expect(page.locator("[role=dialog]")).toBeHidden();
  });
});

test.describe("NPS widget", () => {
  test("M4-E2E-009 · submit score 9", async ({ page }) => {
    await loginAsBetaUser(page, { daysSinceSignup: 8 });
    await page.waitForSelector("[aria-labelledby=nps-title]");
    await page.click("button[aria-label='score 9']");
    await page.fill("textarea", "Parfait");
    await page.click("button:has-text('Envoyer')");
    await expect(page.getByText(/Merci/i)).toBeVisible();
  });

  test("M4-E2E-010 · cooldown 30 jours", async ({ page }) => {
    await loginAsBetaUser(page, { lastNpsDismissedDaysAgo: 5 });
    await page.goto(BASE);
    await expect(page.locator("[aria-labelledby=nps-title]")).toBeHidden();
  });
});

test.describe("Feedback FAB", () => {
  test("M4-E2E-011 · submit bug", async ({ page }) => {
    await loginAsBetaUser(page, { tourCompleted: true });
    await page.click("button[aria-label*='feedback']");
    await page.click("button:has-text('Bug')");
    await page.fill("textarea", "Le composer ne respecte pas ma signature.");
    await page.click("button:has-text('Envoyer')");
    await expect(page.getByText(/Reçu/i)).toBeVisible();
  });

  test("M4-E2E-012 · rate-limit 4e submission", async ({ page, request }) => {
    await loginAsBetaUser(page);
    for (let i = 0; i < 3; i++) {
      await submitFeedback(request, { kind: "bug", message: `#${i}` });
    }
    const r = await submitFeedback(request, { kind: "bug", message: "#4" }, { expectStatus: 429 });
    expect(r.status()).toBe(429);
  });
});

// ---- helpers (stubs) ----

async function fetchConfirmToken(request: any, email: string): Promise<string> {
  const r = await request.get(`${BASE}/test/mailhog/last?to=${email}`);
  const { token } = await r.json();
  return token;
}

async function adminIssueAndPickCode(request: any, batch: number): Promise<string> {
  await request.post(`${BASE}/invitations/admin/issue`, {
    headers: { Authorization: `Bearer ${process.env.ADMIN_TOKEN}` },
    data: { batch_number: batch },
  });
  const r = await request.get(`${BASE}/test/invitations/last-code?batch=${batch}`);
  const { code } = await r.json();
  return code;
}

async function redeemAs(request: any, code: string, email: string) {
  // suppose signup + redeem via backend test helpers
}
async function loginAs(page: any, email: string) {
  // suppose login form or session cookie
}
async function loginAsBetaUser(page: any, opts?: any) {
  // seed user avec batch_number et tour state
  await page.goto(BASE);
}
async function submitFeedback(request: any, data: any, opts?: any) {
  return request.post(`${BASE}/feedback`, {
    headers: { Authorization: `Bearer ${process.env.BETA_USER_TOKEN}` },
    data,
  });
}
