/**
 * Bulle de message — entrant / sortant.
 * Sprint 2 · FE — owner : FE.
 * Sujet affiché uniquement quand il diffère de la bulle précédente
 * (logique gérée côté liste — TODO Sprint 2).
 *
 * Réf. wireframes 03-Wireframes.md §3.3 (écran B) :
 *   - max-width 78 % desktop, 88 % mobile
 *   - radius 18 / coin court 6
 */
import clsx from "clsx";

export interface Msg {
  id: string;
  direction: "in" | "out";
  subject: string | null;
  body_snippet: string;
  sent_at: number;
  has_attachments?: boolean;
}

interface Props {
  msg: Msg;
}

export function MessageBubble({ msg }: Props) {
  const out = msg.direction === "out";
  return (
    <div className={clsx("flex flex-col gap-1", out ? "items-end" : "items-start")}>
      {msg.subject && (
        <div className="text-[11px] text-text-dim uppercase tracking-wide px-1">
          {msg.subject}
        </div>
      )}
      <div
        className={clsx(
          "max-w-[88%] md:max-w-[78%] px-3.5 py-2.5 text-[14px] leading-snug whitespace-pre-wrap break-words",
          "rounded-[18px] border",
          out
            ? "bg-bubble-out border-accent/20 rounded-br-md"
            : "bg-bubble-in border-border rounded-bl-md",
        )}
      >
        {msg.body_snippet}
        {msg.has_attachments && (
          <div className="mt-1.5 text-[11px] text-text-dim flex items-center gap-1">
            <span>📎</span> pièce jointe
          </div>
        )}
      </div>
      <div className="text-[10px] text-text-dim px-1">{formatStamp(msg.sent_at)}</div>
    </div>
  );
}

function formatStamp(ts: number): string {
  const d = new Date(ts * 1000);
  return d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}
