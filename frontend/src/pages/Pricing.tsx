/** Pricing — comparaison Free vs Plus + CTA Checkout.
 *  - User non connecté : CTA → /auth/signup?after=checkout&plan=...
 *  - User connecté     : POST /billing/checkout → redirige vers Stripe Checkout.
 */
import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { post } from "../api/client";
import { useAuthStore } from "../stores/authStore";

type Cycle = "monthly" | "yearly";

const PRICES: Record<Cycle, { amount: string; period: string; hint?: string }> = {
  monthly: { amount: "9 €", period: "/mois" },
  yearly: { amount: "8 €", period: "/mois", hint: "Facturé 96 € / an — 2 mois offerts" },
};

const FEATURES_FREE = [
  "1 compte email",
  "30 derniers jours",
  "Recherche basique",
  "Chiffrement local",
];

const FEATURES_PLUS = [
  "Comptes email illimités",
  "Historique complet (tous les messages)",
  "Recherche plein texte instantanée",
  "Règles & workflows conversationnels",
  "Pièces jointes jusqu'à 50 Mo",
  "Support prioritaire (< 24 h)",
  "Licence offline (Local)",
];

export default function PricingPage() {
  const nav = useNavigate();
  const [cycle, setCycle] = useState<Cycle>("yearly");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const { user } = useAuthStore();

  async function startCheckout() {
    if (!user) {
      nav(`/auth/signup?after=checkout&plan=${cycle}`);
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      const r = await post<{ url: string }>("/billing/checkout", { plan: cycle });
      window.location.href = r.url;
    } catch {
      setErr("Impossible de démarrer le paiement — réessayez.");
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-16 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-3">Des prix simples, pas de piège.</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            PLI reste 100 % utilisable gratuitement. Passez sur Plus quand vous avez besoin de
            plus de comptes, plus d'historique ou des workflows avancés. Annulable en 1 clic.
          </p>
        </div>

        <div className="flex justify-center mb-8">
          <div className="inline-flex rounded-full bg-gray-200 p-1">
            <button
              onClick={() => setCycle("monthly")}
              className={`px-5 py-1.5 rounded-full text-sm font-medium ${cycle === "monthly" ? "bg-white shadow" : "text-gray-600"}`}
            >Mensuel</button>
            <button
              onClick={() => setCycle("yearly")}
              className={`px-5 py-1.5 rounded-full text-sm font-medium ${cycle === "yearly" ? "bg-white shadow" : "text-gray-600"}`}
            >Annuel <span className="text-emerald-600 text-xs ml-1">−17 %</span></button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Free */}
          <div className="rounded-xl bg-white p-8 shadow-sm border border-gray-200">
            <h2 className="text-lg font-semibold mb-1">Free</h2>
            <p className="text-3xl font-bold mb-1">0 €</p>
            <p className="text-sm text-gray-500 mb-6">Pour toujours.</p>
            <ul className="space-y-2 text-sm text-gray-700 mb-6">
              {FEATURES_FREE.map((f) => <li key={f}>✓ {f}</li>)}
            </ul>
            {user ? (
              <Link to="/" className="block text-center rounded-lg border border-gray-300 py-2 font-medium">
                Vous utilisez déjà Free
              </Link>
            ) : (
              <Link to="/auth/signup" className="block text-center rounded-lg border border-gray-300 py-2 font-medium">
                Commencer gratuitement
              </Link>
            )}
          </div>

          {/* Plus */}
          <div className="rounded-xl bg-indigo-600 text-white p-8 shadow-md">
            <div className="flex items-center justify-between mb-1">
              <h2 className="text-lg font-semibold">Plus</h2>
              <span className="text-xs bg-white/20 px-2 py-0.5 rounded-full">14 jours d'essai</span>
            </div>
            <p className="text-3xl font-bold">
              {PRICES[cycle].amount}
              <span className="text-base font-normal opacity-80">{PRICES[cycle].period}</span>
            </p>
            <p className="text-sm opacity-80 mb-6 h-5">{PRICES[cycle].hint ?? ""}</p>
            <ul className="space-y-2 text-sm mb-6">
              {FEATURES_PLUS.map((f) => <li key={f}>✓ {f}</li>)}
            </ul>
            <button
              onClick={startCheckout}
              disabled={busy}
              className="w-full rounded-lg bg-white text-indigo-700 py-2 font-semibold disabled:opacity-50"
            >
              {busy ? "…" : user ? "Passer sur Plus" : "Démarrer mon essai"}
            </button>
            {err && <p className="text-xs text-red-200 mt-2">{err}</p>}
          </div>
        </div>

        <p className="text-center text-xs text-gray-500 mt-8">
          Paiements traités par Stripe. Aucun numéro de carte n'est stocké sur nos serveurs.
        </p>
      </div>
    </div>
  );
}
