/**
 * Header global — référence Cowork `03-Wireframes.md` §3.2 écran A.
 *
 * Règle design : 52 px sous safe area, chrome minimal, menu/drawer, compte
 * actif, actions recherche + composer. La recherche globale reste à câbler en
 * modal plein écran ; le bouton est gardé comme affordance visuelle P0.
 */
interface Props {
  onOpenDrawer: () => void;
}

export function Header({ onOpenDrawer }: Props) {
  return (
    <header
      className="px-2.5 border-b border-border flex items-center gap-1 bg-bg shrink-0"
      style={{ height: "calc(52px + var(--safe-top))", paddingTop: "var(--safe-top)" }}
    >
      <button
        onClick={onOpenDrawer}
        className="w-10 h-10 rounded-[10px] hover:bg-bg-e3 active:bg-bg-e2 flex items-center justify-center text-text-muted transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        aria-label="Ouvrir le menu comptes"
      >
        ☰
      </button>

      <button
        onClick={onOpenDrawer}
        className="w-10 h-10 rounded-full bg-bg-e2 text-[13px] font-semibold flex items-center justify-center hover:bg-bg-e3 active:bg-bg-e2 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        aria-label="Compte actif PLI demo"
        title="Compte demo"
      >
        P
      </button>

      <div className="flex-1" aria-hidden />

      <button
        type="button"
        className="w-10 h-10 rounded-[10px] hover:bg-bg-e3 active:bg-bg-e2 flex items-center justify-center text-text-muted transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        aria-label="Rechercher"
        title="Recherche globale — à câbler en modal"
      >
        🔍
      </button>

      <button
        type="button"
        className="w-10 h-10 rounded-[10px] hover:bg-bg-e3 active:bg-bg-e2 flex items-center justify-center text-accent transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
        aria-label="Nouveau message"
        title="Nouveau message (Cmd/Ctrl + N)"
      >
        ✎
      </button>
    </header>
  );
}
