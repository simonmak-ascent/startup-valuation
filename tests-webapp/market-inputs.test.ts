import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { parseYieldCurve } from "@/lib/finance/treasury";
import { parseFrankfurter } from "@/lib/finance/fx";
import { parseAnnualNetIncome } from "@/lib/finance/sec";

/**
 * The three parsers behind the market inputs. Each fixture is the shape the source actually
 * returned on 2026-11-21 — the Treasury CSV header, the Frankfurter body, and the EDGAR
 * companyconcept body — trimmed to the fields that matter.
 */

const TREASURY_CSV = [
  'Date,"1 Mo","1.5 Month","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"',
  "11/20/2026,4.19,4.26,4.28,4.32,4.32,4.38,4.51,4.63,4.65,4.71,4.80,4.92,5.34,5.31",
  "11/19/2026,4.20,4.27,4.29,4.34,4.35,4.42,4.62,4.76,4.81,4.86,4.94,5.04,5.43,5.40",
].join("\n");

describe("treasury yield curve", () => {
  it("takes the newest row for the requested tenor", () => {
    expect(parseYieldCurve(TREASURY_CSV, "10 Yr")).toEqual({ rate: 4.92, asOf: "2026-11-20" });
  });

  it("reads a different tenor from the same file", () => {
    expect(parseYieldCurve(TREASURY_CSV, "2 Yr")).toEqual({ rate: 4.63, asOf: "2026-11-20" });
  });

  it("returns null for a tenor the file does not carry, rather than a nearby one", () => {
    expect(parseYieldCurve(TREASURY_CSV, "15 Yr")).toBeNull();
  });

  it("returns null on an empty or header-only body", () => {
    expect(parseYieldCurve("")).toBeNull();
    expect(parseYieldCurve('Date,"10 Yr"')).toBeNull();
  });

  it("skips a row whose cell is blank and takes the next complete one", () => {
    const csv = [
      'Date,"10 Yr"',
      "11/20/2026,",
      "11/19/2026,5.04",
    ].join("\n");
    expect(parseYieldCurve(csv, "10 Yr")).toEqual({ rate: 5.04, asOf: "2026-11-19" });
  });
});

describe("Frankfurter / ECB", () => {
  const BODY = { amount: 1.0, base: "USD", date: "2026-11-20", rates: { HKD: 7.8389, CNY: 6.6777 } };

  it("pulls the requested pair and its publication date", () => {
    expect(parseFrankfurter(BODY, "USD", "HKD")).toEqual({ rate: 7.8389, asOf: "2026-11-20" });
  });

  it("refuses a body whose base is a different currency", () => {
    expect(parseFrankfurter(BODY, "EUR", "HKD")).toBeNull();
  });

  it("returns null when the pair is absent", () => {
    expect(parseFrankfurter(BODY, "USD", "JPY")).toBeNull();
  });

  it("returns null when the date is not an ISO day", () => {
    expect(parseFrankfurter({ ...BODY, date: "yesterday" }, "USD", "HKD")).toBeNull();
  });
});

describe("SEC annual net income", () => {
  const BODY = {
    cik: 320193,
    entityName: "Apple Inc.",
    units: {
      USD: [
        { start: "2026-03-29", end: "2026-06-27", val: 29_789_000_000, form: "10-Q", fy: 2026, fp: "Q3" },
        { start: "2025-09-28", end: "2026-09-26", val: 132_175_000_000, form: "10-K", fy: 2026, fp: "FY" },
        { start: "2024-09-29", end: "2025-09-27", val: 96_995_000_000, form: "10-K", fy: 2025, fp: "FY" },
      ],
    },
  };

  it("takes the latest fiscal year, not the latest quarter", () => {
    const out = parseAnnualNetIncome(BODY, "aapl", 320193);
    expect(out?.value).toBe(132_175_000_000);
    expect(out?.fiscalYear).toBe(2026);
    expect(out?.asOf).toBe("2026-09-26");
    expect(out?.ticker).toBe("AAPL");
    expect(out?.form).toBe("10-K");
  });

  it("returns null rather than a quarterly figure when no annual point exists", () => {
    const quarterlyOnly = { units: { USD: [{ end: "2026-06-27", val: 1, form: "10-Q", fy: 2026, fp: "Q3" }] } };
    expect(parseAnnualNetIncome(quarterlyOnly, "X", 1)).toBeNull();
  });

  it("returns null when the units are not USD", () => {
    expect(parseAnnualNetIncome({ units: { shares: [{ end: "2026-09-26", val: 1, form: "10-K", fp: "FY" }] } }, "X", 1)).toBeNull();
  });

  it("returns null on a body with no units at all", () => {
    expect(parseAnnualNetIncome({}, "X", 1)).toBeNull();
  });
});

describe("SEC request bound", () => {
  // The CIK map and the result memo are module-level state, so each test needs its own instance —
  // without this the second test inherits the first one's cache and proves nothing.
  beforeEach(() => {
    vi.resetModules();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  function countingFetch() {
    const calls: string[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        calls.push(url);
        if (url.includes("company_tickers")) {
          return new Response(JSON.stringify({ "0": { cik_str: 320193, ticker: "AAPL", title: "Apple Inc." } }), { status: 200 });
        }
        return new Response(
          JSON.stringify({
            units: {
              USD: [
                { start: "2025-09-28", end: "2026-09-26", val: 132_175_000_000, form: "10-K", fy: 2026, fp: "FY" },
              ],
            },
          }),
          { status: 200 },
        );
      }),
    );
    return calls;
  }

  it("serves a repeat request from memory instead of EDGAR", async () => {
    const calls = countingFetch();
    const { getAnnualNetIncome } = await import("@/lib/finance/sec");
    const first = await getAnnualNetIncome("AAPL");
    // The concept chain asks every tag once (no early stop), so one call is three requests.
    const conceptsAfterFirst = calls.filter((u) => u.includes("companyconcept")).length;
    expect(conceptsAfterFirst).toBe(3);
    const second = await getAnnualNetIncome("AAPL");
    expect(second?.value).toBe(first?.value);
    // …and the second call costs nothing at all.
    expect(calls.filter((u) => u.includes("companyconcept"))).toHaveLength(conceptsAfterFirst);
    expect(calls.filter((u) => u.includes("company_tickers"))).toHaveLength(1);
  });

  it("collapses concurrent requests for the same ticker into one fetch", async () => {
    const calls = countingFetch();
    const { getAnnualNetIncome } = await import("@/lib/finance/sec");
    // AAPL is in the fixture map, so without in-flight dedupe each of the three issues its own
    // companyconcept request (measured: 3); with it, one.
    await Promise.all([getAnnualNetIncome("AAPL"), getAnnualNetIncome("AAPL"), getAnnualNetIncome("AAPL")]);
    // Three concurrent callers collapse into ONE chain: 3 concept requests, not 9.
    expect(calls.filter((u) => u.includes("companyconcept"))).toHaveLength(3);
  });
});

describe("SEC selection rules", () => {
  const annual = (end: string, start: string, val: number, form = "10-K", fp = "FY") => ({
    start,
    end,
    val,
    form,
    fy: Number(end.slice(0, 4)),
    fp,
  });

  it("rejects a quarter-length fact that shares the annual end date", () => {
    // Measured on MA and CAT: a 91-day 10-K/FY point sits at the same `end` as the annual one.
    const body = { units: { USD: [annual("2025-12-31", "2025-10-01", 968), annual("2025-12-31", "2025-01-01", 2700)] } };
    expect(parseAnnualNetIncome(body, "CAT", 1)?.value).toBe(2700);
  });

  it("derives the fiscal year from the period end, not the filing's fy focus", () => {
    // CRM's FY2026 10-K tags the period ending 2026-01-31 with fy 2025.
    const body = { units: { USD: [{ ...annual("2026-01-31", "2025-02-01", 100), fy: 2025 }] } };
    expect(parseAnnualNetIncome(body, "CRM", 1)?.fiscalYear).toBe(2026);
  });

  it("flags a figure older than two years rather than presenting it as current", () => {
    const body = { units: { USD: [annual("2013-12-31", "2013-01-01", 3_116_000_000)] } };
    const out = parseAnnualNetIncome(body, "MA", 1, "NetIncomeLoss");
    expect(out?.value).toBe(3_116_000_000);
    expect(out?.stale).toBe(true);
    expect(out?.concept).toBe("NetIncomeLoss");
  });

  it("takes the newest date, whatever order the file arrives in", () => {
    const ascending = ['Date,"10 Yr"', "11/19/2026,5.04", "11/20/2026,4.92"].join("\n");
    expect(parseYieldCurve(ascending, "10 Yr")).toEqual({ rate: 4.92, asOf: "2026-11-20" });
  });
});

describe("SEC concept chain", () => {
  beforeEach(() => vi.resetModules());
  afterEach(() => vi.unstubAllGlobals());

  it("falls through to ProfitLoss when NetIncomeLoss stopped years ago", async () => {
    // MA's real shape: NetIncomeLoss ends 2013, ProfitLoss reports 2025.
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("company_tickers")) {
          return new Response(JSON.stringify({ "0": { cik_str: 1141391, ticker: "MA", title: "Mastercard" } }), { status: 200 });
        }
        const stale = {
          units: { USD: [{ start: "2013-01-01", end: "2013-12-31", val: 3_116_000_000, form: "10-K", fp: "FY", fy: 2013 }] },
        };
        const current = {
          units: { USD: [{ start: "2025-01-01", end: "2025-12-31", val: 14_968_000_000, form: "10-K", fp: "FY", fy: 2025 }] },
        };
        return new Response(JSON.stringify(url.includes("ProfitLoss") ? current : stale), { status: 200 });
      }),
    );
    const { getAnnualNetIncome } = await import("@/lib/finance/sec");
    const out = await getAnnualNetIncome("MA");
    expect(out?.value).toBe(14_968_000_000);
    expect(out?.concept).toBe("ProfitLoss");
    expect(out?.stale).toBe(false);
  });
});

describe("the early stop that was removed", () => {
  beforeEach(() => vi.resetModules());
  afterEach(() => vi.unstubAllGlobals());

  it("does not publish a recent-but-superseded year when a later concept is newer", async () => {
    // The reviewer's scenario: NetIncomeLoss ends 2025-06-30 (inside the two-year window, so it is
    // NOT stale) while ProfitLoss ends 2026-06-30. An early stop would return 2025 and call it current.
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        if (url.includes("company_tickers")) {
          return new Response(JSON.stringify({ "0": { cik_str: 1, ticker: "SW", title: "Switched" } }), { status: 200 });
        }
        const nineMonthsAgo = {
          units: { USD: [{ start: "2024-07-01", end: "2025-06-30", val: 100, form: "10-K", fp: "FY", fy: 2025 }] },
        };
        const current = {
          units: { USD: [{ start: "2025-07-01", end: "2026-06-30", val: 250, form: "10-K", fp: "FY", fy: 2026 }] },
        };
        return new Response(JSON.stringify(url.includes("ProfitLoss") ? current : nineMonthsAgo), { status: 200 });
      }),
    );
    const { getAnnualNetIncome } = await import("@/lib/finance/sec");
    const out = await getAnnualNetIncome("SW");
    expect(out?.asOf).toBe("2026-06-30");
    expect(out?.value).toBe(250);
  });
});

describe("the /api/inputs symbol guard", () => {
  beforeEach(() => vi.resetModules());
  afterEach(() => vi.unstubAllGlobals());

  function stubSources() {
    const calls: string[] = [];
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
        const url = String(input);
        calls.push(url);
        if (url.includes("treasury.gov")) return new Response('Date,"10 Yr"\n11/20/2026,4.92', { status: 200 });
        if (url.includes("frankfurter")) {
          return new Response(JSON.stringify({ base: "USD", date: "2026-11-20", rates: { HKD: 7.8389 } }), { status: 200 });
        }
        return new Response("{}", { status: 200 });
      }),
    );
    return calls;
  }

  it("treats a non-ticker symbol as absent and never reaches EDGAR", async () => {
    const calls = stubSources();
    const { GET } = await import("@/app/(en)/api/inputs/route");
    const response = await GET(new Request(`https://x/api/inputs?symbol=${"A".repeat(6000)}`));
    const body = (await response.json()) as { net_income: unknown };
    expect(body.net_income).toBeNull();
    expect(calls.some((url) => url.includes("sec.gov"))).toBe(false);
  });

  it("accepts a real ticker", async () => {
    const calls = stubSources();
    const { GET } = await import("@/app/(en)/api/inputs/route");
    const response = await GET(new Request("https://x/api/inputs?symbol=BRK.B"));
    expect(response.status).toBe(200);
    // A valid ticker does reach EDGAR's ticker map.
    expect(calls.some((url) => url.includes("sec.gov"))).toBe(true);
  });
});
