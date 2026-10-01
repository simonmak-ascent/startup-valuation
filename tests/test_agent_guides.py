"""Prompts, resources and input-default reporting on the MCP surface."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
import tomllib

from startup_valuation.mcp import agent_guides as g
from startup_valuation.mcp import tool_surface as ts

ROOT = Path(__file__).resolve().parents[1]


def test_catalog_lists_every_tool_and_method() -> None:
    catalog = json.loads(g.read_resource(g.CATALOG_URI)["contents"][0]["text"])
    assert [t["tool"] for t in catalog["tools"]] == [t["name"] for t in ts.TOOLS]
    for entry, tool in zip(catalog["tools"], ts.TOOLS, strict=True):
        assert [m["method"] for m in entry["methods"]] == [m["key"] for m in tool["methods"]]


def test_every_listed_resource_is_readable() -> None:
    for res in g.list_resources():
        content = g.read_resource(res["uri"])["contents"][0]
        assert content["mimeType"] == "application/json"
        json.loads(content["text"])
    with pytest.raises(ValueError):
        g.read_resource("startup-valuation://methods/nope")


@pytest.mark.parametrize("prompt", g.list_prompts(), ids=lambda p: p["name"])
def test_prompts_render_and_reference_real_methods(prompt: dict) -> None:
    args = {a["name"]: "example" for a in prompt["arguments"]}
    text = g.get_prompt(prompt["name"], args)["messages"][0]["content"]["text"]
    pairs = re.findall(r"call `(\w+)` with method=`(\w+)`", text)
    assert pairs, "prompt names no tool calls"
    for tool_name, method_key in pairs:
        tool = next(t for t in ts.TOOLS if t["name"] == tool_name)
        assert method_key in {m["key"] for m in tool["methods"]}


def test_prompt_requires_its_required_arguments() -> None:
    with pytest.raises(ValueError):
        g.get_prompt("value_saas_startup", {})


def test_defaults_applied_is_reported() -> None:
    result = ts.call_tool("valuation_core", {"method": "berkus", "sound_idea": 500_000})
    assert "prototype" in result["defaults_applied"]
    assert "sound_idea" not in result["defaults_applied"]


def test_all_defaults_is_rejected() -> None:
    with pytest.raises(ValueError, match="needs at least one of"):
        ts.call_tool("valuation_core", {"method": "berkus"})


def test_server_version_matches_pyproject() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    assert ts.SERVER_VERSION == project
    fallback = re.search(r'return "([\d.]+)"', (ROOT / "src/startup_valuation/mcp/tool_surface.py").read_text())
    assert fallback
    assert fallback.group(1) == project


def test_hosted_endpoint_serves_prompts_and_resources() -> None:
    import sys

    sys.path.insert(0, str(ROOT))
    from api.index import handle_request

    def rpc(method: str, params: dict | None = None) -> dict:
        _, _, body = handle_request(
            "POST", "/api", json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}})
        )
        return json.loads(body)

    caps = rpc("initialize")["result"]["capabilities"]
    assert {"tools", "prompts", "resources"} <= set(caps)
    assert len(rpc("prompts/list")["result"]["prompts"]) == len(g.PROMPTS)
    got = rpc("prompts/get", {"name": "model_funding_round", "arguments": {"round": "$2M SAFE at $10M cap"}})
    assert got["result"]["messages"][0]["role"] == "user"
    assert rpc("resources/read", {"uri": g.CATALOG_URI})["result"]["contents"]
    assert rpc("resources/read", {"uri": "x://y"})["error"]["code"] == -32002
