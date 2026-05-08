/**
 * Page /invited?code=XXXX — redemption d'un code d'invitation beta.
 * Exige un compte (sinon redirige vers signup avec code en param).
 */
import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { apiClient } from "@/api/client";
import { useTranslation } from "react-i18next";
import { useUser } from "@/hooks/useUser";

export default function InvitedPage() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const code = (params.get("code") ?? "").trim().toUpperCase();
  const user = useUser();
  const nav = useNavigate();
  const [state, setState] = useState<"idle" | "loading" | "ok" | "error">("idle");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Utilisateur non connecté → on passe le code au signup
    if (!user) {
      nav(`/signup?invite=${encodeURIComponent(code)}`, { replace: true });
    }
  }, [user, code, nav]);

  const redeem = async () => {
    setState("loading");
    setError(null);
    try {
      await apiClient.post("/invitations/redeem", { code });
      setState("ok");
      setTimeout(() => nav("/", { replace: true }), 1500);
    } catch (error: unknown) {
      setState("error");
      setError(getApiDetail(error) ?? t("invited.error_generic"));
    }
  };

  if (!code) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <p className="text-sm text-gray-600">{t("invited.missing_code")}</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6 bg-white">
      <section className="max-w-md w-full text-center">
        <h1 className="text-2xl font-semibold mb-2">{t("invited.title")}</h1>
        <p className="text-gray-600 mb-6">{t("invited.subtitle", { code })}</p>

        {state === "ok" && (
          <div className="bg-green-50 border border-green-200 rounded-xl p-5 text-sm text-green-800">
            {t("invited.ok")}
          </div>
        )}
        {state === "error" && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-5 text-sm text-red-800 mb-4">
            {error}
            <div className="mt-3">
              <a href="/waitlist" className="underline text-red-700">
                {t("invited.back_to_waitlist")}
              </a>
            </div>
          </div>
        )}
        {state !== "ok" && (
          <button
            type="button"
            onClick={redeem}
            disabled={state === "loading"}
            className="bg-black text-white rounded-lg px-4 py-2 text-sm disabled:opacity-50"
          >
            {state === "loading" ? t("invited.redeeming") : t("invited.redeem")}
          </button>
        )}
      </section>
    </main>
  );
}

function getApiDetail(error: unknown): string | undefined {
  if (typeof error !== "object" || error === null || !("response" in error)) return undefined;
  const response = (error as { response?: { data?: { detail?: unknown } } }).response;
  return typeof response?.data?.detail === "string" ? response.data.detail : undefined;
}
