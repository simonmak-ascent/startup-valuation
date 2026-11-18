import type { Metadata } from "next";
import { getQuotes, median, type Quote } from "@/lib/finance/yahoo";
import { ALL_SYMBOLS, WATCHLIST } from "@/lib/finance/watchlist";

export const metadata: Metadata = {
  title: "Valuation Benchmarks",
  description:
    "Median trailing P/E, price/sales and EV/EBITDA across the public comparables, computed from Yahoo Finance data refreshed every five minutes.",
  alternates: {
    canonical: "https://startup-valuation.ascent-partners.com/benchmarks",
  },
};

// A price page that re-fetches twenty symbols on every request is an outage amplifier:
// five minutes of ISR keeps it current enough for comparables and survives a Yahoo 429.
// Note: with ISR the page is rendered at build time too, so `pnpm build` needs egress to
// Yahoo. If the build cannot reach it, the prerendered empty state is served until the
// first revalidation after deploy.
export const revalidate = 300;

function ratio(value: number | null): string {
  return value == null ? "—" : `${value.toFixed(2)}×`;
}

/**
 * Industry medians, computed at request time.
 *
 * The page previously read a `benchmark` table that no source ever filled, so it showed an empty
 * state with a title promising medians. The medians are now the vendor's own reported multiples,
 * grouped by the vertical the product advertises, with the sample size stated — a median over three
 * comparables is not the same claim as a median over thirty, and the page says which it is.
 */
export default async function BenchmarksPage() {
  const symbols = ALL_SYMBOLS;
  const { quotes, failed } = await getQuotes(symbols);
  const bySymbol = new Map(quotes.map((q) => [q.symbol, q]));
  const retrievedAt = quotes[0]?.retrievedAt ?? null;

  // `n` counts companies that resolved; each median drops the companies that did not report that
  // metric, so every figure carries the count it was actually computed over.
  const sampleSize = (members: Quote[], pick: (q: Quote) => number | null) =>
    members.filter((m) => pick(m) != null).length;

  const rows = Object.entries(WATCHLIST).map(([sector, list]) => {
    const members = list.map((s) => bySymbol.get(s)).filter((q): q is Quote => Boolean(q));
    return {
      sector,
      n: members.length,
      pe: median(members.map((m) => m.trailingPE)),
      ps: median(members.map((m) => m.priceToSales)),
      evEbitda: median(members.map((m) => m.evToEbitda)),
      position: median(members.map((m) => m.week52Position)),
      peN: sampleSize(members, (m) => m.trailingPE),
      psN: sampleSize(members, (m) => m.priceToSales),
      evN: sampleSize(members, (m) => m.evToEbitda),
      posN: sampleSize(members, (m) => m.week52Position),
    };
  });

  const overall = {
    n: quotes.length,
    pe: median(quotes.map((q) => q.trailingPE)),
    ps: median(quotes.map((q) => q.priceToSales)),
    evEbitda: median(quotes.map((q) => q.evToEbitda)),
    peN: quotes.filter((q) => q.trailingPE != null).length,
    psN: quotes.filter((q) => q.priceToSales != null).length,
    evN: quotes.filter((q) => q.evToEbitda != null).length,
  };

  return (
    <div className="section max-w-[1000px]">
      <h1 className="text-3xl font-bold text-text mb-2">Valuation Benchmarks</h1>
      <p className="text-muted mb-2">
        Median multiples across the public comparables, computed from Yahoo Finance data and
        revalidated every five minutes. Each row states its sample size: these are medians over a handful of large-cap
        comparables, not a survey of the whole industry.
      </p>
      <p className="text-muted text-sm mb-8">
        {retrievedAt
          ? `Retrieved ${new Date(retrievedAt).toISOString().replace("T", " ").slice(0, 19)} UTC`
          : "No retrieval time: the source did not answer"}
        {failed.length > 0 ? ` · unresolved: ${failed.join(", ")}` : ""}
      </p>

      {quotes.length === 0 ? (
        <p className="text-muted">
          The price source did not answer. Nothing is shown rather than a stale or invented
          benchmark.
        </p>
      ) : (
        <>
          <table className="w-full text-sm mb-10">
            <thead>
              <tr className="text-left text-muted border-b border-border">
                <th className="py-2 pr-4">Vertical</th>
                <th className="py-2 pr-4">n</th>
                <th className="py-2 pr-4">Median P/E</th>
                <th className="py-2 pr-4">Median P/S</th>
                <th className="py-2 pr-4">Median EV/EBITDA</th>
                <th className="py-2">Median 52-week position</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.sector} className="border-b border-border/50">
                  <td className="py-2 pr-4">{row.sector}</td>
                  <td className="py-2 pr-4">{row.n}</td>
                  <td className="py-2 pr-4">
                    {ratio(row.pe)} <span className="text-muted">(n={row.peN})</span>
                  </td>
                  <td className="py-2 pr-4">
                    {ratio(row.ps)} <span className="text-muted">(n={row.psN})</span>
                  </td>
                  <td className="py-2 pr-4">
                    {ratio(row.evEbitda)} <span className="text-muted">(n={row.evN})</span>
                  </td>
                  <td className="py-2">
                    {row.position == null ? "—" : `${Math.round(row.position * 100)}%`}{" "}
                    <span className="text-muted">(n={row.posN})</span>
                  </td>
                </tr>
              ))}
              <tr className="border-t border-border font-semibold">
                <td className="py-2 pr-4">All comparables</td>
                <td className="py-2 pr-4">{overall.n}</td>
                <td className="py-2 pr-4">
                  {ratio(overall.pe)} <span className="text-muted">(n={overall.peN})</span>
                </td>
                <td className="py-2 pr-4">
                  {ratio(overall.ps)} <span className="text-muted">(n={overall.psN})</span>
                </td>
                <td className="py-2 pr-4">
                  {ratio(overall.evEbitda)} <span className="text-muted">(n={overall.evN})</span>
                </td>
                <td className="py-2">—</td>
              </tr>
            </tbody>
          </table>

          <p className="text-muted text-sm">
            A median is computed over the comparables that returned the metric; a metric the vendor
            omits (for example EV/EBITDA for a loss-making company) is excluded rather than counted as
            zero, and the sample size above reports how many companies each row actually covers.
          </p>
        </>
      )}
    </div>
  );
}
