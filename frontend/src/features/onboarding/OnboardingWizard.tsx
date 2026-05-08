/** OnboardingWizard — premier démarrage après signup.
 *
 *  3 étapes :
 *   1. Choix du mode : Local (machine perso) vs Cloud (multi-devices)
 *      NB : en build unique cloud, seul Cloud s'affiche.
 *   2. Connecter 1 compte email (Gmail OAuth / Microsoft OAuth).
 *   3. Premier sync — redirige vers l'appli quand >= 10 messages sont arrivés.
 *
 *  État stocké dans localStorage pour résister au F5, pas côté serveur.
 */
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { get } from "../../api/client";
import { useAuthStore } from "../../stores/authStore";

type Step = "mode" | "connect" | "sync";

interface SyncStatus { messages_synced: number; accounts: number; }

const LS_KEY = "pli_onboarding_step";

export default function OnboardingWizard() {
  const nav = useNavigate();
  const { user } = useAuthStore();
  const [step, setStep] = useState<Step>((localStorage.getItem(LS_KEY) as Step) ?? "mode");

  useEffect(() => { localStorage.setItem(LS_KEY, step); }, [step]);

  function finish() {
    localStorage.removeItem(LS_KEY);
    nav("/", { replace: true });
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white flex items-center justify-center p-4">
      <div className="w-full max-w-xl rounded-xl bg-white p-8 shadow-sm">
        <ProgressDots current={step} />
        <h1 className="text-2xl font-semibold mt-6 mb-2">
          Bienvenue {user?.email?.split("@")[0]}, configurons PLI.
        </h1>

        {step === "mode" && <ModeStep onNext={() => setStep("connect")} />}
        {step === "connect" && <ConnectStep onNext={() => setStep("sync")} />}
        {step === "sync" && <SyncStep onDone={finish} />}
      </div>
    </div>
  );
}

function ProgressDots({ current }: { current: Step }) {
  const order: Step[] = ["mode", "connect", "sync"];
  return (
    <div className="flex gap-2">
      {order.map((s, i) => (
        <div
          key={s}
          className={`h-1.5 flex-1 rounded-full ${
            order.indexOf(current) >= i ? "bg-indigo-600" : "bg-gray-200"
          }`}
        />
      ))}
    </div>
  );
}

function ModeStep({ onNext }: { onNext: () => void }) {
  // En build cloud, seul Cloud est visible ; en build local, seul Local.
  const mode = (import.meta.env.VITE_PLI_MODE as string | undefined) ?? "cloud";
  return (
    <div>
      <p className="text-gray-600 mb-6">
        Deux saveurs de PLI — choisissez celle qui vous ressemble.
      </p>
      <div className="rounded-lg border border-indigo-200 bg-indigo-50 p-4 mb-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="font-medium">{mode === "local" ? "PLI Local" : "PLI Cloud"}</div>
            <p className="text-sm text-gray-600 mt-1">
              {mode === "local"
                ? "Vos données restent sur votre machine. Chiffrement SQLCipher. Aucun serveur Anthropic ou tiers n'y a accès."
                : "Synchro entre vos appareils, hébergé en Europe (Fly.io · Paris). Chiffrement at-rest côté base."}
            </p>
          </div>
          <div className="text-xs rounded-full bg-indigo-600 text-white px-2 py-0.5">Sélectionné</div>
        </div>
      </div>
      <button onClick={onNext} className="w-full rounded-lg bg-indigo-600 text-white py-2 font-semibold">
        Continuer
      </button>
    </div>
  );
}

function ConnectStep({ onNext }: { onNext: () => void }) {
  return (
    <div>
      <p className="text-gray-600 mb-6">Connectez votre premier compte email.</p>
      <div className="space-y-3">
        <a
          href="/api/auth/gmail/start"
          className="flex items-center justify-center gap-2 rounded-lg border border-gray-300 py-2.5 font-medium hover:bg-gray-50"
        >
          <span>Continuer avec Google</span>
        </a>
        <a
          href="/api/auth/microsoft/start"
          className="flex items-center justify-center gap-2 rounded-lg border border-gray-300 py-2.5 font-medium hover:bg-gray-50"
        >
          <span>Continuer avec Microsoft</span>
        </a>
      </div>
      <p className="text-xs text-gray-500 mt-6">
        PLI ne lit vos emails que pour vous les afficher. Aucune donnée n'est partagée avec des tiers.
      </p>
      <button onClick={onNext} className="mt-6 text-sm text-indigo-600">Plus tard →</button>
    </div>
  );
}

function SyncStep({ onDone }: { onDone: () => void }) {
  const [sync, setSync] = useState<SyncStatus | null>(null);
  useEffect(() => {
    let alive = true;
    async function poll() {
      try {
        const s = await get<SyncStatus>("/sync/status");
        if (!alive) return;
        setSync(s);
        if (s.messages_synced >= 10 || s.accounts === 0) return;  // good enough
        setTimeout(poll, 1500);
      } catch { /* ignore */ }
    }
    poll();
    return () => { alive = false; };
  }, []);

  const pct = sync ? Math.min(100, Math.round(sync.messages_synced / 10 * 100)) : 0;

  return (
    <div>
      <p className="text-gray-600 mb-6">On récupère vos derniers messages…</p>
      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div className="h-full bg-indigo-600 transition-all duration-500" style={{ width: `${pct}%` }} />
      </div>
      <p className="text-sm text-gray-500 mt-2">
        {sync ? `${sync.messages_synced} message(s) synchronisé(s)` : "…"}
      </p>
      <button onClick={onDone} className="mt-6 w-full rounded-lg bg-indigo-600 text-white py-2 font-semibold">
        Ouvrir ma boîte
      </button>
    </div>
  );
}
