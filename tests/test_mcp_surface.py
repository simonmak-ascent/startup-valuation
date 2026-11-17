"""Regression tests for the folded MCP tool surface (Glama/TDQS contract)."""

from __future__ import annotations

import pytest

from startup_valuation.mcp import tool_surface as ts

EXPECTED_TOOLS = [
    "valuation_probability",
    "valuation_time_value",
    "valuation_capm",
    "valuation_core",
    "valuation_advanced",
    "valuation_comparables",
    "valuation_saas",
    "valuation_marketplace",
    "valuation_fintech",
    "valuation_biotech",
    "valuation_hardware",
    "valuation_international",
    "valuation_stakeholder",
    "valuation_emerging",
]


def test_tool_count_in_scoring_band():
    # TDQS Tool Count Appropriateness scores 5/5 only in the 3-15 band.
    assert ts.tool_count() == len(EXPECTED_TOOLS) == 14
    assert 3 <= ts.tool_count() <= 15


def test_tool_names_and_order():
    assert [t["name"] for t in ts.TOOLS] == EXPECTED_TOOLS
    definitions = [t["name"] for t in ts.list_tools()]
    assert definitions == EXPECTED_TOOLS


def test_every_tool_has_full_metadata():
    for tool in ts.list_tools():
        assert tool["title"], tool["name"]
        assert len(tool["description"]) > 60, tool["name"]
        assert tool["outputSchema"], tool["name"]
        assert tool["annotations"] == ts.COMMON_ANNOTATIONS
        assert tool["annotations"]["readOnlyHint"] is True
        assert tool["annotations"]["openWorldHint"] is False
        assert tool["annotations"]["destructiveHint"] is False
        assert tool["annotations"]["idempotentHint"] is True
        assert tool["inputSchema"]["type"] == "object"


def test_every_parameter_is_documented():
    for tool in ts.list_tools():
        for name, schema in tool["inputSchema"]["properties"].items():
            assert schema.get("description"), f"{tool['name']}.{name} missing description"


def test_methods_have_summaries_and_unique_keys():
    for tool in ts.TOOLS:
        if tool.get("compound"):
            continue
        keys = [m["key"] for m in tool["methods"]]
        assert keys, tool["name"]
        assert len(keys) == len(set(keys)), f"duplicate method keys in {tool['name']}"
        for method in tool["methods"]:
            assert method["summary"], (tool["name"], method["key"])


def test_method_enum_matches_input_schema():
    for tool in ts.TOOLS:
        if tool.get("compound"):
            continue
        enum = ts.input_schema(tool)["properties"]["method"]["enum"]
        assert enum == [m["key"] for m in tool["methods"]]


@pytest.mark.parametrize(
    ("tool", "arguments", "expected"),
    [
        (
            "valuation_probability",
            {"method": "expected_value_discrete", "outcomes": [0, 100], "probabilities": [0.5, 0.5]},
            50.0,
        ),
        (
            "valuation_time_value",
            {"method": "present_value", "future_value": 1100, "rate": 0.1, "periods": 1},
            pytest.approx(1000.0),
        ),
        (
            "valuation_time_value",
            {"method": "compound_growth", "starting_value": 1_000_000, "growth_rate": 0.4, "periods": 3},
            pytest.approx(2_744_000.0),
        ),
        (
            "valuation_time_value",
            {"method": "cagr", "starting_value": 1_000_000, "ending_value": 2_744_000, "periods": 3},
            pytest.approx(0.4, abs=1e-9),
        ),
        (
            "valuation_time_value",
            {"method": "dcf", "cash_flows": [100_000, 120_000, 140_000], "rate": 0.12, "terminal_growth": 0.03},
            pytest.approx(1_425_028.3, abs=1),
        ),
        (
            "valuation_capm",
            {
                "method": "wacc",
                "equity_value": 700_000,
                "debt_value": 300_000,
                "cost_of_equity": 0.18,
                "cost_of_debt": 0.08,
                "tax_rate": 0.25,
            },
            pytest.approx(0.144, abs=1e-9),
        ),
        (
            "valuation_capm",
            {"method": "capm", "risk_free_rate": 0.04, "beta": 1.0, "market_return": 0.10},
            pytest.approx(0.10),
        ),
        (
            "valuation_core",
            {"method": "scorecard", "average_valuation": 1500000, "weights": [1.0], "scores": [1.2]},
            1800000.0,
        ),
        ("valuation_saas", {"method": "ltv", "arpu": 100, "gross_margin": 0.8, "churn_rate": 0.02}, 4000.0),
        ("valuation_marketplace", {"method": "take_rate", "revenue": 15, "gmv": 100}, pytest.approx(0.15)),
        ("valuation_emerging", {"method": "metcalfe", "n": 100}, 10000.0),
    ],
)
def test_dispatch_values(tool, arguments, expected):
    result = ts.call_tool(tool, arguments)
    assert result["value"] == expected


def test_scenario_adapter_builds_scenario_objects():
    result = ts.call_tool(
        "valuation_advanced",
        {
            "method": "scenario_analysis",
            "scenarios": [
                {"name": "bull", "probability": 0.5, "value": 100},
                {"name": "bear", "probability": 0.5, "value": 20},
            ],
        },
    )
    assert result["value"] == 60.0


def test_compound_method_triangulated():
    result = ts.call_tool(
        "valuation_core",
        {
            "method": "triangulated",
            "average_valuation": 1500000,
            "weights": [1.0],
            "scores": [1.2],
            "terminal_value": 5000000,
            "target_return": 10,
            "investment": 500000,
        },
    )
    assert result["value"] == 900000.0
    assert {"scorecard", "vc_post_money", "vc_pre_money"} <= set(result)


def test_missing_required_parameter_raises():
    with pytest.raises(ValueError, match="requires parameter"):
        ts.call_tool("valuation_saas", {"method": "ltv"})


def test_unknown_method_and_tool_raise():
    with pytest.raises(ValueError, match="Unknown method"):
        ts.call_tool("valuation_saas", {"method": "does_not_exist"})
    with pytest.raises(ValueError, match="Tool not found"):
        ts.call_tool("does_not_exist", {"method": "x"})


def test_stdio_surface_parity_with_spec():
    pytest.importorskip("fastmcp")
    import asyncio

    from startup_valuation.mcp import server

    tools = {t.name: t for t in asyncio.run(server.mcp.list_tools())}
    assert set(tools) == set(EXPECTED_TOOLS)
    for name, tool in tools.items():
        spec = next(t for t in ts.list_tools() if t["name"] == name)
        assert tool.description == spec["description"]
        assert tool.title == spec["title"]
        assert tool.annotations is not None
        annotations = tool.annotations
        read_only = getattr(annotations, "read_only_hint", getattr(annotations, "readOnlyHint", None))
        open_world = getattr(annotations, "open_world_hint", getattr(annotations, "openWorldHint", None))
        assert read_only is True
        assert open_world is False
        schema = tool.parameters  # JSON Schema produced by FastMCP
        spec_props = set(spec["inputSchema"]["properties"])
        assert set(schema["properties"]) == spec_props, name


def test_every_method_argument_is_in_target_signature():
    """Every advertised argument name must exist on the function the method calls.

    A method whose ``args``/``opt`` keys do not match the target's signature raises
    TypeError on the first call — which is how `expected_value_continuous` shipped
    binding `lower`/`upper` to a function taking `a`/`b`.
    """
    import inspect

    failures = []
    for tool in ts.TOOLS:
        for method in tool.get("methods") or []:
            if not method.get("module"):
                continue  # compound/aggregate entries are not dispatched directly
            fn, _injected = ts._resolve(method["module"], method["function"])
            parameters = set(inspect.signature(fn).parameters)
            for mapping in ("args", "opt"):
                for fn_param in method.get(mapping) or {}:
                    if fn_param not in parameters:
                        failures.append(
                            f"{tool['name']}.{method['key']}: '{fn_param}' is not a parameter of "
                            f"{method['module']}.{method['function']}({', '.join(sorted(parameters))})"
                        )
    assert not failures, "\n".join(failures)


@pytest.mark.parametrize(
    ("tool_name", "arguments"),
    [
        ("valuation_probability", {"method": "expected_value_continuous", "lower": -1.0, "upper": 1.0}),
        (
            "valuation_stakeholder",
            {
                "method": "pwerm",
                "pwerm_scenarios": [
                    {"probability": 0.20, "common_value": 92_000_000},
                    {"probability": 0.50, "common_value": 55_000_000},
                    {"probability": 0.20, "common_value": 4_000_000},
                    {"probability": 0.10, "common_value": 0},
                ],
            },
        ),
        (
            "valuation_stakeholder",
            {
                "method": "employee_option",
                "employee_option_scenarios": [
                    {"probability": 0.20, "fmv": 10.0, "strike": 1.0, "shares": 50_000},
                    {"probability": 0.50, "fmv": 5.0, "strike": 1.0, "shares": 50_000},
                    {"probability": 0.30, "fmv": 1.0, "strike": 1.0, "shares": 50_000},
                ],
            },
        ),
        (
            "valuation_biotech",
            {
                "method": "pipeline",
                "drugs": [{"peak_sales": 2_000_000_000, "multiple": 5, "p_success": 0.60, "years_to_peak": 2}],
                "discount_rate": 0.12,
            },
        ),
    ],
)
def test_methods_advertised_but_unreachable_now_dispatch(tool_name, arguments):
    """Regression: these four methods could not execute through the tool surface."""
    result = ts.call_tool(tool_name, arguments)
    assert isinstance(result["value"], (int, float))
