/** Signup — email + mot de passe. Envoie le lien de vérification. */
import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import { PasswordInput } from "./components/PasswordInput";
import { AuthLayout } from "./components/AuthLayout";

const RULES = [
  { k: "len", t: "≥ 12 caractères", test: (p: string) => p.length >= 12 },
  { k: "upper", t: "1 majuscule", test: (p: string) => /[A-Z]/.test(p) },
  { k: "digit", t: "1 chiffre", test: (p: string) => /\d/.test(p) },
  { k: "sym", t: "1 symbole", test: (p: string) => /[^a-zA-Z0-9]/.test(p) },
];

export default function SignupPage() {
  const nav = useNavigate();
  const { signup } = useAuthStore();
  const [email, setEmail] = useState("");
  const [pwd, setPwd] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const passed = RULES.filter(r => r.test(pwd)).length;
  const strongEnough = pwd.length >= 12 && passed >= 4; // len + 3/4 categories

  async function submit(e: FormEvent) {
    e.preventDefault();
    setErr(null);
    setLoading(true);
    try {
      await signup(email, pwd);
      nav(`/auth/check-inbox?email=${encodeURIComponent(email)}`);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "";
      setErr(message.includes("409") ? "Un compte existe déjà avec cet email." : "Inscription impossible — réessayez.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout title="Créer un compte">
      <form onSubmit={submit} className="space-y-4">
        <label className="block">
          <span className="text-sm font-medium">Email</span>
          <input
            type="email"
            required
            autoComplete="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
          />
        </label>
        <PasswordInput value={pwd} onChange={setPwd} label="Mot de passe" />
        <ul className="text-xs space-y-1">
          {RULES.map(r => (
            <li key={r.k} className={r.test(pwd) ? "text-emerald-600" : "text-gray-500"}>
              {r.test(pwd) ? "✓" : "•"} {r.t}
            </li>
          ))}
        </ul>
        {err && <p className="text-sm text-red-600">{err}</p>}
        <button
          type="submit"
          disabled={!strongEnough || !email || loading}
          className="w-full rounded-lg bg-indigo-600 py-2 font-medium text-white disabled:opacity-40"
        >
          {loading ? "…" : "Créer mon compte"}
        </button>
        <p className="text-sm text-gray-600">
          Déjà un compte ? <Link to="/auth/login" className="text-indigo-600">Se connecter</Link>
        </p>
        <p className="text-xs text-gray-500">
          En créant un compte, vous acceptez nos{" "}
          <Link to="/legal/cgu" className="underline">CGU</Link> et notre{" "}
          <Link to="/legal/privacy" className="underline">politique de confidentialité</Link>.
        </p>
      </form>
    </AuthLayout>
  );
}
