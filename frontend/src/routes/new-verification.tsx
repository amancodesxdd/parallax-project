import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowLeft, ChevronDown, FileText, UploadCloud, Play } from "lucide-react";
import { AppShell } from "@/components/AppShell";

export const Route = createFileRoute("/new-verification")({
  head: () => ({
    meta: [
      { title: "New Verification — SNARE KYC Screening" },
      {
        name: "description",
        content:
          "Upload a passport, national ID or driver's licence and run SNARE's KYC and AML document screening engine.",
      },
      { property: "og:title", content: "New Verification — SNARE KYC Screening" },
      {
        property: "og:description",
        content: "Configure document parameters and start an identity screening run.",
      },
    ],
  }),
  component: NewVerification,
});

function NewVerification() {
  const [fileName, setFileName] = useState<string | null>(null);
  const [faceMatch, setFaceMatch] = useState(true);

  return (
    <AppShell>
      <div className="mx-auto max-w-2xl">
        <div className="surface-card p-8">
          <Link
            to="/"
            className="label-caps mb-4 inline-flex items-center gap-1.5 hover:text-foreground"
          >
            <ArrowLeft className="size-3.5" /> KYC / AML Screening
          </Link>
          <h1 className="text-2xl font-bold tracking-tight">New Verification</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Configure document parameters and prepare the extraction engine.
          </p>

          <p className="label-caps mt-6">Document Type</p>
          <div className="relative mt-2">
            <FileText className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-primary" />
            <select className="w-full appearance-none rounded-lg border border-border bg-card py-2.5 pl-9 pr-9 text-sm outline-none focus:ring-2 focus:ring-ring/40">
              <option>Passport (International)</option>
              <option>National ID</option>
              <option>Driver&apos;s License</option>
              <option>Residence Permit</option>
            </select>
            <ChevronDown className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          </div>

          <p className="label-caps mt-5">Upload File</p>
          <label className="mt-2 flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-primary/40 bg-accent/40 px-6 py-10 text-center transition-colors hover:bg-accent/70">
            <UploadCloud className="size-6 text-primary" />
            <span className="text-sm font-medium">
              {fileName ?? "Drag & drop your document here"}
            </span>
            <span className="text-xs text-muted-foreground">or</span>
            <span className="rounded-md bg-card px-3 py-1.5 text-xs font-semibold shadow-sm">
              Browse Files
            </span>
            <span className="text-[10px] text-muted-foreground">
              PDF, JPG, PNG — up to 10MB
            </span>
            <input
              type="file"
              className="hidden"
              onChange={(e) => setFileName(e.target.files?.[0]?.name ?? null)}
            />
          </label>

          <div className="mt-6 flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold">Enable face-match verification</p>
              <p className="text-xs text-muted-foreground">Opens webcam for live selfie capture.</p>
            </div>
            <button
              role="switch"
              aria-checked={faceMatch}
              onClick={() => setFaceMatch(!faceMatch)}
              className={`relative h-6 w-11 shrink-0 rounded-full transition-colors ${faceMatch ? "bg-primary" : "bg-muted"}`}
            >
              <span
                className={`absolute top-0.5 size-5 rounded-full bg-card shadow transition-all ${faceMatch ? "left-[22px]" : "left-0.5"}`}
              />
            </button>
          </div>

          <Link
            to="/screening"
            className="mt-6 flex w-full items-center justify-center gap-2 rounded-lg bg-primary py-3 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
          >
            <Play className="size-4" /> Start Screening
          </Link>
          <p className="mt-3 text-center text-xs text-muted-foreground">
            Upload a document to begin.
          </p>
        </div>
      </div>
    </AppShell>
  );
}
