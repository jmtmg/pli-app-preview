/**
 * Ligne de conversation dans la liste — US-1.7 Sprint 1.
 *
 * Affiche : avatar + nom/email, preview, timestamp relatif, badge non-lus,
 * icones pin + piece jointe. Le swipe bilateral (seuils 33 % / 15 %) est
 * a implementer via `@use-gesture/react` en Sprint 4.
 *
 * Accessibilite : bouton semantique, role="listitem" sur le wrapper,
 * aria-label compose des infos critiques (non-lus, nom, timestamp) pour
 * lecteurs d'ecran. Cibles pointer >= 44 px (WCAG 2.5.5).
 */
import clsx from "clsx";
import type { Conversation } from "@/api/queries";
import { Avatar } from "@/components/Avatar";

interface Props {
  conv: Conversation;
  selected: boolean;
  onClick: () => void;
}

export function ConversationRow({ conv, selected, onClick }: Props) {
  const displayName = conv.display_name ?? conv.email;
  const hasUnread = conv.unread_count > 0;
  const timestampLabel = formatRelativeTime(conv.last_msg_at);

  // aria-label concis et ordonne : etat > emetteur > moment > apercu
  const ariaLabel = [
    hasUnread ? `${conv.unread_count} message${conv.unread_count > 1 ? "s" : ""} non lus de` : "",
    displayName,
    timestampLabel ? `le ${timestampLabel}` : "",
    conv.has_attachments ? "avec piece jointe" : "",
    conv.is_pinned ? "epinglee" : "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      role="listitem"
      className={clsx(
        "relative border-b border-border",
        conv.is_pinned &&
          "before:content-[''] before:absolute before:inset-y-0 before:left-0 before:w-0.5 before:bg-accent/50",
      )}
    >
      <button
        type="button"
        onClick={onClick}
        aria-label={ariaLabel}
        aria-current={selected ? "true" : undefined}
        className={clsx(
          "w-full grid grid-cols-[48px_1fr_auto] gap-3 px-3.5 py-3 items-center text-left transition-colors min-h-[64px]",
          "hover:bg-bg-e3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent",
          conv.is_pinned ? "bg-bg-pinned" : "bg-bg",
          selected && "bg-bg-e3",
        )}
      >
        <Avatar initials={displayName.slice(0, 2).toUpperCase()} />
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <span
              className={clsx(
                "truncate text-[15px]",
                hasUnread ? "font-semibold text-text" : "font-medium text-text",
              )}
            >
              {displayName}
            </span>
          </div>
          <div
            className={clsx(
              "truncate text-[13px] mt-0.5",
              hasUnread ? "text-text" : "text-text-muted",
            )}
          >
            {conv.last_preview ?? <span className="italic text-text-dim">(aucun message)</span>}
          </div>
        </div>
        <div className="flex flex-col items-end gap-1 shrink-0">
          {timestampLabel && (
            <time
              dateTime={conv.last_msg_at ?? undefined}
              className="text-[11px] text-text-dim"
            >
              {timestampLabel}
            </time>
          )}
          <div className="flex items-center gap-1.5">
            {conv.has_attachments && (
              <span className="text-text-dim text-[11px]" aria-hidden>
                {ICON_ATTACHMENT}
              </span>
            )}
            {hasUnread && (
              <span
                className="min-w-[18px] h-[18px] px-1.5 rounded-full bg-accent text-[11px] font-bold text-[#0b0b0c] text-center leading-[18px]"
                aria-hidden
              >
                {conv.unread_count > 99 ? "99+" : conv.unread_count}
              </span>
            )}
            {conv.is_pinned && (
              <span className="text-accent/80 text-[11px]" aria-hidden>
                {ICON_PIN}
              </span>
            )}
          </div>
        </div>
      </button>
    </div>
  );
}

// Icones : emojis discrets plutot que charger lucide-react en M1.
const ICON_ATTACHMENT = "📎";
const ICON_PIN = "📌";

/** Formate un timestamp ISO en libelle relatif court — meme regle que le
 *  mock HTML (`Mail/index.html`) : aujourd'hui = HH:MM, hier = "Hier",
 *  cette semaine = "lun.", sinon = "5 avr.". Tolere null (aucun message). */
export function formatRelativeTime(iso: string | null): string {
  if (!iso) return "";
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "";

  const now = new Date();
  const sameDay = d.toDateString() === now.toDateString();
  if (sameDay) {
    return d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
  }
  const oneDay = 24 * 3600 * 1000;
  const diff = now.getTime() - d.getTime();
  if (diff < 2 * oneDay) return "Hier";
  if (diff < 7 * oneDay) return d.toLocaleDateString("fr-FR", { weekday: "short" });
  return d.toLocaleDateString("fr-FR", { day: "numeric", month: "short" });
}
