import type { Conversation } from "@/api/queries";

export type QuickActionId = "toggle-pin" | "mark-unread" | "toggle-mute" | "archive";
export type SwipeSide = "left" | "right";

export interface QuickAction {
  id: QuickActionId;
  label: string;
  icon: string;
  tone: "accent" | "neutral" | "danger";
  disabled?: boolean;
  hint?: string;
}

export interface QuickActionContext {
  conv: Conversation;
  pinnedCount: number;
}

export interface ConversationActionRequest {
  path: string;
}

const MAX_PINNED = 3;
const SWIPE_OPEN_THRESHOLD = 0.33;
const SWIPE_CLOSE_THRESHOLD = 0.18;

export function buildQuickActions({ conv, pinnedCount }: QuickActionContext): QuickAction[] {
  const pinLimitReached = pinnedCount >= MAX_PINNED && !conv.is_pinned;
  const pinHint = `${Math.min(pinnedCount, MAX_PINNED)}/${MAX_PINNED} épinglées`;

  return [
    {
      id: "toggle-pin",
      label: conv.is_pinned ? "Désépingler" : "Épingler",
      icon: "📌",
      tone: "accent",
      disabled: pinLimitReached,
      hint: pinHint,
    },
    {
      id: "mark-unread",
      label: "Non lu",
      icon: "●",
      tone: "accent",
    },
    {
      id: "toggle-mute",
      label: conv.is_muted ? "Réactiver" : "Silence",
      icon: conv.is_muted ? "🔔" : "🔕",
      tone: "neutral",
    },
    {
      id: "archive",
      label: "Archiver",
      icon: "⌄",
      tone: "danger",
    },
  ];
}

export function getSwipeActions(_side: SwipeSide, context: QuickActionContext): QuickAction[] {
  return buildQuickActions(context);
}

export function getSwipePanelState({
  dragOffset,
  rowWidth,
  wasOpen,
}: {
  dragOffset: number;
  rowWidth: number;
  wasOpen: boolean;
}): { open: boolean; side: SwipeSide | null } {
  if (rowWidth <= 0) return { open: false, side: null };

  const ratio = Math.abs(dragOffset) / rowWidth;
  if (ratio <= SWIPE_CLOSE_THRESHOLD) return { open: false, side: null };
  if (ratio >= SWIPE_OPEN_THRESHOLD || wasOpen) {
    return { open: true, side: dragOffset < 0 ? "left" : "right" };
  }
  return { open: false, side: null };
}

export function getConversationActionRequest(
  actionId: QuickActionId,
  conv: Conversation,
): ConversationActionRequest {
  switch (actionId) {
    case "toggle-pin":
      return { path: `/conversations/${conv.contact_id}/${conv.is_pinned ? "unpin" : "pin"}` };
    case "mark-unread":
      return { path: `/conversations/${conv.contact_id}/mark-unread` };
    case "toggle-mute":
      return { path: `/conversations/${conv.contact_id}/mute?muted=${conv.is_muted ? "false" : "true"}` };
    case "archive":
      return { path: `/conversations/${conv.contact_id}/archive` };
  }
}

export function QuickActionSheet({
  open,
  conv,
  actions,
  pinnedCount,
  onAction,
  onClose,
}: {
  open: boolean;
  conv: Conversation;
  actions: QuickAction[];
  pinnedCount: number;
  onAction: (action: QuickAction) => void;
  onClose: () => void;
}) {
  if (!open) return null;
  const title = conv.display_name ?? conv.email;

  return (
    <div
      className="fixed inset-0 z-40 flex items-end justify-center bg-black/45 px-3 pb-3 motion-safe:transition-opacity"
      data-bottom-sheet="conversation-actions"
      onClick={onClose}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="conversation-actions-title"
        className="w-full max-w-md rounded-[28px] border border-border bg-bg-e2 p-3 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mx-auto mb-3 h-1 w-10 rounded-full bg-border" aria-hidden />
        <div className="px-2 pb-2">
          <h2 id="conversation-actions-title" className="text-[15px] font-semibold text-text">
            Actions rapides
          </h2>
          <p className="mt-1 truncate text-[12px] text-text-muted">
            {title} · Épingles {Math.min(pinnedCount, MAX_PINNED)}/{MAX_PINNED}
          </p>
        </div>
        <div className="grid grid-cols-2 gap-2">
          {actions.map((action) => (
            <button
              key={action.id}
              type="button"
              disabled={action.disabled}
              onClick={() => onAction(action)}
              aria-label={`${action.label} ${title}`}
              className={buttonClass(action)}
            >
              <span aria-hidden className="text-[18px]">
                {action.icon}
              </span>
              <span className="text-[13px] font-semibold">{action.label}</span>
              {action.hint && <span className="text-[11px] opacity-70">{action.hint}</span>}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function buttonClass(action: QuickAction): string {
  const base =
    "min-h-[64px] rounded-2xl border px-3 py-2 text-left transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent disabled:cursor-not-allowed disabled:opacity-45";
  if (action.tone === "danger") return `${base} border-border bg-bg hover:bg-bg-e3 text-text`;
  if (action.tone === "accent") return `${base} border-accent/20 bg-accent/10 hover:bg-accent/15 text-text`;
  return `${base} border-border bg-bg hover:bg-bg-e3 text-text`;
}
