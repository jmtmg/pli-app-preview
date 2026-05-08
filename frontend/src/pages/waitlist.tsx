/**
 * Page publique /waitlist — inscription beta privée.
 */
import { useState } from "react";
import { apiClient } from "@/api/client";
import { useTranslation } from "react-i18next";

export default function WaitlistPage() {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [motivation, setMotivation] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiClient.post("/waitlist", {
        email,
        first_name: firstName || null,
        motivation: motivation || null,
        source: new URLSearchParams(window.location.search).get("source"),
      });
      setSent(true);
    } catch (error: unknown) {
      setError(getApiDetail(error) ?? t("waitlist.error_generic"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-white flex flex-col items-center justify-center px-6">
      <section className="max-w-lg w-full">
        <h1 className="text-3xl font-semibold mb-2">{t("waitlist.title")}</h1>
        <p className="text-gray-600 mb-8">{t("waitlist.subtitle")}</p>

        {sent ? (
          <div className="bg-green-50 border border-green-200 rounded-xl p-5 text-sm text-green-800">
            {t("waitlist.sent")}
          </div>
        ) : (
          <form onSubmit={submit} className="flex flex-col gap-3">
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder={t("waitlist.email_placeholder")}
              className="border border-gray-200 rounded-lg px-3 py-2"
            />
            <input
              type="text"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder={t("waitlist.first_name_placeholder")}
              className="border border-gray-200 rounded-lg px-3 py-2"
            />
            <textarea
              value={motivation}
              onChange={(e) => setMotivation(e.target.value.slice(0, 280))}
              rows={3}
              placeholder={t("waitlist.motivation_placeholder")}
              className="border border-gray-200 rounded-lg px-3 py-2"
            />
            <p className="text-xs text-gray-500">
              {t("waitlist.privacy")}
            </p>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button
              type="submit"
              disabled={loading || !email}
              className="bg-black text-white rounded-lg py-2 disabled:opacity-50"
            >
              {loading ? t("waitlist.sending") : t("waitlist.submit")}
            </button>
          </form>
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
