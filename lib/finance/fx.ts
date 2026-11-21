/**
 * FX spot rates from Frankfurter, which republishes the ECB reference rates — keyless.
 *
 * This fills `spot_rate`, the first argument of `valuation_international` method `ppp`
 * (Eₜ = E₀ × (1+π_foreign)/(1+π_domestic)). Nothing in the product fetched an exchange rate; a
 * caller had to bring one, and there is no honest way to type it from memory.
 *
 * Measured 2026-11-21: `https://api.frankfurter.dev/v1/latest?base=USD&symbols=HKD` →
 * `{"amount":1.0,"base":"USD","date":"2026-11-20","rates":{"HKD":7.8389}}`. ECB publishes on
 * business days, so the date is the last publication, not necessarily today.
 */

const BASE_URL = "https://api.frankfurter.dev/v1/latest";
const TIMEOUT_MS = 12_000;
const REVALIDATE_S = 3600; // ECB publishes once per business day

export interface SpotRate {
  base: string;
  quote: string;
  rate: number;
  /** The ECB reference date, `YYYY-MM-DD`. */
  asOf: string;
  sourceUrl: string;
}

/** Pull one pair out of a Frankfurter body. Exported so the shape is tested without the network. */
export function parseFrankfurter(body: unknown, base: string, quote: string): { rate: number; asOf: string } | null {
  if (typeof body !== "object" || body === null) return null;
  const payload = body as { rates?: Record<string, unknown>; date?: unknown; base?: unknown };
  if (typeof payload.base === "string" && payload.base.toUpperCase() !== base.toUpperCase()) return null;
  const rate = payload.rates?.[quote.toUpperCase()];
  if (typeof rate !== "number" || !Number.isFinite(rate)) return null;
  if (typeof payload.date !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(payload.date)) return null;
  return { rate, asOf: payload.date };
}

export async function getSpotRate(base: string, quote: string): Promise<SpotRate | null> {
  const from = base.trim().toUpperCase();
  const to = quote.trim().toUpperCase();
  if (from === to) return null; // a same-currency "rate" of 1 is arithmetic, not a quote
  try {
    const response = await fetch(`${BASE_URL}?base=${encodeURIComponent(from)}&symbols=${encodeURIComponent(to)}`, {
      signal: AbortSignal.timeout(TIMEOUT_MS),
      next: { revalidate: REVALIDATE_S },
      headers: { accept: "application/json" },
    });
    if (!response.ok) return null;
    const parsed = parseFrankfurter(await response.json(), from, to);
    if (!parsed) return null;
    return {
      base: from,
      quote: to,
      rate: parsed.rate,
      asOf: parsed.asOf,
      sourceUrl: `https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html`,
    };
  } catch {
    return null;
  }
}
