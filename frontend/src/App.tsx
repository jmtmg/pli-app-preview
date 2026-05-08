import { useEffect, useState } from "react";
import { BrowserRouter, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { ConversationList } from "@/features/list/ConversationList";
import { ConversationPane } from "@/features/conversation/ConversationPane";
import { Drawer } from "@/features/drawer/Drawer";
import { ContactSheet } from "@/features/contact/ContactSheet";
import { useAuthStore, useIsAuthenticated } from "@/stores/authStore";

import SignupPage from "@/pages/auth/Signup";
import LoginPage from "@/pages/auth/Login";
import VerifyEmailPage from "@/pages/auth/VerifyEmail";
import CheckInboxPage from "@/pages/auth/CheckInbox";
import RequestResetPage from "@/pages/auth/RequestReset";
import ConfirmResetPage from "@/pages/auth/ConfirmReset";
import PricingPage from "@/pages/Pricing";
import BillingSettings from "@/pages/settings/BillingSettings";
import OnboardingWizard from "@/features/onboarding/OnboardingWizard";

/** Route guard : redirige vers /auth/login si non authentifié. */
function RequireAuth({ children }: { children: JSX.Element }) {
  const authed = useIsAuthenticated();
  const loading = useAuthStore((s) => s.loading);
  const loc = useLocation();
  if (loading) return <div className="p-8 text-gray-500">Chargement…</div>;
  if (!authed) return <Navigate to={`/auth/login?next=${encodeURIComponent(loc.pathname)}`} replace />;
  return children;
}

/** Racine : déclenche le boot auth au montage. */
export default function Root() {
  const boot = useAuthStore((s) => s.boot);
  useEffect(() => { boot(); }, [boot]);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth/signup" element={<SignupPage />} />
        <Route path="/auth/login" element={<LoginPage />} />
        <Route path="/auth/verify" element={<VerifyEmailPage />} />
        <Route path="/auth/check-inbox" element={<CheckInboxPage />} />
        <Route path="/auth/password-reset" element={<RequestResetPage />} />
        <Route path="/auth/reset" element={<ConfirmResetPage />} />
        <Route path="/pricing" element={<PricingPage />} />

        <Route path="/onboarding" element={<RequireAuth><OnboardingWizard /></RequireAuth>} />
        <Route path="/settings/billing" element={<RequireAuth><BillingSettings /></RequireAuth>} />

        <Route path="/" element={<RequireAuth><AppShell /></RequireAuth>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

/**
 * Shell principal — 3 panes responsives.
 * - mobile  (< md)  : une seule colonne (liste OU conversation)
 * - tablet  (md)    : 2 colonnes (liste + conversation)
 * - desktop (xl)    : 3 colonnes (liste + conversation + contact)
 * Drawer en overlay (via position: fixed) — toujours en overlay quel que soit le breakpoint.
 */
function AppShell() {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [selectedAccountId, setSelectedAccountId] = useState<string | null>(null);
  const [selectedContactId, setSelectedContactId] = useState<string | null>(null);
  const [contactSheetOpen, setContactSheetOpen] = useState(false);

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

      {/* Liste — masquée sur mobile si une conversation est sélectionnée */}
      <div className={selectedContactId ? "hidden md:flex md:flex-col min-h-0" : "flex flex-col min-h-0"}>
        <ConversationList
          accountId={selectedAccountId}
          onSelect={setSelectedContactId}
          onOpenDrawer={() => setDrawerOpen(true)}
          selectedId={selectedContactId}
        />
      </div>

      {/* Conversation — masquée sur mobile si aucune sélection */}
      <div className={selectedContactId ? "flex flex-col min-h-0" : "hidden md:flex md:flex-col min-h-0"}>
        <ConversationPane
          contactId={selectedContactId}
          onClose={() => setSelectedContactId(null)}
          onOpenContact={() => setContactSheetOpen(true)}
        />
      </div>

      {/* Fiche contact — desktop uniquement en colonne, mobile en overlay */}
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
    </div>
  );
}
