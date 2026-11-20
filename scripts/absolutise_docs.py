#!/usr/bin/env python3
"""Make every link in the built docs site absolute before it goes into the image.

MkDocs writes *relative* hrefs, authored for a directory URL that ends in a slash:

    /docs/index.html          href="assets/stylesheets/main.css"
    /docs/api/capm/index.html href="../../assets/stylesheets/main.css"

Next serves a rewrite's destination at the URL that was *requested*, and `trailingSlash` is false,
so `/docs` and `/docs/api/capm` keep their slash-less form. Relative resolution then drops one
directory — the page paints unstyled, its stylesheet 404s, and every status in the deployed suite
still says 200 because those tests fetch assets by absolute path.

Rather than change URL policy site-wide for a subtree, this rewrites each link to the file it
actually means:

    href="assets/x.css"  ->  /docs/assets/x.css
    href="mcp-server/"   ->  /docs/mcp-server/index.html

After it runs, every link is absolute and every request is for a real file, so the serving stack's
trailing-slash behaviour cannot matter.

    python3 scripts/absolutise_docs.py public/docs

Exit 0 when it rewrote the tree, 1 when a link could not be resolved (a broken site is not copied).
"""

from __future__ import annotations

import pathlib
import re
import sys
import urllib.parse

# Attributes that carry a URL we can resolve. Deliberately not a full HTML parser: MkDocs emits a
# regular subset, and the test asserts no relative link survives.
ATTR = re.compile(r'(?P<attr>\b(?:href|src))=(?P<q>["\'])(?P<url>.*?)(?P=q)')
EXTERNAL = re.compile(r"^(?:[a-z][a-z0-9+.-]*:|/|#|\?)", re.I)
# A fragment is not a directory: folding `mcp-server/#tool-reference` into the path produced
# `/docs/mcp-server/#tool-reference/index.html`, which loads the page at the top and loses the anchor.
SPLIT = re.compile(r"^(?P<path>[^?#]*)(?P<tail>[?#].*)?$")
# Material resolves these two against `location.href`, not against an attribute — the only channel
# left that still depends on the URL the browser asked for.
CONFIG_BASE = re.compile(r'"base":\s*"[^"]*"')
CONFIG_SEARCH = re.compile(r'"search":\s*"(?P<url>[^"]*)"')
# The block those two live in, so a code sample elsewhere in the page is left alone.
CONFIG = re.compile(r'<script id="__config" type="application/json">.*?</script>', re.S)


def resolve(page: pathlib.Path, root: pathlib.Path, url: str) -> str | None:
    """The absolute path this link should use, or None when it is already absolute."""
    if EXTERNAL.match(url):
        return None
    split = SPLIT.match(url)
    assert split is not None
    path_part, tail = split.group("path"), split.group("tail") or ""
    base = page.parent.relative_to(root)  # "" for the root index, "api/capm" for a page
    target = (base / path_part).as_posix()
    # Normalise `../` without touching the filesystem: posixpath semantics, not os.path.
    parts: list[str] = []
    for part in target.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None  # walks above /docs: leave it alone rather than invent a path
            parts.pop()
        else:
            parts.append(part)
    if not parts:  # `./`, or `../` that lands on the root
        return "/docs/index.html" + tail
    path = "/docs/" + "/".join(parts)
    if path_part.endswith("/") or "." not in parts[-1]:
        path = path.rstrip("/") + "/index.html"
    return path + tail


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: absolutise_docs.py <site-dir>", file=sys.stderr)
        return 2
    root = pathlib.Path(sys.argv[1])
    if not root.is_dir():
        print(f"absolutise_docs: {root} is not a directory", file=sys.stderr)
        return 2

    pages = 0
    links = 0
    for page in sorted(root.rglob("*.html")):
        if "overrides" in page.relative_to(root).parts:
            continue  # Jinja template sources copied verbatim, not pages
        text = page.read_text(encoding="utf-8")

        def sub(m: re.Match[str]) -> str:
            url = m.group("url")
            resolved = resolve(page, root, url)
            if resolved is None:
                return m.group(0)
            nonlocal links
            links += 1
            q = m.group("q")
            return f"{m.group('attr')}={q}{resolved}{q}"

        new = ATTR.sub(sub, text)
        # `base` is what search fetches `search_index.json` against, and `search` is the worker script;
        # Material resolves both with `new URL(value, location.href)`, so at a slash-less `/docs` they
        # land on the origin root and the search box silently does nothing.
        # Scoped to the `__config` block: a code sample elsewhere in a page that happens to contain
        # `"base": "…"` is documentation, and rewriting it would corrupt the page.
        block = CONFIG.search(new)
        if block:
            json_text = block.group(0)
            fixed = CONFIG_BASE.sub(lambda _m: '"base": "/docs/"', json_text)
            search = CONFIG_SEARCH.search(fixed)
            if search:
                rel = search.group("url")
                resolved = resolve(page, root, rel) or rel
                fixed = fixed[: search.start()] + f'"search": "{resolved}"' + fixed[search.end() :]
            new = new[: block.start()] + fixed + new[block.end() :]
        if new != text:
            page.write_text(new, encoding="utf-8")
            pages += 1

    # The whole point is that nothing relative survives; assert it rather than count it.
    leftover = []
    for page in root.rglob("*.html"):
        if "overrides" in page.relative_to(root).parts:
            continue  # not a page; see the rewrite loop
        for m in ATTR.finditer(page.read_text(encoding="utf-8")):
            if not EXTERNAL.match(m.group("url")):
                leftover.append(f"{page.relative_to(root)}: {m.group('url')}")
    if leftover:
        print(f"absolutise_docs: {len(leftover)} relative link(s) remain, e.g. {leftover[:3]}", file=sys.stderr)
        return 1

    # The `__config` pin above is conditional on CONFIG matching Material's tag, and the theme comes
    # from a `>=` requirement with no lock. A page that carries the block but kept a relative base
    # would fail silently: search fetches off the origin root and returns nothing while every status
    # still says 200 — the symptom this file exists to prevent. Assert the pin rather than trust it.
    unpinned = []
    pinned = 0
    for page in root.rglob("*.html"):
        if "overrides" in page.relative_to(root).parts:
            continue
        html = page.read_text(encoding="utf-8")
        # `__config`, not `id="__config"`: a theme that requotes or reorders the attribute still
        # emits the id, so this stays a *candidate* and the check fails closed rather than skipping.
        if "__config" not in html:
            continue
        block = CONFIG.search(html)
        if block is None or '"base": "/docs/"' not in block.group(0):
            unpinned.append(str(page.relative_to(root)))
        else:
            pinned += 1
    if unpinned:
        print(
            f"absolutise_docs: {len(unpinned)} page(s) carry a __config block that was not pinned, e.g. {unpinned[:3]}",
            file=sys.stderr,
        )
        return 1
    # Zero detections is not success: a theme that renames the id would make every page fall through
    # the candidate test, and a real Material build always writes a search index. If the site has one
    # and nothing was pinned, the guard did not run — which is the failure it is meant to catch.
    if pinned == 0 and (root / "search" / "search_index.json").is_file():
        print(
            "absolutise_docs: the site carries a search index but no page was pinned — the "
            "__config block was not recognised, so search would fetch from the origin root",
            file=sys.stderr,
        )
        return 1

    # Absolute is not the same as correct: a link naming a file that does not exist 404s just as
    # loudly, and the fragment case above is exactly how a wrong-but-absolute link appears.
    missing = []
    for page in root.rglob("*.html"):
        if "overrides" in page.relative_to(root).parts:
            continue
        for m in ATTR.finditer(page.read_text(encoding="utf-8")):
            url = m.group("url")
            if not url.startswith("/docs/"):
                continue
            # A percent-encoded link still names the file on disk: compare decoded, or a space or a
            # non-ASCII filename fails the build for being correct.
            rel = urllib.parse.unquote(url[len("/docs/") :].split("#", 1)[0].split("?", 1)[0])
            if not rel:
                continue
            target = (root / rel).resolve()
            # `%2e%2e` decodes to `..`, and a leading `/` makes pathlib discard the left operand:
            # either would stat outside the tree. The guard only stats, never reads, but a link that
            # passes while naming no file in the image is the same false green as a stale marker.
            inside = target.is_relative_to(root.resolve())
            if not inside or not target.is_file():
                missing.append(f"{page.relative_to(root)}: {url}")
    if missing:
        print(f"absolutise_docs: {len(missing)} link(s) name no file, e.g. {missing[:3]}", file=sys.stderr)
        return 1

    print(f"absolutise_docs: {pages} page(s), {links} link(s) made absolute under {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
