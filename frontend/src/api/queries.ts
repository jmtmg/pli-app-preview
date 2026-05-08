/** TanStack Query hooks pour les endpoints PLI. */
import { useInfiniteQuery, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { get, post } from "./client";

export type FilterKind = "humans" | "notifs" | "unread" | "attachments" | "all";

/** Account — aligne sur `AccountSummary` du backend (pli/api/accounts.py).
 * `provider` utilise la forme interne "gmail" (cohérent avec le slug OAuth
 * /auth/gmail/start et la contrainte DB). Le libellé UI affiche "Google". */
export interface Account {
  id: string;
  email: string;
  provider: "gmail" | "microsoft";
  display_name: string | null;
  avatar_color: string | null;
  unread_count: number;
  is_active: boolean;
  last_sync_at: string | null;
}

/** ConversationItem — aligne sur `ConversationListResponse.items` du backend
 * (pli/api/conversations.py). `last_msg_at` est un ISO string (ou null si
 * jamais de message — cas rare mais possible). */
export interface Conversation {
  contact_id: string;
  account_id: string;
  email: string;
  email_normalized: string;
  display_name: string | null;
  kind: "human" | "notif";
  is_pinned: boolean;
  pinned_order: number | null;
  is_muted: boolean;
  unread_count: number;
  has_attachments: boolean;
  last_msg_at: string | null;
  last_preview: string | null;
}

export interface ConversationPage {
  items: Conversation[];
  next_cursor: string | null;
}

export interface Message {
  id: string;
  contact_id: string;
  direction: "in" | "out";
  subject: string | null;
  body_snippet: string;
  sent_at: number;
  has_attachments: boolean;
  is_read: boolean;
}

export interface Attachment {
  id: string;
  message_id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
}

export interface Contact {
  id: string;
  email: string;
  display_name: string | null;
  company: string | null;
  role: string | null;
  notes: string | null;
  attachments: Attachment[];
}

/* ------------------------------------------------------------------ */
/* Queries                                                            */
/* ------------------------------------------------------------------ */

export const useAccounts = () =>
  useQuery({
    queryKey: ["accounts"],
    queryFn: () => get<Account[]>("/accounts"),
  });

function buildConversationsUrl(
  accountId: string | null,
  filter: FilterKind,
  cursor?: string,
): string {
  const params = new URLSearchParams();
  params.set("filter", filter);
  if (accountId) params.set("account_id", accountId);
  if (cursor) params.set("cursor", cursor);
  return `/conversations?${params.toString()}`;
}

/** Infinite query — pagine via le cursor opaque retourne par le backend.
 *  On expose `items` a plat sur `.data?.pages.flatMap(p => p.items)`. */
export const useConversations = (accountId: string | null, filter: FilterKind) =>
  useInfiniteQuery<ConversationPage>({
    queryKey: ["conversations", accountId, filter],
    initialPageParam: undefined as string | undefined,
    queryFn: ({ pageParam }) =>
      get<ConversationPage>(buildConversationsUrl(accountId, filter, pageParam as string | undefined)),
    getNextPageParam: (last) => last.next_cursor ?? undefined,
    staleTime: 30_000,
  });

export const useMessages = (contactId: string | null) =>
  useQuery({
    queryKey: ["messages", contactId],
    queryFn: () => get<Message[]>(`/messages/by-contact/${contactId}`),
    enabled: !!contactId,
  });

export const useContact = (contactId: string | null) =>
  useQuery({
    queryKey: ["contact", contactId],
    queryFn: () => get<Contact>(`/contacts/${contactId}`),
    enabled: !!contactId,
  });

/* ------------------------------------------------------------------ */
/* Mutations                                                          */
/* ------------------------------------------------------------------ */

export const usePinMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, pin }: { id: string; pin: boolean }) =>
      post(`/conversations/${id}/${pin ? "pin" : "unpin"}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["conversations"] }),
  });
};

export const useConversationActionMutation = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ path }: { path: string }) => post<Record<string, unknown>>(path),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["conversations"] });
      qc.invalidateQueries({ queryKey: ["accounts"] });
    },
  });
};

export const useSendMessage = () => {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: { contact_id: string; body: string; subject?: string }) =>
      post<Message>("/messages/send", payload),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["messages", variables.contact_id] });
      qc.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
};
