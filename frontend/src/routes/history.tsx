import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Search, Download, ChevronLeft, ChevronRight } from "lucide-react";
import { AppShell, PageTitle } from "@/components/AppShell";
import { VerdictBadge } from "@/components/VerdictBadge";
import { verificationHistory } from "@/lib/mock-data";

export const Route = createFileRoute("/history")({
  head: () => ({
    meta: [
      { title: "Verification History — SNARE" },
      {
        name: "description",
        content:
          "Browse, filter and export past identity verification records with verdicts, timestamps and reviewers.",
      },
      { property: "og:title", content: "Verification History — SNARE" },
      {
        property: "og:description",
        content: "Searchable archive of every KYC verification run in your workspace.",
      },
    ],
  }),
  component: HistoryPage,
});

function HistoryPage() {
  const [query, setQuery] = useState("");
  const [verdict, setVerdict] = useState("All");

  const rows = useMemo(
    () =>
      verificationHistory.filter(
        (v) =>
          (verdict === "All" || v.verdict === verdict) &&
          (v.name.toLowerCase().includes(query.toLowerCase()) ||
            v.id.toLowerCase().includes(query.toLowerCase())),
      ),
    [query, verdict],
  );

  return (
    <AppShell>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <PageTitle
          title="Verification History"
          hi="इतिहास"
          sub="Browse and export past verification records."
        />
        <button className="flex items-center gap-2 rounded-lg bg-primary px-3.5 py-2 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90">
          <Download className="size-4" /> Export CSV
        </button>
      </div>

      <div className="surface-card p-5">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative min-w-56 flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search by name or ID..."
              className="w-full rounded-lg border border-border bg-card py-2 pl-9 pr-3 text-sm outline-none focus:ring-2 focus:ring-ring/40"
            />
          </div>
          <label className="flex items-center gap-2 text-sm text-muted-foreground">
            Verdict:
            <select
              value={verdict}
              onChange={(e) => setVerdict(e.target.value)}
              className="rounded-lg border border-border bg-card px-2 py-1.5 text-sm font-medium text-foreground outline-none"
            >
              {["All", "Pass", "Fail", "Pending"].map((v) => (
                <option key={v}>{v}</option>
              ))}
            </select>
          </label>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                {["Name", "Verification ID", "Verdict", "Date", "Verified By"].map((h) => (
                  <th key={h} className="label-caps whitespace-nowrap py-2 pr-4">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((v) => (
                <tr key={v.id} className="border-b border-border/60 last:border-0">
                  <td className="py-3 pr-4 font-semibold">
                    {v.name}
                    <span className="ml-2 rounded bg-success-soft px-1.5 py-0.5 text-[10px] font-bold text-success">
                      {v.tag}
                    </span>
                  </td>
                  <td className="py-3 pr-4 font-mono text-xs text-muted-foreground">{v.id}</td>
                  <td className="py-3 pr-4">
                    <VerdictBadge verdict={v.verdict} />
                  </td>
                  <td className="py-3 pr-4 text-muted-foreground">{v.date}</td>
                  <td className="py-3 pr-4">
                    <span className="flex items-center gap-2">
                      <span className="flex size-6 items-center justify-center rounded-full bg-accent text-[10px] font-semibold text-accent-foreground">
                        {v.verifiedBy.slice(0, 2).toUpperCase()}
                      </span>
                      {v.verifiedBy}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-muted-foreground">
            Showing 1-{rows.length} of 248 results
          </p>
          <div className="flex items-center gap-1">
            <PageBtn>
              <ChevronLeft className="size-3.5" />
            </PageBtn>
            <PageBtn active>1</PageBtn>
            <PageBtn>2</PageBtn>
            <PageBtn>3</PageBtn>
            <span className="px-1 text-xs text-muted-foreground">…</span>
            <PageBtn>25</PageBtn>
            <PageBtn>
              <ChevronRight className="size-3.5" />
            </PageBtn>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function PageBtn({ children, active }: { children: React.ReactNode; active?: boolean }) {
  return (
    <button
      className={`flex size-7 items-center justify-center rounded-md border text-xs font-medium transition-colors ${
        active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-border text-muted-foreground hover:bg-muted"
      }`}
    >
      {children}
    </button>
  );
}
