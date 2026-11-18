# Debug and streamlining plan — for approval

Measured 2026-11-18, after the deploy in `9c1f20a`/`6a2f08e`. Every claim below carries the command
or the file that produced it; nothing here is inferred from a README.

## Where the product stands

```
deployed HTTP suite   10 / 10        deployed GUI suite   8 / 8   (Windows Chrome over CDP)
/api/health           200            dependency.name = finance.yahoo.com
GET /mcp              405            POST /mcp initialize 200, 14 tools
/  /zh  /hk           200            /benchmarks, /public-companies 200 with live data
/dashboard /sign-in   404            /docs  404   ← the one advertised surface still missing
TTFB                  45 ms          total 50-55 ms on the heaviest pages
```

The delivery chain works end to end: merge → image → pin → rollout → e2e, with each peer rolled by
the estate's own `rollout.sh`.

## Part A — debug

Ordered by blast radius, not by effort. Each carries the command that proves it.

| # | defect | evidence | fix | verify |
|---|---|---|---|---|
| **D1** | **CI is red on the branch that landed the GUI suite** | `web` job exit 2: `deployed-gui.spec.ts(17,71): error TS2345` — the worker-fixture generic `base.extend<Record<string, never>, …>` is not assignable | `base.extend<{}, { browser: Browser }>` | `pnpm check` clean, PR checks green |
| **D2** | **Critical: unauthenticated RCE in Next.js image optimisation with SVG** | Dependabot: `next` critical, vulnerable `<= 15.5.27`, **patched 15.5.28**; installed `15.5.27` | bump `next` to 15.5.28 | `pnpm build` + `pnpm test` + deployed e2e still green; alert closes |
| **D3** | High: `next` DoS in App Router Server Actions | same alert set, also patched in 15.5.28 | covered by D2 | as D2 |
| **D4** | High: `zod` memory exhaustion — **major** bump (4.6.6, installed 3.25.76) | Dependabot, patched `4.6.6` | evaluate first: every schema is a boundary (`lib/db/validation.ts`, `lib/finance/yahoo.ts`); a major with a behavioural change is not a version-bump task | `pnpm test` + `pnpm check` + a parse of a real Yahoo payload; if incompatible, pin and record why |
| **D5** | **`/docs` 404** — the mkdocs site is built (`site/`, 6.0 MB) but `Dockerfile.web` copies only `public/` | `Dockerfile.web:36`; `ls site/index.html` exists; `/docs` → 404 | build mkdocs in the image and serve it from the app: copy `site/` to `public/docs-static/`, add `rewrites()` for `/docs/:path*` → `/docs-static/:path*` (and `/docs` → the index). `rewrites` is typed in the installed Next (`config-shared.d.ts:811`); there is no `/docs` app route today | `/docs` 200, a nav page 200, and a GUI assertion |
| **D6** | **`/zh` and `/hk` ship English chrome** — nav, footer and legal titles are hard-coded in `RootShell.tsx`; only `lib/landing.ts` is per-locale | live page under `lang="zh-Hans"` shows *Methods, Benchmarks, Public Companies, API Playground, Skills, Why Open Source, … Terms of Service* — the advisor item went with the advisor on 2026-11-18 | a `lib/chrome.ts` with `Record<Locale, …>` beside the existing landing copy — five strings do not need an i18n framework; pass the locale into `RootShell` | GUI test asserts a translated nav item per locale (today it asserts the body copy and would not catch this) |
| **D7** | *Dropped on instruction (2026-11-18): the advisor is removed, not fixed.* It answered **502** for every real query | `POST /api/ai {"query":"value a pre-revenue SaaS"}` → `502 {"error":"DEEPSEEK_API_KEY is not configured"}` | operator: the key exists in the estate's env stores; the web container's env file has only `AUTH_SECRET`/`NEXTAUTH_URL`. Same handoff class as the DB credential | — (dropped) |
| **D8** | `FI` never prices — Yahoo's payload fails the library's schema, so Fintech publishes a median over 3 | build log: `1/20 unresolved; 1 failed, first: Failed Yahoo Schema validation`; page names `FI` | investigate the payload and either map the fields we read with `validateResult: false` (and keep `num()` guards) or replace the symbol — decide from the payload, not by swapping to make the count look full | 20/20 priced, or the exclusion documented on the page |
| **D9** | MCP registry advertises `…/api` | registry `com.ascent-partners/startup-valuation` 2.1.4, `remotes[0].url = …/api` → 404; repo `server.json` says `/mcp` | republish via `mcp-registry.yml` after a version bump | registry URL ends `/mcp` |
| **D10** | Small leftovers | dead `docker_names` job output in `deploy-digest.yml`; the GUI health gate skips on any non-200 rather than only 503; `audit_status: "skipped"` in `api/calculate.py`; `docs/plan-15min.md` untracked | one commit, five lines | `actionlint`, the suite, and a Python-image rebuild for the `audit_status` removal |

## Part B — streamline the product

Not bug fixes; each removes a rough edge a user or an operator meets.

| # | change | why it matters | verify |
|---|---|---|---|
| **F1** | **One comparables model, not three copies** — `/benchmarks` and `/public-companies` each re-fetch and re-shape the same quotes, and each renders its own failure copy | two pages that disagree about "the source is down" is how the earlier empty-state defect survived a green suite | a single `getMarketSnapshot()` used by both; a test asserts they agree in both states |
| **F2** | **Hide a median computed over fewer than three companies** | a median over two is arithmetic, not a benchmark; the page currently prints `(n=2)` without comment | rows under the threshold render `—` with the count, and a test pins it |
| **F3** | **Docs in the product** (D5 is the bug; this is the feature) — search, the formula reference, and the method pages cross-linked | today the docs are a separate artefact nobody reaches | `/docs` reachable from the nav, and the GUI suite asserts one page |
| **F4** | **Localised chrome** (D6) plus the legal pages | a Chinese-language site with English navigation reads as unfinished | as D6 |
| **F5** | **Release and publish**: version lockstep now holds at 2.1.4 across five carriers; publish 2.2.0 with the `/mcp` remote and the removed database | the published package and the registry entry are the product's public face | PyPI 2.2.0 installs and its stdio server answers `initialize`; registry entry matches |
| **F6** | **A page that says what the data is**: source, retrieval time and coverage per vertical | the benchmarks page already prints a timestamp; `/public-companies` should say which symbols are covered and which are excluded | a user can answer "is this number complete?" from the page |

## Sequence

1. **D1** (CI green) → **D2/D3** (one-line bump of `next`) → re-run the deployed suite. That is one
   PR and it closes the critical.
2. **D5 + F3** (docs) and **D6 + F4** (chrome) in parallel — both are image changes, so they land
   together and roll out once.
3. **D4** (zod) as its own PR under review, because a major needs a behavioural argument.
4. **D8, F2, F6** — the data-quality group, which also wants `F1` first so there is one place to
   change.
5. **D9/F5** wait on a version bump, **D10** whenever. **D7 is dropped** — the advisor is deleted.

## What I need from you

- **Approval to bump `next` to 15.5.28** — a patch bump that closes a critical unauthenticated RCE.
- **A decision on `zod` 4**: take the major under review, or pin and record the advisory as accepted
  risk. I will not take a major silently.
- ~~The `DEEPSEEK_API_KEY` handoff~~ — withdrawn: the advisor is removed, so nothing reads that key.
- **Confirmation that `/docs` served from the app** is the shape you want, rather than a separate
  hostname — it is the smaller change and keeps one ingress.

Everything else above needs no decision; it is a defect with a verify line.
