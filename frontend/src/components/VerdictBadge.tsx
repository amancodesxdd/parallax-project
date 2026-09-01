import { cn } from "@/lib/utils";

const tone: Record<string, string> = {
  Pass: "bg-success-soft text-success",
  SUCCESS: "bg-success-soft text-success",
  Clear: "bg-success-soft text-success",
  APPROVE: "bg-success-soft text-success",
  Fail: "bg-danger-soft text-destructive",
  DENIED: "bg-danger-soft text-destructive",
  REJECT: "bg-danger-soft text-destructive",
  Pending: "bg-warning-soft text-warning-foreground",
  PENDING: "bg-warning-soft text-warning-foreground",
  REVIEW: "bg-warning-soft text-warning-foreground",
};

export function VerdictBadge({ verdict }: { verdict: string }) {
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