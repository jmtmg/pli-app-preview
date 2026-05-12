import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it, vi } from "vitest";
import type { Account } from "@/api/queries";
import {
  DrawerView,
  buildDrawerSyncSummary,
  formatSyncStatus,
  getNextThemeMode,
  getProviderLabel,
  getThemeDatasetValue,
  getAccountSignaturePreview,
} from "./Drawer";

const NOW = new Date("2026-05-12T10:00:00Z");

const ACCOUNTS: Account[] = [
  {
    id: "account-a",
    email: "demo@pli-app.fr",
    provider: "gmail",
    display_name: "PLI Demo",
    avatar_color: null,
    unread_count: 7,
    is_active: true,
    last_sync_at: "2026-05-12T09:30:00Z",
    signature: "—\nAlice PLI",
  },
  {
    id: "account-b",
    email: "ops@pli-app.fr",
    provider: "microsoft",
    display_name: "Ops PLI",
    avatar_color: null,
    unread_count: 0,
    is_active: true,
    last_sync_at: null,
    signature: null,
  },
];

describe("Drawer v1 account status", () => {
  it("rend le compte sélectionné avec barre active, provider lisible, unread badge, sync et thème", () => {
    const html = renderToStaticMarkup(
      <DrawerView
        open
        accounts={ACCOUNTS}
        isLoading={false}
        isError={false}
        selectedAccountId="account-a"
        themeMode="Sombre"
        now={NOW}
        onClose={vi.fn()}
        onRetry={vi.fn()}
        onSelectAccount={vi.fn()}
        onToggleTheme={vi.fn()}
      />,
    );

    expect(html).toContain("aria-current=\"true\"");
    expect(html).toContain("data-active-account-bar=\"true\"");
    expect(html).toContain("data-focus-trap=\"true\"");
    expect(html).toContain("demo@pli-app.fr");
    expect(html).toContain("Google");
    expect(html).toContain("7 non lus");
    expect(html).toContain("Synchronisé récemment");
    expect(html).toContain("Signature: Alice PLI");
    expect(html).toContain("Thème");
    expect(html).toContain("role=\"switch\"");
    expect(html).toContain("aria-checked=\"false\"");
    expect(html).toContain("Sombre");
  });

  it("retire les contrôles du tab order quand le drawer est fermé", () => {
    const html = renderToStaticMarkup(
      <DrawerView
        open={false}
        accounts={ACCOUNTS}
        isLoading={false}
        isError={false}
        selectedAccountId="account-a"
        themeMode="Clair"
        now={NOW}
        onClose={vi.fn()}
        onRetry={vi.fn()}
        onSelectAccount={vi.fn()}
        onToggleTheme={vi.fn()}
      />,
    );

    expect(html).toContain("aria-hidden=\"true\"");
    expect(html).toContain("inert=\"\"");
    expect(html).toContain("tabindex=\"-1\"");
  });

  it("expose des helpers déterministes pour provider, thème et statut sync", () => {
    expect(getProviderLabel("gmail")).toBe("Google");
    expect(getProviderLabel("microsoft")).toBe("Microsoft");
    expect(getAccountSignaturePreview("—\nAlice PLI")).toBe("Signature: Alice PLI");
    expect(getAccountSignaturePreview(null)).toBe("Signature non configurée");
    expect(getNextThemeMode("Sombre")).toBe("Clair");
    expect(getNextThemeMode("Clair")).toBe("Sombre");
    expect(getThemeDatasetValue("Sombre")).toBe("dark");
    expect(getThemeDatasetValue("Clair")).toBe("light");

    expect(formatSyncStatus(null, NOW)).toBe("Jamais synchronisé");
    expect(formatSyncStatus("2026-05-12T09:30:00Z", NOW)).toBe("Synchronisé récemment");
    expect(formatSyncStatus("2026-05-11T09:30:00Z", NOW)).toContain("Dernière sync");
    expect(formatSyncStatus("date-invalide", NOW)).toBe("Sync inconnue");

    expect(buildDrawerSyncSummary([], NOW)).toBe("Aucun compte synchronisé");
    expect(buildDrawerSyncSummary(ACCOUNTS.map((account) => ({ ...account, last_sync_at: null })), NOW)).toBe(
      "Jamais synchronisé",
    );
    expect(buildDrawerSyncSummary([{ ...ACCOUNTS[0], last_sync_at: "2026-05-12T09:30:00Z" }], NOW)).toBe(
      "Sync à jour",
    );
    expect(buildDrawerSyncSummary([{ ...ACCOUNTS[0], last_sync_at: "2026-05-11T09:30:00Z" }], NOW)).toBe(
      "Dernière sync ancienne",
    );
    expect(buildDrawerSyncSummary(ACCOUNTS, NOW)).toBe("Sync partielle");
  });
});
