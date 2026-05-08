/** PaywallModal — affiché quand l'utilisateur tente une action réservée à Plus.
 *  Ex : ajouter un 2e compte email, rechercher > 30 j, créer une règle.
 *
 *  L'appelant passe un `reason` qui détermine le texte — on ne veut pas de
 *  surprise, on explique précisément *pourquoi* c'est bloqué.
 */
import { useNavigate } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";

export type PaywallReason =
  | "multiple_accounts"
  | "full_history"
  | "fts_search"
  | "rules"
  | "large_attachment"
  | "offline_license";

const COPY: Record<PaywallReason, { title: string; body: string }> = {
  multiple_accounts: {
    title: "Ajoutez autant de comptes que vous voulez",
    body: "Le plan Free inclut 1 compte email. PLI Plus vous permet de centraliser tous vos comptes — pro, perso, alias.",
  },
  full_history: {
    title: "Accédez à tout votre historique",
    body: "Le plan Free garde les 30 derniers jours en sync. PLI Plus télécharge l'intégralité de vos messages.",
  },
  fts_search: {
    title: "Recherche plein texte instantanée",
    body: "Le plan Free cherche dans les objets et expéditeurs. PLI Plus indexe tout le contenu — 10 ms pour retrouver n'importe quoi.",
  },
  rules: {
    title: "Règles & workflows conversationnels",
    body: "Étiqueter, archiver, transférer automatiquement… PLI Plus tourne des règles comme un pro, sans quitter la conversation.",
  },
  large_attachment: {
    title: "Pièces jointes jusqu'à 50 Mo",
    body: "Le plan Free limite les pièces à 10 Mo. Plus passe à 50 Mo par message.",
  },
  offline_license: {
    title: "Mode hors-ligne",
    body: "PLI Plus inclut une licence offline signée — aucune connexion requise pour utiliser l'appli.",
  },
};

export function PaywallModal({
  open, onClose, reason,
}: { open: boolean; onClose: () => void; reason: PaywallReason }) {
  const nav = useNavigate();
  const { user } = useAuthStore();
  if (!open) return null;
  const copy = COPY[reason];

  return (
    <div className="fixed inset-0 z-50 bg-black/40 flex items-center justify-center p-4" onClick={onClose}>
      <div
        className="max-w-md w-full rounded-xl bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <div className="mb-2 inline-flex items-center gap-2 text-xs font-medium text-indigo-700 bg-indigo-50 px-2 py-1 rounded-full">
          ✨ Fonctionnalité PLI Plus
        </div>
        <h2 className="text-lg font-semibold mb-2">{copy.title}</h2>
        <p className="text-sm text-gray-600 mb-5">{copy.body}</p>
        <div className="flex gap-2">
          <button
            onClick={onClose}
            className="flex-1 rounded-lg border border-gray-300 py-2 text-sm font-medium"
          >Plus tard</button>
          <button
            onClick={() => {
              onClose();
              nav(user?.plan === "plus_trial" ? "/settings/billing" : "/pricing");
            }}
            className="flex-1 rounded-lg bg-indigo-600 text-white py-2 text-sm font-semibold"
          >
            {user?.plan === "plus_trial" ? "Activer l'abonnement" : "Essayer 14 jours"}
          </button>
        </div>
      </div>
    </div>
  );
}
