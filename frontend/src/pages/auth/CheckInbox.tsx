import { Link, useSearchParams } from "react-router-dom";
import { AuthLayout } from "./components/AuthLayout";

export default function CheckInboxPage() {
  const [sp] = useSearchParams();
  const email = sp.get("email") ?? "votre adresse email";
  return (
    <AuthLayout title="Vérifiez votre boîte de réception">
      <p>
        Nous avons envoyé un lien de confirmation à <strong>{email}</strong>.
        Cliquez sur le lien pour activer votre compte.
      </p>
      <p className="text-sm text-gray-500 mt-4">
        Pas reçu ? Pensez à regarder dans les spams ou attendez quelques minutes.
      </p>
      <Link to="/auth/login" className="mt-6 inline-block text-indigo-600">
        Retour à la connexion
      </Link>
    </AuthLayout>
  );
}
