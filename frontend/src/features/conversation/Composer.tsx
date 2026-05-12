/**
 * Composer inline — pied de pane conversation.
 *
 * P0 Cowork couvert ici : textarea auto-resize, sujet RE éditable via bottom
 * sheet, brouillon local autosauvegardé toutes les 3 s, raccourci Cmd/Ctrl+Entrée.
 */
import { useEffect, useMemo, useRef, useState } from "react";
import type { Message } from "@/api/queries";
import { useAccounts, useDeleteDraft, useDraft, useSaveDraft, useSendMessage } from "@/api/queries";
import {
  buildDraftPayload,
  buildReplyCcState,
  buildSignedBody,
  canSendComposer,
  getComposerInstanceKey,
  getDefaultReplySubject,
  isCurrentDraftGeneration,
} from "./draftModel";

interface Props {
  accountId: string | null;
  contactId: string;
  messages?: Message[];
}

export function Composer(props: Props) {
  return <ComposerInner key={getComposerInstanceKey(props.accountId, props.contactId)} {...props} />;
}

function ComposerInner({ accountId, contactId, messages }: Props) {
  const defaultSubject = useMemo(() => getDefaultReplySubject(messages), [messages]);
  const defaultCcState = useMemo(() => buildReplyCcState(messages), [messages]);
  const [body, setBody] = useState("");
  const [subject, setSubject] = useState(defaultSubject);
  const [signatureActive, setSignatureActive] = useState(true);
  const [ccVisible, setCcVisible] = useState(defaultCcState.visible);
  const [ccEmails, setCcEmails] = useState<string[]>(defaultCcState.emails);
  const [subjectSheetOpen, setSubjectSheetOpen] = useState(false);
  const [draftId, setDraftId] = useState<string | null>(null);
  const [savedNotice, setSavedNotice] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);
  const subjectInputRef = useRef<HTMLInputElement>(null);
  const validateButtonRef = useRef<HTMLButtonElement>(null);
  const hydratedKeyRef = useRef<string | null>(null);
  const draftGenerationRef = useRef(0);
  const send = useSendMessage();
  const draft = useDraft(accountId, contactId);
  const saveDraft = useSaveDraft();
  const deleteDraft = useDeleteDraft();
  const accounts = useAccounts();
  const accountSignature = accounts.data?.find((account) => account.id === accountId)?.signature ?? null;
  const signatureLabel = accountSignature ? "Compte" : "off";
  const composerKey = accountId ? `${accountId}:${contactId}` : null;

  useEffect(() => {
    if (!composerKey || !messages || draft.isLoading || hydratedKeyRef.current === composerKey) return;
    hydratedKeyRef.current = composerKey;
    if (draft.data) {
      setDraftId(draft.data.id);
      setBody(draft.data.body_text);
      setSubject(draft.data.subject ?? defaultSubject);
      setCcEmails(draft.data.cc_emails);
      setCcVisible(draft.data.cc_emails.length > 0 || defaultCcState.visible);
      setSignatureActive(draft.data.signature_active);
      setSavedNotice("Brouillon repris");
      return;
    }
    setDraftId(null);
    setBody("");
    setSubject(defaultSubject);
    setCcEmails(defaultCcState.emails);
    setCcVisible(defaultCcState.visible);
    setSignatureActive(true);
    setSavedNotice("");
  }, [composerKey, defaultCcState, defaultSubject, draft.data, draft.isLoading, messages]);

  // Auto-resize : croît jusqu'à ~6 lignes puis devient scrollable.
  useEffect(() => {
    if (!ref.current) return;
    ref.current.style.height = "auto";
    ref.current.style.height = `${Math.min(ref.current.scrollHeight, 160)}px`;
  }, [body]);

  // Autosave Cowork : toutes les 3 s, un brouillon local par conversation.
  useEffect(() => {
    if (!accountId || !contactId) return;
    const subjectChanged = subject.trim() !== defaultSubject.trim();
    if (!body.trim() && !subjectChanged) return;
    const generation = draftGenerationRef.current;
    const timer = window.setTimeout(() => {
      if (
        !isCurrentDraftGeneration({
          scheduledGeneration: generation,
          currentGeneration: draftGenerationRef.current,
        })
      ) {
        return;
      }
      saveDraft.mutate(
        buildDraftPayload({
          accountId,
          contactId,
          subject,
          body,
          ccEmails: ccVisible ? ccEmails : [],
          signatureActive,
        }),
        {
          onSuccess: (saved) => {
            if (
              !isCurrentDraftGeneration({
                scheduledGeneration: generation,
                currentGeneration: draftGenerationRef.current,
              })
            ) {
              return;
            }
            setDraftId(saved.id);
            setSavedNotice("Brouillon sauvegardé");
          },
        },
      );
    }, 3_000);
    return () => window.clearTimeout(timer);
  }, [accountId, body, ccEmails, ccVisible, contactId, defaultSubject, saveDraft, signatureActive, subject]);

  useEffect(() => {
    if (!subjectSheetOpen) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        setSubjectSheetOpen(false);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [subjectSheetOpen]);

  function handleSend() {
    if (!canSendComposer({ body, sendPending: send.isPending, savePending: saveDraft.isPending })) return;
    draftGenerationRef.current += 1;
    const signedBody = buildSignedBody({ body, signature: accountSignature, signatureActive });
    send.mutate(
      {
        account_id: accountId ?? undefined,
        contact_id: contactId,
        body: signedBody,
        subject,
        cc_emails: ccVisible ? ccEmails : [],
      },
      {
        onSuccess: () => {
          setBody("");
          setSubject(defaultSubject);
          setCcEmails(defaultCcState.emails);
          setCcVisible(defaultCcState.visible);
          setSavedNotice("");
          if (draftId && accountId) {
            deleteDraft.mutate({ id: draftId, accountId, contactId });
          }
          setDraftId(null);
        },
      },
    );
  }

  function handleKey(e: React.KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  }

  function trapSubjectSheetFocus(event: React.KeyboardEvent<HTMLDivElement>) {
    if (event.key !== "Tab") return;
    const first = subjectInputRef.current;
    const last = validateButtonRef.current;
    if (!first || !last) return;
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  return (
    <div className="border-t border-border bg-bg" style={{ paddingBottom: "var(--safe-bottom)" }}>
      <div className="px-3 py-1.5 text-[11px] text-text-dim border-b border-border flex items-center gap-1.5 min-h-[44px]">
        <button
          type="button"
          onClick={() => setSubjectSheetOpen(true)}
          className="min-h-11 min-w-0 flex-1 text-left truncate rounded-lg px-1.5 hover:bg-bg-e3 active:bg-bg-e2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          aria-label="Modifier le sujet du message"
        >
          ↳ <span className="text-text-muted">{subject || "Sans sujet"}</span>
        </button>
        {(defaultCcState.visible || ccVisible) && (
          <button
            type="button"
            onClick={() => setCcVisible((value) => !value)}
            className="min-h-11 rounded-lg px-2 hover:bg-bg-e3 active:bg-bg-e2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            aria-pressed={ccVisible}
            aria-label="Inclure ou retirer les destinataires en copie du dernier message"
          >
            Cc <span className="text-text-muted">{ccVisible ? ccEmails.length : "off"}</span>
          </button>
        )}
        <button
          type="button"
          onClick={() => setSignatureActive((value) => !value)}
          className="min-h-11 rounded-lg px-2 hover:bg-bg-e3 active:bg-bg-e2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          aria-pressed={signatureActive}
          aria-label="Activer ou désactiver la signature du compte"
        >
          Sig. <span className="text-text-muted">{signatureActive ? signatureLabel : "off"}</span>
        </button>
        <span className="hidden sm:inline truncate">
          De <span className="text-text-muted">demo@pli-app.fr</span>
        </span>
      </div>

      {ccVisible && ccEmails.length > 0 && (
        <div className="px-3 pt-2 text-[11px] text-text-dim flex flex-wrap items-center gap-1.5">
          <span className="font-medium text-text-muted">Cc</span>
          {ccEmails.map((email) => (
            <span key={email} className="rounded-full border border-border px-2 py-1">
              {email}
            </span>
          ))}
        </div>
      )}

      <div className="px-3 py-2 flex items-end gap-2">
        <button
          type="button"
          className="w-11 h-11 rounded-full hover:bg-bg-e3 active:bg-bg-e2 flex items-center justify-center text-text-muted transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          aria-label="Ajouter une pièce jointe"
          title="Pièces jointes — à câbler"
        >
          📎
        </button>
        <textarea
          ref={ref}
          value={body}
          onChange={(e) => setBody(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Message"
          rows={1}
          className="flex-1 resize-none bg-bg-e2 rounded-2xl px-3.5 py-2.5 text-[14px] placeholder:text-text-dim border border-transparent focus:border-border-strong focus:outline-none max-h-[100px]"
        />
        <button
          onClick={handleSend}
          disabled={!canSendComposer({ body, sendPending: send.isPending, savePending: saveDraft.isPending })}
          className="w-11 h-11 rounded-full bg-accent text-[#0b0b0c] text-[17px] font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-opacity flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          title="Envoyer (Cmd/Ctrl + Entrée)"
          aria-label="Envoyer le message"
        >
          {send.isPending ? "…" : "→"}
        </button>
      </div>

      <div className="px-3 pb-1 min-h-5 text-[11px] text-text-dim">
        {saveDraft.isPending ? "Sauvegarde…" : savedNotice}
      </div>

      {subjectSheetOpen && (
        <div
          className="fixed inset-0 z-50 flex items-end bg-black/50"
          role="presentation"
          onClick={() => setSubjectSheetOpen(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Modifier le sujet"
            className="w-full rounded-t-[24px] border border-border bg-bg-e2 p-4 shadow-2xl"
            onClick={(event) => event.stopPropagation()}
            onKeyDown={trapSubjectSheetFocus}
          >
            <div className="mx-auto mb-3 h-1 w-10 rounded-full bg-border-strong" />
            <label className="block text-[13px] font-semibold text-text" htmlFor="composer-subject">
              Sujet du message
            </label>
            <input
              ref={subjectInputRef}
              id="composer-subject"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              className="mt-2 w-full rounded-2xl border border-border bg-bg px-3.5 py-3 text-[15px] outline-none focus:border-accent"
              placeholder="RE: dernier sujet"
              autoFocus
            />
            <div className="mt-4 flex gap-2">
              <button
                type="button"
                onClick={() => setSubject(defaultSubject)}
                className="min-h-11 flex-1 rounded-2xl border border-border px-4 text-[14px] text-text-muted"
              >
                Réinitialiser
              </button>
              <button
                ref={validateButtonRef}
                type="button"
                onClick={() => setSubjectSheetOpen(false)}
                className="min-h-11 flex-1 rounded-2xl bg-accent px-4 text-[14px] font-semibold text-[#0b0b0c]"
              >
                Valider
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
