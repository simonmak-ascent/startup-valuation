"""Vercel serverless MCP server for startup-valuation."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import pure-Python library modules (no numpy/scipy required)
from startup_valuation import capm, comparables, core, probability, saas, tv  # noqa: E402


def _unwrap(r):
    """Unwrap ValuationResult to JSON-safe dict."""
    return {
        "value": r.value,
        "method": r.method,
        "inputs": r.inputs,
        "assumptions": r.assumptions,
        "chapter": r.chapter,
        "formula_number": r.formula_number,
    }


TOOLS = {
    "valuation_scorecard": {
        "fn": lambda avg, w, s: _unwrap(core.scorecard_valuation(avg, w, s)),
        "schema": {"average_valuation": "number", "weights": "array", "scores": "array"},
    },
    "valuation_berkus": {
        "fn": lambda si, pr, qt, sr, po: _unwrap(core.berkus_valuation(si, pr, qt, sr, po)),
        "schema": {
            "sound_idea": "number",
            "prototype": "number",
            "quality_team": "number",
            "strategic_relationships": "number",
            "product_rollout": "number",
        },
    },
    "valuation_risk_factor": {
        "fn": lambda bv, rr: _unwrap(core.risk_factor_summation(bv, rr)),
        "schema": {"base_valuation": "number", "risk_ratings": "array"},
    },
    "valuation_vc_post_money": {
        "fn": lambda tv, tr: _unwrap(core.vc_method_post_money(tv, tr)),
        "schema": {"terminal_value": "number", "target_return": "number"},
    },
    "valuation_vc_pre_money": {
        "fn": lambda pm, inv: _unwrap(core.vc_method_pre_money(pm, inv)),
        "schema": {"post_money": "number", "investment": "number"},
    },
    "valuation_capm": {
        "fn": lambda rf, beta, mrp: _unwrap(capm.capm(rf, beta, mrp)),
        "schema": {"risk_free_rate": "number", "beta": "number", "market_risk_premium": "number"},
    },
    "valuation_saas_ltv": {
        "fn": lambda arpu, gm, ch: _unwrap(saas.ltv_saas(arpu, gm, ch)),
        "schema": {"arpu": "number", "gross_margin": "number", "churn_rate": "number"},
    },
    "valuation_saas_magic_number": {
        "fn": lambda narr, sme: _unwrap(saas.magic_number(narr, sme)),
        "schema": {"net_new_arr": "number", "sm_expense_prior": "number"},
    },
    "valuation_saas_rule_of_40": {
        "fn": lambda gr, pm: _unwrap(saas.rule_of_40(gr, pm)),
        "schema": {"growth_rate": "number", "profit_margin": "number"},
    },
    "valuation_saas_cac": {
        "fn": lambda sme, nc: _unwrap(saas.cac(sme, nc)),
        "schema": {"sales_marketing_expense": "number", "new_customers": "integer"},
    },
    "valuation_present_value": {
        "fn": lambda fv, r, p: _unwrap(tv.present_value(fv, r, p)),
        "schema": {"future_value": "number", "rate": "number", "periods": "number"},
    },
    "valuation_expected_value": {
        "fn": lambda o, p: _unwrap(probability.expected_value_discrete(o, p)),
        "schema": {"outcomes": "array", "probabilities": "array"},
    },
    "valuation_pe_ratio": {
        "fn": lambda p, eps: _unwrap(comparables.pe_ratio(p, eps)),
        "schema": {"price": "number", "earnings_per_share": "number"},
    },
    "valuation_terminal_value": {
        "fn": lambda pr, m: _unwrap(core.terminal_value_multiple(pr, m)),
        "schema": {"projected_revenue": "number", "multiple": "number"},
    },
}


def handle_request(method, path, body_raw):
    body = json.loads(body_raw) if body_raw else {}
    if method == "GET":
        return (
            200,
            {"Content-Type": "application/json"},
            json.dumps({"status": "ok", "version": "1.0.2", "tools": len(TOOLS)}).encode(),
        )
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
