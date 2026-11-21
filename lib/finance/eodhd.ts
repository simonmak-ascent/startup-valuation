/**
 * EODHD fundamentals — the second market-data source, for the figures Yahoo's quote does not carry.
 *
 * Why this exists: the comparables tools take `market_cap`, `revenue`, `ebitda` and
 * `enterprise_value` as inputs, and the Yahoo quote fetched by `yahoo.ts` exposes only the *ratios*
 * (`trailingPE`, `priceToSales`, `enterpriseToEbitda`, `enterpriseToRevenue`). EODHD's
 * `/fundamentals` answers with the underlying figures, so the same multiples can be computed from
 * reported values rather than taken on trust. Measured 2026-11-21 against the public demo token:
 *
 *   General.Code AAPL · MarketCapitalization 5074783305728 · PERatio 39.2371
 *   RevenueTTM 478833999872 · EBITDA 171486003200 · EnterpriseValue 5098172276220
 *   PriceSalesTTM 10.4844 · EnterpriseValueEbitda 29.9582
 *
 * Two spellings matter and were wrong in the first version: the ratio is `EnterpriseValueEbitda`
 * (camel), and `Highlights` carries **no** net-income field at all — its 25 keys were checked. Net
 * income comes from SEC EDGAR (`sec.ts`), which is the filing rather than a vendor's summary.
 *
 * Every field is `number | null` and nothing is defaulted to 0: a zero would publish a figure the
 * source never gave.
 *
 * Server-only. The key is read from `EODHD_API_KEY` (explicit override) or `EODHD_API_TOKEN`
 * (the estate's name); with
 * neither set this module reports "not configured" and the pages keep using Yahoo — it never falls
 * back to the demo token silently, because that token only answers for a few symbols and a partial
 * table would look complete.
 */

const BASE_URL = "https://eodhd.com/api";

/**
 * No module-level `AbortSignal.timeout()`: the signal starts its clock when it is *created*, so a
 * shared one aborts every request a few seconds after the process starts. `yahoo.ts` shipped that
 * defect once; the signal is built per call here for the same reason.
 */
const TIMEOUT_MS = 12_000;


/** Politeness cap: twenty symbols at once would be a burst the free tier counts. */
const CONCURRENCY = 4;

export interface Fundamentals {
  symbol: string;
  name: string | null;
  currency: string | null;
  marketCap: number | null;
  enterpriseValue: number | null;
  revenueTTM: number | null;
  ebitda: number | null;
  trailingPE: number | null;
  priceToSales: number | null;
  /** EODHD's own ratio when present, otherwise EV/EBITDA computed from the two figures it gave. */
  evToEbitda: number | null;
  sourceUrl: string;
  retrievedAt: string;
}

function num(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

/** `CRM` -> `CRM.US`. EODHD requires an exchange suffix; every watchlist symbol is a US listing. */
export function toEodhdSymbol(symbol: string): string {
  const upper = symbol.trim().toUpperCase();
  return upper.includes(".") ? upper : `${upper}.US`;
}

/**
 * The estate provides this credential as `EODHD_API_TOKEN` (measured 2026-11-21: present in the
 * workstation environment, 23 characters). The first version of this module read only
 * `EODHD_API_KEY`, so EODHD was silently unconfigured everywhere the estate had set it. Both names
 * are accepted, the estate's first.
 */
function apiKey(): string {
  // `EODHD_API_KEY` wins when both are set: an explicit override should not be shadowed by the
  // estate's ambient token. Otherwise the estate's `EODHD_API_TOKEN` is what this runs on.
  const token = process.env.EODHD_API_KEY?.trim() || process.env.EODHD_API_TOKEN?.trim();
  return token ?? "";
}

export function eodhdConfigured(): boolean {
  return apiKey().length > 0;
}

function mapFundamentals(symbol: string, payload: unknown, now: string): Fundamentals | null {
  if (typeof payload !== "object" || payload === null) return null;
  const body = payload as Record<string, unknown>;
  const general = (body.General ?? {}) as Record<string, unknown>;
  const highlights = (body.Highlights ?? {}) as Record<string, unknown>;
  const valuation = (body.Valuation ?? {}) as Record<string, unknown>;

  // A body with neither section is the "no data for this symbol" shape, not a company worth $0.
  if (Object.keys(general).length === 0 && Object.keys(highlights).length === 0) return null;

  const enterpriseValue = num(valuation.EnterpriseValue);
  const ebitda = num(highlights.EBITDA);
  const computed = enterpriseValue != null && ebitda != null && ebitda !== 0 ? enterpriseValue / ebitda : null;

  return {
    symbol,
    name: typeof general.Name === "string" ? general.Name : null,
    currency: typeof general.CurrencyCode === "string" ? general.CurrencyCode : null,
    marketCap: num(highlights.MarketCapitalization),
    enterpriseValue,
    revenueTTM: num(highlights.RevenueTTM),
    ebitda,
    trailingPE: num(valuation.TrailingPE) ?? num(highlights.PERatio),
    priceToSales: num(valuation.PriceSalesTTM),
    // `EnterpriseValueEbitda` is the field the API returns (measured: 29.9582). Reading only
    // `EnterpriseValueEBITDA` left this branch unreachable and published a computed 29.729 in its
    // place — a number that disagreed with the vendor while the page named the vendor.
    evToEbitda: num(valuation.EnterpriseValueEbitda) ?? computed,
    sourceUrl: `https://eodhd.com/financial-summary/${toEodhdSymbol(symbol)}`,
    retrievedAt: now,
  };
}

/** One symbol, or null when unconfigured, unreachable, or answered without data. */
export async function getFundamentals(symbol: string): Promise<Fundamentals | null> {
  if (!eodhdConfigured()) return null;
  const eodhdSymbol = toEodhdSymbol(symbol);
  const url = `${BASE_URL}/fundamentals/${encodeURIComponent(eodhdSymbol)}?api_token=${encodeURIComponent(
    apiKey(),
  )}&fmt=json`;
  try {
    // `no-store`, deliberately, and not `next: { revalidate }`: EODHD requires the token in the
    // query string, and Next's fetch cache persists the full URL (`CachedFetchData.url`) to
    // `.next/cache` and prints it from its own cache-write error path (`console.warn("Failed to set
    // fetch cache", input, …)`). The page's own ISR window already bounds how often this runs.
    const response = await fetch(url, {
      signal: AbortSignal.timeout(TIMEOUT_MS),
      cache: "no-store",
      headers: { accept: "application/json" },
    });
    if (!response.ok) return null;
    return mapFundamentals(symbol, await response.json(), new Date().toISOString());
  } catch {
    // A timeout, a refused connection or a 401 all mean "no figure from this source"; the caller
    // renders the Yahoo value or a dash rather than a substituted number.
    return null;
  }
}

/** Every symbol that answered, by ticker. Failures are absent, never filled in. */
export interface FundamentalBatch {
  fundamentals: Map<string, Fundamentals>;
  /** Symbols this source did not answer for — coverage limits, a revoked key, a timeout. */
  failed: string[];
}

/**
 * A page-level deadline. Six waves of four symbols at a 12 s per-call timeout is 60 s worst case,
 * and a per-call timeout does not bound the render — `yahoo.ts` records the same trap. Whatever has
 * arrived when this fires is returned and the rest are reported as failed, so the page states a
 * partial result instead of becoming an ALB idle timeout.
 */
const BATCH_DEADLINE_MS = 15_000;

export async function getFundamentalsMany(
  symbols: readonly string[],
  deadlineMs: number = BATCH_DEADLINE_MS,
): Promise<FundamentalBatch> {
  const out = new Map<string, Fundamentals>();
  if (!eodhdConfigured()) return { fundamentals: out, failed: [] };

  let index = 0;
  async function worker(): Promise<void> {
    while (index < symbols.length) {
      const symbol = symbols[index];
      index += 1;
      if (symbol === undefined) continue;
      const found = await getFundamentals(symbol);
      if (found) out.set(symbol, found);
    }
  }
  let timer: ReturnType<typeof setTimeout> | undefined;
  const deadline = new Promise<void>((resolve) => {
    timer = setTimeout(resolve, deadlineMs);
  });
  try {
    await Promise.race([Promise.all(Array.from({ length: Math.min(CONCURRENCY, symbols.length) }, worker)), deadline]);
  } finally {
    if (timer) clearTimeout(timer);
  }
  const failed = symbols.filter((symbol) => !out.has(symbol));
  if (failed.length > 0) {
    console.error(`eodhd: no fundamentals for ${failed.length}/${symbols.length} symbols (${failed.join(", ")})`);
  }
  return { fundamentals: out, failed };
}
