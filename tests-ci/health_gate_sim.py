#!/usr/bin/env python3
"""Run the *actual* `newest` step body from pin-digest.yml against a stub `gh`.


The previous two rounds both shipped a shell bug that no static check caught: a regex that
rejected every valid pin, and a bounded window that hid a failure behind ten skipped runs. This
executes the step as written, with a stub `gh` on PATH, and asserts the three outcomes.

    python3 tests-ci/health_gate_sim.py
"""

import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

WF = Path(__file__).resolve().parents[1] / ".github/workflows/pin-digest.yml"


def step_body(text: str, step_id: str) -> str:
    lines = text.split("\n")
    # find `id: <step_id>`, then the next `run: |` after it, take its block, dedent
    start = next(i for i, line in enumerate(lines) if re.match(rf"\s*id:\s*{step_id}\s*$", line))
    run_at = next(i for i in range(start, len(lines)) if re.match(r"\s*run:\s*\|\s*$", lines[i]))
    indent = len(lines[run_at]) - len(lines[run_at].lstrip())
    body = []
    for line in lines[run_at + 1 :]:
        if line.strip() and (len(line) - len(line.lstrip())) <= indent:
            break
        body.append(line[indent + 2 :] if line.strip() else "")
    return textwrap.dedent("\n".join(body))


STUB = r"""#!/bin/sh
# Stub gh: SCENARIO selects the answers.
case "$*" in
  *"run list"*"e2e-deployed"*) echo "success" ;;
  *"run list"*"image"*) echo "${THIS_RUN:-112}" ;;
  *"actions/workflows/deploy-digest.yml/runs"*)
    if [ "${SCENARIO}" = "enumfail" ]; then echo "boom" >&2; exit 1; fi
    case "$*" in
      *"&page=2"*) printf '%s\n' ${PAGE2} ;;
      *)           printf '%s\n' ${PAGE1} ;;
    esac ;;
  *"run view"*)
    id=""
    for a in "$@"; do case "$a" in *[0-9]) id="$a" ;; esac; done
    if [ "${SCENARIO}" = "skipped_then_failure" ] && [ "$id" = "900" ]; then echo "failure"; else echo "skipped"; fi ;;
  *) echo "stub: unexpected gh invocation: $*" >&2; exit 1 ;;
esac
exit 0
"""

SKIPPED_SHORT = " ".join(str(i) for i in range(101, 113))  # one short page: the end of history
SKIPPED_FULL = " ".join(str(i) for i in range(101, 201))  # a full page, so page 2 is fetched

CASES = [
    (
        "skipped_then_failure",
        SKIPPED_FULL,
        "900",
        1,
        "a failure behind a full page of skipped runs must refuse",
    ),
    ("enumfail", "", "", 1, "an enumeration failure must refuse, not proceed"),
    ("healthy", SKIPPED_SHORT, "", 0, "no verify outcome anywhere is announced, not fatal"),
]


def main() -> int:
    body = step_body(WF.read_text(), "newest")
    tmp = Path(tempfile.mkdtemp())
    (tmp / "gh").write_text(STUB)
    (tmp / "gh").chmod(0o755)
    script = tmp / "step.sh"
    script.write_text("set -eu\n" + body)

    failures = 0
    for scenario, page1, page2, expect, why in CASES:
        env = {
            **os.environ,
            "PATH": f"{tmp}:{os.environ['PATH']}",
            "SCENARIO": scenario,
            "PAGE1": page1,
            "PAGE2": page2,
            "REPO": "simonmak-ascent/startup-valuation",
            "THIS_RUN": "112",
            # Actions always sets this; the step writes `superseded` into it.
            "GITHUB_OUTPUT": str(tmp / f"out-{scenario}"),
        }
        r = subprocess.run(["sh", str(script)], env=env, capture_output=True, text=True)
        ok = r.returncode == expect
        failures += 0 if ok else 1
        tail = [line for line in (r.stdout + r.stderr).splitlines() if line.strip()][-1:] or [""]
        print(f"{'PASS' if ok else 'FAIL'}  {scenario:22} exit={r.returncode} (want {expect})  {tail[0][:90]}")
        if not ok:
            print("      " + why)
    print()
    print("all cases behaved as required" if not failures else f"{failures} case(s) wrong")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
