import { useState } from "react";
import { apiClient } from "@/api/client";
import { useT } from "@/i18n/hooks";
import { useToast } from "@/components/Toast";
import { Modal } from "@/components/Modal";

type DeletionState = { scheduled: boolean; purge_at: string | null };

type Props = {
  deletionState: DeletionState;
  onChange: (s: DeletionState) => void;
};

export function DeleteAccountButton({ deletionState, onChange }: Props) {
  const t = useT("settings");
  const toast = useToast();
  const [open, setOpen] = useState(false);
  const [password, setPassword] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  async function confirmDelete() {
    setSubmitting(true);
    try {
      const r = await apiClient.post<DeletionState>("/gdpr/delete", {
        password_confirmation: password,
        i_understand_this_is_permanent: true,
      });
      onChange(r.data);
      toast.success(t("delete.scheduled"));
      setOpen(false);
      setPassword("");
      setConfirmed(false);
    } catch (e: any) {
      toast.error(t("delete.error"));
    } finally {
      setSubmitting(false);
    }
  }

  async function cancelDelete() {
    setSubmitting(true);
    try {
      const r = await apiClient.delete<DeletionState>("/gdpr/cancel-deletion");
      onChange(r.data);
      toast.success(t("delete.cancelled"));
    } catch {
      toast.error(t("delete.cancel_error"));
    } finally {
      setSubmitting(false);
    }
  }

  if (deletionState.scheduled && deletionState.purge_at) {
    return (
      <div role="status" className="rounded-md border border-red-300 bg-red-50 dark:bg-red-950 dark:border-red-700 p-3">
        <p className="text-sm">
          <strong>{t("delete.scheduled_title")}</strong>
        </p>
        <p className="text-sm mt-1">
          {t("delete.scheduled_body", { date: new Date(deletionState.purge_at).toLocaleDateString() })}
        </p>
        <button
          type="button"
          onClick={cancelDelete}
          disabled={submitting}
          className="mt-3 inline-flex items-center rounded-md bg-white dark:bg-neutral-800 border border-neutral-300 dark:border-neutral-600 px-3 py-1.5 text-sm font-medium"
        >
          {t("delete.cancel_button")}
        </button>
      </div>
    );
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rounded-md border border-red-500 text-red-600 dark:text-red-400 px-4 py-2 text-sm font-medium hover:bg-red-500 hover:text-white focus:outline-none focus:ring-2 focus:ring-red-500"
      >
        {t("delete.trigger")}
      </button>

      <Modal open={open} onClose={() => setOpen(false)} titleId="delete-account-title">
        <div className="p-6 max-w-md">
          <h2 id="delete-account-title" className="text-lg font-semibold text-red-700 dark:text-red-300">
            {t("delete.modal_title")}
          </h2>
          <p className="mt-2 text-sm">{t("delete.modal_body")}</p>
          <ul className="list-disc list-inside mt-3 text-sm text-neutral-600 dark:text-neutral-400 space-y-1">
            <li>{t("delete.modal_consequence_data")}</li>
            <li>{t("delete.modal_consequence_cancel")}</li>
            <li>{t("delete.modal_consequence_legal")}</li>
          </ul>

          <div className="mt-4">
            <label htmlFor="delete-password" className="block text-sm font-medium">
              {t("delete.password_label")}
            </label>
            <input
              id="delete-password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 block w-full rounded-md border-neutral-300 dark:border-neutral-700 dark:bg-neutral-800 shadow-sm focus:border-red-500 focus:ring-red-500 text-sm"
            />
          </div>

          <label className="mt-3 flex items-start gap-2 text-sm">
            <input
              type="checkbox"
              checked={confirmed}
              onChange={(e) => setConfirmed(e.target.checked)}
              className="mt-0.5"
            />
            <span>{t("delete.confirm_permanent")}</span>
          </label>

          <div className="mt-5 flex justify-end gap-2">
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="rounded-md px-4 py-2 text-sm font-medium"
            >
              {t("common.cancel")}
            </button>
            <button
              type="button"
              disabled={!password || !confirmed || submitting}
              onClick={confirmDelete}
              className="rounded-md bg-red-600 text-white px-4 py-2 text-sm font-medium disabled:opacity-50"
            >
              {submitting ? t("common.sending") : t("delete.confirm_button")}
            </button>
          </div>
        </div>
      </Modal>
    </>
  );
}
