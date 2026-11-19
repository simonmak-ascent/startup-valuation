// End-to-end tests against the DEPLOYED product, not a local build.
//
// These run after every rollout (deploy-digest.yml) and on a schedule, so the gate is
// "the live host serves the contract", which no unit test can assert. Nothing here starts
// a server: `DEPLOYED_BASE_URL` defaults to production.
//
// Plain node:test + fetch on purpose — no browser binary to download on a runner, no extra
// dependency, and the surface that matters here is HTTP.
//
// Run: pnpm test:e2e:deployed        (or DEPLOYED_BASE_URL=… node --test tests-deployed/)

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import http from "node:http";
import https from "node:https";

const BASE = (
  process.env.DEPLOYED_BASE_URL ?? "https://startup-valuation.ascent-partners.com"
).replace(/\/+$/, "");

const TIMEOUT = 15_000;

function get(path, init = {}) {
  return fetch(`${BASE}${path}`, {
    redirect: "manual",
    signal: AbortSignal.timeout(TIMEOUT),
    ...init,
  });
}

function postJSON(path, body) {
  return get(path, {
    method: "POST",
    headers: { "content-type": "application/json", accept: "application/json, text/event-stream" },
    body: JSON.stringify(body),
  });
}

test("the site answers 200 and serves the application", async () => {
  const res = await get("/");
  assert.equal(res.status, 200, `${BASE}/ returned ${res.status}`);
  const html = await res.text();
  assert.match(html, /<title>[^<]*Startup Valuation/i);
});

test("both translated locales answer 200", async (t) => {
  for (const path of ["/zh", "/hk"]) {
    const res = await get(path);
    assert.equal(res.status, 200, `${path} returned ${res.status}`);
    await res.arrayBuffer();
  }
});

test("the public health path reports the dependency the product actually has", async () => {
  // Health used to check a database this application never had, so it answered 503 from the first
  // deployment and could not distinguish a broken app from a missing dependency. It now probes the
  // market-data source: 200 when Yahoo answers, 503 when it does not, with the latency and the
  // reason in the body. Both states are honest; only 200 is healthy.
  const res = await get("/api/health");
  const body = await res.json();
  // 200, not "200 or 503": a probe that is permanently degraded passes the tolerant form while the
  // comparables pages are dead, which is the defect this change-set exists to remove. A sustained
  // 503 is a real outage — the product has no data to show — and the scheduled run should say so.
  assert.equal(res.status, 200, `/api/health returned ${res.status} (${JSON.stringify(body)})`);
  assert.match(String(body.version), /^\d+\.\d+\.\d+$/, `version '${body.version}' is not a release`);
  assert.equal(body.dependency?.name, "finance.yahoo.com", "health does not name the dependency it probes");
  assert.ok(
    body.dependency?.status === "reachable" || body.dependency?.status === "unreachable",
    `dependency status '${body.dependency?.status}' is not one of the two states`,
  );
  assert.equal(body.status, "ok", "a 200 health body must say ok");
});

test("the comparables pages serve live market data, not an empty shell", async () => {
  // Neither page had an assertion anywhere, so a page rendering its empty state while /api/health
  // stayed green was invisible — the exact defect this change-set removes. Both pages name the
  // vendor they read; the retired builds had no such attribution and showed an empty table.
  //
  // The disjunction alone cannot tell a vendor outage from a page whose own fetch path is broken:
  // both render the same honest-failure copy. The probe uses its own client and its own symbol, so
  // when it reports the vendor reachable the page must have priced something.
  const health = await get("/api/health");
  const vendorUp = (await health.json())?.dependency?.status === "reachable";
  for (const path of ["/benchmarks", "/public-companies"]) {
    const res = await get(path);
    assert.equal(res.status, 200, `${path} returned ${res.status}`);
    // Both pages are ISR (`revalidate = 300`), but the App Router does not emit `x-nextjs-cache`:
    // in Next 15 only the Pages Router sets it, so a cached body cannot be told from a fresh one
    // and a branch keyed on that header would be dead code with a false rationale attached. The
    // assertion is unconditional instead, and the distinction comes from the body: a stale-but-good
    // page still carries a price and passes, while the source-down copy beside a reachable-source
    // health probe means this page's own fetch path is broken.
    const html = await res.text();
    assert.ok(/Yahoo Finance/i.test(html), `${path} does not name the market-data source`);
    const priced = /\d+\.\d{2}\s*(USD|\u00d7)/.test(html);
    const honestFailure = /did not answer|No price resolved/i.test(html);
    assert.ok(priced || honestFailure, `${path} shows neither a price nor an honest failure state`);
    assert.ok(
      !vendorUp || priced,
      `${path} rendered the source-down state while /api/health reports the source reachable`,
    );
  }
});

test("the MCP discovery card names the endpoint", async () => {
  const res = await get("/.well-known/mcp.json");
  assert.equal(res.status, 200, `/.well-known/mcp.json returned ${res.status}`);
  assert.match(String(res.headers.get("content-type")), /application\/json/);
  const card = await res.json();
  const url = card?.transport?.url ?? card?.remotes?.[0]?.url ?? "";
  assert.ok(url.endsWith("/mcp"), `server card points at '${url}', not the /mcp endpoint`);
});

test("the MCP endpoint completes an initialize handshake", async () => {
  const res = await postJSON("/mcp", {
    jsonrpc: "2.0",
    id: 1,
    method: "initialize",
    params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "e2e", version: "1" } },
  });
  assert.equal(res.status, 200, `POST /mcp returned ${res.status}`);
  const body = await res.json();
  assert.equal(body.jsonrpc, "2.0");
  assert.ok(body.result?.serverInfo?.name, "initialize returned no serverInfo");
});

test("GET on the MCP endpoint is refused, not answered with a status body", async () => {
  // A 200 here is what makes a client read the endpoint as a REST API and give up.
  const res = await get("/mcp");
  assert.equal(res.status, 405, `GET /mcp returned ${res.status}, expected 405`);
  await res.arrayBuffer();
});

test("the calculator computes through the deployed routing", async () => {
  const res = await postJSON("/api/calculate", {
    method: "pe_ratio",
    params: { market_cap: 1000, net_income: 100 },
  });
  assert.equal(res.status, 200, `POST /api/calculate returned ${res.status}`);
  const body = await res.json();
  assert.equal(body.value, 10, `expected 10, got ${JSON.stringify(body).slice(0, 120)}`);
});

test("the removed surfaces stay removed", async () => {
  // Sign-in, the dashboard and billing were deleted with the database dependency on 2026-11-18.
  // A reintroduction without a session store would go green on every other assertion here, so the
  // absence is asserted explicitly: these paths must 404, not redirect to a page that cannot work.
  // Every surface docs/plan.md removed, not a sample: /api/audit was an unauthenticated write
  // endpoint, and a reintroduced checkout or Stripe webhook would otherwise go unnoticed.
  const removed = [
    "/sign-in",
    "/dashboard",
    "/api/auth/session",
    "/api/auth/providers",   // Auth.js served both under the same catch-all route
    "/api/auth/csrf",
    "/api/audit",
    "/api/billing/checkout",
    "/api/export/report",
    "/api/webhooks/stripe",
    "/api/ai",          // removed with the advisor on 2026-11-18
    "/ai-advisor",      // the page: the GUI suite that also checks it is run by no workflow
  ];
  for (const path of removed) {
    const res = await get(path);
    assert.equal(res.status, 404, `${path} returned ${res.status} — the surface was removed`);
  }
});

test("/api/* reaches the web application, not a Python status blob", async () => {
  // The regression this catches: both Python handlers used to answer every /api/* path, so the web
  // app's own routes were shadowed by a 200 that looked fine. `/api/health` is the surviving web
  // route, and its body is shaped by Next — a `dependency` object the Python handlers never emit.
  // The advisor route that used to carry this assertion was removed with the advisor on 2026-11-18.
  const res = await get("/api/health");
  const raw = await res.text();
  const body = JSON.parse(raw);
  assert.equal(body.dependency?.name, "finance.yahoo.com", `/api/health is not answered by the web app: ${raw.slice(0, 80)}`);
  for (const leak of ["available", "methods"]) {
    assert.ok(!(leak in body), `/api/health is answered by a Python status blob (saw '${leak}')`);
  }
  // `/api/health` is also the Python containers' probe path, so shape alone is a weaker signal than
  // the /api/ai route this replaced. `/api/playground` is a Next page and can only be served by the
  // web app: HTML, not the handler's JSON.
  const page = await get("/api/playground");
  assert.equal(page.status, 200, `/api/playground returned ${page.status}`);
  assert.match(String(page.headers.get("content-type")), /text\/html/, "/api/playground is not served by the web app");
});

// --- the fleet, not just the node the deploy replaced --------------------------------

function pinnedImage() {
  const manifest = JSON.parse(readFileSync(new URL("../container.json", import.meta.url), "utf8"));
  const spec = (manifest.containers ?? []).find((c) => c.name === "startup-valuation");
  return String(spec?.image ?? "").split("@")[1] ?? "";
}

// One connection per probe. The ALB balances per connection, so a keep-alive pool would let a single
// node answer every sample — which is exactly how a fleet split across two digests stays invisible.
function probeImage() {
  const url = new URL(`${BASE}/api/health`);
  const mod = url.protocol === "https:" ? https : http;
  return new Promise((resolve) => {
    // `signal` is the hard bound; `req.setTimeout` below is an inactivity timer, so a body that
    // trickles a byte at a time resets it and the probe would never settle — which on a shared
    // runner holds the post-deploy gate open.
    const req = mod.get(
      url,
      { agent: false, signal: AbortSignal.timeout(TIMEOUT), headers: { accept: "application/json" } },
      (res) => {
        let raw = "";
        res.setEncoding("utf8");
        // A response-stream error is emitted on `res`, not `req`; unhandled it takes the whole test
        // process down with no result at all.
        res.on("error", () => resolve("(error)"));
        res.on("data", (chunk) => {
          raw += chunk;
        });
        res.on("end", () => {
          try {
            resolve(String(JSON.parse(raw).image ?? "") || "(none)");
          } catch {
            resolve("(unparseable)");
          }
        });
      },
    );
    req.setTimeout(TIMEOUT, () => {
      req.destroy();
      resolve("(timeout)");
    });
    req.on("error", () => resolve("(error)"));
  });
}

test("every node the balancer routes to serves the pinned image, not only the one the deploy replaced", async () => {
  const pinned = pinnedImage();
  assert.match(pinned, /^sha256:[0-9a-f]{64}$/, `container.json does not pin a digest for startup-valuation (${pinned || "none"})`);

  // A rollout replaces one node synchronously and then moves ghcr.io/<repo>:desired-<container>;
  // every other node converges from that tag on its own five-minute timer, then pulls, probes and
  // swaps. So the budget is one tick plus a rollout — 15 minutes, not 7, or a correct deploy is
  // reported as a failure whenever the timer fires late. A converged fleet costs one round (12
  // requests), so this does not slow the scheduled run.
  //
  // The limit of the assertion, stated: samples go through the ALB, so a target that is unhealthy
  // and out of rotation is never sampled. This catches a split fleet, not a drained node.
  const budget = Number(process.env.FLEET_DEADLINE_MS ?? 15 * 60_000);
  const deadline = Date.now() + budget;
  let seen = {};
  for (;;) {
    seen = {};
    for (let i = 0; i < 12; i += 1) {
      const image = await probeImage();
      seen[image] = (seen[image] ?? 0) + 1;
    }
    const keys = Object.keys(seen);
    if (keys.length === 1 && keys[0] === pinned) return; // the whole fleet serves the pin
    if (Date.now() > deadline) break;
    await new Promise((resolve) => setTimeout(resolve, 10_000));
  }
  const keys = Object.keys(seen);
  // Two different facts, and only the second is a split. Every node agreeing on a value that is not
  // the pin means the fleet is uniform but unlabelled: the running image predates the IMAGE_DIGEST
  // injection. Collapsing the two sends whoever reads the filed issue looking for a diverge that is
  // not there.
  const detail =
    keys.length === 1
      ? `every sampled node answered '${keys[0]}', so the fleet is uniform but does not name the pinned ` +
        `image (container.json pins ${pinned}). Not a split: the running build predates the IMAGE_DIGEST ` +
        `injection, or a peer converged under a payload that did not inject it.`
      : `the fleet is split: 12 samples, one connection each, returned ${JSON.stringify(seen)}; ` +
        `container.json pins ${pinned}`;
  assert.deepEqual(keys.sort(), [pinned], detail);
});
