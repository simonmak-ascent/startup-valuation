# Test plan — the whole advertised surface, and how each claim is proven

Derived from what the application *tells a user it does*: the landing copy (`lib/landing.ts`), each
page's own metadata, `compliance.json` (the declared contract), `server.json` (what the MCP registry
publishes) and the generated method registry. A surface is in scope because the product advertises
it, not because a directory exists.

Measured 2026-11-18 against `https://startup-valuation.ascent-partners.com`.

## 1 · What "100%" means here

Four axes, all of them required. A route that only answers `200` with an empty shell is **not**
covered.

| axis | the claim being tested | count |
|---|---|---|
| **routes** | every page the navigation and metadata advertise | 17 pages + 3 legal |
| **states** | each route's reachable states — anonymous, signed-in, degraded, invalid input | ≥3 per data-bearing page |
| **journeys** | each multi-step workflow the copy describes (calculate, MCP, playground, advisor, billing) | 6 |
| **claims** | each sentence in the advertising that promises behaviour | 13 (§5 matrix) |

**Rule:** a claim with no assertion is a gap, and a gap is listed in §6 rather than left implicit.
Coverage is reported as `claims asserted / claims advertised`, never as a percentage of files.

## 2 · The advertised contract, quoted

| # | where it is advertised | the promise | measured |
|---|---|---|---|
| C1 | `lib/landing.ts:56` | *Value pre-revenue and fast-growing startups with scorecard, VC and options methods* | 27 methods in `method_registry` |
| C2 | `lib/landing.ts:57` | *We make the forecast explicit — and method-backed* | each result carries its method name |
| C3 | `lib/landing.ts:69` | *Auditable: every result carries its formula, assumptions and steps* | `ValuationResult` has all three |
| C4 | `lib/landing.ts:67` | *Scorecard, Berkus, VC method, Black-Scholes, scenario analysis* | five method families present |
| C5 | `lib/landing.ts:68` | *SaaS, biotech, fintech, marketplace, hardware* | 7 Industry methods |
| C6 | `lib/landing.ts:73` | *Point an MCP client at the hosted endpoint. Open access, no API key.* | `POST /mcp` answers without `Authorization` |
| C7 | `lib/landing.ts:59` | *14 MCP tools* | `tools/list` → **14** |
| C8 | `lib/landing.ts:60` | *80+ formulas* | **no computable referent** — see F1 |
| C9 | `lib/landing.ts:61` | *5 method families* | Core 5, Industry 7, Foundation 9, Stakeholder 4, Emerging 2 = **5** |
| C10 | `app/(en)/api/playground/page.tsx:7` | *Test 27+ valuation methods* | registry has **27**, not 27+ — see F2 |
| C11 | `server.json` | MCP package `startup-valuation` 2.1.4, remote `…/mcp`, streamable-http | registry entry still advertises `…/api` — see B5 |
| C12 | `compliance.json` | PR-required merge; verify = pytest + ruff + tsc + vitest; probes | four probes, all `200` once the DB lands |
| C13 | page metadata (`/methods/[slug]`, legal) | each method page is canonical and indexable | 27 slugs |

**F1 — "80+ formulas" cannot be tested as written.** The registry exposes one `formula_number` per
method and there are 14 distinct values across 27 methods. Nothing in the repository produces a
count of 80. Either the claim counts something not modelled (formulas per chapter, in the
textbook) and needs its referent named, or the copy is wrong. A test cannot assert a number the
code does not define — this is the `AGENTS.md` §1.2 case, and it is reported, not guessed.

**F2 — "27+" is false at 27.** `METHODS` has exactly 27 entries, and the playground's metadata
promises "27+". Either the copy becomes "27" or a method is added; the assertion
`options ≥ 27` passes today, so this is a copy defect a test must **not** be written to hide —
it is asserted as `count == 27` and the discrepancy is recorded here.

## 3 · Surface inventory

`expected` is what the test asserts; `state` is the interesting condition, not just the happy path.

### 3.1 Pages — public

| route | advertised purpose | expected | state to test |
|---|---|---|---|
| `/` | landing: value, thesis, capabilities, MCP connect block | 200; `<html lang="en-GB">`; H1 carries "Startup Valuation"; the capability list renders every item from `LANDING_COPY` | anonymous; zh/hk switch visible |
| `/zh` | Simplified Chinese landing | 200; `lang="zh-Hans"`; body text is Chinese, not a fallback copy | anonymous |
| `/hk` | Traditional Chinese (HK) landing | 200; `lang="zh-Hant-HK"` | anonymous |
| `/methods/[slug]` | one page per method, formula + inputs | 200 for **every** slug in `METHODS`; H1 = method name; the formula block renders (KaTeX) | all 27 slugs; one unknown slug → 404 |
| `/api/playground` | "test 27+ methods with live inputs" | 200; the method selector offers exactly **27** options (F2: the copy says 27+); submitting returns JSON in-page | valid input; invalid input shows an error, not a blank |
| `/ai-advisor` | AI advisor UI | 200; the form renders; submit disabled without input | no key configured → visible error, not a hang |
| `/benchmarks` | industry benchmarks | 200; renders rows **or** an explicit empty state | empty (today) and populated (after ETL) |
| `/public-companies` | comparables | 200; rows or explicit empty state | empty and populated |
| `/skills` | agent skill catalogue | 200; each skill entry has a name and a callable example | anonymous |
| `/why-open-source` | positioning page | 200; contains the licence/source link | anonymous |
| `/support` | contact | 200; contact address present | anonymous |
| `/sign-in` | authentication entry | 200; provider button present | anonymous |
| `/dashboard` | private area | **307 → `/sign-in`** when anonymous; 200 when signed in | anonymous (today), signed-in (blocked, §6) |
| `/legal/privacy`, `/legal/terms`, `/legal/cookies` | legal pages | 200; non-empty body; last-updated date present | all three |
| `/docs` | documentation site (advertised in AGENTS.md) | **404 today** — gap G1 | — |

### 3.2 HTTP API

| route | method | expected | state to test |
|---|---|---|---|
| `/api/calculate` | POST | 200 `{"value": <finite>, "method", "inputs", "assumptions", "chapter", "formula_number", "steps"}` | one request per method key; unknown method → 4xx with a message, never 200 with an error body (the `$NaN` bug) |
| `/api/calculate` | GET | 405 or 404, never a 200 status blob | method check |
| `/api/health` | GET | 200 `{"status":"ok", …}` when the DB is reachable; 503 `{"status":"degraded","db_status":"disconnected"}` when not | **degraded today** — asserts the honest failure |
| `/api/auth/session` | GET | 200 `null` anonymous; 200 with `user` when signed in | anonymous |
| `/api/ai` | POST | validation error (`VALIDATION_ERROR`) without `method`; 200 with an answer when configured | invalid input; configured (gated) |
| `/api/audit` | GET | requires a session; 401/403 anonymous | anonymous |
| `/api/export/report` | GET | requires `run_id`; 4xx without one | missing param |
| `/api/billing/checkout` | POST | 401/redirect anonymous | anonymous |
| `/api/webhooks/stripe` | POST | **rejects an unsigned payload** | no signature → 4xx |
| `/.well-known/mcp.json` | GET | 200 JSON; `url` ends `/mcp`; `transport` is streamable-http | shape + value |

### 3.3 MCP endpoint

| check | expected |
|---|---|
| `POST /mcp` `initialize` | 200, `protocolVersion` present, `serverInfo.name` = startup-valuation |
| `POST /mcp` `tools/list` | 200; **14** tools; every tool has `name`, `description`, `inputSchema` |
| `POST /mcp` `tools/call` | one call per tool: result carries a value, inputs and assumptions (see C3) |
| `POST /mcp` unknown method | JSON-RPC error object, not HTTP 500 |
| `GET /mcp` | **405** with `Allow: POST, OPTIONS` — a 200 here makes a client treat the endpoint as REST and never send `initialize` |
| `POST /mcp` no auth | works — C6 promises open access |

### 3.4 Discovery & i18n

| check | expected |
|---|---|
| `/robots.txt` | 200; `Disallow` entries present; sitemap referenced |
| `/sitemap.xml` | 200; contains `/zh` and `/hk`; every listed URL resolves 200 |
| `hreflang` on `/` | three alternates (en, zh-Hans, zh-Hant-HK) |
| locale switch | from `/` → `/zh` → `/hk` preserves the current page, not the home page |

## 4 · Journey tests — the workflows the UI describes

Each journey is a browser test (headed Chrome over CDP); the API and MCP halves are also asserted
head-lessly so a UI regression and a protocol regression are distinguishable.

**J1 — "value a startup and inspect the maths"** (C1, C2, C3)
`/` → method catalogue → `/methods/scorecard` → fill inputs → Calculate →
assert a currency figure, a formula reference (`3.1`), a step list, and assumptions; then change one
input and assert the figure changes (proves it is computed, not canned).

**J2 — "point an MCP client at the endpoint"** (C6, C9)
`initialize` → `tools/list` (14) → `tools/call` on a method → assert the result matches J1's
calculation for the same inputs. This is the one assertion that ties the two surfaces together.

**J3 — playground** (C7)
`/api/playground` → choose a method → submit → assert the rendered JSON has the same shape as
`/api/calculate`; then submit an invalid input and assert an inline error.

**J4 — AI advisor**
`/ai-advisor` → type a question → submit → either an answer grounded in a method, or an explicit
"not configured" message. No spinner forever, no empty message bubble.

**J5 — auth and gated area**
`/dashboard` anonymous → 307 `/sign-in` → sign in (blocked, §6) → dashboard renders the user's runs.
Anonymous half is testable today; the signed-in half is not.

**J6 — money**
`/sign-in` → checkout → Stripe → webhook → subscription visible in dashboard. Blocked (§6).

## 5 · Claim → assertion matrix

| claim | asserted by |
|---|---|
| C1 methods value a startup | J1 + `/api/calculate` per method key |
| C2 forecast is explicit and method-backed | J1 asserts the method name and inputs echo |
| C3 every result is auditable | J1 asserts formula + assumptions + steps; MCP `tools/call` asserts the same |
| C4 the five named method families | `/methods/*` 200 for each family's slug; one calculate call per family |
| C5 the five industry verticals | `/api/calculate` with each vertical's method key |
| C6 open MCP access, no key | `POST /mcp` without `Authorization` |
| C7 "14 MCP tools" | `tools/list` length == 14 |
| C8 "80+ formulas" | **not asserted** — no referent (F1); reported as a copy defect |
| C9 "5 method families" | distinct `category` values in `METHODS` == 5 |
| C10 "27+" playground methods | selector option count == **27**, and F2 is reported |
| C11 registry entry | `server.json` remote == `/.well-known/mcp.json` url == `/mcp` |
| C12 declared contract | `compliance.json` probes run as the deployed suite |
| C13 method pages indexable | canonical + title present on each of the 27 slugs |

## 6 · Gaps — advertised but not yet testable

| # | gap | why it cannot be asserted today |
|---|---|---|
| G1 | `/docs` | **404** — the mkdocs `site/` is not in the web image (plan B3) |
| G2 | `/benchmarks`, `/public-companies` populated states | the DB has no tables; both render empty states |
| G3 | `/dashboard` signed-in | no user can sign in without a DB-backed session store |
| G4 | `/api/export/report` success | needs a `run_id`, which needs the DB |
| G5 | `/api/ai` 200 path | needs `DEEPSEEK_API_KEY` wired into the web container |
| G6 | billing end-to-end | needs Stripe test keys and a webhook endpoint |
| G7 | `POST /mcp` per-tool semantics | one call per tool exists; the *valuation* assertions for all 14 are partly blocked on tools that read data |

Each gap is already a task in `docs/plan.md` Part 2 (B2, B3, F2). A gap is not a hidden failure: the
route is asserted for its *current* honest state (503, empty state, 307) so a change in behaviour is
caught even before the dependency lands.

## 7 · Levels, commands, cadence

| level | what | command | when |
|---|---|---|---|
| L1 deployed black box | routes, headers, JSON shapes, MCP protocol | `node --test --test-reporter=spec tests-deployed/*.test.mjs` | every deploy + twice daily (schedule) |
| L2 journeys | J1–J6 in a real browser | `pnpm test:e2e` (Playwright, `PLAYWRIGHT_BASE_URL` pointed at the deployed origin) | before a release, and on the deployed origin after a routing change |
| L3 unit | route handlers, methods registry, pin checker | `pnpm test` + `python3 -m pytest tests-ci/` | every PR |
| L4 Python library | 103 public functions, `ValuationResult` shape | `pytest --cov-fail-under=85` | every PR |

**Gate wiring.** L1 runs inside `deploy-digest.yml`'s `verify` job and its failure stops the chain
(no new pins while production is red). L3/L4 are `ci.yml`'s required checks. L2 is deliberately not
a merge gate — a browser suite on a shared runner is flaky — but a red L2 on the deployed origin is
recorded as an issue by `e2e-deployed.yml`'s diagnosis step.

## 8 · How this plan fails honestly

- Every expected value above is a **literal** (status code, count, field name), so a test can only
  pass by matching it. No "assert truthy".
- Each journey asserts a *change* (input changes → output changes) where the product claims
  computation. A canned response must fail J1.
- The gated surfaces are asserted for their current failure state, so "degraded" is a known value,
  not an absence of a test. When the dependency lands, that assertion flips from 503 to 200 — a
  deliberate edit, visible in review.
