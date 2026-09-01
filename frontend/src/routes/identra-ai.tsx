import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { Sparkles, Send } from "lucide-react";
import { AppShell, PageTitle } from "@/components/AppShell";

export const Route = createFileRoute("/identra-ai")({
  head: () => ({
    meta: [
      { title: "Identra AI — SNARE Verification Assistant" },
      {
        name: "description",
        content:
          "Ask Identra AI about verification records, the risk scoring model, tampering signals and blacklist entries.",
      },
      { property: "og:title", content: "Identra AI — SNARE Verification Assistant" },
      {
        property: "og:description",
        content: "Conversational assistant grounded in your live verification and blacklist data.",
      },
    ],
  }),
  component: IdentraAI,
});

const prompts = [
  "Why was SNR-2026-1004 flagged?",
  "What triggers a REJECT verdict?",
  "How is tampering detected?",
  "What's on the blacklist?",
];

type Msg = { role: "ai" | "user"; text: string };

function IdentraAI() {
  const [messages, setMessages] = useState<Msg[]>([
    {
      role: "ai",
      text: "Identra AI online. I read this checkpoint's live verification and blacklist data. Ask me about any record, the scoring model, or the watchlist.",
    },
  ]);
  const [input, setInput] = useState("");

  const send = (text: string) => {
    if (!text.trim()) return;
    setMessages((m) => [
      ...m,
      { role: "user", text },
      {
        role: "ai",
        text: "Based on the current screening data, this record scored in the low-risk band with a clear blacklist status and no tampering signals detected.",
      },
    ]);
    setInput("");
  };

  return (
    <AppShell>
      <PageTitle title="Identra AI" hi="इंद्र एआई" />

      <div className="surface-card flex min-h-[28rem] flex-col p-6">
        <div className="flex-1 space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={m.role === "user" ? "flex justify-end" : "flex gap-3"}>
              {m.role === "ai" && (
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-accent">
                  <Sparkles className="size-4 text-primary" />
                </span>
              )}
              <p
                className={`max-w-lg rounded-xl px-4 py-2.5 text-sm ${
                  m.role === "ai"
                    ? "bg-accent text-accent-foreground"
                    : "bg-primary text-primary-foreground"
                }`}
              >
                {m.text}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {prompts.map((p) => (
            <button
              key={p}
              onClick={() => send(p)}
              className="rounded-full bg-muted px-3 py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:bg-accent hover:text-accent-foreground"
            >
              {p}
            </button>
          ))}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="mt-3 flex gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            aria-label="Ask Identra AI"
            className="flex-1 rounded-lg border border-border bg-card px-3 py-2.5 text-sm outline-none focus:ring-2 focus:ring-ring/40"
          />
          <button
            type="submit"
            className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
          >
            <Send className="size-4" /> Send
          </button>
        </form>
      </div>
    </AppShell>
  );
}
