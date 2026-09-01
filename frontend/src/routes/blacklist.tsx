import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { PlusCircle, Info, Search, Trash2, FileText } from "lucide-react";
import { AppShell, PageTitle } from "@/components/AppShell";
import { blacklistEntries } from "@/lib/mock-data";

export const Route = createFileRoute("/blacklist")({
  head: () => ({
    meta: [
      { title: "Blacklist Admin — SNARE" },
      {
        name: "description",
        content:
          "Add, monitor and manage revoked or fraudulent identity document entries used during KYC screening.",
      },
      { property: "og:title", content: "Blacklist Admin — SNARE" },
      {
        property: "og:description",
        content: "Manage blocked document numbers and the reasons behind each blacklist entry.",
      },
    ],
  }),
  component: BlacklistAdmin,
});

function BlacklistAdmin() {
  const [entries, setEntries] = useState(blacklistEntries);
  const [number, setNumber] = useState("");
  const [docType, setDocType] = useState("Passport");
  const [reason, setReason] = useState("");

  const add = () => {
    if (!number.trim()) return;
    setEntries([
      {
        docType,
        number,
        reason: reason || "Manual entry",
        addedBy: "Priyadarshani B.",
        date: "Sep 1, 2026",
      },
      ...entries,
    ]);
    setNumber("");
    setReason("");
  };

  return (
    <AppShell>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <PageTitle
          title="Blacklist Admin"
          hi="काली सूची प्रशासन"
          sub="Add, monitor and manage revoked or fraudulent identity document entries."
        />
        <div className="flex gap-3">
          <div className="surface-card px-4 py-2.5">
            <p className="label-caps">Total Blocked</p>
            <p className="text-xl font-bold">1,482</p>
          </div>
          <div className="surface-card px-4 py-2.5">
            <p className="label-caps">Added Today</p>
            <p className="text-xl font-bold text-success">+14</p>
          </div>
        </div>
      </div>

      <div className="surface-card p-5">
        <p className="flex items-center gap-2 text-sm font-semibold">
          <PlusCircle className="size-4 text-primary" /> Add New Blacklisted Document
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <Field label="Document Type *">
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value)}
              className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring/40"
            >
              {["Passport", "Driver's License", "National ID"].map((d) => (
                <option key={d}>{d}</option>
              ))}
            </select>
          </Field>
          <Field label="Document Number *">
            <input
              value={number}
              onChange={(e) => setNumber(e.target.value)}
              placeholder="NLD8840192A"
              className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring/40"
            />
          </Field>
          <Field label="Reason for Blacklist (optional)">
            <input
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="e.g. Identity theft, reported stolen..."
              className="w-full rounded-lg border border-border bg-card px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-ring/40"
            />
          </Field>
        </div>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Info className="size-3.5" /> Ensure document checks have been fully audited before
            manual lock.
          </p>
          <button
            onClick={add}
            className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
          >
            <PlusCircle className="size-4" /> Add to Blacklist
          </button>
        </div>
      </div>

      <div className="surface-card mt-4 p-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <p className="text-sm font-semibold">
            Blacklisted Entries{" "}
            <span className="ml-1 rounded bg-muted px-1.5 py-0.5 text-[11px] font-medium text-muted-foreground">
              {entries.length} entries
            </span>
          </p>
          <div className="relative">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <input
              placeholder="Search entries..."
              className="rounded-lg border border-border bg-card py-1.5 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-ring/40"
            />
          </div>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                {["Document Type", "Document Number", "Reason", "Added By", "Date Added", "Actions"].map(
                  (h) => (
                    <th key={h} className="label-caps whitespace-nowrap py-2 pr-4">
                      {h}
                    </th>
                  ),
                )}
              </tr>
            </thead>
            <tbody>
              {entries.map((e) => (
                <tr key={e.number} className="border-b border-border/60 last:border-0">
                  <td className="py-3 pr-4">
                    <span className="flex items-center gap-2 font-medium">
                      <FileText className="size-4 text-primary" /> {e.docType}
                    </span>
                  </td>
                  <td className="py-3 pr-4 font-mono text-xs">{e.number}</td>
                  <td className="py-3 pr-4">
                    <span className="rounded-md bg-danger-soft px-2 py-0.5 text-[11px] font-semibold text-destructive">
                      {e.reason}
                    </span>
                  </td>
                  <td className="py-3 pr-4 text-muted-foreground">{e.addedBy}</td>
                  <td className="py-3 pr-4 text-muted-foreground">{e.date}</td>
                  <td className="py-3 pr-4">
                    <button
                      aria-label={`Remove ${e.number}`}
                      onClick={() => setEntries(entries.filter((x) => x.number !== e.number))}
                      className="text-destructive transition-opacity hover:opacity-70"
                    >
                      <Trash2 className="size-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppShell>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p className="label-caps mb-1.5">{label}</p>
      {children}
    </div>
  );
}
