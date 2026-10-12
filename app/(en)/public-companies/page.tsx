import type { Metadata } from "next";
import { getCompanies } from "@/lib/db/repositories/public-data";

export const metadata: Metadata = {
  title: "Public Company Valuations — Startup Valuation Engine",
  description:
    "Searchable database of public company valuations and financial metrics, aggregated from recognized sources with full provenance.",
  alternates: {
    canonical: "https://startup-valuation.simonmak.com/public-companies",
  },
};

export const dynamic = "force-dynamic";

async function loadCompanies(search?: string) {
  try {
    return await getCompanies(search ? { search } : {}, 100);
  } catch {
    return [];
  }
}

export default async function PublicCompaniesPage({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  const companies = await loadCompanies(q);

  return (
    <div className="section max-w-[1100px]">
      <h1 className="text-3xl font-bold text-text mb-2">Public Companies</h1>
      <p className="text-muted mb-6">
        Aggregated company profiles and financial metrics from recognized public sources. Every data
        point is provenance-tracked.
      </p>

      <form method="GET" className="flex gap-3 mb-8 max-w-md">
        <input
          type="search"
          name="q"
          defaultValue={q}
          placeholder="Search companies…"
          className="input flex-1"
          aria-label="Search companies"
        />
        <button type="submit" className="btn-brand">
          Search
        </button>
      </form>

      {companies.length === 0 ? (
        <div className="card text-center py-16">
          <h2 className="text-xl font-semibold mb-2">No data yet</h2>
          <p className="text-muted">
            Public company data is imported via <code>pnpm etl:import</code> from recognized sources
            (SEC EDGAR, Crunchbase). No synthetic data is seeded.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {companies.map((c) => (
            <div key={c.id} className="card">
              <h3 className="font-semibold text-text">
                {c.name}
                {c.ticker && (
                  <span className="text-muted font-mono ml-2 text-sm">({c.ticker})</span>
                )}
              </h3>
              {c.sector && <p className="text-muted text-sm mt-1">{c.sector}</p>}
              {c.country && <p className="text-muted text-xs mt-1">{c.country}</p>}
              <div className="mt-3 pt-3 border-t border-border text-xs text-muted">
                <div>
                  Source: <span className="text-text">{c.source_name}</span>
                </div>
                <div className="mt-1">Retrieved: {c.source_retrieved_at.slice(0, 10)}</div>
                <a
                  href={c.source_url}
                  className="text-brand hover:underline break-all"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {c.source_url}
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
