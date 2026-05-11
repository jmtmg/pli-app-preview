import { describe, expect, it } from "vitest";
import type { Conversation } from "@/api/queries";
import {
  buildNewMessagePayload,
  canSendNewMessage,
  filterRecipientSuggestions,
  getRecipientLabel,
  type NewMessageDraft,
} from "./newMessageModel";

const CONVERSATIONS: Conversation[] = [
  {
    contact_id: "c-alice",
    account_id: "account-a",
    email: "alice.martin@example.com",
    email_normalized: "alice.martin@example.com",
    display_name: "Alice Martin",
    kind: "human",
    is_pinned: false,
    pinned_order: null,
    is_muted: false,
    unread_count: 0,
    has_attachments: false,
    last_msg_at: null,
    last_preview: null,
  },
  {
    contact_id: "c-support",
    account_id: "account-a",
    email: "support@example.com",
    email_normalized: "support@example.com",
    display_name: "Support PLI",
    kind: "notif",
    is_pinned: false,
    pinned_order: null,
    is_muted: false,
    unread_count: 0,
    has_attachments: false,
    last_msg_at: null,
    last_preview: null,
  },
];

describe("newMessageModel", () => {
  it("filtre les suggestions par nom ou email avec une limite stable", () => {
    expect(filterRecipientSuggestions(CONVERSATIONS, "ali", 4).map((c) => c.contact_id)).toEqual(["c-alice"]);
    expect(filterRecipientSuggestions(CONVERSATIONS, "example", 1)).toHaveLength(1);
  });

  it("construit un payload contact_id quand une suggestion existante est choisie", () => {
    const draft: NewMessageDraft = {
      accountId: "account-a",
      selectedContactId: "c-alice",
      toEmail: "alice.martin@example.com",
      subject: "Point v1",
      body: "Bonjour Alice",
    };

    expect(buildNewMessagePayload(draft)).toEqual({
      account_id: "account-a",
      contact_id: "c-alice",
      subject: "Point v1",
      body: "Bonjour Alice",
    });
  });

  it("construit un payload to_email quand le destinataire est nouveau", () => {
    const draft: NewMessageDraft = {
      accountId: "account-a",
      selectedContactId: null,
      toEmail: "new.person@example.com",
      subject: "Premier contact",
      body: "Bonjour",
    };

    expect(buildNewMessagePayload(draft)).toEqual({
      account_id: "account-a",
      to_email: "new.person@example.com",
      subject: "Premier contact",
      body: "Bonjour",
    });
  });

  it("bloque l'envoi sans compte, destinataire email valide ou corps", () => {
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "new@example.com", body: "Bonjour", isPending: false })).toBe(true);
    expect(canSendNewMessage({ accountId: null, toEmail: "new@example.com", body: "Bonjour", isPending: false })).toBe(false);
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "not-an-email", body: "Bonjour", isPending: false })).toBe(false);
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "new@example.com", body: "", isPending: false })).toBe(false);
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "new@example.com", body: "Bonjour", isPending: true })).toBe(false);
  });

  it("affiche le libellé de suggestion contact sans exposer d'autre compte", () => {
    expect(getRecipientLabel(CONVERSATIONS[0])).toBe("Alice Martin — alice.martin@example.com");
  });
});
