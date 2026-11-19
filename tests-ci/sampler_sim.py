#!/usr/bin/env python3
"""Exercise the digest sampler in deploy-digest.yml against stub bodies.

The sampler tells seven states apart, and every one of them has been the wrong label at least once
while this was written: `(no answer)` covered a dead node, a missing key and a body that was not
JSON; and "build predates IMAGE_DIGEST" was attached to `"image":null`, which means the build *has*
the field and was started without the variable.

So the loop is extracted from the workflow and executed — not grepped — with a stub `curl` on PATH.
A reviewer cannot see this by reading the YAML, and the report it feeds is the artefact written to
explain a broken rollout.

    python3 tests-ci/sampler_sim.py

Exit 0 when every case matches, 1 otherwise.
"""

from __future__ import annotations

import os
import pathlib
import subprocess
import sys
import tempfile

WF = pathlib.Path(__file__).resolve().parents[1] / ".github/workflows/deploy-digest.yml"

CASES = [
    # (label, body, curl exit code, expected stdout)
    ("digest", '{"status":"ok","image":"sha256:abc"}', 0, "sha256:abc"),
    ("non-digest", '{"status":"ok","image":"latest"}', 0, "(image set to 'latest', which is not a digest)"),
    (
        "null",
        '{"status":"ok","image":null}',
        0,
        "(image null: the rollout started this container without IMAGE_DIGEST)",
    ),
    (
        "no key",
        '{"status":"ok","version":"1.0.2","methods":45}',
        0,
        "(no image key: this backend does not report a digest)",
    ),
    ("not a string", '{"status":"ok","image":123}', 0, "(image present but not a digest string)"),
    ("not json", "<html>502 Bad Gateway</html>", 0, "(unparseable body: not JSON)"),
    ("no answer", "", 7, "(no answer)"),
    ("pretty-printed", '{\n  "status": "ok",\n  "image": "sha256:def"\n}', 0, "sha256:def"),
]


def sampler_script() -> str:
    lines = WF.read_text().splitlines()
    start = next(i for i, line in enumerate(lines) if "for _ in 1 2 3 4 5 6 7 8 9 10" in line)
    indent = len(lines[start]) - len(lines[start].lstrip())
    # Take the whole loop, `for` through `done`: a body without its `for` makes the `continue` in the
    # empty-body branch an error rather than a loop jump, so execution falls through and prints twice.
    try:
        end_i = next(
            i
            for i in range(start + 1, len(lines))
            if lines[i].strip().startswith("done")
            and (len(lines[i]) - len(lines[i].lstrip())) == indent
        )
    except StopIteration:
        raise SystemExit(
            f"sampler_sim: no 'done' at the same indent as the loop that starts on line {start + 1} "
            f"of {WF} — the extraction cannot tell where the sampler ends"
        )
    block = [line[indent:] if len(line) > indent else "" for line in lines[start : end_i + 1]]
    text = "\n".join(block).replace("1 2 3 4 5 6 7 8 9 10", "1")
    text = text.replace("done | sort | uniq -c", "done")
    return "set -eu\nORIGIN=https://example.test\n" + text


def main() -> int:
    script = sampler_script()
    tmp = pathlib.Path(tempfile.mkdtemp())
    (tmp / "step.sh").write_text(script)

    failures = 0
    for label, body, code, expected in CASES:
        stub = tmp / "curl"
        emit = f"cat <<'BODY'\n{body}\nBODY\n" if body else ""
        stub.write_text(f"#!/bin/sh\n{emit}exit {code}\n")
        stub.chmod(0o755)
        env = dict(os.environ, PATH=f"{tmp}:{os.environ['PATH']}")
        r = subprocess.run(["bash", str(tmp / "step.sh")], env=env, capture_output=True, text=True)
        out = "\n".join(line for line in r.stdout.splitlines() if line.strip())
        ok = r.returncode == 0 and out == expected
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  {label:14} {out or '(empty)'}")
        if not ok:
            print(f"      expected: {expected!r}")
            if r.returncode:
                print(f"      exit {r.returncode}: {r.stderr.strip()[:160]}")

    print()
    print("all cases behaved as required" if not failures else f"{failures} case(s) wrong")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
