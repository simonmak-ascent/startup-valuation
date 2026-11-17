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
- **verify:** `tests-webapp/rate-limit.test.ts` — 4 cases incl. a forged leftmost value.

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
| **Live verification of T1.7/T1.16** | operator | webhook write and sign-in proven against real SurrealDB/Stripe |

## Ordering as landed

1. Python handler discipline (`api/index.py`, `api/calculate.py`) → 2. MCP surface + tests
(`tool_surface.py`, regenerated `server.py`, `tests/test_mcp_surface.py`) → 3. version single-source
(`generate.py` + regenerated `lib/methods/index.ts`, `prompts.ts`) → 4. data integrity (`billing.ts`,
`audit.ts`, export route, dashboard) → 5. web hardening (health, sitemap, robots, rate limit, AI,
audit, auth, calculator UI, locales, benchmarks, methods) → 6. CI determinism.

Each was verified as it landed; the full gate run is at the end of the branch.
