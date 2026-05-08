/**
 * Widget NPS in-app.
 * Règles :
 * - Déclenché à J+7 d'usage
 * - Max 1×/30 jours
 * - Non bloquant, fermeture libre
 */
import { useEffect, useState } from "react";
import { apiClient } from "@/api/client";
import { useTranslation } from "react-i18next";
import { useUserPrefs } from "@/hooks/useUserPrefs";
import { trackEvent } from "@/api/analytics";

const STORAGE_KEY = "pli.nps.last_dismissed";

export function NPSWidget() {
  const { t } = useTranslation();
  const { prefs } = useUserPrefs();
  const [visible, setVisible] = useState(false);
  const [score, setScore] = useState<number | null>(null);
  const [comment, setComment] = useState("");
  const [sent, setSent] = useState(false);

  useEffect(() => {
    if (!prefs) return;
    const daysSinceSignup = daysBetween(new Date(prefs.created_at), new Date());
    const lastDismissed = prefs.last_nps_dismissed_at
      ? new Date(prefs.last_nps_dismissed_at)
      : null;
    const daysSinceDismiss = lastDismissed ? daysBetween(lastDismissed, new Date()) : Infinity;

    if (daysSinceSignup >= 7 && daysSinceDismiss >= 30) {
      setVisible(true);
      trackEvent("nps_displayed");
    }
  }, [prefs]);

  const submit = async (anonymous: boolean) => {
    if (score === null) return;
    await apiClient.post("/feedback", {
      kind: "nps",
      score,
      message: comment || null,
      app_version: __APP_VERSION__,
      platform: detectPlatform(),
      anonymous,
    });
    trackEvent("nps_submitted", { score });
    setSent(true);
    setTimeout(close, 1800);
  };

  const close = async () => {
    setVisible(false);
    await apiClient.patch("/me/prefs", { last_nps_dismissed_at: new Date().toISOString() });
  };

  if (!visible) return null;

  return (
    <div
      className="fixed bottom-4 right-4 bg-white shadow-lg rounded-xl p-5 w-[360px] max-w-[92vw] border border-gray-100 z-40"
      role="dialog"
      aria-labelledby="nps-title"
    >
      {sent ? (
        <p className="text-sm text-gray-700 py-4 text-center">{t("nps.thanks")}</p>
      ) : (
        <>
          <button
            type="button"
            onClick={close}
            aria-label={t("nps.close")}
            className="absolute top-2 right-3 text-gray-400 hover:text-gray-700"
          >
            ×
          </button>
          <h3 id="nps-title" className="font-semibold text-sm mb-1">
            {t("nps.title")}
          </h3>
          <p className="text-xs text-gray-500 mb-3">{t("nps.subtitle")}</p>

          <ScoreScale value={score} onChange={setScore} />

          {score !== null && (
            <>
              <label className="block text-xs text-gray-600 mt-3 mb-1">
                {promptForScore(score, t)}
              </label>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value.slice(0, 500))}
                rows={3}
                className="w-full border border-gray-200 rounded-lg px-2 py-1 text-sm"
                placeholder={t("nps.comment_placeholder")}
              />
              <div className="flex gap-2 mt-3 justify-end">
                <button
                  type="button"
                  onClick={() => submit(true)}
                  className="text-xs text-gray-600 underline"
                >
                  {t("nps.send_anonymous")}
                </button>
                <button
                  type="button"
                  onClick={() => submit(false)}
                  className="bg-black text-white rounded-lg px-3 py-1.5 text-sm"
                >
                  {t("nps.send")}
                </button>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}

function ScoreScale({
  value,
  onChange,
}: {
  value: number | null;
  onChange: (n: number) => void;
}) {
  return (
    <div className="grid grid-cols-11 gap-1">
      {Array.from({ length: 11 }, (_, i) => (
        <button
          key={i}
          type="button"
          onClick={() => onChange(i)}
          className={`h-9 text-xs rounded-md border ${
            value === i ? "bg-black text-white border-black" : "bg-white border-gray-200 hover:border-gray-400"
          }`}
          aria-label={`score ${i}`}
        >
          {i}
        </button>
      ))}
    </div>
  );
}

function promptForScore(score: number, t: (k: string) => string): string {
  if (score <= 6) return t("nps.prompt.detractor");
  if (score <= 8) return t("nps.prompt.passive");
  return t("nps.prompt.promoter");
}

function daysBetween(a: Date, b: Date): number {
  return Math.floor((b.getTime() - a.getTime()) / 86400000);
}

function detectPlatform(): "pwa-mobile" | "pwa-desktop" {
  return window.matchMedia("(pointer: coarse)").matches ? "pwa-mobile" : "pwa-desktop";
}

declare const __APP_VERSION__: string;
