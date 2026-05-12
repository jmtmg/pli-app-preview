import { describe, expect, it } from "vitest";
import type { Message } from "@/api/queries";
import {
  buildDraftPayload,
  buildReplyCcState,
  buildSignedBody,
  canSendComposer,
  getComposerInstanceKey,
  getDefaultReplySubject,
  getReplyCcCandidates,
  isCurrentDraftGeneration,
  shouldSaveDraft,
} from "./draftModel";

const baseMessage: Message = {
  id: "msg-1",
  contact_id: "contact-alice",
  direction: "in",
  subject: "Projet Alpha",
  body_snippet: "Bonjour",
  sent_at: 1_778_000_000,
  has_attachments: false,
  is_read: true,
  cc_emails: [],
};

describe("composer draft model", () => {
  it("prépare un sujet RE éditable depuis le dernier sujet de la conversation", () => {
    expect(getDefaultReplySubject([baseMessage])).toBe("RE: Projet Alpha");
    expect(getDefaultReplySubject([{ ...baseMessage, subject: "Re: Déjà répondu" }])).toBe("Re: Déjà répondu");
    expect(getDefaultReplySubject([{ ...baseMessage, subject: null }])).toBe("RE: réponse en cours");
  });

  it("ne sauvegarde pas les brouillons entièrement vides", () => {
    expect(shouldSaveDraft({ subject: "RE: Projet Alpha", body: "" })).toBe(true);
    expect(shouldSaveDraft({ subject: "", body: "   " })).toBe(false);
    expect(shouldSaveDraft({ subject: "", body: "À relire" })).toBe(true);
  });

  it("construit le payload backend scoped au compte et à la conversation", () => {
    expect(
      buildDraftPayload({
        accountId: "demo-account-gmail",
        contactId: "demo-contact-alice",
        subject: "RE: Projet Alpha",
        body: "Brouillon local",
        ccEmails: ["copie@example.com"],
        signatureActive: true,
      }),
    ).toEqual({
      account_id: "demo-account-gmail",
      contact_id: "demo-contact-alice",
      subject: "RE: Projet Alpha",
      body_text: "Brouillon local",
      cc_emails: ["copie@example.com"],
      signature_active: true,
    });
  });

  it("propose les CC du dernier message entrant uniquement quand il y en a", () => {
    const incomingWithCc: Message = {
      ...baseMessage,
      id: "msg-in-cc",
      direction: "in",
      cc_emails: ["copie@example.com", "team@example.com"],
    };
    const laterOutgoing: Message = {
      ...baseMessage,
      id: "msg-out",
      direction: "out",
      cc_emails: ["ne-pas-reprendre@example.com"],
      sent_at: incomingWithCc.sent_at + 10,
    };

    expect(getReplyCcCandidates([incomingWithCc, laterOutgoing])).toEqual([
      "copie@example.com",
      "team@example.com",
    ]);
    expect(getReplyCcCandidates([{ ...baseMessage, cc_emails: [] }])).toEqual([]);
    expect(buildReplyCcState([incomingWithCc])).toEqual({ visible: true, emails: ["copie@example.com", "team@example.com"] });
    expect(buildReplyCcState([{ ...baseMessage, cc_emails: [] }])).toEqual({ visible: false, emails: [] });
  });

  it("applique la signature du compte uniquement quand le toggle est actif", () => {
    expect(buildSignedBody({ body: "Bonjour", signature: "—\nAlice", signatureActive: true })).toBe(
      "Bonjour\n\n—\nAlice",
    );
    expect(buildSignedBody({ body: "Bonjour", signature: "—\nAlice", signatureActive: false })).toBe("Bonjour");
    expect(buildSignedBody({ body: "Bonjour", signature: null, signatureActive: true })).toBe("Bonjour");
  });

  it("bloque l'envoi pendant une sauvegarde de brouillon en vol", () => {
    expect(canSendComposer({ body: "À envoyer", sendPending: false, savePending: false })).toBe(true);
    expect(canSendComposer({ body: "À envoyer", sendPending: true, savePending: false })).toBe(false);
    expect(canSendComposer({ body: "À envoyer", sendPending: false, savePending: true })).toBe(false);
    expect(canSendComposer({ body: "   ", sendPending: false, savePending: false })).toBe(false);
  });

  it("ignore les autosaves dont la génération n'est plus courante", () => {
    expect(isCurrentDraftGeneration({ scheduledGeneration: 3, currentGeneration: 3 })).toBe(true);
    expect(isCurrentDraftGeneration({ scheduledGeneration: 3, currentGeneration: 4 })).toBe(false);
  });

  it("isole l'instance du composer par compte et conversation", () => {
    expect(getComposerInstanceKey("account-a", "contact-a")).toBe("account-a:contact-a");
    expect(getComposerInstanceKey("account-a", "contact-a")).not.toBe(
      getComposerInstanceKey("account-a", "contact-b"),
    );
    expect(getComposerInstanceKey(null, "contact-b")).toBe("pending-account:contact-b");
  });
});
