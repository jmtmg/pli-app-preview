/**
 * Tour produit 5 étapes — déclenché au premier lancement après onboarding account.
 * Skippable, persisté via API user_prefs.tour_completed_at.
 */
import { useEffect, useState } from "react";
import { apiClient } from "@/api/client";
import { useTranslation } from "react-i18next";
import { useUserPrefs } from "@/hooks/useUserPrefs";
import { trackEvent } from "@/api/analytics";

type Step = {
  key: string;
  target: string; // CSS selector de l'élément à pointer
  titleKey: string;
  bodyKey: string;
  placement: "bottom" | "top" | "left" | "right";
};

const STEPS: Step[] = [
  {
    key: "list",
    target: "[data-tour='conversation-list']",
    titleKey: "tour.list.title",
    bodyKey: "tour.list.body",
    placement: "right",
  },
  {
    key: "filters",
    target: "[data-tour='filters']",
    titleKey: "tour.filters.title",
    bodyKey: "tour.filters.body",
    placement: "bottom",
  },
  {
    key: "swipe",
    target: "[data-tour='swipe-card']",
    titleKey: "tour.swipe.title",
    bodyKey: "tour.swipe.body",
    placement: "left",
  },
  {
    key: "composer",
    target: "[data-tour='composer-fab']",
    titleKey: "tour.composer.title",
    bodyKey: "tour.composer.body",
    placement: "top",
  },
  {
    key: "search",
    target: "[data-tour='search-fab']",
    titleKey: "tour.search.title",
    bodyKey: "tour.search.body",
    placement: "bottom",
  },
];

export function Tour() {
  const { prefs, refetch } = useUserPrefs();
  const [idx, setIdx] = useState(0);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (prefs && !prefs.tour_completed_at) {
      setVisible(true);
      trackEvent("tour_started");
    }
  }, [prefs]);

  const finish = async (skipped: boolean) => {
    await apiClient.patch("/me/prefs", { tour_completed_at: new Date().toISOString() });
    trackEvent(skipped ? "tour_skipped" : "tour_completed", { last_step: idx });
    setVisible(false);
    refetch();
  };

  if (!visible) return null;
  const step = STEPS[idx];

  return (
    <div className="fixed inset-0 z-50 pointer-events-none">
      {/* Overlay semi-transparent */}
      <div
        className="absolute inset-0 bg-black/40 pointer-events-auto"
        onClick={() => finish(true)}
        aria-hidden
      />

      <TourBubble
        step={step}
        stepIndex={idx}
        total={STEPS.length}
        onNext={() => {
          if (idx === STEPS.length - 1) finish(false);
          else setIdx(idx + 1);
          trackEvent("tour_step_advanced", { step: idx + 1 });
        }}
        onSkip={() => finish(true)}
      />
    </div>
  );
}

function TourBubble({
  step,
  stepIndex,
  total,
  onNext,
  onSkip,
}: {
  step: Step;
  stepIndex: number;
  total: number;
  onNext: () => void;
  onSkip: () => void;
}) {
  const { t } = useTranslation();
  const [rect, setRect] = useState<DOMRect | null>(null);

  useEffect(() => {
    const el = document.querySelector(step.target);
    if (el) {
      setRect(el.getBoundingClientRect());
      el.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [step]);

  const style = bubblePosition(rect, step.placement);

  return (
    <div
      className="absolute bg-white rounded-xl shadow-lg p-4 w-80 pointer-events-auto"
      style={style}
      role="dialog"
      aria-labelledby={`tour-${step.key}-title`}
    >
      <h3 id={`tour-${step.key}-title`} className="font-semibold text-base mb-2">
        {t(step.titleKey)}
      </h3>
      <p className="text-sm text-gray-700 mb-4">{t(step.bodyKey)}</p>

      <div className="flex items-center justify-between">
        <button
          type="button"
          onClick={onSkip}
          className="text-xs text-gray-500 underline"
        >
          {t("tour.skip")}
        </button>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">
            {stepIndex + 1} / {total}
          </span>
          <button
            type="button"
            onClick={onNext}
            className="bg-black text-white rounded-lg px-3 py-1.5 text-sm"
          >
            {stepIndex === total - 1 ? t("tour.finish") : t("tour.next")}
          </button>
        </div>
      </div>
    </div>
  );
}

function bubblePosition(
  rect: DOMRect | null,
  placement: Step["placement"]
): React.CSSProperties {
  if (!rect) return { top: "50%", left: "50%", transform: "translate(-50%, -50%)" };
  const gap = 12;
  switch (placement) {
    case "bottom":
      return { top: rect.bottom + gap, left: rect.left };
    case "top":
      return { top: rect.top - gap, left: rect.left, transform: "translateY(-100%)" };
    case "left":
      return { top: rect.top, left: rect.left - gap, transform: "translateX(-100%)" };
    case "right":
      return { top: rect.top, left: rect.right + gap };
  }
}
