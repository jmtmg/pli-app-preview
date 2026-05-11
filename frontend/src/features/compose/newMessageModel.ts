import type { Conversation } from "@/api/queries";

export const MAX_LOCAL_ATTACHMENT_BYTES = 25 * 1024 * 1024;

export interface NewMessageAttachment {
  id: string;
  name: string;
  type: string;
  size: number;
}

export interface NewMessageDraft {
  accountId: string | null;
  selectedContactId: string | null;
  toEmail: string;
  ccEmails: string;
  bccEmails: string;
  subject: string;
  body: string;
  attachments: NewMessageAttachment[];
}

export interface NewMessageSendGuard {
  accountId: string | null;
  toEmail: string;
  ccEmails: string;
  bccEmails: string;
  body: string;
  attachments: NewMessageAttachment[];
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

export function parseEmailList(value: string): string[] {
  return value
    .split(/[\s,;]+/)
    .map((email) => email.trim())
    .filter(Boolean);
}

export function areValidOptionalEmails(value: string): boolean {
  return parseEmailList(value).every(isValidEmail);
}

export function areLocalAttachmentsValid(attachments: NewMessageAttachment[]): boolean {
  return attachments.every((attachment) => (
    attachment.name.trim().length > 0
    && attachment.size >= 0
    && attachment.size <= MAX_LOCAL_ATTACHMENT_BYTES
  ));
}

export function formatAttachmentSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} o`;
  if (bytes < 1024 * 1024) return `${Math.round(bytes / 1024)} Ko`;
  const megabytes = bytes / (1024 * 1024);
  return `${Number(megabytes.toFixed(megabytes < 10 ? 1 : 0))} Mo`;
}

function createAttachmentId(): string {
  const randomId = typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : `${Date.now()}-${Math.random().toString(36).slice(2)}`;
  return `local-att-${randomId}`;
}

export function fileToLocalAttachment(file: File, id = createAttachmentId()): NewMessageAttachment {
  return {
    id,
    name: file.name,
    type: file.type,
    size: file.size,
  };
}

export function canSendNewMessage({
  accountId,
  toEmail,
  ccEmails,
  bccEmails,
  body,
  attachments,
  isPending,
}: NewMessageSendGuard): boolean {
  return Boolean(
    accountId
      && isValidEmail(toEmail)
      && areValidOptionalEmails(ccEmails)
      && areValidOptionalEmails(bccEmails)
      && areLocalAttachmentsValid(attachments)
      && body.trim()
      && !isPending,
  );
}

export function buildNewMessagePayload(draft: NewMessageDraft) {
  const subject = draft.subject.trim();
  const body = draft.body.trim();
  const ccEmails = parseEmailList(draft.ccEmails);
  const bccEmails = parseEmailList(draft.bccEmails);
  const attachments = draft.attachments.map((attachment) => ({
    filename: attachment.name,
    mime_type: attachment.type || undefined,
    size_bytes: attachment.size,
  }));
  const base = {
    account_id: draft.accountId ?? "",
    ...(ccEmails.length > 0 ? { cc_emails: ccEmails } : {}),
    ...(bccEmails.length > 0 ? { bcc_emails: bccEmails } : {}),
    subject: subject || undefined,
    body,
    ...(attachments.length > 0 ? { attachments } : {}),
  };
  if (draft.selectedContactId) {
    return { ...base, contact_id: draft.selectedContactId };
  }
  return { ...base, to_email: draft.toEmail.trim() };
}
