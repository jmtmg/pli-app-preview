import { useCallback, useEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { useQuery } from "@tanstack/react-query";
import { get } from "@/api/client";
import {
  canRunSearch,
  buildSearchPath,
  countSearchResults,
  getSearchResultContactId,
  hasSearchResults,
  normalizeSearchQuery,
  type SearchAttachmentResult,
  type SearchContactResult,
  type SearchMessageResult,
  type SearchResponse,
  type SearchResultKind,
} from "./searchModel";

interface Props {
  open: boolean;
  accountId: string | null;
  onClose: () => void;
  onSelectContact: (target: SearchSelection) => void;
}

export interface SearchSelection {
  kind: SearchResultKind;
  contactId: string;
  resultId: string;
}

function useGlobalSearch(query: string, accountId: string | null, open: boolean) {
  const normalized = normalizeSearchQuery(query);
  return useQuery({
    queryKey: ["search", accountId, normalized],
    queryFn: () => {
      if (!accountId) return Promise.resolve({ contacts: [], messages: [], attachments: [] });
      return get<SearchResponse>(buildSearchPath(normalized, accountId));
    },
    enabled: open && !!accountId && canRunSearch(normalized),
    staleTime: 20_000,
  });
}

export function SearchModal({ open, accountId, onClose, onSelectContact }: Props) {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  const normalized = useMemo(() => normalizeSearchQuery(query), [query]);
  const search = useGlobalSearch(query, accountId, open);

  useEffect(() => {
    if (!open) return;
    previousFocusRef.current = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const timer = window.setTimeout(() => inputRef.current?.focus(), 50);
    return () => window.clearTimeout(timer);
  }, [open]);

  const close = useCallback(() => {
    onClose();
    window.setTimeout(() => previousFocusRef.current?.focus(), 0);
  }, [onClose]);

  useEffect(() => {
    if (!open) return;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        close();
        return;
      }
      if (event.key !== "Tab") return;
      const focusables = dialogRef.current?.querySelectorAll<HTMLElement>(
        'button:not([disabled]), input:not([disabled]), [href], [tabindex]:not([tabindex="-1"])',
      );
      if (!focusables?.length) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [close, open]);

  if (!open) return null;

  const hasScopedAccount = !!accountId;
  const canSearch = hasScopedAccount && canRunSearch(normalized);
  const resultCount = countSearchResults(search.data);

  const select = (kind: SearchResultKind, result: SearchContactResult | SearchMessageResult | SearchAttachmentResult) => {
    onSelectContact({
      kind,
      contactId: getSearchResultContactId(kind, result),
      resultId: result.id,
    });
    close();
  };

  return (
    <div ref={dialogRef} className="fixed inset-0 z-50 bg-bg/95 backdrop-blur-xl text-text" role="dialog" aria-modal="true" aria-label="Recherche globale">
      <div className="mx-auto flex h-full w-full max-w-3xl flex-col border-border bg-bg md:my-8 md:h-[calc(100%-4rem)] md:rounded-[24px] md:border md:shadow-2xl">
        <header
          className="flex shrink-0 items-center gap-2 border-b border-border px-3"
          style={{ height: "calc(58px + var(--safe-top))", paddingTop: "var(--safe-top)" }}
        >
          <button
            type="button"
            onClick={close}
            className="flex h-11 w-11 items-center justify-center rounded-[12px] text-text-muted transition-colors hover:bg-bg-e3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
            aria-label="Fermer la recherche"
          >
            ←
          </button>
          <label className="sr-only" htmlFor="global-search-input">Recherche globale</label>
          <input
            ref={inputRef}
            id="global-search-input"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Rechercher contact, message, pièce jointe…"
            className="min-w-0 flex-1 bg-transparent text-[16px] outline-none placeholder:text-text-dim"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="flex h-11 w-11 items-center justify-center rounded-full text-text-muted transition-colors hover:bg-bg-e3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-accent"
              aria-label="Effacer la recherche"
            >
              ×
            </button>
          )}
        </header>

        <main className="min-h-0 flex-1 overflow-y-auto px-4 py-4" style={{ paddingBottom: "calc(1rem + var(--safe-bottom))" }}>
          {!hasScopedAccount && (
            <StatusBlock title="Compte requis" body="Sélectionne un compte actif pour lancer une recherche isolée." />
          )}

          {hasScopedAccount && !canSearch && (
            <SearchPrompt />
          )}

          {canSearch && search.isPending && (
            <StatusBlock title="Recherche en cours…" body="PLI parcourt les contacts, messages et pièces jointes du compte actif." />
          )}

          {canSearch && search.isError && (
            <StatusBlock title="Recherche indisponible" body="Le backend local n’a pas répondu correctement. Réessaie dans quelques secondes." tone="error" />
          )}

          {canSearch && search.data && !hasSearchResults(search.data) && (
            <StatusBlock title="Aucun résultat" body="Essaie un autre mot-clé, un nom de contact ou le nom d’une pièce jointe." />
          )}

          {canSearch && search.data && hasSearchResults(search.data) && (
            <div className="space-y-6">
              <div className="text-[12px] text-text-muted">
                {resultCount} résultat{resultCount > 1 ? "s" : ""} pour <span className="text-accent">{normalized}</span>
              </div>
              <ResultSection title="Contacts" emptyLabel="Aucun contact" count={search.data.contacts.length}>
                {search.data.contacts.map((contact) => (
                  <ResultButton
                    key={contact.id}
                    title={contact.display_name ?? contact.email}
                    meta={[contact.email, contact.company].filter(Boolean).join(" · ")}
                    query={normalized}
                    icon="👤"
                    onClick={() => select("contact", contact)}
                  />
                ))}
              </ResultSection>

              <ResultSection title="Messages" emptyLabel="Aucun message" count={search.data.messages.length}>
                {search.data.messages.map((message) => (
                  <ResultButton
                    key={message.id}
                    title={message.subject ?? "Sans sujet"}
                    meta={`${message.display_name ?? message.email} · ${message.snippet ?? ""}`}
                    query={normalized}
                    icon="✉️"
                    onClick={() => select("message", message)}
                  />
                ))}
              </ResultSection>

              <ResultSection title="Pièces jointes" emptyLabel="Aucune pièce jointe" count={search.data.attachments.length}>
                {search.data.attachments.map((attachment) => (
                  <ResultButton
                    key={attachment.id}
                    title={attachment.filename}
                    meta={[attachment.display_name, attachment.mime_type].filter(Boolean).join(" · ")}
                    query={normalized}
                    icon="📎"
                    onClick={() => select("attachment", attachment)}
                  />
                ))}
              </ResultSection>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

function SearchPrompt() {
  return (
    <div className="flex min-h-[45vh] flex-col items-center justify-center gap-3 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-bg-e2 text-2xl">🔍</div>
      <div className="text-[17px] font-semibold">Recherche globale</div>
      <div className="max-w-xs text-[13px] leading-5 text-text-muted">
        Tape au moins deux caractères pour retrouver un contact, un message ou une pièce jointe.
      </div>
      <div className="rounded-full border border-border px-3 py-1 text-[11px] text-text-dim">Esc pour fermer</div>
    </div>
  );
}

function StatusBlock({ title, body, tone = "muted" }: { title: string; body: string; tone?: "muted" | "error" }) {
  return (
    <div className="flex min-h-[45vh] flex-col items-center justify-center gap-2 text-center">
      <div className={tone === "error" ? "text-[15px] font-semibold text-red-300" : "text-[15px] font-semibold text-text"}>{title}</div>
      <div className="max-w-xs text-[13px] leading-5 text-text-muted">{body}</div>
    </div>
  );
}

function ResultSection({ title, count, emptyLabel, children }: { title: string; count: number; emptyLabel: string; children: ReactNode }) {
  return (
    <section className="space-y-2" aria-label={title}>
      <div className="flex items-center justify-between text-[12px] uppercase tracking-[0.16em] text-text-dim">
        <span>{title}</span>
        <span>{count}</span>
      </div>
      {count === 0 ? (
        <div className="rounded-[16px] border border-border bg-bg-e1 px-3 py-3 text-[13px] text-text-muted">{emptyLabel}</div>
      ) : (
        <div className="overflow-hidden rounded-[18px] border border-border bg-bg-e1">{children}</div>
      )}
    </section>
  );
}

function ResultButton({ title, meta, query, icon, onClick }: { title: string; meta: string; query: string; icon: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="grid w-full grid-cols-[38px_1fr] gap-3 border-b border-border px-3 py-3 text-left last:border-b-0 transition-colors hover:bg-bg-e2 focus-visible:outline focus-visible:outline-2 focus-visible:outline-inset focus-visible:outline-accent"
    >
      <span className="flex h-9 w-9 items-center justify-center rounded-full bg-bg-e3 text-[15px]" aria-hidden>{icon}</span>
      <span className="min-w-0">
        <span className="block truncate text-[14px] font-medium text-text"><HighlightedText text={title} query={query} /></span>
        <span className="block truncate text-[12px] text-text-muted"><HighlightedText text={meta} query={query} /></span>
      </span>
    </button>
  );
}

function HighlightedText({ text, query }: { text: string; query: string }) {
  const trimmed = query.trim();
  if (!trimmed) return <>{text}</>;
  const lowerText = text.toLocaleLowerCase("fr-FR");
  const lowerQuery = trimmed.toLocaleLowerCase("fr-FR");
  const index = lowerText.indexOf(lowerQuery);
  if (index < 0) return <>{text}</>;
  return (
    <>
      {text.slice(0, index)}
      <mark className="rounded bg-accent/20 px-0.5 text-accent">{text.slice(index, index + trimmed.length)}</mark>
      {text.slice(index + trimmed.length)}
    </>
  );
}
