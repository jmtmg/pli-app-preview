/** Hook paywall — centralise la logique "cette feature demande Plus".
 *
 *  Usage :
 *    const { check, modalProps } = usePaywall();
 *    if (!check("fts_search")) return;   // bloque + ouvre la modale
 *    // sinon : action libre
 */
import { useState } from "react";
import { isPlusPlan, usePlan } from "../../stores/authStore";
import { PaywallReason } from "./PaywallModal";

/** Features réservées à Plus. Single source of truth pour le frontend. */
const PLUS_ONLY: Set<PaywallReason> = new Set([
  "multiple_accounts",
  "full_history",
  "fts_search",
  "rules",
  "large_attachment",
  "offline_license",
]);

export function usePaywall() {
  const plan = usePlan();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState<PaywallReason>("fts_search");

  function check(r: PaywallReason): boolean {
    if (!PLUS_ONLY.has(r)) return true;
    if (isPlusPlan(plan)) return true;
    setReason(r);
    setOpen(true);
    return false;
  }

  return {
    check,
    modalProps: { open, onClose: () => setOpen(false), reason },
  };
}
