"use client";

import { useState } from "react";
import Link from "next/link";
import { getAllMethods } from "@/lib/methods";
import { AI_DISCLAIMER } from "@/lib/ai/prompts";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const methodSlugs = new Set(getAllMethods().map((m) => m.slug));

function extractMethodLinks(text: string): string[] {
  const found = new Set<string>();
  for (const slug of methodSlugs) {
    if (text.toLowerCase().includes(slug.replace(/-/g, " ").toLowerCase())) {
      found.add(slug);
    }
  }
  return [...found];
}

export function AIChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    const query = input.trim();
    if (!query || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: query }]);
    setLoading(true);

    try {
      const res = await fetch("/api/ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "AI request failed");
      setMessages((m) => [...m, { role: "assistant", content: data.text }]);
    } catch (e) {
      setMessages((m) => [...m, { role: "assistant", content: `Error: ${(e as Error).message}` }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="space-y-4 max-h-[420px] overflow-y-auto mb-4">
        {messages.length === 0 && (
          <div className="text-muted text-sm">
            Try:{" "}
            <em>
              &ldquo;I have a pre-revenue SaaS startup with 3 founders and a prototype — how should
              I value it?&rdquo;
            </em>
          </div>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`p-4 rounded-lg ${
              m.role === "user" ? "bg-brand/10 ml-8" : "bg-slate-50 mr-8"
            }`}
          >
            <div
              className={`text-xs font-semibold mb-1 ${m.role === "user" ? "text-brand" : "text-muted"}`}
            >
              {m.role === "user" ? "You" : "Advisor"}
            </div>
            <div className="text-sm whitespace-pre-wrap">{m.content}</div>
            {m.role === "assistant" && (
              <div className="mt-3 flex flex-wrap gap-2">
                {extractMethodLinks(m.content).map((slug) => (
                  <Link
                    key={slug}
                    href={`/methods/${slug}`}
                    className="inline-block bg-brand text-white px-3 py-1 rounded-full text-xs font-medium hover:no-underline"
                  >
                    Run {slug.replace(/-/g, " ")} valuation →
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="text-muted text-sm animate-pulse">Thinking…</div>}
      </div>

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Describe your startup…"
          className="input flex-1"
          aria-label="Valuation question"
        />
        <button onClick={send} disabled={loading} className="btn-brand">
          Ask
        </button>
      </div>
      <p className="text-xs text-muted mt-3">{AI_DISCLAIMER}</p>
    </div>
  );
}
