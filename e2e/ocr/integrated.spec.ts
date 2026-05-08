/**
 * OCR E2E — chemin intégré (T3.3 ticket M3-rebaseline).
 *
 * Ce test ne doit tourner que contre un binaire PLI_ENABLE_M2=1 avec le
 * router OCR monté. Il vérifie :
 *
 *   1. Upload PJ PDF scanné (fixture : invoice_scanned_3pages.pdf)
 *   2. Enqueue OCR via POST /api/attachments/{id}/ocr
 *   3. Poll status → "done" sous 10 s
 *   4. GET /api/attachments/{id}/text → text non vide, lang inclut "fr"
 *   5. Recherche FTS5 avec un terme attendu du scan → retourne l'attachment
 *
 * Le point (5) est le vrai gate : c'est ce qui prouve que le worker
 * alimente bien l'index (et pas seulement la table attachment_text).
 */

import { test, expect } from "@playwright/test";
import path from "node:path";
import fs from "node:fs/promises";

const FIXTURE = path.resolve(
  __dirname,
  "../fixtures/ocr/invoice_scanned_3pages.pdf"
);

test.describe("OCR intégré @integrated", () => {
  test.skip(
    process.env.PLI_ENABLE_M2 !== "1",
    "Nécessite PLI_ENABLE_M2=1 et M2 T2.2 livré"
  );

  test("PDF scanné → extraction fra+eng → index FTS5", async ({
    request,
    page,
  }) => {
    // --- login parcours minimal (réutilise fixture auth globale)
    await page.goto("/login/test");
    await page.getByRole("button", { name: /^Continuer$/ }).click();
    await expect(page).toHaveURL(/\/conversations/);

    // --- upload PJ via API (plus stable qu'un drag-drop)
    const pdfBytes = await fs.readFile(FIXTURE);
    const upload = await request.post("/api/attachments", {
      multipart: {
        file: {
          name: "invoice_scanned_3pages.pdf",
          mimeType: "application/pdf",
          buffer: pdfBytes,
        },
      },
    });
    expect(upload.ok()).toBeTruthy();
    const { id: attachmentId } = await upload.json();

    // --- enqueue OCR
    const enqueue = await request.post(`/api/attachments/${attachmentId}/ocr`);
    expect(enqueue.status()).toBe(202);

    // --- poll status (timeout 10 s, 5 p de 2 s)
    await expect.poll(async () => {
      const r = await request.get(`/api/attachments/${attachmentId}/ocr/status`);
      return (await r.json()).state;
    }, { timeout: 10_000, intervals: [500, 1000, 2000] }).toBe("done");

    // --- récupération texte
    const text = await request
      .get(`/api/attachments/${attachmentId}/text`)
      .then((r) => r.json());
    expect(text.text.length).toBeGreaterThan(50);
    expect(text.language).toMatch(/fr/);
    expect(text.source).toBe("pdf_raster"); // scan → raster attendu
    expect(text.pages).toBe(3);

    // --- index FTS5 : on recherche un mot qu'on sait présent dans la facture
    //     (fixture contient "TVA" et "facture").
    const search = await request
      .get("/api/search?q=facture&kind=attachments")
      .then((r) => r.json());
    const found = search.hits.some((h: { id: string }) => h.id === attachmentId);
    expect(found).toBe(true);
  });
});
