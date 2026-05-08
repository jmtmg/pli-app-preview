/**
 * Fiche contact (3e colonne sur desktop, sheet bottom sur mobile).
 * Sprint 2 · FE — owner : FE.
 * Réf. wireframes 03-Wireframes.md §3.5 (écran D).
 *
 * Champs P0 : avatar, nom, email, société, fonction, notes.
 * Onglets : Conversations · Pièces jointes (FTS5).
 */
import { useState } from "react";
import clsx from "clsx";
import { useContact } from "@/api/queries";
import { Avatar } from "@/components/Avatar";

interface Props {
  contactId: string;
  onClose: () => void;
}

type Tab = "conv" | "attachments";

export function ContactSheet({ contactId, onClose }: Props) {
  const [tab, setTab] = useState<Tab>("conv");
  const { data, isLoading } = useContact(contactId);

  if (isLoading || !data) {
    return (
      <aside className="border-l border-border bg-bg-e1 flex items-center justify-center p-6">
        <span className="text-text-muted text-sm">Chargement…</span>
      </aside>
    );
  }

  const initials = (data.display_name ?? data.email).slice(0, 2);

  return (
    <aside className="border-l border-border bg-bg-e1 flex flex-col min-h-0">
      <header className="h-14 border-b border-border px-3 flex items-center justify-between">
        <h2 className="font-semibold text-[15px]">Contact</h2>
        <button
          onClick={onClose}
          className="w-8 h-8 rounded-lg hover:bg-bg-e3 text-text-muted flex items-center justify-center"
          aria-label="Fermer"
        >
          ✕
        </button>
      </header>

      <div className="px-5 py-5 flex flex-col items-center gap-2 border-b border-border">
        <Avatar initials={initials} size={56} />
        <div className="text-[16px] font-semibold text-center">
          {data.display_name ?? data.email}
        </div>
        <div className="text-[12px] text-text-muted">{data.email}</div>
        {data.company && (
          <div className="text-[12px] text-text-dim">
            {data.company}{data.role ? ` · ${data.role}` : ""}
          </div>
        )}
      </div>

      <div className="flex border-b border-border" role="tablist">
        {(["conv", "attachments"] as const).map(t => (
          <button
            key={t}
            role="tab"
            aria-selected={tab === t}
            onClick={() => setTab(t)}
            className={clsx(
              "flex-1 h-10 text-[12px] font-medium transition-colors",
              tab === t ? "text-accent border-b-2 border-accent" : "text-text-muted hover:text-text",
            )}
          >
            {t === "conv" ? "Conversations" : "Pièces jointes"}
          </button>
        ))}
      </div>

      <div className="flex-1 min-h-0 overflow-y-auto p-3 text-[13px] text-text-muted">
        {tab === "conv" ? (
          <div>Historique de la conversation (Sprint 2 · FE).</div>
        ) : (
          <ul className="flex flex-col gap-1.5">
            {(data.attachments ?? []).map(a => (
              <li key={a.id} className="px-3 py-2 rounded-lg bg-bg-e2 flex items-center gap-2">
                <span>📎</span>
                <span className="truncate flex-1">{a.filename}</span>
                <span className="text-text-dim text-[11px]">{formatSize(a.size_bytes)}</span>
              </li>
            )) || <li className="text-text-dim">Aucune pièce jointe.</li>}
          </ul>
        )}
      </div>
    </aside>
  );
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} o`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} ko`;
  return `${(bytes / 1024 / 1024).toFixed(1)} Mo`;
}
