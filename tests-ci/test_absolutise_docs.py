"""The docs link rewriter, against a known-good and two known-bad trees.

`scripts/absolutise_docs.py` runs in the image build, and its assertions are what stop a broken
subtree reaching the image — `/docs` returning 200 while its own stylesheet 404s is the failure it
exists to prevent. So the assertions need fixtures that make them fail; a checker never observed
failing is unproven.

    python3 -m pytest tests-ci/test_absolutise_docs.py -q
"""

from __future__ import annotations

import pathlib
import subprocess
import sys

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "absolutise_docs.py"


def run(tree: pathlib.Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), str(tree)], capture_output=True, text=True)


def write(root: pathlib.Path, where: str, body: str) -> pathlib.Path:
    target = root / where
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"<html><head></head><body>{body}</body></html>", encoding="utf-8")
    return target


def test_relative_links_become_absolute_and_fragments_survive(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "docs"
    write(root, "assets/x.css", "")  # the file the link names
    write(root, "guide/index.html", "")  # the page a directory link means
    index = write(
        root,
        "index.html",
        '<link rel="stylesheet" href="assets/x.css"><a href="guide/">guide</a>',
    )
    nested = write(root, "api/capm/index.html", '<a href="../../index.html#methods">home</a>')

    r = run(root)
    assert r.returncode == 0, r.stderr

    assert 'href="/docs/assets/x.css"' in index.read_text()
    # A directory link names the file it means rather than leaving the server to guess.
    assert 'href="/docs/guide/index.html"' in index.read_text()
    # The fragment must stay a fragment: `…/index.html#methods`, never `…#methods/index.html`.
    assert 'href="/docs/index.html#methods"' in nested.read_text()


def test_a_single_quoted_link_is_rewritten_too(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "docs"
    write(root, "assets/x.css", "")
    index = write(root, "index.html", "<a href='assets/x.css'>x</a>")
    r = run(root)
    assert r.returncode == 0, r.stderr
    assert "href='/docs/assets/x.css'" in index.read_text()


def test_a_link_naming_no_file_fails_the_build(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "docs"
    # Absolute but wrong — what a fragment folded into a path used to produce, and what the two dead
    # links in the examples page were. A browser 404s just as loudly on it.
    write(root, "index.html", '<a href="/docs/nowhere/index.html">gone</a>')
    r = run(root)
    assert r.returncode == 1, f"expected failure, got {r.returncode}"
    assert "name no file" in r.stderr


def test_the_theme_override_is_not_treated_as_a_page(tmp_path: pathlib.Path) -> None:
    root = tmp_path / "docs"
    write(root, "index.html", "")
    # `overrides/main.html` is a Jinja template copied verbatim; the theme resolves its hrefs at
    # build time, so rewriting them would corrupt the template.
    over = write(root, "overrides/main.html", '<link href="assets/style.css" rel="stylesheet">')
    r = run(root)
    assert r.returncode == 0, r.stderr
    assert 'href="assets/style.css"' in over.read_text()

def test_the_config_block_is_pinned_to_docs(tmp_path: pathlib.Path) -> None:
    """The two values Material resolves against `location.href`, not against an attribute.

    Miss them and every status still says 200 while the search box does nothing: `base` decides
    where `search_index.json` is fetched from and `search` is the worker script.
    """
    root = tmp_path / "docs"
    write(root, "assets/javascripts/workers/search.abc.min.js", "")
    page = root / "api" / "capm" / "index.html"
    page.parent.mkdir(parents=True)
    page.write_text(
        '<html><head><script id="__config" type="application/json">'
        '{"base": "../..", "search": "../../assets/javascripts/workers/search.abc.min.js"}'
        '</script></head><body><p>"base": "a code sample, not config"</p></body></html>',
        encoding="utf-8",
    )
    r = run(root)
    assert r.returncode == 0, r.stderr
    html = page.read_text()
    assert '"base": "/docs/"' in html
    assert '"search": "/docs/assets/javascripts/workers/search.abc.min.js"' in html
    # A code sample that happens to contain `"base":` is documentation, not configuration.
    assert '"base": "a code sample, not config"' in html

def test_a_config_block_that_was_not_pinned_fails_the_build(tmp_path: pathlib.Path) -> None:
    """The pin is conditional on a regex matching a floating theme's tag.

    If Material adds a nonce or reorders the attributes, the substitution silently stops applying and
    search dies with every status still 200. This asserts the *outcome*, not the regex.
    """
    root = tmp_path / "docs"
    page = root / "index.html"
    root.mkdir(parents=True)
    page.write_text(
        '<html><head><script id="__config" type="application/x">{"base": "."}</script>'
        "</head><body></body></html>",
        encoding="utf-8",
    )
    r = run(root)
    assert r.returncode == 1, f"an unpinned block passed: {r.stdout}"
    assert "not pinned" in r.stderr


def test_a_link_escaping_the_tree_fails_the_build(tmp_path: pathlib.Path) -> None:
    # Percent-decoded `..` must not satisfy the existence check by stat-ing outside the tree.
    root = tmp_path / "docs"
    write(root, "index.html", '<a href="/docs/%2e%2e/package.json">out</a>')
    r = run(root)
    assert r.returncode == 1, f"a link escaping the tree passed: {r.stdout}"
    assert "name no file" in r.stderr

def test_a_renamed_config_id_fails_instead_of_passing_vacuously(tmp_path: pathlib.Path) -> None:
    """Zero detections is not success.

    If the theme renames the id, every page falls through the candidate test and nothing is pinned —
    search then fetches from the origin root with every status still 200. A real Material build writes
    `search/search_index.json`, so its presence plus zero pins means the guard never ran.
    """
    root = tmp_path / "docs"
    write(root, "search/search_index.json", "{}")
    page = root / "index.html"
    page.write_text(
        '<html><head><script id="site-config" type="application/json">{"base": "."}</script>'
        "</head><body></body></html>",
        encoding="utf-8",
    )
    r = run(root)
    assert r.returncode == 1, f"a renamed id passed: {r.stdout}"
    assert "not recognised" in r.stderr


def test_no_search_index_and_no_block_still_passes(tmp_path: pathlib.Path) -> None:
    # The guard must not fire on a tree that simply has no search plugin.
    root = tmp_path / "docs"
    write(root, "index.html", "<p>no config here</p>")
    r = run(root)
    assert r.returncode == 0, r.stderr
