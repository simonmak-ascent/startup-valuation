import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

/**
 * `/api/health` is the probe the rollout gate and the ALB both depend on, and it was the one route
 * with no test at all. It reports the market-data dependency, caches the answer for a window, and
 * must not leak the upstream's message on an unauthenticated endpoint.
 */
const quote = vi.fn();

vi.mock("yahoo-finance2", () => ({
  default: class {
    quote = quote;
  },
}));

// The memo is module state, so each test gets a fresh module: without this a later case reads the
// previous case's cached answer and the assertions stop describing the probe.
async function load() {
  vi.resetModules();
  const mod = await import("@/app/(en)/api/health/route");
  return mod.GET;
}

async function body(response: Response): Promise<Record<string, unknown>> {
  return (await response.json()) as Record<string, unknown>;
}

beforeEach(() => {
  quote.mockReset();
  vi.useFakeTimers();
  vi.setSystemTime(new Date("2026-11-18T12:00:00Z"));
});

afterEach(() => {
  vi.useRealTimers();
});

describe("GET /api/health", () => {
  it("reports the dependency it actually probes", async () => {
    quote.mockResolvedValue({ regularMarketPrice: 350 });
    const GET = await load();
    const res = await GET();
    const json = await body(res);
    expect(res.status).toBe(200);
    expect(json.status).toBe("ok");
    const dependency = json.dependency as Record<string, unknown>;
    expect(dependency.name).toBe("finance.yahoo.com");
    expect(dependency.status).toBe("reachable");
    expect(dependency.cached).toBeUndefined();
  });

  it("answers from the memo inside the window instead of probing again", async () => {
    quote.mockResolvedValue({ regularMarketPrice: 350 });
    const GET = await load();
    await GET();
    expect(quote).toHaveBeenCalledTimes(1);

    vi.setSystemTime(new Date("2026-11-18T12:00:10Z")); // 10 s later, inside the 15 s window
    const second = await GET();
    const json = await body(second);
    expect(quote).toHaveBeenCalledTimes(1);
    expect((json.dependency as Record<string, unknown>).cached).toBe(true);
  });

  it("probes again once the window has passed", async () => {
    quote.mockResolvedValue({ regularMarketPrice: 350 });
    const GET = await load();
    await GET();
    vi.setSystemTime(new Date("2026-11-18T12:00:20Z")); // past the window
    await GET();
    expect(quote).toHaveBeenCalledTimes(2);
  });

  it("coalesces concurrent callers onto one upstream probe", async () => {
    let release: (value: unknown) => void = () => {};
    quote.mockReturnValue(new Promise<unknown>((resolve) => { release = resolve; }));
    const GET = await load();

    const first = GET();
    const second = GET();
    // Two callers, one probe. Without the cached promise this counted twice and the endpoint was a
    // free upstream client for whoever arrived during the window.
    expect(quote).toHaveBeenCalledTimes(1);

    release({ regularMarketPrice: 350 });
    const [a, b] = await Promise.all([first, second]);
    expect(a.status).toBe(200);
    expect(b.status).toBe(200);
  });

  it("maps a timeout to 503 with a classified detail, not the upstream message", async () => {
    const upstream = Object.assign(new Error("socket hang up at api.example.internal"), {
      name: "TimeoutError",
    });
    quote.mockRejectedValue(upstream);
    const GET = await load();
    const res = await GET();
    const json = await body(res);
    expect(res.status).toBe(503);
    expect(json.status).toBe("degraded");
    const dependency = json.dependency as Record<string, unknown>;
    expect(dependency.status).toBe("unreachable");
    expect(dependency.detail).toBe("timeout");
    // The endpoint is unauthenticated: the upstream's own text must not appear.
    expect(JSON.stringify(json)).not.toContain("socket hang up");
    expect(JSON.stringify(json)).not.toContain("api.example.internal");
  });

  it("classifies an ordinary failure as upstream_error", async () => {
    quote.mockRejectedValue(new Error("boom"));
    const GET = await load();
    const json = await body(await GET());
    expect((json.dependency as Record<string, unknown>).detail).toBe("upstream_error");
  });
});
