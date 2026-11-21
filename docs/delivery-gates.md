# Delivery gates — the pipeline every change must complete

This repository's delivery contract, and the mechanism that enforces each stage. A change is
**merged**, not delivered, until stage 5 passes; "merged" is not a synonym for "live", and this
document exists because three pull requests were merged on 2026-11-17 while production still served
a build from 2026-10-29.

## The five stages

| # | stage | gate that enforces it | how you know it passed |
|---|---|---|---|
| 1 | **commit** | `review-gate` plugin | a `reviewer` returned `REVIEW-VERDICT: ship` over the bytes being committed |
| 2 | **push** | same gate binds the verdict to the pushed bytes | the branch is on the remote |
| 3 | **merge to main** | branch protection: `pr-required` + required checks `test (3.10/3.11/3.12)`, `web`, `docs`; `release-gate` requires the commit to *be* the merge commit of a merged PR | the PR shows `MERGED`, and the push-to-main run is green |
| 4 | **deploy** | **automatic**: a push to `main` touching `container.json` runs `deploy-digest.yml` inline against `deploy/container/` (a pinned copy of apg-infra's payload): main-only `guard`, digest must equal the pin | the rollout job succeeded and the container reports the pinned digest |
| 5 | **e2e** | **automatic**: `e2e-deployed.yml`, called by the deploy workflow's `verify` job | **`tests-deployed/` passed against the live origin** |

## How it runs without being asked

```
push to main (source)
  └─ image.yml          builds Dockerfile.web on apg-ecs-01, publishes the digest as an artefact
       └─ pin-digest.yml  writes that digest into container.json, opens the pin PR, arms auto-merge
            └─ pin PR merges itself   (no required human approval; the five checks are the gate)
                 └─ push to main (container.json only)
                      ├─ deploy-digest.yml  rolls out the containers whose digest changed
                      │    └─ verify job   calls e2e-deployed.yml against the live origin
                      ├─ release-gate.yml   the pin commit also came through a PR — it did
                      └─ image.yml          skipped: container.json is in paths-ignore
```

That last line is what stops the loop. A pin commit changes only `container.json`, so it rebuilds
nothing, and the chain terminates after exactly one rollout and one e2e run.

The **approval** is the pin PR merging with the check suite green — nobody has to press a button,
and nobody can deploy an image the repository does not declare. Be precise about what that buys:
the pin PR is authored and merged by the `DEPLOY_TOKEN` account's own user (never `github-actions[bot]`, which `guard-tamper` would refuse as an automated author), so "it came through a pull request" no
longer means "a person approved it" on that path. What it still means is that the image is one this
repository built from a reviewed commit, and that the check suite ran. The human decision in the
chain is the one at stage 3 that put the *source* on `main`. `workflow_dispatch` survives for two
narrow uses: re-rolling an existing pin deliberately, and `dry_run`.

## The rule for plans and todos

Every task in a plan, and every item in a working todo list, carries the five stages explicitly.
A task is not done because the code exists or the PR merged:

```
T1.2 path guards — commit ✅ · push ✅ · merge ✅ (b32d136) · deploy ⛔ OI-40 · e2e ⛔ (5 failing)
```

The `⛔` names the blocker, not "pending". An item with no deploy and no e2e row is a task that has
not started delivery, whatever its code says. The session todo list uses this form too.

## Why each stage is where it is

- **Review before commit, not before merge.** The verdict binds to the bytes; any edit after it voids
  it. Reviewing at merge time lets unreviewed bytes reach `main`.
- **`release-gate` on push to `main`.** Branch protection can be bypassed by an admin or a token with
  the right scope, and a direct push leaves no PR to review. This check fails the run when the pushed
  commit is not the merge commit of a merged pull request.
- **The deploy proves provenance itself.** `release-gate` *reports* a direct push; it runs in
  parallel with the deploy and nothing waits for it. So `deploy-digest.yml`'s `guard` job repeats the
  provenance query before any rollout: a direct push that changed `container.json` is refused by the
  thing that would have acted on it, not merely flagged by a neighbour.
- **`pin-digest` merges only its own pull request.** `gh pr list --head <name>` matches on branch
  name alone, so a stable branch name would let anyone who can open a PR register a colliding
  `attacker:chore/pin-web-digest → main` and have the bot arm auto-merge on *that* — pinning an
  older, known-vulnerable digest. The branch name now includes the source SHA, and before merging the
  job asserts the PR is same-repository, on that branch, against `main`, owned by this repository.
- **The digest artefact is validated.** Anything that is not `sha256:` + 64 hex characters stops the
  job before it reaches `container.json`; the artefact is a boundary only if its content is checked.
- **Actions are pinned to full SHAs** on the build and deploy path. `image.yml` — the job that
  produces the artefact everything else trusts, holding `packages: write` on a Docker-socket node —
  ran `actions/checkout@v7` and `actions/upload-artifact@v4` as movable tags, which is the opposite
  of this document's own rule. `publish.yml` still uses tags; it is the release path, not this chain.
- **The deploy proves the digest, not the tag.** `deploy-digest.yml` refuses a digest that is not the
  one `container.json` pins, so the pin is the reviewed artefact and a rollout cannot ship something
  nobody approved.
- **e2e after the rollout, against the origin.** A rollout reporting success is not the product
  working. The suite asserts the contract, and the same suite runs twice daily so the host cannot
  drift back into a failing state unnoticed.

## What is *not* enforced, and would need an operator

- **A merge that never deploys** — no longer possible for the web container: the chain above runs
  unattended. It remains possible for `sv-api`/`sv-calc`, which have no reproducible image yet
  (OI-40), so a pin of those digests still needs an operator.
- **The ALB path rules.** They live on the broker (`/root/edge/hosts`, `publish.py`), outside this
  repository. Until they match the delivery contract's path table, `/mcp` and `/api/*` cannot be
  delivered however green the pipeline is.
- **Rebuilding the Python containers.** OI-40; the recipe is written, the build runs on a node.

## Current state (2026-11-17)

Reported in the form this document requires. `⛔` names the blocker.

| change | commit | push | merge | deploy | e2e |
|---|---|---|---|---|---|
| app-surface fixes (21 findings) | ✅ | ✅ | ✅ `b32d136` | ⛔ OI-40: Python image unrebuildable | ⛔ 5 of 8 failing |
| digest-rollout caller + health | ✅ | ✅ | ✅ `6fbaf27` | ⛔ nothing to roll out yet | ⛔ |
| MCP endpoint + e2e gate | ✅ | ✅ | ✅ `33f16cd` | ⛔ web rollout pending; `/mcp` needs the ALB split | ⛔ |
| web image pinned to `1a789dec…` | in this PR | — | — | — | — |

The web container is the one stage-4 step this repository can complete alone: `image.yml` builds
`Dockerfile.web` on `apg-ecs-01`, this PR pins the digest it produced, and `deploy-digest.yml`
rolls it out. Everything in the `sv-api`/`sv-calc` containers waits on OI-40, and `/mcp` waits on
the ALB split regardless.

### What stops the automatic chain today, and why it is not "fixed" in code

The chain is wired, and it will **not** run unattended until a bot credential exists. Measured on the
repository, not assumed:

```
gh api repos/…/actions/permissions/workflow
  default_workflow_permissions     : read
  can_approve_pull_request_reviews : false     ← Actions cannot open a pull request at all
secrets                            : PYPI_API_TOKEN (no bot token)
```

Three GitHub behaviours combine, and each fails quietly or confusingly:

1. With `can_approve_pull_request_reviews: false`, `gh pr create` under `GITHUB_TOKEN` is refused.
2. A pull request opened by `GITHUB_TOKEN` has its check runs held for approval — nobody is there
   to click, so the required checks never report.
3. **A merge performed with `GITHUB_TOKEN` does not trigger `push` workflows.** Even if 1 and 2
   were solved, the pin would merge and `deploy-digest.yml` and `release-gate.yml` would never run:
   the chain would build, pin, merge, and then do nothing — the exact silent no-op this document
   exists to prevent.

So `pin-digest.yml` refuses to run without `secrets.DEPLOY_TOKEN` and says why. **Provisioning is
one fine-grained PAT** scoped to this repository with `contents: write` and `pull-requests: write`,
stored as `DEPLOY_TOKEN`. Its merges are attributed to a user, which restores the `push` event. Until
then, stage 4 is a dispatch and stage 5 runs on the schedule.

An alternative with a shorter token lifetime is a GitHub App installation token
(`actions/create-github-app-token`), at the cost of managing an App. Either way the decision is a
credential one, not a code one.

## Self-healing loop
The loop is: **e2e red → diagnose → fix → commit → push → merge → deploy → e2e green.** It has three
stages; two are live, and the third is written down because it cannot authenticate yet.

```
e2e-deployed fails
  └─ stage A  diagnosis issue (LIVE)   one open issue per failing set, updated in place
       └─ stage B  agent fix (NEEDS PROVISIONING)
              └─ stage C  the ordinary pipeline: review → commit → push → PR → checks → merge
                   └─ deploy-digest → e2e-deployed        (already automatic, see above)
```

### Stage A — diagnosis (live)

`e2e-deployed.yml` files or updates an issue labelled `e2e-failure`, keyed by a fingerprint of the
failing assertion set, so a breakage recurring every six hours produces one ticket rather than twelve.
It names the origin, the run, the failing assertions and the three usual causes in order — routing,
digest, not-deployed. That is the input a fix needs, produced by the machine.

### Stage B — the fix (blocked on credentials, deliberately not faked)

Measured on ecs-04, the runner node: `opencode` **is** installed (`/usr/local/bin/opencode`), `gh` is
installed, Node is v24 — but **no model credential is present** (`ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`, `DEEPSEEK_API_KEY` all unset), and the only agent auth store is under `/root`, which
the `gha` runner user cannot read. The bwrap sandbox helper is also absent there.

An auto-fix workflow would therefore start, fail to authenticate, and become exactly the dead path
this repository has spent the session removing. Provisioning needed before stage B exists:

1. a model credential in the **runner user's** environment, not root's;
2. an agent auth store readable by that user, or the provider variables exported;
3. the sandbox helper on the node, so the agent runs with a read-only system and no reach into the
   credential stores;
4. a repository variable `AUTO_FIX=on` as the kill switch — absent means the loop stays at stage A.

### Stage C — the controls that make stage B safe

- **`guard-tamper.yml`** — gate files are `tests-deployed/**`, `tests-ci/**`, `scripts/**`, `compliance.json`,
  `docs/delivery-gates.md`, `.github/workflows/**` and `container.json`. The test is a **deny-by-default
  allowlist of human logins**, not a `*[bot]` name pattern: a machine account holding a PAT appears as
  an ordinary user, and a name pattern is exactly what that defeats. A bot-authored commit anywhere in
  the PR also refuses it. A fix may change the product; it may never change the definition of done.
  The same rule is enforced a second time in `deploy-digest`'s `guard`, against the merge commit that
  is about to reach production — a pull-request report can be bypassed by a push after it ran.
  A digest-only change to `container.json` is exempt because it is the approval itself; the guard
  proves that by diffing the manifest, not by trusting the filename.
- **Bounded attempts.** Two per failure fingerprint, then the issue gets a comment and the loop stops
  for a human. Unbounded retries against a broken host burn quota and still ship nothing.
- **No self-merge exemption.** A fix goes through review → PR → required checks like any other change.
- **The diagnosis is not the fix.** A green result that came from editing the expectation is caught
  by `guard-tamper`, not by hope.

### What the loop must never do

Widen its own permissions. When a fix needs the ALB split or a Python image rebuild (OI-40), it stops
at the issue and names the operator action — those are not repository changes, and a green pipeline
over a broken host is worse than a red one.
