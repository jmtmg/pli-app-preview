import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import type { Account, Conversation } from "@/api/queries";
import { NewMessageModalView } from "./NewMessageModal";

const ACCOUNT: Account = {
  id: "account-a",
  email: "demo@pli-app.fr",
  provider: "gmail",
  display_name: "PLI demo",
  avatar_color: null,
  unread_count: 0,
  is_active: true,
  last_sync_at: null,
};

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
];

describe("NewMessageModalView", () => {
  it("rend De, À, Sujet, Corps, suggestions et état provider local", () => {
    const html = renderToStaticMarkup(
      <NewMessageModalView
        open
        account={ACCOUNT}
        conversations={CONVERSATIONS}
        selectedContactId={null}
        toEmail="ali"
        subject="Point v1"
        body="Bonjour"
        isSending={false}
        errorMessage={null}
        onClose={vi.fn()}
        onFieldChange={vi.fn()}
        onSelectRecipient={vi.fn()}
        onSubmit={vi.fn()}
      />,
    );

    expect(html).toContain("Nouveau message");
    expect(html).toContain("De");
    expect(html).toContain("demo@pli-app.fr");
    expect(html).toContain("À");
    expect(html).toContain("Sujet");
    expect(html).toContain("Corps");
    expect(html).toContain("Alice Martin — alice.martin@example.com");
    expect(html).toContain("Envoi local démo");
    expect(html).toContain("Cmd/Ctrl + Enter");
  });

  it("désactive l'envoi si le destinataire ou le corps manque", () => {
    const html = renderToStaticMarkup(
      <NewMessageModalView
        open
        account={ACCOUNT}
        conversations={CONVERSATIONS}
        selectedContactId={null}
        toEmail="not-an-email"
        subject=""
        body=""
        isSending={false}
        errorMessage={null}
        onClose={vi.fn()}
        onFieldChange={vi.fn()}
        onSelectRecipient={vi.fn()}
        onSubmit={vi.fn()}
      />,
    );

    expect(html).toContain("disabled=\"\"");
    expect(html).toContain("Saisis une adresse email valide et un message.");
  });
});
