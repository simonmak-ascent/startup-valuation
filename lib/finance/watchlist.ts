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
  Fintech: ["V", "MA", "PYPL", "FI"],
  Marketplace: ["ABNB", "UBER", "ETSY", "MELI"],
  Hardware: ["AAPL", "DELL", "HPQ", "CSCO"],
} as const;

export const ALL_SYMBOLS: readonly string[] = Object.values(WATCHLIST).flat();
