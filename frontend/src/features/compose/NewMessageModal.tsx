import { useEffect, useState, type FormEvent, type KeyboardEvent } from "react";
import type { Account, Conversation } from "@/api/queries";
import { useConversations, useSendMessage } from "@/api/queries";
import {
  buildNewMessagePayload,
  canSendNewMessage,
  filterRecipientSuggestions,
  getRecipientLabel,
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
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const conversations = data?.pages.flatMap((page) => page.items) ?? [];

  useEffect(() => {
    if (!open) {
      setToEmail("");
      setSelectedContactId(null);
      setSubject("");
      setBody("");
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
          subject,
          body,
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
      subject={subject}
      body={body}
      isSending={sendMessage.isPending}
      errorMessage={errorMessage}
      onClose={onClose}
      onFieldChange={(field, value) => {
        if (field === "toEmail") {
          setToEmail(value);
          setSelectedContactId(null);
        }
        if (field === "subject") setSubject(value);
        if (field === "body") setBody(value);
      }}
      onSelectRecipient={(conversation) => {
        setToEmail(conversation.email);
        setSelectedContactId(conversation.contact_id);
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
  subject: string;
  body: string;
  isSending: boolean;
  errorMessage: string | null;
  onClose: () => void;
  onFieldChange: (field: "toEmail" | "subject" | "body", value: string) => void;
  onSelectRecipient: (conversation: Conversation) => void;
  onSubmit: () => void;
}

export function NewMessageModalView({
  open,
  account,
  conversations,
  selectedContactId,
  toEmail,
  subject,
  body,
  isSending,
  errorMessage,
  onClose,
  onFieldChange,
  onSelectRecipient,
  onSubmit,
}: NewMessageModalViewProps) {
  if (!open) return null;
  const suggestions = filterRecipientSuggestions(conversations, toEmail, 5);
  const canSend = canSendNewMessage({
    accountId: account?.id ?? null,
    toEmail,
    body,
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

          <label className="grid gap-1.5 text-[12px] text-text-muted" htmlFor="new-message-to">
            <span>À</span>
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
          </label>

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

          {errorMessage && <p role="alert" className="rounded-xl border border-red-500/30 bg-red-500/10 px-3 py-2 text-[12px] text-red-200">{errorMessage}</p>}
          {!canSend && <p className="text-[12px] text-text-dim">Saisis une adresse email valide et un message.</p>}

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
