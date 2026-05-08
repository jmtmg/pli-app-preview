/** Client HTTP vers le backend FastAPI — M2 : JWT + refresh rotation.
 *
 * En dev : requests passent par le proxy Vite (/api → :8000).
 * En prod Local : PLI backend sur un port random, main process écrit dans localStorage.
 * En prod Cloud : URL pointée par VITE_API_URL (ou même origine par défaut).
 *
 * Stratégie d'auth :
 *  - access token en mémoire uniquement (JWT HS256, 15 min, jti révocable)
 *  - refresh token en cookie httpOnly+SameSite=Lax+Secure, path=/auth
 *  - sur 401, on rejoue une fois via /auth/refresh avant de propager l'erreur
 */

let accessToken: string | null = null;

export function setAccessToken(tok: string | null) {
  accessToken = tok;
}
export function getAccessToken() {
  return accessToken;
}

const BASE = import.meta.env.DEV
  ? "/api"
  : (import.meta.env.VITE_API_URL as string | undefined)
    ?? localStorage.getItem("pli_backend_url")
    ?? "";

type InitOpts = RequestInit & { retryOn401?: boolean };

async function rawFetch<T>(path: string, init: InitOpts): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string> | undefined ?? {}),
  };
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`;
  const res = await fetch(`${BASE}${path}`, {
    credentials: "include",  // envoi du cookie refresh
    ...init,
    headers,
  });
  if (res.status === 401 && (init.retryOn401 ?? true) && !path.startsWith("/auth/")) {
    const refreshed = await tryRefresh();
    if (refreshed) {
      return rawFetch(path, { ...init, retryOn401: false });
    }
  }
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new ApiError(res.status, `HTTP ${res.status} on ${path}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export class ApiError extends Error {
  constructor(public status: number, msg: string) {
    super(msg);
  }
}

async function tryRefresh(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE}/auth/refresh`, {
      method: "POST",
      credentials: "include",
    });
    if (!res.ok) return false;
    const data = await res.json() as { access_token: string };
    accessToken = data.access_token;
    return true;
  } catch {
    return false;
  }
}

export async function api<T>(path: string, init?: InitOpts): Promise<T> {
  return rawFetch<T>(path, init ?? {});
}

export const get   = <T>(p: string)                  => api<T>(p);
export const post  = <T>(p: string, body?: unknown)  => api<T>(p, { method: "POST", body: body ? JSON.stringify(body) : undefined });
export const patch = <T>(p: string, body?: unknown)  => api<T>(p, { method: "PATCH", body: body ? JSON.stringify(body) : undefined });
export const del   = <T>(p: string)                  => api<T>(p, { method: "DELETE" });
