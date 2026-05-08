/** Paramètres → Facturation — état de l'abonnement, bouton "Gérer via Stripe". */
import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { get, post } from "../../api/client";
import { useAuthStore, usePlan } from "../../stores/authStore";

interface Sub {
  plan: string;
  status: string;
  current_period_end: string | null;
  trial_end: string | null;
  cancel_at_period_end: boolean;
}

const PLAN_LABEL: Record<string, string> = {
  free: "Free",
  plus_trial: "Plus — Essai gratuit",
  plus_monthly: "Plus — Abonnement mensuel",
  plus_yearly: "Plus — Abonnement annuel",
};

export default function BillingSettings() {
  const [sub, setSub] = useState<Sub | null | undefined>(undefined);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [sp] = useSearchParams();
  const justPaid = sp.get("status") === "success";
  const plan = usePlan();
  const { refreshMe } = useAuthStore();

  useEffect(() => {
    get<Sub | null>("/billing/subscription")
      .then(setSub)
      .catch(() => setSub(null));
    if (justPaid) refreshMe();
  }, [justPaid, refreshMe]);

  async function openPortal() {
    setBusy(true); setErr(null);
    try {
      const r = await post<{ url: string }>("/billing/portal");
      window.location.href = r.url;
    } catch {
      setErr("Impossible d'ouvrir le portail Stripe — réessayez.");
      setBusy(false);
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-8 px-4">
      <h1 className="text-2xl font-semibold mb-6">Facturation</h1>

      {justPaid && (
        <div className="mb-6 rounded-lg bg-emerald-50 border border-emerald-200 p-3 text-sm text-emerald-800">
          🎉 Paiement confirmé. Bienvenue sur PLI Plus !
        </div>
      )}

      <section className="rounded-xl border border-gray-200 bg-white p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="text-sm text-gray-500">Plan actuel</div>
            <div className="text-xl font-semibold">{PLAN_LABEL[plan] ?? plan}</div>
            {sub?.trial_end && plan === "plus_trial" && (
              <p className="text-sm text-gray-500 mt-1">
                Essai jusqu'au {new Date(sub.trial_end).toLocaleDateString()}.
              </p>
            )}
            {sub?.current_period_end && plan !== "plus_trial" && plan !== "free" && (
              <p className="text-sm text-gray-500 mt-1">
                {sub.cancel_at_period_end ? "Se termine " : "Prochain prélèvement "}
                le {new Date(sub.current_period_end).toLocaleDateString()}.
              </p>
            )}
          </div>
          {plan === "free" && (
            <Link
              to="/pricing"
              className="rounded-lg bg-indigo-600 text-white px-4 py-2 text-sm font-semibold"
            >Passer sur Plus</Link>
          )}
        </div>
      </section>

      {sub && sub.plan !== "free" && (
        <section className="rounded-xl border border-gray-200 bg-white p-6">
          <h2 className="font-semibold mb-2">Gérer mon abonnement</h2>
          <p className="text-sm text-gray-600 mb-4">
            Mettez à jour votre moyen de paiement, téléchargez vos factures ou résiliez via le portail Stripe.
          </p>
          <button
            onClick={openPortal}
            disabled={busy}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium disabled:opacity-50"
          >
            {busy ? "…" : "Ouvrir le portail Stripe"}
          </button>
          {err && <p className="text-xs text-red-600 mt-2">{err}</p>}
        </section>
      )}
    </div>
  );
}
