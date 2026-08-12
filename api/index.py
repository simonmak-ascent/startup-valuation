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
        "fn": lambda average_valuation, weights, scores: _unwrap(
            core.scorecard_valuation(average_valuation, weights, scores)
        ),
        "schema": {"average_valuation": "number", "weights": "array", "scores": "array"},
    },
    "valuation_berkus": {
        "fn": lambda sound_idea, prototype, quality_team, strategic_relationships, product_rollout: _unwrap(
            core.berkus_valuation(sound_idea, prototype, quality_team, strategic_relationships, product_rollout)
        ),
        "schema": {
            "sound_idea": "number",
            "prototype": "number",
            "quality_team": "number",
            "strategic_relationships": "number",
            "product_rollout": "number",
        },
    },
    "valuation_risk_factor": {
        "fn": lambda base_valuation, risk_ratings: _unwrap(core.risk_factor_summation(base_valuation, risk_ratings)),
        "schema": {"base_valuation": "number", "risk_ratings": "array"},
    },
    "valuation_vc_post_money": {
        "fn": lambda terminal_value, target_return: _unwrap(core.vc_method_post_money(terminal_value, target_return)),
        "schema": {"terminal_value": "number", "target_return": "number"},
    },
    "valuation_vc_pre_money": {
        "fn": lambda post_money, investment: _unwrap(core.vc_method_pre_money(post_money, investment)),
        "schema": {"post_money": "number", "investment": "number"},
    },
    "valuation_capm": {
        "fn": lambda risk_free_rate, beta, market_risk_premium: _unwrap(
            capm.capm(risk_free_rate, beta, market_risk_premium)
        ),
        "schema": {"risk_free_rate": "number", "beta": "number", "market_risk_premium": "number"},
    },
    "valuation_saas_ltv": {
        "fn": lambda arpu, gross_margin, churn_rate: _unwrap(saas.ltv_saas(arpu, gross_margin, churn_rate)),
        "schema": {"arpu": "number", "gross_margin": "number", "churn_rate": "number"},
    },
    "valuation_saas_magic_number": {
        "fn": lambda net_new_arr, sm_expense_prior: _unwrap(saas.magic_number(net_new_arr, sm_expense_prior)),
        "schema": {"net_new_arr": "number", "sm_expense_prior": "number"},
    },
    "valuation_saas_rule_of_40": {
        "fn": lambda growth_rate, profit_margin: _unwrap(saas.rule_of_40(growth_rate, profit_margin)),
        "schema": {"growth_rate": "number", "profit_margin": "number"},
    },
    "valuation_saas_cac": {
        "fn": lambda sales_marketing_expense, new_customers: _unwrap(
            saas.cac(sales_marketing_expense, int(new_customers))
        ),
        "schema": {"sales_marketing_expense": "number", "new_customers": "number"},
    },
    "valuation_present_value": {
        "fn": lambda future_value, rate, periods: _unwrap(tv.present_value(future_value, rate, periods)),
        "schema": {"future_value": "number", "rate": "number", "periods": "number"},
    },
    "valuation_expected_value": {
        "fn": lambda outcomes, probabilities: _unwrap(probability.expected_value_discrete(outcomes, probabilities)),
        "schema": {"outcomes": "array", "probabilities": "array"},
    },
    "valuation_pe_ratio": {
        "fn": lambda price, earnings_per_share: _unwrap(comparables.pe_ratio(price, earnings_per_share)),
        "schema": {"price": "number", "earnings_per_share": "number"},
    },
    "valuation_terminal_value": {
        "fn": lambda projected_revenue, multiple: _unwrap(core.terminal_value_multiple(projected_revenue, multiple)),
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
