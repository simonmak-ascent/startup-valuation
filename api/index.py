"""Vercel serverless MCP server for startup-valuation — 45+ tools."""

import json as _json
import os as _os
import sys as _sys

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))

from startup_valuation import capm, comparables, core, marketplace, probability, saas, stakeholders, tv  # noqa: E402

LIBRARY_VERSION = "1.0.2"
TOTAL_LIBRARY_TOOLS = 62  # full library (including advanced, biotech, etc.)
PURE_PYTHON_MODULES = ["core", "saas", "comparables", "capm", "tv", "probability", "stakeholders", "marketplace"]
FULL_LIBRARY_MODULES = ["advanced", "biotech", "fintech", "hardware", "international", "emerging"]


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


# fmt: off
TOOLS = {
    # === Core ===
    "valuation_scorecard": {
        "fn": lambda average_valuation, weights, scores: _unwrap(core.scorecard_valuation(average_valuation, weights, scores)),
        "schema": {"average_valuation": "number", "weights": "array", "scores": "array"},
        "description": "Scorecard valuation method: adjust average valuation by weighted factor scores for pre-revenue startups.",
    },
    "valuation_berkus": {
        "fn": lambda sound_idea, prototype, quality_team, strategic_relationships, product_rollout: _unwrap(
            core.berkus_valuation(sound_idea, prototype, quality_team, strategic_relationships, product_rollout)
        ),
        "schema": {"sound_idea": "number", "prototype": "number", "quality_team": "number", "strategic_relationships": "number", "product_rollout": "number"},
        "description": "Berkus Method: value a pre-revenue startup based on 5 key risk factors ($0–$500K each).",
    },
    "valuation_risk_factor": {
        "fn": lambda base_valuation, risk_ratings: _unwrap(core.risk_factor_summation(base_valuation, risk_ratings)),
        "schema": {"base_valuation": "number", "risk_ratings": "array"},
        "description": "Risk Factor Summation: adjust baseline valuation by 12 risk factors, each ±$250K per unit.",
    },
    "valuation_vc_post_money": {
        "fn": lambda terminal_value, target_return: _unwrap(core.vc_method_post_money(terminal_value, target_return)),
        "schema": {"terminal_value": "number", "target_return": "number"},
        "description": "VC Method (Post-Money): discount terminal value by target return multiple.",
    },
    "valuation_vc_pre_money": {
        "fn": lambda post_money, investment: _unwrap(core.vc_method_pre_money(post_money, investment)),
        "schema": {"post_money": "number", "investment": "number"},
        "description": "VC Method (Pre-Money): subtract investment from post-money valuation.",
    },
    "valuation_terminal_value": {
        "fn": lambda projected_revenue, multiple: _unwrap(core.terminal_value_multiple(projected_revenue, multiple)),
        "schema": {"projected_revenue": "number", "multiple": "number"},
        "description": "Terminal Value (Exit Multiple): multiply projected revenue by industry exit multiple.",
    },
    # === SaaS ===
    "valuation_saas_ltv": {
        "fn": lambda arpu, gross_margin, churn_rate: _unwrap(saas.ltv_saas(arpu, gross_margin, churn_rate)),
        "schema": {"arpu": "number", "gross_margin": "number", "churn_rate": "number"},
        "description": "SaaS LTV: Lifetime Value = ARPU × Gross Margin ÷ Monthly Churn.",
    },
    "valuation_saas_cac": {
        "fn": lambda sales_marketing_expense, new_customers: _unwrap(saas.cac(sales_marketing_expense, int(new_customers))),
        "schema": {"sales_marketing_expense": "number", "new_customers": "number"},
        "description": "SaaS CAC: Customer Acquisition Cost = Sales & Marketing Expense ÷ New Customers.",
    },
    "valuation_saas_mrr": {
        "fn": lambda total_customers, arpu: _unwrap(saas.mrr(total_customers, arpu)),
        "schema": {"total_customers": "number", "arpu": "number"},
        "description": "SaaS MRR: Monthly Recurring Revenue = Total Customers × ARPU.",
    },
    "valuation_saas_arr": {
        "fn": lambda mrr: _unwrap(saas.arr(mrr)),
        "schema": {"mrr": "number"},
        "description": "SaaS ARR: Annual Recurring Revenue = MRR × 12.",
    },
    "valuation_saas_nrr": {
        "fn": lambda starting_arr, expansion_arr, contraction_arr, churn_arr: _unwrap(saas.net_revenue_retention(starting_arr, expansion_arr, contraction_arr, churn_arr)),
        "schema": {"starting_arr": "number", "expansion_arr": "number", "contraction_arr": "number", "churn_arr": "number"},
        "description": "SaaS NRR: Net Revenue Retention = (Start + Expansion - Contraction - Churn) / Start.",
    },
    "valuation_saas_magic_number": {
        "fn": lambda net_new_arr, sm_expense_prior: _unwrap(saas.magic_number(net_new_arr, sm_expense_prior)),
        "schema": {"net_new_arr": "number", "sm_expense_prior": "number"},
        "description": "SaaS Magic Number: Net New ARR ÷ Prior Quarter S&M Expense.",
    },
    "valuation_saas_rule_of_40": {
        "fn": lambda growth_rate, profit_margin: _unwrap(saas.rule_of_40(growth_rate, profit_margin)),
        "schema": {"growth_rate": "number", "profit_margin": "number"},
        "description": "SaaS Rule of 40: Revenue Growth Rate + Profit Margin ≥ 40%.",
    },
    "valuation_saas_cac_payback": {
        "fn": lambda cac, arpu, gross_margin: _unwrap(saas.cac_payback_period(cac, arpu, gross_margin)),
        "schema": {"cac": "number", "arpu": "number", "gross_margin": "number"},
        "description": "SaaS CAC Payback Period: Months to recover CAC from customer gross profit.",
    },
    "valuation_saas_revenue_multiple": {
        "fn": lambda arr, revenue_multiple: _unwrap(saas.saas_revenue_multiple_valuation(arr, revenue_multiple)),
        "schema": {"arr": "number", "revenue_multiple": "number"},
        "description": "SaaS Revenue Multiple Valuation: ARR × Market Revenue Multiple.",
    },
    # === Comparables ===
    "valuation_pe_ratio": {
        "fn": lambda price, earnings_per_share: _unwrap(comparables.pe_ratio(price, earnings_per_share)),
        "schema": {"price": "number", "earnings_per_share": "number"},
        "description": "P/E Ratio: Price per Share ÷ Earnings per Share.",
    },
    "valuation_ps_ratio": {
        "fn": lambda market_cap, revenue: _unwrap(comparables.ps_ratio(market_cap, revenue)),
        "schema": {"market_cap": "number", "revenue": "number"},
        "description": "P/S Ratio: Market Capitalization ÷ Revenue.",
    },
    "valuation_ev_ebitda": {
        "fn": lambda enterprise_value, ebitda: _unwrap(comparables.ev_ebitda(enterprise_value, ebitda)),
        "schema": {"enterprise_value": "number", "ebitda": "number"},
        "description": "EV/EBITDA: Enterprise Value ÷ EBITDA.",
    },
    "valuation_ev_revenue": {
        "fn": lambda enterprise_value, revenue: _unwrap(comparables.ev_revenue(enterprise_value, revenue)),
        "schema": {"enterprise_value": "number", "revenue": "number"},
        "description": "EV/Revenue: Enterprise Value ÷ Revenue.",
    },
    "valuation_regression_multiple": {
        "fn": lambda intercept, growth_coef, growth, margin_coef, margin: _unwrap(
            comparables.regression_adjusted_multiple(intercept, growth_coef, growth, margin_coef, margin)
        ),
        "schema": {"intercept": "number", "growth_coef": "number", "growth": "number", "margin_coef": "number", "margin": "number"},
        "description": "Regression-Adjusted Multiple: statistical multiple adjusted for growth and margin factors.",
    },
    "valuation_target_multiple": {
        "fn": lambda comparable_multiple, target_metric: _unwrap(comparables.target_valuation_multiple(comparable_multiple, target_metric)),
        "schema": {"comparable_multiple": "number", "target_metric": "number"},
        "description": "Target Valuation: Comparable Multiple × Target Company Metric.",
    },
    # === CAPM ===
    "valuation_capm": {
        "fn": lambda risk_free_rate, beta, market_risk_premium: _unwrap(capm.capm(risk_free_rate, beta, market_risk_premium)),
        "schema": {"risk_free_rate": "number", "beta": "number", "market_risk_premium": "number"},
        "description": "CAPM: Cost of Equity = Rf + β × (Rm − Rf).",
    },
    "valuation_startup_capm": {
        "fn": lambda risk_free_rate, beta, market_risk_premium, size_premium, specific_risk: _unwrap(
            capm.startup_adjusted_capm(risk_free_rate, beta, market_risk_premium, size_premium, specific_risk)
        ),
        "schema": {"risk_free_rate": "number", "beta": "number", "market_risk_premium": "number", "size_premium": "number", "specific_risk": "number"},
        "description": "Startup-Adjusted CAPM: adds size premium and company-specific risk premium.",
    },
    "valuation_portfolio_beta": {
        "fn": lambda weights, betas: _unwrap(capm.portfolio_beta(weights, betas)),
        "schema": {"weights": "array", "betas": "array"},
        "description": "Portfolio Beta: weighted average of individual asset betas.",
    },
    "valuation_portfolio_variance": {
        "fn": lambda weights, variances, covariance_matrix: _unwrap(capm.portfolio_variance(weights, variances, covariance_matrix)),
        "schema": {"weights": "array", "variances": "array", "covariance_matrix": "array"},
        "description": "Portfolio Variance: weighted variance with covariance adjustments.",
    },
    # === Time Value ===
    "valuation_present_value": {
        "fn": lambda future_value, rate, periods: _unwrap(tv.present_value(future_value, rate, periods)),
        "schema": {"future_value": "number", "rate": "number", "periods": "number"},
        "description": "Present Value: PV = FV ÷ (1 + r)^n.",
    },
    "valuation_npv": {
        "fn": lambda initial_investment, cash_flows, rate: _unwrap(tv.net_present_value(initial_investment, cash_flows, rate)),
        "schema": {"initial_investment": "number", "cash_flows": "array", "rate": "number"},
        "description": "Net Present Value: NPV = −Investment + Σ CF_t ÷ (1 + r)^t.",
    },
    "valuation_annuity": {
        "fn": lambda payment, rate, periods: _unwrap(tv.annuity_present_value(payment, rate, periods)),
        "schema": {"payment": "number", "rate": "number", "periods": "number"},
        "description": "Annuity Present Value: PV of equal periodic payments.",
    },
    # === Probability ===
    "valuation_expected_value": {
        "fn": lambda outcomes, probabilities: _unwrap(probability.expected_value_discrete(outcomes, probabilities)),
        "schema": {"outcomes": "array", "probabilities": "array"},
        "description": "Expected Value (Discrete): Σ outcome_i × probability_i.",
    },
    "valuation_joint_probability": {
        "fn": lambda prob_a, prob_b, independent: _unwrap(probability.joint_probability(prob_a, prob_b, independent)),
        "schema": {"prob_a": "number", "prob_b": "number", "independent": "boolean"},
        "description": "Joint Probability: P(A∩B) = P(A)×P(B) if independent, else P(A|B)×P(B).",
    },
    "valuation_prob_weighted": {
        "fn": lambda scenarios: _unwrap(probability.probability_weighted_value(scenarios)),
        "schema": {"scenarios": "array"},
        "description": "Probability-Weighted Value: Σ scenario_value × scenario_probability.",
    },
    "valuation_portfolio_return": {
        "fn": lambda weights, returns: _unwrap(probability.portfolio_expected_return(weights, returns)),
        "schema": {"weights": "array", "returns": "array"},
        "description": "Portfolio Expected Return: weighted average of individual asset returns.",
    },
    "valuation_poisson": {
        "fn": lambda rate, k: _unwrap(probability.poisson_probability(rate, k)),
        "schema": {"rate": "number", "k": "number"},
        "description": "Poisson Probability: probability of k events given rate λ (uses scipy.stats).",
    },
    # === Stakeholders ===
    "valuation_dilution": {
        "fn": lambda ownership_before, investment, post_money: _unwrap(stakeholders.single_round_dilution(ownership_before, investment, post_money)),
        "schema": {"ownership_before": "number", "investment": "number", "post_money": "number"},
        "description": "Single-Round Dilution: calculate ownership dilution from a funding round.",
    },
    "valuation_multi_dilution": {
        "fn": lambda initial_ownership, investments, post_money_vals: _unwrap(stakeholders.multi_round_dilution(initial_ownership, investments, post_money_vals)),
        "schema": {"initial_ownership": "number", "investments": "array", "post_money_vals": "array"},
        "description": "Multi-Round Dilution: cumulative ownership dilution across multiple funding rounds.",
    },
    "valuation_common_discount": {
        "fn": lambda preferred_price, discount_rate: _unwrap(stakeholders.common_stock_discount(preferred_price, discount_rate)),
        "schema": {"preferred_price": "number", "discount_rate": "number"},
        "description": "Common Stock Discount: Common = Preferred × (1 − Discount).",
    },
    "valuation_liquidation": {
        "fn": lambda assets, recovery_rates: _unwrap(stakeholders.liquidation_value(assets, recovery_rates)),
        "schema": {"assets": "array", "recovery_rates": "array"},
        "description": "Liquidation Value: weighted recovery value of assets in liquidation scenario.",
    },
    "valuation_acquisition": {
        "fn": lambda standalone_value, revenue_synergies, cost_synergies, integration_costs, prob_revenue, prob_cost: _unwrap(
            stakeholders.acquisition_value(standalone_value, revenue_synergies, cost_synergies, integration_costs, prob_revenue, prob_cost)
        ),
        "schema": {"standalone_value": "number", "revenue_synergies": "number", "cost_synergies": "number", "integration_costs": "number", "prob_revenue": "number", "prob_cost": "number"},
        "description": "Acquisition Value: value of target company in an M&A transaction.",
    },
    "valuation_opm": {
        "fn": lambda strike_price, current_value, volatility, time_to_exit, risk_free_rate: _unwrap(
            stakeholders.opm_common_stock(strike_price, current_value, volatility, time_to_exit, risk_free_rate)
        ),
        "schema": {"strike_price": "number", "current_value": "number", "volatility": "number", "time_to_exit": "number", "risk_free_rate": "number"},
        "description": "OPM Common Stock: Option-Pricing Model for common stock valuation (uses scipy.stats.norm).",
    },
    "valuation_pwerm": {
        "fn": lambda scenarios: _unwrap(stakeholders.pwerm(scenarios)),
        "schema": {"scenarios": "array"},
        "description": "PWERM: Probability-Weighted Expected Return Method for multi-scenario valuation. Each scenario: {probability, value}.",
    },
    "valuation_venture_debt": {
        "fn": lambda warrant_coverage, loan_amount, post_money: _unwrap(
            stakeholders.venture_debt_dilution(warrant_coverage, loan_amount, post_money)
        ),
        "schema": {"warrant_coverage": "number", "loan_amount": "number", "post_money": "number"},
        "description": "Venture Debt Dilution: dilution impact of venture debt warrants on equity value.",
    },
    # === Marketplace ===
    "valuation_gmv": {
        "fn": lambda total_transactions, avg_transaction_value: _unwrap(marketplace.gmv(total_transactions, avg_transaction_value)),
        "schema": {"total_transactions": "number", "avg_transaction_value": "number"},
        "description": "GMV: Gross Merchandise Value = Total Transactions × Average Transaction Value.",
    },
    "valuation_take_rate": {
        "fn": lambda revenue, gmv: _unwrap(marketplace.take_rate(revenue, gmv)),
        "schema": {"revenue": "number", "gmv": "number"},
        "description": "Take Rate: Revenue ÷ GMV — the platform's commission percentage.",
    },
    "valuation_liquidity": {
        "fn": lambda completed_transactions, total_listings: _unwrap(marketplace.liquidity(completed_transactions, total_listings)),
        "schema": {"completed_transactions": "number", "total_listings": "number"},
        "description": "Marketplace Liquidity: Completed Transactions ÷ Total Listings.",
    },
    "valuation_gmv_multiple": {
        "fn": lambda gmv, multiple: _unwrap(marketplace.gmv_multiple_valuation(gmv, multiple)),
        "schema": {"gmv": "number", "multiple": "number"},
        "description": "GMV Multiple Valuation: GMV × Market GMV Multiple.",
    },
    "valuation_network_value": {
        "fn": lambda active_users, k, alpha: _unwrap(marketplace.network_value(active_users, k, alpha)),
        "schema": {"active_users": "number", "k": "number", "alpha": "number"},
        "description": "Metcalfe's Law: Network Value ∝ n^α, approximated as k × n^α.",
    },
}
# fmt: on


def handle_request(http_method, _path, body_raw):
    body = _json.loads(body_raw) if body_raw else {}
    if http_method == "GET":
        return (
            200,
            {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            _json.dumps(
                {
                    "status": "ok",
                    "version": LIBRARY_VERSION,
                    "tools": len(TOOLS),
                    "pure_python_tools": len(TOOLS),
                    "full_library_tools": TOTAL_LIBRARY_TOOLS,
                    "pure_python_modules": PURE_PYTHON_MODULES,
                    "full_library_modules": FULL_LIBRARY_MODULES,
                }
            ).encode(),
        )
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
    if http_method != "POST":
        return 405, {"Content-Type": "application/json"}, b"{}"
    req_method = body.get("method", "")
    req_id = body.get("id")
    if req_method == "initialize":
        return (
            200,
            {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            _json.dumps(
                {
                    "jsonrpc": "2.0",
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "serverInfo": {"name": "startup-valuation", "version": LIBRARY_VERSION},
                        "capabilities": {"tools": {}},
                    },
                    "id": req_id,
                }
            ).encode(),
        )
    if req_method == "tools/list":
        tools = [
            {
                "name": n,
                "description": i.get("description", ""),
                "inputSchema": {"type": "object", "properties": {k: {"type": v} for k, v in i["schema"].items()}},
            }
            for n, i in TOOLS.items()
        ]
        return (
            200,
            {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
            _json.dumps({"jsonrpc": "2.0", "result": {"tools": tools}, "id": req_id}).encode(),
        )
    if req_method == "tools/call":
        params = body.get("params", {})
        name = params.get("name", "")
        args = params.get("arguments", {})
        tool = TOOLS.get(name)
        if not tool:
            return (
                200,
                {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                _json.dumps(
                    {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Tool not found: {name}"}, "id": req_id}
                ).encode(),
            )
        try:
            result = tool["fn"](**args)
            return (
                200,
                {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                _json.dumps(
                    {
                        "jsonrpc": "2.0",
                        "result": {"content": [{"type": "text", "text": _json.dumps(result)}]},
                        "id": req_id,
                    }
                ).encode(),
            )
        except Exception as e:
            return (
                200,
                {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
                _json.dumps({"jsonrpc": "2.0", "error": {"code": -32603, "message": str(e)}, "id": req_id}).encode(),
            )
    return (
        200,
        {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        _json.dumps(
            {"jsonrpc": "2.0", "error": {"code": -32601, "message": f"Unknown method: {req_method}"}, "id": req_id}
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

    def do_OPTIONS(self):
        code, headers, body = handle_request("OPTIONS", self.path, None)
        self.send_response(code)
        for k, v in headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)
