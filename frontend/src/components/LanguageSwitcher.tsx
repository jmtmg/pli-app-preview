import { useTranslation } from "react-i18next";
import { changeLanguage, SUPPORTED_LOCALES, type Locale } from "@/i18n";

export function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const current = (i18n.resolvedLanguage ?? "fr") as Locale;

  return (
    <label className="inline-flex items-center gap-2 text-sm">
      <span className="sr-only">Language</span>
      <select
        value={current}
        onChange={(e) => changeLanguage(e.target.value as Locale)}
        className="rounded-md border border-[var(--color-border-default)] bg-[var(--color-bg-elevated)] px-2 py-1 text-sm"
      >
        {SUPPORTED_LOCALES.map((l) => (
          <option key={l} value={l}>
            {l === "fr" ? "Français" : "English"}
          </option>
        ))}
      </select>
    </label>
  );
}
