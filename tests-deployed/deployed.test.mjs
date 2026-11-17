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

test("the public health path reports a serving instance", async () => {
  // The public /api/health, not the container-level probe: after the split this is the web
  // app's route, before it the Python status body. Either way it must answer 200 with a
  // release version — a health path that cannot fail is the defect this replaced.
  const res = await get("/api/health");
  assert.equal(res.status, 200, `/api/health returned ${res.status}`);
  const body = await res.json();
  assert.equal(body.status, "ok");
  assert.match(String(body.version), /^\d+\.\d+\.\d+$/, `version '${body.version}' is not a release`);
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

test("/api/* reaches the web application, not a Python status blob", async () => {
  // The regression this catches: both Python handlers used to answer every /api/* path,
  // so Auth.js, billing and the Stripe webhook were shadowed by a 200 that looked fine.
  // The status assertion matters as much as the shape one: once the handlers 404 unowned
  // paths, a 404 is JSON with no `available`/`methods` and would otherwise pass the leak
  // check while the route was still dead. Auth.js answers this endpoint with 200.
  const res = await get("/api/auth/session");
  const raw = await res.text();
  assert.equal(res.status, 200, `/api/auth/session returned ${res.status} — expected the web app, not a Python handler`);
  assert.match(String(res.headers.get("content-type")), /application\/json/);
  const body = JSON.parse(raw);
  // Auth.js answers `null` when unauthenticated; the calculator blob and its 404 are objects.
  assert.ok(
    body === null || (typeof body === "object" && !Array.isArray(body)),
    `unexpected /api/auth/session body: ${raw.slice(0, 80)}`,
  );
  if (body && typeof body === "object") {
    for (const leak of ["available", "methods", "error"]) {
      assert.ok(!(leak in body), `/api/auth/session is answered by a Python handler (saw '${leak}')`);
    }
  }
});
