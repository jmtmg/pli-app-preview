/**
 * Pane conversation (bulles, composer inline).
 * Sprint 2 · FE — lecture.
 * Sprint 3 · FE+BE — composer + envoi.
 */
import { useMessages, useContact } from "@/api/queries";
import { MessageBubble } from "./MessageBubble";
import { Composer } from "./Composer";
import { EmptyState } from "@/components/EmptyState";
import { Avatar } from "@/components/Avatar";

interface Props {
  contactId: string | null;
  onClose: () => void;
  onOpenContact: () => void;
}

export function ConversationPane({ contactId, onClose, onOpenContact }: Props) {
  const { data: messages } = useMessages(contactId);
  const { data: contact } = useContact(contactId);

  if (!contactId) {
    return <EmptyState filter="none" />;
  }

  const title = contact?.display_name ?? contact?.email ?? "Conversation";

  return (
    <section className="flex flex-col min-h-0 bg-bg">
      <header className="h-14 border-b border-border px-3 flex items-center gap-2">
        <button
          onClick={onClose}
          className="md:hidden w-9 h-9 rounded-lg hover:bg-bg-e3 flex items-center justify-center"
          aria-label="Retour"
        >
          ←
        </button>
        <button
          onClick={onOpenContact}
          className="flex items-center gap-2.5 flex-1 min-w-0 hover:bg-bg-e3 rounded-lg px-2 py-1 transition-colors xl:pointer-events-none xl:hover:bg-transparent"
          aria-label="Voir la fiche contact"
        >
          <Avatar initials={title.slice(0, 2)} size={32} />
          <div className="min-w-0 text-left">
            <div className="truncate text-[14px] font-semibold">{title}</div>
            {contact?.company && (
              <div className="truncate text-[11px] text-text-dim">{contact.company}</div>
            )}
          </div>
        </button>
      </header>

      <div className="flex-1 min-h-0 overflow-y-auto p-4 flex flex-col gap-2.5">
        {(messages ?? []).map(m => <MessageBubble key={m.id} msg={m} />)}
      </div>

      <Composer contactId={contactId} />
    </section>
  );
}
