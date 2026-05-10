import type { Message } from "@/api/queries";

export interface DraftPayload {
  account_id: string;
  contact_id: string;
  subject: string;
  body_text: string;
  signature_active: boolean;
}

export function getDefaultReplySubject(messages: Message[] | undefined): string {
  const lastSubject = [...(messages ?? [])]
    .reverse()
    .map((message) => message.subject?.trim())
    .find((subject): subject is string => !!subject);
  if (!lastSubject) return "RE: réponse en cours";
  if (/^re\s*:/i.test(lastSubject)) return lastSubject;
  return `RE: ${lastSubject}`;
}

export function shouldSaveDraft({ subject, body }: { subject: string; body: string }): boolean {
  return Boolean(subject.trim() || body.trim());
}

export function canSendComposer({
  body,
  sendPending,
  savePending,
}: {
  body: string;
  sendPending: boolean;
  savePending: boolean;
}): boolean {
  return Boolean(body.trim()) && !sendPending && !savePending;
}

export function isCurrentDraftGeneration({
  scheduledGeneration,
  currentGeneration,
}: {
  scheduledGeneration: number;
  currentGeneration: number;
}): boolean {
  return scheduledGeneration === currentGeneration;
}

export function getComposerInstanceKey(accountId: string | null, contactId: string): string {
  return `${accountId ?? "pending-account"}:${contactId}`;
}

export function buildDraftPayload({
  accountId,
  contactId,
  subject,
  body,
  signatureActive,
}: {
  accountId: string;
  contactId: string;
  subject: string;
  body: string;
  signatureActive: boolean;
}): DraftPayload {
  return {
    account_id: accountId,
    contact_id: contactId,
    subject,
    body_text: body,
    signature_active: signatureActive,
  };
}
