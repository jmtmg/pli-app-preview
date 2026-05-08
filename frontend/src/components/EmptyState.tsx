/**
 * Etat vide — fallback utilise dans la liste et le pane conversation.
 * Sprint 2 · FE — owner : FE / UX.
 * Textes conformes aux wireframes §5.
 */
import type { FilterKind } from "@/api/queries";

interface Props {
  filter: FilterKind | "none";
}

const COPY: Record<FilterKind | "none", { title: string; body: string }> = {
  humans:      { title: "Boite au calme",  body: "Aucun humain ne t'a ecrit dans ce filtre." },
  notifs:      { title: "Pas de bruit",    body: "Les notifs des apps apparaitront ici." },
  unread:      { title: "Tout est lu",     body: "Plus rien a traiter, profite." },
  attachments: { title: "Pas de pieces",   body: "Les fichiers recus apparaitront ici." },
  all:         { title: "Boite vide",      body: "Aucune conversation pour ce compte." },
  none:        { title: "Selectionne une conversation", body: "Pour commencer a lire ou a repondre." },
};

export function EmptyState({ filter }: Props) {
  const { title, body } = COPY[filter];
  return (
    <div className="flex-1 flex flex-col items-center justify-center px-6 text-center gap-2 py-12">
      <div className="text-[15px] font-semibold text-text">{title}</div>
      <div className="text-[13px] text-text-muted max-w-xs">{body}</div>
    </div>
  );
}
