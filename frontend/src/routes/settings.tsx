import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { Moon, FileDown, FileSpreadsheet } from "lucide-react";
import { AppShell, PageTitle, useDarkMode } from "@/components/AppShell";
import { fetchScans, downloadPdfReport, ApiError } from "@/api";

export const Route = createFileRoute("/settings")({
  head: () => ({
    meta: [
      { title: "Settings — SNARE Console" },
      {
        name: "description",
        content:
          "Switch appearance and export session verification reports as PDF or CSV from the SNARE console.",
      },
      { property: "og:title", content: "Settings — SNARE Console" },
      {
        property: "og:description",
        content: "Appearance preferences and report export options for your workspace.",
      },
    ],
  }),
  component: SettingsPage,
});

function SettingsPage() {
  const { dark, setDark } = useDarkMode();
  const [busy, setBusy] = useState<"pdf" | "csv" | null>(null);
  const [noticeError, setNoticeError] = useState<string | null>(null);

  const exportCsv = async () => {
    setBusy("csv");
    setNoticeError(null);
    try {
      const res = await fetchScans({ limit: 100 });
      const header = ["Verification ID", "Document Number", "Verdict", "Risk Score", "Date"];
      const lines = res.data.map((scan) =>
        [
          scan.id,
          String(scan.extractedData?.documentNumber ?? ""),
          scan.verdict,
          scan.riskScore,
          scan.createdAt,
        ]
          .map((v) => `"${String(v).replace(/"/g, '""')}"`)
          .join(","),
      );
      const blob = new Blob([[header.join(","), ...lines].join("\n")], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "snare-verifications.csv";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (err) {
      setNoticeError(
        err instanceof ApiError ? err.message : "Export failed. Is the backend running?",
      );
    } finally {
      setBusy(null);
    }
  };

  const exportPdf = async () => {
    setBusy("pdf");
    setNoticeError(null);
    try {
      const res = await fetchScans({ limit: 1 });
      const latest = res.data[0];
      if (!latest) {
        setNoticeError("No verifications yet to export.");
        return;
      }
      await downloadPdfReport(latest.id);
    } catch (err) {
      setNoticeError(
        err instanceof ApiError ? err.message : "Export failed. Is the backend running?",
      );
    } finally {
      setBusy(null);
    }
  };

  return (
    <AppShell>
      <div className="mx-auto max-w-3xl">
        <PageTitle title="Settings" hi="सेटिंग" />

        <div className="surface-card flex items-center justify-between p-5">
          <div className="flex items-center gap-3">
            <Moon className="size-5 text-primary" />
            <div>
              <p className="text-sm font-semibold">Dark mode</p>
              <p className="text-xs text-muted-foreground">डार्क मोड</p>
            </div>
          </div>
          <button
            role="switch"
            aria-checked={dark}
            onClick={() => setDark(!dark)}
            className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${dark ? "bg-primary" : "bg-warning"}`}
          >
            <span
              className={`absolute top-0.5 size-5 rounded-full bg-card shadow transition-all ${dark ? "left-[22px]" : "left-0.5"}`}
            />
          </button>
        </div>

        <div className="surface-card mt-4 p-5">
          <p className="text-sm font-semibold">Reports</p>
          <p className="text-xs text-muted-foreground">रिपोर्ट</p>

          {noticeError && (
            <p className="mt-3 rounded-lg bg-danger-soft px-3 py-2 text-xs text-destructive">
              {noticeError}
            </p>
          )}

          <div className="mt-4 flex flex-wrap gap-3">
            <button
              onClick={exportPdf}
              disabled={busy !== null}
              className="flex items-center gap-2 rounded-lg border border-border bg-card px-4 py-2 text-sm font-medium transition-colors hover:bg-muted disabled:cursor-not-allowed disabled:opacity-50"
            >
              <FileDown className="size-4" /> {busy === "pdf" ? "Generating..." : "Export PDF"}
            </button>
            <button
              onClick={exportCsv}
              disabled={busy !== null}
              className="flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-sm font-semibold text-accent-foreground transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <FileSpreadsheet className="size-4" /> {busy === "csv" ? "Exporting..." : "Export CSV"}
            </button>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            रिपोर्ट / Reports are generated from verified screening records stored in the database.
          </p>
          <Link to="/history" className="mt-2 inline-block text-xs font-semibold text-primary hover:underline">
            Browse verification history →
          </Link>
        </div>
      </div>
    </AppShell>
  );
}