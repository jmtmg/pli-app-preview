/**
 * Layout responsif PLI (Sprint 8 — US-8.7).
 *
 * - Mobile (< 768) : single pane, navigation via routes
 * - Tablet (768–1199) : 2 colonnes (liste + conversation)
 * - Desktop (≥ 1200) : 3 colonnes (drawer comptes | liste | conversation)
 *
 * Le composant détecte via `window.matchMedia` pour éviter le rendu double
 * (pas de hydration mismatch en SSR si on passe à un SSR plus tard).
 */

import { useEffect, useMemo, useState } from "react";
import { Outlet } from "react-router-dom";

type Breakpoint = "mobile" | "tablet" | "desktop";

export function ResponsiveLayout({
  drawer,
  list,
}: {
  drawer: React.ReactNode;
  list: React.ReactNode;
}) {
  const bp = useBreakpoint();

  return (
    <div
      className="h-screen w-screen flex bg-[var(--color-bg-canvas)] text-[var(--color-text-primary)]"
      data-bp={bp}
    >
      {bp === "desktop" && <aside className="w-64 border-r border-[var(--color-border-default)]">{drawer}</aside>}
      {bp !== "mobile" && (
        <nav
          aria-label="Conversations"
          className="w-80 border-r border-[var(--color-border-default)] overflow-y-auto"
        >
          {list}
        </nav>
      )}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

function useBreakpoint(): Breakpoint {
  const queries = useMemo(
    () => ({
      desktop: "(min-width: 1200px)",
      tablet: "(min-width: 768px) and (max-width: 1199px)",
    }),
    [],
  );
  const [bp, setBp] = useState<Breakpoint>("mobile");

  useEffect(() => {
    const mqlDesktop = window.matchMedia(queries.desktop);
    const mqlTablet = window.matchMedia(queries.tablet);

    function update() {
      if (mqlDesktop.matches) setBp("desktop");
      else if (mqlTablet.matches) setBp("tablet");
      else setBp("mobile");
    }
    update();
    mqlDesktop.addEventListener("change", update);
    mqlTablet.addEventListener("change", update);
    return () => {
      mqlDesktop.removeEventListener("change", update);
      mqlTablet.removeEventListener("change", update);
    };
  }, [queries]);

  return bp;
}
