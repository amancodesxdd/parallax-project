import { cn } from "@/lib/utils";
import type { Verdict, AuditResult } from "@/lib/mock-data";

const tone: Record<string, string> = {
  Pass: "bg-success-soft text-success",
  SUCCESS: "bg-success-soft text-success",
  Clear: "bg-success-soft text-success",
  Fail: "bg-danger-soft text-destructive",
  DENIED: "bg-danger-soft text-destructive",
  Pending: "bg-warning-soft text-warning-foreground",
  PENDING: "bg-warning-soft text-warning-foreground",
};

export function VerdictBadge({ verdict }: { verdict: Verdict | AuditResult | string }) {
  return (
    <span
      className={cn(
        "inline-flex rounded-md px-2 py-0.5 text-[11px] font-semibold",
        tone[verdict] ?? "bg-muted text-muted-foreground",
      )}
    >
      {verdict}
    </span>
  );
}
