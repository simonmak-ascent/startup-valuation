import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

/**
 * The module that had the defect this file exists for: a timeout created once at module load would
 * have aborted every request ~6 s after the process started, and the pages would have rendered their
 * empty state for ever while `/api/health` stayed green. These tests drive the mapping and the
 * failure partition without touching the network.
 */
const quoteSummary = vi.fn();
const constructorOptions = vi.fn();

vi.mock("yahoo-finance2", () => ({
  default: class {
    quoteSummary = quoteSummary;
    constructor(options: unknown) {
      constructorOptions(options);
    }
  },
}));

const { getQuote, getQuotes } = await import("@/lib/finance/yahoo");

type Module = Record<string, unknown>;
interface Payload {
  summaryDetail: Module;
  defaultKeyStatistics: Module;
  financialData: Module;
  price: Module;
}

function summary(overrides: Module = {}): Payload {
  return {
    summaryDetail: {
      marketCap: 5_114_019_971_072,
      trailingPE: 39.19,
      priceToSalesTrailing12Months: 10.68,
      fiftyTwoWeekLow: 200,
      fiftyTwoWeekHigh: 400,
      currency: "USD",
      exchangeName: "NasdaqGS",
      ...overrides,
    },
    defaultKeyStatistics: { enterpriseToEbitda: 30.04, enterpriseToRevenue: 10.76 },
    financialData: { currentPrice: 300 },
    price: { marketCap: 5_114_019_971_072, currency: "USD", exchangeName: "NasdaqGS" },
  };
}

beforeEach(() => {
  quoteSummary.mockReset();
});

describe("getQuote", () => {
  it("maps the vendor's figures without inventing any", async () => {
    quoteSummary.mockResolvedValue(summary());
    const q = await getQuote("AAPL");
    expect(q.symbol).toBe("AAPL");
    expect(q.price).toBe(300);
    expect(q.marketCap).toBe(5_114_019_971_072);
    expect(q.trailingPE).toBe(39.19);
    expect(q.evToEbitda).toBe(30.04);
    expect(q.currency).toBe("USD");
    expect(q.live).toBe(true);
    // 300 within a 200–400 range is exactly the midpoint.
    expect(q.week52Position).toBeCloseTo(0.5, 5);
    expect(q.sourceUrl).toContain("AAPL");
  });

  it("keeps a missing metric null rather than defaulting it to zero", async () => {
    quoteSummary.mockResolvedValue(
      summary({ trailingPE: undefined, priceToSalesTrailing12Months: undefined }),
    );
    const q = await getQuote("PRIVATE");
    expect(q.trailingPE).toBeNull();
    expect(q.priceToSales).toBeNull();
    expect(q.marketCap).not.toBeNull();
  });

  it("marks a previous close as not live", async () => {
    const payload = summary({ previousClose: 295 });
    payload.financialData = {};
    payload.price = { marketCap: 1, currency: "USD", exchangeName: "NYSE" };
    quoteSummary.mockResolvedValue(payload);
    const q = await getQuote("OLD");
    // The vendor figure is real, but it is a close — the table labels it "(prev close)".
    expect(q.price).toBe(295);
    expect(q.live).toBe(false);
  });

  it("throws when the vendor returns no price at all", async () => {
    const payload = summary();
    payload.financialData = {};
    payload.price = { currency: "USD" };
    quoteSummary.mockResolvedValue(payload);
    await expect(getQuote("GONE")).rejects.toThrow(/no price/i);
  });
});

describe("getQuotes", () => {
  it("returns the quotes that resolved and names the symbols that did not", async () => {
    quoteSummary.mockImplementation(async (symbol: string) => {
      if (symbol === "BAD") throw new Error("delisted");
      return summary();
    });
    const { quotes, failed } = await getQuotes(["AAPL", "BAD", "MSFT"]);
    expect(quotes.map((q) => q.symbol).sort()).toEqual(["AAPL", "MSFT"]);
    expect(failed).toEqual(["BAD"]);
  });

  it("returns what resolved at the deadline and names the rest", async () => {
    // Without the race in `getQuotes`, this test hangs (or the page hangs in production) until the
    // ALB idle timeout: the per-call signal does not bound a page whose calls are queued.
    vi.useFakeTimers();
    try {
      quoteSummary.mockImplementation((symbol: string) =>
        symbol === "SLOW" ? new Promise(() => {}) : Promise.resolve(summary()),
      );
      // A flag set by the promise itself. A race against an already-resolved arm cannot see an
      // early settle: that arm's reaction is queued ahead of `pending`'s continuation, so the race
      // reports "pending" even when the deadline has already fired — the guard would have passed
      // with any budget at all, including one that aborts healthy callers.
      let settled = false;
      const pending = getQuotes(["AAPL", "SLOW"]).finally(() => {
        settled = true;
      });
      await vi.advanceTimersByTimeAsync(29_000);
      expect(settled).toBe(false);
      await vi.advanceTimersByTimeAsync(1_000);
      const { quotes, failed } = await pending;
      expect(quotes.map((q) => q.symbol)).toEqual(["AAPL"]);
      expect(failed).toEqual(["SLOW"]);
    } finally {
      vi.useRealTimers();
    }
  });

  it("does not throw when every symbol fails — the page must still render", async () => {
    quoteSummary.mockRejectedValue(new Error("upstream down"));
    const { quotes, failed } = await getQuotes(["A", "B"]);
    expect(quotes).toEqual([]);
    expect(failed).toEqual(["A", "B"]);
  });
});

describe("the abort signal", () => {
  it("is created per call, never once when the client is constructed", async () => {
    quoteSummary.mockResolvedValue(summary());
    await getQuote("AAPL");
    await getQuote("MSFT");

    // A signal in the constructor's `fetchOptions` is reused for every request and expires ~20 s
    // after module load: the pages would then fail for ever while health stayed green. This asserts
    // the absence of that signal and the presence of a *fresh* one per call — the defect this file
    // exists for is invisible to a mock that ignores its arguments.
    const options = (constructorOptions.mock.calls[0]?.[0] ?? {}) as {
      fetchOptions?: { signal?: unknown };
    };
    expect(options.fetchOptions?.signal).toBeUndefined();

    const signals = quoteSummary.mock.calls.map(
      (call) => (call[2] as { fetchOptions?: { signal?: unknown } } | undefined)?.fetchOptions?.signal,
    );
    expect(signals).toHaveLength(2);
    expect(signals[0]).toBeInstanceOf(AbortSignal);
    expect(signals[1]).toBeInstanceOf(AbortSignal);
    expect(signals[0]).not.toBe(signals[1]);
  });
});
