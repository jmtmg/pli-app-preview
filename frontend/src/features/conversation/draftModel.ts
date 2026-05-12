import type { Message } from "@/api/queries";

export interface DraftPayload {
  account_id: string;
  contact_id: string;
  subject: string;
  body_text: string;
  cc_emails: string[];
  signature_active: boolean;
}

export interface ReplyCcState {
  visible: boolean;
  emails: string[];
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

export function getReplyCcCandidates(messages: Message[] | undefined): string[] {
  const lastIncomingWithCc = [...(messages ?? [])]
    .reverse()
    .find((message) => message.direction === "in" && message.cc_emails.length > 0);
  return lastIncomingWithCc ? [...lastIncomingWithCc.cc_emails] : [];
}

export function buildReplyCcState(messages: Message[] | undefined): ReplyCcState {
  const emails = getReplyCcCandidates(messages);
  return { visible: emails.length > 0, emails };
}

export function buildSignedBody({
  body,
  signature,
  signatureActive,
}: {
  body: string;
  signature: string | null | undefined;
  signatureActive: boolean;
}): string {
  const cleanSignature = (signature ?? "").trim();
  if (!signatureActive || !cleanSignature) return body;
  return `${body.trimEnd()}\n\n${cleanSignature}`;
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
  ccEmails = [],
}: {
  accountId: string;
  contactId: string;
  subject: string;
  body: string;
  signatureActive: boolean;
  ccEmails?: string[];
}): DraftPayload {
  return {
    account_id: accountId,
    contact_id: contactId,
    subject,
    body_text: body,
    cc_emails: ccEmails,
    signature_active: signatureActive,
  };
}
