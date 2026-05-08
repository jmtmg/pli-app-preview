/** US-1.7 — tests du formatteur de timestamp de ConversationRow.
 *
 * Les tests de rendu React sont reportes a Sprint 2 (setup jsdom dedie).
 * Ici on couvre la logique pure qui conditionne l'UX de la liste.
 */
import { describe, it, expect, beforeAll, afterAll, vi } from "vitest";
import { formatRelativeTime } from "./ConversationRow";

// Fige "now" pour obtenir des labels deterministes. Vendredi 22 avril 2026
// 14:30 UTC — cale sur le kickoff Sprint 1.
const NOW = new Date("2026-04-22T14:30:00Z");

beforeAll(() => {
  vi.useFakeTimers();
  vi.setSystemTime(NOW);
});

afterAll(() => {
  vi.useRealTimers();
});

describe("formatRelativeTime", () => {
  it("retourne chaine vide pour null", () => {
    expect(formatRelativeTime(null)).toBe("");
  });

  it("retourne chaine vide pour ISO invalide", () => {
    expect(formatRelativeTime("pas-une-date")).toBe("");
  });

  it("affiche l'heure pour aujourd'hui (meme date locale)", () => {
    const out = formatRelativeTime(NOW.toISOString());
    // Format fr-FR : "14:30" ou "14:30" — on verifie juste la presence d'un ":".
    expect(out).toMatch(/\d{2}:\d{2}/);
  });

  it("affiche 'Hier' pour la veille", () => {
    const yesterday = new Date(NOW.getTime() - 24 * 3600 * 1000).toISOString();
    expect(formatRelativeTime(yesterday)).toBe("Hier");
  });

  it("affiche le jour de semaine pour cette semaine (3 jours avant)", () => {
    const threeDaysAgo = new Date(NOW.getTime() - 3 * 24 * 3600 * 1000).toISOString();
    const out = formatRelativeTime(threeDaysAgo);
    // "mar." / "lun." / "dim." — 3-4 chars terminant par ".".
    expect(out.length).toBeLessThanOrEqual(5);
    expect(out).toMatch(/\./);
  });

  it("affiche jour+mois pour plus d'une semaine", () => {
    const tenDaysAgo = new Date(NOW.getTime() - 10 * 24 * 3600 * 1000).toISOString();
    const out = formatRelativeTime(tenDaysAgo);
    // "12 avr." — contient au moins un chiffre et un point.
    expect(out).toMatch(/\d+/);
    expect(out).toMatch(/\./);
  });
});
