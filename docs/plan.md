# Implementation plan — capability audit of the live deployment

Derived from `docs/plan-context.md` (37 in-repo defects, all measured on 2026-11-17).
This file records the plan **and** what landed. Statuses are the outcome of the work in this
branch, not intentions.

| status | meaning |
|---|---|
| **done** | implemented and verified in this change |
| **deferred** | agreed, not in this change — reason given |
| **blocked** | cannot be done from this repo; needs an operator |

## Decision

1. **The Python handlers stop answering paths they do not own.** Both `handle_request`
   implementations ignored `_path`, so whichever container a request landed on returned a 200
   status blob for *any* `/api/*` path. That is what turned a routing fault into silent success
   across eight Next.js endpoints. The guard accepts the four paths the deployment declares
   (`/api`, `/api/`, `/api/calculate`, `/api/health`) and 404s every other one.
   *Deviation from the advisor plan:* it proposed each handler own only its declared route, which
   would have taken `/api` and `/api/calculate` to 404 as well and left **no** working API before
   the operator fixes the ingress. The union keeps every currently-working path alive while
   removing the silent-200 class; it tightens to per-handler routes once X1/X2 land.
2. **A routing fault is the operator's, a lie is ours.** X1/X2 live in `apg-infra` publish
   declarations; this repo cannot fix them, so it stops misreporting them.
3. **One identity per number.** `2.1.4` had four homes: `pyproject.toml`/`__init__.py` (correct),
   `api/calculate.py` (`1.0.2`), `app/(en)/api/health/route.ts` (`1.0.2`), `lib/ai/prompts.ts`
   (`1.0.2`). The last three now derive from the lockstep-owned value — the web one via codegen.
4. **Do not redefine a published formula unilaterally.** NRR's arithmetic is encoded in
   `tests/test_saas.py:42`; the contradiction was in three prose descriptions, so the prose was
   corrected and the number left alone. The semantic question is flagged for the owner.
5. **Generated files only ever come from their source** (`AGENTS.md:28-44`): `tool_surface.py` was
   edited and `server.py` regenerated; `generate.py` was extended and `lib/methods/index.ts`
   regenerated. Both generators are idempotent (verified by double-run hash).

## Phase 1 — stop lying, stop losing data

### T1.1 · Make the `web` required check deterministic — **done**
- **files:** `.github/workflows/ci.yml`
- **change:** workflow-level `concurrency` with `cancel-in-progress: true`; `pnpm install
  --frozen-lockfile` replacing `--no-frozen-lockfile`, so the lockfile is enforced.
- **verify:** `pnpm install --frozen-lockfile` → exit 0 in 7.2 s (local); `pnpm check` + `pnpm test` green.

### T1.2 · Path guards in both Python handlers — **done**
- **files:** `api/index.py:56`, `api/calculate.py:159`
- **change:** `_OWNED_PATHS` allowlist; 404 `{"error":"NOT_FOUND"}` for anything else.
- **verify:** `handle_request("GET","/api/auth/session",None)` → 404 on both handlers.

### T1.3 · HEAD support — **done**
- **files:** `api/index.py`, `api/calculate.py`
- **change:** `do_HEAD` on both handlers; shared `_respond` sends `Content-Length` and skips the body.
- **verify:** `HEAD /api` → 200 (was 501).

### T1.4 · Reject non-finite JSON — **done**
- **files:** `api/index.py`, `api/calculate.py`
- **change:** `json.dumps(..., allow_nan=False)` everywhere; `_non_finite_key` rejects a non-finite
  **input** with 400 `NON_FINITE_INPUT` and a non-finite **result** with 422 `NON_FINITE_RESULT`.
- **verify:** `{"market_cap":NaN}` → 400 `NON_FINITE_INPUT` (was 200 with bare `NaN`).

### T1.5 · Calculator error taxonomy — **done**
- **files:** `api/calculate.py`
- **change:** `_json.loads` guarded (400 `PARSE_ERROR`); non-object bodies and `params` rejected;
  `TypeError`/`ValueError` from the library → 400 `VALIDATION_ERROR`; only genuine failures → 500.
- **verify:** malformed JSON → 400; `params:null` → 400; `weights` not summing to 1 → 400.

### T1.6 · Single version source — **done**
- **files:** `api/calculate.py`, `scripts/generate.py`, `lib/methods/index.ts`, `lib/ai/prompts.ts`
- **change:** `LIBRARY_VERSION` is `startup_valuation.__version__` in Python and a generated
  `LIBRARY_VERSION` export in TypeScript. `LIBRARY_VERSION = "1.0.2"` deleted in both places.
- **verify:** calculator GET reports `2.1.4`; `lib/methods/index.ts` emits `"2.1.4"` from `__init__.py`.

### T1.7 · Subscription upsert no longer inserts per event — **done**
- **files:** `lib/db/repositories/billing.ts`
- **change:** `UPDATE … WHERE stripe_subscription_id = $id RETURN AFTER` when the row exists, else
  `CREATE subscription:<id>` with the Stripe id as a validated, deterministic record id. SurrealDB
  semantics confirmed from the docs: an `UPSERT` with neither id nor `WHERE` is an `INSERT`.
- **verify:** `pnpm check`; end-to-end proof needs a live SurrealDB (see Blocked).

### T1.8 · Export IDOR closed — **done**
- **files:** `lib/db/repositories/audit.ts`, `app/(en)/api/export/report/route.ts`
- **change:** `getAuditLogForRun(valuationRunId, userId)` adds
  `AND user = type::record('user', $user_id)`; the route passes `session.user.id`.
- **verify:** the only call site is the export route; `tsc` confirms the new arity.

### T1.9 · Export link passes the valuation-run id — **done**
- **files:** `app/(en)/dashboard/page.tsx`
- **change:** `run.valuation_run` instead of `run.id`, matching `WHERE valuation_run = …`.
- **verify:** `tsc`; `AuditLog.valuation_run` is declared in `lib/db/schema.ts:89`.

### T1.10 · Health probe can fail — **done**
- **files:** `app/(en)/api/health/route.ts`, `lib/sdk/client.ts`
- **change:** 503 when the DB is not connected; version from `package.json`; the invented
  `tools: 46` dropped and the SDK's `health()` type corrected to the fields the route returns.
- **verify:** `pnpm check`; `healthCheck()` returns rather than throws, so the 503 path is reachable.

### T1.11 · Sitemap stops advertising non-pages — **done**
- **files:** `app/sitemap.ts`, `app/robots.ts`
- **change:** `/api/playground` and `/sign-in` removed (an API route and a disallowed page); `/zh`
  and `/hk` added; `robots` disallows `/dashboard` rather than only `/dashboard/`.
- **verify:** `pnpm build` emits `sitemap.xml`; `pnpm check`.

### T1.12 · Un-dead the three broken MCP methods — **done**
- **files:** `src/startup_valuation/mcp/tool_surface.py`, regenerated `server.py`
- **change:** `expected_value_continuous` binds `a`/`b` (it was passing `lower`/`upper`); `pwerm` and
  `employee_option` get their own schema keys (`pwerm_scenarios`, `employee_option_scenarios`) and
  stop using the `Scenario`-building adapter they could not read; the `drugs` description now names
  the four keys `pipeline_valuation` reads.
- **verify:** `pwerm` → 46,700,000 (matches its documented example); `employee_option` → 190,000;
  `pipeline` → 4.78bn; `expected_value_continuous` → 0.0.

### T1.13 · Signature-binding test — **done**
- **files:** `tests/test_mcp_surface.py`
- **change:** `test_every_method_argument_is_in_target_signature` binds every `args`/`opt` key to the
  target's `inspect.signature`, plus a parametrised dispatch test for the four repaired methods.
- **verify:** `pytest tests/test_mcp_surface.py` → 25+ pass; suite 185 pass (was 180 at HEAD).

### T1.14 · Rate-limit key + AI endpoint hardening — **done**
- **files:** `lib/rate-limit.ts`, three routes, `app/(en)/api/ai/route.ts`, `lib/ai/deepseek.ts`
- **change:** new `clientKey()` takes the **rightmost** `X-Forwarded-For` hop (the one the ALB
  appends) in all four routes; the AI advisor gains a 10/min limiter and a 30 s request timeout.
- **verify:** `tests-webapp/rate-limit.test.ts (deleted 2026-11-18 with the advisor — this row is a snapshot)` — 4 cases incl. a forged leftmost value.

### T1.15 · Audit route returns 503, not 200, on DB failure — **done**
- **files:** `app/(en)/api/audit/route.ts`
- **change:** catch returns `503 {"audit_status":"failed","error":"DB_UNAVAILABLE"}`; the raw driver
  message no longer leaks.
- **verify:** `pnpm check`.

### T1.16 · Auth.js behind the ALB — **done**
- **files:** `lib/auth/vendor/config.ts`, `lib/auth/edge-auth.ts`
- **change:** `trustHost: true` in both configs. Auth.js docs: without it (or `AUTH_TRUST_HOST`),
  every request behind a reverse proxy raises `UntrustedHost`.
- **verify:** `tsc`; runtime proof needs a live sign-in (see Blocked).

### T1.17 · Calculator reads the response it is given — **done**
- **files:** `components/CalculatorPage.tsx`, `lib/sdk/client.ts`
- **change:** state is typed as the shared `ValuationResult` (snake_case) instead of a locally
  invented camelCase shape, and the four reads follow it. `assumptions` corrected to a list.
- **verify:** `tsc` — this is the check that previously could not fire, because the shape was local.

### T1.18 · Per-locale canonical — **done**
- **files:** `components/layout/RootShell.tsx`, three layouts
- **change:** `metadataFor("/zh" | "/hk" | "")` gives each locale its own canonical while keeping one
  hreflang set. Nav left root-relative on purpose: `/zh` and `/hk` are the only pages in those
  groups, so there is no localized target to link to.
- **verify:** `pnpm build` (`/zh`, `/hk` prerendered).

### T1.19 · Benchmarks page queries the version that exists — **done**
- **files:** `lib/db/repositories/public-data.ts`, `app/(en)/benchmarks/page.tsx`
- **change:** `getLatestBenchmarkVersion()` (`ORDER BY version DESC LIMIT 1`) replaces the literal
  `"latest"`, which the ETL never writes (it writes an ISO date).
- **verify:** `pnpm check`; the writer is `etl/compute-benchmarks.ts:8`.

### T1.20 · Method pages revalidate — **done**
- **files:** `app/(en)/methods/[slug]/page.tsx`
- **change:** `export const revalidate = 3600`, so the SurrealDB assumptions panel is refreshed
  instead of frozen at build time.
- **verify:** `pnpm build` shows `1h` against `/methods/[slug]`.

## Phase 2 — correctness of published numbers

### T2.1 · NRR descriptions reconciled — **done** (arithmetic unchanged, deliberately)
Three formulas were in circulation for one function. `tests/test_saas.py:42` pins the behaviour
(`ending` excludes expansion, 1.2 for 110k + 10k), so the docstring, the step formula and the tool
summary were corrected to state that one formula, and `expansion_revenue` was added to the echoed
`inputs`. **Owner decision outstanding:** whether `ending_revenue` should be inclusive.

### T2.2 · CAPM defaults aligned — **done**
`size_premium`/`liquidity_premium` schema defaults were `0.0/0.0` against function defaults
`0.05/0.03`; the schema now states `0.05/0.03`, so the advertised default matches the applied one.
No number changes.

### T2.3 · `safe_conversion_cap` ignores `cap` — **deferred**
Fixing the formula needs the textbook's chapter-14 definition; inventing one would be worse than
the bug. Recorded, not changed.

### T2.4 · Monte Carlo positive-only truncation — **deferred**
Changes a published number; needs an owner decision on the clamp policy.

### T2.5 · Binomial "American" claim — **deferred**
Either implement early exercise (changes numbers) or change the assumption text; needs the same
decision.

### T2.6 · Description/code drift (NPV t=0, ARR ×12, density divisor, "rounded to 2 decimals") — **deferred**
Each needs the textbook formula confirmed before the text is changed.

### T2.7 · `sensitivity` never populated — **deferred, decision required**
`types.py` declares the field, `AGENTS.md:19-20` states every result carries it, and no function
sets it. Populating it across 103 functions is a project, not a patch; correcting `AGENTS.md` is a
contract change. Neither is silently decidable here.

## Phase 3 — hardening not in this change

**deferred unless noted:** audit-ledger binding for anonymous writes (`W6` — the anonymous path is
deliberate, `app/(en)/api/audit/route.ts:17`; binding rows to a server-side computation is a design
change), route-level integration tests for auth/billing/webhook (`W15`), and the Streamable-HTTP
transport claim in `api/index.py` (`P14`; only meaningful once `/api` routes to the MCP container).

## Blocked / operator

| item | who | done looks like |
|---|---|---|
| **X1/X2 — ingress inversion** | apg-infra, `publish.py plan\|apply` in a publishing window (OI-25: both node groups at the 20-rule SG limit) | `POST /api` runs the MCP `initialize`; `POST /api/calculate` runs the calculator; other `/api/*` reach the Next container |
| **X3 — `web` flake root cause** | runner owner: `PNPM_HOME` carries a pnpm **v11** store while the action switches to v10.30.3 | `web` green on the same commit for both PR and push |
| **No working deploy path** | operator | `deploy-digest.yml` exists (absent; `apg-infra`'s `container-cd.yml` is `workflow_call`-only) and `image.yml` builds (last dispatch failed at *Build and push*) |
| **api/calculate images** | operator | a Dockerfile that builds `pylaunch` + the venv; `Dockerfile.web` is Node-only, yet `container.json` pins the *same digest* for both Python containers |
| **`/docs` hosting** | operator | `GET /docs` → 200; `docs.yml` builds `site/` and publishes it nowhere |
| ~~Live verification of T1.7/T1.16~~ | **withdrawn 2026-11-18** — the Stripe webhook and sign-in were deleted with the account model (Part 5); there is nothing left to verify | — |

## Ordering as landed

1. Python handler discipline (`api/index.py`, `api/calculate.py`) → 2. MCP surface + tests
(`tool_surface.py`, regenerated `server.py`, `tests/test_mcp_surface.py`) → 3. version single-source
(`generate.py` + regenerated `lib/methods/index.ts`, `prompts.ts`) → 4. data integrity (`billing.ts`,
`audit.ts`, export route, dashboard) → 5. web hardening (health, sitemap, robots, rate limit, AI,
audit, auth, calculator UI, locales, benchmarks, methods) → 6. CI determinism.

Each was verified as it landed; the full gate run is at the end of the branch.

## Delivery status

Per `docs/delivery-gates.md`, every task above carries the five stages. As of 2026-11-17:

| stage | state |
|---|---|
| commit | ✅ 21 tasks in `3962902` |
| push | ✅ |
| merge | ✅ `b32d136` |
| deploy | ⛔ **every task that touches `api/*.py` is undeployable** — OI-40, no reproducible Python image |
| e2e | ⛔ 5 of 8 assertions fail against the live origin |

So the correct reading of this plan is **merged, not delivered**. The tasks that live in the web
container (health route, sitemap, robots, canonical) become deliverable with the `image.yml` build
pinned in `container.json`; the rest do not.

---

# Part 2 — bug fixes and feature enhancement (2026-11-18)

Everything below is measured on this date, against the live origin and the estate, not inferred.
Ordering is by what unblocks the most: the three operator items gate every delivery, so they come
first and nothing else is claimed as deliverable behind them.

## Delivery state, measured

| item | state | evidence |
|---|---|---|
| website `/`, `/zh`, `/hk` | **live** | `200`; browser render verified |
| `/mcp` (POST) | **live** | `initialize` 200; `tools/list` → **14 tools** |
| `/api/calculate` | **live** | `{"value": 10.0, "method": "P/E Ratio", …}`, 6/6 through the ALB on 3 nodes |
| calculator UI | **fixed this session** | `Result — Scorecard Method (3.1)`, `$1,800,000`; the `$NaN` was `/api/calculate` landing on the MCP handler |
| deployed e2e | **6 of 9 pass** | remaining: health body (needs the web image), `GET /mcp` (needs the Python image), and the removed-surface 404s |
| `/api/health` | **503** | `{"status":"degraded","db_status":"disconnected"}` — no `SURREALDB_*` anywhere |
| `/docs` | **404** | mkdocs `site/` is not in the web image |
| MCP registry | **advertises a dead URL** | registry says `…/api`; repo `server.json` correctly says `…/mcp` |
| Python service image | **built and probed, unshipped** | `sv-py:src-ee0ff7b` on ecs-01, 469 MB; `GET /mcp` → 405 with `Allow: POST, OPTIONS` |
| delivery chain | **built, reviewed 7×, unshipped** | 13 invariants + 13 fixtures + 1 behavioural simulator, all green |

## Operator items (blocking; agent cannot proceed)

| # | item | unblocks | verify |
|---|---|---|---|
| O1 | `rm ~/.local/share/opencode/review-gate/ses_e17d4a7e7ffesJM94SEnIaWGIV.json` | every `git commit`/`push`/deploy — record has `snapshot: {}`, so no verdict can bind (7 `ship` verdicts already lost to it) | `git commit` succeeds |
| O2 | ~~App database identity + credential handoff~~ | **withdrawn 2026-11-18** — the database was removed from the runtime on operator instruction; `/api/health` reads Yahoo, the comparables pages read Yahoo, and there is no store to credential | — |
| O3 | `DEPLOY_TOKEN` (Contents write, PR write, **Actions read**) | unattended build → pin → deploy | a push to `main` deploys without a human |

## Bug fixes

Each carries the command that proves it. Ordered so each makes the next one verifiable.

| # | bug | fix | verify |
|---|---|---|---|
| B1 | `GET /mcp` answers 200 instead of 405 | ship `sv-py:src-ee0ff7b` (built from the public repo, both roles probed) | e2e: "GET on the MCP endpoint is refused" passes |
| B2 | `/api/health` 503 | **superseded — see Part 4/5.** The runtime has no database; health reports the market-data dependency | `/api/health` 200 with `dependency.name`; e2e green |
| B3 | `/docs` 404 | build `site/` into `Dockerfile.web` and serve it | `/docs` 200 and a nav page 200 |
| B4 | retired `@vercel/analytics` fires 404s on every page load | remove the dependency and its mount | browser network: no third-party 404 |
| B5 | MCP registry points at `/api` | republish `server.json` (already correct) via `mcp-registry.yml` | registry `remotes[0].url` ends `/mcp` |
| B6 | Python image exists only on ecs-01 behind a moved tag (`sv-py:lean-v2` had three IDs) | commit the clean-room `Dockerfile.svc` + a build input on `image.yml` to apg-infra `estate/startup-valuation/` | rebuilt twice → same digest |
| B7 | `container.json` pins `362d06fd…` for both Python containers; unverifiable anonymously | resolve with an authenticated `docker manifest inspect` on a node; repin to a digest that exists | rollout pulls the pinned digest, not a local image |
| B8 | ALB target groups have **no health check** (`path=None`, `enabled=None` on all six groups) | declare per-group probes in the publish declaration and re-apply | `publish.py plan` shows no `UPDATE probe` drift |
| B9 | calculator reports the library version from `api/calculate.py`'s stale constant | derive from `startup_valuation.__version__` (fixed in the built image `sv-py:src-ee0ff7b`) | UI stamp reads 2.1.4, not 1.0.2 |

## Features

| # | feature | why | verify |
|---|---|---|---|
| F1 | deployed e2e covers a `tools/call` round trip, not just `tools/list` | listing 14 tools proves the surface, not that a method computes | a tool returns a `ValuationResult` with inputs and assumptions |
| F2 | populate `benchmark` / `public_company` from the repo's own ETL | both pages render empty states today | page shows rows sourced from `pnpm etl:import` |
| F3 | `/api/health` reports digest, version and DB latency | the current probe cannot distinguish "serving" from "serving nothing" (OI-58) | probe body contains the running digest |
| F4 | `deepseek-vision` MCP tool wired into the `vision` role | it works from the orchestrator today (`VISION-PROBE-4729`, `alpha 3.0 / beta 7.0 / gamma 5.0`); subagents have no MCP namespace yet | the `vision` agent returns the tool's text, not its own |
| F5 | one plan-visible dashboard of the chain's last 10 runs | the pin gate now depends on run history; reading it by hand is how a fail-open hid for two rounds | a URL or command that shows pin/deploy/verify per commit |

## Notes that keep the plan honest

- **The gate is the product here.** Two defects this session were found only by executing shell
  (`tests-ci/health_gate_sim.py`): a pin guard that rejected every legitimate pin, and a health
  search that hid a failure behind a page of skipped runs. Static checks passed both.
- **No health claim without a dependency.** `/api/health` now reports the market-data source it
  actually probes; it returns 200 when Yahoo answers and 503 when it does not, and the deployed suite
  asserts both states. It reads no database, so no credential can change its answer.
- **`GET /mcp` 200 is not cosmetic**: a client that gets 200 on GET treats the endpoint as REST and
  never sends `initialize`.

---

# Part 3 — the data layer, replanned on measurement

Replan of B2 after discovery, superseding "wire `SURREALDB_*`". The SurrealDB route is closed:
the managed instance answers `/health` 200 but rejects the only credential the environment holds
(401), `SURREALDB_*` — the keys `lib/db/client.ts` reads — exist nowhere, and a self-hosted instance
contradicts `apg-infra/docs/standards.md:323` (**"Every application database lives here; no node runs
a database of its own"**). The instance I started was removed.

## What the measurement says the port costs

| dimension | measured |
|---|---|
| call sites | **49** `getDb().query(...)` across 12 modules |
| verbs | SELECT 27, CREATE 18, DELETE 15, RETURN 14, UPDATE 9, UPSERT 6, INSERT 1, DEFINE 194 (schema only) |
| graph features | **none** — no `RELATE`, no edge tables, no transactions. Recordsets only |
| schema | 17 tables + indexes, `lib/db/migrate.ts`; `SCHEMALESS` by default |
| client | no `pg`/`drizzle`/`prisma`/`kysely` in `package.json` |
| network | RDS `10.20.12.80:5432` **open** from ecs-01/02/03 (`psql` 18 present); workstation cannot reach it |
| credentials | none for this app; `sv-api.env` has only auth keys. Other apps hold their own DSNs, not ours |
| roles | application roles are `rolcreatedb=f` (`standards.md:1113`) — an app cannot create its own database |

No graph features is the load-bearing fact: every verb maps 1:1 to SQL, and 194 of the 303 verb
occurrences are schema definitions that translate once.

## P0 — the one prerequisite (operator)

A **role** and a **database-or-schema** for this app on `pgm-3nsg37yxwbwd74jf`. Not inferable and
not creatable from anything held here: app roles cannot create databases, and `apg-ops` is denied
the RDS control plane. Following the estate's existing precedent for a shared database
(`ndc_report` owns `ndc_`-prefixed tables in `esg_hub/main`), either shape works:

- a database `startup_valuation` with a role of the same name, **or**
- a Postgres schema `startup_valuation` inside an existing database, with the role set as its owner.

**verify:** `psql "$DSN" -c 'select current_database(), current_user'` returns the pair, and the role
owns what it creates.

## Tasks, each with the command that proves it

| # | task | verify |
|---|---|---|
| **T1** | add `pg` and a pool; rewrite `lib/db/client.ts` behind its existing surface (`getDb().query`) so the 49 call sites do not change shape | `pnpm check` passes; a unit test drives `healthCheck()` against a stub pool for both states |
| **T2** | translate `lib/db/migrate.ts` (17 tables, indexes) into `db/migrations/*.sql`, applied by a runner in one transaction | applied to a scratch database inside a **rolled-back** transaction (`standards.md:1278` precedent); `\d` output diffed against the table list in `migrate.ts` |
| **T3** | port the 49 sites by verb: `RETURN` → `SELECT`, `UPSERT` → `INSERT … ON CONFLICT`, `CREATE … CONTENT` → `INSERT … RETURNING` | each module's existing tests pass; a golden test asserts the generated SQL for the three non-trivial shapes |
| **T4** | wire `DATABASE_URL` into `/etc/startup-valuation/sv-web.env` from RDS, never from a file I read | `/api/health` → 200 `{"status":"ok"}`, and 503 with a *timeout* when the pool is broken — both asserted |
| **T5** | ETL sources (`fred`, `eodhd`, `damodaran`, `crunchbase`, `sec-edgar`) write through the new client | row counts per source after a run, and provenance columns non-null on a sample of 3 rows |
| **T6** | deployed e2e | 8/8, including the health assertion |

## Why not the alternatives

| option | rejected because |
|---|---|
| keep the managed SurrealDB | its credential is dead (401) and it is outside estate control; `SURREALDB_*` exists nowhere |
| self-host SurrealDB on a node | `standards.md:323` forbids a node running its own database; the user also forbade a new database |
| point `/api/health` at RDS without porting | the check would report "connected" while every data page still speaks SurrealQL — a checker that cannot fail |
| borrow another app's DSN | not ours; `hkex-tracker` and `ascent-linkage` credentials are their own identities |

## Sequence

`P0` → T1 → T2 → T3 (per module, each merged on its own) → T4 → T5 → T6. T4 is deliberately after
T3: switching the health check before the call sites means the suite goes green while the product
does not work.

---

# Part 4 — do we even need the database? (measured 2026-11-18)

Part 3 assumed the data layer must move to RDS wholesale. That assumption was too broad. Split by
*who writes the data*, because the two halves have different answers.

## Reference data — no database at all

The two pages that render empty states need data that is published publicly and moves slowly.

| page | table it reads | public source | measured today |
|---|---|---|---|
| `/benchmarks` | `benchmark` (industry betas, multiples, risk premia) | Damodaran Online | `betas.xls` **200, 82 KB**; `vebitda.xls` **200, 59 KB** — no key |
| `/public-companies` | `public_company`, `financial_metric` | SEC EDGAR | `company_tickers.json` **200, 796 KB**; `companyfacts` **200** — no key, User-Agent only |

**And the importers fetch nothing.** `etl/sources/damodaran.ts` and `sec-edgar.ts` read
`etl/data/damodaran.csv` / `sec-edgar.csv`; `etl/data/` contains only a README. The acquisition half
of the pipeline was never written — only `eodhd.ts` calls an API, and it needs a paid key.

So the smallest honest path for these two pages is **build-time acquisition into versioned JSON**,
carrying the provenance the repo already enforces (`source_url`, `source_name`,
`source_retrieved_at`, `source_version` in `validateProvenance`). No runtime database, no empty
state, no invented rows.

## User-generated data — needs a store

`valuation_run`, `audit_log`, `/dashboard`, `/api/export/report` are per-user records. Nothing
public replaces them. They are also entirely behind sign-in, which does not work today (the auth
config pulls a SurrealDB adapter, and sessions are JWT only for the edge runtime).

## What this changes about the port

Part 3's T3 (port 49 call sites) shrinks: **`lib/benchmarks/compute.ts` and the two reference
importers leave the list**, because they stop reading a database. What remains is user-record
persistence, which can wait until there is a user who can sign in.

It also corrects a claim in Part 3: the model is **not** graph-free. `lib/db/migrate.ts` defines six
`TYPE record<…>` links (`method`, `audit_log.valuation_run`, `industry`, `company` ×2,
`benchmark.industry`) and `compute.ts` traverses one (`source.reputation`). Those become JOINs, not a
blocker — but the earlier "none" was wrong.

## Revised tasks

| # | task | verify |
|---|---|---|
| **D1** | `scripts/fetch-reference.ts`: pull Damodaran `.xls` + SEC `companyfacts` for a declared ticker set; write `data/reference/*.json` with provenance columns | file exists, row count > 0, and every row has non-null `source_url`/`retrieved_at`; a validator that fails on a row with an empty field |
| **D2** | `lib/benchmarks/*` and the two pages read that JSON instead of `getDb()` | `/benchmarks` and `/public-companies` render rows from the artefact; with the file removed they render the empty state, and that state is distinguishable in a test |
| **D3** | `/api/health` reports the artefact's freshness and a real computation, not a DB socket | 200 with `reference_age_hours` and a computed value; 503 when the artefact is missing or stale |
| **D4** | user records (runs, audit, dashboard, export) stay gated on a store | deferred: nothing behind sign-in works today, so nothing regresses |

`D3` is the one that makes the deployed suite honest: health would then assert something the product
actually depends on, instead of a database it never had.

---

# Part 5 — the database is gone (2026-11-18)

Operator instruction: remove the database dependency, take finance data from Yahoo, and remove
sign-in and dashboard. Done, and the result is smaller than the port in Part 3.

## What was removed

| removed | why |
|---|---|
| `app/(en)/sign-in`, `app/(en)/dashboard` | not reachable from the site's own navigation; they gated a page nobody could open |
| `app/(en)/api/auth/[...nextauth]`, `api/billing/checkout`, `api/webhooks/stripe`, `api/audit`, `api/export/report` | every one of them existed to read or write user records; with no store they were dead routes |
| `lib/auth/**` (640 lines of vendored Auth.js), `lib/billing/stripe.ts`, `lib/db/repositories/**`, `lib/benchmarks/compute.ts`, `components/SessionProvider.tsx`, `middleware.ts` | the code behind those routes |
| dependencies `next-auth`, `@auth/core`, `bcryptjs`, `stripe` | nothing imports them |
| `etl/compute-benchmarks.ts` and its script | it computed benchmarks from the database that is now unused |

`lib/db/client.ts`, `lib/db/schema.ts` and `lib/db/migrate.ts` remain for the **offline** ETL only;
nothing in `app/` or `components/` imports them, which `tsc --noEmit` verifies.

## What replaced it

`yahoo-finance2` (v4.0.6) performs the crumb/cookie handshake that Yahoo's `v7/quote` and
`v10/quoteSummary` endpoints require — the ones that answer **401** to a plain fetch. Measured against
`AAPL`: marketCap 5.11e12, trailingPE 39.19, priceToSales 10.68, enterpriseToEbitda 30.04,
enterpriseToRevenue 10.76, currentPrice 351.91.

- `/public-companies` — live multiples per vertical, with the vendor's own values and `—` where it
  returns nothing. No cached table, no invented cell.
- `/benchmarks` — medians of P/E, P/S and EV/EBITDA per vertical **with the sample size stated**; a
  metric a company does not report is excluded rather than counted as zero.
- `/api/health` — probes the market-data dependency and returns 200/503 with the reason and latency.
  It no longer reports a database this application never had.

## What this costs, stated

Every page that shows market data now depends on Yahoo answering. The pages say so, with the
retrieval time and any unresolved symbols; when the source is down they show nothing rather than a
stale figure. A user-record feature — saved runs, exports, an account — is no longer possible, because
it needs the store that was removed. That is the trade the instruction makes.

## Sequencing, measured 2026-11-18

The ALB split **is applied** (verified against the live origin, not the 2026-11-17 notes):

```
GET  /api/health        503 {"status":"degraded","version":"1.0.0","db_status":…}  ← the pre-change
                              Next route (bad by design); the pin replaces it with the dependency probe
GET  /api/auth/session  200                                                        ← the app, not Python
POST /mcp               200 initialize
POST /api/calculate     200
GET  /mcp               200   ← the OLD Python image answers GET with 200 instead of 405
```

So a web-only pin would deploy correctly and then fail `verify` on the `GET /mcp` assertion, for a
reason no change in this repository can fix.

**And the chain cannot bootstrap itself.** `pin-digest` refuses to pin while the newest completed
scheduled `e2e-deployed` run on `main` is a failure, and both are: runs `44212898428` (2026-11-18) and
`44089080711` (2026-11-17), red because `/api/health` answers 503 and `GET /mcp` answers 200 on the
deployed build — the pre-existing defects this change removes. That is the gate working, and it means
the **first** pin is a human `workflow_dispatch` of `deploy-digest.yml` carrying both digests, not an
auto-merge. That dispatch must also be opened by `simonmak-ascent`: the same commit carries the
`container.json` corrections, which makes it a manifest change rather than a digest-only pin, so
`guard` falls through to the human allowlist and a bot-authored commit is refused. (Two distinct new
digests *are* accepted by `check_manifest_pin.py`; this commit changes `notes` and `dataClass` too,
which is why it does not take that path. Merging the human PR is an equivalent route to dispatching,
since the merge is itself a push touching `container.json`.)

**And the chain does not resume until O3 lands.** Without `DEPLOY_TOKEN`, `pin-digest` cannot open or
merge the pin PR, and a `GITHUB_TOKEN` merge would not fire the `push` that deploys. The manual
dispatch above is the delivery; unattended delivery begins when the token is provisioned. **The first pin must move both images**: the web image
from the automatic build and `sv-py:src-ee0ff7b` for `startup-valuation-api` and
`-calculate`. Two distinct new digests in one commit is the case `check_manifest_pin.py` accepts.
That single commit also carries the `container.json` corrections — the stale `AUTH_SECRET` note and
`dataClass: "RDS"`, which is no longer true of any container here.

Also deferred, and recorded here because a deferral that lives only in a summary is lost at the next
build: `api/calculate.py` still emits `audit_status: "skipped"` and the SDK still declares
`audit_id?`/`audit_status`. The field is truthful (the badge says "No audit trail") but it should be
removed end-to-end when the Python image is next built, since its only possible value is the absence
of the feature.

## The health path is now the Python containers' liveness — a decision, not an accident

`container.json:36,60` declare `/api/health` as the probe for `startup-valuation-api` (8021, `/mcp`)
and `-calculate` (8020), and that path is served by the **web** container. Since this change it
reports the market-data dependency, so a Yahoo outage now marks both Python containers unhealthy and
fails a web-only rollout's `verify`.

Under the previous database probe those containers were permanently 503, so this is an improvement —
but the coupling is now load-bearing where it previously could not be trusted, and it is recorded
here as a decision rather than left to emerge. If the coupling is unwanted, the fix is a `/api/live`
that reports only process liveness, with `/api/health` staying truthful about the dependency; that is
a separate change with its own review, not a patch to this one.
