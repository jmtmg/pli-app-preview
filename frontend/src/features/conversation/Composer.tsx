/**
 * Composer inline — pied de pane conversation.
 * Sprint 3 · FE — owner : FE.
 *
 * P0 :
 *   - textarea auto-resize
 *   - méta-bar : "Sujet : <réponse> · De : <compte>"
 *   - bouton Envoyer (Cmd/Ctrl + Entrée)
 *   - sauvegarde brouillon toutes les 30 s (TODO Sprint 3 BE)
 */
import { useEffect, useRef, useState } from "react";
import { useSendMessage } from "@/api/queries";

interface Props {
  contactId: string;
}

export function Composer({ contactId }: Props) {
  const [body, setBody] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);
  const send = useSendMessage();

  // Auto-resize : croît jusqu'à ~6 lignes puis devient scrollable.
  useEffect(() => {
    if (!ref.current) return;
    ref.current.style.height = "auto";
    ref.current.style.height = `${Math.min(ref.current.scrollHeight, 160)}px`;
  }, [body]);

  function handleSend() {
    if (!body.trim()) return;
    send.mutate({ contact_id: contactId, body });
    setBody("");
  }

  function handleKey(e: React.KeyboardEvent) {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="border-t border-border bg-bg" style={{ paddingBottom: "var(--safe-bottom)" }}>
      <div className="px-3 py-1.5 text-[11px] text-text-dim border-b border-border">
        Sujet : <span className="text-text-muted">réponse en cours</span>
        <span className="mx-1.5">·</span>
        De : <span className="text-text-muted">jms2b99@gmail.com</span>
      </div>
      <div className="px-3 py-2 flex items-end gap-2">
        <textarea
          ref={ref}
          value={body}
          onChange={e => setBody(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Écrire un message…"
          rows={1}
          className="flex-1 resize-none bg-bg-e2 rounded-2xl px-3 py-2 text-[14px] placeholder:text-text-dim border border-transparent focus:border-border-strong focus:outline-none"
        />
        <button
          onClick={handleSend}
          disabled={!body.trim() || send.isPending}
          className="h-9 px-4 rounded-full bg-accent text-[#0b0b0c] text-[13px] font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-opacity"
          title="Envoyer (Cmd/Ctrl + Entrée)"
        >
          {send.isPending ? "…" : "Envoyer"}
        </button>
      </div>
    </div>
  );
}
