import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Check, Clock, Circle } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { screeningSteps } from "@/lib/mock-data";

export const Route = createFileRoute("/screening")({
  head: () => ({
    meta: [
      { title: "Screening in Progress — SNARE" },
      {
        name: "description",
        content:
          "Live progress of OCR extraction, blacklist checks, tampering scan and risk assessment for the submitted document.",
      },
      { property: "og:title", content: "Screening in Progress — SNARE" },
      {
        property: "og:description",
        content: "Track each stage of the SNARE identity screening pipeline in real time.",
      },
    ],
  }),
  component: Screening,
});

function Screening() {
  const [progress, setProgress] = useState(15);
  const [elapsed, setElapsed] = useState(5);

  useEffect(() => {
    const t = setInterval(() => {
      setProgress((p) => Math.min(100, p + 3));
      setElapsed((e) => e + 1);
    }, 1000);
    return () => clearInterval(t);
  }, []);

  const done = Math.floor((progress / 100) * screeningSteps.length);

  return (
    <AppShell>
      <div className="mx-auto max-w-xl">
        <div className="surface-card p-8">
          <div className="flex items-center justify-between">
            <h1 className="text-lg font-bold">Screening in Progress</h1>
            <span className="text-sm font-semibold text-muted-foreground">{progress}%</span>
          </div>
          <div className="mt-3 h-1.5 overflow-hidden rounded-full bg-muted">
            <div
              className="h-full rounded-full bg-primary transition-all duration-700"
              style={{ width: `${progress}%` }}
            />
          </div>

          <ol className="mt-6 space-y-3">
            {screeningSteps.map((step, i) => {
              const complete = i < done;
              const active = i === done;
              return (
                <li key={step}>
                  {step === "Tampering Scan" && (
                    <p className="pb-1 text-sm font-semibold">Tampering Scan</p>
                  )}
                  {step !== "Tampering Scan" && (
                    <div className="flex items-center gap-2.5 text-sm">
                      {complete ? (
                        <Check className="size-4 text-success" />
                      ) : active ? (
                        <Clock className="size-4 animate-pulse text-primary" />
                      ) : (
                        <Circle className="size-4 text-muted-foreground/50" />
                      )}
                      <span
                        className={
                          complete || active ? "font-medium" : "text-muted-foreground/70"
                        }
                      >
                        {step}
                      </span>
                    </div>
                  )}
                </li>
              );
            })}
          </ol>

          <p className="mt-6 flex items-center justify-center gap-1.5 text-xs text-muted-foreground">
            <Clock className="size-3.5" /> Elapsed: 00:{String(elapsed).padStart(2, "0")}
          </p>
          <div className="mt-3 text-center">
            <Link
              to="/verification-complete"
              className="text-sm font-semibold text-destructive hover:underline"
            >
              Cancel Screening
            </Link>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
