import { NextResponse } from "next/server";
import pkg from "../../../../package.json";
import YahooFinance from "yahoo-finance2";

// Deliberately its own client: sharing one with the pages puts the probe behind their queue, so a
// revalidation burst would make the ALB probe return 503 for queue wait rather than for Yahoo.
const probe = new YahooFinance({ suppressNotices: ["yahooSurvey"] });

// The probe costs an upstream round-trip and this endpoint is unauthenticated — the web container's
// ALB probe is `/`, and `/api/health` is the Python containers' probe path, so any caller can reach
// it. Without a memo the health path is a free Yahoo client, and a burst there degrades the
// comparables pages to their "source did not answer" state with the prober as the cause.
const MEMO_MS = 15_000;
type Probe = { reachable: boolean; detail: string; latency: number };
let memo: (Probe & { at: number }) | null = null;
// Caching the *promise*, not just the result: without this every request arriving together at a
// window boundary starts its own upstream probe, and the caller chooses how many arrive.
let inFlight: Promise<Probe> | null = null;

export const dynamic = "force-dynamic";

/**
 * Health for a service whose only external dependency is the market-data source.
 *
 * There used to be a database check here. This application never had a database on this estate —
 * the keys it read (`SURREALDB_*`) were configured nowhere — so the probe reported `degraded` from
 * the first deployment and could not distinguish a broken app from a missing dependency. It now
 * reports the thing the product actually depends on: whether the comparables can be priced. If
 * Yahoo does not answer, `/benchmarks` and `/public-companies` have nothing to show, and saying so
 * is the truthful answer.
 */


export async function GET() {
  const started = Date.now();
  if (memo && started - memo.at < MEMO_MS) {
    return NextResponse.json(
      {
        status: memo.reachable ? "ok" : "degraded",
        version: pkg.version,
        dependency: {
          name: "finance.yahoo.com",
          status: memo.reachable ? "reachable" : "unreachable",
          detail: memo.detail,
          latency_ms: memo.latency,
          cached: true,
        },
      },
      { status: memo.reachable ? 200 : 503 },
    );
  }

  // One upstream probe per window, however many callers arrive during it. The memo alone only helps
  // once a probe has finished; caching the *promise* is what a burst actually shares, and it is what
  // stops an unauthenticated path from being a free Yahoo client.
  let pending = inFlight;
  if (!pending) {
    const at = started;
    pending = (async (): Promise<Probe> => {
      const t0 = Date.now();
      let reachable = false;
      let detail = "";

      try {
        // Per request: a signal created at module scope aborts every later probe.
        // This route's own client (see the file header): one crumb handshake per probe, deliberately
        // not the pages' queue, with a budget short enough that a caller is not waiting on it.
        const quote = await probe.quote("AAPL", {}, {
          fetchOptions: { signal: AbortSignal.timeout(4000) },
        });
        reachable = Boolean(quote && (quote.regularMarketPrice ?? quote.marketCap));
        detail = reachable ? "AAPL priced" : "no price in the response";
      } catch (error) {
        // Classified, not echoed: this endpoint is unauthenticated, so the upstream's own text does
        // not belong in the response body. `AbortSignal.timeout` rejects with "TimeoutError", not
        // "AbortError"; both are accepted so the branch cannot rot into unreachable.
        const name = error instanceof Error ? error.name : "";
        detail = name === "TimeoutError" || name === "AbortError" ? "timeout" : "upstream_error";
        console.error("[health] market-data probe failed:", error);
      }

      const result: Probe = { reachable, detail, latency: Date.now() - t0 };
      // Written by the probe itself, so a caller that joins mid-flight still leaves a warm memo.
      memo = { ...result, at };
      return result;
    })().finally(() => {
      inFlight = null;
    });
    inFlight = pending;
  }

  const shared = await pending;

  return NextResponse.json(
    {
      status: shared.reachable ? "ok" : "degraded",
      version: pkg.version,
      dependency: {
        name: "finance.yahoo.com",
        status: shared.reachable ? "reachable" : "unreachable",
        detail: shared.detail,
        latency_ms: shared.latency,
      },
    },
    { status: shared.reachable ? 200 : 503 },
  );
}
