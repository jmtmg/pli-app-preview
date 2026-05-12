/**
 * Drawer lateral — bascule de compte + ajout OAuth. US-1.8 Sprint 1.
 *
 * Ref. wireframes 03-Wireframes.md §3.4 (ecran C).
 *
 * P0 Sprint 1 :
 *   - liste des comptes connectes (avatar + email + provider + nb non lus)
 *   - bouton "Tous les comptes" (reset filter)
 *   - boutons "Ajouter un compte" Google / Microsoft -> /api/auth/{provider}/start
 *   - Escape ferme le drawer (a11y)
 *   - focus rentre dans le drawer a l'ouverture, revient au trigger a la fermeture
 *   - etats loading / error / empty explicites
 *   - backdrop clic ferme, backdrop cache aux lecteurs d'ecran
 */
import { useEffect, useRef, useState } from "react";
import clsx from "clsx";
import { useAccounts, type Account } from "@/api/queries";
import { Avatar } from "@/components/Avatar";

interface Props {
  open: boolean;
  onClose: () => void;
  selectedAccountId: string | null;
  onSelectAccount: (id: string | null) => void;
}

export type ThemeMode = "Sombre" | "Clair";

export interface DrawerViewProps extends Props {
  accounts: Account[] | undefined;
  isLoading: boolean;
  isError: boolean;
  themeMode: ThemeMode;
  now?: Date;
  onRetry: () => void;
  onToggleTheme: () => void;
}

const RECENT_SYNC_MS = 60 * 60 * 1000;
const FOCUSABLE_SELECTOR = [
  "a[href]",
  "button:not([disabled])",
  "input:not([disabled])",
  "select:not([disabled])",
  "textarea:not([disabled])",
  "[tabindex]:not([tabindex='-1'])",
].join(", ");

export function Drawer({ open, onClose, selectedAccountId, onSelectAccount }: Props) {
  const { data: accounts, isLoading, isError, refetch } = useAccounts();
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => readStoredThemeMode());

  const toggleTheme = () => {
    setThemeMode((current) => getNextThemeMode(current));
  };

  useEffect(() => {
    if (typeof document === "undefined") return;
    document.documentElement.dataset.theme = getThemeDatasetValue(themeMode);
    persistThemeMode(themeMode);
  }, [themeMode]);

  return (
    <DrawerView
      open={open}
      onClose={onClose}
      selectedAccountId={selectedAccountId}
      onSelectAccount={onSelectAccount}
      accounts={accounts}
      isLoading={isLoading}
      isError={isError}
      onRetry={() => refetch()}
      themeMode={themeMode}
      onToggleTheme={toggleTheme}
    />
  );
}

export function getProviderLabel(provider: Account["provider"]): string {
  return provider === "gmail" ? "Google" : "Microsoft";
}

export function getNextThemeMode(themeMode: ThemeMode): ThemeMode {
  return themeMode === "Sombre" ? "Clair" : "Sombre";
}

export function getThemeDatasetValue(themeMode: ThemeMode): "dark" | "light" {
  return themeMode === "Clair" ? "light" : "dark";
}

export function readStoredThemeMode(): ThemeMode {
  if (typeof window === "undefined") return "Sombre";
  try {
    return window.localStorage.getItem("pli-theme-mode") === "Clair" ? "Clair" : "Sombre";
  } catch {
    return "Sombre";
  }
}

export function persistThemeMode(themeMode: ThemeMode): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem("pli-theme-mode", themeMode);
  } catch {
    // Storage can be unavailable in private/restricted contexts; keep UI usable.
  }
}

function parseSyncDate(lastSyncAt: string | null): Date | null {
  if (!lastSyncAt) return null;
  const date = new Date(lastSyncAt);
  return Number.isNaN(date.getTime()) ? null : date;
}

function isRecentSync(date: Date, now: Date): boolean {
  const ageMs = now.getTime() - date.getTime();
  return ageMs >= 0 && ageMs <= RECENT_SYNC_MS;
}

export function formatSyncStatus(lastSyncAt: string | null, now = new Date()): string {
  if (!lastSyncAt) return "Jamais synchronisé";
  const date = parseSyncDate(lastSyncAt);
  if (!date) return "Sync inconnue";
  if (isRecentSync(date, now)) return "Synchronisé récemment";
  const formatted = new Intl.DateTimeFormat("fr-FR", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
  return `Dernière sync ${formatted}`;
}

export function buildDrawerSyncSummary(accounts: Account[] | undefined, now = new Date()): string {
  if (!accounts || accounts.length === 0) return "Aucun compte synchronisé";
  const syncDates = accounts.map((account) => parseSyncDate(account.last_sync_at));
  if (syncDates.every((date) => date === null)) return "Jamais synchronisé";
  if (syncDates.some((date) => date === null)) return "Sync partielle";
  if (syncDates.every((date) => date && isRecentSync(date, now))) return "Sync à jour";
  return "Dernière sync ancienne";
}

function trapFocusInDrawer(event: KeyboardEvent, container: HTMLElement | null): void {
  if (event.key !== "Tab" || !container) return;
  const focusable = Array.from(container.querySelectorAll<HTMLElement>(FOCUSABLE_SELECTOR)).filter(
    (element) => !element.hasAttribute("disabled") && element.getAttribute("aria-hidden") !== "true",
  );
  if (focusable.length === 0) {
    event.preventDefault();
    container.focus();
    return;
  }
  const first = focusable[0];
  const last = focusable[focusable.length - 1];
  const active = document.activeElement;
  if (event.shiftKey && active === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && active === last) {
    event.preventDefault();
    first.focus();
  } else if (!container.contains(active)) {
    event.preventDefault();
    first.focus();
  }
}

export function DrawerView({
  open,
  onClose,
  selectedAccountId,
  onSelectAccount,
  accounts,
  isLoading,
  isError,
  onRetry,
  themeMode,
  now = new Date(),
  onToggleTheme,
}: DrawerViewProps) {
  const asideRef = useRef<HTMLElement | null>(null);
  const triggerRef = useRef<HTMLElement | null>(null);
  const accountList = accounts ?? [];

  useEffect(() => {
    if (!open) return;
    triggerRef.current = document.activeElement as HTMLElement | null;
    const t = window.setTimeout(() => {
      asideRef.current?.querySelector<HTMLElement>("[data-drawer-close]")?.focus();
    }, 50);

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onClose();
        return;
      }
      trapFocusInDrawer(e, asideRef.current);
    };
    window.addEventListener("keydown", onKey);
    return () => {
      window.clearTimeout(t);
      window.removeEventListener("keydown", onKey);
      triggerRef.current?.focus?.();
    };
  }, [open, onClose]);

  const hiddenProps = open ? {} : { inert: "" };

  return (
    <>
      <div
        className={clsx(
          "fixed inset-0 bg-black/40 backdrop-blur-sm z-40 transition-opacity duration-200",
          open ? "opacity-100" : "opacity-0 pointer-events-none",
        )}
        onClick={onClose}
        aria-hidden
      />

      <aside
        {...hiddenProps}
        ref={asideRef}
        className={clsx(
          "fixed top-0 left-0 bottom-0 w-[300px] max-w-[88vw] bg-bg-e1 border-r border-border z-50",
          "flex flex-col transition-transform duration-200 ease-ios",
          open ? "translate-x-0" : "-translate-x-full",
        )}
        style={{ paddingTop: "var(--safe-top)", paddingBottom: "var(--safe-bottom)" }}
        role="dialog"
        aria-modal="true"
        aria-label="Menu comptes et parametres"
        aria-hidden={!open}
        data-focus-trap={open ? "true" : undefined}
        tabIndex={open ? undefined : -1}
      >
        <header className="h-14 px-4 border-b border-border flex items-center justify-between">
          <h2 className="font-semibold text-[15px]">Comptes</h2>
          <button
            type="button"
            data-drawer-close
            onClick={onClose}
            className="w-8 h-8 rounded-lg hover:bg-bg-e3 text-text-muted flex items-center justify-center focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            aria-label="Fermer le menu"
          >
            X
          </button>
        </header>

        <div className="flex-1 min-h-0 overflow-y-auto py-2">
          <button
            type="button"
            onClick={() => {
              onSelectAccount(null);
              onClose();
            }}
            className={clsx(
              "w-full px-4 py-2 text-left text-[13px] font-medium transition-colors",
              "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent",
              selectedAccountId === null ? "bg-accent-soft text-accent" : "hover:bg-bg-e3",
            )}
            aria-current={selectedAccountId === null ? "true" : undefined}
          >
            Tous les comptes
          </button>

          <div className="mt-1 border-t border-border">
            {isLoading ? (
              <DrawerLoading />
            ) : isError ? (
              <DrawerError onRetry={onRetry} />
            ) : accountList.length === 0 ? (
              <div className="px-4 py-6 text-[12px] text-text-muted">
                Aucun compte connecte. Ajoute-en un ci-dessous.
              </div>
            ) : (
              accountList.map((account) => {
                const isSelected = selectedAccountId === account.id;
                return (
                  <button
                    key={account.id}
                    type="button"
                    onClick={() => {
                      onSelectAccount(account.id);
                      onClose();
                    }}
                    aria-current={isSelected ? "true" : undefined}
                    className={clsx(
                      "relative w-full px-4 py-2.5 flex items-center gap-3 text-left transition-colors",
                      "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent",
                      isSelected ? "bg-accent-soft text-text" : "hover:bg-bg-e3",
                    )}
                  >
                    {isSelected && (
                      <span
                        data-active-account-bar="true"
                        className="absolute left-0 top-2 bottom-2 w-1 rounded-r-full bg-accent"
                        aria-hidden
                      />
                    )}
                    <Avatar initials={account.email.slice(0, 2)} size={32} />
                    <div className="flex-1 min-w-0">
                      <div className="truncate text-[13px] font-medium">{account.email}</div>
                      <div className="text-[11px] text-text-dim uppercase">
                        {getProviderLabel(account.provider)} · {formatSyncStatus(account.last_sync_at, now)}
                      </div>
                    </div>
                    {account.unread_count > 0 && (
                      <span
                        className="min-w-[20px] h-[18px] px-1.5 rounded-full bg-accent/80 text-[11px] font-bold text-[#0b0b0c] text-center leading-[18px]"
                        aria-label={`${account.unread_count} non lus`}
                      >
                        {account.unread_count > 99 ? "99+" : account.unread_count}
                      </span>
                    )}
                  </button>
                );
              })
            )}
          </div>

          <div className="border-t border-border mt-1">
            <a
              href="/api/auth/gmail/start"
              className="block w-full px-4 py-2.5 text-left text-[13px] text-accent hover:bg-bg-e3 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent"
            >
              + Ajouter un compte Google
            </a>
            <a
              href="/api/auth/microsoft/start"
              className="block w-full px-4 py-2.5 text-left text-[13px] text-accent hover:bg-bg-e3 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent"
            >
              + Ajouter un compte Microsoft
            </a>
            <p className="px-4 pb-2 text-[11px] text-text-dim">
              Connexion officielle uniquement, sans secret stocké dans la démo locale.
            </p>
          </div>
        </div>

        <footer className="border-t border-border px-4 py-3 text-[12px] text-text-muted space-y-2">
          <div className="flex items-center justify-between gap-3">
            <span>{buildDrawerSyncSummary(accountList, now)}</span>
            <span>PLI · v0.1</span>
          </div>
          <button
            type="button"
            onClick={onToggleTheme}
            className="min-h-11 w-full rounded-xl border border-border px-3 text-left hover:bg-bg-e3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            role="switch"
            aria-checked={themeMode === "Clair"}
            aria-label={`Basculer le thème. Thème actuel: ${themeMode}`}
          >
            Thème: {themeMode}
          </button>
        </footer>
      </aside>
    </>
  );
}

function DrawerLoading() {
  return (
    <div role="status" aria-label="Chargement des comptes">
      {Array.from({ length: 2 }, (_, i) => (
        <div
          key={i}
          className="w-full px-4 py-2.5 flex items-center gap-3 animate-pulse"
        >
          <div className="w-8 h-8 rounded-full bg-bg-e2" />
          <div className="flex-1 space-y-1.5">
            <div className="h-3 w-2/3 bg-bg-e2 rounded" />
            <div className="h-2.5 w-1/3 bg-bg-e2 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

function DrawerError({ onRetry }: { onRetry: () => void }) {
  return (
    <div role="alert" className="px-4 py-4 space-y-2">
      <div className="text-[12px] text-text-muted">Impossible de charger les comptes.</div>
      <button
        type="button"
        onClick={onRetry}
        className="text-[12px] text-accent hover:underline focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
      >
        Reessayer
      </button>
    </div>
  );
}
