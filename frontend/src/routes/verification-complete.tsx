import { createFileRoute, Link } from "@tanstack/react-router";
import { Download, Flag, ShieldCheck, BatteryMedium, ScanSearch } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { useScan } from "@/lib/scan";

export const Route = createFileRoute("/verification-complete")({
  head: () => ({
    meta: [
      { title: "Verification Complete — SNARE Report" },
      {
        name: "description",
        content:
          "Risk score, document authenticity, face match, blacklist status and extracted document data for a completed SNARE screening.",
      },
      { property: "og:title", content: "Verification Complete — SNARE Report" },
      {
        property: "og:description",
        content: "Low-risk verdict with full verification findings and extracted system data.",
      },
    ],
  }),
  component: VerificationComplete,
});

const mockFindings = [
  { label: "Document Auth...", value: "Passed" },
  { label: "Face Match", value: "98.2% Match" },
  { label: "Blacklist Status", value: "Clear" },
  { label: "Tampering Dete...", value: "None Found" },
];

const mockExtracted: [string, string][] = [
  ["Full Name", "Elena Marchetti"],
  ["Document", "Passport"],
  ["Country", "Italy"],
  ["Expiry Date", "Mar 2029"],
];

function VerificationComplete() {
  const { scanResult, scanLoading } = useScan();

  const riskScore = scanResult?.riskScore ?? 23;
  const lowRisk = (scanResult?.verdict ?? "LOW_RISK") !== "FAIL" && riskScore < 50;
  const evidenceUrl = scanResult?.evidenceImageUrl ?? null;
  const extracted: [string, string][] = scanResult
    ? Object.entries(scanResult.extractedData)
        .filter(([, v]) => v !== null && v !== "")
        .map(([k, v]) => [k.replace(/([A-Z])/g, " $1").replace(/^./, (c) => c.toUpperCase()), String(v)])
    : mockExtracted;
  const findings = scanResult
    ? [
        { label: "Face Match", value: `${Math.round((scanResult.faceScore ?? 0) * 100)}% Match` },
        {
          label: "Tampering",
          value: scanResult.tamperingFlags.length ? `${scanResult.tamperingFlags.length} Flag(s)` : "None Found",
        },
      ]
    : mockFindings;

  return (
    <AppShell>
      <div className="mx-auto max-w-2xl">
        <div className="surface-card p-8">
          <div className="flex items-center gap-3">
            <span className="rounded-md bg-success-soft px-2 py-0.5 text-[11px] font-bold text-success">
              SUCCESS
            </span>
            <h1 className="text-lg font-bold">Verification Complete</h1>
          </div>

          <div className="mt-6 text-center">
            <p className="label-caps">Risk Score</p>
            <p className="flex items-center justify-center gap-2 text-4xl font-bold">
              <BatteryMedium className="size-6 text-success" />
              {Math.round(riskScore)}
              <span className="text-sm font-medium text-muted-foreground">/100</span>
            </p>
            <p className="mt-1 flex items-center justify-center gap-1.5 text-sm font-semibold text-success">
              <ShieldCheck className="size-4" /> {lowRisk ? "Low Risk Verdict" : "High Risk Verdict"}
            </p>
          </div>

          <p className="label-caps mt-8">Verification Findings</p>
          <div className="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {findings.map((f) => (
              <div key={f.label}>
                <p className="text-[11px] text-muted-foreground">{f.label}</p>
                <p className="text-sm font-semibold text-success">• {f.value}</p>
              </div>
            ))}
          </div>

          <p className="label-caps mt-8">Extracted System Data</p>
          <dl className="mt-3 divide-y divide-border">
            {extracted.map(([k, v]) => (
              <div key={k} className="flex justify-between py-2 text-sm">
                <dt className="text-muted-foreground">{k}</dt>
                <dd className="font-medium">{v}</dd>
              </div>
            ))}
          </dl>

          <div className="mt-8">
            <p className="label-caps flex items-center gap-1.5">
              <ScanSearch className="size-3.5" /> Automated Evidence (XAI)
            </p>
            {scanLoading && !evidenceUrl ? (
              <p className="mt-3 rounded-lg border border-border bg-accent/40 px-4 py-6 text-center text-sm text-muted-foreground">
                Generating visual evidence…
              </p>
            ) : evidenceUrl ? (
              <div className="mt-3 overflow-hidden rounded-xl border border-border">
                <img
                  src={evidenceUrl}
                  alt="Automated detection overlay of the scanned document"
                  className="w-full"
                  loading="lazy"
                />
                <p className="border-t border-border bg-accent/40 px-4 py-2 text-xs text-muted-foreground">
                  Detection boxes overlay: red = suspected photo cut / tampering, magenta = AI
                  spectral anomaly, green = live face match. Generated by the forensics engine.
                </p>
              </div>
            ) : (
              <p className="mt-3 rounded-lg border border-border bg-accent/40 px-4 py-6 text-center text-sm text-muted-foreground">
                No annotated evidence available for this scan run.
              </p>
            )}
          </div>

          <button className="mt-8 flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90">
            <Download className="size-4" /> Download Report
          </button>
          <button className="mt-3 flex w-full items-center justify-center gap-2 text-sm text-muted-foreground hover:text-foreground">
            <Flag className="size-3.5" /> Flag for Review
          </button>
          <div className="mt-4 text-center">
            <Link to="/" className="text-xs font-semibold text-primary hover:underline">
              Back to Dashboard
            </Link>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
