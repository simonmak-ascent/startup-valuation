"""Vercel serverless generic calculator endpoint.

POST /api/calculate
Body: { "method": "scorecard", "params": { ... } }
Response: CalculatorResponse with value, steps, formula reference, audit meta.
"""

import json as _json
import os as _os
import sys as _sys
import time as _time

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from startup_valuation import capm, comparables, core, marketplace, probability, saas, stakeholders, tv  # noqa: E402

LIBRARY_VERSION = "1.0.2"
_AVAILABLE_METHODS: list[str] = []


def _unwrap(r):
    return {
        "value": r.value,
        "method": r.method,
        "inputs": r.inputs,
        "assumptions": r.assumptions,
        "chapter": r.chapter,
        "formula_number": r.formula_number,
        "steps": r.steps,
    }


_NAMED_TOOLS: dict[str, tuple] = {
    # Core
    "scorecard": (core.scorecard_valuation, ["average_valuation", "weights", "scores"]),
    "berkus": (
        core.berkus_valuation,
        ["sound_idea", "prototype", "quality_team", "strategic_relationships", "product_rollout"],
    ),
    "risk_factor": (core.risk_factor_summation, ["base_valuation", "risk_ratings"]),
    "vc_post_money": (core.vc_method_post_money, ["terminal_value", "target_return"]),
    "vc_pre_money": (core.vc_method_pre_money, ["post_money", "investment"]),
    "terminal_value": (core.terminal_value_multiple, ["projected_revenue", "multiple"]),
    # SaaS
    "saas_ltv": (saas.ltv_saas, ["arpu", "gross_margin", "churn_rate"]),
    "saas_cac": (saas.cac, ["sales_marketing_expense", "new_customers"]),
    "saas_mrr": (saas.mrr, ["arr_value"]),
    "saas_arr": (saas.arr, ["subscription_values"]),
    "saas_nrr": (saas.net_revenue_retention, ["starting_revenue", "ending_revenue", "expansion_revenue"]),
    "saas_magic_number": (saas.magic_number, ["net_new_arr", "sm_expense_prior"]),
    "saas_rule_of_40": (saas.rule_of_40, ["growth_rate", "profit_margin"]),
    "saas_cac_payback": (saas.cac_payback_period, ["cac", "mrr_per_customer", "gross_margin"]),
    "saas_revenue_multiple": (saas.saas_revenue_multiple_valuation, ["arr", "multiple"]),
    # Comparables
    "pe_ratio": (comparables.pe_ratio, ["market_cap", "net_income"]),
    "ps_ratio": (comparables.ps_ratio, ["market_cap", "revenue"]),
    "ev_ebitda": (comparables.ev_ebitda, ["enterprise_value", "ebitda"]),
    "ev_revenue": (comparables.ev_revenue, ["enterprise_value", "revenue"]),
    "target_multiple": (comparables.target_valuation_multiple, ["multiple", "metric"]),
    # CAPM
    "capm": (capm.capm, ["risk_free_rate", "beta", "market_return"]),
    "startup_capm": (
        capm.startup_adjusted_capm,
        ["risk_free_rate", "beta", "market_risk_premium", "size_premium", "illiquidity_premium"],
    ),
    "portfolio_beta": (capm.portfolio_beta, ["weights", "betas"]),
    "portfolio_variance": (capm.portfolio_variance, ["weights", "covariance_matrix"]),
    # Time value
    "present_value": (tv.present_value, ["future_value", "rate", "periods"]),
    "npv": (tv.net_present_value, ["cash_flows", "rate"]),
    "annuity": (tv.annuity_present_value, ["payment", "rate", "periods"]),
    # Probability
    "expected_value": (probability.expected_value_discrete, ["outcomes", "probabilities"]),
    "joint_probability": (probability.joint_probability, ["probabilities"]),
    "prob_weighted": (probability.probability_weighted_value, ["outcomes", "probabilities"]),
    "portfolio_return": (probability.portfolio_expected_return, ["weights", "returns"]),
    "poisson": (probability.poisson_probability, ["lambda_", "k"]),
    # Stakeholders
    "dilution": (stakeholders.single_round_dilution, ["ownership_before", "investment", "post_money"]),
    "multi_dilution": (stakeholders.multi_round_dilution, ["initial_ownership", "investments", "post_money_vals"]),
    "common_discount": (stakeholders.common_stock_discount, ["preferred_value", "common_value"]),
    "liquidation": (stakeholders.liquidation_value, ["assets", "recovery_rates"]),
    "acquisition": (
        stakeholders.acquisition_value,
        ["standalone_value", "revenue_synergies", "cost_synergies", "integration_costs", "prob_revenue", "prob_cost"],
    ),
    "opm": (
        stakeholders.opm_common_stock,
        ["enterprise_value", "liquidation_preference", "time_to_exit", "volatility", "risk_free_rate"],
    ),
    "pwerm": (stakeholders.pwerm, ["scenarios"]),
    "venture_debt": (stakeholders.venture_debt_dilution, ["warrant_coverage", "loan_amount", "post_money"]),
    # Marketplace
    "gmv": (marketplace.gmv, ["transaction_values"]),
    "take_rate": (marketplace.take_rate, ["revenue", "gmv"]),
    "liquidity": (marketplace.liquidity, ["successful_transactions", "total_attempts"]),
    "gmv_multiple": (marketplace.gmv_multiple_valuation, ["gmv", "multiple"]),
    "network_value": (marketplace.network_value, ["active_users", "k", "alpha"]),
}

_AVAILABLE_METHODS = sorted(_NAMED_TOOLS.keys())


def _error(status, code, message, extra=None):
    body = {"error": code, "message": message}
    if extra:
        body.update(extra)
    return status, {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, _json.dumps(body).encode()


def calculate(method_name, params):
    if method_name not in _NAMED_TOOLS:
        return _error(400, "UNKNOWN_METHOD", f"Unknown method: {method_name}", {"available": _AVAILABLE_METHODS})

    func, param_names = _NAMED_TOOLS[method_name]

    missing = [p for p in param_names if p not in params]
    if missing:
        return _error(
            400, "VALIDATION_ERROR", "Missing required parameters", {"missing": missing, "required": param_names}
        )

    try:
        kwargs = {p: params[p] for p in param_names}
        result = func(**kwargs)
    except Exception as e:
        return _error(500, "COMPUTATION_ERROR", str(e))

    unwrapped = _unwrap(result)
    unwrapped["library_version"] = LIBRARY_VERSION
    unwrapped["timestamp"] = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime())
    unwrapped["git_commit"] = _os.environ.get("VERCEL_GIT_COMMIT_SHA", "")
    unwrapped["audit_status"] = "skipped"

    return (
        200,
        {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        _json.dumps(unwrapped).encode(),
    )


def handle_request(http_method, _path, body_raw):
    if http_method == "OPTIONS":
        return (
            200,
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            b"{}",
        )
    if http_method == "GET":
        return (
            200,
            {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            _json.dumps(
                {
                    "status": "ok",
                    "version": LIBRARY_VERSION,
                    "methods": len(_AVAILABLE_METHODS),
                    "available": _AVAILABLE_METHODS,
                }
            ).encode(),
        )
    if http_method != "POST":
        return 405, {"Content-Type": "application/json"}, b"{}"

    body = _json.loads(body_raw) if body_raw else {}
    method = body.get("method", "")
    params = body.get("params", {})

    if not method:
        return _error(400, "VALIDATION_ERROR", "method is required")

    return calculate(method, params)


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

    def do_OPTIONS(self):
        code, headers, body = handle_request("OPTIONS", self.path, None)
        self.send_response(code)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)
