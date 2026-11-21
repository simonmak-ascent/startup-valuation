import { getRiskFreeRate } from "@/lib/finance/treasury";
import { getSpotRate } from "@/lib/finance/fx";
import { getAnnualNetIncome } from "@/lib/finance/sec";

/**
 * The inputs a valuation tool cannot invent: `risk_free_rate`, `spot_rate`, and net income.
 *
 * Three parameters in the tool surface had no source in the product — the CAPM tools say
 * "typically 10-year Treasury yield", the PPP method needs an exchange rate, and `pe_ratio` needs
 * net income — and each was caller-supplied with a convention attached. This route publishes the
 * figures with the date and the publisher behind them, so a caller can fetch rather than recall.
 *
 * Each value carries its own `asOf` and `sourceUrl`. A source that does not answer is absent, never
 * filled: the caller sees the gap and can decide what to do about it.
 *
 * `?symbol=AAPL` adds that company's latest filed annual net income from SEC EDGAR.
 */
export const revalidate = 3600;

/**
 * No `Access-Control-Allow-Origin`. The consumer is an agent or a server, not a browser; a wildcard
 * would let any third party's page spend the estate's SEC quota from its visitors' browsers, and
 * there is no credential or origin to revoke. The data is public, so this withholds nothing.
 *
 * `s-maxage` is a hint, not the bound: the ALB is ingress-only and nginx serves static files, so no
 * intermediary honours it. The real bound is in `sec.ts` — promise memo per ticker, a two-at-a-time
 * limiter, and a minute's negative cache for a refusing EDGAR.
 */
const JSON_HEADERS = {
  "Content-Type": "application/json",
  "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=600",
} as const;

/**
 * `symbol` reaches a module-level memo in `sec.ts`, so it is bounded here: an arbitrary string would
 * otherwise become a permanent cache key on a public route. A ticker is 1-10 characters of
 * A-Z, 0-9, dot or hyphen (`BRK.B`), and anything else is treated as absent rather than guessed at.
 */
const SYMBOL_PATTERN = /^[A-Z][A-Z0-9.-]{0,9}$/;

export async function GET(request: Request): Promise<Response> {
  const raw = new URL(request.url).searchParams.get("symbol")?.trim().toUpperCase();
  const symbol = raw && SYMBOL_PATTERN.test(raw) ? raw : null;

  const [riskFreeRate, fxRate, netIncome] = await Promise.all([
    getRiskFreeRate(),
    getSpotRate("USD", "HKD"),
    symbol ? getAnnualNetIncome(symbol) : Promise.resolve(null),
  ]);

  const body = {
    risk_free_rate: riskFreeRate,
    fx: fxRate,
    net_income: netIncome,
    note:
      "risk_free_rate is per cent as published (4.92 = 4.92%); net_income is the newest filed " +
      "annual figure under the `concept` reported, not trailing twelve months — `stale: true` means " +
      "it is more than two years old and is not the current year's income, and `fiscalYear` is the " +
      "period end's year, not the filing's `fy` focus. A field is null when its source did not answer.",
  };
  return new Response(JSON.stringify(body), { status: 200, headers: JSON_HEADERS });
}
