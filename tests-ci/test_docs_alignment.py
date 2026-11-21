"""The published documentation must describe the application that exists.

Audited 2026-11-21 against production: `docs/` held five internal planning documents — `plan.md`,
`plan-context.md`, `plan-product.md`, `plan-delivery.md`, `test-plan.md` — that name routes this
application no longer has (`/api/auth/session`, `/api/audit/route`, `/api/export/report`,
`/api/billing/checkout`). mkdocs builds every file under `docs_dir` whether or not it is in the
nav, so all five were served under /docs/ — /docs/plan/, /docs/plan-context/, /docs/plan-product/,
/docs/plan-delivery/ and /docs/test-plan/ — and read as current documentation of a vanished app.

They are `.gitignore`d, so a clone does not contain them at all; on the workstation they are still on
disk, and `mkdocs.yml`'s `exclude_docs` stops a local `mkdocs build` from publishing them.

These tests hold the two properties that failure violated:

* a document that names an `/api` route the app does not serve must be excluded from the published
  set, and no stray markdown document may sit in the published tree at all;
* an excluded name must be a file that exists, or a path `.gitignore` covers — the two states above —
  so the list cannot rot into decoration. This catches a typo; it no longer catches a planning
  document deleted from disk while its exclusion and ignore entry are both left behind.
"""

from __future__ import annotations

import functools
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MKDOCS = ROOT / "mkdocs.yml"

# Paths the documentation may name that are not Next.js routes: the ALB sends `/mcp` and
# `/api/calculate` to the Python containers, `/docs*` is the built site, and `/api` alone is the
# prefix those live under.
NOT_NEXT_ROUTES = ("/docs", "/mcp", "/api/calculate")

ROUTE_PATTERN = re.compile(r"(?<![\w.:-])/api/[\w/-]+")


def _mkdocs_config() -> str:
    return MKDOCS.read_text(encoding="utf-8")


def _excluded() -> set[str]:
    """Files named under `exclude_docs:` in mkdocs.yml, as paths relative to docs/."""
    text = _mkdocs_config()
    match = re.search(r"^exclude_docs:\s*\|\s*\n((?:[ \t]+.*\n?)+)", text, re.M)
    if not match:
        return set()
    return {line.strip() for line in match.group(1).splitlines() if line.strip()}


@functools.lru_cache(maxsize=1)
def _routes() -> set[str]:
    """Every path the Next app serves, derived from app/ itself."""
    listing = subprocess_listing()
    routes = set()
    for path in listing:
        for suffix, prefixes in (("/page.tsx", ("app/(en)", "app/(zh)", "app/(hk)")), ("/route.ts", ("app/(en)",))):
            if not path.endswith(suffix):
                continue
            route = path[: -len(suffix)]
            for prefix in prefixes:
                if route.startswith(prefix):
                    route = route[len(prefix) :]
                    break
            routes.add(route or "/")
    return routes


def subprocess_listing() -> list[str]:
    import subprocess

    return subprocess.run(
        ["git", "ls-files", "app"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()


def _offending_routes(path: pathlib.Path) -> set[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    found = set()
    for mention in ROUTE_PATTERN.findall(text):
        cleaned = mention.rstrip("/")
        if cleaned in _routes() or cleaned.startswith(NOT_NEXT_ROUTES) or cleaned == "/api":
            continue
        found.add(cleaned)
    return found


def test_every_document_in_the_published_tree_is_tracked_or_excluded() -> None:
    # MkDocs builds the *filesystem*, and this suite used to enumerate the git index — so an
    # untracked working paper sitting in docs/ was invisible to every check above while still being
    # built and published. A file here must be tracked (part of the manual) or excluded (a working
    # paper); anything else is named rather than silently published.
    import subprocess

    listed = subprocess.run(["git", "ls-files", "docs"], cwd=ROOT, check=True, capture_output=True, text=True).stdout
    tracked = set(listed.splitlines())
    excluded = _excluded()
    stray = sorted(
        p.relative_to(ROOT).as_posix()
        for p in DOCS.rglob("*.md")
        if p.relative_to(ROOT).as_posix() not in tracked and p.relative_to(DOCS).as_posix() not in excluded
    )
    assert not stray, f"documents in the published tree that are neither tracked nor excluded: {stray}"


def _tracked_docs() -> list[pathlib.Path]:
    import subprocess

    listing = subprocess.run(
        ["git", "ls-files", "docs"], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.splitlines()
    return [ROOT / p for p in listing if p.endswith(".md")]


def test_the_application_serves_the_routes_this_test_expects() -> None:
    routes = _routes()
    # A derivation that returned nothing would make every check below vacuous.
    assert "/api/health" in routes, f"route derivation is broken: {sorted(routes)[:6]}"
    assert len(routes) >= 10, f"expected the app's full route set, got {sorted(routes)}"


def test_a_document_naming_a_dead_route_is_excluded_from_the_site() -> None:
    published = [p for p in _tracked_docs() if p.relative_to(DOCS).as_posix() not in _excluded()]
    offenders = sorted(
        (p.relative_to(DOCS).as_posix(), sorted(_offending_routes(p))[:3]) for p in published if _offending_routes(p)
    )
    assert not offenders, "these documents are published and name routes the app does not serve: " + "; ".join(
        f"{name} -> {routes}" for name, routes in offenders
    )


def test_every_excluded_document_exists_or_is_ignored() -> None:
    # In a clone the planning papers are absent — they are .gitignore'd — while on the workstation
    # they are present and must still be excluded from the build. Either state is valid; a name that
    # is neither present nor ignored is a typo that would silently protect nothing.
    import subprocess

    bad = []
    for name in _excluded():
        path = f"docs/{name}"
        if (DOCS / name).exists():
            continue
        ignored = subprocess.run(["git", "check-ignore", "-q", path], cwd=ROOT, capture_output=True).returncode
        if ignored != 0:
            bad.append(name)
    assert not bad, f"exclude_docs names files that neither exist nor are ignored: {bad}"


def test_the_planning_documents_are_the_ones_excluded() -> None:
    # Named so that removing an exclusion to "fix a link" is a visible, failing edit rather than a
    # silent republication of documents describing an app that no longer exists.
    excluded = _excluded()
    for name in ("plan.md", "plan-context.md", "plan-product.md", "plan-delivery.md", "test-plan.md"):
        assert name in excluded, f"{name} names dead routes and is no longer excluded from the build"


def test_the_published_nav_and_the_published_files_agree() -> None:
    # Every nav entry must be a real file, so a rename cannot leave a broken nav behind.
    nav = re.findall(r":\s*([\w./-]+\.md)\s*$", _mkdocs_config(), re.M)
    missing = [entry for entry in nav if not (DOCS / entry).exists()]
    assert not missing, f"mkdocs.yml nav names files that do not exist: {missing}"
