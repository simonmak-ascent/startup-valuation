from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "scripts/check_manifest_pin.py"
HEX_A = "a" * 64
HEX_B = "b" * 64
HEX_C = "c" * 64
WEB = "ghcr.io/simonmak-ascent/startup-valuation"


def manifest(web=HEX_A, api=HEX_A, calc=HEX_A, web_port=3110) -> dict:
    """Three containers, with the images the fleet actually runs."""
    return {
        "containers": [
            {"name": "startup-valuation", "image": f"{WEB}@sha256:{web}", "port": web_port},
            {"name": "startup-valuation-api", "image": f"{WEB}@sha256:{api}", "port": 8021},
            {"name": "startup-valuation-calculate", "image": f"{WEB}@sha256:{calc}", "port": 8020},
        ]
    }


def run(tmp_path: Path, old: dict, new: dict) -> subprocess.CompletedProcess:
    o, n = tmp_path / "old.json", tmp_path / "new.json"
    o.write_text(json.dumps(old))
    n.write_text(json.dumps(new))
    return subprocess.run([sys.executable, str(CHECKER), str(o), str(n)], capture_output=True, text=True)


def test_digest_only_pin_is_accepted(tmp_path):
    r = run(tmp_path, manifest(), manifest(api=HEX_B, calc=HEX_B))
    assert r.returncode == 0, r.stderr
    assert "digest-only" in r.stdout


def test_a_port_change_is_a_manifest_change(tmp_path):
    r = run(tmp_path, manifest(), manifest(web=HEX_B, web_port=3111))
    assert r.returncode == 1
    assert "port" in r.stderr and "manifest" in r.stderr


def test_swapping_two_containers_digests_is_refused(tmp_path):
    # The swap the line-oriented guard accepted: every changed line is an image line, one repository,
    # and every per-container field looks unchanged — but the web container adopts the api's digest
    # and the api adopts the web's, so production runs the wrong image per role.
    old = manifest(web=HEX_A, api=HEX_B, calc=HEX_B)
    new = manifest(web=HEX_B, api=HEX_A, calc=HEX_B)
    r = run(tmp_path, old, new)
    assert r.returncode == 1
    assert "different digests" in r.stderr


def test_a_repository_move_is_refused(tmp_path):
    new = manifest(api=HEX_B)
    new["containers"][1]["image"] = f"ghcr.io/attacker/img@sha256:{HEX_B}"
    r = run(tmp_path, manifest(), new)
    assert r.returncode == 1
    assert "repository moved" in r.stderr


def test_a_tag_is_not_a_digest(tmp_path):
    new = manifest()
    new["containers"][1]["image"] = f"{WEB}:latest"
    r = run(tmp_path, manifest(), new)
    assert r.returncode == 1
    assert "not ghcr.io/<repo>@sha256" in r.stderr


def test_an_unchanged_manifest_is_refused(tmp_path):
    r = run(tmp_path, manifest(), manifest())
    assert r.returncode == 1
    assert "unchanged" in r.stderr


def test_adding_a_container_is_a_manifest_change(tmp_path):
    new = manifest()
    new["containers"].append({"name": "extra", "image": f"{WEB}@sha256:{HEX_B}", "port": 9999})
    r = run(tmp_path, manifest(), new)
    assert r.returncode == 1
    assert "container set changed" in r.stderr


def test_a_non_container_change_is_a_manifest_change(tmp_path):
    new = manifest()
    new["containers"][0]["health"] = {"proto": "http", "path": "/api/health"}
    r = run(tmp_path, manifest(), new)
    assert r.returncode == 1
    assert "'health' changed" in r.stderr


def test_usage_error_exits_two(tmp_path):
    r = subprocess.run([sys.executable, str(CHECKER)], capture_output=True, text=True)
    assert r.returncode == 2


def test_two_containers_moving_to_two_new_digests_is_accepted(tmp_path):
    # The web image and the Python image are pinned together in one commit; `deploy-digest.yml`
    # builds one matrix entry per container for exactly this case. A "one new digest" rule refused
    # it, so this is the fixture that keeps the rule honest.
    old = manifest(web=HEX_A, api=HEX_A, calc=HEX_A)
    new = manifest(web=HEX_B, api=HEX_C, calc=HEX_C)
    r = run(tmp_path, old, new)
    assert r.returncode == 0, r.stderr
    assert "digest-only" in r.stdout


def test_a_container_adopting_a_siblings_digest_is_refused(tmp_path):
    # One-sided adoption: only the web container changes, onto the digest the api already ran.
    # `new_digests` had length one, so a "one new digest" rule accepted it — and production would
    # run the calculate image in the web container. Nothing about the repository or the other
    # fields distinguishes it; only the sibling's previous digest does.
    old = manifest(web=HEX_A, api=HEX_C, calc=HEX_C)
    new = manifest(web=HEX_C, api=HEX_C, calc=HEX_C)
    r = run(tmp_path, old, new)
    assert r.returncode == 1
    assert "adopts digest" in r.stderr


def test_a_tag_plus_digest_reference_is_still_same_repository(tmp_path):
    # `ghcr.io/x/y:tag@sha256:…` is a valid pin form; the tag must not be read as part of the repo.
    new = manifest(api=HEX_B)
    new["containers"][1]["image"] = f"{WEB}:v2@sha256:{HEX_B}"
    r = run(tmp_path, manifest(), new)
    assert r.returncode == 0, r.stderr


def test_a_duplicate_container_name_is_refused(tmp_path):
    new = manifest()
    new["containers"].append({"name": "startup-valuation", "image": f"{WEB}@sha256:{HEX_B}", "port": 3110})
    r = run(tmp_path, manifest(), new)
    assert r.returncode == 1
    assert "twice" in r.stderr


def test_all_containers_converging_on_one_new_digest_is_refused(tmp_path):
    # The same outcome as adoption, by another route: every container moves, onto one digest none
    # of them held. Production would run one image for three roles. The legitimate shared-digest
    # case is api+calc, which already shared 362d06fd… before moving together.
    old = manifest(web=HEX_A, api=HEX_B, calc=HEX_B)
    new = manifest(web=HEX_C, api=HEX_C, calc=HEX_C)
    r = run(tmp_path, old, new)
    assert r.returncode == 1
    assert "converge" in r.stderr


def test_a_group_that_already_shared_a_digest_can_move_together(tmp_path):
    # api and calc have always shared one digest (container.json:29,53); moving them together is
    # the normal Python-image pin, and the web container is untouched.
    old = manifest(web=HEX_A, api=HEX_B, calc=HEX_B)
    new = manifest(web=HEX_A, api=HEX_C, calc=HEX_C)
    r = run(tmp_path, old, new)
    assert r.returncode == 0, r.stderr


def test_the_web_only_pin_the_automation_actually_makes_is_accepted(tmp_path):
    # `pin-digest.yml` moves the web container and nothing else, and the fleet's shape is
    # web=1a789dec…, api=calc=362d06fd…. Every other fixture here starts with all containers on one
    # digest, so the one move the chain makes was not a case — a false refusal in the convergence
    # rule would have stalled the automation with nothing to blame.
    old = manifest(web=HEX_A, api=HEX_B, calc=HEX_B)
    new = manifest(web=HEX_C, api=HEX_B, calc=HEX_B)
    r = run(tmp_path, old, new)
    assert r.returncode == 0, r.stderr
    assert "digest-only" in r.stdout
