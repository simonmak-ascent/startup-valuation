"use client";

import { useState, useCallback } from "react";
import type { MethodConfig } from "@/lib/valuation/types";
import { CalculatorForm } from "./CalculatorForm";
import { ResultPanel } from "./ResultPanel";
import { StepsPanel } from "./StepsPanel";
import { SourcesSection } from "./SourcesSection";

interface CalculatorPageProps {
  config: MethodConfig;
}

export function CalculatorPage({ config }: CalculatorPageProps) {
  const [result, setResult] = useState<{
    value: number;
    steps: { label: string; value: number; formula: string }[];
    formulaNumber: string;
    chapter: string;
    libraryVersion: string;
    timestamp: string;
    gitCommit: string;
    auditId?: string;
    auditStatus: string;
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (params: Record<string, unknown>) => {
      setLoading(true);
      setError(null);
      setResult(null);

      try {
        const response = await fetch("/api/calculate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ method: config.slug, params }),
        });

        if (!response.ok) {
          const errData = await response.json().catch(() => ({}));
          throw new Error(errData.message ?? `Calculation failed (${response.status})`);
        }

        const data = await response.json();
        setResult(data);

        // Fire-and-forget audit log to SurrealDB
        fetch("/api/audit", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            method: config.slug,
            inputs: params,
            result: data.value,
            steps: data.steps,
            formula_number: data.formula_number,
            chapter: data.chapter,
            library_version: data.library_version,
            git_commit: data.git_commit,
          }),
        }).catch(() => {});
      } catch (e) {
        setError(e instanceof Error ? e.message : "An unexpected error occurred");
      } finally {
        setLoading(false);
      }
    },
    [config.slug],
  );

  return (
    <div className="section max-w-[900px]">
      <div className="mb-8">
        <nav className="text-sm text-muted mb-4">
          <a href="/" className="text-brand hover:underline">
            Home
          </a>
          <span className="mx-2">→</span>
          <a href="/#methods" className="text-brand hover:underline">
            Methods
          </a>
          <span className="mx-2">→</span>
          <span className="text-text">{config.name}</span>
        </nav>

        <h1 className="text-3xl font-bold text-text mb-2">{config.name}</h1>
        <div className="flex gap-2 flex-wrap mb-4">
          <span className="inline-block bg-blue-50 text-blue-700 px-2.5 py-0.5 rounded-xl text-xs font-medium">
            {config.category}
          </span>
          <span className="inline-block bg-brand/10 text-brand px-2.5 py-0.5 rounded-xl text-xs font-medium">
            {config.textbookChapter}
          </span>
          <span className="inline-block bg-amber-50 text-amber-700 px-2.5 py-0.5 rounded-xl text-xs font-medium">
            Formula {config.formulaNumber}
          </span>
        </div>
        <p className="text-muted text-lg">{config.description}</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <CalculatorForm inputs={config.inputs} onSubmit={handleSubmit} loading={loading} />
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
              <button onClick={() => setError(null)} className="ml-2 underline hover:no-underline">
                Dismiss
              </button>
            </div>
          )}
        </div>

        <div>
          {loading && (
            <div className="card animate-pulse space-y-4">
              <div className="h-8 bg-border rounded w-2/3" />
              <div className="h-16 bg-border rounded" />
              <div className="h-4 bg-border rounded w-1/2" />
              <div className="space-y-2">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-6 bg-border rounded" />
                ))}
              </div>
            </div>
          )}

          {result && (
            <div className="space-y-6">
              <ResultPanel
                value={result.value}
                method={config.name}
                formulaNumber={result.formulaNumber}
                auditStatus={result.auditStatus}
              />
              <StepsPanel steps={result.steps} />
            </div>
          )}
        </div>
      </div>

      {result && (
        <div className="mt-8">
          <SourcesSection
            chapter={config.textbookChapter}
            formulaNumber={config.formulaNumber}
            libraryVersion={result.libraryVersion}
            timestamp={result.timestamp}
            gitCommit={result.gitCommit}
          />
        </div>
      )}
    </div>
  );
}
