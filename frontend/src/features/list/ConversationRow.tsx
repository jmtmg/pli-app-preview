/**
 * Ligne de conversation dans la liste — US-1.7 Sprint 1.
 *
 * Affiche : avatar + nom/email, preview, timestamp relatif, badge non-lus,
 * icones pin + piece jointe. Le swipe bilateral revele les mêmes actions des
 * deux côtés avec seuil Cowork 33 % / fermeture 18 %, pilote par le parent pour
 * garantir un seul panneau ouvert à la fois.
 *
 * Accessibilite : bouton semantique, role="listitem" sur le wrapper,
 * aria-label compose des infos critiques (non-lus, nom, timestamp) pour
 * lecteurs d'ecran. Cibles pointer >= 44 px (WCAG 2.5.5).
 */
import { useEffect, useRef, useState } from "react";
import { useDrag } from "@use-gesture/react";
import clsx from "clsx";
import type { Conversation } from "@/api/queries";
import { Avatar } from "@/components/Avatar";
import { getSwipePanelState, type QuickAction, type SwipeSide } from "./quickActions";

interface Props {
  conv: Conversation;
  selected: boolean;
  actions: QuickAction[];
  swipeOpen: boolean;
  onClick: () => void;
  onOpenActions: () => void;
  onQuickAction: (action: QuickAction) => void;
  onSwipeOpen: (side: SwipeSide) => void;
  onSwipeClose: () => void;
}

const REVEAL_WIDTH = 228;

export function ConversationRow({
  conv,
  selected,
  actions,
  swipeOpen,
  onClick,
  onOpenActions,
  onQuickAction,
  onSwipeOpen,
  onSwipeClose,
}: Props) {
  const displayName = conv.display_name ?? conv.email;
  const hasUnread = conv.unread_count > 0;
  const timestampLabel = formatRelativeTime(conv.last_msg_at);
  const rowRef = useRef<HTMLDivElement | null>(null);
  const [dragX, setDragX] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [openSide, setOpenSide] = useState<SwipeSide | null>(null);

  useEffect(() => {
    if (!swipeOpen) {
      setDragX(0);
      setOpenSide(null);
    }
  }, [swipeOpen]);

  const bind = useDrag(
    ({ down, movement: [mx], tap }) => {
      if (tap) return;
      const width = rowRef.current?.offsetWidth ?? 0;
      setDragging(down);

      if (down) {
        setDragX(clamp(mx, -REVEAL_WIDTH, REVEAL_WIDTH));
        return;
      }

      const state = getSwipePanelState({ dragOffset: mx, rowWidth: width, wasOpen: swipeOpen });
      if (state.open && state.side) {
        setOpenSide(state.side);
        setDragX(state.side === "left" ? -REVEAL_WIDTH : REVEAL_WIDTH);
        onSwipeOpen(state.side);
      } else {
        setOpenSide(null);
        setDragX(0);
        onSwipeClose();
      }
    },
    { axis: "x", filterTaps: true, pointer: { touch: true } },
  );

  // aria-label concis et ordonne : etat > emetteur > moment > apercu
  const ariaLabel = [
    hasUnread ? `${conv.unread_count} message${conv.unread_count > 1 ? "s" : ""} non lus de` : "",
    displayName,
    timestampLabel ? `le ${timestampLabel}` : "",
    conv.has_attachments ? "avec piece jointe" : "",
    conv.is_pinned ? "epinglee" : "",
    conv.is_muted ? "silencieuse" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const activeSide = openSide ?? (dragX < 0 ? "left" : dragX > 0 ? "right" : null);

  return (
    <div
      role="listitem"
      ref={rowRef}
      className={clsx(
        "relative overflow-hidden border-b border-border touch-pan-y",
        conv.is_pinned &&
          "before:content-[''] before:absolute before:inset-y-0 before:left-0 before:z-20 before:w-0.5 before:bg-accent/50",
      )}
      {...bind()}
    >
      <ActionRail
        side="left"
        active={activeSide === "right"}
        actions={actions}
        onQuickAction={onQuickAction}
      />
      <ActionRail
        side="right"
        active={activeSide === "left"}
        actions={actions}
        onQuickAction={onQuickAction}
      />

      <div
        className={clsx("relative z-10 grid grid-cols-[1fr_44px]", !dragging && "transition-transform duration-200 ease-ios")}
        style={{ transform: `translateX(${dragX}px)` }}
      >
        <button
          type="button"
          onClick={() => {
            if (swipeOpen) {
              onSwipeClose();
              return;
            }
            onClick();
          }}
          aria-label={ariaLabel}
          aria-current={selected ? "true" : undefined}
          className={clsx(
            "w-full grid grid-cols-[48px_1fr_auto] gap-3 px-3.5 py-3 items-center text-left transition-colors min-h-[68px]",
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
              {conv.is_muted && (
                <span className="text-text-dim text-[11px]" aria-hidden>
                  {ICON_MUTED}
                </span>
              )}
              {conv.has_attachments && (
                <span className="text-text-dim text-[11px]" aria-hidden>
                  {ICON_ATTACHMENT}
                </span>
              )}
              {hasUnread && (
                <span
                  className="min-w-[18px] h-[18px] px-1.5 rounded-full bg-unread text-[11px] font-bold text-[#0b0b0c] text-center leading-[18px]"
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
        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            onOpenActions();
          }}
          aria-label={`Ouvrir le menu d'actions rapides pour ${displayName}`}
          className={clsx(
            "min-h-[68px] min-w-[44px] border-l border-border bg-bg text-[22px] text-text-muted transition-colors",
            "hover:bg-bg-e3 hover:text-text focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent",
            conv.is_pinned && "bg-bg-pinned",
          )}
        >
          ⋯
        </button>
      </div>
    </div>
  );
}

function ActionRail({
  side,
  active,
  actions,
  onQuickAction,
}: {
  side: SwipeSide;
  active: boolean;
  actions: QuickAction[];
  onQuickAction: (action: QuickAction) => void;
}) {
  return (
    <div
      className={clsx(
        "absolute inset-y-0 z-0 flex w-full items-stretch bg-bg-e2 transition-opacity duration-150",
        side === "left" ? "left-0 justify-start" : "right-0 justify-end",
        active ? "opacity-100" : "opacity-0",
      )}
      aria-hidden={!active}
    >
      <div className="grid w-[228px] grid-cols-4">
        {actions.map((action) => (
          <button
            key={`${side}-${action.id}`}
            type="button"
            disabled={action.disabled}
            onClick={(event) => {
              event.stopPropagation();
              onQuickAction(action);
            }}
            className={railButtonClass(action)}
            aria-label={action.label}
          >
            <span aria-hidden className="text-[15px]">
              {action.icon}
            </span>
            <span className="text-[10px] font-semibold leading-tight">{action.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function railButtonClass(action: QuickAction): string {
  const base =
    "min-w-[44px] border-l border-border px-1 text-center transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-40";
  if (action.tone === "accent") return `${base} bg-accent/10 text-text hover:bg-accent/20`;
  if (action.tone === "danger") return `${base} bg-bg-e3 text-text hover:bg-bg-e2`;
  return `${base} bg-bg-e2 text-text hover:bg-bg-e3`;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max);
}

// Icones : emojis discrets plutot que charger lucide-react en M1.
const ICON_ATTACHMENT = "📎";
const ICON_PIN = "📌";
const ICON_MUTED = "🔕";

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
