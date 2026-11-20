/**
 * The ticker list the public pages show.
 *
 * This is **configuration**, not data: it names which companies to ask Yahoo about. Every number on
 * the page comes from the Yahoo response at request time, and a symbol that cannot be resolved is
 * reported as missing rather than substituted. Adding a symbol here does not add a figure.
 *
 * Grouped by the textbook's industry verticals (`lib/landing.ts`), so the page lines up with the
 * methods the product advertises rather than with an arbitrary list.
 */
export const WATCHLIST: Readonly<Record<string, readonly string[]>> = {
  SaaS: ["CRM", "NOW", "ADBE", "HUBS"],
  Biotech: ["AMGN", "GILD", "VRTX", "REGN"],
  // Fiserv trades under `FI` (renamed from `FISV` in 2023), but Yahoo answers `FI` with a shell:
  // `summaryDetail` and `price` both come back with no `regularMarketPrice`, no `marketCap` and
  // `currency: null` — measured 2026-11-20 — so the Fintech median published over three companies
  // and said so. `FISV` still resolves to the same company with a live price. The payload decided
  // this, not the count: `FI` is asked for, returns nothing, and `FISV` returns Fiserv.
  Fintech: ["V", "MA", "PYPL", "FISV"],
  Marketplace: ["ABNB", "UBER", "ETSY", "MELI"],
  Hardware: ["AAPL", "DELL", "HPQ", "CSCO"],
} as const;

export const ALL_SYMBOLS: readonly string[] = Object.values(WATCHLIST).flat();
