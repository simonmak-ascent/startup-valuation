import type { Metadata } from "next";
import { getQuotes, type Quote } from "@/lib/finance/yahoo";
import { ALL_SYMBOLS, WATCHLIST } from "@/lib/finance/watchlist";

export const metadata: Metadata = {
  title: "Public Company Multiples",
  description:
    "Live multiples for the public comparables behind the valuation methods: market cap, trailing P/E, price/sales and EV/EBITDA, fetched from Yahoo Finance and refreshed every five minutes.",
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
  const { quotes, failed } = await getQuotes(symbols);
  const bySymbol = new Map(quotes.map((q) => [q.symbol, q]));
  const retrievedAt = quotes[0]?.retrievedAt ?? null;

  return (
    <div className="section max-w-[1100px]">
      <h1 className="text-3xl font-bold text-text mb-2">Public Companies</h1>
      <p className="text-muted mb-2">
        Live multiples for the comparables behind the methods, grouped by the industry vertical the
        product advertises. Every figure is Yahoo Finance&apos;s own value, refreshed every five minutes; a metric
        the vendor does not return is shown as <code>—</code> rather than filled in.
      </p>
      <p className="text-muted text-sm mb-8">
        Source:{" "}
        <a className="underline" href="https://finance.yahoo.com" rel="noreferrer noopener">
          Yahoo Finance
        </a>
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
                    {rows.map((q) => (
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
                        <td className="py-2 pr-4">{money(q.marketCap, q.currency)}</td>
                        <td className="py-2 pr-4">{ratio(q.trailingPE)}</td>
                        <td className="py-2 pr-4">{ratio(q.priceToSales)}</td>
                        <td className="py-2 pr-4">{ratio(q.evToEbitda)}</td>
                        <td className="py-2">
                          {q.week52Position == null
                            ? "—"
                            : `${Math.round(q.week52Position * 100)}% of range`}
                        </td>
                      </tr>
                    ))}
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
