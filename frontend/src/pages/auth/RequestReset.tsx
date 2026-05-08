import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import { AuthLayout } from "./components/AuthLayout";

export default function RequestResetPage() {
  const { requestPasswordReset } = useAuthStore();
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await requestPasswordReset(email);
    } finally {
      setLoading(false);
      setSent(true);  // même en cas d'erreur : silent on unknown email (side-channel safety)
    }
  }

  if (sent) {
    return (
      <AuthLayout title="Vérifiez votre boîte de réception">
        <p>
          Si un compte existe avec <strong>{email}</strong>, vous recevrez un lien
          de réinitialisation dans les minutes qui viennent.
        </p>
        <Link to="/auth/login" className="mt-6 inline-block text-indigo-600">
          Retour à la connexion
        </Link>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout title="Mot de passe oublié">
      <form onSubmit={submit} className="space-y-4">
        <label className="block">
          <span className="text-sm font-medium">Email</span>
          <input
            type="email" required value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
          />
        </label>
        <button
          disabled={loading}
          className="w-full rounded-lg bg-indigo-600 py-2 font-medium text-white disabled:opacity-40"
        >
          {loading ? "…" : "M'envoyer un lien"}
        </button>
        <Link to="/auth/login" className="text-sm text-indigo-600">Retour à la connexion</Link>
      </form>
    </AuthLayout>
  );
}
