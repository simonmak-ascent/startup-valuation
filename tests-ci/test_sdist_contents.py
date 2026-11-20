"""The sdist is the deliverable; the test suites are the development process.

Measured 2026-11-20, before this check existed: `startup_valuation-2.1.4.tar.gz` carried 37 files
from `tests*/`, 38 from `docs/` and 62 from the Next.js app (`app|components|lib`) — every
`pip download --no-binary` consumer received a tarball of the whole repository. The wheel was
already clean (`packages = ["src/startup_valuation"]`); only the sdist was wrong.

The sdist is an allowlist rather than an exclude list, because an exclude list is the shape that
failed: it enumerated a handful of artefacts and shipped everything else by default.

Four arms, because each one is blind to a different defect:

* the configuration must equal the intended set — catches a widened allowlist before a build;
* `artifacts`/`force-include`/`hooks` may not appear — `artifacts` is `include` under another name;
* a tracked file inside the package must be code — catches a committed `.env` or fixture;
* the built tarball must match the tracked tree exactly — the only arm that sees what hatchling
  actually emits, and the only one that notices a tracked module dropped by an ignore pattern or an
  untracked file added from a dirty working tree.

Isolation stays on in the build because that is what a consumer does: `pip install <sdist>` builds it
in pip's own isolated environment. The backend version is no longer a variable in either direction —
`pyproject.toml` declares `requires = ["hatchling==1.33.0"]`, and the release installs that same
version by hash from `requirements/publish.txt` and builds `--no-isolation`, so this isolated
resolution and the release's resolve one backend.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tarfile

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 — the package ships tomli for exactly this
    import tomli as tomllib

ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

# The package directory, not all of `src/`: `src/wasm/` is the optional Rust crate and is not part
# of what `[tool.hatch.build.targets.wheel] packages` delivers.
PACKAGE = "src/startup_valuation/"
SHIPPED = {
    f"/{PACKAGE}",
    "/pyproject.toml",
    "/README.md",
    "/LICENSE",
    "/CHANGELOG.md",
}


def _locked_versions() -> dict[str, str]:
    """Name -> version from requirements/publish.txt, parsed rather than substring-matched."""
    pinned: dict[str, str] = {}
    for line in (ROOT / "requirements" / "publish.txt").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#") or "--hash=" not in line:
            continue
        name, _, version = line.split(" --hash=")[0].strip().partition("==")
        if version:
            pinned[name.strip().lower()] = version.strip()
    return pinned


def _sdist() -> dict:
    return CONFIG["tool"]["hatch"]["build"]["targets"]["sdist"]


def _run(args: list[str]) -> str:
    """Run `args` at the repository root, keeping stderr in the failure message.

    `check=True` with `capture_output=True` throws the reason away: the traceback then says only
    "returned non-zero exit status 1", and for the build step that reason is the whole finding.
    """
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, (
        f"{' '.join(args)} exited {result.returncode}\n--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
    )
    return result.stdout


def _tracked(prefix: str) -> set[str]:
    return {path for path in _run(["git", "ls-files", "-z", prefix]).split("\0") if path}


def test_the_sdist_ships_only_the_package() -> None:
    declared = set(_sdist()["include"])
    unexpected = sorted(declared - SHIPPED)
    missing = sorted(SHIPPED - declared)
    assert not unexpected, f"the sdist would ship development files: {unexpected}"
    assert not missing, f"the sdist would omit files a source build needs: {missing}"


def test_nothing_else_can_add_files_to_the_sdist() -> None:
    # `artifacts` is `include` under another name and is NOT affected by `exclude`; `force-include`
    # and `hooks` can add or generate files. Any of them restores a bloated sdist while the
    # allowlist above still reads as five entries. Checked on the target AND on the global
    # `[tool.hatch.build]`, because the global table is inherited by the target.
    for table in (CONFIG["tool"]["hatch"]["build"], _sdist()):
        for key in ("artifacts", "force-include", "hooks"):
            assert key not in table, f"the sdist target uses {key}, which this suite does not check"


def test_the_sdist_carries_the_files_pyproject_declares() -> None:
    # An sdist that omits its own readme or licence fails at the consumer's build, not here.
    declared = set(_sdist()["include"])
    readme = CONFIG["project"].get("readme")
    if readme:
        assert f"/{readme}" in declared, f"pyproject declares readme = {readme}, but the sdist omits it"
    assert "/LICENSE" in declared, "the sdist omits LICENSE, which the licence metadata refers to"


def test_no_test_tree_is_named_as_deliverable() -> None:
    trees = sorted(p.name for p in ROOT.iterdir() if p.is_dir() and p.name.startswith("tests"))
    assert trees, "no tests*/ directory found — this check would be vacuous"
    declared = set(_sdist()["include"])
    leaked = [tree for tree in trees if f"/{tree}/" in declared]
    assert not leaked, f"test suites named in the sdist allowlist: {leaked}"


def test_the_wheel_still_packages_only_the_library() -> None:
    packages = CONFIG["tool"]["hatch"]["build"]["targets"]["wheel"]["packages"]
    assert packages == [PACKAGE.rstrip("/")], (
        f"the wheel is no longer library-only: {packages}. A test tree or the web app in this list "
        f"puts development files in the delivered package."
    )


def test_the_build_backend_pin_matches_the_publish_lock() -> None:
    # `--no-isolation` builds from the *installed* backend, so `[build-system] requires` does not
    # govern our own build — but it governs everyone building from the sdist, and the lock governs
    # ours. Two declarations of one version, so a test holds them together: a backend bump on one
    # side without the other is how the metadata version changed without a commit last time.
    requires = CONFIG["build-system"]["requires"]
    hatchling = [req for req in requires if req.startswith("hatchling")]
    assert len(hatchling) == 1, f"expected one hatchling requirement, found {requires}"
    assert "==" in hatchling[0], f"the build backend is not pinned: {hatchling[0]}"
    pinned = _locked_versions()
    want = hatchling[0].split("==", 1)[1]
    assert pinned.get("hatchling") == want, (
        f"[build-system] pins hatchling=={want}; requirements/publish.txt pins {pinned.get('hatchling')}"
    )


def test_no_stray_file_sits_inside_the_package_directory() -> None:
    # The allowlists above are configuration. A `.env`, a key or a customer fixture committed into
    # the package would ship in the sdist, and every test above would stay green, because they
    # compare directory names. This one reads the tracked tree the package actually is.
    tracked = sorted(_tracked(PACKAGE.rstrip("/")))
    assert tracked, f"no tracked files under {PACKAGE} — this check would be vacuous"
    stray = [p for p in tracked if not (p.endswith((".py", ".pyi")) or p.endswith("/py.typed"))]
    assert not stray, f"files that would ship inside the package: {stray[:5]}"


def test_the_built_sdist_contains_exactly_the_tracked_package(tmp_path: pathlib.Path) -> None:
    # The artefact, not the configuration that produces it: hatchling's defaults decide what a
    # tarball carries, so a change in those defaults is invisible to every assertion above.
    # The build jobs install their toolchain into `.build-libs` / `.publish-libs` inside the
    # checkout, so the tree this is cut from carries directories that must never ship.
    planted = [ROOT / name / "planted.py" for name in (".build-libs", ".publish-libs")]
    for path in planted:
        path.parent.mkdir(exist_ok=True)
        path.write_text("PLANTED = 1\n", encoding="utf-8")
    try:
        _run([sys.executable, "-m", "build", "--sdist", "--outdir", str(tmp_path)])
    finally:
        for path in planted:
            path.unlink(missing_ok=True)
            try:
                path.parent.rmdir()
            except OSError:
                pass  # a real directory from a local workflow run: leave it alone
    (tarball,) = tmp_path.glob("*.tar.gz")
    with tarfile.open(tarball) as archive:
        members = [name.split("/", 1)[1] for name in archive.getnames() if "/" in name and not name.endswith("/")]

    # Hatchling's `SdistBuilder.get_default_build_data` force-includes the project file, the readme,
    # every license file, the root VCS ignore file, and `hatch.toml`/`hatch_build.py` when those
    # exist; `build_standard` writes `PKG-INFO` itself.
    always = {
        "pyproject.toml",
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
        ".gitignore",
        "hatch.toml",
        "hatch_build.py",
        "PKG-INFO",
    }
    leaked = sorted(m for m in members if ".publish-libs" in m or ".build-libs" in m)
    assert not leaked, f"a workspace library directory reached the sdist: {leaked[:3]}"
    stray = sorted({m for m in members if not m.startswith(PACKAGE) and m not in always})
    assert not stray, f"the sdist shipped files outside the package: {stray[:5]}"
    required = {"pyproject.toml", "README.md", "LICENSE", "CHANGELOG.md"}
    assert required <= set(members), f"the sdist dropped files a source build needs: {sorted(required - set(members))}"

    # The other direction, which no assertion above can see: the tarball is built from the working
    # tree and hatchling's walk filters by `.gitignore` pattern rather than by what git tracks, so
    # an untracked unignored file is added and a tracked file matching an ignore pattern is dropped
    # with every arm above still green. Compare the shipped package against the tree that defines it.
    shipped = {m for m in members if m.startswith(PACKAGE)}
    tracked = _tracked(PACKAGE.rstrip("/"))
    assert shipped == tracked, (
        f"the sdist does not match the tracked package: "
        f"missing={sorted(tracked - shipped)[:5]} extra={sorted(shipped - tracked)[:5]}"
    )

    # Redundant with `test_no_stray_file_sits_inside_the_package_directory` while that test stands —
    # together they already imply this — and deliberately kept as the backstop for the day the
    # source arm is relaxed, deleted, or made to skip.
    not_code = sorted(m for m in shipped if not (m.endswith((".py", ".pyi")) or m.endswith("/py.typed")))
    assert not not_code, f"the sdist carried non-code files inside the package: {not_code[:5]}"
