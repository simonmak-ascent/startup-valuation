/**
 * SEC EDGAR XBRL company facts — the primary filing, for `net_income`.
 *
 * EODHD withholds net income (its `Highlights` has 25 keys and none is net income), and Yahoo's
 * quote carries only the resulting ratio, so `pe_ratio(market_cap, net_income)` had no source for
 * its second argument. EDGAR is the filing itself, keyless, and authoritative in a way no vendor is.
 *
 * Three things were measured against the live endpoint on 2026-11-21 and each changed the code:
 *
 * 1. **`NetIncomeLoss` is not a tag every filer keeps using.** Mastercard (a watchlist symbol)
 *    stopped at `2013-12-31, 3 116 000 000` under that tag while `ProfitLoss` reports
 *    `2025-12-31, 14 968 000 000`. So the concept is tried in a chain, newest figure wins, and a
 *    result older than two years is returned with `stale: true` rather than silently as current.
 * 2. **A 10-K also carries quarter-length facts.** MA and CAT each have a 91-day `10-K`/`FY` point
 *    sharing the annual `end`, so selection by `end` alone was decided by array order. The period
 *    length — 300 to 400 days — is what makes a point annual.
 * 3. **`fy` is the filing's fiscal-year focus, not the period's.** CRM's FY2026 10-K tags the
 *    period ending `2026-01-31` with `fy: 2025`, so the label is derived from `end`.
 *
 * SEC asks for a `User-Agent` identifying the caller with contact details and for no more than ten
 * requests per second; the constant below and the two-at-a-time limiter honour both.
 */

const UA = "startup-valuation (https://startup-valuation.ascent-partners.com; ops@ascent-partners.com)";
const TIMEOUT_MS = 15_000;

/** Tried in order; the newest `asOf` across all of them wins. */
const CONCEPTS = ["NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic", "ProfitLoss"] as const;

/** A figure older than this is still returned, but flagged: it is not the current year's income. */
const RECENT_DAYS = 730;

/** Annual means a year, not a quarter that happens to sit in a 10-K. */
const MIN_ANNUAL_DAYS = 300;
const MAX_ANNUAL_DAYS = 400;

export interface AnnualNetIncome {
  ticker: string;
  cik: number;
  /** USD, as filed. */
  value: number;
  /** Derived from the period end, not from the filing's `fy` focus. */
  fiscalYear: number;
  /** Period end, `YYYY-MM-DD`. */
  asOf: string;
  form: string;
  /** Which XBRL concept this came from, so a reader can tell why MA differs from AAPL. */
  concept: string;
  /** True when the newest filed figure is more than two years old. */
  stale: boolean;
  sourceUrl: string;
}

function daysBetween(start: unknown, end: unknown): number | null {
  if (typeof start !== "string" || typeof end !== "string") return null;
  const from = Date.parse(start);
  const to = Date.parse(end);
  if (!Number.isFinite(from) || !Number.isFinite(to)) return null;
  return (to - from) / 86_400_000;
}

/** The newest annual point in one companyconcept body, or null. Exported for testing. */
export function parseAnnualNetIncome(
  body: unknown,
  ticker: string,
  cik: number,
  concept: string = "NetIncomeLoss",
): AnnualNetIncome | null {
  if (typeof body !== "object" || body === null) return null;
  const units = (body as { units?: Record<string, unknown> }).units;
  const usd = units?.USD;
  if (!Array.isArray(usd)) return null;

  const annual = usd
    .filter((p): p is Record<string, unknown> => typeof p === "object" && p !== null)
    .filter((p) => p.form === "10-K" && p.fp === "FY")
    .filter((p) => typeof p.val === "number" && Number.isFinite(p.val))
    .filter((p) => typeof p.end === "string" && /^\d{4}-\d{2}-\d{2}$/.test(p.end))
    // The period decides what is annual; sorting on `end` alone left it to array order.
    .filter((p) => {
      const days = daysBetween(p.start, p.end);
      return days !== null && days >= MIN_ANNUAL_DAYS && days <= MAX_ANNUAL_DAYS;
    })
    .sort((a, b) => String(b.end).localeCompare(String(a.end)));

  const latest = annual[0];
  if (!latest) return null;

  const end = String(latest.end);
  const ageDays = (Date.now() - Date.parse(end)) / 86_400_000;
  return {
    ticker: ticker.toUpperCase(),
    cik,
    value: latest.val as number,
    fiscalYear: Number(end.slice(0, 4)),
    asOf: end,
    form: "10-K",
    concept,
    stale: Number.isFinite(ageDays) && ageDays > RECENT_DAYS,
    sourceUrl: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=${cik}&type=10-K`,
  };
}

/**
 * Ticker → CIK from EDGAR's own map.
 *
 * The *promise* is cached, not just the result: without that, N concurrent cold requests each
 * download the ~800 KB file and the caller chooses N. A failure is remembered for a minute so a
 * throttled EDGAR is not hammered by a retry storm — which is exactly the state it enters when it
 * starts refusing this caller.
 */
const CIK_FAILURE_TTL_MS = 60_000;
let cikPromise: Promise<Map<string, number> | null> | null = null;
let cikFailedAt = 0;

async function loadCikMap(): Promise<Map<string, number> | null> {
  try {
    const response = await fetch("https://www.sec.gov/files/company_tickers.json", {
      signal: AbortSignal.timeout(TIMEOUT_MS),
      next: { revalidate: 86_400 },
      headers: { accept: "application/json", "user-agent": UA },
    });
    if (!response.ok) return null;
    const body = (await response.json()) as Record<string, { cik_str?: unknown; ticker?: unknown }>;
    const map = new Map<string, number>();
    for (const row of Object.values(body)) {
      const symbol = typeof row.ticker === "string" ? row.ticker.toUpperCase() : null;
      const cik = typeof row.cik_str === "number" ? row.cik_str : null;
      if (symbol && cik) map.set(symbol, cik);
    }
    return map;
  } catch {
    return null;
  }
}

async function getCik(ticker: string): Promise<number | null> {
  if (cikPromise === null) {
    if (cikFailedAt !== 0 && Date.now() - cikFailedAt < CIK_FAILURE_TTL_MS) return null;
    cikPromise = loadCikMap();
  }
  const map = await cikPromise;
  if (map === null) {
    if (Date.now() - cikFailedAt > CIK_FAILURE_TTL_MS) {
      cikPromise = null;
      cikFailedAt = Date.now();
    }
    return null;
  }
  return map.get(ticker.toUpperCase()) ?? null;
}

/** EDGAR asks for no more than ten requests per second and blocks the source that ignores it. */
const MAX_CONCURRENT = 2;
let active = 0;
const waiters: Array<() => void> = [];

async function limited<T>(work: () => Promise<T>): Promise<T> {
  // Re-check in a loop: a waiter resumes on a microtask after `active` was decremented, and a fresh
  // caller can take that slot in between — which made "two at a time" three at a time.
  while (active >= MAX_CONCURRENT) await new Promise<void>((resolve) => waiters.push(resolve));
  active += 1;
  try {
    return await work();
  } finally {
    active -= 1;
    waiters.shift()?.();
  }
}

/** Results, per ticker, for an hour; a null for five minutes, so a transient failure does not stick. */
const RESULT_TTL_MS = 3_600_000;
const NULL_TTL_MS = 300_000;
/** A caller names this key on a public route; without a bound it is caller-driven allocation. */
const MAX_CACHED_TICKERS = 2_000;
const results = new Map<string, { at: number; value: AnnualNetIncome | null }>();
const inflight = new Map<string, Promise<AnnualNetIncome | null>>();

async function fetchConcept(paddedCik: string, concept: string): Promise<unknown | null> {
  return limited(async () => {
    try {
      const response = await fetch(
        `https://data.sec.gov/api/xbrl/companyconcept/CIK${paddedCik}/us-gaap/${concept}.json`,
        {
          signal: AbortSignal.timeout(TIMEOUT_MS),
          next: { revalidate: 3_600 },
          headers: { accept: "application/json", "user-agent": UA },
        },
      );
      if (!response.ok) return null;
      return await response.json();
    } catch {
      return null;
    }
  });
}

/**
 * Newest annual net income across the concept chain.
 *
 * Every concept is asked and the newest point wins. There is deliberately no early stop: `stale` is
 * a two-year window, so "not stale" cannot establish that a later concept holds no newer year — a
 * filer that switched tags eighteen months ago would otherwise publish last year's figure labelled
 * current. Three cached requests per ticker per hour is the cheaper error, and the limiter bounds it.
 */
async function resolveNetIncome(ticker: string, cik: number): Promise<AnnualNetIncome | null> {
  const padded = String(cik).padStart(10, "0");
  let best: AnnualNetIncome | null = null;
  for (const concept of CONCEPTS) {
    const body = await fetchConcept(padded, concept);
    if (body === null) continue;
    const parsed = parseAnnualNetIncome(body, ticker, cik, concept);
    if (parsed && (best === null || parsed.asOf > best.asOf)) best = parsed;
  }
  return best;
}

export async function getAnnualNetIncome(ticker: string): Promise<AnnualNetIncome | null> {
  const key = ticker.trim().toUpperCase();
  const cached = results.get(key);
  const ttl = cached?.value === null ? NULL_TTL_MS : RESULT_TTL_MS;
  if (cached && Date.now() - cached.at < ttl) return cached.value;

  const running = inflight.get(key);
  if (running) return running;

  const work = (async (): Promise<AnnualNetIncome | null> => {
    const cik = await getCik(key);
    if (cik == null) return null;
    return resolveNetIncome(key, cik);
  })();

  inflight.set(key, work);
  try {
    const value = await work;
    if (!results.has(key) && results.size >= MAX_CACHED_TICKERS) {
      const oldest = results.keys().next();
      if (!oldest.done) results.delete(oldest.value);
    }
    results.set(key, { at: Date.now(), value });
    return value;
  } finally {
    inflight.delete(key);
  }
}
