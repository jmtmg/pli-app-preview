import { useState } from "react";

export function PasswordInput({
  value, onChange, label, autoComplete = "new-password",
}: {
  value: string;
  onChange: (v: string) => void;
  label: string;
  autoComplete?: string;
}) {
  const [show, setShow] = useState(false);
  return (
    <label className="block">
      <span className="text-sm font-medium">{label}</span>
      <div className="relative mt-1">
        <input
          type={show ? "text" : "password"}
          required
          autoComplete={autoComplete}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 pr-10"
        />
        <button
          type="button"
          onClick={() => setShow((s) => !s)}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-xs text-gray-500"
          tabIndex={-1}
        >
          {show ? "Masquer" : "Afficher"}
        </button>
      </div>
    </label>
  );
}
