/**
 * US Treasury daily par yield curve — the source for `risk_free_rate`.
 *
 * The CAPM tools take `risk_free_rate` and the docs say "typically 10-year Treasury yield", but
 * nothing in the product fetched it: it was caller-supplied with a convention attached. This reads
 * the Treasury's own published curve, keyless, so the figure has a date and a URL behind it.
 *
 * Measured 2026-11-21: the CSV is newest-first, `Date,"1 Mo",…,"10 Yr",…`, and the 2026-11-20 row
 * reads `10 Yr = 4.92`.
 */

const CSV_URL = (year: number) =>
  `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/${year}/all` +
  `?type=daily_treasury_yield_curve&field_tdr_date_value=${year}&page&_format=csv`;

const TIMEOUT_MS = 12_000;
const REVALIDATE_S = 3600; // the curve is published once per business day

export interface TreasuryRate {
  /** Percent, as published — 4.92 means 4.92%, not 0.0492. */
  rate: number;
  tenor: string;
  /** The curve date, `YYYY-MM-DD`. */
  asOf: string;
  sourceUrl: string;
}

/**
 * Newest row of the CSV for one tenor. Exported so the parser can be tested without the network:
 * the file is quoted headers, `MM/DD/YYYY` dates, and a row per business day.
 */
export function parseYieldCurve(csv: string, tenor = "10 Yr"): { rate: number; asOf: string } | null {
  const lines = csv.trim().split(/\r?\n/);
  if (lines.length < 2) return null;
  const header = (lines[0] ?? "").split(",").map((h) => h.replace(/^"|"$/g, "").trim());
  const column = header.indexOf(tenor);
  if (column < 0) return null;

  // Take the greatest date, rather than trusting row order: the file is newest-first today
  // (measured: 2026 → 223 rows descending, 2025 → 249 rows), but an ascending or re-sorted file
  // would otherwise hand back the oldest row labelled as current.
  let best: { rate: number; asOf: string } | null = null;
  for (const line of lines.slice(1)) {
    const cells = line.split(",");
    const raw = cells[column]?.trim();
    if (!raw) continue;
    const rate = Number(raw);
    const [month, day, year] = (cells[0] ?? "").split("/");
    if (!Number.isFinite(rate) || !month || !day || !year) continue;
    const asOf = `${year}-${month.padStart(2, "0")}-${day.padStart(2, "0")}`;
    if (best === null || asOf > best.asOf) best = { rate, asOf };
  }
  return best;
}

/** The latest 10-year (or other tenor) par yield, or null when Treasury does not answer. */
export async function getRiskFreeRate(tenor = "10 Yr"): Promise<TreasuryRate | null> {
  // On 1–2 January the current year's file exists and is empty (measured 2026-11-21: the 2027 file
  // returns 200 with 0 bytes while 2025 has 249 rows), so fall back one year rather than reporting
  // no rate at the turn of the year.
  for (const year of [new Date().getUTCFullYear(), new Date().getUTCFullYear() - 1]) {
    const found = await fetchCurve(year, tenor);
    if (found) return found;
  }
  return null;
}

async function fetchCurve(year: number, tenor: string): Promise<TreasuryRate | null> {
  try {
    const response = await fetch(CSV_URL(year), {
      signal: AbortSignal.timeout(TIMEOUT_MS),
      next: { revalidate: REVALIDATE_S },
      // No custom `user-agent`. Measured 2026-11-21: sending one makes home.treasury.gov hold the
      // connection until the timeout (18,173 bytes never arrive), while the default header returns
      // 200. `curl` with the same string succeeds, so it is a request-fingerprint rule, not the
      // header syntax.
      headers: { accept: "text/csv" },
    });
    if (!response.ok) return null;
    const parsed = parseYieldCurve(await response.text(), tenor);
    if (!parsed) return null;
    return { ...parsed, tenor, sourceUrl: "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve" };
  } catch {
    return null;
  }
}
