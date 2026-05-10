/**
 * Fiche contact Cowork MVP.
 *
 * Scope volontairement local/safe : lecture + PATCH des champs déjà exposés par
 * le backend, actions rapides locales (tel/mailto/archive), sans extraction de
 * signature réelle ni OAuth.
 */
import { useEffect, useMemo, useState } from "react";
import clsx from "clsx";
import {
  useContact,
  useConversationActionMutation,
  useUpdateContact,
  type Contact,
  type ContactPatchPayload,
} from "@/api/queries";
import { Avatar } from "@/components/Avatar";

interface Props {
  contactId: string;
  onClose: () => void;
}

type EditableContactField = keyof ContactPatchPayload;

interface ContactActionState {
  canCall: boolean;
  callHref: string | null;
  messageHref: string;
  archivePath: string;
}

interface ContactProfileProps {
  contact: Contact;
  form: ContactPatchPayload;
  isEditing: boolean;
  isSaving: boolean;
  isArchiving: boolean;
  saveError: string | null;
  archiveError: string | null;
  onEdit: () => void;
  onCancelEdit: () => void;
  onFieldChange: (field: EditableContactField, value: string) => void;
  onSave: () => void;
  onArchive: () => void;
}

interface ContactFormSyncState {
  formContactId: string | null;
  nextContactId: string;
  isEditing: boolean;
  isDirty: boolean;
}

const EMPTY_FORM: ContactPatchPayload = {
  display_name: "",
  company: "",
  role: "",
  phone: "",
  notes: "",
};

export function ContactSheet({ contactId, onClose }: Props) {
  const { data, isLoading, isError } = useContact(contactId);
  const updateContact = useUpdateContact();
  const conversationAction = useConversationActionMutation();
  const [isEditing, setIsEditing] = useState(false);
  const [form, setForm] = useState<ContactPatchPayload>(EMPTY_FORM);
  const [formContactId, setFormContactId] = useState<string | null>(null);
  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    if (!data) return;
    if (!shouldSyncContactForm({ formContactId, nextContactId: contactId, isEditing, isDirty })) return;
    const contactChanged = formContactId !== contactId;
    setForm(contactToForm(data));
    setFormContactId(contactId);
    setIsDirty(false);
    if (contactChanged) setIsEditing(false);
  }, [data, contactId, formContactId, isDirty, isEditing]);

  const isSaving = updateContact.isPending;
  const isArchiving = conversationAction.isPending;

  if (isError) {
    return (
      <aside className="border-l border-border bg-bg-e1 flex flex-col items-center justify-center gap-3 p-6">
        <p className="text-sm text-text-muted text-center">Fiche contact indisponible.</p>
        <button
          type="button"
          onClick={onClose}
          className="h-11 px-4 rounded-xl bg-bg-e2 hover:bg-bg-e3 text-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        >
          Fermer
        </button>
      </aside>
    );
  }

  if (isLoading || !data) {
    return (
      <aside
        className="border-l border-border bg-bg-e1 flex items-center justify-center p-6"
        aria-busy="true"
        aria-label="Chargement de la fiche contact"
      >
        <span className="text-text-muted text-sm">Chargement…</span>
      </aside>
    );
  }

  const handleSave = () => {
    const patch = normalizeContactPatch(form);
    updateContact.mutate(
      { id: contactId, patch },
      { onSuccess: (contact) => {
        setForm(contactToForm(contact));
        setFormContactId(contact.id);
        setIsDirty(false);
        setIsEditing(false);
      } },
    );
  };

  const handleArchive = () => {
    conversationAction.mutate(
      { path: getContactActionState(data).archivePath },
      { onSuccess: onClose },
    );
  };

  return (
    <aside className="border-l border-border bg-bg-e1 flex flex-col min-h-0" aria-label="Fiche contact complète">
      <header className="h-14 border-b border-border px-3 flex items-center justify-between shrink-0">
        <h2 className="font-semibold text-[15px]">Contact</h2>
        <button
          type="button"
          onClick={onClose}
          className="w-11 h-11 rounded-xl hover:bg-bg-e3 text-text-muted flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          aria-label="Fermer la fiche contact"
        >
          ✕
        </button>
      </header>

      <ContactProfile
        contact={data}
        form={form}
        isEditing={isEditing}
        isSaving={isSaving}
        isArchiving={isArchiving}
        saveError={updateContact.isError ? getContactMutationErrorMessage("save", updateContact.error) : null}
        archiveError={conversationAction.isError ? getContactMutationErrorMessage("archive", conversationAction.error) : null}
        onEdit={() => setIsEditing(true)}
        onCancelEdit={() => {
          setForm(contactToForm(data));
          setIsDirty(false);
          setIsEditing(false);
        }}
        onFieldChange={(field, value) => {
          setForm((current) => ({ ...current, [field]: value }));
          setIsDirty(true);
        }}
        onSave={handleSave}
        onArchive={handleArchive}
      />
    </aside>
  );
}

export function ContactProfile({
  contact,
  form,
  isEditing,
  isSaving,
  isArchiving,
  saveError,
  archiveError,
  onEdit,
  onCancelEdit,
  onFieldChange,
  onSave,
  onArchive,
}: ContactProfileProps) {
  const title = contact.display_name?.trim() || contact.email;
  const roleCompany = formatRoleCompany(contact.role, contact.company);
  const actions = useMemo(() => getContactActionState(contact), [contact]);

  return (
    <div className="flex-1 min-h-0 overflow-y-auto px-4 pb-5">
      <section className="py-5 flex flex-col items-center gap-2 border-b border-border text-center">
        <div data-contact-avatar="large">
          <Avatar initials={title.slice(0, 2)} size={76} />
        </div>
        <div>
          <h3 className="text-[20px] leading-tight font-semibold text-text">{title}</h3>
          <p className="mt-1 text-[13px] text-text-muted min-h-[18px]">
            {roleCompany || "Rôle et société non renseignés"}
          </p>
        </div>

        <div className="mt-3 grid grid-cols-3 gap-2 w-full" aria-label="Actions rapides contact">
          <a
            href={actions.callHref ?? undefined}
            aria-disabled={!actions.canCall}
            className={clsx(actionClassName, !actions.canCall && "opacity-45 pointer-events-none")}
            aria-label={actions.canCall ? `Appeler ${title}` : "Téléphone non renseigné"}
          >
            <span aria-hidden>☎</span>
            <span>Appeler</span>
          </a>
          <a href={actions.messageHref} className={actionClassName} aria-label={`Écrire à ${title}`}>
            <span aria-hidden>✉</span>
            <span>Message</span>
          </a>
          <button
            type="button"
            onClick={onArchive}
            disabled={isArchiving}
            className={actionClassName}
            aria-label={`Archiver la conversation avec ${title}`}
          >
            <span aria-hidden>⌫</span>
            <span>{isArchiving ? "Archivage…" : "Archiver"}</span>
          </button>
        </div>
        {archiveError && (
          <p role="alert" className="mt-2 rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-[12px] text-red-200">
            {archiveError}
          </p>
        )}
      </section>

      <section className="py-4 border-b border-border" aria-labelledby="contact-fields-title">
        <div className="flex items-center justify-between gap-3 mb-3">
          <h4 id="contact-fields-title" className="text-[12px] uppercase tracking-[0.12em] text-text-dim font-semibold">
            Coordonnées
          </h4>
          {!isEditing && (
            <button
              type="button"
              onClick={onEdit}
              className="h-11 px-3 rounded-xl bg-bg-e2 hover:bg-bg-e3 text-[13px] text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            >
              Modifier
            </button>
          )}
        </div>

        {isEditing ? (
          <EditContactForm
            form={form}
            isSaving={isSaving}
            saveError={saveError}
            email={contact.email}
            onCancelEdit={onCancelEdit}
            onFieldChange={onFieldChange}
            onSave={onSave}
          />
        ) : (
          <dl className="grid gap-2.5">
            <ContactInfoRow label="Email" value={contact.email} />
            <ContactInfoRow label="Téléphone" value={contact.phone || "Téléphone non renseigné"} empty={!contact.phone} />
            <ContactInfoRow label="Société" value={contact.company || "Société non renseignée"} empty={!contact.company} />
            <ContactInfoRow label="Poste" value={contact.role || "Poste non renseigné"} empty={!contact.role} />
            <ContactInfoRow label="Notes" value={contact.notes || "Aucune note"} empty={!contact.notes} multiline />
          </dl>
        )}
      </section>

      <section className="py-4" aria-labelledby="contact-attachments-title">
        <div className="flex items-center justify-between gap-3 mb-3">
          <h4 id="contact-attachments-title" className="text-[12px] uppercase tracking-[0.12em] text-text-dim font-semibold">
            Pièces jointes
          </h4>
          <span className="text-[12px] text-text-dim">{contact.attachments.length}/24</span>
        </div>
        {contact.attachments.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border bg-bg-e2/60 px-4 py-6 text-center text-sm text-text-muted">
            Aucune pièce jointe échangée
          </div>
        ) : (
          <ul className="grid gap-2 sm:grid-cols-2 xl:grid-cols-1" aria-label="Grille des pièces jointes échangées">
            {contact.attachments.map((attachment) => (
              <li key={attachment.id} className="rounded-2xl bg-bg-e2 border border-border p-3 min-w-0">
                <div className="flex items-start gap-2 min-w-0">
                  <span className="w-9 h-9 rounded-xl bg-accent-soft text-accent flex items-center justify-center shrink-0" aria-hidden>
                    📎
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-[13px] text-text font-medium">{attachment.filename}</p>
                    <p className="mt-0.5 text-[11px] text-text-dim">
                      {formatAttachmentType(attachment.mime_type, attachment.filename)} · {formatSize(attachment.size_bytes)} · {formatAttachmentDate(attachment.created_at)}
                    </p>
                  </div>
                </div>
                <a
                  href={`#attachment-${attachment.id}`}
                  className="mt-3 h-11 rounded-xl bg-bg-e3 hover:bg-border text-[12px] text-text flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
                  aria-label={`Ouvrir ${attachment.filename}`}
                >
                  Ouvrir
                </a>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function EditContactForm({
  form,
  email,
  isSaving,
  saveError,
  onCancelEdit,
  onFieldChange,
  onSave,
}: {
  form: ContactPatchPayload;
  email: string;
  isSaving: boolean;
  saveError: string | null;
  onCancelEdit: () => void;
  onFieldChange: (field: EditableContactField, value: string) => void;
  onSave: () => void;
}) {
  return (
    <form
      className="grid gap-3"
      onSubmit={(event) => {
        event.preventDefault();
        onSave();
      }}
    >
      <ReadonlyField label="Email" value={email} help="Adresse d’origine conservée pour la conversation locale." />
      <EditableField label="Nom" name="display_name" value={form.display_name} onFieldChange={onFieldChange} />
      <EditableField label="Poste" name="role" value={form.role} onFieldChange={onFieldChange} />
      <EditableField label="Société" name="company" value={form.company} onFieldChange={onFieldChange} />
      <EditableField label="Téléphone" name="phone" value={form.phone} inputMode="tel" onFieldChange={onFieldChange} />
      <EditableField label="Notes" name="notes" value={form.notes} multiline onFieldChange={onFieldChange} />
      {saveError && (
        <p role="alert" className="rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-[12px] text-red-200">
          {saveError}
        </p>
      )}
      <div className="grid grid-cols-2 gap-2 pt-1">
        <button
          type="button"
          onClick={onCancelEdit}
          className="h-11 rounded-xl bg-bg-e2 hover:bg-bg-e3 text-[13px] text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        >
          Annuler
        </button>
        <button
          type="submit"
          disabled={isSaving}
          className="h-11 rounded-xl bg-accent text-bg font-semibold text-[13px] disabled:opacity-60 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        >
          {isSaving ? "Enregistrement…" : "Enregistrer"}
        </button>
      </div>
    </form>
  );
}

function EditableField({
  label,
  name,
  value,
  inputMode,
  multiline = false,
  onFieldChange,
}: {
  label: string;
  name: EditableContactField;
  value: string;
  inputMode?: "tel";
  multiline?: boolean;
  onFieldChange: (field: EditableContactField, value: string) => void;
}) {
  const id = `contact-${name}`;
  return (
    <label htmlFor={id} className="grid gap-1.5 text-[12px] text-text-muted">
      <span>{label}</span>
      {multiline ? (
        <textarea
          id={id}
          name={name}
          value={value}
          onChange={(event) => onFieldChange(name, event.currentTarget.value)}
          rows={4}
          className="min-h-[96px] rounded-xl bg-bg border border-border px-3 py-2 text-[14px] text-text resize-y focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        />
      ) : (
        <input
          id={id}
          name={name}
          value={value}
          inputMode={inputMode}
          onChange={(event) => onFieldChange(name, event.currentTarget.value)}
          className="h-11 rounded-xl bg-bg border border-border px-3 text-[14px] text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        />
      )}
    </label>
  );
}

function ReadonlyField({ label, value, help }: { label: string; value: string; help: string }) {
  return (
    <div className="grid gap-1.5 text-[12px] text-text-muted">
      <span>{label}</span>
      <div className="min-h-11 rounded-xl bg-bg-e2 border border-border px-3 py-2 text-[14px] text-text flex items-center">
        {value}
      </div>
      <span className="text-[11px] text-text-dim">{help}</span>
    </div>
  );
}

function ContactInfoRow({
  label,
  value,
  empty = false,
  multiline = false,
}: {
  label: string;
  value: string;
  empty?: boolean;
  multiline?: boolean;
}) {
  return (
    <div className="rounded-2xl bg-bg-e2 border border-border px-3 py-2.5">
      <dt className="text-[11px] uppercase tracking-[0.08em] text-text-dim">{label}</dt>
      <dd className={clsx("mt-1 text-[14px] text-text break-words", empty && "text-text-muted", multiline && "whitespace-pre-wrap")}>{value}</dd>
    </div>
  );
}

function contactToForm(contact: Contact): ContactPatchPayload {
  return {
    display_name: contact.display_name ?? "",
    company: contact.company ?? "",
    role: contact.role ?? "",
    phone: contact.phone ?? "",
    notes: contact.notes ?? "",
  };
}

function normalizeContactPatch(form: ContactPatchPayload): Partial<ContactPatchPayload> {
  return {
    display_name: form.display_name.trim(),
    company: form.company.trim(),
    role: form.role.trim(),
    phone: form.phone.trim(),
    notes: form.notes.trim(),
  };
}

export function shouldSyncContactForm({
  formContactId,
  nextContactId,
  isEditing,
  isDirty,
}: ContactFormSyncState): boolean {
  if (formContactId !== nextContactId) return true;
  return !(isEditing && isDirty);
}

export function getContactMutationErrorMessage(action: "save" | "archive", error: unknown): string {
  const detail = error instanceof Error && error.message ? ` (${error.message.slice(0, 160)})` : "";
  if (action === "save") return `Enregistrement impossible pour le moment${detail}`;
  return `Archivage impossible pour le moment${detail}`;
}

export function getContactActionState(contact: Contact): ContactActionState {
  const phone = contact.phone?.trim() ?? "";
  const compactPhone = phone.replace(/(?!^)\+/g, "").replace(/[^\d+]/g, "");
  return {
    canCall: compactPhone.length > 0,
    callHref: compactPhone ? `tel:${compactPhone}` : null,
    messageHref: `mailto:${contact.email}`,
    archivePath: `/conversations/${contact.id}/archive`,
  };
}

function formatRoleCompany(role: string | null, company: string | null): string {
  return [role, company].map((part) => part?.trim()).filter(Boolean).join(" · ");
}

export function formatAttachmentType(mimeType: string | null, filename: string): string {
  const mime = mimeType?.toLowerCase() ?? "";
  const lowerFilename = filename.toLowerCase();
  if (mime.includes("pdf") || lowerFilename.endsWith(".pdf")) return "PDF";
  if (mime.startsWith("image/") || /\.(png|jpe?g|gif|webp)$/.test(lowerFilename)) return "Image";
  if (mime.includes("spreadsheet") || /\.(xlsx?|csv)$/.test(lowerFilename)) return "Tableur";
  if (mime.includes("word") || /\.(docx?|rtf)$/.test(lowerFilename)) return "Document";
  if (mime.includes("zip") || lowerFilename.endsWith(".zip")) return "Archive";
  return "Fichier";
}

export function formatAttachmentDate(createdAt: number | string | null | undefined): string {
  if (createdAt === null || createdAt === undefined || createdAt === "") return "Date inconnue";
  const raw = typeof createdAt === "number" ? createdAt * 1000 : Date.parse(createdAt);
  if (!Number.isFinite(raw)) return "Date inconnue";
  return new Intl.DateTimeFormat("fr-FR", { day: "2-digit", month: "short", year: "numeric" }).format(new Date(raw));
}

function formatSize(bytes: number | null): string {
  if (bytes === null || !Number.isFinite(bytes)) return "Taille inconnue";
  if (bytes < 1024) return `${bytes} o`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} ko`;
  return `${(bytes / 1024 / 1024).toFixed(1)} Mo`;
}

const actionClassName =
  "min-h-11 rounded-2xl bg-bg-e2 hover:bg-bg-e3 border border-border text-[12px] text-text flex flex-col items-center justify-center gap-1 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent";
