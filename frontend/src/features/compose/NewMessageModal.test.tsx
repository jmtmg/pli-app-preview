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
        ccEmails=""
        bccEmails=""
        subject="Point v1"
        body="Bonjour"
        attachments={[]}
        advancedOpen={false}
        isSending={false}
        errorMessage={null}
        onClose={vi.fn()}
        onFieldChange={vi.fn()}
        onSelectRecipient={vi.fn()}
        onToggleAdvanced={vi.fn()}
        onFilesSelected={vi.fn()}
        onRemoveAttachment={vi.fn()}
        onSubmit={vi.fn()}
      />,
    );

    expect(html).toContain("Nouveau message");
    expect(html).toContain("De");
    expect(html).toContain("demo@pli-app.fr");
    expect(html).toContain("À");
    expect(html).toContain("Cc/Cci");
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
        ccEmails=""
        bccEmails=""
        subject=""
        body=""
        attachments={[]}
        advancedOpen={false}
        isSending={false}
        errorMessage={null}
        onClose={vi.fn()}
        onFieldChange={vi.fn()}
        onSelectRecipient={vi.fn()}
        onToggleAdvanced={vi.fn()}
        onFilesSelected={vi.fn()}
        onRemoveAttachment={vi.fn()}
        onSubmit={vi.fn()}
      />,
    );

    expect(html).toContain("disabled=\"\"");
    expect(html).toContain("Saisis une adresse email valide et un message.");
  });

  it("rend les champs CC/CCI et les chips de pièces jointes quand les options sont ouvertes", () => {
    const html = renderToStaticMarkup(
      <NewMessageModalView
        open
        account={ACCOUNT}
        conversations={CONVERSATIONS}
        selectedContactId={null}
        toEmail="alice.martin@example.com"
        ccEmails="copy@example.com"
        bccEmails="hidden@example.com"
        subject="Point v1"
        body="Bonjour"
        attachments={[
          {
            id: "att-1",
            name: "brief.pdf",
            type: "application/pdf",
            size: 12_345,
          },
        ]}
        advancedOpen
        isSending={false}
        errorMessage={null}
        onClose={vi.fn()}
        onFieldChange={vi.fn()}
        onSelectRecipient={vi.fn()}
        onToggleAdvanced={vi.fn()}
        onFilesSelected={vi.fn()}
        onRemoveAttachment={vi.fn()}
        onSubmit={vi.fn()}
      />,
    );

    expect(html).toContain("Cc");
    expect(html).toContain("Cci");
    expect(html).toContain("copy@example.com");
    expect(html).toContain("hidden@example.com");
    expect(html).toContain("brief.pdf");
    expect(html).toContain("12 Ko");
  });
});
