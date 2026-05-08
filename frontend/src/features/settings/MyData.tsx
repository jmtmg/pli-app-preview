import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useT } from "@/i18n/hooks";
import { apiClient } from "@/api/client";
import { useToast } from "@/components/Toast";
import { formatBytes, formatDate } from "@/lib/format";
import { DeleteAccountButton } from "./DeleteAccount";

type Account = {
  id: string;
  provider: "gmail" | "microsoft";
  email: string;
  connected_at: string;
};

type MyData = {
  user_id: string;
  email: string;
  locale: string;
  plan: string;
  created_at: string;
  accounts: Account[];
  volumetrie: {
    nb_accounts: number;
    nb_messages: number;
    nb_contacts: number;
    deletion: { scheduled: boolean; purge_at: string | null };
  };
  legal_bases: { finalite: string; base: string }[];
  subprocessors_url: string;
  dpo_contact: string;
};

type ExportJob = {
  job_id: string;
  status: "pending" | "running" | "ready" | "failed" | "expired";
  created_at: string;
  expires_at?: string;
  download_url?: string;
  size_bytes?: number;
};

export default function MyDataPage() {
  const t = useT("settings");
  const toast = useToast();
  const [data, setData] = useState<MyData | null>(null);
  const [exportJob, setExportJob] = useState<ExportJob | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiClient
      .get<MyData>("/gdpr/my-data")
      .then((r) => setData(r.data))
      .catch(() => toast.error(t("my_data.load_error")))
      .finally(() => setLoading(false));
  }, []);

  // Poll export status while a job is running.
  useEffect(() => {
    if (!exportJob || exportJob.status === "ready" || exportJob.status === "failed") return;
    const id = setInterval(async () => {
      try {
        const r = await apiClient.get<ExportJob>(`/gdpr/export/${exportJob.job_id}`);
        setExportJob(r.data);
      } catch {
        /* keep polling, transient errors tolerated */
      }
    }, 3000);
    return () => clearInterval(id);
  }, [exportJob?.job_id, exportJob?.status]);

  async function requestExport() {
    try {
      const r = await apiClient.post<ExportJob>("/gdpr/export");
      setExportJob(r.data);
      toast.success(t("export.requested"));
    } catch (error: unknown) {
      const msg = getHttpStatus(error) === 429 ? t("export.rate_limited") : t("export.error");
      toast.error(msg);
    }
  }

  if (loading || !data) {
    return (
      <main className="p-6" aria-busy="true">
        <h1 className="text-xl font-semibold">{t("my_data.title")}</h1>
        <p className="text-neutral-500 mt-2">{t("common.loading")}</p>
      </main>
    );
  }

  return (
    <main className="p-6 max-w-3xl" aria-labelledby="my-data-heading">
      <header className="mb-6">
        <h1 id="my-data-heading" className="text-2xl font-semibold">
          {t("my_data.title")}
        </h1>
        <p className="text-sm text-neutral-500 mt-1">{t("my_data.subtitle")}</p>
      </header>

      <Section title={t("my_data.identity")}>
        <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm">
          <dt className="font-medium">{t("my_data.email_label")}</dt>
          <dd>{data.email}</dd>
          <dt className="font-medium">{t("my_data.plan_label")}</dt>
          <dd>{data.plan}</dd>
          <dt className="font-medium">{t("my_data.since_label")}</dt>
          <dd>{formatDate(data.created_at, data.locale)}</dd>
          <dt className="font-medium">{t("my_data.locale_label")}</dt>
          <dd>{data.locale.toUpperCase()}</dd>
        </dl>
      </Section>

      <Section title={t("my_data.accounts_connected")}>
        {data.accounts.length === 0 ? (
          <p className="text-sm text-neutral-500">{t("my_data.no_accounts")}</p>
        ) : (
          <ul className="space-y-2">
            {data.accounts.map((a) => (
              <li key={a.id} className="flex justify-between items-center text-sm">
                <span>
                  <span className="font-medium">{a.email}</span>{" "}
                  <span className="text-neutral-500">({a.provider})</span>
                </span>
                <span className="text-xs text-neutral-400">
                  {t("my_data.connected_on")} {formatDate(a.connected_at, data.locale)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title={t("my_data.volume")}>
        <dl className="grid grid-cols-3 gap-4 text-sm">
          <Stat label={t("my_data.nb_messages")} value={data.volumetrie.nb_messages} />
          <Stat label={t("my_data.nb_contacts")} value={data.volumetrie.nb_contacts} />
          <Stat label={t("my_data.nb_accounts")} value={data.volumetrie.nb_accounts} />
        </dl>
      </Section>

      <Section title={t("my_data.legal_bases")}>
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-neutral-500">
              <th className="pb-2">{t("my_data.purpose")}</th>
              <th className="pb-2">{t("my_data.legal_basis")}</th>
            </tr>
          </thead>
          <tbody>
            {data.legal_bases.map((b, i) => (
              <tr key={i} className="border-t border-neutral-200 dark:border-neutral-700">
                <td className="py-2">{b.finalite}</td>
                <td className="py-2">{b.base}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <p className="text-xs text-neutral-500 mt-2">
          {t("my_data.subprocessors_intro")}{" "}
          <a
            className="underline"
            href={data.subprocessors_url}
            target="_blank"
            rel="noopener noreferrer"
          >
            {t("my_data.subprocessors_link")}
          </a>
          .
        </p>
      </Section>

      <Section title={t("my_data.export_section")}>
        <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-3">
          {t("my_data.export_explain")}
        </p>
        {exportJob?.status === "ready" && exportJob.download_url ? (
          <a
            href={exportJob.download_url}
            className="inline-block rounded-md bg-indigo-600 text-white px-4 py-2 text-sm font-medium"
            download
          >
            {t("export.download")}{" "}
            {exportJob.size_bytes ? `(${formatBytes(exportJob.size_bytes)})` : ""}
          </a>
        ) : exportJob && exportJob.status !== "failed" ? (
          <p className="text-sm text-neutral-500" role="status">
            {t(`export.status.${exportJob.status}`)}…
          </p>
        ) : (
          <button
            type="button"
            onClick={requestExport}
            className="rounded-md bg-indigo-600 text-white px-4 py-2 text-sm font-medium"
          >
            {t("export.request")}
          </button>
        )}
        {exportJob?.expires_at && (
          <p className="text-xs text-neutral-500 mt-2">
            {t("export.expires_at")} {formatDate(exportJob.expires_at, data.locale)}
          </p>
        )}
      </Section>

      <Section title={t("my_data.rights")}>
        <p className="text-sm">{t("my_data.rights_body")}</p>
        <p className="text-sm mt-2">
          {t("my_data.dpo_contact")}:{" "}
          <a className="underline" href={`mailto:${data.dpo_contact}`}>
            {data.dpo_contact}
          </a>
        </p>
        <p className="text-sm mt-2">
          <Link to="/legal/privacy" className="underline">
            {t("my_data.read_privacy")}
          </Link>
        </p>
      </Section>

      <Section title={t("my_data.danger_zone")} tone="danger">
        <p className="text-sm mb-3">{t("my_data.delete_explain")}</p>
        <DeleteAccountButton
          deletionState={data.volumetrie.deletion}
          onChange={(s) =>
            setData((prev) => (prev ? { ...prev, volumetrie: { ...prev.volumetrie, deletion: s } } : prev))
          }
        />
      </Section>
    </main>
  );
}

function getHttpStatus(error: unknown): number | undefined {
  if (typeof error !== "object" || error === null || !("response" in error)) return undefined;
  const response = (error as { response?: { status?: unknown } }).response;
  return typeof response?.status === "number" ? response.status : undefined;
}

function Section({
  title,
  children,
  tone,
}: {
  title: string;
  children: React.ReactNode;
  tone?: "danger";
}) {
  return (
    <section
      className={
        "mb-6 border rounded-lg p-5 " +
        (tone === "danger"
          ? "border-red-400 bg-red-50 dark:border-red-700 dark:bg-red-950"
          : "border-neutral-200 dark:border-neutral-700 bg-white dark:bg-neutral-900")
      }
    >
      <h2 className={"font-semibold text-base mb-3 " + (tone === "danger" ? "text-red-700 dark:text-red-300" : "")}>
        {title}
      </h2>
      {children}
    </section>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div>
      <div className="text-xs text-neutral-500">{label}</div>
      <div className="text-lg font-semibold tabular-nums">{value.toLocaleString()}</div>
    </div>
  );
}
