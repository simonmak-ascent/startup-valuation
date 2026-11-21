#!/usr/bin/env python3
"""Generate the `## MCP Tools` section of every skill pack from the canonical tool surface.

The packs used to be written by hand, and drifted twice: first to per-method functions that never
existed (`valuation_berkus`), then to the *function* parameter names rather than the *MCP* ones
(`lambda_` where the tool accepts `mean_events`), because `args`/`opt` map function parameter ->
argument name and the dispatch in `tool_surface.py` indexes by the value.

Generated, so neither can happen again: `ci.yml` runs this and diffs `skills/`.

The scope of each pack is its own summary line — which tools that pack covers — transcribed below.
"""

from __future__ import annotations

import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from startup_valuation.mcp.tool_surface import TOOLS  # noqa: E402

TOOLS_BY_NAME = {tool["name"]: tool for tool in TOOLS}

# Each pack's scope, from the sub-line under its H1.
SCOPE = {
    "valuation-core": ["valuation_core"],
    "valuation-foundations": [
        "valuation_probability",
        "valuation_time_value",
        "valuation_capm",
        "valuation_comparables",
        "valuation_international",
    ],
    "valuation-advanced": ["valuation_advanced"],
    "valuation-industry": [
        "valuation_saas",
        "valuation_biotech",
        "valuation_fintech",
        "valuation_marketplace",
        "valuation_hardware",
    ],
    "valuation-emerging": ["valuation_emerging"],
    "valuation-stakeholder": ["valuation_stakeholder"],
}

INTRO = (
    "Each tool takes `method` plus that method's own parameters — the arguments below are the ones\n"
    "the tool validates, and an unknown method or a missing parameter returns an error instead of a value."
)


def _params(method: dict) -> str:
    # The mapping is function-parameter -> MCP argument name; the tool takes the *value*.
    required = list((method.get("args") or {}).values())
    optional = list((method.get("opt") or {}).values())
    if required and optional:
        return ", ".join(required) + f" (optional: {', '.join(optional)})"
    if required:
        return ", ".join(required)
    if optional:
        return f"all optional: {', '.join(optional)}"
    return "no parameters"


def _section(tool_name: str) -> str:
    tool = TOOLS_BY_NAME[tool_name]
    description = tool.get("description") or ""
    summary = re.split(r"(?<=[.!?])\s", description)[0].rstrip(".")
    if len(summary) < 20:  # a decimal or an "e.g." would truncate mid-clause
        summary = description.rstrip(".")
    lines = [f"### `{tool_name}`", "", f"{summary}.", ""]
    lines += [f'- `method: "{m["key"]}"` — {_params(m)}' for m in tool["methods"]]
    return "\n".join(lines) + "\n"


def render(pack: str) -> str:
    return "## MCP Tools\n\n" + INTRO + "\n\n" + "\n".join(_section(t) for t in SCOPE[pack])


def main() -> int:
    changed = 0
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        pack = path.parent.name
        if pack not in SCOPE:
            raise SystemExit(f"no scope declared for skill pack {pack!r}")
        text = path.read_text(encoding="utf-8")
        head, marker, rest = text.partition("## MCP Tools")
        if not marker:
            raise SystemExit(f"{path} has no '## MCP Tools' section")
        _, sep, tail = rest.partition("\n## ")
        new = head + render(pack) + (("\n## " + tail) if sep else "")
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed += 1
    print(f"rendered {len(SCOPE)} skill packs, {changed} changed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
