# Plan context — capability audit of the live deployment

Written 2026-11-17 by the orchestrator, before the `plan` agent was dispatched.
Every claim below carries a locator: a `file:line`, a command, or a measured response.
Nothing here is inferred from a document alone.

## 1 · What the estate claims

`AGENTS.md:16-17` — one host serves four things:

```
https://startup-valuation.ascent-partners.com
  /                Next.js site (route groups (en), (zh), (hk))
  /api             Streamable HTTP MCP
  /api/calculate   calculator REST
  /docs            mkdocs site
```

`AGENTS.md:93-106` — three containers, each with a pinned digest, rolled out by
`image.yml` → pin digest in `container.json` → `deploy-digest.yml`.
`compliance.json` (added in `498922f`) instead declares `deploy.workflow = publish.yml`,
which is the **PyPI release** workflow (`AGENTS.md:123-124`). The contract and the repo
disagree about how a change reaches production.

## 2 · What the live deployment actually does (measured 2026-11-17 06:28-06:35Z)

Base `https://startup-valuation.ascent-partners.com`.

| probe | result | verdict |
|---|---|---|
| `GET /` | 200, 43,922 B, 0.08 s | ok |
| `GET /zh` | 200, 43,992 B | ok |
| `GET /hk` | 200, 43,998 B | ok |
| `GET /en` | 404 | by design — `hreflang` maps `en-GB` to `/`; switcher links only `/zh`, `/hk` |
| `GET /docs` | 404 | **declared mkdocs site absent** |
| `GET /docs/` | 308 → `/docs` → 404 | redirect loop into a 404 |
| `GET /api` | 404 `text/html` — Next.js 404 page | **declared MCP endpoint absent** |
| `POST /api` (MCP `initialize`) | Next.js HTML | **MCP handshake fails** |
| `GET /api/calculate` | `{"status":"ok","server":"startup-valuation","tools":14}` | that is `api/index.py:56-67`, **not** the calculator |
| `POST /api/calculate {"method":"scorecard","params":{…}}` | `{"jsonrpc":"2.0","error":{"code":-32601,"message":"Unknown method: scorecard"}}`, HTTP 200 | calculator contract unreachable |
| `GET /api/health` | `{"status":"ok","version":"1.0.2","methods":45,"available":[…]}` | that is `api/calculate.py:170-182`, **not** `app/(en)/api/health/route.ts` |
| `GET /api/auth/session`, `/api/auth/providers`, `/api/ai`, `/api/audit`, `/api/export/report`, `/api/billing/checkout`, `/api/webhooks/stripe`, `/api/playground` | **all** 200 + the same calculator blob | every Next API route is shadowed |
| `POST /api/webhooks/stripe` (unsigned) | `{"error":"VALIDATION_ERROR","message":"method is required"}`, 400 | Stripe webhook never reaches its handler |
| `HEAD /api/calculate`, `HEAD /api/health` | **501** `text/html` | no `do_HEAD` on either handler |
| `GET /sitemap.xml` | 7 URLs | 4 of them 404, one is `/api/health`, none is `/zh` or `/hk` |
| `GET /methods/scorecard` | 200 | ok |
| `GET /methods/black-scholes`, `/methods/dcf`, `/methods/saas-metrics`, `/methods` | 404 | advertised in the sitemap |

### 1 — CRITICAL · the whole Next.js API surface is unreachable in production

`middleware.ts` protects `/dashboard` and `/api/export`; `app/(en)/api/` holds auth
(`[...nextauth]`), billing (`checkout`), `webhooks/stripe`, `ai`, `audit`, `export/report`,
`health`, `playground` — eight routes. Measured: **every one of them is answered by
`api/calculate.py`**, not by Next.

Consequences, in order of damage:
- Stripe webhooks get HTTP 400 from a Python handler. Delivery is marked failed; no
  subscription state is ever written.
- Auth.js endpoints (`/api/auth/*`) return a JSON status blob with 200. Sign-in cannot work,
  and it fails *silently* — a 200 looks like success to a client.
- The dashboard/playground/AI advisor/export all resolve to the same blob.

### 2 — CRITICAL · the cause: routing and handler discipline are both wrong

Two independent faults compound:

a. **Ingress.** `container.json` declares `startup-valuation-api` (port 8021,
   `api.index:handler`) and `startup-valuation-calculate` (port 8020, `api.calculate:handler`,
   note: *"declared at priority 23 for /api/calculate"*). Measured behaviour is the inverse:
   `/api/calculate` answers from `api.index`, while every other `/api/*` answers from
   `api.calculate`. The publish declaration and the running routes disagree.

b. **Handlers ignore the path.** `api/index.py:56` signature is
   `handle_request(http_method, _path, body_raw)` and `_path` is never read;
   `api/calculate.py:159` is identical. So whichever container a path lands on answers it —
   any GET returns 200 with a status body. This is what converts a routing bug into silent
   success across eight endpoints instead of a visible 404.

### 3 — HIGH · sitemap advertises dead pages and a control endpoint

`sitemap.xml` (7 entries): `/`, `/api/health`, `/methods/{scorecard,black-scholes,dcf,saas-metrics,vc-method}`.
Only `/methods/scorecard` returns 200. `/api/health` is an API endpoint in a sitemap.
`/zh` and `/hk` serve 200 and are declared in `hreflang` but are not in the sitemap. No `lastmod`.

### 4 — MEDIUM · both Python handlers return 501 to HEAD

`BaseHTTPRequestHandler` with `do_GET`/`do_POST`/`do_OPTIONS` only
(`api/index.py:148-166`, `api/calculate.py:202-227`). Anything that probes with HEAD —
uptime monitors, some CDN origin checks — reads 501 as an outage.

### 5 — MEDIUM · three different version strings from one deployment

| source | value |
|---|---|
| `pyproject.toml` / `startup_valuation.__version__` | 2.1.4 (measured: `python3 -c 'import startup_valuation'`) |
| live MCP `initialize` → `serverInfo.version` | 2.1.4 |
| live `/api/health` and `/api/calculate` GET | **1.0.2** — `api/calculate.py:19` `LIBRARY_VERSION` |
| `app/(en)/api/health/route.ts` | hardcodes `version: "1.0.2"` and `tools: 46` |
| live calculator `methods` count | **45**, not 46 |

`AGENTS.md:153-154` acknowledges the `LIBRARY_VERSION` drift and tells the reader to treat it
as stale. That is a doc working around a defect; the fix is one source of truth.

### 6 — LOW · header hygiene

`x-powered-by: Next.js` is disclosed. CSP (`/` headers) allows `script-src 'unsafe-eval'` and
names `va.vercel-scripts.com`, a retired-Vercel remnant (`AGENTS.md:109-110`). HSTS,
`X-Frame-Options: DENY`, `nosniff` and `Referrer-Policy` are present and correct.

### 7 — CRITICAL · the `web` required check is flaky and `main` HEAD is red

`gh api …/branches/main/protection` → required contexts: `test (3.10)`, `test (3.11)`,
`test (3.12)`, **`web`**, `docs`; `strict: false`.

- On PR #72 the same commit `498922f` had `web` = **SUCCESS**.
- On the push-to-main run `41366298544` (2026-11-02T00:16Z) the same commit had `web` = **FAILURE**.
- The failure is at `pnpm install --no-frozen-lockfile`:

```
[WARN] Detected a pnpm v10 installation layout at PNPM_HOME. The pnpm shims at PNPM_HOME have
       been refreshed so the new version is active, but pnpm v11 expects bins in PNPM_HOME/bin.
Switching pnpm from v11.19.0 to v10.30.3...
ERROR  Worker pnpm#1 exited with code 1
##[error]Process completed with exit code 1.
```

So: a **required** check is nondeterministic, and the default branch is currently red. Two
independent faults — a v11 store left under `PNPM_HOME` while `pnpm/action-setup@v6` switches to
v10.30.3, and CI installing with `--no-frozen-lockfile` (the lockfile is not enforced at all on a
PR). Any merge this session is subject to that flake.

## 3 · Constraints on any fix

- **Ingress is not this repo.** `AGENTS.md:3-6` and `:103-106` put host rules on ecs-04 through
  `apg-infra` `publish.py` in a publishing window, and both node groups are at the 20-rule
  security-group limit (OI-25). A routing change here is an operator action. What *this* repo
  can do is stop the handlers from lying: a path guard turns 200-on-everything into honest 404s
  and makes the routing fault visible instead of silent.
- **Generated files are not hand-edited** (`AGENTS.md:28-44`): `lib/methods/*.ts` regenerates
  from `method_registry/registry.py`; `src/startup_valuation/mcp/server.py` regenerates from
  `tool_surface.py`. Any change to those must be made in the source and regenerated, or CI's
  `git diff --exit-code` gate fails.
- **Version lockstep** (`AGENTS.md:118-122`): `pyproject.toml`, `server.json` (×2),
  `__init__.__version__`, `_package_version()` in `tool_surface.py`, enforced by
  `tests/test_agent_guides.py::test_server_version_matches_pyproject`.
- **Checks**: `AGENTS.md:48` says `cs run "<cmd>"` (offload to ecs-02); the global contract says
  run in the checkout. `cs` rsyncs the worktree first, so both test the same bytes; heavy checks
  will go through `cs run` and be reported as such. Local toolchain is present and working
  (node 24.22.2, pnpm 10.30.3, python 3.12.3, pytest 9.0.2, ruff, mypy); `node_modules` is absent.
- **Delivery**: PR → `ci.yml` green → merge → digest rollout → prove on the live host. The
  `deploy.yml`→`app-cd.yml` slot path cannot run (Caddy purged, OI-38).

## 4 · Open questions for the plan

1. Should the two Python handlers gain a path guard (404 on a path they do not own), and what is
   the exact path each owns given the ingress is currently inverted?
2. What is the smallest correct way to make the calculator reachable and prove it, without an
   operator publishing window — or is that part genuinely `BLOCKED` on apg-infra?
3. Which of the sitemap defects are code (the generator emits dead `/methods/*` routes) and which
   are content (the pages were never built)?
4. Version: adopt `startup_valuation.__version__` as the single source in both handlers and the
   Next health route, or keep them independent?
5. Does `docs.yml` produce a `site/` that anything serves? If not, `/docs` is a decision, not a fix.

## 5 · Findings from the three read-only audits (folded in 2026-11-17)

Severity as reported, then **verified by me** where marked ✓.

### Web surface (`app/`, `lib/`, `components/`)

| # | sev | where | what | verified |
|---|---|---|---|---|
| W1 | critical | `lib/db/repositories/billing.ts:43-56` + `migrate.ts:223` | `UPSERT subscription SET …` has no `WHERE` and no id; SurrealDB treats it as an INSERT, so every Stripe event creates a row and hits `idx_subscription_stripe … UNIQUE` → 500, Stripe retries, status never persists | ✓ read both |
| W2 | high | `app/(en)/api/export/report/route.ts:136` | IDOR: `getAuditLogForRun(runId)` with no user predicate; any Pro user exports any run | ✓ read |
| W3 | high | `app/(en)/dashboard/page.tsx:70` vs `audit.ts:71`+`migrate.ts:72` | export link passes an `audit_log` id into `WHERE valuation_run = $id` (`record<valuation_run>`) → export always 404 | ✓ read |
| W4 | high | `components/CalculatorPage.tsx:54,159-190` | reads camelCase (`formulaNumber`, `libraryVersion`) from a snake_case response → audit badge dead, shows `startup-valuation@undefined` | |
| W5 | high | `app/(en)/api/ai/route.ts (deleted 2026-11-18 — this file is a snapshot, see the date above):6-23` | most expensive endpoint has no auth and no rate limit; `chatCompletion` has no timeout | |
| W6 | high | `app/(en)/api/audit/route.ts:17-18,47-60` | unauthenticated clients can write arbitrary rows into the append-only audit ledger the paid report is built from | |
| W7 | medium | `audit/route.ts:8`, `checkout/route.ts:11`, `export/report/route.ts:103` | rate limits key on the leftmost `x-forwarded-for` hop, which the client controls | |
| W8 | medium | `app/(en)/api/health/route.ts:9-14` | returns 200 when the DB is down; hardcodes `version:"1.0.2"`, `tools:46` | ✓ read |
| W9 | medium | `lib/auth/vendor/config.ts:83-105`, `lib/auth/edge-auth.ts:13-17` | no `trustHost`/`AUTH_TRUST_HOST` though it runs behind the ALB → `UntrustedHost` | |
| W10 | medium | `audit/route.ts:66-71` | DB failure returned as HTTP 200 + raw driver message | |
| W11 | medium | `components/layout/RootShell.tsx:32-40,47-55` | all three locales share one canonical pointing at `/`; nav links are root-relative; sitemap omits `/zh`,`/hk` | ✓ sitemap measured |
| W12 | medium | `app/robots.ts:11` vs `app/sitemap.ts:40` | playground lives under `/api/`, is disallowed to crawlers, yet is submitted in the sitemap and nav-linked; `"/dashboard/"` does not block `/dashboard` | |
| W13 | medium | `app/(en)/benchmarks/page.tsx:16,22` | queries `version = "latest"`; the writer stores an ISO date → page permanently empty | |
| W14 | medium | `app/(en)/methods/[slug]/page.tsx:49-54` | static page reads SurrealDB at build and swallows failure to `[]` | |
| W15 | medium | `tests-webapp/` | no test covers any API route, webhook, auth, export or repository; the 80% coverage thresholds are unreachable | |

### Python library + MCP (`src/`, `api/`)

| # | sev | where | what |
|---|---|---|---|
| P1 | critical | `mcp/tool_surface.py:454-460` + `probability.py:223-228` | `expected_value_continuous` binds `lower`/`upper`; the function takes `a`/`b` → `TypeError`, method cannot execute |
| P2 | critical | `tool_surface.py:1193-1200,1232-1239,1604-1609` | `pwerm` and `employee_option` build `Scenario` objects but index them as dicts → dead |
| P3 | high | `tool_surface.py:283-286` + `biotech.py:105-132` | `drugs` schema advertises `{name,peak_sales,probability,years_to_market}`; code needs `p_success`,`years_to_peak` → `KeyError` |
| P4 | high | `emerging.py:185-212` | `safe_conversion_cap` ignores `cap` and returns `series_a_price` |
| P5 | high | `types.py:9-18,40` | `sensitivity` is never populated by any of the 103 functions, contradicting `AGENTS.md:19-20` |
| P6 | high | `api/calculate.py:17` | reports library version **1.0.2** while the lockstep set is **2.1.4** (live-confirmed) |
| P7 | high | `saas.py:154-192` + `tool_surface.py:860-867` | NRR adds `expansion_revenue` on top of an `ending_revenue` that already contains it; step text and summary state two further formulas |
| P8 | high | `capm.py:105-111` + `tool_surface.py:146-147` | schema defaults 0.0/0.0 vs function defaults 0.05/0.03 → ~8pp silent uplift |
| P9 | high | `api/index.py:119-122`, `api/calculate.py:146-156` | no finiteness validation; `json.dumps` emits bare `NaN`/`Infinity` → 200 with unparseable JSON |
| P10 | high | `api/calculate.py:134-144,186-196` | all input errors surface as 500; `params:null` raises out of `do_POST`; `_json.loads` unguarded |
| P11 | medium | `advanced.py:259-264` | Monte Carlo truncates the sample to positive values, biasing the mean up; `NaN` when all draws are ≤0 |
| P12 | medium | `advanced.py:111-192` | `binomial_tree` claims American and never tests early exercise; neither binomial function validates inputs |
| P13 | medium | `tool_surface.py:121-122,236-238,851-857,939-941,1442-1446` | descriptions contradict the code: NPV t=0 vs t=1, ARR monthly×12, density divisor, "rounded to 2 decimals" |
| P14 | medium | `api/index.py:34,56-67` | claims `transport: streamable-http` but returns `application/json` on GET; spec requires SSE or 405 |
| P15 | medium | `tests/test_mcp_surface.py` | no test binds every tool's `args` keys to the target signature — which is why P1-P3 shipped |

### Cross-cutting, from the live probe and CI

| # | sev | finding |
|---|---|---|
| X1 | critical | every Next `/api/*` route shadowed by the Python handler (see §2) |
| X2 | critical | `/api/calculate` and `/api/*` container routing inverted vs `container.json` (see §2) |
| X3 | critical | `web` required check is flaky; `main` HEAD red (see §7) |
| X4 | high | both handlers ignore `_path` → unknown paths return 200 (see §2) |
| X5 | high | sitemap advertises 4 dead URLs + `/api/health`, omits `/zh`,`/hk` (see §3) |
| X6 | medium | `HEAD` → 501 on both Python endpoints (see §4) |
| X7 | low | `/docs` 404; `compliance.json` names `publish.yml` (PyPI) as the deploy path (see §1) |

## 6 · Scoping decision

The audit produced 37 in-repo defects plus 3 that live outside this repo. They do not all belong in
one change. The plan splits them into:

- **Phase 1 — stop lying, stop losing data.** The handler path/HEAD/NaN/version fixes, the billing
  upsert, the export IDOR, the dashboard id, the health probe, the sitemap, and the three dead MCP
  methods. Every one is either a silent-success bug or a data-integrity bug.
- **Phase 2 — correctness of published numbers.** NRR, CAPM defaults, `safe_conversion_cap`,
  Monte Carlo truncation, binomial claim, description/code drift.
- **Phase 3 — hardening and tests.** auth trust, AI rate limit, audit-ledger binding, XFF, route
  tests, the signature-binding test.
- **Out of repo / operator.** X2 (ingress rules), `/docs` hosting, and the `web` flake's root cause
  if it is runner state.
