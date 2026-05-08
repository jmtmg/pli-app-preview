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
      <div className="px-3 py-1.5 text-[11px] text-text-dim border-b border-border truncate">
        ↳ <span className="text-text-muted">RE: réponse en cours</span>
        <span className="mx-1.5">·</span>
        Sig. <span className="text-text-muted">Démo</span>
        <span className="mx-1.5">·</span>
        De <span className="text-text-muted">demo@pli-app.fr</span>
      </div>
      <div className="px-3 py-2 flex items-end gap-2">
        <button
          type="button"
          className="w-10 h-10 rounded-full hover:bg-bg-e3 active:bg-bg-e2 flex items-center justify-center text-text-muted transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          aria-label="Ajouter une pièce jointe"
          title="Pièces jointes — à câbler"
        >
          📎
        </button>
        <textarea
          ref={ref}
          value={body}
          onChange={e => setBody(e.target.value)}
          onKeyDown={handleKey}
          placeholder="Message"
          rows={1}
          className="flex-1 resize-none bg-bg-e2 rounded-2xl px-3.5 py-2.5 text-[14px] placeholder:text-text-dim border border-transparent focus:border-border-strong focus:outline-none max-h-[100px]"
        />
        <button
          onClick={handleSend}
          disabled={!body.trim() || send.isPending}
          className="w-10 h-10 rounded-full bg-accent text-[#0b0b0c] text-[17px] font-semibold disabled:opacity-40 disabled:cursor-not-allowed transition-opacity flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
          title="Envoyer (Cmd/Ctrl + Entrée)"
          aria-label="Envoyer le message"
        >
          {send.isPending ? "…" : "→"}
        </button>
      </div>
    </div>
  );
}
