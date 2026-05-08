import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import type { Conversation } from "@/api/queries";
import {
  QuickActionSheet,
  buildQuickActions,
  getConversationActionRequest,
  getSwipeActions,
  getSwipePanelState,
} from "./quickActions";

function conversation(overrides: Partial<Conversation> = {}): Conversation {
  return {
    contact_id: "contact-alice",
    account_id: "account-a",
    email: "alice@example.com",
    email_normalized: "alice@example.com",
    display_name: "Alice",
    kind: "human",
    is_pinned: false,
    pinned_order: null,
    is_muted: false,
    unread_count: 0,
    has_attachments: false,
    last_msg_at: "2026-05-08T12:00:00Z",
    last_preview: "Dernier message",
    ...overrides,
  };
}

describe("quick conversation actions", () => {
  it("expose les 4 actions Cowork dans le même ordre pour swipe gauche, swipe droite et bottom sheet", () => {
    const conv = conversation();
    const expected = ["Épingler", "Non lu", "Silence", "Archiver"];

    expect(buildQuickActions({ conv, pinnedCount: 1 }).map((action) => action.label)).toEqual(expected);
    expect(getSwipeActions("left", { conv, pinnedCount: 1 }).map((action) => action.label)).toEqual(expected);
    expect(getSwipeActions("right", { conv, pinnedCount: 1 }).map((action) => action.label)).toEqual(expected);
  });

  it("bascule les libellés et grise Épingler quand la limite 3/3 du compte est atteinte", () => {
    const full = buildQuickActions({ conv: conversation(), pinnedCount: 3 });
    expect(full[0]).toMatchObject({ id: "toggle-pin", label: "Épingler", disabled: true, hint: "3/3 épinglées" });

    const pinned = buildQuickActions({ conv: conversation({ is_pinned: true }), pinnedCount: 3 });
    expect(pinned[0]).toMatchObject({ id: "toggle-pin", label: "Désépingler", disabled: false, hint: "3/3 épinglées" });

    const muted = buildQuickActions({ conv: conversation({ is_muted: true }), pinnedCount: 1 });
    expect(muted[2]).toMatchObject({ id: "toggle-mute", label: "Réactiver" });
  });

  it("applique les seuils Cowork: ouverture à 33%, fermeture instinctive à 18%, avec direction bilatérale", () => {
    expect(getSwipePanelState({ dragOffset: -120, rowWidth: 300, wasOpen: false })).toEqual({
      open: true,
      side: "left",
    });
    expect(getSwipePanelState({ dragOffset: 120, rowWidth: 300, wasOpen: false })).toEqual({
      open: true,
      side: "right",
    });
    expect(getSwipePanelState({ dragOffset: 75, rowWidth: 300, wasOpen: false })).toEqual({
      open: false,
      side: null,
    });
    expect(getSwipePanelState({ dragOffset: 45, rowWidth: 300, wasOpen: true })).toEqual({
      open: false,
      side: null,
    });
  });

  it("résout les endpoints backend associés aux actions rapides", () => {
    const conv = conversation({ is_pinned: false, is_muted: false });
    expect(getConversationActionRequest("toggle-pin", conv)).toEqual({ path: "/conversations/contact-alice/pin" });
    expect(getConversationActionRequest("mark-unread", conv)).toEqual({ path: "/conversations/contact-alice/mark-unread" });
    expect(getConversationActionRequest("toggle-mute", conv)).toEqual({ path: "/conversations/contact-alice/mute?muted=true" });
    expect(getConversationActionRequest("archive", conv)).toEqual({ path: "/conversations/contact-alice/archive" });

    expect(getConversationActionRequest("toggle-pin", conversation({ is_pinned: true }))).toEqual({
      path: "/conversations/contact-alice/unpin",
    });
    expect(getConversationActionRequest("toggle-mute", conversation({ is_muted: true }))).toEqual({
      path: "/conversations/contact-alice/mute?muted=false",
    });
  });

  it("rend une bottom sheet accessible avec compteur X/3 et targets d'action", () => {
    const html = renderToStaticMarkup(
      <QuickActionSheet
        open
        conv={conversation()}
        actions={buildQuickActions({ conv: conversation(), pinnedCount: 1 })}
        pinnedCount={1}
        onAction={vi.fn()}
        onClose={vi.fn()}
      />,
    );

    expect(html).toContain("data-bottom-sheet=\"conversation-actions\"");
    expect(html).toContain("role=\"dialog\"");
    expect(html).toContain("Actions rapides");
    expect(html).toContain("Épingles 1/3");
    for (const label of ["Épingler", "Non lu", "Silence", "Archiver"]) {
      expect(html).toContain(label);
    }

    expect(
      renderToStaticMarkup(
        <QuickActionSheet
          open={false}
          conv={conversation()}
          actions={[]}
          pinnedCount={0}
          onAction={vi.fn()}
          onClose={vi.fn()}
        />,
      ),
    ).toBe("");
  });
});
