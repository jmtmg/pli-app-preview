import { FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import { PasswordInput } from "./components/PasswordInput";
import { AuthLayout } from "./components/AuthLayout";

export default function LoginPage() {
  const nav = useNavigate();
  const [sp] = useSearchParams();
  const redirectTo = sp.get("next") ?? "/";
  const { login } = useAuthStore();
  const [email, setEmail] = useState("");
  const [pwd, setPwd] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      await login(email, pwd);
      nav(redirectTo, { replace: true });
    } catch (e: any) {
      if (e.message.includes("403")) {
        setErr("Votre email n'est pas encore vérifié. Vérifiez votre boîte de réception.");
      } else {
        setErr("Email ou mot de passe incorrect.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout title="Se connecter">
      <form onSubmit={submit} className="space-y-4">
        <label className="block">
          <span className="text-sm font-medium">Email</span>
          <input
            type="email" required autoComplete="email"
            value={email} onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2"
          />
        </label>
        <PasswordInput value={pwd} onChange={setPwd} label="Mot de passe" autoComplete="current-password" />
        {err && <p className="text-sm text-red-600">{err}</p>}
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-indigo-600 py-2 font-medium text-white disabled:opacity-40"
        >
          {loading ? "…" : "Se connecter"}
        </button>
        <div className="flex justify-between text-sm">
          <Link to="/auth/password-reset" className="text-indigo-600">Mot de passe oublié ?</Link>
          <Link to="/auth/signup" className="text-indigo-600">Créer un compte</Link>
        </div>
      </form>
    </AuthLayout>
  );
}
