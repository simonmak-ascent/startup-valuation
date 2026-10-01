"""Vercel serverless MCP endpoint for startup-valuation — 14 folded tools, prompts and resources.

The tool surface is defined once in ``startup_valuation/mcp/tool_surface.py`` and shared
with the stdio server, so the hosted endpoint and the local server advertise
byte-identical tool definitions (name, title, description, JSON Schemas,
annotations). Model Context Protocol (MCP) JSON-RPC 2.0 over POST:

* ``initialize``   — handshake
* ``tools/list``   — 14 tool definitions
* ``tools/call``   — execute a tool by name
* ``prompts/list`` / ``prompts/get``       — guided valuation workflows
* ``resources/list`` / ``resources/read`` — the method catalog
"""

import json as _json
import os as _os
import sys as _sys

_ROOT = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
# Repo root (for a bundled src/ tree) and src/ (so `startup_valuation` resolves
# whether or not the package is pip-installed in the function environment).
_sys.path.insert(0, _os.path.join(_ROOT, "src"))
_sys.path.insert(0, _ROOT)

from startup_valuation.mcp import agent_guides  # noqa: E402
from startup_valuation.mcp.tool_surface import (  # noqa: E402
    SERVER_NAME,
    SERVER_VERSION,
    call_tool,
    list_tools,
    tool_count,
)

PROTOCOL_VERSION = "2025-06-18"

_CORS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Accept, MCP-Protocol-Version",
}


def _ok(payload: dict) -> tuple:
    return 200, _CORS, _json.dumps(payload).encode()


def _rpc_result(req_id, result) -> tuple:
    return _ok({"jsonrpc": "2.0", "id": req_id, "result": result})


def _rpc_error(req_id, code: int, message: str) -> tuple:
    return _ok({"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}})


def handle_request(http_method: str, _path: str, body_raw: str | None) -> tuple:
    if http_method == "GET":
        return _ok(
            {
                "status": "ok",
                "server": SERVER_NAME,
                "version": SERVER_VERSION,
                "protocolVersion": PROTOCOL_VERSION,
                "transport": "streamable-http",
                "tools": tool_count(),
            }
        )
    if http_method == "OPTIONS":
        return 200, _CORS, b"{}"
    if http_method != "POST":
        return 405, {"Content-Type": "application/json"}, b"{}"

    try:
        body = _json.loads(body_raw) if body_raw else {}
    except _json.JSONDecodeError:
        return _rpc_error(None, -32700, "Parse error")

    req_method = body.get("method", "")
    req_id = body.get("id")

    if req_method == "initialize":
        return _rpc_result(
            req_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "capabilities": {
                    "tools": {"listChanged": False},
                    "prompts": {"listChanged": False},
                    "resources": {"listChanged": False, "subscribe": False},
                },
                "instructions": (
                    "Startup valuation calculators: 14 tools covering probability, time value, "
                    "CAPM, core pre-revenue methods, options, comparables, SaaS, marketplaces, "
                    "fintech, biotech, hardware, international, stakeholder equity, and emerging "
                    "methods. Select a formula with the `method` argument. Read the resource "
                    f"{agent_guides.CATALOG_URI} for every method's required parameters, or use a "
                    "prompt (value_pre_revenue_startup, value_saas_startup, model_funding_round) "
                    "for a guided multi-method workflow."
                ),
            },
        )
    if req_method in ("notifications/initialized", "notifications/cancelled"):
        return 202, {"Content-Type": "application/json"}, b"{}"
    if req_method == "ping":
        return _rpc_result(req_id, {})
    if req_method == "tools/list":
        return _rpc_result(req_id, {"tools": list_tools()})
    if req_method == "tools/call":
        params = body.get("params", {})
        name = params.get("name", "")
        arguments = params.get("arguments", {}) or {}
        try:
            result = call_tool(name, arguments)
        except ValueError as exc:
            return _rpc_error(req_id, -32602, str(exc))
        except Exception as exc:  # noqa: BLE001 — surface any computation error to the client
            return _rpc_error(req_id, -32603, str(exc))
        return _rpc_result(
            req_id,
            {"content": [{"type": "text", "text": _json.dumps(result)}], "structuredContent": result},
        )

    if req_method == "prompts/list":
        return _rpc_result(req_id, {"prompts": agent_guides.list_prompts()})
    if req_method == "prompts/get":
        params = body.get("params", {})
        try:
            return _rpc_result(req_id, agent_guides.get_prompt(params.get("name", ""), params.get("arguments")))
        except ValueError as exc:
            return _rpc_error(req_id, -32602, str(exc))
    if req_method == "resources/list":
        return _rpc_result(req_id, {"resources": agent_guides.list_resources()})
    if req_method == "resources/templates/list":
        return _rpc_result(req_id, {"resourceTemplates": []})
    if req_method == "resources/read":
        try:
            return _rpc_result(req_id, agent_guides.read_resource(body.get("params", {}).get("uri", "")))
        except ValueError as exc:
            return _rpc_error(req_id, -32002, str(exc))

    return _rpc_error(req_id, -32601, f"Unknown method: {req_method}")


from http.server import BaseHTTPRequestHandler  # noqa: E402


class handler(BaseHTTPRequestHandler):  # noqa: N801
    def _respond(self, code, headers, body):
        self.send_response(code)
        for key, value in headers.items():
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        self._respond(*handle_request("GET", self.path, None))

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(length).decode() if length else "{}"
        self._respond(*handle_request("POST", self.path, body_raw))

    def do_OPTIONS(self):  # noqa: N802
        self._respond(*handle_request("OPTIONS", self.path, None))
