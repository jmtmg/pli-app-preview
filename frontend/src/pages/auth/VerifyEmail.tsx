import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useAuthStore } from "../../stores/authStore";
import { AuthLayout } from "./components/AuthLayout";

type Status = "pending" | "ok" | "err";

export default function VerifyEmailPage() {
  const [sp] = useSearchParams();
  const token = sp.get("token") ?? "";
  const { verifyEmail } = useAuthStore();
  const [status, setStatus] = useState<Status>("pending");

  useEffect(() => {
    if (!token) {
      setStatus("err");
      return;
    }
    verifyEmail(token)
      .then(() => setStatus("ok"))
      .catch(() => setStatus("err"));
  }, [token, verifyEmail]);

  return (
    <AuthLayout title="Vérification de votre email">
      {status === "pending" && <p className="text-gray-600">Un instant…</p>}
      {status === "ok" && (
        <div>
          <p className="text-emerald-700 font-medium">Votre email est confirmé.</p>
          <Link to="/auth/login" className="mt-4 inline-block rounded-lg bg-indigo-600 px-4 py-2 text-white">
            Se connecter
          </Link>
        </div>
      )}
      {status === "err" && (
        <div>
          <p className="text-red-600">Ce lien est invalide ou a expiré.</p>
          <Link to="/auth/login" className="mt-4 inline-block text-indigo-600">Retour à la connexion</Link>
        </div>
      )}
    </AuthLayout>
  );
}
