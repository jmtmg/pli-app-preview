import type { Conversation } from "@/api/queries";

export interface NewMessageDraft {
  accountId: string | null;
  selectedContactId: string | null;
  toEmail: string;
  subject: string;
  body: string;
}

export interface NewMessageSendGuard {
  accountId: string | null;
  toEmail: string;
  body: string;
  isPending: boolean;
}

export function filterRecipientSuggestions(
  conversations: Conversation[],
  query: string,
  limit = 5,
): Conversation[] {
  const q = query.trim().toLowerCase();
  if (!q) return conversations.slice(0, limit);
  return conversations
    .filter((conversation) => {
      const haystack = [conversation.display_name, conversation.email, conversation.email_normalized]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      return haystack.includes(q);
    })
    .slice(0, limit);
}

export function getRecipientLabel(conversation: Conversation): string {
  const name = conversation.display_name?.trim();
  return name ? `${name} — ${conversation.email}` : conversation.email;
}

export function isValidEmail(value: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

export function canSendNewMessage({
  accountId,
  toEmail,
  body,
  isPending,
}: NewMessageSendGuard): boolean {
  return Boolean(accountId && isValidEmail(toEmail) && body.trim() && !isPending);
}

export function buildNewMessagePayload(draft: NewMessageDraft) {
  const subject = draft.subject.trim();
  const body = draft.body.trim();
  const base = {
    account_id: draft.accountId ?? "",
    subject: subject || undefined,
    body,
  };
  if (draft.selectedContactId) {
    return { ...base, contact_id: draft.selectedContactId };
  }
  return { ...base, to_email: draft.toEmail.trim() };
}
