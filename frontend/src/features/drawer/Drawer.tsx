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
import { useEffect, useRef } from "react";
import clsx from "clsx";
import { useAccounts } from "@/api/queries";
import { Avatar } from "@/components/Avatar";

interface Props {
  open: boolean;
  onClose: () => void;
  selectedAccountId: string | null;
  onSelectAccount: (id: string | null) => void;
}

export function Drawer({ open, onClose, selectedAccountId, onSelectAccount }: Props) {
  const { data: accounts, isLoading, isError, refetch } = useAccounts();
  const asideRef = useRef<HTMLElement | null>(null);
  const triggerRef = useRef<HTMLElement | null>(null);

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
      }
    };
    window.addEventListener("keydown", onKey);
    return () => {
      window.clearTimeout(t);
      window.removeEventListener("keydown", onKey);
      triggerRef.current?.focus?.();
    };
  }, [open, onClose]);

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
              <DrawerError onRetry={() => refetch()} />
            ) : (accounts ?? []).length === 0 ? (
              <div className="px-4 py-6 text-[12px] text-text-muted">
                Aucun compte connecte. Ajoute-en un ci-dessous.
              </div>
            ) : (
              (accounts ?? []).map((a) => (
                <button
                  key={a.id}
                  type="button"
                  onClick={() => {
                    onSelectAccount(a.id);
                    onClose();
                  }}
                  aria-current={selectedAccountId === a.id ? "true" : undefined}
                  className={clsx(
                    "w-full px-4 py-2.5 flex items-center gap-3 text-left transition-colors",
                    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-[-2px] focus-visible:outline-accent",
                    selectedAccountId === a.id ? "bg-bg-e3" : "hover:bg-bg-e3",
                  )}
                >
                  <Avatar initials={a.email.slice(0, 2)} size={32} />
                  <div className="flex-1 min-w-0">
                    <div className="truncate text-[13px] font-medium">{a.email}</div>
                    <div className="text-[11px] text-text-dim uppercase">{a.provider}</div>
                  </div>
                  {a.unread_count > 0 && (
                    <span
                      className="min-w-[20px] h-[18px] px-1.5 rounded-full bg-accent/80 text-[11px] font-bold text-[#0b0b0c] text-center leading-[18px]"
                      aria-label={`${a.unread_count} non lus`}
                    >
                      {a.unread_count > 99 ? "99+" : a.unread_count}
                    </span>
                  )}
                </button>
              ))
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
          </div>
        </div>

        <footer className="border-t border-border px-4 py-3 text-[12px] text-text-muted">
          PLI . v0.1
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
