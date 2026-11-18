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
    "/api/audit",
    "/api/billing/checkout",
    "/api/export/report",
    "/api/webhooks/stripe",
  ];
  for (const path of removed) {
    const res = await get(path);
    assert.equal(res.status, 404, `${path} returned ${res.status} — the surface was removed`);
  }
});

test("/api/* reaches the web application, not a Python status blob", async () => {
  // The regression this catches: both Python handlers used to answer every /api/* path, so the
  // web app's own routes were shadowed by a 200 that looked fine. Sign-in, billing and the Stripe
  // webhook have since been removed with the database dependency, so this asserts against a route
  // that must keep existing: POST /api/ai with an empty query answers 400 {"error":"Query is
  // required"}, which a Python handler never produced. A GET answers 405 with no body at all, so it
  // cannot be asserted for content-type — measured live before writing this.
  const res = await postJSON("/api/ai", { query: "" });
  const raw = await res.text();
  assert.equal(res.status, 400, `/api/ai returned ${res.status} for an empty query`);
  assert.match(String(res.headers.get("content-type")), /application\/json/);
  const body = JSON.parse(raw);
  assert.equal(body?.error, "Query is required", `unexpected /api/ai body: ${raw.slice(0, 80)}`);
  for (const leak of ["available", "methods"]) {
    assert.ok(!(leak in body), `/api/ai is answered by a Python status blob (saw '${leak}')`);
  }
});
