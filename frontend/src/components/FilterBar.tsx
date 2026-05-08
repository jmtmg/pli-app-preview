/**
 * Barre de filtres — chips scrollables.
 * Sprint 2 · FE — owner : FE.
 * Filtres P0 : Humains (défaut), Notifs, Non lus, Pièces jointes.
 */
import clsx from "clsx";
import type { FilterKind } from "@/api/queries";

const FILTERS: { key: FilterKind; label: string }[] = [
  { key: "humans",      label: "Humains" },
  { key: "notifs",      label: "Notifs" },
  { key: "unread",      label: "Non lus" },
  { key: "attachments", label: "Pièces jointes" },
];

interface Props {
  value: FilterKind;
  onChange: (v: FilterKind) => void;
}

export function FilterBar({ value, onChange }: Props) {
  return (
    <div
      className="h-11 px-3 border-b border-border flex gap-2 items-center overflow-x-auto"
      style={{ scrollbarWidth: "none" }}
      role="tablist"
      aria-label="Filtres de conversations"
    >
      {FILTERS.map(f => {
        const active = f.key === value;
        return (
          <button
            key={f.key}
            onClick={() => onChange(f.key)}
            role="tab"
            aria-selected={active}
            className={clsx(
              "h-7 px-3 rounded-full text-[12px] font-medium whitespace-nowrap transition-colors",
              active
                ? "bg-accent-soft text-accent border border-accent/30"
                : "bg-bg-e2 text-text-muted hover:text-text border border-transparent",
            )}
          >
            {f.label}
          </button>
        );
      })}
    </div>
  );
}
