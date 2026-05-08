import { describe, expect, it } from "vitest";
import {
  buildSearchPath,
  canRunSearch,
  countSearchResults,
  getSearchResultContactId,
  hasSearchResults,
  normalizeSearchQuery,
  type SearchResponse,
} from "./searchModel";

const RESULTS: SearchResponse = {
  contacts: [
    { id: "contact-1", email: "alice@example.com", display_name: "Alice", company: "JMJ" },
  ],
  messages: [
    {
      id: "msg-1",
      subject: "MVP local",
      snippet: "Validation de la recherche",
      received_at: 1778270000,
      contact_id: "contact-2",
      display_name: "Bob",
      email: "bob@example.com",
    },
  ],
  attachments: [
    {
      id: "att-1",
      filename: "brief.pdf",
      mime_type: "application/pdf",
      contact_id: "contact-3",
      display_name: "Claire",
    },
  ],
};

describe("searchModel", () => {
  it("normalise les espaces sans retirer la ponctuation utile", () => {
    expect(normalizeSearchQuery("  test.pli   demo  ")).toBe("test.pli demo");
  });

  it("ne lance la recherche qu'à partir de deux caractères", () => {
    expect(canRunSearch("a")).toBe(false);
    expect(canRunSearch("  a  ")).toBe(false);
    expect(canRunSearch("jm")).toBe(true);
  });

  it("construit une URL de recherche limitée au compte actif", () => {
    expect(buildSearchPath("test.pli", "demo-account-gmail")).toBe(
      "/search?q=test.pli&account_id=demo-account-gmail",
    );
    expect(buildSearchPath("Alice Martin", "demo-account-gmail")).toBe(
      "/search?q=Alice+Martin&account_id=demo-account-gmail",
    );
  });

  it("compte les résultats groupés", () => {
    expect(countSearchResults(RESULTS)).toBe(3);
    expect(hasSearchResults(RESULTS)).toBe(true);
    expect(hasSearchResults({ contacts: [], messages: [], attachments: [] })).toBe(false);
  });

  it("résout le contact à ouvrir selon le type de résultat", () => {
    expect(getSearchResultContactId("contact", RESULTS.contacts[0])).toBe("contact-1");
    expect(getSearchResultContactId("message", RESULTS.messages[0])).toBe("contact-2");
    expect(getSearchResultContactId("attachment", RESULTS.attachments[0])).toBe("contact-3");
  });
});
