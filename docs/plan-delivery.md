# Delivery capability plan — how a change reaches production

Companion to `docs/plan.md` (which fixed the application surface). This pass audits the
**delivery chain** and fixes what this repository owns.

## What was measured

Read from `~/git/apg-infra` (the estate authority) and this repo, 2026-11-17.

| # | finding | evidence | sev |
|---|---|---|---|
| **D1** | **The documented deploy path does not exist here.** `AGENTS.md:127` tells an agent to run `deploy-digest.yml -f container=…`, but `.github/workflows/` holds only `ci`, `docs`, `image`, `mcp-registry`, `publish`. The estate's real path is a `workflow_call` reusable — `apg-infra/.github/workflows/container-cd.yml` — whose header says *"callers are eight lines (see the header of any `.github/workflows/deploy-digest.yml`)"* | `ls .github/workflows`; `container-cd.yml:5-9` | critical |
| **D2** | **`compliance.json` declares the wrong deploy.** It names `publish.yml`, the PyPI release, which uploads a package and touches no container. Its `verify` also claims `pnpm build`, which no workflow runs | `compliance.json`; `publish.yml` trigger | critical |
| **D3** | **The Python containers cannot be rebuilt at all.** OI-40: no Dockerfile reproduces the running `sv-api`/`sv-calc` (production uses `/opt/<app>/venv`, the repo's Dockerfile uses `/app` + system pip), no env file, no recorded run command. Every handler fix — path guards, HEAD, NaN — is undeployable until this is done, and it has to be done on a node | `apg-infra/docs/open-issues.md:134-158` | critical |
| **D4** | **`/api/health` cannot fail.** The ALB probes `GET /api/health` on 8021 expecting `http_2xx`; `api/index.py` returns a static 200 blob. OI-58 names this exact target: *"answer 200 on every path … they need an application-side route that fails when the app is broken"*. The contract says `health.path` must *"return 200 only when the service can serve"* | `alb-health.py:43-47`; `container-contract.md:41`; OI-58 | high |
| **D5** | **The `web` required check is flaky for a documented, fixable reason.** `ci.yml` uses `pnpm/action-setup@v6` with no `version` and no `dest`, so it shares `~/setup-pnpm` with every other repo on the node. OI-34 suggests *"pin `version:` and set `dest: ${{ runner.temp }}`"* — **the `dest` half is wrong on this runner and breaks the job (see T4)**; only the version pin is sound. The failure log showed the collision it describes (`pnpm v11` store, `Worker pnpm#1 exited`) | OI-34; run 41366298544 | high |
| **D6** | **The manifest and the balancer disagree about health.** `container.json` declares `"proto": "tcp"` for api and calculate, so the rollout gate degrades to "container is running"; but the ALB health-checks 8021 over HTTP `/api/health`. A 500-serving app passes the rollout | `container.json`; `alb-health.py`; `container-contract.md:49` | medium |
| **D7** | **Nothing verifies a deploy.** `compliance.json` declares an `e2e` probe that no workflow runs; `app-cd.yml` used to call `scripts/audit-e2e.mjs`, which does not exist. So a rollout can succeed while the host is broken | `compliance.json`; `AGENTS.md:158-159` | medium |
| **D8** | **Doc drift in the authority file.** `AGENTS.md:127` names `-f container=` / `-f docker_name=`; `container-cd.yml` takes `containers` / `docker_names` | both files | low |
| **D9** | **A dead path is still vendored.** `.deploy/` is the Caddy-era platform (writes `/etc/caddy`); Caddy was purged 2026-10-27, so those verbs cannot run. A dead path documented as "do not use" is indistinguishable from a live one to the next agent | `.deploy/kinds/next-website.sh`; OI-38 | low |

Not in scope, deliberately: OI-40's Dockerfile (an `apg-infra/estate/<app>/` deliverable that needs a
node), and deleting `.deploy/` (a separate decision with its own risk).

## Tasks

### T1 · Add the deploy caller — **the missing eight lines**
`deploy-digest.yml` with a `workflow_dispatch` surface matching `container-cd.yml`'s inputs,
pinned to an apg-infra commit SHA (the workflow's own comment: *"a tag can be moved under you"*).
- **verify:** the workflow appears in `gh workflow list`; a dispatch with `dry_run=true` resolves the
  manifest, passes the digest gate, and prints the run command without changing production.

### T2 · Make `/api/health` prove the service can serve
`api/index.py` and `api/calculate.py`: run one cheap real computation through the same dispatch path
a client uses; 200 on success, 503 on failure. This is what the contract asks for and what OI-58
records as missing.
- **verify:** `pytest`; a handler test asserting 200 on the healthy path and 503 when the underlying
  call raises.

### T3 · Make the rollout gate real
`container.json`: api and calculate move from `"proto": "tcp"` to an HTTP probe on `/api/health`
with the production `Host` (the same path the ALB uses). `container-spec.py` and `rollout.sh`
already support it.
- **verify:** `deploy/container/container-spec.py` output for each container shows
  `PROTO=http HEALTH_PATH=/api/health`; `dry_run` rollout prints the same probe.

### T4 · Fix the `web` flake — pin the version, and do **not** set `dest`
`ci.yml`: pin `version: 10.30.3` on `pnpm/action-setup`. **Superseded:** the OI-34 note also says to
set `dest: ${{ runner.temp }}`, and doing so fails the job in 13 s — `dest` is the action's install
directory and it *destructively recreates* it, so pointing it at the runner's temp root removes the
runner's own `_runner_file_commands/add_path_<guid>`. Measured on PR #74; no repository in the estate
sets `dest`. The hazard is contained by the version pin plus `--frozen-lockfile` and the
`concurrency` group.
- **verify:** the `web` job goes green on a pull request and on the push-to-main run of the same
  commit (the run that failed on `498922f`).

### T5 · Declare the truth in `compliance.json`
`deploy.workflow` → `deploy-digest.yml`; `verify` → the gates CI actually runs (`pnpm check`,
`pnpm test`, `pytest`, `ruff`), dropping `pnpm build` which nothing runs.
- **verify:** `json.load` parses; every command in `verify` exists in `.github/workflows/`.

### T6 · Verify the deploy, don't assume it
The caller gets a second job after the rollout that polls the live host and fails the run if it does
not answer 200 — the `e2e` probe `compliance.json` declares and nothing executed.
- **verify:** `dry_run` dispatch skips it; a real dispatch runs it.

### T7 · Correct the authority file
`AGENTS.md`: the input names, and the fact that the caller now exists.
- **verify:** the command in `AGENTS.md` matches `deploy-digest.yml`'s declared inputs.

## Blocked / operator

| item | who | done looks like |
|---|---|---|
| **D3 — Python images** | operator, on a node | `estate/<app>/Dockerfile` + `build.sh` + a real env file generated from `docker inspect`; then `image.yml` can publish a digest for api/calculate and T2 can ship |
| **Ingress** | apg-infra `publish.py` window | `/api` → MCP, `/api/calculate` → calculator, other `/api/*` → web |
| **A real rollout** | operator | dispatch `deploy-digest.yml` with a digest that `container.json` pins; dry-run proves the wiring first |

## Status after implementation

| task | outcome |
|---|---|
| **T1** caller | **done** — `.github/workflows/deploy-digest.yml`, job-level `uses` pinned to apg-infra `55b77e2`, inputs mirroring `container-cd.yml`, plus `probe_url`. YAML parses; appears as `jobs: [deploy, verify]`. |
| **T2** health proves it can serve | **done** — both handlers run a real computation: the MCP handler through `call_tool` (the same dispatch a client uses), the calculator by calling `tv.present_value` directly so the probe does not consume its rate-limit budget. 200 on success, 503 on failure; `tests/test_api_handlers.py` covers both branches. |
| **T3** rollout gate | **done** — api and calculate now declare `proto: http`, `path: /api/health`, the production `Host`. Verified by running `apg-infra/deploy/container/container-spec.py`: `PROTO=http HEALTH_PATH=/api/health HEALTH_HOST=startup-valuation.ascent-partners.com` for both. |
| **T4** pnpm flake | **partly done, and the first attempt was wrong** — `version: 10.30.3` is pinned, but `dest: ${{ runner.temp }}` (which the OI-34 note suggests) **breaks the job**: the action points at the runner's temp root and fails with `Missing file at path: …/_temp/_runner_file_commands/add_path_…` (measured on PR #74, `web` red in 13 s). `dest` is now removed and the measurement recorded in `ci.yml` so nobody re-adds it. Nothing in the estate uses `dest`; every repo pins `version` only. What actually keeps this job green is `--frozen-lockfile` plus the concurrency group, which is what PR #73 ran. |
| **T5** compliance | **done** — `deploy.workflow` is `deploy-digest.yml`; `verify` is `pytest`, `ruff check .`, `pnpm check`, `pnpm test`, all of which CI runs. |
| **T6** verify the deploy | **done** — a `verify` job polls the live host after the rollout and fails the run otherwise. |
| **T7** authority file | **done locally, cannot be committed** — `AGENTS.md` is gitignored in this repo (`.gitignore:19`, "internal AI-agent config"), so the corrected command examples and the deployable-container note exist only in this checkout and reach no clone. The correction still matters for the next session *here*; it needs an owner decision to track the file or to move that text into a tracked doc. |

Test count: 185 → **200** (15 handler tests, which did not exist before — the Python API surface
had no test at all).

Still blocked, unchanged: D3 (Python images, OI-40) and the ingress rules. A dispatch of
`deploy-digest.yml` with `dry_run=true` is the safe way to prove the wiring without touching
production; a real rollout needs a digest that `container.json` pins, which means a new image from
`image.yml` first.

## Upstream findings from the security review (apg-infra, cannot be fixed here)

Both are in `apg-infra/.github/workflows/container-cd.yml` at the pinned SHA. They are recorded
here because this repository is where they will bite, and because the first real rollout should
not happen until they are decided.

**U1 · the deploy implementation is fetched unpinned.** `container-cd.yml:71-74` checks out
`simonmak-ascent/apg-infra` with **no `ref`**, so the `deploy/container/rollout.sh` that pulls,
swaps and health-checks production containers is whatever `main` is at dispatch time — despite the
caller correctly pinning the *workflow file* to a full SHA. Pinning the reusable workflow while
resolving its payload from a moving branch does not pin the thing that runs.
Suggested fix (apg-infra): `ref:` the same full SHA on that checkout, and pin `actions/checkout` too.

**U2 · the digest gate reads the dispatched ref's manifest.** `container-cd.yml:67-68` runs
`actions/checkout@v7` with no `ref:`, which defaults to the triggering ref, so a branch that pins its
own digest passes the gate that exists to prevent exactly that — bypassing the pull request that
reviews the pin.

**Mitigated from this repository:** the caller now has a `guard` job that fails unless
`GITHUB_REF == refs/heads/main`, so a branch dispatch cannot reach the deploy job from here.
That closes the bypass for this repo without editing apg-infra; U1 remains open upstream.

**Deliberately not "fixed":** the security review suggested dropping `packages: write` from the
caller's workflow-level `permissions`. That would break deploys — a reusable workflow's permissions
can only be *downgraded* by its caller, so removing the grant would strip the `:desired` tag push
`container-cd.yml` performs. The least-privilege fix applied instead is `permissions: {}` on the
`verify` job, which genuinely needs no token.

### Known limitation of the post-deploy probe

`probe_url` defaults to the web apex, and the `verify` job polls it whatever was deployed. For the
web container that is the right check. Once the Python containers are deployable (OI-40), a
dispatch of `startup-valuation-api` or `-calculate` must pass
`-f probe_url=https://startup-valuation.ascent-partners.com/api/health`, or the job will confirm the
site is up without exercising the container that changed. The per-container gate is still real:
`rollout.sh` probes each container on its declared `health.path` before the swap, so a broken
container cannot replace a working one.
