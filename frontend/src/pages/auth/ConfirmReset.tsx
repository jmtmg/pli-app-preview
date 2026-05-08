import { FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import { PasswordInput } from "./components/PasswordInput";
import { AuthLayout } from "./components/AuthLayout";

export default function ConfirmResetPage() {
  const nav = useNavigate();
  const [sp] = useSearchParams();
  const token = sp.get("token") ?? "";
  const { confirmPasswordReset } = useAuthStore();
  const [pwd, setPwd] = useState("");
  const [confirm, setConfirm] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    if (pwd !== confirm) { setErr("Les mots de passe ne correspondent pas."); return; }
    if (pwd.length < 12) { setErr("Le mot de passe doit faire au moins 12 caractères."); return; }
    setLoading(true);
    try {
      await confirmPasswordReset(token, pwd);
      nav("/auth/login?reset=ok", { replace: true });
    } catch {
      setErr("Ce lien est invalide ou a expiré. Demandez-en un nouveau.");
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <AuthLayout title="Lien invalide">
        <p className="text-red-600">Ce lien n'est pas valide.</p>
        <Link to="/auth/password-reset" className="mt-4 inline-block text-indigo-600">
          Demander un nouveau lien
        </Link>
      </AuthLayout>
    );
  }

  return (
    <AuthLayout title="Choisir un nouveau mot de passe">
      <form onSubmit={submit} className="space-y-4">
        <PasswordInput value={pwd} onChange={setPwd} label="Nouveau mot de passe" autoComplete="new-password" />
        <PasswordInput value={confirm} onChange={setConfirm} label="Confirmation" autoComplete="new-password" />
        {err && <p className="text-sm text-red-600">{err}</p>}
        <p className="text-xs text-gray-500">
          Toutes vos sessions actives seront déconnectées dès l'enregistrement du nouveau mot de passe.
        </p>
        <button
          disabled={loading}
          className="w-full rounded-lg bg-indigo-600 py-2 font-medium text-white disabled:opacity-40"
        >
          {loading ? "…" : "Enregistrer"}
        </button>
      </form>
    </AuthLayout>
  );
}
