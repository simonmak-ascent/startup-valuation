"""Vercel serverless generic calculator endpoint.

POST /api/calculate
Body: { "method": "scorecard", "params": { ... } }
Response: CalculatorResponse with value, steps, formula reference, audit meta.
"""

import json as _json
import logging as _logging
import math as _math
import os as _os
import sys as _sys
import time as _time

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

_LOGGER = _logging.getLogger("startup_valuation.api.calculate")

import startup_valuation as _startup_valuation  # noqa: E402
from startup_valuation import capm, comparables, core, marketplace, probability, saas, stakeholders, tv  # noqa: E402

# Single source of truth for the version this build reports: the package's own
# __version__, which the release lockstep keeps in step with pyproject.toml.
LIBRARY_VERSION = _startup_valuation.__version__

# Paths this deployment declares for the Python side of the API. The ALB maps them
# to the MCP (8021) and calculate (8020) containers. Until that mapping is corrected
# in apg-infra, each handler answers these paths and 404s every other one, so the
# Next.js routes under app/(en)/api/ are not shadowed by a 200 from here.
_OWNED_PATHS = frozenset({"/api", "/api/", "/api/calculate", "/api/health"})

_AVAILABLE_METHODS: list[str] = []

# In-memory sliding-window rate limiter (per warm Vercel instance).
_RATE_BUCKETS: dict[str, list[float]] = {}
_RATE_LIMIT = 60
_RATE_WINDOW_S = 60.0


def _rate_limited(key: str) -> bool:
    now = _time.time()
    window_start = now - _RATE_WINDOW_S
    timestamps = [t for t in _RATE_BUCKETS.get(key, []) if t > window_start]
    if len(timestamps) >= _RATE_LIMIT:
        _RATE_BUCKETS[key] = timestamps
        return True
    timestamps.append(now)
    _RATE_BUCKETS[key] = timestamps
    return False


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


def _non_finite_key(value: object, prefix: str = "") -> str | None:
    """Path to the first non-finite number in a payload, or None when all are finite."""
    if isinstance(value, bool):
        return None
    if isinstance(value, float):
        return prefix if not _math.isfinite(value) else None
    if isinstance(value, dict):
        for key, item in value.items():
            found = _non_finite_key(item, f"{prefix}.{key}" if prefix else str(key))
            if found:
                return found
    elif isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            found = _non_finite_key(item, f"{prefix}[{index}]")
            if found:
                return found
    return None


def calculate(method_name, params):
    if method_name not in _NAMED_TOOLS:
        return _error(400, "UNKNOWN_METHOD", f"Unknown method: {method_name}", {"available": _AVAILABLE_METHODS})

    func, param_names = _NAMED_TOOLS[method_name]

    missing = [p for p in param_names if p not in params]
    if missing:
        return _error(
            400, "VALIDATION_ERROR", "Missing required parameters", {"missing": missing, "required": param_names}
        )

    bad_input = _non_finite_key(params)
    if bad_input:
        return _error(400, "NON_FINITE_INPUT", f"Input '{bad_input}' must be a finite number")

    try:
        kwargs = {p: params[p] for p in param_names}
        result = func(**kwargs)
    except (TypeError, ValueError) as exc:
        return _error(400, "VALIDATION_ERROR", str(exc))
    except Exception:
        _LOGGER.exception("calculation failed: %s", method_name)
        return _error(500, "COMPUTATION_ERROR", "The calculation failed")

    try:
        unwrapped = _unwrap(result)
        unwrapped["library_version"] = LIBRARY_VERSION
        unwrapped["timestamp"] = _time.strftime("%Y-%m-%dT%H:%M:%SZ", _time.gmtime())
        unwrapped["git_commit"] = _os.environ.get("VERCEL_GIT_COMMIT_SHA", "")
        unwrapped["audit_status"] = "skipped"

        bad_output = _non_finite_key(unwrapped)
        if bad_output:
            return _error(422, "NON_FINITE_RESULT", f"Result '{bad_output}' is not a finite number")

        payload = _json.dumps(unwrapped, allow_nan=False).encode()
    except Exception:
        _LOGGER.exception("result could not be serialised: %s", method_name)
        return _error(500, "COMPUTATION_ERROR", "The result could not be serialised")

    return (
        200,
        {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        payload,
    )


def _health() -> tuple:
    """200 only when the library can actually compute; see api/index.py `_health`."""
    try:
        tv.present_value(100.0, 0.1, 1)
    except Exception:  # noqa: BLE001 — any failure means this instance cannot serve
        _LOGGER.exception("health probe failed")
        return 503, {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"}, b'{"status":"failing"}'
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


def handle_request(http_method, path, body_raw):
    if path and path.split("?", 1)[0] not in _OWNED_PATHS:
        return 404, {"Content-Type": "application/json"}, b'{"error":"NOT_FOUND"}'

    if http_method == "OPTIONS":
        return (
            200,
            {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, HEAD, POST, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type",
            },
            b"{}",
        )
    if http_method in ("GET", "HEAD"):
        return _health()
    if http_method != "POST":
        return 405, {"Content-Type": "application/json"}, b"{}"

    try:
        body = _json.loads(body_raw) if body_raw else {}
    except _json.JSONDecodeError:
        return _error(400, "PARSE_ERROR", "Request body is not valid JSON")
    if not isinstance(body, dict):
        return _error(400, "VALIDATION_ERROR", "Request body must be a JSON object")

    method = body.get("method", "")
    params = body.get("params") or {}
    if not isinstance(params, dict):
        return _error(400, "VALIDATION_ERROR", "params must be a JSON object")

    if _rate_limited("calculate"):
        return _error(429, "RATE_LIMITED", "Too many requests. Please try again later.")

    if not method:
        return _error(400, "VALIDATION_ERROR", "method is required")

    return calculate(method, params)


from http.server import BaseHTTPRequestHandler  # noqa: E402


class handler(BaseHTTPRequestHandler):  # noqa: N801
    def _respond(self, code, headers, body):
        self.send_response(code)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        self._respond(*handle_request("GET", self.path, None))

    def do_HEAD(self):  # noqa: N802
        self._respond(*handle_request("HEAD", self.path, None))

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        body_raw = self.rfile.read(length).decode() if length else "{}"
        self._respond(*handle_request("POST", self.path, body_raw))

    def do_OPTIONS(self):  # noqa: N802
        self._respond(*handle_request("OPTIONS", self.path, None))
