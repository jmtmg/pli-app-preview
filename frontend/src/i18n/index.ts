import i18n from "i18next";
import LanguageDetector from "i18next-browser-languagedetector";
import HttpBackend from "i18next-http-backend";
import { initReactI18next } from "react-i18next";

/**
 * i18n bootstrap for PLI.
 *
 * - FR as reference (fallback)
 * - EN fully translated (reviewed by native speaker before release)
 * - Namespace-split JSON files loaded on demand (code splitting)
 * - Detection order: user setting (server-side) > localStorage > navigator
 */

export const SUPPORTED_LOCALES = ["fr", "en"] as const;
export type Locale = (typeof SUPPORTED_LOCALES)[number];

const NAMESPACES = ["common", "settings", "compose", "conversation", "errors", "legal"] as const;

i18n
  .use(HttpBackend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    fallbackLng: "fr",
    supportedLngs: [...SUPPORTED_LOCALES],
    nonExplicitSupportedLngs: true,
    load: "languageOnly",
    ns: NAMESPACES as unknown as string[],
    defaultNS: "common",
    backend: {
      loadPath: "/locales/{{lng}}/{{ns}}.json",
    },
    detection: {
      order: ["querystring", "cookie", "localStorage", "navigator"],
      lookupQuerystring: "lang",
      lookupCookie: "pli_locale",
      lookupLocalStorage: "pli_locale",
      caches: ["cookie", "localStorage"],
      cookieOptions: { path: "/", sameSite: "strict", secure: true },
    },
    interpolation: { escapeValue: false }, // React already escapes
    returnEmptyString: false,
    react: { useSuspense: true },
  });

export async function changeLanguage(lng: Locale): Promise<void> {
  await i18n.changeLanguage(lng);
  // Persist server-side (for multi-device coherence).
  try {
    await fetch("/api/settings/locale", {
      method: "PATCH",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ locale: lng }),
    });
  } catch {
    /* silent: client-side persistence still takes effect */
  }
  document.documentElement.lang = lng;
}

export default i18n;
