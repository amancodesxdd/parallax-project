import { createFileRoute } from "@tanstack/react-router";
import { Calendar, Trash2, ChevronLeft, ChevronRight, LogIn } from "lucide-react";
import { AppShell, PageTitle } from "@/components/AppShell";
import { VerdictBadge } from "@/components/VerdictBadge";
import { auditTrail } from "@/lib/mock-data";

export const Route = createFileRoute("/audit-trail")({
  head: () => ({
    meta: [
      { title: "Audit Trail — SNARE Compliance Log" },
      {
        name: "description",
        content:
          "Immutable log of verification runs, approvals, overrides and blacklist changes with actor, resource and result.",
      },
      { property: "og:title", content: "Audit Trail — SNARE Compliance Log" },
      {
        property: "og:description",
        content: "Filter compliance events by date, actor, resource and outcome.",
      },
    ],
  }),
  component: AuditTrailPage,
});

function AuditTrailPage() {
  return (
    <AppShell>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <PageTitle title="Audit trail" hi="लेखा परीक्षा विवरण" />
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
        <div className="grid gap-3 md:grid-cols-4">
          {["dd-mm-yyyy", "dd-mm-yyyy"].map((ph, i) => (
            <div key={i} className="relative">
              <input
                placeholder={ph}
                aria-label={i === 0 ? "From date" : "To date"}
                className="w-full rounded-lg border border-border bg-card px-3 py-2 pr-9 text-sm outline-none focus:ring-2 focus:ring-ring/40"
              />
              <Calendar className="pointer-events-none absolute right-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
            </div>
          ))}
          <select
            aria-label="Filter by resource"
            className="rounded-lg border border-border bg-card px-3 py-2 text-sm outline-none"
          >
            <option>ALL</option>
            <option>VERIFICATION_RUN</option>
            <option>VERIFICATION_APPROVE</option>
            <option>BLACKLIST_ADD</option>
          </select>
          <select
            aria-label="Filter by result"
            className="rounded-lg border border-border bg-card px-3 py-2 text-sm outline-none"
          >
            <option>ALL</option>
            <option>SUCCESS</option>
            <option>DENIED</option>
            <option>PENDING</option>
          </select>
        </div>

        <div className="mt-5 overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left">
                {["Timestamp (UTC)", "Actor", "Resource", "Result", "Actions"].map((h) => (
                  <th key={h} className="label-caps whitespace-nowrap py-2 pr-4">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {auditTrail.map((row, i) => (
                <tr key={i} className="border-b border-border/60 last:border-0">
                  <td className="whitespace-nowrap py-3 pr-4 font-mono text-xs font-semibold text-primary">
                    <span className="flex items-center gap-1.5">
                      {row.resource === "LOG_IN" && <LogIn className="size-3.5" />}
                      {row.timestamp}
                    </span>
                  </td>
                  <td className="py-3 pr-4 font-medium">{row.actor}</td>
                  <td className="py-3 pr-4 font-mono text-xs text-muted-foreground">
                    {row.resource}
                  </td>
                  <td className="py-3 pr-4">
                    <VerdictBadge verdict={row.result} />
                  </td>
                  <td className="py-3 pr-4">
                    <button aria-label="Delete log entry" className="text-destructive hover:opacity-70">
                      <Trash2 className="size-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
          <p className="text-xs text-muted-foreground">Showing 1-8 of 24 entries</p>
          <div className="flex items-center gap-1">
            {[<ChevronLeft key="l" className="size-3.5" />, "1", "2", "3", <ChevronRight key="r" className="size-3.5" />].map(
              (c, i) => (
                <button
                  key={i}
                  className={`flex size-7 items-center justify-center rounded-md border text-xs font-medium transition-colors ${
                    c === "1"
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border text-muted-foreground hover:bg-muted"
                  }`}
                >
                  {c}
                </button>
              ),
            )}
          </div>
        </div>
      </div>
    </AppShell>
  );
}
