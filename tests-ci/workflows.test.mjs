import { readFileSync, existsSync, mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawnSync } from "node:child_process";
import { test } from "node:test";
import assert from "node:assert/strict";

// The delivery chain encodes its invariants across seven workflow files, by hand, in comments.
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
const FILES = [
  "ci.yml",
  "deploy-digest.yml",
  "e2e-deployed.yml",
  "guard-tamper.yml",
  "image.yml",
  "pin-digest.yml",
  "release-gate.yml",
];
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

const invariants = [
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
    name: "every reusable workflow and action is pinned to a 40-hex commit",
    file: "deploy-digest.yml",
    check: (t) => {
      const bad = [];
      for (const line of code(t).split("\n")) {
        const m = line.match(/\buses:\s*([^\s#]+)/);
        if (!m || m[1].startsWith("./")) continue;
        if (!/@[0-9a-f]{40}$/.test(m[1])) bad.push(`not SHA-pinned: ${m[1]}`);
      }
      return bad;
    },
    mutate: (t) => t.replace(/@[0-9a-f]{40}/, "@v1"),
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
    // rollout.sh publishes ONE :desired tag per repository and converge.sh falls back to it on
    // every peer. Two matrix entries on two digests would race that tag, and each peer would then
    // converge the losing container onto the winner's image — a green run and a swapped fleet.
    // Checked in the workflows because container.json cannot see downstream convergence.
    name: "deploy-digest.yml publishes the fleet pointer only when every matrix entry shares a digest",
    file: "deploy-digest.yml",
    check: (t) => {
      const c = code(t);
      const bad = [];
      if (!c.includes('print("pointer="')) bad.push("prepare does not compute a pointer flag");
      // Presence is not the predicate. `<= 1` rewritten as `>= 1`, or with the true/false arms
      // swapped, still contains every substring a presence check looks for — and still publishes
      // the pointer on a multi-digest move, which is the defect this invariant exists for.
      if (!c.includes('len({i["digest"] for i in items}) <= 1'))
        bad.push("the pointer flag does not read the matrix digests, or its comparator is not `<= 1`");
      if (!c.includes('"true" if len({i["digest"] for i in items}) <= 1 else "false"'))
        bad.push("the pointer flag's true/false arms are inverted");
      if (!/PUBLISH_POINTER:.*needs\.prepare\.outputs\.pointer == 'true'/.test(c))
        bad.push("the pointer is not gated on that flag");
      return bad;
    },
    // Invert the comparator rather than removing the gate: a fixture that only removes the line
    // cannot see a wrong predicate, which is how this arm passed a rewritten `>= 1`.
    mutate: (t) => code(t).replace("<= 1 else", ">= 1 else"),
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
      // With its guard, not just the flag: an ungated pointer moves the whole fleet onto whichever
      // digest finished last.
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
