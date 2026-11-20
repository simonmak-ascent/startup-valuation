import YahooFinance from "yahoo-finance2";

/**
 * Live market data from Yahoo Finance.
 *
 * Yahoo's public JSON endpoints are split: `v8/finance/chart` answers without credentials, while
 * `v7/finance/quote` and `v10/finance/quoteSummary` answer **401** because they want a crumb carried
 * in a cookie. `yahoo-finance2` performs that crumb/cookie dance, so the fundamentals a valuation
 * comparables table actually needs — market cap, trailing P/E, price/sales, EV/EBITDA, EV/revenue —
 * are available server-side without a browser and without a database.
 *
 * Every figure below is the vendor's own value. A missing module yields `null`, never a zero: a
 * fabricated market cap in a valuation table is worse than an empty cell, and the pages are written
 * to render `—` for null rather than to invent.
 *
 * Measured 2026-11-18 against `AAPL`: marketCap 5.11e12, trailingPE 39.19, priceToSales 10.68,
 * enterpriseToEbitda 30.04, enterpriseToRevenue 10.76, currentPrice 351.91.
 */

// `queue.concurrency` is stated explicitly because the pages depend on it: 20 comparables at 1 would
// be 20 serial round-trips per render.
//
// **No timeout here.** `AbortSignal.timeout()` starts its clock when the signal is *created*, and
// this library reuses the constructor's `fetchOptions` for every request — so a signal built at
// module load aborts every call ~6 s after the process starts, and the pages then render their
// "source did not answer" state for ever while health stays green. The signal is created per call
// in `getQuote` instead.
export const yf = new YahooFinance({
  suppressNotices: ["yahooSurvey"],
  validation: { logErrors: false },
  queue: { concurrency: 8, interval: 0 },
});

/** Hard cap on one page's worth of quotes, whatever the upstream does. */
const DEADLINE_MS = 30_000;

export interface Quote {
  symbol: string;
  price: number | null;
  /** False when `price` is a previous close rather than a live quote. */
  live: boolean;
  currency: string;
  exchange: string;
  marketCap: number | null;
  trailingPE: number | null;
  priceToSales: number | null;
  evToEbitda: number | null;
  evToRevenue: number | null;
  week52High: number | null;
  week52Low: number | null;
  /** Position within the 52-week range: 0 at the low, 1 at the high. Null without a range. */
  week52Position: number | null;
  sourceUrl: string;
  retrievedAt: string;
}

/** A non-blank string, or null — the string counterpart of `num()`. */
function firstString(value: unknown): string | null {
  return typeof value === "string" && value.trim().length > 0 ? value : null;
}

function num(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function position(price: number | null, low: number | null, high: number | null): number | null {
  if (price == null || low == null || high == null || high <= low) return null;
  const clamped = Math.min(Math.max(price, low), high);
  return (clamped - low) / (high - low);
}

/** One symbol. Throws when Yahoo cannot be reached or answers nothing usable for it. */
export async function getQuote(symbol: string): Promise<Quote> {
  // The library types the result as `{}` unless the module list is generic over its keys, so the
  // shapes are declared here and every field is read through `num()`. Nothing is trusted to be
  // present: a module Yahoo omits yields null rather than a zero.
  type Module = Record<string, unknown>;
  type Summary = {
    summaryDetail?: Module;
    defaultKeyStatistics?: Module;
    financialData?: Module;
    price?: Module;
  };

  // `?? {}` because `validateResult: false` also drops the library's assertion that a result
  // exists: an empty `result` would otherwise throw a TypeError on the first property read, instead
  // of the `no price for X` line the page prints.
  const summary = ((await yf.quoteSummary(
    symbol,
    { modules: ["summaryDetail", "defaultKeyStatistics", "financialData", "price"] },
    // 15 s per call, and 8 in flight against a 20-symbol watchlist — so at most three waves, and
    // `getQuotes` caps the whole page at DEADLINE_MS regardless. The signal's clock starts before the
    // call is enqueued, so a tight budget here measures the queue, not Yahoo, and silently drops
    // comparables from the medians.
    {
      fetchOptions: { signal: AbortSignal.timeout(15_000) },
      // Yahoo omits required fields often enough that the library's schema rejects a usable
      // response: measured 2026-11-20, `FI` returned `summaryDetail.currency: null`, which the
      // schema requires to be a string, so the whole quote threw and the Fintech median published
      // over three companies. Every field below is already read through `num()` or a `typeof`
      // guard, so the validation adds no safety this file does not provide itself.
      validateResult: false,
    },
  )) ?? {}) as Summary;

  const detail: Module = summary.summaryDetail ?? {};
  const stats: Module = summary.defaultKeyStatistics ?? {};
  const financial: Module = summary.financialData ?? {};
  const priceModule: Module = summary.price ?? {};

  // `currentPrice` is the live figure; the fallbacks are last/previous close. The flag lets the
  // table label a non-live number instead of printing a close under a "Price" heading.
  const live = num(financial.currentPrice) ?? num(priceModule.regularMarketPrice);
  const price = live ?? num(detail.previousClose);
  const low = num(detail.fiftyTwoWeekLow);
  const high = num(detail.fiftyTwoWeekHigh);

  if (price == null) throw new Error(`Yahoo returned no price for ${symbol}`);

  // Prefer the first *usable* string, not the first non-nullish one: a malformed `price.currency`
  // (123, "") used to win over a perfectly good `detail.currency` and the quote rendered empty.
  const currency = firstString(priceModule.currency) ?? firstString(detail.currency);
  const exchange = firstString(priceModule.exchangeName) ?? firstString(detail.exchangeName);

  return {
    symbol,
    price,
    live: live != null,
    currency: typeof currency === "string" ? currency : "",
    exchange: typeof exchange === "string" ? exchange : "",
    marketCap: num(priceModule.marketCap) ?? num(detail.marketCap),
    trailingPE: num(detail.trailingPE),
    priceToSales: num(detail.priceToSalesTrailing12Months),
    evToEbitda: num(stats.enterpriseToEbitda),
    evToRevenue: num(stats.enterpriseToRevenue),
    week52High: high,
    week52Low: low,
    week52Position: position(price, low, high),
    sourceUrl: `https://finance.yahoo.com/quote/${encodeURIComponent(symbol)}`,
    retrievedAt: new Date().toISOString(),
  };
}

/**
 * Many symbols, in parallel, tolerating individual failures.
 *
 * A delisted or mistyped ticker must not blank the page: the caller gets what resolved and the
 * symbols that did not, so the UI can show a partial table and name what is missing.
 */
export async function getQuotes(symbols: readonly string[]): Promise<{
  quotes: Quote[];
  failed: string[];
}> {
  // A per-call timeout does not bound the page: with waves queued behind each other the worst case
  // is (symbols / concurrency) × timeout, and a hanging upstream then turns a page render into an
  // ALB idle timeout instead of the honest "source did not answer" state. This caps the page.
  const done = new Map<string, Quote>();
  const reasons: string[] = [];
  const tasks = symbols.map((s) =>
    getQuote(s)
      .then((quote) => {
        done.set(s, quote);
      })
      .catch((error: unknown) => {
        reasons.push(error instanceof Error ? error.message : String(error));
      }),
  );

  // Cleared on every path: an orphaned 30 s timer outlives the response, and both pages revalidate
  // every 300 s, so without this the process carries a pending handle per render.
  let timer: ReturnType<typeof setTimeout> | undefined;
  let fired = false;
  const deadline = new Promise<void>((resolve) => {
    timer = setTimeout(() => {
      fired = true;
      resolve();
    }, DEADLINE_MS);
  });
  try {
    await Promise.race([Promise.all(tasks), deadline]);
  } finally {
    clearTimeout(timer);
  }

  // One line per render, not per symbol. A symbol that never settled pushes no reason, so a trip of
  // the deadline — the case it exists for — would otherwise be the only silent failure.
  const unresolved = symbols.filter((sym) => !done.has(sym));
  if (reasons.length > 0 || unresolved.length > 0) {
    const parts = [`[finance] ${unresolved.length}/${symbols.length} unresolved`];
    // "at the deadline" only when the race actually fired: a symbol that rejected fast is failed,
    // not unresolved, and saying otherwise sends the reader looking for a timeout that never happened.
    if (fired && unresolved.length > 0) parts.push(`at the ${DEADLINE_MS} ms deadline`);
    if (reasons.length > 0) parts.push(`${reasons.length} failed, first: ${reasons[0]}`);
    console.error(parts.join("; "));
  }

  return {
    quotes: symbols.map((s) => done.get(s)).filter((q): q is Quote => q != null),
    // Anything not resolved when the deadline fired is reported as failed, which is what the page
    // shows the reader: a named symbol it could not price.
    failed: unresolved,
  };
}

/** Median of the defined values; null when nothing is defined. */
export function median(values: Array<number | null>): number | null {
  const known = values.filter((v): v is number => v != null && Number.isFinite(v)).sort((a, b) => a - b);
  if (known.length === 0) return null;
  const mid = Math.floor(known.length / 2);
  return known.length % 2 === 0 ? (known[mid - 1]! + known[mid]!) / 2 : known[mid]!;
}
