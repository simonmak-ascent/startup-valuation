#!/usr/bin/env python3
"""Decide whether two container.json revisions differ only in image digests.

Called by `deploy-digest.yml`'s provenance guard and by `guard-tamper.yml`, and unit-tested in
`tests-ci/test_manifest_pin.py`. It exists because the shell it replaces could not express the rule:

* line-matching proved the *file* consisted of image lines, not that a *container* kept its own
  image. Swapping two containers' digests produced two valid image lines, one repository, and a
  guard that exited 0 — deploying the calculate image in the web container.
* ports, health probes and run settings live in the same file, so "every changed line is an image"
  was a proxy for "nothing else moved". Parsing states it directly.

Exit 0 only for a digest-only transition:
  - the same set of container names, in any order
  - every field except `image` byte-identical per container
  - each changed `image` is `ghcr.io/<repo>@sha256:<64 hex>`
  - that repository is the same one the container used before (a pin moves a digest, not an image)
  - at least one image actually changed
Exit 1 otherwise, with the reason on stderr. Exit 2 for a usage or parse error.

    python3 scripts/check_manifest_pin.py old.json new.json
"""

from __future__ import annotations

import json
import re
import sys

IMAGE = re.compile(r"^ghcr\.io/(?P<repo>[^:@]+(?:/[^:@]+)*)(?::(?P<tag>[^@]*))?@(?P<digest>sha256:[0-9a-f]{64})$")


def digest_only(old: dict, new: dict) -> tuple[bool, str]:
    """(True, summary) for a digest-only transition, (False, reason) otherwise."""
    try:
        old_list, new_list = old["containers"], new["containers"]
        old_c = {c["name"]: c for c in old_list}
        new_c = {c["name"]: c for c in new_list}
    except (KeyError, TypeError) as exc:
        return False, f"container.json does not have the expected shape: {exc}"

    # Two entries with one name collapse in a dict, so a manifest that declares a container twice
    # would pass every comparison below while publishing two conflicting definitions.
    for label, items in (("previous", old_list), ("new", new_list)):
        names = [c.get("name") for c in items]
        if len(names) != len(set(names)):
            return False, f"the {label} manifest declares a container name twice — a manifest change"

    if set(old_c) != set(new_c):
        added = sorted(set(new_c) - set(old_c))
        removed = sorted(set(old_c) - set(new_c))
        return False, f"container set changed (added {added}, removed {removed}) — a manifest change"

    moved = []
    for name, after in new_c.items():
        before = old_c[name]
        for key in set(before) | set(after):
            if key == "image":
                continue
            if before.get(key) != after.get(key):
                return False, f"{name}: '{key}' changed — a manifest change, not a digest pin"

        old_image, new_image = before.get("image"), after.get("image")
        if old_image == new_image:
            continue
        old_m, new_m = IMAGE.match(old_image or ""), IMAGE.match(new_image or "")
        if not new_m:
            return False, f"{name}: '{new_image}' is not ghcr.io/<repo>@sha256:<64 hex>"
        if not old_m:
            return False, f"{name}: previous image '{old_image}' was not a digest reference"
        if old_m["repo"] != new_m["repo"]:
            return False, f"{name}: image repository moved {old_m['repo']} → {new_m['repo']}"
        moved.append(f"{name}:{new_m['digest'][7:19]}")

    if not moved:
        return False, "container.json is unchanged — nothing to deploy"

    # A pin moves a container onto a digest that nothing else in this manifest already runs.
    # Comparing the repository cannot see a swap — both containers keep it, and every per-container
    # field is unchanged — so the only evidence is the digest a sibling already held. Two containers
    # moving onto two *new* digests is legitimate: the web image and the Python image are pinned
    # together. A container adopting a sibling's digest is not: that is the web container running
    # the calculate image.
    for name, after in new_c.items():
        image = after.get("image")
        if image == old_c[name].get("image"):
            continue
        holders = sorted(n for n, c in old_c.items() if c.get("image") == image and n != name)
        if holders:
            return False, (
                f"{name}: adopts digest {image.rsplit('@', 1)[-1][7:19]} already held by "
                f"{', '.join(holders)} — different digests are legitimate only when each is new"
            )

    # Convergence: several containers ending on one digest they all newly adopted is the same
    # outcome by another route — production running one image for three roles. A set of containers
    # may share a digest only if that same set already shared one, which is what a two-image pin
    # looks like: api and calc both held 362d06fd… and move together, so their old images agree.
    by_digest: dict[str, list[str]] = {}
    for name, after in new_c.items():
        by_digest.setdefault(after.get("image"), []).append(name)
    for digest, members in by_digest.items():
        if len(members) < 2:
            continue
        if all(new_c[m].get("image") == old_c[m].get("image") for m in members):
            continue  # unchanged group; not this pin's business
        old_images = {old_c[m].get("image") for m in members}
        if len(old_images) > 1:
            return False, (
                f"{', '.join(sorted(members))} converge on one digest but ran different images "
                f"before — different digests per container are legitimate only when each stays its own"
            )

    return True, "digest-only: " + ", ".join(sorted(moved))


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[-1], file=sys.stderr)
        return 2
    try:
        with open(argv[1]) as fh:
            old = json.load(fh)
        with open(argv[2]) as fh:
            new = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"cannot read a manifest: {exc}", file=sys.stderr)
        return 2

    ok, detail = digest_only(old, new)
    print(detail, file=sys.stdout if ok else sys.stderr)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
