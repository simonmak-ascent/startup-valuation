"use client";

import { useEffect, useRef, useState } from "react";
import type { InputField } from "@/lib/valuation/types";
import { formatNumber } from "@/lib/utils";

interface SensitivitySlidersProps {
  inputs: InputField[];
  values: Record<string, number>;
  onValuesChange: (values: Record<string, number>) => void;
}

function sliderBounds(input: InputField, value: number) {
  const center = value !== 0 ? value : input.defaultValue !== 0 ? input.defaultValue : 1;
  const span = Math.abs(center);
  const min = input.min ?? (center >= 0 ? center - span : center * 1.5);
  const max = input.max ?? (center >= 0 ? center + span : center * 0.5);
  const step = input.step ?? Math.max(Math.abs(max - min) / 100, 0.0001);
  return { min, max, step };
}

export function SensitivitySliders({ inputs, values, onValuesChange }: SensitivitySlidersProps) {
  const [local, setLocal] = useState<Record<string, number>>(values);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    setLocal(values);
  }, [values]);

  const handleChange = (name: string, value: number) => {
    const next = { ...local, [name]: value };
    setLocal(next);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => onValuesChange(next), 300);
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-text mb-1">Sensitivity Analysis</h3>
      <p className="text-sm text-muted mb-4">
        Drag a slider to see how changes affect the valuation in real time.
      </p>
      <div className="space-y-4">
        {inputs.map((input) => {
          const value = local[input.name] ?? input.defaultValue;
          const { min, max, step } = sliderBounds(input, value);
          return (
            <div key={input.name}>
              <div className="flex justify-between items-baseline mb-1">
                <label className="text-sm font-medium text-text" htmlFor={`slider-${input.name}`}>
                  {input.label}
                </label>
                <span className="text-sm font-semibold text-brand tabular-nums">
                  {formatNumber(value, 4)}
                </span>
              </div>
              <input
                id={`slider-${input.name}`}
                type="range"
                min={min}
                max={max}
                step={step}
                value={value}
                onChange={(e) => handleChange(input.name, Number(e.target.value))}
                className="w-full accent-[#0083AB]"
                aria-label={input.label}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}
