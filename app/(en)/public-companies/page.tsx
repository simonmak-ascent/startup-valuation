import type { Metadata } from "next";
import { getQuotes, type Quote } from "@/lib/finance/yahoo";
import { eodhdConfigured, getFundamentalsMany } from "@/lib/finance/eodhd";
import { ALL_SYMBOLS, WATCHLIST } from "@/lib/finance/watchlist";

export const metadata: Metadata = {
  title: "Public Company Multiples",
  description:
    "Live multiples for the public comparables behind the valuation methods: market cap, trailing P/E, price/sales and EV/EBITDA — from EODHD fundamentals where a key is configured, otherwise from Yahoo Finance — refreshed every five minutes.",
  alternates: {
    canonical: "https://startup-valuation.ascent-partners.com/public-companies",
  },
};

// A price page that re-fetches twenty symbols on every request is an outage amplifier:
// five minutes of ISR keeps it current enough for comparables and survives a Yahoo 429.
// Note: with ISR the page is rendered at build time too, so `pnpm build` needs egress to
// Yahoo. If the build cannot reach it, the prerendered empty state is served until the
// first revalidation after deploy.
export const revalidate = 300;

function money(value: number | null, currency = "USD"): string {
  if (value == null) return "—";
  if (Math.abs(value) >= 1e12) return `${(value / 1e12).toFixed(2)}T ${currency}`;
  if (Math.abs(value) >= 1e9) return `${(value / 1e9).toFixed(2)}B ${currency}`;
  if (Math.abs(value) >= 1e6) return `${(value / 1e6).toFixed(2)}M ${currency}`;
  return `${value.toFixed(2)} ${currency}`;
}

function ratio(value: number | null): string {
  return value == null ? "—" : `${value.toFixed(2)}×`;
}

export default async function PublicCompaniesPage() {
  const symbols = ALL_SYMBOLS;
  // Two sources, fetched together. EODHD carries the reported figures behind the multiples
  // (market cap, revenue, EBITDA, enterprise value) and is preferred when a key is configured;
  // Yahoo answers the quote either way. With no key this is a no-op and the page is Yahoo-only.
  const [{ quotes, failed }, fundamentalBatch] = await Promise.all([
    getQuotes(symbols),
    eodhdConfigured() ? getFundamentalsMany(symbols) : Promise.resolve({ fundamentals: new Map(), failed: [] }),
  ]);
  const fundamentals = fundamentalBatch.fundamentals;
  const bySymbol = new Map(quotes.map((q) => [q.symbol, q]));
  const retrievedAt = quotes[0]?.retrievedAt ?? null;
  // What actually arrived, not what was configured: a key with no coverage must not claim EODHD.
  const covered = quotes.filter((q) => fundamentals.has(q.symbol)).length;

  return (
    <div className="section max-w-[1100px]">
      <h1 className="text-3xl font-bold text-text mb-2">Public Companies</h1>
      <p className="text-muted mb-2">
        Live multiples for the comparables behind the methods, grouped by the industry vertical the
        product advertises. Every figure comes from one of the two sources named below, refreshed
        every five minutes; a metric neither source returns is shown as <code>—</code> rather than
        filled in.
      </p>
      <p className="text-muted text-sm mb-8">
        {covered === 0 ? "Source" : "Multiples"}:{" "}
        {covered > 0 ? (
          <>
            {covered === quotes.length ? "from " : `${covered} of ${quotes.length} from `}
            <a className="underline" href="https://eodhd.com" rel="noreferrer noopener">
              EODHD
            </a>{" "}
            fundamentals, the rest and all prices from{" "}
            <a className="underline" href="https://finance.yahoo.com" rel="noreferrer noopener">
              Yahoo Finance
            </a>
          </>
        ) : (
          <a className="underline" href="https://finance.yahoo.com" rel="noreferrer noopener">
            Yahoo Finance
          </a>
        )}
        {retrievedAt
          ? ` · retrieved ${new Date(retrievedAt).toISOString().replace("T", " ").slice(0, 19)} UTC`
          : ""}
        {failed.length > 0 ? ` · unresolved symbols: ${failed.join(", ")}` : ""}
      </p>

      {quotes.length === 0 ? (
        <p className="text-muted">
          The price source did not answer, so this page shows nothing rather than stale or invented
          figures. Try again shortly.
        </p>
      ) : (
        Object.entries(WATCHLIST).map(([sector, list]) => {
          const rows = list.map((s) => bySymbol.get(s)).filter((q): q is Quote => Boolean(q));
          // A vertical where every symbol failed still gets its heading and a line saying so: the
          // benchmarks page shows the row with n=0, and a section that silently disappears is only
          // discoverable by counting the header's symbols.
          if (rows.length === 0) {
            return (
              <section key={sector} className="mb-10">
                <h2 className="text-xl font-semibold text-text mb-3">{sector}</h2>
                <p className="text-muted text-sm">
                  No price resolved for this vertical ({list.join(", ")}).
                </p>
              </section>
            );
          }
          return (
            <section key={sector} className="mb-10">
              <h2 className="text-xl font-semibold text-text mb-3">{sector}</h2>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-muted border-b border-border">
                      <th className="py-2 pr-4">Symbol</th>
                      <th className="py-2 pr-4">Price</th>
                      <th className="py-2 pr-4">Market cap</th>
                      <th className="py-2 pr-4">P/E</th>
                      <th className="py-2 pr-4">P/S</th>
                      <th className="py-2 pr-4">EV/EBITDA</th>
                      <th className="py-2">52-week</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((q) => {
                      const fundamentalsRow = fundamentals.get(q.symbol);
                      return (
                      <tr key={q.symbol} className="border-b border-border/50">
                        <td className="py-2 pr-4">
                          <a className="underline" href={q.sourceUrl} rel="noreferrer noopener">
                            {q.symbol}
                          </a>
                        </td>
                        <td className="py-2 pr-4">
                        {money(q.price, q.currency)}
                        {q.live ? "" : <span className="text-muted"> (prev close)</span>}
                      </td>
                        <td className="py-2 pr-4">
                          {money(fundamentalsRow?.marketCap ?? q.marketCap, q.currency)}
                        </td>
                        <td className="py-2 pr-4">{ratio(fundamentalsRow?.trailingPE ?? q.trailingPE)}</td>
                        <td className="py-2 pr-4">{ratio(fundamentalsRow?.priceToSales ?? q.priceToSales)}</td>
                        <td className="py-2 pr-4">{ratio(fundamentalsRow?.evToEbitda ?? q.evToEbitda)}</td>
                        <td className="py-2">
                          {q.week52Position == null
                            ? "—"
                            : `${Math.round(q.week52Position * 100)}% of range`}
                        </td>
                      </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </section>
          );
        })
      )}
    </div>
  );
}
