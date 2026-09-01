import { createFileRoute, Link } from "@tanstack/react-router";
import { Download, Flag, ShieldCheck, BatteryMedium } from "lucide-react";
import { AppShell } from "@/components/AppShell";

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

const findings = [
  { label: "Document Auth...", value: "Passed" },
  { label: "Face Match", value: "98.2% Match" },
  { label: "Blacklist Status", value: "Clear" },
  { label: "Tampering Dete...", value: "None Found" },
];

const extracted = [
  ["Full Name", "Elena Marchetti"],
  ["Document", "Passport"],
  ["Country", "Italy"],
  ["Expiry Date", "Mar 2029"],
];

function VerificationComplete() {
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
              23
              <span className="text-sm font-medium text-muted-foreground">/100</span>
            </p>
            <p className="mt-1 flex items-center justify-center gap-1.5 text-sm font-semibold text-success">
              <ShieldCheck className="size-4" /> Low Risk Verdict
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
