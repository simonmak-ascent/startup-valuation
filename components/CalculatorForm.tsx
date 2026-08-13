"use client";

import { useState } from "react";
import type { InputField } from "@/lib/valuation/types";

interface CalculatorFormProps {
  inputs: InputField[];
  onSubmit: (values: Record<string, number>) => void;
  loading: boolean;
}

export function CalculatorForm({ inputs, onSubmit, loading }: CalculatorFormProps) {
  const [values, setValues] = useState<Record<string, string>>(() => {
    const initial: Record<string, string> = {};
    for (const input of inputs) {
      initial[input.name] = String(input.defaultValue);
    }
    return initial;
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (name: string, value: string) => {
    setValues((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[name];
        return next;
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const newErrors: Record<string, string> = {};
    const params: Record<string, number> = {};

    for (const input of inputs) {
      const raw = values[input.name];
      if (!raw) {
        newErrors[input.name] = "Required";
        continue;
      }
      const num = Number(raw);
      if (isNaN(num)) {
        newErrors[input.name] = "Must be a number";
        continue;
      }
      if (input.min !== undefined && num < input.min) {
        newErrors[input.name] = `Minimum: ${input.min}`;
        continue;
      }
      if (input.max !== undefined && num > input.max) {
        newErrors[input.name] = `Maximum: ${input.max}`;
        continue;
      }
      params[input.name] = num;
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    onSubmit(params);
  };

  return (
    <form onSubmit={handleSubmit} className="card">
      <h2 className="text-xl font-semibold text-text mb-4">Input Parameters</h2>
      <div className="space-y-4">
        {inputs.map((input) => (
          <div key={input.name}>
            <label htmlFor={`input-${input.name}`} className="label">
              {input.label}
            </label>
            {input.description && <p className="text-xs text-muted mb-1">{input.description}</p>}
            <input
              id={`input-${input.name}`}
              type="number"
              step={input.step ?? "any"}
              value={values[input.name] ?? ""}
              onChange={(e) => handleChange(input.name, e.target.value)}
              className={`input ${errors[input.name] ? "input-error" : ""}`}
              aria-invalid={!!errors[input.name]}
              aria-describedby={errors[input.name] ? `error-${input.name}` : undefined}
            />
            {errors[input.name] && (
              <p id={`error-${input.name}`} className="text-red-500 text-xs mt-1" role="alert">
                {errors[input.name]}
              </p>
            )}
          </div>
        ))}
      </div>
      <button type="submit" disabled={loading} className="btn-brand w-full mt-6">
        {loading ? "Calculating..." : "Calculate Valuation"}
      </button>
    </form>
  );
}
