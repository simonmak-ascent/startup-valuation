import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { eodhdConfigured, getFundamentals, getFundamentalsMany, toEodhdSymbol } from "@/lib/finance/eodhd";

/**
 * EODHD is the second market-data source. The figures below are the shape the public demo token
 * returned on 2026-11-21 — including the two nulls it withholds (`NetIncomeTTM`,
 * `EnterpriseValueEBITDA`), which are the reason nothing here defaults to 0.
 */
const DEMO_BODY = {
  General: { Code: "AAPL", Name: "Apple Inc.", CurrencyCode: "USD", Sector: "Technology" },
  Highlights: {
    // 25 keys, measured; `NetIncomeTTM` is not one of them. Net income comes from SEC EDGAR.
    MarketCapitalization: 5074783305728,
    PERatio: 39.2371,
    RevenueTTM: 478833999872,
    EBITDA: 171486003200,
  },
  Valuation: {
    EnterpriseValue: 5098172276220,
    // The field the API returns, measured 2026-11-21: `EnterpriseValueEbitda` 29.9582. There is no
    // `EnterpriseValueEBITDA` key; reading that spelling made the "source ratio" branch dead.
    EnterpriseValueEbitda: 29.9582,
    PriceSalesTTM: 10.4844,
    TrailingPE: 39.2371,
  },
};

function mockFetch(handler: (url: string) => Response | Promise<Response>) {
  const fn = vi.fn(async (input: RequestInfo | URL) => handler(String(input)));
  vi.stubGlobal("fetch", fn);
  return fn;
}

beforeEach(() => {
  delete process.env.EODHD_API_KEY;
  delete process.env.EODHD_API_TOKEN;
});

afterEach(() => {
  vi.unstubAllGlobals();
  delete process.env.EODHD_API_KEY;
  delete process.env.EODHD_API_TOKEN;
});

describe("credential resolution", () => {
  it("accepts the estate's EODHD_API_TOKEN, not only EODHD_API_KEY", async () => {
    process.env.EODHD_API_TOKEN = "estate-token";
    mockFetch(() => new Response(JSON.stringify(DEMO_BODY), { status: 200 }));
    expect(eodhdConfigured()).toBe(true);
    expect(await getFundamentals("AAPL")).not.toBeNull();
  });

  it("uses the explicit EODHD_API_KEY when both are set", async () => {
    // The first version asserted only that configuration was true, which held whichever name won —
    // it could not fail. What matters is which token goes on the wire.
    process.env.EODHD_API_KEY = "explicit";
    process.env.EODHD_API_TOKEN = "estate";
    let seen = "";
    mockFetch((url) => {
      seen = url;
      return new Response(JSON.stringify(DEMO_BODY), { status: 200 });
    });
    await getFundamentals("AAPL");
    expect(seen).toContain("api_token=explicit");
    expect(seen).not.toContain("estate");
  });
});

describe("symbol formatting", () => {
  it("adds the US suffix the API requires, and leaves an explicit market alone", () => {
    expect(toEodhdSymbol("crm")).toBe("CRM.US");
    expect(toEodhdSymbol("AAPL.US")).toBe("AAPL.US");
    expect(toEodhdSymbol("  v  ")).toBe("V.US");
  });
});

describe("unconfigured", () => {
  it("reports not configured and makes no request", async () => {
    const fetchFn = mockFetch(() => new Response("{}", { status: 200 }));
    expect(eodhdConfigured()).toBe(false);
    expect(await getFundamentals("AAPL")).toBeNull();
    expect(await getFundamentalsMany(["AAPL", "CRM"])).toEqual({ fundamentals: new Map(), failed: [] });
    expect(fetchFn).not.toHaveBeenCalled();
  });
});

describe("mapping", () => {
  it("carries the reported figures, and keeps the withheld ones null rather than zero", async () => {
    process.env.EODHD_API_KEY = "test";
    mockFetch(() => new Response(JSON.stringify(DEMO_BODY), { status: 200 }));

    const f = await getFundamentals("AAPL");
    expect(f).not.toBeNull();
    expect(f?.marketCap).toBe(5_074_783_305_728);
    expect(f?.revenueTTM).toBe(478_833_999_872);
    expect(f?.ebitda).toBe(171_486_003_200);
    expect(f?.enterpriseValue).toBe(5_098_172_276_220);
    expect(f?.trailingPE).toBeCloseTo(39.2371, 4);
    expect(f?.priceToSales).toBeCloseTo(10.4844, 4);
    expect(f?.name).toBe("Apple Inc.");
    expect(f?.currency).toBe("USD");
    // The vendor's own ratio, not one computed from its figures — this is the arm that was dead
    // while the code read the wrong spelling.
    expect(f?.evToEbitda).toBeCloseTo(29.9582, 4);
  });

  it("computes EV/EBITDA from the two figures only when the source omits the ratio", async () => {
    process.env.EODHD_API_KEY = "test";
    const { EnterpriseValueEbitda: _omit, ...valuation } = DEMO_BODY.Valuation;
    mockFetch(() => new Response(JSON.stringify({ ...DEMO_BODY, Valuation: valuation }), { status: 200 }));
    const f = await getFundamentals("AAPL");
    expect(f?.evToEbitda).toBeCloseTo(5_098_172_276_220 / 171_486_003_200, 6);
    // ...and that number is not the vendor's, which is why the source branch must win when present.
    expect(f?.evToEbitda).not.toBeCloseTo(29.9582, 2);
  });

  it("returns null for a body with neither General nor Highlights", async () => {
    process.env.EODHD_API_KEY = "test";
    mockFetch(() => new Response(JSON.stringify({}), { status: 200 }));
    expect(await getFundamentals("ZZZZ")).toBeNull();
  });
});

describe("failure paths", () => {
  it("returns null on a 401 rather than a partial figure", async () => {
    process.env.EODHD_API_KEY = "wrong";
    mockFetch(() => new Response("Unauthorized", { status: 401 }));
    expect(await getFundamentals("AAPL")).toBeNull();
  });

  it("returns null when the request throws or aborts", async () => {
    process.env.EODHD_API_KEY = "test";
    mockFetch(() => {
      throw new DOMException("aborted", "AbortError");
    });
    expect(await getFundamentals("AAPL")).toBeNull();
  });

  it("omits the symbols that failed from a batch, and never invents one", async () => {
    process.env.EODHD_API_KEY = "test";
    mockFetch((url) =>
      url.includes("CRM") ? new Response(JSON.stringify(DEMO_BODY), { status: 200 }) : new Response("", { status: 500 }),
    );
    const batch = await getFundamentalsMany(["AAPL", "CRM", "NOW"]);
    expect([...batch.fundamentals.keys()]).toEqual(["CRM"]);
    // A failure is named, not silently absent: the page reports how many rows each source served.
    expect(batch.failed.sort()).toEqual(["AAPL", "NOW"]);
  });
});
