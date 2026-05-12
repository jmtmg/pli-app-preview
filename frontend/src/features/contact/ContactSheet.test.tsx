import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import type { Contact, ContactPatchPayload } from "@/api/queries";
import {
  ContactProfile,
  formatAttachmentDate,
  formatAttachmentPreview,
  formatAttachmentType,
  getContactActionState,
  getContactMutationErrorMessage,
  shouldSyncContactForm,
} from "./ContactSheet";

const CONTACT: Contact = {
  id: "c-alice",
  account_id: "account-a",
  email: "alice@example.com",
  display_name: "Alice Martin",
  company: "JMJ Consulting",
  role: "Direction opérations",
  phone: "12345",
  notes: "Note prioritaire à garder visible.",
  kind: "human",
  is_muted: false,
  is_pinned: false,
  pinned_order: null,
  unread_count: 1,
  has_attachments: true,
  attachments: [
    {
      id: "att-1",
      message_id: "m1",
      filename: "brief-strategie.pdf",
      mime_type: "application/pdf",
      size_bytes: 42_000,
      created_at: 1_778_270_400,
    },
    {
      id: "att-2",
      message_id: "m1",
      filename: "photo-chantier.png",
      mime_type: "image/png",
      size_bytes: 120_000,
      created_at: 1_778_270_500,
    },
  ],
};

const FORM: ContactPatchPayload = {
  display_name: "Alice Martin",
  company: "JMJ Consulting",
  role: "Direction opérations",
  phone: "12345",
  notes: "Note prioritaire à garder visible.",
};

describe("ContactSheet Cowork MVP", () => {
  it("rend une fiche complète avec avatar large, infos visibles, actions rapides et grille PJ", () => {
    const html = renderToStaticMarkup(
      <ContactProfile
        contact={CONTACT}
        form={FORM}
        isEditing={false}
        isSaving={false}
        isArchiving={false}
        saveError={null}
        archiveError={null}
        onArchive={vi.fn()}
        onCancelEdit={vi.fn()}
        onEdit={vi.fn()}
        onFieldChange={vi.fn()}
        onSave={vi.fn()}
      />,
    );

    expect(html).toContain("data-contact-avatar=\"large\"");
    expect(html).toContain("Alice Martin");
    expect(html).toContain("Direction opérations · JMJ Consulting");
    expect(html).toContain("alice@example.com");
    expect(html).toContain("12345");
    expect(html).toContain("Note prioritaire à garder visible.");
    for (const label of ["Appeler", "Message", "Archiver", "Modifier"]) {
      expect(html).toContain(label);
    }
    expect(html).toContain("href=\"tel:12345\"");
    expect(html).toContain("href=\"mailto:alice@example.com\"");
    expect(html).toContain("brief-strategie.pdf");
    expect(html).toContain("PDF");
    expect(html).toContain("Aperçu PDF local");
    expect(html).toContain("photo-chantier.png");
    expect(html).toContain("Aperçu image local");
    expect(html).toContain("41.0 ko");
    expect(html).toContain("Ouvrir");
  });

  it("affiche des états vides accessibles quand téléphone, notes et PJ manquent", () => {
    const contact: Contact = {
      ...CONTACT,
      phone: null,
      notes: null,
      has_attachments: false,
      attachments: [],
    };
    const html = renderToStaticMarkup(
      <ContactProfile
        contact={contact}
        form={{ ...FORM, phone: "", notes: "" }}
        isEditing={false}
        isSaving={false}
        isArchiving={false}
        saveError={null}
        archiveError={null}
        onArchive={vi.fn()}
        onCancelEdit={vi.fn()}
        onEdit={vi.fn()}
        onFieldChange={vi.fn()}
        onSave={vi.fn()}
      />,
    );

    expect(html).toContain("Téléphone non renseigné");
    expect(html).toContain("Aucune note");
    expect(html).toContain("Aucune pièce jointe échangée");
    expect(html).toContain("aria-disabled=\"true\"");
    expect(html).not.toContain("href=\"tel:");
  });

  it("expose le formulaire PATCH local des champs modifiables", () => {
    const html = renderToStaticMarkup(
      <ContactProfile
        contact={CONTACT}
        form={{ ...FORM, display_name: "Alice M.", phone: "67890" }}
        isEditing
        isSaving={false}
        isArchiving={false}
        saveError={null}
        archiveError={null}
        onArchive={vi.fn()}
        onCancelEdit={vi.fn()}
        onEdit={vi.fn()}
        onFieldChange={vi.fn()}
        onSave={vi.fn()}
      />,
    );

    for (const name of ["display_name", "role", "company", "phone", "notes"]) {
      expect(html).toContain(`name="${name}"`);
    }
    expect(html).toContain("value=\"Alice M.\"");
    expect(html).toContain("value=\"67890\"");
    expect(html).toContain("Enregistrer");
    expect(html).toContain("Annuler");
  });

  it("résout les actions rapides et les libellés PJ sans brancher OAuth", () => {
    expect(getContactActionState(CONTACT)).toEqual({
      canCall: true,
      callHref: "tel:12345",
      messageHref: "mailto:alice@example.com",
      archivePath: "/conversations/c-alice/archive",
    });
    expect(formatAttachmentType("application/pdf", "brief-strategie.pdf")).toBe("PDF");
    expect(formatAttachmentType("image/png", "avatar.png")).toBe("Image");
    expect(formatAttachmentPreview("image/png", "avatar.png")).toBe("Aperçu image local");
    expect(formatAttachmentPreview("application/pdf", "brief.pdf")).toBe("Aperçu PDF local");
    expect(formatAttachmentPreview("text/plain", "notes.txt")).toBe("Aperçu texte local");
    expect(formatAttachmentPreview("application/zip", "archive.zip")).toBe("Aperçu indisponible");
    expect(formatAttachmentDate(1_778_270_400)).toMatch(/2026/);
  });

  it("protège les éditions locales sales contre un refetch React Query du même contact", () => {
    expect(
      shouldSyncContactForm({
        formContactId: "c-alice",
        nextContactId: "c-alice",
        isEditing: true,
        isDirty: true,
      }),
    ).toBe(false);

    expect(
      shouldSyncContactForm({
        formContactId: "c-alice",
        nextContactId: "c-bob",
        isEditing: true,
        isDirty: true,
      }),
    ).toBe(true);

    expect(
      shouldSyncContactForm({
        formContactId: "c-alice",
        nextContactId: "c-alice",
        isEditing: false,
        isDirty: false,
      }),
    ).toBe(true);
  });

  it("fournit des messages d'erreur visibles pour PATCH et archive", () => {
    expect(getContactMutationErrorMessage("save", new Error("HTTP 500"))).toContain("Enregistrement impossible");
    expect(getContactMutationErrorMessage("archive", new Error("HTTP 500"))).toContain("Archivage impossible");
  });
});
