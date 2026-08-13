"use client";

import { useState } from "react";
import { getAllMethods } from "@/lib/methods";

export function APIPlayground() {
  const methods = getAllMethods();
  const [selected, setSelected] = useState(methods[0]!.slug);
  const [params, setParams] = useState<Record<string, string>>({});
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const method = methods.find((m) => m.slug === selected)!;

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const values: Record<string, number> = {};
      for (const input of method.inputs) {
        values[input.name] = Number(params[input.name] ?? input.defaultValue);
      }
      const body = method.toParams ? method.toParams(values) : values;

      const res = await fetch("/api/calculate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ method: method.methodName, params: body }),
      });
      const data = await res.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">1. Select a method</h3>
        <select
          value={selected}
          onChange={(e) => setSelected(e.target.value)}
          className="input"
          aria-label="Method"
        >
          {methods.map((m) => (
            <option key={m.slug} value={m.slug}>
              {m.name} ({m.methodName})
            </option>
          ))}
        </select>

        <h3 className="text-lg font-semibold mt-6 mb-4">2. Parameters</h3>
        <div className="space-y-3">
          {method.inputs.map((input) => (
            <div key={input.name}>
              <label className="label text-sm" htmlFor={`pg-${input.name}`}>
                {input.label} <code className="text-xs text-brand">({input.name})</code>
              </label>
              <input
                id={`pg-${input.name}`}
                type="number"
                className="input"
                defaultValue={input.defaultValue}
                onChange={(e) => setParams((p) => ({ ...p, [input.name]: e.target.value }))}
              />
            </div>
          ))}
        </div>

        <button onClick={run} disabled={loading} className="btn-brand w-full mt-6">
          {loading ? "Running…" : "Execute"}
        </button>
        {error && <p className="text-red-500 text-sm mt-3">{error}</p>}
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold mb-4">3. Response</h3>
        {result ? (
          <pre className="bg-slate-800 text-slate-200 p-4 rounded-lg text-xs overflow-x-auto">
            {result}
          </pre>
        ) : (
          <div className="text-muted text-sm">
            Select a method, set parameters, and press Execute to see the JSON response (with
            step-by-step derivation and traceability metadata).
          </div>
        )}
      </div>
    </div>
  );
}
