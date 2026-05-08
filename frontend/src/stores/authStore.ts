/** authStore — état d'authentification global (Zustand).
 *  Responsabilités :
 *    - connaître l'utilisateur courant (email, plan, mode local/cloud)
 *    - persister le fait qu'on était loggué (pas le token) pour savoir s'il
 *      faut appeler /auth/refresh au boot
 *    - exposer login / signup / logout / verifyEmail / requestReset / confirmReset
 */
import { create } from "zustand";
import { post, get, setAccessToken } from "../api/client";

export type Plan = "free" | "plus_trial" | "plus_monthly" | "plus_yearly";

export interface CurrentUser {
  id: string;
  email: string;
  plan: Plan;
  emailVerified: boolean;
  mode: "local" | "cloud";
}

interface AuthState {
  user: CurrentUser | null;
  loading: boolean;

  boot: () => Promise<void>;
  signup: (email: string, password: string) => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  verifyEmail: (token: string) => Promise<void>;
  requestPasswordReset: (email: string) => Promise<void>;
  confirmPasswordReset: (token: string, newPassword: string) => Promise<void>;
  refreshMe: () => Promise<void>;
}

const PERSIST_FLAG = "pli_was_authed";

export const useAuthStore = create<AuthState>((set, get_) => ({
  user: null,
  loading: true,

  async boot() {
    set({ loading: true });
    const wasAuthed = localStorage.getItem(PERSIST_FLAG) === "1";
    if (!wasAuthed) {
      set({ user: null, loading: false });
      return;
    }
    try {
      // tente /auth/refresh via le cookie httpOnly
      const r = await post<{ access_token: string }>("/auth/refresh");
      setAccessToken(r.access_token);
      await get_().refreshMe();
    } catch {
      localStorage.removeItem(PERSIST_FLAG);
      setAccessToken(null);
      set({ user: null });
    } finally {
      set({ loading: false });
    }
  },

  async signup(email, password) {
    await post("/auth/signup", { email, password });
    // Après signup, on laisse l'utilisateur vérifier son email puis login
  },

  async login(email, password) {
    const r = await post<{ access_token: string }>("/auth/login", { email, password });
    setAccessToken(r.access_token);
    localStorage.setItem(PERSIST_FLAG, "1");
    await get_().refreshMe();
  },

  async logout() {
    try { await post("/auth/logout"); } catch { /* best-effort */ }
    setAccessToken(null);
    localStorage.removeItem(PERSIST_FLAG);
    set({ user: null });
  },

  async verifyEmail(token) {
    await post("/auth/verify", { token });
    if (get_().user) await get_().refreshMe();
  },

  async requestPasswordReset(email) {
    await post("/auth/password-reset/request", { email });
  },

  async confirmPasswordReset(token, newPassword) {
    await post("/auth/password-reset/confirm", { token, password: newPassword });
  },

  async refreshMe() {
    const me = await get<CurrentUser>("/auth/me");
    set({ user: me });
  },
}));

/** Hook pratique : renvoie true seulement si user est connecté ET email vérifié. */
export function useIsAuthenticated(): boolean {
  return useAuthStore((s) => !!s.user && s.user.emailVerified);
}

/** Hook pratique : renvoie le plan courant avec fallback `free`. */
export function usePlan(): Plan {
  return useAuthStore((s) => s.user?.plan ?? "free");
}

export function isPaidPlan(p: Plan): boolean {
  return p === "plus_monthly" || p === "plus_yearly";
}

export function isPlusPlan(p: Plan): boolean {
  return p !== "free";
}
