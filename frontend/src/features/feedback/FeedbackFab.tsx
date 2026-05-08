/**
 * Bouton flottant "Signaler" (bug/suggestion).
 * Visible uniquement pour les beta users (batch_number != null).
 */
import { useState } from "react";
import { apiClient } from "@/api/client";
import { useTranslation } from "react-i18next";
import { useUser } from "@/hooks/useUser";
import { trackEvent } from "@/api/analytics";

type Kind = "bug" | "suggestion" | "other";

export function FeedbackFab() {
  const { t } = useTranslation();
  const user = useUser();
  const [open, setOpen] = useState(false);
  const [kind, setKind] = useState<Kind>("bug");
  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [sent, setSent] = useState(false);

  if (!user?.batch_number) return null; // non-beta → rien

  const submit = async () => {
    if (!message.trim()) return;
    setSubmitting(true);
    try {
      await apiClient.post("/feedback", { kind, message, platform: detectPlatform() });
      trackEvent("feedback_submitted", { kind });
      setSent(true);
      setTimeout(() => {
        setOpen(false);
        setSent(false);
        setMessage("");
      }, 1600);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label={t("feedback.fab.open")}
        className="fixed bottom-24 right-4 bg-white border border-gray-200 shadow rounded-full h-11 w-11 flex items-center justify-center z-30"
      >
        💬
      </button>

      {open && (
        <div
          role="dialog"
          aria-labelledby="feedback-title"
          className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40"
          onClick={() => setOpen(false)}
        >
          <div
            className="bg-white rounded-xl p-5 w-[400px] max-w-[92vw]"
            onClick={(e) => e.stopPropagation()}
          >
            {sent ? (
              <p className="text-sm text-gray-700 py-6 text-center">{t("feedback.thanks")}</p>
            ) : (
              <>
                <h3 id="feedback-title" className="font-semibold text-sm mb-3">
                  {t("feedback.title")}
                </h3>
                <div className="flex gap-1 mb-3">
                  {(["bug", "suggestion", "other"] as const).map((k) => (
                    <button
                      key={k}
                      type="button"
                      onClick={() => setKind(k)}
                      className={`flex-1 text-xs py-1.5 rounded-md border ${
                        kind === k ? "bg-black text-white border-black" : "bg-white border-gray-200"
                      }`}
                    >
                      {t(`feedback.kind.${k}`)}
                    </button>
                  ))}
                </div>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value.slice(0, 2000))}
                  rows={5}
                  className="w-full border border-gray-200 rounded-lg px-2 py-1 text-sm"
                  placeholder={t("feedback.placeholder")}
                />
                <div className="flex justify-end gap-2 mt-3">
                  <button type="button" onClick={() => setOpen(false)} className="text-xs text-gray-500 underline">
                    {t("common.cancel")}
                  </button>
                  <button
                    type="button"
                    onClick={submit}
                    disabled={submitting || !message.trim()}
                    className="bg-black text-white rounded-lg px-3 py-1.5 text-sm disabled:opacity-50"
                  >
                    {t("feedback.send")}
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}

function detectPlatform() {
  return window.matchMedia("(pointer: coarse)").matches ? "pwa-mobile" : "pwa-desktop";
}
