import { describe, expect, it } from "vitest";
import type { Conversation } from "@/api/queries";
import {
  buildNewMessagePayload,
  canSendNewMessage,
  fileToLocalAttachment,
  filterRecipientSuggestions,
  formatAttachmentSize,
  getRecipientLabel,
  parseEmailList,
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
      ccEmails: "",
      bccEmails: "",
      subject: "Point v1",
      body: "Bonjour Alice",
      attachments: [],
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
      ccEmails: "",
      bccEmails: "",
      subject: "Premier contact",
      body: "Bonjour",
      attachments: [],
    };

    expect(buildNewMessagePayload(draft)).toEqual({
      account_id: "account-a",
      to_email: "new.person@example.com",
      subject: "Premier contact",
      body: "Bonjour",
    });
  });

  it("normalise les listes CC/CCI et les métadonnées PJ dans le payload", () => {
    const draft: NewMessageDraft = {
      accountId: "account-a",
      selectedContactId: null,
      toEmail: "new.person@example.com",
      ccEmails: "copy@example.com; second@example.com",
      bccEmails: "hidden@example.com",
      subject: "Pièces jointes",
      body: "Bonjour",
      attachments: [
        {
          id: "att-1",
          name: "brief.pdf",
          type: "application/pdf",
          size: 12_345,
        },
      ],
    };

    expect(buildNewMessagePayload(draft)).toEqual({
      account_id: "account-a",
      to_email: "new.person@example.com",
      cc_emails: ["copy@example.com", "second@example.com"],
      bcc_emails: ["hidden@example.com"],
      subject: "Pièces jointes",
      body: "Bonjour",
      attachments: [
        {
          filename: "brief.pdf",
          mime_type: "application/pdf",
          size_bytes: 12_345,
        },
      ],
    });
  });

  it("bloque l'envoi sans compte, destinataire email valide ou corps", () => {
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "new@example.com", ccEmails: "", bccEmails: "", body: "Bonjour", attachments: [], isPending: false })).toBe(true);
    expect(canSendNewMessage({ accountId: null, toEmail: "new@example.com", ccEmails: "", bccEmails: "", body: "Bonjour", attachments: [], isPending: false })).toBe(false);
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "not-an-email", ccEmails: "", bccEmails: "", body: "Bonjour", attachments: [], isPending: false })).toBe(false);
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "new@example.com", ccEmails: "", bccEmails: "", body: "", attachments: [], isPending: false })).toBe(false);
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "new@example.com", ccEmails: "", bccEmails: "", body: "Bonjour", attachments: [], isPending: true })).toBe(false);
  });

  it("bloque l'envoi avec une liste CC/CCI invalide ou une pièce jointe trop lourde", () => {
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "new@example.com", ccEmails: "copy@example.com", bccEmails: "hidden@example.com", body: "Bonjour", attachments: [], isPending: false })).toBe(true);
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "new@example.com", ccEmails: "not-an-email", bccEmails: "", body: "Bonjour", attachments: [], isPending: false })).toBe(false);
    expect(canSendNewMessage({ accountId: "account-a", toEmail: "new@example.com", ccEmails: "", bccEmails: "bad", body: "Bonjour", attachments: [], isPending: false })).toBe(false);
    expect(canSendNewMessage({
      accountId: "account-a",
      toEmail: "new@example.com",
      ccEmails: "",
      bccEmails: "",
      body: "Bonjour",
      attachments: [{ id: "big", name: "big.zip", size: 26 * 1024 * 1024, type: "application/zip" }],
      isPending: false,
    })).toBe(false);
  });

  it("parse les emails et formate les fichiers locaux sans contenu", () => {
    expect(parseEmailList(" a@example.com, b@example.com ; c@example.com ")).toEqual([
      "a@example.com",
      "b@example.com",
      "c@example.com",
    ]);
    expect(formatAttachmentSize(12_345)).toBe("12 Ko");
    expect(formatAttachmentSize(2_400_000)).toBe("2.3 Mo");

    const file = new File(["contenu local ignoré"], "notes.txt", { type: "text/plain" });
    const metadata = fileToLocalAttachment(file, "att-1");
    expect(metadata).toEqual({
      id: "att-1",
      name: "notes.txt",
      type: "text/plain",
      size: file.size,
    });
  });

  it("affiche le libellé de suggestion contact sans exposer d'autre compte", () => {
    expect(getRecipientLabel(CONVERSATIONS[0])).toBe("Alice Martin — alice.martin@example.com");
  });
});
