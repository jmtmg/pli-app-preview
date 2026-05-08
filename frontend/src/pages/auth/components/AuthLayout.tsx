import { ReactNode } from "react";
import { Link } from "react-router-dom";

export function AuthLayout({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-gray-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md rounded-xl bg-white p-8 shadow-sm">
        <Link to="/" className="mb-6 block text-xl font-semibold text-indigo-600">PLI</Link>
        <h1 className="mb-4 text-2xl font-semibold text-gray-900">{title}</h1>
        {children}
      </div>
    </div>
  );
}
