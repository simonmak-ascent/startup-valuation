"use client";

import { renderLatexInline } from "@/lib/katex";
import { formatCurrency } from "@/lib/utils";

interface Step {
  label: string;
  value: number;
  formula: string;
}

interface StepsPanelProps {
  steps: Step[];
}

export function StepsPanel({ steps }: StepsPanelProps) {
  if (!steps || steps.length === 0) {
    return null;
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-text mb-4">Step-by-Step Derivation</h3>
      <div className="space-y-3">
        {steps.map((step, i) => {
          const isFinal = i === steps.length - 1;
          const formulaHtml = step.formula ? renderLatexInline(step.formula) : null;

          return (
            <div
              key={i}
              className={`py-3 px-4 rounded-lg ${
                isFinal ? "bg-brand/10 border border-brand/20" : "bg-gray-50 border border-border"
              }`}
            >
              <div className="flex justify-between items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-sm text-text">{step.label}</div>
                  {formulaHtml && (
                    <div
                      className="text-xs mt-1 text-muted"
                      dangerouslySetInnerHTML={{ __html: formulaHtml }}
                    />
                  )}
                </div>
                <div className="text-right shrink-0">
                  <div
                    className={`font-bold font-mono tabular-nums ${isFinal ? "text-brand text-lg" : "text-text"}`}
                  >
                    {step.value % 1 === 0
                      ? formatCurrency(step.value)
                      : step.value.toLocaleString("en-US", {
                          maximumFractionDigits: 4,
                        })}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
