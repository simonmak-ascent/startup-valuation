# Vendored deploy payload — why this is a copy, and how to update it

These five files are **copies** of `apg-infra/deploy/container/`. `VERSION` names
`6157e6bbefb5eccafa411b5b55074140d576bb1f` — the commit that last *changed* `deploy/container/`, and
the same SHA the estate's own callee pinned as its payload. A later `apg-infra` commit (`48dd8bad…`,
a docs change) is where the copy was physically taken from; naming it here instead would make drift
detection a `git log` over the wrong range.

## Why a copy exists

This repository is **public**; `apg-infra` is **private**. A public repository may not call a
reusable workflow that lives in a private one — GitHub refuses at run creation, producing a run with
**zero jobs** and the workflow file's path as its name, and no error message that says so. Measured
2026-11-18: the rollout this repository's `deploy-digest.yml` asked for never started, twice, before
the cause was found.

The estate's rule is that deploy logic lives in one place. That rule assumed every caller could reach
it. Until `apg-infra` is public or this repository is private, the honest options are a copy or no
deploy at all. This is the copy, and it is pinned by commit so it cannot move under a running deploy.

## What is vendored, and what is not

| file | role |
|---|---|
| `rollout.sh` | pull by digest, probe on a spare port, swap, health-check, roll back on failure |
| `container-spec.py` | read `container.json` for a container's port, image, `cmd`, `docker_name` |
| `converge.sh`, `converge-all.sh` | the node-side reconciler, kept for parity; not invoked by CI |
| `check.sh` | the contract check on a repository's manifest — **vendored for parity, not runnable here**: it requires `deploy.kind == "container"` and a `deploy.converge` key, while this repository declares `kind: "workflow"` and neither. Running it against this checkout reports two failures about a contract this repo does not claim; do not "fix" `compliance.json` to satisfy a checker that is not in force. |

Not vendored: the systemd units, `install.sh` and `bootstrap.sh`, which install the reconciler on a
node — that is operator provisioning, not CI.

## Updating

```bash
# from an apg-infra checkout, at the commit that changed deploy/container/
cp deploy/container/{rollout.sh,converge.sh,converge-all.sh,container-spec.py,check.sh} \
   <startup-valuation>/deploy/container/
```

Then update `deploy/container/VERSION` (the machine-readable pin `check.sh` reads) and this file's
prose, and confirm two things, because both have bitten:

1. `scripts/check_manifest_pin.py` and `container.json` still agree with what `rollout.sh` reads.
2. `container-spec.py` still emits `SPEC_DOCKER_NAME` — the rollout prefers `--docker-name`, and the
   workflow passes the manifest's `docker_name`, so a container name change must reach both.

## The drift risks this copy creates, named rather than assumed away

1. **A fix landing upstream and not here.** `apg-infra/deploy/container/README.md` is the upstream
   record; diff against it when either side moves.
2. **The YAML half is duplicated too, and the update recipe does not mention it.** The digest gate and
   the pull-retry loop in `.github/workflows/deploy-digest.yml` are copies of `container-cd.yml`'s
   `The digest must be the one this repository declares` and its pull loop. A change to that workflow
   upstream is silently missed by a recipe that copies only `deploy/container/`.
3. **Two of the five files are unchecked and unused.** `converge.sh` and `converge-all.sh` are kept for
   parity and are not invoked by CI; `check.sh` compares only `rollout.sh` and `container-spec.py`. The
   two files that never run are the two nothing verifies.
4. **The pin is only as good as `VERSION`.** Nothing in a public repository can compare these bytes to
   a private checkout, so drift here is detectable only if someone diffs against an apg-infra clone.
   `deploy/` is a gate file in both guards, which makes a change *reviewable* by a human; it does not
   make it *correct*.
