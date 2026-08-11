"""Vercel serverless MCP server for startup-valuation."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def dcf(revenue, growth_rate, discount_rate, terminal_growth=0.025, projection_years=5):
    cash_flows = [revenue * (1 + growth_rate) ** i for i in range(projection_years)]
    terminal_value = cash_flows[-1] * (1 + terminal_growth) / max(discount_rate - terminal_growth, 0.01)
    pv = sum(cf / (1 + discount_rate) ** (i + 1) for i, cf in enumerate(cash_flows))
    pv_terminal = terminal_value / (1 + discount_rate) ** projection_years
    ev = pv + pv_terminal
    eq = ev * 0.85
    return {
        "method": "DCF",
        "low": round(eq * 0.8, 2),
        "high": round(eq * 1.2, 2),
        "currency": "HKD",
        "assumptions": [f"revenue={revenue}", f"growth={growth_rate}", f"wacc={discount_rate}"],
        "value_low": round(eq * 0.8, 2),
        "value_high": round(eq * 1.2, 2),
    }


def market_multiple(revenue, ebitda=0, sector="technology"):
    mult = 8.0 if sector == "technology" else 6.0
    base = ebitda if ebitda > 0 else revenue * 0.25
    ev = base * mult
    return {
        "method": "Market Multiples",
        "low": round(ev * 0.8, 2),
        "high": round(ev * 1.2, 2),
        "currency": "HKD",
        "assumptions": [f"sector={sector}", f"multiple={mult}x EV/EBITDA"],
    }


TOOLS = {
    "valuation_dcf": {
        "fn": dcf,
        "schema": {
            "revenue": "number",
            "growth_rate": "number",
            "discount_rate": "number",
            "terminal_growth": "number",
            "projection_years": "integer",
        },
    },
    "valuation_market_multiple": {
        "fn": market_multiple,
        "schema": {"revenue": "number", "ebitda": "number", "sector": "string"},
    },
}


def handle_request(method, path, body_raw):
    body = json.loads(body_raw) if body_raw else {}
    if method == "GET" and path in ("/health", "/api/health"):
        return 200, {"Content-Type": "application/json"}, json.dumps({"status": "ok", "version": "1.0.2"}).encode()
    if method != "POST":
        return 405, {"Content-Type": "application/json"}, b"{}"
    req_method = body.get("method", "")
    if req_method == "initialize":
        return (
            200,
            {"Content-Type": "application/json"},
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "startup-valuation", "version": "1.0.2"},
                        "capabilities": {"tools": {}},
                    },
                    "id": body.get("id"),
                }
            ).encode(),
        )
    if req_method == "tools/list":
        tools = [
            {
                "name": n,
                "description": "",
                "inputSchema": {"type": "object", "properties": {k: {"type": v} for k, v in i["schema"].items()}},
            }
            for n, i in TOOLS.items()
        ]
        return (
            200,
            {"Content-Type": "application/json"},
            json.dumps({"jsonrpc": "2.0", "result": {"tools": tools}, "id": body.get("id")}).encode(),
        )
    if req_method == "tools/call":
        params = body.get("params", {})
        name = params.get("name", "")
        args = params.get("arguments", {})
        tool = TOOLS.get(name)
        if not tool:
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "error": {"code": -32601, "message": f"Tool not found: {name}"},
                        "id": body.get("id"),
                    }
                ).encode(),
            )
        try:
            result = tool["fn"](**args)
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "result": {"content": [{"type": "text", "text": json.dumps(result)}]},
                        "id": body.get("id"),
                    }
                ).encode(),
            )
        except Exception as e:
            return (
                200,
                {"Content-Type": "application/json"},
                json.dumps(
                    {"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": body.get("id")}
                ).encode(),
            )
    return (
        200,
        {"Content-Type": "application/json"},
        json.dumps(
            {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Unknown method: {req_method}"},
                "id": body.get("id"),
            }
        ).encode(),
    )


from http.server import BaseHTTPRequestHandler  # noqa: E402


class handler(BaseHTTPRequestHandler):  # noqa: N801
    def do_GET(self):
        code, headers, body = handle_request("GET", self.path, None)
        self.send_response(code)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(length).decode() if length else "{}"
        code, headers, body = handle_request("POST", self.path, body_raw)
        self.send_response(code)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)
