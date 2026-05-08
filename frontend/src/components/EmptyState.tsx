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
  humans:      { title: "Boîte au calme",  body: "Aucun humain ne t’a écrit dans ce filtre." },
  notifs:      { title: "Pas de bruit",    body: "Les notifs des apps apparaîtront ici." },
  unread:      { title: "Tout est lu",     body: "Plus rien à traiter, profite." },
  attachments: { title: "Pas de pièces",   body: "Les fichiers reçus apparaîtront ici." },
  all:         { title: "Boîte vide",      body: "Aucune conversation pour ce compte." },
  none:        { title: "Sélectionne une conversation", body: "Pour commencer à lire ou à répondre." },
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
