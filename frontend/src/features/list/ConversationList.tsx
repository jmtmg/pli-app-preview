/**
 * Liste des conversations — colonne principale. US-1.7 Sprint 1.
 *
 * Reference UX : doc 03-Wireframes.md §3.2 (ecran A).
 * Reference prototype HTML : `Mail/index.html` (comportement complet mock).
 *
 * Etats : loading (skeleton 6 lignes), empty (EmptyState), error (message +
 *   bouton retry), success (pinned en tete puis le reste, infinite-scroll
 *   via IntersectionObserver sur sentinelle de fin).
 *
 * Accessibilite : role="list" sur le conteneur, aria-busy pendant fetch,
 *   aria-live="polite" pour le passage loading -> success.
 */
import { useEffect, useRef, useState } from "react";
import {
  useConversationActionMutation,
  useConversations,
  type Conversation,
  type FilterKind,
} from "@/api/queries";
import { Header } from "@/components/Header";
import { FilterBar } from "@/components/FilterBar";
import { ConversationRow } from "./ConversationRow";
import { EmptyState } from "@/components/EmptyState";
import {
  QuickActionSheet,
  buildQuickActions,
  getConversationActionRequest,
  type QuickAction,
} from "./quickActions";

interface Props {
  accountId: string | null;
  onSelect: (id: string) => void;
  onOpenDrawer: () => void;
  onOpenSearch: () => void;
  selectedId: string | null;
}

export function ConversationList({ accountId, onSelect, onOpenDrawer, onOpenSearch, selectedId }: Props) {
  const [filter, setFilter] = useState<FilterKind>("humans");
  const [openSwipeId, setOpenSwipeId] = useState<string | null>(null);
  const [sheetConversation, setSheetConversation] = useState<Conversation | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const quickActionMutation = useConversationActionMutation();
  const {
    data,
    isLoading,
    isError,
    error,
    refetch,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useConversations(accountId, filter);

  const items: Conversation[] = data?.pages.flatMap((p) => p.items) ?? [];
  const pinned = items.filter((c) => c.is_pinned);
  const rest = items.filter((c) => !c.is_pinned);
  const pinnedCount = pinned.length;

  useEffect(() => {
    if (!toast) return;
    const timer = window.setTimeout(() => setToast(null), 2400);
    return () => window.clearTimeout(timer);
  }, [toast]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setSheetConversation(null);
        setOpenSwipeId(null);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  async function runQuickAction(action: QuickAction, conv: Conversation) {
    if (action.disabled || quickActionMutation.isPending) return;
    const request = getConversationActionRequest(action.id, conv);
    try {
      const result = await quickActionMutation.mutateAsync(request);
      setOpenSwipeId(null);
      setSheetConversation(null);
      if (result.ok === false) {
        setToast(result.reason === "limit_3_reached" ? "Limite 3/3 épinglées atteinte" : "Action impossible");
        return;
      }
      setToast(actionToast(action.id, conv));
    } catch (e) {
      setToast(e instanceof Error ? e.message : "Action impossible");
    }
  }

  // Infinite-scroll via IntersectionObserver sur une sentinelle a la fin.
  const sentinelRef = useRef<HTMLDivElement | null>(null);
  useEffect(() => {
    const el = sentinelRef.current;
    if (!el || !hasNextPage || isFetchingNextPage) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          void fetchNextPage();
        }
      },
      { root: el.closest("[data-scroll-container]"), rootMargin: "200px" },
    );
    io.observe(el);
    return () => io.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  return (
    <section
      className="relative flex flex-col min-h-0 bg-bg border-r border-border"
      aria-busy={isLoading || undefined}
    >
      <Header onOpenDrawer={onOpenDrawer} onOpenSearch={onOpenSearch} />
      <FilterBar value={filter} onChange={setFilter} />
      <div
        data-scroll-container
        className="flex-1 min-h-0 overflow-y-auto"
        role="list"
        aria-live="polite"
        aria-label="Liste des conversations"
      >
        {isLoading ? (
          <ListSkeleton />
        ) : isError ? (
          <ListError onRetry={() => refetch()} message={formatError(error)} />
        ) : items.length === 0 ? (
          <EmptyState filter={filter} />
        ) : (
          <>
            {[...pinned, ...rest].map((c) => {
              const actions = buildQuickActions({ conv: c, pinnedCount });
              return (
                <ConversationRow
                  key={c.contact_id}
                  conv={c}
                  selected={selectedId === c.contact_id}
                  actions={actions}
                  swipeOpen={openSwipeId === c.contact_id}
                  onClick={() => onSelect(c.contact_id)}
                  onOpenActions={() => {
                    setOpenSwipeId(null);
                    setSheetConversation(c);
                  }}
                  onQuickAction={(action) => {
                    void runQuickAction(action, c);
                  }}
                  onSwipeOpen={() => setOpenSwipeId(c.contact_id)}
                  onSwipeClose={() => setOpenSwipeId(null)}
                />
              );
            })}
            <div ref={sentinelRef} aria-hidden className="h-6">
              {isFetchingNextPage && (
                <div className="py-2 text-center text-[12px] text-text-dim">
                  Chargement…
                </div>
              )}
            </div>
          </>
        )}
      </div>

      {sheetConversation && (
        <QuickActionSheet
          open
          conv={sheetConversation}
          actions={buildQuickActions({ conv: sheetConversation, pinnedCount })}
          pinnedCount={pinnedCount}
          onClose={() => setSheetConversation(null)}
          onAction={(action) => {
            void runQuickAction(action, sheetConversation);
          }}
        />
      )}

      {toast && (
        <div
          role="status"
          className="pointer-events-none absolute bottom-4 left-1/2 z-50 -translate-x-1/2 rounded-full border border-border bg-bg-e3 px-4 py-2 text-[12px] font-medium text-text shadow-xl"
        >
          {toast}
        </div>
      )}
    </section>
  );
}

/* ------------------------------------------------------------------ */
/* Sous-composants d'etat                                             */
/* ------------------------------------------------------------------ */

function actionToast(actionId: QuickAction["id"], conv: Conversation): string {
  switch (actionId) {
    case "toggle-pin":
      return conv.is_pinned ? "Conversation désépinglée" : "Conversation épinglée";
    case "mark-unread":
      return "Conversation marquée non lue";
    case "toggle-mute":
      return conv.is_muted ? "Notifications réactivées" : "Conversation silencieuse";
    case "archive":
      return "Conversation archivée";
  }
}

function ListSkeleton() {
  // 6 lignes skeleton avec animation subtile. Placeholder WCAG :
  // aria-label explicit + role="status" pour annoncer le chargement.
  return (
    <div role="status" aria-label="Chargement de la liste">
      {Array.from({ length: 6 }, (_, i) => (
        <div
          key={i}
          className="grid grid-cols-[48px_1fr_auto] gap-3 px-3.5 py-3 items-center border-b border-border animate-pulse"
        >
          <div className="w-12 h-12 rounded-full bg-bg-e2" />
          <div className="min-w-0 space-y-2">
            <div className="h-3 w-2/3 bg-bg-e2 rounded" />
            <div className="h-3 w-5/6 bg-bg-e2 rounded" />
          </div>
          <div className="h-3 w-10 bg-bg-e2 rounded" />
        </div>
      ))}
    </div>
  );
}

function ListError({ onRetry, message }: { onRetry: () => void; message: string }) {
  return (
    <div
      role="alert"
      className="flex-1 flex flex-col items-center justify-center px-6 text-center gap-3 py-12"
    >
      <div className="text-[15px] font-semibold text-text">Impossible de charger</div>
      <div className="text-[13px] text-text-muted max-w-xs">{message}</div>
      <button
        type="button"
        onClick={onRetry}
        className="mt-2 px-4 py-2 rounded-md bg-bg-e3 hover:bg-bg-e2 text-[13px] font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
      >
        Reessayer
      </button>
    </div>
  );
}

function formatError(e: unknown): string {
  if (e instanceof Error) return e.message;
  return "Erreur inconnue";
}
