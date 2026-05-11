import { useEffect, useState, type FormEvent, type KeyboardEvent } from "react";
import type { Account, Conversation } from "@/api/queries";
import { useConversations, useSendMessage } from "@/api/queries";
import {
  buildNewMessagePayload,
  canSendNewMessage,
  fileToLocalAttachment,
  filterRecipientSuggestions,
  formatAttachmentSize,
  getRecipientLabel,
  type NewMessageAttachment,
} from "./newMessageModel";

export interface NewMessageModalProps {
  open: boolean;
  account: Account | null;
  onClose: () => void;
  onSent: (contactId: string) => void;
}

export function NewMessageModal({ open, account, onClose, onSent }: NewMessageModalProps) {
  const { data } = useConversations(account?.id ?? null, "all");
  const sendMessage = useSendMessage();
  const [toEmail, setToEmail] = useState("");
  const [selectedContactId, setSelectedContactId] = useState<string | null>(null);
  const [ccEmails, setCcEmails] = useState("");
  const [bccEmails, setBccEmails] = useState("");
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [attachments, setAttachments] = useState<NewMessageAttachment[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const conversations = data?.pages.flatMap((page) => page.items) ?? [];

  useEffect(() => {
    if (!open) {
      setToEmail("");
      setSelectedContactId(null);
      setCcEmails("");
      setBccEmails("");
      setAdvancedOpen(false);
      setSubject("");
      setBody("");
      setAttachments([]);
      setErrorMessage(null);
    }
  }, [open]);

  async function handleSubmit() {
    if (!account) return;
    try {
      setErrorMessage(null);
      const sent = await sendMessage.mutateAsync(
        buildNewMessagePayload({
          accountId: account.id,
          selectedContactId,
          toEmail,
          ccEmails,
          bccEmails,
          subject,
          body,
          attachments,
        }),
      );
      onSent(sent.contact_id);
      onClose();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Envoi local impossible");
    }
  }

  return (
    <NewMessageModalView
      open={open}
      account={account}
      conversations={conversations}
      selectedContactId={selectedContactId}
      toEmail={toEmail}
      ccEmails={ccEmails}
      bccEmails={bccEmails}
      subject={subject}
      body={body}
      attachments={attachments}
      advancedOpen={advancedOpen}
      isSending={sendMessage.isPending}
      errorMessage={errorMessage}
      onClose={onClose}
      onFieldChange={(field, value) => {
        if (field === "toEmail") {
          setToEmail(value);
          setSelectedContactId(null);
        }
        if (field === "ccEmails") setCcEmails(value);
        if (field === "bccEmails") setBccEmails(value);
        if (field === "subject") setSubject(value);
        if (field === "body") setBody(value);
      }}
      onSelectRecipient={(conversation) => {
        setToEmail(conversation.email);
        setSelectedContactId(conversation.contact_id);
      }}
      onToggleAdvanced={() => setAdvancedOpen((value) => !value)}
      onFilesSelected={(files) => {
        const nextAttachments = Array.from(files ?? []).map((file) => fileToLocalAttachment(file));
        setAttachments((current) => [...current, ...nextAttachments]);
      }}
      onRemoveAttachment={(id) => {
        setAttachments((current) => current.filter((attachment) => attachment.id !== id));
      }}
      onSubmit={() => {
        void handleSubmit();
      }}
    />
  );
}

export interface NewMessageModalViewProps {
  open: boolean;
  account: Account | null;
  conversations: Conversation[];
  selectedContactId: string | null;
  toEmail: string;
  ccEmails: string;
  bccEmails: string;
  subject: string;
  body: string;
  attachments: NewMessageAttachment[];
  advancedOpen: boolean;
  isSending: boolean;
  errorMessage: string | null;
  onClose: () => void;
  onFieldChange: (field: "toEmail" | "ccEmails" | "bccEmails" | "subject" | "body", value: string) => void;
  onSelectRecipient: (conversation: Conversation) => void;
  onToggleAdvanced: () => void;
  onFilesSelected: (files: FileList | null) => void;
  onRemoveAttachment: (id: string) => void;
  onSubmit: () => void;
}

export function NewMessageModalView({
  open,
  account,
  conversations,
  selectedContactId,
  toEmail,
  ccEmails,
  bccEmails,
  subject,
  body,
  attachments,
  advancedOpen,
  isSending,
  errorMessage,
  onClose,
  onFieldChange,
  onSelectRecipient,
  onToggleAdvanced,
  onFilesSelected,
  onRemoveAttachment,
  onSubmit,
}: NewMessageModalViewProps) {
  if (!open) return null;
  const suggestions = filterRecipientSuggestions(conversations, toEmail, 5);
  const canSend = canSendNewMessage({
    accountId: account?.id ?? null,
    toEmail,
    ccEmails,
    bccEmails,
    body,
    attachments,
    isPending: isSending,
  });

  function submit(event?: FormEvent) {
    event?.preventDefault();
    if (!canSend) return;
    onSubmit();
  }

  function onKeyDown(event: KeyboardEvent<HTMLFormElement>) {
    if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
      event.preventDefault();
      submit();
    }
    if (event.key === "Escape") {
      event.preventDefault();
      onClose();
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/55 p-0 sm:p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="new-message-title"
      onClick={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <form
        className="relative w-full sm:max-w-xl max-h-[92vh] overflow-y-auto rounded-t-[28px] sm:rounded-[28px] border border-border bg-bg-e1 shadow-2xl"
        onSubmit={submit}
        onKeyDown={onKeyDown}
        onClick={(event) => event.stopPropagation()}
      >
        <header className="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
          <div>
            <h2 id="new-message-title" className="text-[17px] font-semibold text-text">Nouveau message</h2>
            <p className="mt-0.5 text-[12px] text-text-muted">Envoi local démo — OAuth Gmail/Microsoft viendra ensuite.</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="h-11 w-11 rounded-xl hover:bg-bg-e3 text-text-muted focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            aria-label="Fermer"
          >
            ✕
          </button>
        </header>

        <div className="grid gap-3 px-4 py-4">
          <ReadonlyLine label="De" value={account?.email ?? "Compte local indisponible"} />

          <div className="grid gap-1.5 text-[12px] text-text-muted">
            <div className="flex items-center justify-between gap-3">
              <label htmlFor="new-message-to">À</label>
              <button
                type="button"
                onClick={onToggleAdvanced}
                className="min-h-11 rounded-lg px-2 text-[12px] text-text-muted hover:bg-bg-e3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
                aria-expanded={advancedOpen}
                aria-controls="new-message-advanced"
              >
                Cc/Cci
              </button>
            </div>
            <input
              id="new-message-to"
              name="to"
              autoFocus
              inputMode="email"
              value={toEmail}
              onChange={(event) => onFieldChange("toEmail", event.currentTarget.value)}
              placeholder="contact@example.com"
              className="h-11 rounded-xl border border-border bg-bg px-3 text-[14px] text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            />
          </div>

          {suggestions.length > 0 && (
            <div className="grid gap-1" aria-label="Suggestions destinataires">
              {suggestions.map((conversation) => (
                <button
                  key={conversation.contact_id}
                  type="button"
                  onClick={() => onSelectRecipient(conversation)}
                  className="min-h-11 rounded-xl border border-border bg-bg-e2 px-3 py-2 text-left text-[13px] text-text hover:bg-bg-e3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
                  aria-pressed={selectedContactId === conversation.contact_id}
                >
                  {getRecipientLabel(conversation)}
                </button>
              ))}
            </div>
          )}

          {advancedOpen && (
            <div id="new-message-advanced" className="grid gap-3 sm:grid-cols-2">
              <label className="grid gap-1.5 text-[12px] text-text-muted" htmlFor="new-message-cc">
                <span>Cc</span>
                <input
                  id="new-message-cc"
                  name="cc"
                  inputMode="email"
                  value={ccEmails}
                  onChange={(event) => onFieldChange("ccEmails", event.currentTarget.value)}
                  placeholder="copie@example.com"
                  className="h-11 rounded-xl border border-border bg-bg px-3 text-[14px] text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
                />
              </label>

              <label className="grid gap-1.5 text-[12px] text-text-muted" htmlFor="new-message-bcc">
                <span>Cci</span>
                <input
                  id="new-message-bcc"
                  name="bcc"
                  inputMode="email"
                  value={bccEmails}
                  onChange={(event) => onFieldChange("bccEmails", event.currentTarget.value)}
                  placeholder="discret@example.com"
                  className="h-11 rounded-xl border border-border bg-bg px-3 text-[14px] text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
                />
              </label>
            </div>
          )}

          <label className="grid gap-1.5 text-[12px] text-text-muted" htmlFor="new-message-subject">
            <span>Sujet</span>
            <input
              id="new-message-subject"
              name="subject"
              value={subject}
              onChange={(event) => onFieldChange("subject", event.currentTarget.value)}
              placeholder="Sujet"
              className="h-11 rounded-xl border border-border bg-bg px-3 text-[14px] text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            />
          </label>

          <label className="grid gap-1.5 text-[12px] text-text-muted" htmlFor="new-message-body">
            <span>Corps</span>
            <textarea
              id="new-message-body"
              name="body"
              value={body}
              onChange={(event) => onFieldChange("body", event.currentTarget.value)}
              rows={6}
              placeholder="Écris ton message…"
              className="min-h-[148px] rounded-xl border border-border bg-bg px-3 py-2 text-[14px] text-text resize-y focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            />
          </label>

          <div className="grid gap-2">
            <input
              id="new-message-attachments"
              name="attachments"
              type="file"
              multiple
              className="sr-only"
              onChange={(event) => {
                onFilesSelected(event.currentTarget.files);
                event.currentTarget.value = "";
              }}
            />
            <label
              htmlFor="new-message-attachments"
              className="inline-flex min-h-11 w-fit cursor-pointer items-center gap-2 rounded-xl border border-border bg-bg-e2 px-3 text-[13px] text-text-muted hover:bg-bg-e3 focus-within:outline focus-within:outline-2 focus-within:outline-accent"
            >
              <span aria-hidden="true">📎</span>
              <span>Pièce jointe</span>
            </label>

            {attachments.length > 0 && (
              <div className="flex flex-wrap gap-2" aria-label="Pièces jointes sélectionnées">
                {attachments.map((attachment) => (
                  <span
                    key={attachment.id}
                    className="inline-flex min-h-9 max-w-full items-center gap-2 rounded-xl border border-border bg-bg px-2.5 py-1 text-[12px] text-text"
                  >
                    <span className="max-w-[180px] truncate" title={attachment.name}>{attachment.name}</span>
                    <span className="shrink-0 text-text-dim">{formatAttachmentSize(attachment.size)}</span>
                    <button
                      type="button"
                      onClick={() => onRemoveAttachment(attachment.id)}
                      className="grid h-7 w-7 place-items-center rounded-lg text-text-muted hover:bg-bg-e3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
                      aria-label={`Retirer ${attachment.name}`}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {errorMessage && <p role="alert" className="rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-[12px] text-red-200">{errorMessage}</p>}
          {!canSend && <p className="text-[12px] text-text-dim">Saisis une adresse email valide et un message. Vérifie aussi Cc/Cci et les fichiers de 25 Mo max.</p>}

          <div className="flex items-center justify-between gap-3 pt-1">
            <p className="text-[11px] text-text-dim">Cmd/Ctrl + Enter pour envoyer</p>
            <button
              type="submit"
              disabled={!canSend}
              className="h-11 min-w-28 rounded-xl bg-accent px-4 text-[13px] font-semibold text-bg disabled:opacity-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            >
              {isSending ? "Envoi…" : "Envoyer"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

function ReadonlyLine({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid gap-1.5 text-[12px] text-text-muted">
      <span>{label}</span>
      <div className="min-h-11 rounded-xl border border-border bg-bg-e2 px-3 py-2 text-[14px] text-text flex items-center">
        {value}
      </div>
    </div>
  );
}
