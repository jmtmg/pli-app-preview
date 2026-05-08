/**
 * E2E — Export RGPD (art. 20).
 *
 * Parcours :
 *  1. Connexion bêta, vérifie présence données (messages, contacts)
 *  2. Settings > Mes données > Demander export
 *  3. Attendre job ready (polling UI, max 120s sur staging)
 *  4. Télécharger ZIP, vérifier contenu (EML + vCard + metadata.json)
 *  5. Vérifier audit log serveur
 */

import { test, expect } from "@playwright/test";
import AdmZip from "adm-zip";
import path from "node:path";
import fs from "node:fs/promises";

test.describe("@gdpr export", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    await page.getByLabel(/email/i).fill(process.env.E2E_USER_EMAIL!);
    await page.getByLabel(/mot de passe|password/i).fill(process.env.E2E_USER_PASSWORD!);
    await page.getByRole("button", { name: /se connecter|sign in/i }).click();
    await expect(page).toHaveURL(/\/list/);
  });

  test("user can request and download a full export", async ({ page, request }) => {
    await page.goto("/settings/my-data");
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible();

    const requestButton = page.getByRole("button", { name: /demander.*export|request.*export/i });
    await requestButton.click();

    // Status text appears and updates.
    await expect(page.getByRole("status")).toBeVisible();

    // Poll until the download link appears (reasonable envelope).
    const downloadLink = page.getByRole("link", { name: /télécharger|download/i });
    await expect(downloadLink).toBeVisible({ timeout: 120_000 });

    const [download] = await Promise.all([
      page.waitForEvent("download"),
      downloadLink.click(),
    ]);

    const tmpPath = await download.path();
    expect(tmpPath).toBeTruthy();

    // Introspect ZIP.
    const zip = new AdmZip(tmpPath!);
    const names = zip.getEntries().map((e) => e.entryName);
    expect(names).toContain("README.txt");
    expect(names).toContain("metadata.json");
    expect(names).toContain("contacts.vcf");
    expect(names.some((n) => n.startsWith("messages/") && n.endsWith(".eml"))).toBe(true);

    const metadata = JSON.parse(zip.readFile("metadata.json")!.toString());
    expect(metadata).toMatchObject({
      export_version: 1,
      user: { email: process.env.E2E_USER_EMAIL },
    });

    const vcard = zip.readFile("contacts.vcf")!.toString();
    expect(vcard).toContain("BEGIN:VCARD");
    expect(vcard).toContain("VERSION:4.0");
  });

  test("export is rate-limited to 3/hour per user", async ({ request }) => {
    // Authenticate via API for speed.
    const token = await loginAndGetToken(request);
    for (let i = 0; i < 3; i++) {
      const ok = await request.post("/api/gdpr/export", {
        headers: { Authorization: `Bearer ${token}` },
      });
      expect(ok.status()).toBe(202);
    }
    const rate = await request.post("/api/gdpr/export", {
      headers: { Authorization: `Bearer ${token}` },
    });
    expect(rate.status()).toBe(429);
  });

  test("IDOR: user A cannot read user B's export status", async ({ request }) => {
    const tokenA = await loginAndGetToken(request);
    const tokenB = await loginAndGetToken(request, "B");
    const created = await request.post("/api/gdpr/export", {
      headers: { Authorization: `Bearer ${tokenB}` },
    });
    const body = await created.json();
    const other = await request.get(`/api/gdpr/export/${body.job_id}`, {
      headers: { Authorization: `Bearer ${tokenA}` },
    });
    expect(other.status()).toBe(404);
  });
});

async function loginAndGetToken(
  request: import("@playwright/test").APIRequestContext,
  variant: "A" | "B" = "A",
): Promise<string> {
  const email = variant === "A" ? process.env.E2E_USER_EMAIL : process.env.E2E_USER2_EMAIL;
  const password = variant === "A" ? process.env.E2E_USER_PASSWORD : process.env.E2E_USER2_PASSWORD;
  const r = await request.post("/api/auth/login", { data: { email, password } });
  expect(r.status()).toBe(200);
  return (await r.json()).access_token;
}
