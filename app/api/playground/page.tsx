import type { Metadata } from "next";
import { APIPlayground } from "@/components/APIPlayground";

export const metadata: Metadata = {
  title: "API Playground — Startup Valuation Engine",
  description:
    "Interactive playground for the Startup Valuation API. Test 27+ valuation methods with live inputs and JSON responses.",
  alternates: {
    canonical: "https://startup-valuation.simonmak.com/api/playground",
  },
};

export default function ApiPlaygroundPage() {
  return (
    <div className="section max-w-[1100px]">
      <h1 className="text-3xl font-bold text-text mb-2">API Playground</h1>
      <p className="text-muted mb-8">
        Explore the valuation API interactively. Each method maps to the Python library via the{" "}
        <code>/api/calculate</code> endpoint.
      </p>

      <APIPlayground />

      <div className="card mt-8">
        <h2 className="text-lg font-semibold mb-3">Programmatic access</h2>
        <div className="bg-slate-800 text-slate-200 p-4 rounded-lg text-xs font-mono overflow-x-auto">
          <div className="mb-2">
            <span className="text-green-400"># TypeScript SDK</span>
          </div>
          <pre className="whitespace-pre-wrap">{`import { scorecard } from "@simonmak/startup-valuation";
const r = await scorecard(1500000, [0.3,0.25,0.15,0.1,0.1,0.05,0.05], [1.25,1.5,1.2,0.75,1,0.9,1]);
console.log(r.value); // 1800000`}</pre>
        </div>
        <div className="bg-slate-800 text-slate-200 p-4 rounded-lg text-xs font-mono mt-3 overflow-x-auto">
          <div className="mb-2">
            <span className="text-green-400"># MCP JSON-RPC (AI agents)</span>
          </div>
          <pre className="whitespace-pre-wrap">{`POST /api
{ "jsonrpc": "2.0", "method": "tools/call",
  "params": { "name": "valuation_scorecard", "arguments": {...} }, "id": 1 }`}</pre>
        </div>
      </div>
    </div>
  );
}
