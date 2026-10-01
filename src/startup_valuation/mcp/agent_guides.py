"""MCP prompts and resources for the Startup Valuation server.

Shared by the stdio FastMCP server and the hosted Streamable HTTP endpoint so both
advertise the same agent-facing surface:

* **Resources** expose the method catalog (every tool, method key, and its required
  and optional parameters) so an agent can plan a calculation without trial calls.
* **Prompts** are guided, multi-step valuation workflows. Each step names the exact
  tool and ``method`` to call; the required/optional parameter lists are generated
  from the canonical tool surface, so the prompts cannot drift from the tools.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from startup_valuation.mcp.tool_surface import SERVER_NAME, SERVER_VERSION, TOOLS

URI_SCHEME = "startup-valuation"
CATALOG_URI = f"{URI_SCHEME}://methods"


# --------------------------------------------------------------------------
# Resources
# --------------------------------------------------------------------------


def _method_entry(method: dict[str, Any]) -> dict[str, Any]:
    return {
        "method": method["key"],
        "label": method.get("label", method["key"]),
        "summary": method.get("summary", ""),
        "required": list(method.get("args", {}).values()),
        "optional": list(method.get("opt", {}).values()),
    }


def _tool_entry(tool: dict[str, Any]) -> dict[str, Any]:
    return {
        "tool": tool["name"],
        "title": tool["title"],
        "methods": [_method_entry(m) for m in tool["methods"]],
    }


def method_catalog() -> dict[str, Any]:
    """Every tool and method with its parameters, as one JSON document."""
    return {
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "tools": [_tool_entry(t) for t in TOOLS],
    }


def list_resources() -> list[dict[str, Any]]:
    resources = [
        {
            "uri": CATALOG_URI,
            "name": "method-catalog",
            "title": "Method catalog",
            "description": "Every tool, method key, and its required and optional parameters.",
            "mimeType": "application/json",
        }
    ]
    for tool in TOOLS:
        resources.append(
            {
                "uri": f"{CATALOG_URI}/{tool['name']}",
                "name": f"methods-{tool['name']}",
                "title": f"{tool['title']} methods",
                "description": f"Methods and parameters of {tool['name']}.",
                "mimeType": "application/json",
            }
        )
    return resources


def read_resource(uri: str) -> dict[str, Any]:
    """Return an MCP ``resources/read`` result. Raises ValueError for unknown URIs."""
    if uri == CATALOG_URI:
        payload: dict[str, Any] = method_catalog()
    else:
        prefix = f"{CATALOG_URI}/"
        tool = next((t for t in TOOLS if uri == prefix + t["name"]), None)
        if tool is None:
            raise ValueError(f"Unknown resource: {uri}")
        payload = _tool_entry(tool)
    return {"contents": [{"uri": uri, "mimeType": "application/json", "text": json.dumps(payload, indent=2)}]}


# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------


def _method_spec(tool_name: str, method_key: str) -> dict[str, Any]:
    tool = next(t for t in TOOLS if t["name"] == tool_name)
    return next(m for m in tool["methods"] if m["key"] == method_key)


def _render_steps(steps: list[tuple[str, str, str]]) -> str:
    lines = []
    for i, (purpose, tool_name, method_key) in enumerate(steps, start=1):
        spec = _method_spec(tool_name, method_key)
        required = ", ".join(spec.get("args", {}).values()) or "none"
        optional = ", ".join(spec.get("opt", {}).values())
        line = f"{i}. {purpose}: call `{tool_name}` with method=`{method_key}` (required: {required}"
        line += f"; optional: {optional})." if optional else ")."
        lines.append(line)
    return "\n".join(lines)


def _build(intro: str, steps: list[tuple[str, str, str]], outro: str) -> str:
    return (
        f"{intro}\n\n"
        "Use only explicit inputs. If an input the method requires is missing, ask the user for it "
        "instead of inventing a number. Rates are decimals (0.10 = 10%).\n\n"
        f"{_render_steps(steps)}\n\n{outro}\n\n"
        "Finish with a table of each method used, its value, key inputs and assumptions, and cite the "
        "chapter and formula_number returned by each result."
    )


PROMPTS: list[dict[str, Any]] = [
    {
        "name": "value_pre_revenue_startup",
        "title": "Value a pre-revenue startup",
        "description": (
            "Triangulate a pre-revenue valuation with Scorecard, Berkus, Risk-Factor Summation and the VC Method."
        ),
        "arguments": [
            {
                "name": "company",
                "description": "Company, sector, stage and any figures you already have.",
                "required": True,
            },
            {
                "name": "region",
                "description": "Region used to pick the comparable average pre-money valuation.",
                "required": False,
            },
        ],
        "build": lambda a: _build(
            f"Value this pre-revenue startup: {a.get('company', '')}"
            + (f" (region: {a['region']})" if a.get("region") else "")
            + ". Use several independent methods and reconcile them.",
            [
                ("Scorecard against a regional average pre-money", "valuation_core", "scorecard"),
                ("Berkus milestone value (supply every factor you can assess)", "valuation_core", "berkus"),
                ("Risk-Factor Summation adjustment", "valuation_core", "risk_factor"),
                ("Exit value from projected revenue", "valuation_core", "terminal_value"),
                ("VC Method post-money from that exit value", "valuation_core", "vc_post_money"),
                ("VC Method pre-money", "valuation_core", "vc_pre_money"),
                ("Blend the indications with explicit weights", "valuation_probability", "probability_weighted"),
            ],
            "Explain why the indications differ and which you weight most for this stage.",
        ),
    },
    {
        "name": "value_saas_startup",
        "title": "Value a SaaS startup",
        "description": "Unit economics, growth quality and an ARR-multiple, cross-checked with a DCF.",
        "arguments": [
            {
                "name": "company",
                "description": "Company and its ARR, growth, churn, margin and CAC figures.",
                "required": True,
            },
        ],
        "build": lambda a: _build(
            f"Value this SaaS company: {a.get('company', '')}. Check unit economics before applying a multiple.",
            [
                ("Customer lifetime value", "valuation_saas", "ltv"),
                ("Customer acquisition cost", "valuation_saas", "cac"),
                ("CAC payback period", "valuation_saas", "cac_payback"),
                ("Net revenue retention", "valuation_saas", "nrr"),
                ("Rule of 40", "valuation_saas", "rule_of_40"),
                ("ARR revenue-multiple valuation", "valuation_saas", "revenue_multiple"),
                ("Startup-adjusted discount rate", "valuation_capm", "startup_capm"),
                ("DCF cross-check with terminal growth", "valuation_time_value", "dcf"),
            ],
            "Flag any metric outside common SaaS benchmarks (for example LTV/CAC below 3 or NRR below 100%).",
        ),
    },
    {
        "name": "model_funding_round",
        "title": "Model a funding round",
        "description": "Pre/post-money, dilution and SAFE conversion for a priced round or SAFE.",
        "arguments": [
            {
                "name": "round",
                "description": "Round terms: amount, valuation or cap, discount, current ownership.",
                "required": True,
            },
        ],
        "build": lambda a: _build(
            f"Model this financing: {a.get('round', '')}.",
            [
                ("Pre-money valuation from post-money and investment", "valuation_core", "vc_pre_money"),
                ("Founder dilution", "valuation_stakeholder", "dilution"),
                ("SAFE conversion price under the cap", "valuation_emerging", "safe_cap"),
                ("SAFE conversion price under the discount", "valuation_emerging", "safe_discount"),
                ("Expected SAFE ownership", "valuation_emerging", "safe_expected"),
            ],
            "Skip the SAFE steps for a priced round, and the priced-round steps for a SAFE-only raise.",
        ),
    },
]


def list_prompts() -> list[dict[str, Any]]:
    return [
        {
            "name": p["name"],
            "title": p["title"],
            "description": p["description"],
            "arguments": p["arguments"],
        }
        for p in PROMPTS
    ]


def get_prompt(name: str, arguments: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return an MCP ``prompts/get`` result. Raises ValueError for unknown prompts."""
    prompt = next((p for p in PROMPTS if p["name"] == name), None)
    if prompt is None:
        raise ValueError(f"Unknown prompt: {name}")
    args = arguments or {}
    for arg in prompt["arguments"]:
        if arg.get("required") and not args.get(arg["name"]):
            raise ValueError(f"prompt '{name}' requires argument '{arg['name']}'")
    builder: Callable[[dict[str, Any]], str] = prompt["build"]
    return {
        "description": prompt["description"],
        "messages": [{"role": "user", "content": {"type": "text", "text": builder(args)}}],
    }


# --------------------------------------------------------------------------
# FastMCP registration (stdio server)
# --------------------------------------------------------------------------


def register(mcp: Any) -> None:
    """Register the resources and prompts on a FastMCP server."""

    @mcp.resource(CATALOG_URI, name="method-catalog", mime_type="application/json")  # type: ignore[untyped-decorator]
    def _catalog() -> str:
        return str(read_resource(CATALOG_URI)["contents"][0]["text"])

    for tool in TOOLS:
        uri = f"{CATALOG_URI}/{tool['name']}"

        def _make(u: str) -> Callable[[], str]:
            def _read() -> str:
                return str(read_resource(u)["contents"][0]["text"])

            return _read

        mcp.resource(uri, name=f"methods-{tool['name']}", mime_type="application/json")(_make(uri))

    for prompt in PROMPTS:
        arg_names = [a["name"] for a in prompt["arguments"]]

        def _make_prompt(p: dict[str, Any], names: list[str]) -> Callable[..., str]:
            # FastMCP derives prompt arguments from a real signature, so build one with
            # explicit keyword parameters (required ones have no default).
            required = {a["name"] for a in p["arguments"] if a.get("required")}
            sig = ", ".join((f"{n}: str" if n in required else f"{n}: str = ''") for n in names)
            body = ", ".join(f"{n!r}: {n}" for n in names)
            namespace: dict[str, Any] = {"_render": lambda kw: get_prompt(p["name"], kw)}
            exec(  # noqa: S102 — names come from the static PROMPTS table above
                f"def {p['name']}({sig}) -> str:\n"
                f"    return str(_render({{{body}}})['messages'][0]['content']['text'])\n",
                namespace,
            )
            fn: Callable[..., str] = namespace[p["name"]]
            return fn

        mcp.prompt(name=prompt["name"], title=prompt["title"], description=prompt["description"])(
            _make_prompt(prompt, arg_names)
        )
