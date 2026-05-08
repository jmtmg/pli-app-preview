export interface SearchContactResult {
  id: string;
  email: string;
  display_name: string | null;
  company: string | null;
}

export interface SearchMessageResult {
  id: string;
  subject: string | null;
  snippet: string | null;
  received_at: number;
  contact_id: string;
  display_name: string | null;
  email: string;
}

export interface SearchAttachmentResult {
  id: string;
  filename: string;
  mime_type: string | null;
  contact_id: string;
  display_name: string | null;
}

export interface SearchResponse {
  contacts: SearchContactResult[];
  messages: SearchMessageResult[];
  attachments: SearchAttachmentResult[];
}

export type SearchResultKind = "contact" | "message" | "attachment";
export type SearchResult = SearchContactResult | SearchMessageResult | SearchAttachmentResult;

export function normalizeSearchQuery(query: string): string {
  return query.trim().replace(/\s+/g, " ");
}

export function canRunSearch(query: string): boolean {
  return normalizeSearchQuery(query).length >= 2;
}

export function buildSearchPath(query: string, accountId: string): string {
  const params = new URLSearchParams({ q: normalizeSearchQuery(query) });
  params.set("account_id", accountId);
  return `/search?${params.toString()}`;
}

export function countSearchResults(results: SearchResponse | undefined): number {
  if (!results) return 0;
  return results.contacts.length + results.messages.length + results.attachments.length;
}

export function hasSearchResults(results: SearchResponse | undefined): boolean {
  return countSearchResults(results) > 0;
}

export function getSearchResultContactId(kind: SearchResultKind, result: SearchResult): string {
  if (kind === "contact") return (result as SearchContactResult).id;
  return (result as SearchMessageResult | SearchAttachmentResult).contact_id;
}
