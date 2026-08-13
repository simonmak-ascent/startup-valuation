import type { Metadata } from "next";
import { getBenchmarks, getIndustries } from "@/lib/db/repositories/public-data";
import { formatCurrency } from "@/lib/utils";

export const metadata: Metadata = {
  title: "Valuation Benchmarks — Startup Valuation Engine",
  description:
    "Industry valuation medians and percentiles, computed from provenance-tracked public data.",
  alternates: {
    canonical: "https://startup-valuation.simonmak.com/benchmarks",
  },
};

export const dynamic = "force-dynamic";

const LATEST_VERSION = "latest";

export default async function BenchmarksPage() {
  let benchmarks: Awaited<ReturnType<typeof getBenchmarks>> = [];
  let industries: Awaited<ReturnType<typeof getIndustries>> = [];
  try {
    benchmarks = await getBenchmarks(LATEST_VERSION);
    industries = await getIndustries();
  } catch {
    // DB unavailable — empty state below.
  }

  return (
    <div className="section max-w-[1100px]">
      <h1 className="text-3xl font-bold text-text mb-2">Valuation Benchmarks</h1>
      <p className="text-muted mb-6">
        Industry valuation medians and percentiles, computed exclusively from provenance-tracked
        data (no hardcoded values). Run <code>pnpm etl:compute-benchmarks</code> after importing
        data.
      </p>

      {benchmarks.length === 0 ? (
        <div className="card text-center py-16">
          <h2 className="text-xl font-semibold mb-2">No benchmarks yet</h2>
          <p className="text-muted">
            Benchmarks are computed from imported valuation events. Import public data first, then
            compute benchmarks.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto card p-6">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b-2 border-border text-left">
                <th className="py-3 px-4 font-semibold">Stage</th>
                <th className="py-3 px-4 font-semibold">P25</th>
                <th className="py-3 px-4 font-semibold">Median</th>
                <th className="py-3 px-4 font-semibold">P75</th>
                <th className="py-3 px-4 font-semibold">Count</th>
              </tr>
            </thead>
            <tbody>
              {benchmarks.map((b) => (
                <tr key={b.id} className="border-b border-border">
                  <td className="py-3 px-4 font-medium text-text">{b.stage ?? "All stages"}</td>
                  <td className="py-3 px-4 text-muted font-mono tabular-nums">
                    {formatCurrency(b.p25 ?? 0)}
                  </td>
                  <td className="py-3 px-4 font-semibold text-brand font-mono tabular-nums">
                    {formatCurrency(b.value)}
                  </td>
                  <td className="py-3 px-4 text-muted font-mono tabular-nums">
                    {formatCurrency(b.p75 ?? 0)}
                  </td>
                  <td className="py-3 px-4 text-muted font-mono tabular-nums">{b.count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {industries.length > 0 && (
        <div className="mt-8 card p-6">
          <h2 className="text-lg font-semibold mb-3">Industries tracked</h2>
          <div className="flex flex-wrap gap-2">
            {industries.map((i) => (
              <span
                key={i.id}
                className="inline-block bg-brand/10 text-brand px-3 py-1 rounded-full text-sm"
              >
                {i.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
