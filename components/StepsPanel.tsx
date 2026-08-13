"use client";

import { useEffect, useRef } from "react";
import { formatCurrency } from "@/lib/utils";

interface Step {
  label: string;
  value: number;
  formula: string;
}

interface StepsPanelProps {
  steps: Step[];
}

declare global {
  interface Window {
    katex: {
      render: (formula: string, element: HTMLElement, options?: Record<string, unknown>) => void;
    };
  }
}

export function StepsPanel({ steps }: StepsPanelProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current || !window.katex) return;

    const formulaElements = containerRef.current.querySelectorAll<HTMLElement>("[data-latex]");
    formulaElements.forEach((el) => {
      const formula = el.getAttribute("data-latex");
      if (formula) {
        try {
          window.katex.render(formula, el, { throwOnError: false });
        } catch {
          el.textContent = formula;
        }
      }
    });
  }, [steps]);

  if (!steps || steps.length === 0) {
    return null;
  }

  const staticMode = typeof window === "undefined" || !window.katex;

  return (
    <div className="card" ref={containerRef}>
      <h3 className="text-lg font-semibold text-text mb-4">Step-by-Step Derivation</h3>
      <div className="space-y-3">
        {steps.map((step, i) => (
          <div
            key={i}
            className={`py-3 px-4 rounded-lg ${
              i === steps.length - 1
                ? "bg-brand/10 border border-brand/20"
                : "bg-gray-50 border border-border"
            }`}
          >
            <div className="flex justify-between items-start gap-4">
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-sm text-text">{step.label}</div>
                <div className={`text-xs mt-1 ${staticMode ? "font-mono text-muted" : ""}`}>
                  {staticMode ? <code>{step.formula}</code> : <span data-latex={step.formula} />}
                </div>
              </div>
              <div className="text-right shrink-0">
                <div
                  className={`font-bold ${
                    i === steps.length - 1 ? "text-brand text-lg" : "text-text"
                  }`}
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
        ))}
      </div>
    </div>
  );
}
