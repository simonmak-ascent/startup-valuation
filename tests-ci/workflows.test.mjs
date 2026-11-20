import { readFileSync, readdirSync, existsSync, mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { test } from "node:test";
import assert from "node:assert/strict";

// The delivery chain encodes its invariants across every workflow file, with the file list derived
// from the directory rather than written down.
// actionlint validates syntax and action names; it cannot know that a job needs a scope, that a
// guard must gate the steps below it, or that two files must agree. Every invariant here
// corresponds to a defect that was actually present in this branch:
//
//   * a guard job with `permissions: {}` that called the API and could never pass
//   * a callee pinned at a commit that does not exist
//   * a superseded build that skipped one step and still pinned
//   * production health read from the wrong workflow, so a red rollout did not stop the chain
//   * a tamper exemption that trusted the filename instead of proving a digest-only change
//   * a `container.json`-derived matrix interpolated into shell
//   * a fleet-wide pointer published by a fan-out whose entries disagree on the digest
//
// A check that has never been seen to fail is not evidence, so every invariant must also carry a
// fixture that breaks it: the last test asserts each one reports its own mutation.

const W = ".github/workflows";
// Derived, never listed. The hand-maintained list WAS the defect: a workflow added after the list
// was written escaped the pinning invariant and every `.ALL` invariant with the suite green. Sorted
// so a failure message does not reorder between runs.
const FILES = readdirSync(W)
  .filter((f) => /\.ya?ml$/.test(f))
  .sort();
const read = (f) => readFileSync(`${W}/${f}`, "utf8");

/**
 * Whole-line comments removed. Without this a check matches the prose that *describes* the rule
 * and passes after the rule itself was deleted — which is how three of these defects survived a
 * first review.
 */
const code = (text) =>
  text
    .split("\n")
    .filter((l) => !/^\s*#/.test(l))
    .join("\n");

/** The lines of one job (2-space key under `jobs:`), or "" if the job is absent. */
function jobBlock(text, job) {
  const lines = text.split("\n");
  const start = lines.findIndex((l) => new RegExp(`^  ${job}:\\s*$`).test(l));
  if (start < 0) return "";
  const out = [];
  for (let i = start + 1; i < lines.length; i++) {
    if (/^  [A-Za-z0-9_-]+:\s*$/.test(lines[i])) break;
    out.push(lines[i]);
  }
  return out.join("\n");
}

/** Every `run:` body — block scalars and inline one-liners — so a check sees the shell itself. */
function runBodies(text) {
  const lines = text.split("\n");
  const blocks = [];
  for (let i = 0; i < lines.length; i++) {
    const m = lines[i].match(/^(\s*)(?:-\s+)?run:\s*[|>]\s*$/);
    if (m) {
      const indent = m[1].length;
      const body = [];
      for (let j = i + 1; j < lines.length; j++) {
        const l = lines[j];
        if (l.trim() === "") continue;
        if (l.match(/^\s*/)[0].length <= indent) break;
        body.push(l);
      }
      blocks.push(body.join("\n"));
      continue;
    }
    // `run: echo "${{ steps.x.outputs.y }}" > file` — an inline command is shell source too, and
    // ignoring it left a live `steps.*` interpolation uncovered while the suite reported green.
    const inline = lines[i].match(/^(\s*)(?:-\s+)?run:\s+(?!\s)(.+)$/);
    if (inline && !/^\s*#/.test(lines[i])) blocks.push(inline[2]);
  }
  return blocks;
}

/** Entries of a YAML list under `key:` (e.g. paths-ignore). */
function listUnder(text, key) {
  const lines = text.split("\n");
  const at = lines.findIndex((l) => new RegExp(`^\\s*${key}:\\s*$`).test(l));
  if (at < 0) return [];
  const indent = lines[at].match(/^\s*/)[0].length;
  const out = [];
  for (let i = at + 1; i < lines.length; i++) {
    const l = lines[i];
    if (l.trim() === "") continue;
    if (l.match(/^\s*/)[0].length <= indent) break;
    out.push(l.trim().replace(/^-\s*/, "").replace(/^["']|["']$/g, ""));
  }
  return out;
}

/**
 * The report job's load-bearing properties, shared by one fixture per arm.
 *
 * One fixture per arm on purpose: a mutant that trips two of three proves only that two exist — the
 * same argument the GATE_RE fixture makes above. The `failure()` mutation is anchored to the
 * expression line, because an unanchored one lands on the prose above it (`code()` strips comments
 * for the check, but `mutate` runs on the raw text) and leaves that arm untested.
 */
function reportRecords(text) {
  const c = code(text);
  const job = jobBlock(c, "report");
  const bad = [];
  if (!/^ {2}report:/m.test(c)) bad.push("no report job — a failed rollout leaves no record");
  if (!/failure\(\)/.test(job)) bad.push("the report job does not run on failure");
  // Job-scoped: `verify` also grants issues: write, so a file-wide match proves nothing here.
  if (!/issues: write/.test(job)) bad.push("the report job cannot file an issue");
  // A job with no `needs` has no ancestor to fail, so `if: failure()` is never true — the whole fix
  // silently disabled with every other assertion still green.
  if (!/needs: \[prepare, guard, deploy, verify\]/.test(job))
    bad.push("the report job declares no needs, so if: failure() can never be true");
  if (!/^ {6}- apg-ci-04$/m.test(job))
    bad.push("the report job is not on the always-on CI node the other reporting jobs use");
  if (!/api\/health/.test(job)) bad.push("the report does not sample what the fleet is serving");
  return bad;
}

// One rule, three fixtures. A mutant that trips two arms proves only that two exist — the file's own
// note — and the third arm here is the shape the rule was widened for.
const downloadIsVerified = (_t, all) => {
  const bad = [];
  for (const [file, text] of Object.entries(all))
    for (const body of runBodies(code(text))) {
      const fetches = /\b(curl|wget)\b|\bgh release download\b/.test(body);
      const writes =
        /\s-o\s|\s-O\s|--output|--output-document|\|\s*(tar|sh|bash)\b|\bgh release download\b/.test(body);
      if (!(fetches && writes)) continue;
      if (/releases\/latest|download\/latest/.test(body))
        bad.push(`${file}: a download is pinned to \`latest\``);
      if (!/sha256sum\s+-c/.test(body)) bad.push(`${file}: a download is not checksum-verified`);
    }
  return bad;
};

const invariants = [
  {
    // The opposite drift to the arms below: not a rule that drifted, but files nothing calls.
    // `.github/scripts/` held two helpers whose only caller, `license.yml`, was deleted in
    // 0f7a68e — nothing noticed, because nothing asked whether a called script exists. This
    // invariant asks it of every workflow at once, so the fixture mutates a file the check does not
    // name: a mutant confined to one file would only exercise that file's read.
    name: "every python|bash|sh|node script path in a run body exists",
    file: ".ALL",
    check: (_t, all) => {
      const bad = [];
      for (const [f, text] of Object.entries(all)) {
        for (const body of runBodies(text)) {
          for (const m of body.matchAll(
            /\b(?:python3?|bash|sh|node)\s+([\w.-]+\/[\w./-]+\.(?:py|sh|mjs|js|ts))\b/g,
          )) {
            const p = m[1];
            if (!existsSync(p)) bad.push(`${f}: runs ${p}, which does not exist`);
          }
        }
      }
      return bad;
    },
    mutate: (_t, all) => ({
      ...all,
      "deploy-digest.yml": all["deploy-digest.yml"].replace(
        /(python3\s+scripts\/)[\w-]+\.py/,
        "$1does-not-exist.py",
      ),
    }),
  },
  {
    // The only thing that terminates the chain: Dockerfile.web copies with fresh mtimes, so a
    // rebuild of byte-identical source is a new digest, which would pin again.
    name: "image.yml ignores container.json, so the pin commit cannot trigger another build",
    file: "image.yml",
    check: (t) =>
      listUnder(code(t), "paths-ignore").includes("container.json")
        ? []
        : ["push.paths-ignore does not list container.json — the build/pin loop never terminates"],
    mutate: (t) => t.replace(/^\s*-\s*container\.json\s*$/m, ""),
  },
  {
    name: "deploy-digest.yml grants each job the scope its own API call and checkout need",
    file: "deploy-digest.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      if (!/permissions:\s*\n(\s+[a-z-]+:\s*\w+\s*\n)*\s+pull-requests:\s*read/.test(jobBlock(c, "guard")))
        bad.push("guard reads commits/{sha}/pulls but does not grant pull-requests: read");
      if (!/permissions:\s*\n(\s+[a-z-]+:\s*\w+\s*\n)*\s+contents:\s*read/.test(jobBlock(c, "prepare")))
        bad.push("prepare runs actions/checkout but does not grant contents: read");
      return bad;
    },
    mutate: (t) => code(t) && t.replace(/^(\s*)permissions:\n\s+contents: read\n\s+pull-requests: read$/m, "$1permissions: {}"),
  },
  {
    name: "deploy-digest.yml derives the change-set from event.before, not HEAD~1",
    file: "deploy-digest.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      if (runBodies(c).some((b) => /HEAD~1/.test(b))) bad.push("a run body compares against HEAD~1");
      if (!/BEFORE:\s*\$\{\{\s*github\.event\.before\s*\}\}/.test(c))
        bad.push("the derive step does not read github.event.before");
      return bad;
    },
    mutate: (t) =>
      t
        .replace(/BEFORE:\s*\$\{\{\s*github\.event\.before\s*\}\}/g, "BEFORE: x")
        .replace('f"{before_sha}:container.json"', '"HEAD~1:container.json"'),
  },
  {
    // A 40-hex pattern cannot tell a real commit from a deleted one; that is what let a nonexistent
    // apg-infra SHA through. This check pins the *relationship* instead: the checked-in pin must
    // carry a 40-hex SHA and an in-repo comment naming the payload it expects, so a wrong SHA is a
    // deliberate, visible edit rather than a typo that fails at dispatch.
    name: "every action in every workflow is pinned to a 40-hex commit",
    file: "publish.yml",
    check: (t) => {
      // Every file, not one: this check used to name `deploy-digest.yml` alone, and publish.yml —
      // the workflow that pushes to PyPI — kept four mutable refs (two tags and a branch) while it
      // passed. `FILES` is derived from the directory, so a new workflow is in scope the moment it
      // is added, not when someone remembers to list it.
      const bad = [];
      for (const f of FILES) {
        // The file under test is the passed text, so the fixture's mutation is what the check sees;
        // every other file is read from disk. Reading all of them would make the mutant a no-op.
        const text = f === "publish.yml" ? t : read(f);
        for (const line of code(text).split("\n")) {
          const m = line.match(/\buses:\s*([^\s#]+)/);
          if (!m || m[1].startsWith("./")) continue;
          if (!/@[0-9a-f]{40}$/.test(m[1])) bad.push(`${f}: not SHA-pinned: ${m[1]}`);
        }
      }
      return bad;
    },
    mutate: (t) => t.replace(/@[0-9a-f]{40}/, "@v1"),
  },
  {
    // `docs/**` is image content since this workflow builds the site into `public/docs`, so ignoring
    // it would leave /docs serving the previous edit until an unrelated push rebuilt the image. The
    // recipe arm below is the other thing this file must never ignore.
    name: "image.yml rebuilds on a docs-only merge, because the docs are image content",
    file: "image.yml",
    check: (t) =>
      listUnder(code(t), "paths-ignore").some((p) => p.startsWith("docs/"))
        ? ["push.paths-ignore excludes docs/**, so a docs-only merge leaves /docs stale in the image"]
        : [],
    mutate: (t) => t.replace(/^(\s*)paths-ignore:\n/m, "$1paths-ignore:\n      - 'docs/**'\n"),
  },
  {
    // Its own invariant and its own fixture: bolted onto the arm above, the only mutant injects
    // `docs/**`, so this exclusion would never be observed failing — the file's own per-arm rule.
    name: "image.yml rebuilds when the build recipe itself changes",
    file: "image.yml",
    check: (t) =>
      listUnder(code(t), "paths-ignore").some((p) => p.startsWith(".github/workflows/"))
        ? [
            "push.paths-ignore excludes .github/workflows/**, so a fix to the docs build recipe cannot reach the image",
          ]
        : [],
    mutate: (t) =>
      t.replace(/^(\s*)paths-ignore:\n/m, "$1paths-ignore:\n      - '.github/workflows/**'\n"),
  },
  {
    name: "e2e-deployed.yml pins a reporter whose output the diagnosis step can parse",
    file: "e2e-deployed.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      if (!c.includes("--test-reporter=spec"))
        bad.push("the suite runs without --test-reporter=spec, so its output is TAP, not ✖ lines");
      if (!/grep -E '\^✖ '/.test(c)) bad.push("the diagnosis step no longer parses ✖ lines");
      return bad;
    },
    mutate: (t) => t.replace(/--test-reporter=spec /g, ""),
  },
  {
    // The invariants that protect the pipeline live in tests-ci/, and the pin decision lives in
    // scripts/. If either is not a gate file, an automated author can empty the tests or edit the
    // checker in one PR and weaken a guard in the next, each PR passing guard-tamper on its own.
    name: "the delivery tests and the pin checker are gate files in both guards, identically",
    file: ".ALL",
    check: (_t, all) => {
      const bad = [];
      const classes = {};
      for (const f of ["guard-tamper.yml", "deploy-digest.yml"]) {
        const m = code(all[f] || "").match(/GATE_RE='([^']+)'/);
        if (!m) {
          bad.push(`${f}: no GATE_RE found`);
          continue;
        }
        // The literal opens with a capturing group for the whole alternation, so the first match is the
        // expression itself rather than a class; drop it before comparing.
        const found = [...m[1].matchAll(/\(([^)]+)\)/g)].map((x) => x[1])
          .filter((cls) => cls.startsWith("(") === false)
          .sort();
        classes[f] = found;
        for (const cls of ["tests-ci/", "scripts/", "deploy/", "container\\.json"]) {
          if (!found.includes(cls)) bad.push(`${f}: GATE_RE does not cover ${cls}`);
        }
      }
      // Two copies of one rule drift. Comparing the *set* of classes means a reordering is caught
      // by the equality arm alone, which the fixture below exercises without also failing coverage.
      const a = classes["guard-tamper.yml"];
      const b = classes["deploy-digest.yml"];
      if (a && b && a.join("|") !== b.join("|")) {
        bad.push("the two GATE_RE literals disagree — one guard allows what the other refuses");
      }
      return bad;
    },
    mutate: (_t, all) => ({
      ...all,
      // Add a class to one guard only: every required class is still present, so coverage passes
      // and only the equality arm can catch the drift. Removing a class — the earlier fixture —
      // trips both arms at once and therefore proves neither.
      "guard-tamper.yml": all["guard-tamper.yml"].replace(
        "(compliance\\.json)|",
        "(compliance\\.json)|(secrets/)|",
      ),
    }),
  },
  {
    // A `${{ }}` expression inside `run:` is substituted before the shell parses the line. This
    // checks the ones whose content is not constrained: dispatch inputs and step outputs (which
    // can carry manifest data). `github.actor` and secrets are excluded on purpose — a login is
    // charset-restricted and secrets are masked — so the name says what is covered.
    name: "no workflow interpolates a dispatch input or step output inside shell source",
    file: ".ALL",
    check: (_t, all) => {
      const bad = [];
      for (const [file, text] of Object.entries(all)) {
        for (const body of runBodies(code(text))) {
          if (/\$\{\{\s*(inputs|github\.event\.inputs|steps)\./.test(body))
            bad.push(`${file}: a run: body interpolates an expression into shell`);
        }
      }
      return bad;
    },
    mutate: (_t, all) => ({ ...all, "x.yml": "jobs:\n  a:\n    steps:\n      - run: |\n          echo ${{ steps.derive.outputs.matrix }}\n" }),
  },
  {
    name: "pin-digest.yml leaves no credential in the workspace and pins only container.json",
    file: "pin-digest.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      if (!/persist-credentials:\s*false/.test(c))
        bad.push("checkout persists a contents:write PAT into .git/config on a shared runner");
      for (const body of runBodies(c)) {
        for (const m of body.matchAll(/^\s*git add\s+(.+)$/gm)) {
          if (m[1].trim() !== "container.json") bad.push(`the pin commit stages ${m[1].trim()}`);
        }
      }
      return bad;
    },
    mutate: (t) => code(t).replace(/persist-credentials: false/, "persist-credentials: true"),
  },
  {
    // The superseded guard is useless if it only skips the step beneath it: `current` skipped
    // leaves `unchanged` empty, `'' != 'true'` is true, and the pin runs anyway. Every step that
    // keys off `current` must also key off `superseded`.
    name: "pin-digest.yml gates every pin step on the superseded decision",
    file: "pin-digest.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      for (const line of c.split("\n")) {
        if (!/if:.*steps\.current\.outputs\.unchanged/.test(line)) continue;
        if (!/steps\.newest\.outputs\.superseded/.test(line))
          bad.push(`a step keys off current.unchanged without superseded: ${line.trim()}`);
      }
      return bad;
    },
    mutate: (t) => t.replace(/steps\.newest\.outputs\.superseded != 'true' && /g, ""),
  },
  {
    // The post-deploy e2e is a *job* inside deploy-digest; it never appears as a run of its own.
    // Reading production health from e2e-deployed alone therefore sees an older green scheduled
    // run and pins onto a host whose last rollout failed its verification. And the search must not
    // be a bounded window: ten newer runs that skipped `verify` would hide a real failure.
    name: "pin-digest.yml reads production health from the workflow that ran the post-deploy suite",
    file: "pin-digest.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      if (!/actions\/workflows\/deploy-digest\.yml\/runs\?/.test(c))
        bad.push("production health is not read from deploy-digest's completed runs, whose verify job records the post-deploy suite");
      if (!/page=\$page/.test(c)) bad.push("the health search is not paginated, so a fixed window can hide a failure");
      if (/--limit 10[\s\S]{0,120}deploy-digest|deploy-digest[\s\S]{0,120}--limit 10/.test(c))
        bad.push("the health search still uses a bounded run list");
      return bad;
    },
    mutate: (t) => t.replace(/page=\$page/g, "x").replace(/actions\/workflows\/deploy-digest\.yml\/runs\?/g, "nothing"),
  },
  {
    // The gate must fail CLOSED. A rollout that dies before the post-deploy suite has no `verify` job
    // at all, and "no verdict" is not the same as a dry run: measured 2026-11-19, the pointer push
    // failed, `verify` was skipped, and this loop judged an older green run instead.
    name: "pin-digest.yml treats a rollout that failed without a verify job as a failure",
    file: "pin-digest.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      if (!/"\\\(\.id\) \\\(\.conclusion\)"/.test(c))
        bad.push(
          "the run list does not carry each run's own conclusion, so a failed run cannot be told from a dry run",
        );
      if (!/\$run_conclusion" != "success"/.test(c))
        bad.push("a run with no verify job is not checked against the run's own conclusion");
      if (!/run_conclusion" != "success"[\s\S]{0,400}?last="failure"/.test(c))
        bad.push("a non-success run with no verify job does not set the failed verdict");
      return bad;
    },
    mutate: (t) => t.replace(/\$run_conclusion" != "success"/, '"x" != "success"'),
  },
  {
    // This is the check that would have caught the bug the case above missed: the pairs are text, so a
    // substring match stayed green while `for entry in $ids` split them into words and put the run id
    // in `run_conclusion`.
    name: "pin-digest.yml reads each run's id and conclusion as one pair",
    file: "pin-digest.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      if (!/while read -r id run_conclusion; do/.test(c))
        bad.push(
          "the id/conclusion pairs are not read as a pair — an unquoted `for` iterates words, so run_conclusion would hold the run id",
        );
      if (/for\s+\w+\s+in\s+\$ids/.test(c)) bad.push("the run list is still iterated as words");
      // `tests-ci/health_gate_sim.py` runs the step under `sh`, so a bashism is a syntax error there
      // and the step dies with exit 2 — which is how `<<<` was caught.
      if (/<<</.test(c))
        bad.push("a here-string is a bashism; this step is executed by `sh` in the simulator");
      if (!/done <<'?EOF'?/.test(c))
        bad.push("the loop is not fed by a heredoc, so it is either a bashism or a subshell");
      return bad;
    },
    mutate: (t) => t.replace(/while read -r id run_conclusion; do/, "for entry in $ids; do"),
  },
  {
    // A reusable-workflow call is named `<caller job> / <called job>`, so the post-deploy suite
    // appears as `verify / deployed`. An equality against `verify` matched no job on any run, every
    // run read as "no verdict", and the chain pinned blind on the bootstrapping branch — the defect
    // this arm exists for. No other job name in deploy-digest.yml begins with `verify` (prepare,
    // guard, deploy (…), report), and e2e-deployed.yml declares exactly one job (`deployed`).
    //
    // Its own invariant and its own fixture on purpose: bolted onto the pair check above, the only
    // mutation broke the `while read` line instead, so this arm was never observed failing.
    name: "pin-digest.yml matches the post-deploy job by its reusable-workflow name",
    file: "pin-digest.yml",
    check: (t) => {
      const c = code(t);
      // Bound to the jobs selector, not the bare token: a stray `startswith("verify")` elsewhere in
      // the file would satisfy a substring match while the selector went back to equality.
      if (!/\.jobs\[\]\s*\|\s*select\(\(\.name \| startswith\("verify"\)\)/.test(c))
        return [
          "the verify job is matched by equality, but a reusable-workflow job is named `verify / deployed`",
        ];
      return [];
    },
    mutate: (t) => t.replace('select((.name | startswith("verify"))', 'select(.name == "verify")'),
  },
  {
    // `verify` is skipped when `deploy` fails, so without this job a failed rollout leaves nothing but
    // a red run: no issue, no digest list, no next step. Measured 2026-11-19.
    name: "deploy-digest.yml records a failed rollout (the failure gate itself)",
    file: "deploy-digest.yml",
    check: reportRecords,
    mutate: (t) => t.replace("(failure() || cancelled())", "false"),
  },
  {
    name: "deploy-digest.yml records a failed rollout (its needs list)",
    file: "deploy-digest.yml",
    check: reportRecords,
    mutate: (t) => t.replace(/ {4}needs: \[prepare, guard, deploy, verify\]\n/, ""),
  },
  {
    name: "deploy-digest.yml records a failed rollout (it may file an issue)",
    file: "deploy-digest.yml",
    check: reportRecords,
    mutate: (t) => t.replace(/ {6}issues: write\n/, ""),
  },
  {
    // "container.json changed" is not "a digest changed": ports, probes, run settings and the image
    // repository all live in that file, and a line match cannot tie a digest to a container — a swap
    // between two containers passed it. The decision is a program, and the program is unit-tested.
    name: "deploy-digest.yml decides a container.json change with the checked program, not a line match",
    file: "deploy-digest.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      if (!/python3 scripts\/check_manifest_pin\.py/.test(c))
        bad.push("the guard does not call scripts/check_manifest_pin.py");
      if (!existsSync("scripts/check_manifest_pin.py")) bad.push("scripts/check_manifest_pin.py is missing");
      if (!existsSync("tests-ci/test_manifest_pin.py")) bad.push("the checker has no unit test");
      if (!/manifest change; human check follows/.test(c))
        bad.push("a manifest change must fall through to the human branch, not exit 1");
      if (!/HUMANS:/.test(c)) bad.push("no human allowlist for non-pin gate changes");
      return bad;
    },
    mutate: (t) => t.replace("python3 scripts/check_manifest_pin.py", "true"),
  },
  {
    // One pointer tag per container. The uniform-digest gate was correct for the old single
    // `:desired` tag — two containers on two digests would have raced it — but with
    // `:desired-<container>` it suppressed the whole publish instead, which on a multi-digest run
    // suppressed the per-container tags themselves, i.e. the exact case they exist for.
    //
    // The legacy repo-wide tag's safety did not move into this workflow: the vendored rollout.sh
    // publishes it only when the manifest names one digest for that repository, which is a fact
    // about the manifest and is checked where the manifest is read.
    name: "deploy-digest.yml publishes the pointer on every rollout, without a uniform-digest gate",
    file: "deploy-digest.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      if (!/PUBLISH_POINTER:.*github\.event_name == 'push' \|\| inputs\.publish_pointer/.test(c))
        bad.push("the pointer is not published on a push");
      if (!/\[ "\$PUBLISH_POINTER" = "true" \] && args\+=\(--publish-pointer\)/.test(c))
        bad.push("the rollout is not told to publish a pointer");
      return bad;
    },
    mutate: (t) => t.replace(/PUBLISH_POINTER: \$\{\{[^}]*\}\}/, "PUBLISH_POINTER: false"),
  },
  {
    // The historical defect, with its own fixture: a re-added uniform-digest gate keeps the push
    // predicate intact, so it passes every arm of the invariant above and is caught only here.
    name: "deploy-digest.yml does not gate the pointer on the uniform-digest flag",
    file: "deploy-digest.yml",
    check: (t) =>
      /needs\.prepare\.outputs\.pointer/.test(code(t))
        ? [
            "the pointer publish is gated on the uniform-digest flag again — with one tag per container that suppresses the multi-digest case the tags exist for",
          ]
        : [],
    mutate: (t) =>
      t.replace(
        /PUBLISH_POINTER: \$\{\{ github\.event_name == 'push' \|\| inputs\.publish_pointer \}\}/,
        "PUBLISH_POINTER: ${{ (github.event_name == 'push' || inputs.publish_pointer) && needs.prepare.outputs.pointer == 'true' }}",
      ),
  },
  {
    // `pin-digest` takes the FIRST job whose name begins with `verify`, because a reusable-workflow
    // call appears as `<caller job> / <called job>`. That is unambiguous only while the called
    // workflow declares one job: a second would make `[0]` whichever the API listed first, and a red
    // sibling could be masked while the pin proceeded.
    name: "e2e-deployed.yml declares one job, so the `verify / <job>` match is unambiguous",
    file: "e2e-deployed.yml",
    check: (t) => {
      const lines = code(t).split("\n");
      const at = lines.findIndex((l) => /^jobs:\s*$/.test(l));
      const jobs = lines
        .slice(at + 1)
        .map((l) => l.match(/^ {2}([A-Za-z0-9_-]+):\s*$/))
        .filter(Boolean)
        .map((m) => m[1]);
      return jobs.length === 1
        ? []
        : [
            `the called workflow declares ${jobs.length} jobs (${jobs.join(", ")}); pin-digest takes [0] of the verify* match and would mask a red sibling`,
          ];
    },
    mutate: (t) => t.replace(/^jobs:\s*$/m, "jobs:\n  second:\n    runs-on: ubuntu-latest"),
  },
  {
    // The rollout moved from a SHA-pinned private reusable workflow into this repository, so the
    // safety path is now code the deploying commit can change. This asserts the inline job still
    // carries it: a digest gate against this repo's manifest, the vendored rollout, and the two
    // flags that make the name and the fleet pointer correct.
    name: "deploy-digest.yml keeps the rollout's safety path inline, not behind a uses:",
    file: "deploy-digest.yml",
    check: (t) => {
      const c = code(t);
      const job = jobBlock(c, "deploy");
      const bad = [];
      if (/^\s+uses:/m.test(job)) bad.push("the deploy job calls a reusable workflow instead of running inline");
      // Presence is not behaviour: `includes("container.json")` stayed green over a gate whose
      // final line had been rewritten to `raise SystemExit(0)`, and over one whose comparator was
      // inverted. Assert the comparison and the failure, and the flags in the form they are used.
      if (!/json\.load\(open\("container\.json"\)\)/.test(job))
        bad.push("the digest gate no longer reads container.json");
      if (!/if pinned != digest:/.test(job))
        bad.push("the digest gate no longer compares the pin with the requested digest");
      if (!/raise SystemExit\(1 if bad else 0\)/.test(job))
        bad.push("the digest gate no longer fails the step on a mismatch");
      // Invoking it, not merely chmod-ing it. Deleting the call leaves `chmod +x …` and the string,
      // so the job exits 0 with nothing rolled out; the post-deploy e2e then passes because the old
      // image answers the contract, and the chain pins again on that "health".
      if (!/deploy\/container\/rollout\.sh "\$\{args\[@\]\}"/.test(job))
        bad.push("the deploy job does not run the vendored rollout");
      if (!/args\+=\(--docker-name "\$DOCKER_NAME"\)/.test(job))
        bad.push("the container name is no longer passed to the rollout");
      // With its guard, not just the flag: the flag is the operator's opt-out (`publish_pointer:
      // false`), and an unconditional `args+=(--publish-pointer)` would ignore it.
      if (!/\[\s*"\$PUBLISH_POINTER"\s*=\s*"true"\s*\]\s*&&\s*args\+=\(--publish-pointer\)/.test(job))
        bad.push("the fleet pointer is no longer passed to the rollout");
      if (!/\[\s*"\$DRY_RUN"\s*=\s*"true"\s*\]\s*&&\s*args\+=\(--dry-run\)/.test(job))
        bad.push("--dry-run is no longer gated, so a dry run would replace production containers");
      return bad;
    },
    // Every occurrence: the path appears in both the `chmod` and the invocation, and replacing one
    // left the other to satisfy the check.
    mutate: (t) =>
      code(t)
        .replaceAll("deploy/container/rollout.sh", "somewhere/else.sh")
        .replace("if pinned != digest:", "if pinned == digest:"),
  },
  {
    name: "guard-tamper.yml runs on every PR, so it can be a required check",
    file: "guard-tamper.yml",
    check: (t) => {
      const head = code(t).split("\n").slice(0, code(t).split("\n").findIndex((l) => /^jobs:/.test(l)));
      return head.some((l) => /^\s*paths:/.test(l))
        ? ["guard-tamper is path-filtered and cannot be a required check"]
        : [];
    },
    mutate: (t) => t.replace(/^on:$/m, "on:\n  paths: [x]"),
  },
  {
    name: "every locally called workflow exists and declares workflow_call",
    file: ".ALL",
    check: (_t, all) => {
      const bad = [];
      for (const [file, text] of Object.entries(all)) {
        for (const m of code(text).matchAll(/uses:\s*\.\/\.github\/workflows\/([^\s@]+)/g)) {
          const target = m[1];
          if (!existsSync(`${W}/${target}`)) {
            bad.push(`${file} calls ${target}, which does not exist`);
            continue;
          }
          if (!/workflow_call:/.test(readFileSync(`${W}/${target}`, "utf8")))
            bad.push(`${W}/${target} does not declare workflow_call`);
        }
      }
      return bad;
    },
    mutate: (_t, all) => ({ ...all, "x.yml": "jobs:\n  a:\n    uses: ./.github/workflows/nope.yml\n" }),
  },
  {
    // A runner is a shared box with a dedicated unprivileged user — `gha` on apg-ci-04 has no sudo
    // rule at all. A step that escalates therefore works only on a registration that happens to run
    // privileged, which is why the same commit failed and succeeded on different days for a step
    // that only needed to put a binary somewhere it could be found.
    name: "no workflow escalates privilege in a run body",
    file: ".ALL",
    check: (_t, all) => {
      const bad = [];
      for (const [file, text] of Object.entries(all))
        for (const body of runBodies(code(text)))
          if (/\bsudo\b/.test(body)) bad.push(`${file}: a run body invokes sudo`);
      return bad;
    },
    mutate: (_t, all) => ({ ...all, "ci.yml": `${all["ci.yml"]}\n      - run: sudo true\n` }),
  },
  {
    // Fetching a remote binary is a supply-chain decision. One without a checksum is a decision made
    // by the network; one pinned to `latest` is a decision made by whoever published upstream that
    // day. The registry install was both, and the sudo failure was hiding it.
    //
    // "Download" means a curl that writes a file or pipes into an archiver or a shell — not every
    // curl. `deploy-digest.yml` polls our own `/api/health` with curl, and that is not a fetch of
    // code to execute.
    name: "every downloaded binary is checksum-verified",
    file: ".ALL",
    check: downloadIsVerified,
    mutate: (_t, all) => ({
      ...all,
      // Only the checksums, so the `latest` arm below is not also tripped here.
      "mcp-registry.yml": all["mcp-registry.yml"].replace(/^.*sha256sum -c -.*\n/gm, ""),
    }),
  },
  {
    name: "no download is pinned to `latest`",
    file: ".ALL",
    check: downloadIsVerified,
    mutate: (_t, all) => ({
      ...all,
      "mcp-registry.yml": all["mcp-registry.yml"].replace(
        "releases/download/${MCP_PUBLISHER_VERSION}/",
        "releases/latest/download/",
      ),
    }),
  },
  {
    // The shape the rule was widened for: before this fixture existed, a body with no `curl` in it
    // was skipped entirely, so `wget -O` and `gh release download` were unreachable code.
    name: "a wget download is held to the same rule as a curl one",
    file: ".ALL",
    check: downloadIsVerified,
    mutate: (_t, all) => ({
      ...all,
      "x.yml": "jobs:\n  a:\n    steps:\n      - run: |\n          wget -O f.tgz https://example.com/f.tgz\n",
    }),
  },
  {
    // `pip install build twine` was unpinned in both the gate and the publisher, so they resolved
    // different versions and CI validated an artefact with a twine the release would never use.
    // `requirements/publish.txt` is the only source of those tools now.
    name: "no workflow names build or twine as a pip requirement outside the lock",
    file: ".ALL",
    check: (_t, all) => {
      const bad = [];
      for (const [file, text] of Object.entries(all))
        for (const line of code(text).split("\n")) {
          if (!/pip install/.test(line)) continue;
          if (!/\b(build|twine)\b/.test(line)) continue;
          if (/requirements\/publish\.txt/.test(line)) continue;
          bad.push(`${file}: installs build/twine outside the lock — ${line.trim().slice(0, 60)}`);
        }
      return bad;
    },
    mutate: (_t, all) => ({
      ...all,
      "ci.yml": all["ci.yml"].replace(
        '--require-hashes --target "$PWD/.build-libs" -r requirements/publish.txt',
        '"build>=1.2" "twine>=7"',
      ),
    }),
  },
];

const all = Object.fromEntries(
  FILES.filter((f) => existsSync(`${W}/${f}`)).map((f) => [f, read(f)]),
);

for (const inv of invariants) {
  test(inv.name, () => {
    const found = inv.file === ".ALL" ? inv.check("", all) : inv.check(read(inv.file), all);
    assert.deepEqual(found, [], found.join("\n"));
  });
}

// Every invariant must be able to fail. A fixture that does not trip its own check means the check
// is decorative — it would have stayed green through the defect it was written for.
for (const inv of invariants) {
  test(`fails on a known-bad fixture: ${inv.name}`, () => {
    assert.equal(typeof inv.mutate, "function", "this invariant has no known-bad fixture");
    if (inv.file === ".ALL") {
      const mutated = inv.mutate("", all);
      assert.notDeepEqual(inv.check("", mutated), [], "the check passed a known-bad fixture");
      return;
    }
    const broken = inv.mutate(read(inv.file), all);
    assert.notEqual(broken, read(inv.file), "the fixture did not change the file — nothing was tested");
    assert.notDeepEqual(inv.check(broken, all), [], "the check passed a known-bad fixture");
  });
}

// Negative mutations are not enough for the pin guard. Two earlier versions passed every mutation
// test while refusing every legitimate pin, and while accepting a swap between containers. These
// assertions run the real checker over real fixtures.
test("the pin checker accepts a digest transition and refuses everything else", () => {
  const dir = mkdtempSync(join(tmpdir(), "sv-pin-"));
  const hex = (c) => c.repeat(64);
  const repo = "ghcr.io/simonmak-ascent/startup-valuation";
  const base = (over = {}) => ({
    containers: [
      { name: "web", image: `${repo}@sha256:${over.web ?? hex("a")}`, port: 3110 },
      { name: "api", image: `${repo}@sha256:${over.api ?? hex("a")}`, port: 8021 },
    ],
  });
  const check = (oldManifest, newManifest) => {
    writeFileSync(join(dir, "old.json"), JSON.stringify(oldManifest));
    writeFileSync(join(dir, "new.json"), JSON.stringify(newManifest));
    return spawnSync("python3", ["scripts/check_manifest_pin.py", join(dir, "old.json"), join(dir, "new.json")],
                     { encoding: "utf8" });
  };

  const ok = check(base(), base({ web: hex("b"), api: hex("b") }));
  assert.equal(ok.status, 0, `a real digest pin was refused: ${ok.stderr}`);
  assert.match(ok.stdout, /digest-only/);

  const port = check(base(), { ...base({ web: hex("b") }), containers: [
    { name: "web", image: `${repo}@sha256:${hex("b")}`, port: 3111 },
    { name: "api", image: `${repo}@sha256:${hex("a")}`, port: 8021 },
  ] });
  assert.equal(port.status, 1, "a port change must not be treated as a pin");
  assert.match(port.stderr, /port/);

  // The swap a line match accepted: both containers change image, one repository, every other
  // field identical — and production would run the api image in the web container.
  const swap = check(base({ web: hex("a"), api: hex("b") }), base({ web: hex("b"), api: hex("a") }));
  assert.equal(swap.status, 1, "a swap between containers must be refused");
  assert.match(swap.stderr, /different digests|unchanged/);

  rmSync(dir, { recursive: true, force: true });
});
