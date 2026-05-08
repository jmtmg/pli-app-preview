import { useTranslation } from "react-i18next";

/**
 * Thin wrapper to give a namespaced `t` function with a stable signature.
 * Usage: `const t = useT("settings");`  then  `t("my_data.title")`.
 */
export function useT(namespace?: string) {
  const { t } = useTranslation(namespace);
  return t as (key: string, vars?: Record<string, unknown>) => string;
}

export { useTranslation } from "react-i18next";
