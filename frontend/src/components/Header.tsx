/**
 * Header global — 56 px.
 * Sprint 2 · FE — owner : FE.
 * Prototype HTML : `Mail/index.html` (header avec avatar comptes + recherche).
 */
import { useState } from "react";

interface Props {
  onOpenDrawer: () => void;
}

export function Header({ onOpenDrawer }: Props) {
  const [query, setQuery] = useState("");

  return (
    <header
      className="h-14 px-3 border-b border-border grid grid-cols-[auto_1fr_auto] items-center gap-2 bg-bg"
      style={{ paddingTop: "var(--safe-top)" }}
    >
      <button
        onClick={onOpenDrawer}
        className="w-9 h-9 rounded-full bg-bg-e2 text-[13px] font-semibold flex items-center justify-center hover:bg-bg-e3 transition-colors"
        aria-label="Changer de compte"
      >
        JM
      </button>

      <div className="relative">
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          type="search"
          placeholder="Rechercher"
          className="w-full h-9 px-3 rounded-lg bg-bg-e2 text-[14px] placeholder:text-text-dim border border-transparent focus:border-border-strong focus:outline-none"
          aria-label="Rechercher"
        />
      </div>

      <button
        className="w-9 h-9 rounded-lg hover:bg-bg-e3 flex items-center justify-center text-text-muted transition-colors"
        aria-label="Nouveau message"
        title="Nouveau message (Cmd/Ctrl + N)"
      >
        ✎
      </button>
    </header>
  );
}
