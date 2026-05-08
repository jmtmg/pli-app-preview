import { useEffect, useState } from "react";
import { ConversationList } from "@/features/list/ConversationList";
import { ConversationPane } from "@/features/conversation/ConversationPane";
import { Drawer } from "@/features/drawer/Drawer";
import { ContactSheet } from "@/features/contact/ContactSheet";
import { SearchModal } from "@/features/search/SearchModal";
import { useAccounts } from "@/api/queries";

/**
 * Local MVP shell — 3 responsive panes.
 *
 * The recovered corpus contains several later M2/M4 routes (auth, billing,
 * onboarding, feedback) that are not wired end-to-end yet. The functional MVP
 * starts with the core PLI promise: a WhatsApp-like conversation UI over a
 * local mailbox dataset, no real OAuth credentials required.
 */
export default function AppShell() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);
  const [selectedContactId, setSelectedContactId] = useState<string | null>(null);
  const [selectedMessageId, setSelectedMessageId] = useState<string | null>(null);
  const [contactSheetOpen, setContactSheetOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const { data: accounts } = useAccounts();

  const activeAccountId = accounts?.find((account) => account.is_active)?.id ?? accounts?.[0]?.id ?? null;
  const effectiveSearchAccountId = selectedAccountId ?? activeAccountId;

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <div
      className="fixed inset-0 grid bg-bg text-text font-sys
                 grid-cols-1
                 md:grid-cols-[360px_1fr]
                 xl:grid-cols-[380px_1fr_320px]"
    >
      <Drawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        selectedAccountId={selectedAccountId}
        onSelectAccount={setSelectedAccountId}
      />

      <div className={selectedContactId ? "hidden md:flex md:flex-col min-h-0" : "flex flex-col min-h-0"}>
        <ConversationList
          accountId={selectedAccountId}
          onSelect={(contactId) => {
            setSelectedContactId(contactId);
            setSelectedMessageId(null);
          }}
          onOpenDrawer={() => setDrawerOpen(true)}
          onOpenSearch={() => setSearchOpen(true)}
          selectedId={selectedContactId}
        />
      </div>

      <div className={selectedContactId ? "flex flex-col min-h-0" : "hidden md:flex md:flex-col min-h-0"}>
        <ConversationPane
          contactId={selectedContactId}
          highlightedMessageId={selectedMessageId}
          onClose={() => setSelectedContactId(null)}
          onOpenContact={() => setContactSheetOpen(true)}
        />
      </div>

      {selectedContactId && (
        <div
          className={
            contactSheetOpen
              ? "fixed inset-0 z-30 md:static md:z-auto"
              : "hidden xl:flex xl:flex-col min-h-0"
          }
        >
          <ContactSheet
            contactId={selectedContactId}
            onClose={() => setContactSheetOpen(false)}
          />
        </div>
      )}

      <SearchModal
        open={searchOpen}
        accountId={effectiveSearchAccountId}
        onClose={() => setSearchOpen(false)}
        onSelectContact={(target) => {
          setSelectedContactId(target.contactId);
          setSelectedMessageId(target.kind === "message" ? target.resultId : null);
          setContactSheetOpen(false);
        }}
      />
    </div>
  );
}
