"""Canonical MCP tool surface for the Startup Valuation library.

Single source of truth for every MCP tool definition — descriptions,
parameter semantics, JSON Schemas, annotations, and dispatch. Both the
stdio server (``startup_valuation/mcp/server.py``) and the hosted HTTP endpoint
(``api/index.py``) consume this module, so the two surfaces cannot drift.

Design notes (Glama / TDQS Tool Definition Quality Score):

* Tools are **folded by valuation family** (15 tools) rather than one tool
  per formula (60). TDQS scores *Tool Count Appropriateness* 5/5 only in the
  3-15 band; a `method` enum selects the formula inside each tool.
* Every tool carries a ``title``, an ``outputSchema``, and MCP
  ``annotations``. All tools are pure calculators: read-only, idempotent,
  closed-world, non-destructive.
* Every parameter is documented here (name, type, meaning, units, default),
  which feeds the *Parameter Semantics* dimension.
* Purpose + when-to-use + alternatives are written per tool, feeding
  *Purpose Clarity*, *Usage Guidelines*, and *Contextual Completeness*.
"""

from __future__ import annotations

from typing import Any

from startup_valuation.types import Scenario

# --------------------------------------------------------------------------
# Shared shape
# --------------------------------------------------------------------------

SERVER_NAME = "startup-valuation"
SERVER_VERSION = "2.0.0"

#: Behaviour shared by every tool: pure arithmetic, no I/O.
COMMON_ANNOTATIONS: dict[str, Any] = {
    "readOnlyHint": True,
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": False,
}

#: Documented return shape so clients need not restate it.
OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "value": {"type": "number", "description": "Computed valuation or metric."},
        "method": {"type": "string", "description": "Formula / method name that produced the result."},
        "inputs": {"type": "object", "description": "Echo of the normalised inputs used."},
        "assumptions": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Modelling assumptions applied.",
        },
        "chapter": {"type": "string", "description": "Source textbook chapter."},
        "formula_number": {"type": "string", "description": "Source textbook formula number (e.g. '3.1')."},
        "steps": {"type": "array", "items": {"type": "object"}, "description": "Intermediate steps for traceability."},
        "error": {"type": "string", "description": "Error message when the call fails."},
    },
    "required": ["value"],
}


# --------------------------------------------------------------------------
# Parameter vocabulary  (name -> json type + description + default)
# type strings: number | integer | array:number | array:object | object
# --------------------------------------------------------------------------

PARAMS: dict[str, dict[str, Any]] = {
    # probabilities
    "outcomes": {
        "type": "array:number",
        "description": "Possible outcome values x_i, in any currency unit (must match probabilities in length/order).",
    },
    "probabilities": {
        "type": "array:number",
        "description": "Probability of each outcome or stage, each in [0,1]; the list must sum to 1 where it is exhaustive.",
    },
    "weights": {
        "type": "array:number",
        "description": "Portfolio or factor weights, each in [0,1] and summing to 1 (same order as the paired value list).",
    },
    "returns": {
        "type": "array:number",
        "description": "Return of each asset or scenario as a decimal (0.20 = 20%), aligned with weights.",
    },
    "values": {
        "type": "array:number",
        "description": "Value of each asset or scenario in currency units, aligned with probabilities.",
    },
    "betas": {
        "type": "array:number",
        "description": "Asset betas aligned with weights; typically 0.5–3.0 (market = 1.0).",
    },
    "mean_events": {"type": "number", "description": "Poisson mean λ = expected number of events in the interval."},
    "k": {"type": "integer", "description": "Number of events k for the Poisson probability P(X=k); integer ≥ 0."},
    "lower": {"type": "number", "description": "Lower integration bound (standard-normal domain, e.g. -1.0)."},
    "upper": {"type": "number", "description": "Upper integration bound (standard-normal domain, e.g. 1.0)."},
    # time value
    "future_value": {"type": "number", "description": "Future cash amount to discount, in currency units."},
    "rate": {"type": "number", "description": "Per-period discount rate as a decimal (0.10 = 10%)."},
    "periods": {"type": "number", "description": "Number of compounding periods, must be ≥ 1 (may be fractional)."},
    "cash_flows": {
        "type": "array:number",
        "description": "Cash flows by period, first element at t=1; negatives allowed for outflows.",
    },
    "payment": {"type": "number", "description": "Recurring payment per period, in currency units."},
    "starting_value": {
        "type": "number",
        "description": "Value at t=0 (revenue or cash flow) to grow forward, in currency units.",
    },
    "ending_value": {
        "type": "number",
        "description": "Value at t=n to compare against the starting value, in currency units.",
    },
    "terminal_growth": {
        "type": "number",
        "description": "Perpetual growth rate g applied after the forecast window, as a decimal.",
        "default": 0.0,
    },
    "debt_value": {"type": "number", "description": "Market value of debt, in currency units."},
    "cost_of_equity": {"type": "number", "description": "After-tax cost of equity Re as a decimal."},
    "cost_of_debt": {"type": "number", "description": "Pre-tax cost of debt Rd as a decimal."},
    # capm
    "risk_free_rate": {"type": "number", "description": "Risk-free rate as a decimal (e.g. 0.04 for 4%)."},
    "beta": {"type": "number", "description": "Systematic risk beta (market = 1.0)."},
    "market_return": {"type": "number", "description": "Expected market return as a decimal (e.g. 0.10 for 10%)."},
    "market_risk_premium": {"type": "number", "description": "Market risk premium as a decimal (e.g. 0.06)."},
    "size_premium": {"type": "number", "description": "Small-cap / size premium as a decimal.", "default": 0.0},
    "liquidity_premium": {"type": "number", "description": "Illiquidity premium as a decimal.", "default": 0.0},
    # core
    "average_valuation": {
        "type": "number",
        "description": "Average pre-revenue valuation for the sector, currency units.",
    },
    "scores": {
        "type": "array:number",
        "description": "Factor multipliers aligned with weights (1.0 = average, >1 above average).",
    },
    "sound_idea": {
        "type": "number",
        "description": "Berkus award for soundness of the idea, 0 to 500,000 (USD).",
        "default": 0.0,
    },
    "prototype": {
        "type": "number",
        "description": "Berkus award for prototype / technology, 0 to 500,000.",
        "default": 0.0,
    },
    "quality_team": {
        "type": "number",
        "description": "Berkus award for management team, 0 to 500,000.",
        "default": 0.0,
    },
    "strategic_relationships": {
        "type": "number",
        "description": "Berkus award for strategic relationships, 0 to 500,000.",
        "default": 0.0,
    },
    "product_rollout": {
        "type": "number",
        "description": "Berkus award for product rollout / sales, 0 to 500,000.",
        "default": 0.0,
    },
    "base_valuation": {"type": "number", "description": "Pre-adjustment baseline valuation, currency units."},
    "risk_ratings": {
        "type": "array:number",
        "description": "12 risk factor ratings in [-2,2] (very low to very high); each unit shifts value ±250,000.",
    },
    "terminal_value": {"type": "number", "description": "Expected exit / terminal value, currency units."},
    "target_return": {"type": "number", "description": "VC target return multiple (e.g. 10 for a 10x target)."},
    "post_money": {"type": "number", "description": "Post-money valuation, currency units."},
    "investment": {"type": "number", "description": "Amount invested, currency units."},
    "projected_revenue": {"type": "number", "description": "Projected revenue at exit, currency units."},
    "multiple": {"type": "number", "description": "Exit or market multiple applied to the metric."},
    # advanced
    "underlying": {"type": "number", "description": "Underlying asset value S, currency units."},
    "strike": {"type": "number", "description": "Strike / exercise price K, currency units."},
    "volatility": {"type": "number", "description": "Annualised volatility σ as a decimal (0.80 = 80%)."},
    "time_to_maturity": {"type": "number", "description": "Time to expiry in years T, must be ≥ 0."},
    "steps": {
        "type": "integer",
        "description": "Binomial tree time steps (integer ≥ 1; higher = more accurate).",
        "default": 50,
    },
    "scenarios": {
        "type": "array:object",
        "description": "Scenario objects: {name: str, probability: 0-1, value: currency}; probabilities should sum to 1.",
    },
    # comparables
    "market_cap": {"type": "number", "description": "Market capitalisation, currency units."},
    "net_income": {"type": "number", "description": "Net income (earnings), currency units."},
    "revenue": {"type": "number", "description": "Revenue for the period, currency units."},
    "enterprise_value": {"type": "number", "description": "Enterprise value (market cap + net debt), currency units."},
    "ebitda": {"type": "number", "description": "EBITDA, currency units."},
    "intercept": {"type": "number", "description": "Regression intercept β0 (base multiple)."},
    "growth_rate": {"type": "number", "description": "Revenue growth rate as a decimal (0.40 = 40%)."},
    "growth_coefficient": {
        "type": "number",
        "description": "Regression slope on growth (multiple points per unit growth).",
    },
    "market_maturity": {"type": "number", "description": "Market maturity indicator.", "default": 0.0},
    "maturity_coefficient": {"type": "number", "description": "Regression slope on market maturity.", "default": 0.0},
    "stage": {"type": "number", "description": "Company stage indicator.", "default": 0.0},
    "stage_coefficient": {"type": "number", "description": "Regression slope on stage.", "default": 0.0},
    "geography": {"type": "number", "description": "Geography indicator.", "default": 0.0},
    "geography_coefficient": {"type": "number", "description": "Regression slope on geography.", "default": 0.0},
    # saas
    "arpu": {"type": "number", "description": "Average revenue per user per month, currency units."},
    "gross_margin": {"type": "number", "description": "Gross margin as a decimal (0.80 = 80%)."},
    "churn_rate": {"type": "number", "description": "Periodic churn rate as a decimal (0.02 = 2% per month)."},
    "sales_marketing_expense": {
        "type": "number",
        "description": "Sales & marketing spend for the period, currency units.",
    },
    "new_customers": {"type": "integer", "description": "Number of customers acquired in the period."},
    "arr_value": {"type": "number", "description": "Annual recurring revenue, currency units."},
    "subscription_values": {
        "type": "array:number",
        "description": "Monthly subscription revenue per customer (summed x12 for ARR).",
    },
    "starting_revenue": {"type": "number", "description": "Revenue from the cohort at period start, currency units."},
    "ending_revenue": {"type": "number", "description": "Revenue from the same cohort at period end, currency units."},
    "expansion_revenue": {
        "type": "number",
        "description": "Expansion revenue from the cohort in the period.",
        "default": 0.0,
    },
    "net_new_arr": {"type": "number", "description": "Net new ARR added in the period, currency units."},
    "sm_expense_prior": {
        "type": "number",
        "description": "Sales & marketing expense in the prior period, currency units.",
    },
    "profit_margin": {"type": "number", "description": "Profit margin as a decimal (0.15 = 15%)."},
    "cac": {"type": "number", "description": "Customer acquisition cost per customer, currency units."},
    "mrr_per_customer": {"type": "number", "description": "Monthly recurring revenue per customer, currency units."},
    "arr": {"type": "number", "description": "Annual recurring revenue, currency units."},
    "revenue_multiple": {"type": "number", "description": "SaaS revenue multiple (e.g. 8 for 8x ARR)."},
    # marketplace
    "take_rate": {"type": "number", "description": "Take rate as a decimal (0.15 = 15% of GMV)."},
    "gmv": {"type": "number", "description": "Gross merchandise value (total transaction volume), currency units."},
    "buyers_period_1": {"type": "integer", "description": "Distinct buyers in the base period."},
    "buyers_repeat": {"type": "integer", "description": "Distinct buyers from the base period who purchased again."},
    "active_buyers": {"type": "integer", "description": "Active buyers in the period."},
    "active_sellers": {"type": "integer", "description": "Active sellers in the period."},
    "total_users": {"type": "integer", "description": "Total users (buyers + sellers) in the period."},
    # fintech
    "transaction_volume": {"type": "number", "description": "Total payment transaction volume, currency units."},
    "loan_book": {"type": "number", "description": "Outstanding loan book / principal, currency units."},
    "roe": {"type": "number", "description": "Return on equity as a decimal (0.20 = 20%)."},
    "pe_multiple": {"type": "number", "description": "Price/earnings multiple applied to earnings."},
    "npl_reserves": {
        "type": "number",
        "description": "Non-performing loan reserves deducted, currency units.",
        "default": 0.0,
    },
    "discount_rate": {"type": "number", "description": "Discount rate as a decimal (0.12 = 12%)."},
    "terminal_multiple": {"type": "number", "description": "Terminal value multiple applied at the horizon."},
    "years": {"type": "integer", "description": "Forecast horizon in years; integer ≥ 1.", "default": 5},
    "customers": {"type": "integer", "description": "Number of customers."},
    # biotech
    "patient_population": {"type": "number", "description": "Target patient population treated per year."},
    "penetration": {"type": "number", "description": "Market penetration as a decimal (0.10 = 10%)."},
    "price": {"type": "number", "description": "Price per unit / treatment, currency units."},
    "compliance": {"type": "number", "description": "Compliance / adherence rate as a decimal.", "default": 1.0},
    "drugs": {
        "type": "array:object",
        "description": "Pipeline drugs: {name, peak_sales, probability, years_to_market, multiple(optional)}.",
    },
    # hardware
    "market_size": {"type": "number", "description": "Total addressable market, currency units."},
    "market_share": {"type": "number", "description": "Target market share as a decimal in [0,1]."},
    "margin": {"type": "number", "description": "Profit margin as a decimal."},
    "trl_discount": {"type": "number", "description": "TRL risk discount as a decimal (applied as 1 - discount)."},
    "fixed_costs": {"type": "number", "description": "Fixed costs for the period, currency units."},
    "asp": {"type": "number", "description": "Average selling price per unit, currency units."},
    "variable_cost": {"type": "number", "description": "Variable cost per unit, currency units."},
    # international
    "spot_rate": {"type": "number", "description": "Spot FX rate (domestic per foreign), e.g. 7.2 CNY/USD."},
    "inflation_foreign": {"type": "number", "description": "Foreign inflation rate as a decimal."},
    "inflation_domestic": {"type": "number", "description": "Domestic inflation rate as a decimal."},
    "sovereign_yield": {"type": "number", "description": "Foreign sovereign bond yield as a decimal."},
    "us_treasury_yield": {"type": "number", "description": "US Treasury yield as a decimal."},
    "mrp": {"type": "number", "description": "Market risk premium as a decimal."},
    "crp": {"type": "number", "description": "Country risk premium as a decimal."},
    # stakeholder
    "ownership_before": {
        "type": "number",
        "description": "Founder ownership before the round as a decimal (0.60 = 60%).",
    },
    "liquidation_pref": {"type": "number", "description": "Liquidation preference amount, currency units."},
    "time_to_exit": {"type": "number", "description": "Expected time to exit / liquidity in years."},
    "assets": {"type": "object", "description": 'Map of asset name to book value, e.g. {"cash": 500000}.'},
    "recovery_rates": {
        "type": "object",
        "description": "Map of asset name to recovery rate in [0,1], matching assets.",
    },
    "revenue_synergies": {"type": "number", "description": "Revenue synergy value, currency units."},
    "cost_synergies": {"type": "number", "description": "Cost synergy value, currency units."},
    "prob_revenue": {
        "type": "number",
        "description": "Probability of realising revenue synergies, 0-1.",
        "default": 0.4,
    },
    "prob_cost": {"type": "number", "description": "Probability of realising cost synergies, 0-1.", "default": 0.8},
    "strike_price": {"type": "number", "description": "Option strike price, currency units."},
    "fair_market_value": {"type": "number", "description": "Current fair market value per share, currency units."},
    "shares": {"type": "integer", "description": "Number of option shares."},
    "total_value": {"type": "number", "description": "Total grant value, currency units."},
    "vested_fraction": {"type": "number", "description": "Fraction vested in [0,1]."},
    "annual_vest_rate": {"type": "number", "description": "Annual vesting rate as a decimal.", "default": 0.25},
    "retention_prob": {"type": "number", "description": "Probability the holder stays, 0-1.", "default": 0.8},
    "years_remaining": {"type": "integer", "description": "Years of vesting remaining.", "default": 3},
    "salary_reduction": {"type": "number", "description": "Annual salary foregone for equity, currency units."},
    "equity_value": {"type": "number", "description": "Value of equity offered, currency units."},
    "tax_rate": {"type": "number", "description": "Effective tax rate as a decimal in [0,1].", "default": 0.3},
    "cash": {"type": "number", "description": "Cash and equivalents, currency units.", "default": 0.0},
    "accounts_receivable": {"type": "number", "description": "Accounts receivable, currency units.", "default": 0.0},
    "inventory": {"type": "number", "description": "Inventory, currency units.", "default": 0.0},
    "equipment": {"type": "number", "description": "Equipment, currency units.", "default": 0.0},
    "real_estate": {"type": "number", "description": "Real estate, currency units.", "default": 0.0},
    # emerging
    "series_a_price": {"type": "number", "description": "Price per share in the next priced (Series A) round."},
    "discount": {"type": "number", "description": "Conversion discount as a decimal (0.20 = 20% discount)."},
    "cap": {"type": "number", "description": "SAFE valuation cap, currency units."},
    "series_a_valuation": {"type": "number", "description": "Series A post-money valuation, currency units."},
    "price_per_tx": {"type": "number", "description": "Protocol revenue per transaction, currency units."},
    "velocity": {"type": "number", "description": "Token velocity (turnover of supply per period)."},
    "supply": {"type": "number", "description": "Circulating token supply."},
    "n": {"type": "number", "description": "Number of users or nodes in the network."},
    "esg_score": {"type": "number", "description": "ESG score in points (e.g. 0-100)."},
    "premium_per_point": {
        "type": "number",
        "description": "Valuation premium per ESG point as a decimal.",
        "default": 0.02,
    },
    "esg_risk_score": {"type": "number", "description": "ESG risk score in points (higher = riskier)."},
    "discount_per_point": {
        "type": "number",
        "description": "Valuation discount per ESG risk point as a decimal.",
        "default": 0.01,
    },
    "esg_risk_premium": {
        "type": "number",
        "description": "ESG risk premium added to the rate, as a decimal.",
        "default": 0.0,
    },
    "esg_opportunity_discount": {
        "type": "number",
        "description": "ESG opportunity discount subtracted from the rate.",
        "default": 0.0,
    },
    "data_volume": {"type": "number", "description": "Volume of proprietary data held."},
    "data_uniqueness": {"type": "number", "description": "Uniqueness / scarcity of the data in [0,1]."},
    "monetization_rate": {"type": "number", "description": "Fraction of data value monetisable as a decimal."},
    "competitive_advantage_years": {"type": "number", "description": "Years the data moat is expected to last."},
    "annual_savings": {"type": "number", "description": "Annual cost savings, currency units."},
    "cost_savings_pct": {"type": "number", "description": "Cost savings as a fraction of baseline.", "default": 0.2},
    "talent_access_premium": {"type": "number", "description": "Talent-access premium as a decimal.", "default": 0.1},
    "productivity_gain": {"type": "number", "description": "Productivity gain as a decimal.", "default": 0.05},
    # compound
    "scores_full": {
        "type": "array:number",
        "description": "Scorecard factor multipliers (7 values, aligned with weights).",
    },
}


# --------------------------------------------------------------------------
# Tools  (folded by valuation family; `method` enum selects the formula)
# args:    {function_param: mcp_param}  — required, always passed
# opt:     {function_param: mcp_param}  — passed only when provided
# adapter: optional transform of an mcp param before the call
# --------------------------------------------------------------------------

TOOLS: list[dict[str, Any]] = [
    {
        "name": "valuation_probability",
        "title": "Probability & Expected Value",
        "description": (
            "Compute expected value and probability-weighted outcomes for startup scenarios: "
            "discrete E[X], joint probability of sequential events, probability-weighted value, VC "
            "portfolio expected return, Poisson event probability, and continuous E[X] over a range. "
            "Method selects the formula. Use for probability-weighted central estimates; for named "
            "bull/base/bear tables or option pricing use valuation_advanced, and to discount cash "
            "flows use valuation_time_value. Parameters apply per method: expected_value_discrete and "
            "probability_weighted need outcomes + probabilities; portfolio_return needs weights + "
            "returns; poisson needs mean_events + k; expected_value_continuous needs lower + upper. "
            "outcomes and probabilities must be equal length, and the probabilities should sum to 1. "
            "Routing: use valuation_advanced method 'scenario_analysis' for named bull/base/bear "
            "scenario tables, and its black_scholes/binomial methods for option pricing; use this tool "
            "for arbitrary outcome lists and probability-weighted central estimates."
        ),
        "tags": ["probability", "expected-value", "risk"],
        "methods": [
            {
                "key": "expected_value_discrete",
                "label": "Expected value (discrete)",
                "summary": "E[X] = Σ xᵢ·P(X=xᵢ) over a discrete outcome list.",
                "module": "probability",
                "function": "expected_value_discrete",
                "args": {"outcomes": "outcomes", "probabilities": "probabilities"},
            },
            {
                "key": "joint_probability",
                "label": "Joint probability",
                "summary": "P(total) = Π pᵢ for independent sequential events.",
                "module": "probability",
                "function": "joint_probability",
                "args": {"probabilities": "probabilities"},
            },
            {
                "key": "probability_weighted",
                "label": "Probability-weighted value",
                "summary": "E[V] = Σ pᵢ·Vᵢ.",
                "module": "probability",
                "function": "probability_weighted_value",
                "args": {"outcomes": "outcomes", "probabilities": "probabilities"},
            },
            {
                "key": "portfolio_return",
                "label": "Portfolio expected return",
                "summary": "E[R] = Σ wᵢ·Rᵢ across a VC portfolio.",
                "module": "probability",
                "function": "portfolio_expected_return",
                "args": {"weights": "weights", "returns": "returns"},
            },
            {
                "key": "poisson",
                "label": "Poisson event probability",
                "summary": "P(X=k) = e^-λ λ^k / k! for rare events.",
                "module": "probability",
                "function": "poisson_probability",
                "args": {"lambda_": "mean_events", "k": "k"},
            },
            {
                "key": "expected_value_continuous",
                "label": "Expected value (continuous)",
                "summary": "E[X] = ∫ x·f(x) dx over [lower, upper] on the standard normal.",
                "module": "probability",
                "function": "expected_value_continuous_std_normal",
                "args": {"lower": "lower", "upper": "upper"},
            },
        ],
    },
    {
        "name": "valuation_time_value",
        "title": "Time Value of Money",
        "description": (
            "Discount, compound, and forecast value over time: single future value PV, net present "
            "value of a cash-flow stream, annuity present value, discounted cash flow with a Gordon "
            "terminal value, constant-rate compound growth of revenue or cash flow, and the implied "
            "compound annual growth rate (CAGR). Method selects "
            "the formula. Use to convert future cash to today's value, to value a full forecast with "
            "a terminal value (dcf), to project a revenue or cash-flow series forward, or to derive "
            "the growth rate implied by two values; get the "
            "discount rate from valuation_capm or valuation_international. Parameters apply per method: "
            "present_value needs future_value + rate + periods; npv needs cash_flows + rate; annuity "
            "needs payment + rate + periods; dcf needs cash_flows + rate (optional: terminal_growth); "
            "compound_growth needs "
            "starting_value + growth_rate + periods; cagr needs starting_value + ending_value + "
            "periods. growth_rate must be greater "
            "than -1, cagr requires starting_value > 0 and periods > 0, and dcf requires rate greater "
            "than terminal_growth. Not for option values (use "
            "valuation_advanced) or for expected values over outcomes (use valuation_probability)."
        ),
        "tags": ["dcf", "discounting", "time-value", "growth", "forecasting"],
        "methods": [
            {
                "key": "present_value",
                "label": "Present value",
                "summary": "PV = C / (1+r)^t.",
                "module": "tv",
                "function": "present_value",
                "args": {"future_value": "future_value", "rate": "rate", "periods": "periods"},
            },
            {
                "key": "npv",
                "label": "Net present value",
                "summary": "NPV = Σ Cₜ / (1+r)^t.",
                "module": "tv",
                "function": "net_present_value",
                "args": {"cash_flows": "cash_flows", "rate": "rate"},
            },
            {
                "key": "annuity",
                "label": "Annuity present value",
                "summary": "PV = P·[1-(1+r)^-n]/r.",
                "module": "tv",
                "function": "annuity_present_value",
                "args": {"payment": "payment", "rate": "rate", "periods": "periods"},
            },
            {
                "key": "compound_growth",
                "label": "Compound growth",
                "summary": "V_n = V_0 (1+g)^n.",
                "module": "growth",
                "function": "compound_growth",
                "args": {
                    "starting_value": "starting_value",
                    "growth_rate": "growth_rate",
                    "periods": "periods",
                },
            },
            {
                "key": "cagr",
                "label": "Compound annual growth rate",
                "summary": "CAGR = (V_n / V_0)^(1/n) - 1.",
                "module": "growth",
                "function": "compound_annual_growth_rate",
                "args": {
                    "starting_value": "starting_value",
                    "ending_value": "ending_value",
                    "periods": "periods",
                },
            },
            {
                "key": "dcf",
                "label": "Discounted cash flow",
                "summary": "DCF = Σ Cₜ/(1+r)^t + [C_n(1+g)/(r−g)]/(1+r)^n.",
                "module": "tv",
                "function": "dcf_valuation",
                "args": {"cash_flows": "cash_flows", "rate": "rate"},
                "opt": {"terminal_growth": "terminal_growth"},
            },
        ],
    },
    {
        "name": "valuation_capm",
        "title": "CAPM & Cost of Equity",
        "description": (
            "Estimate the cost of capital: standard CAPM, startup-adjusted CAPM with size and "
            "illiquidity premiums, portfolio beta from weighted asset betas, and WACC blending "
            "after-tax cost of equity and debt. Method selects the "
            "formula. Use to derive the discount rate that feeds valuation_time_value and DCF models; "
            "for cross-border rates add valuation_international. Parameters apply per method: capm "
            "needs risk_free_rate + beta + market_return; startup_capm adds size_premium and "
            "liquidity_premium; portfolio_beta needs weights + betas, which must be equal length; "
            "wacc needs equity_value + debt_value + cost_of_equity + cost_of_debt + tax_rate."
        ),
        "tags": ["capm", "cost-of-equity", "beta", "wacc", "cost-of-capital"],
        "methods": [
            {
                "key": "capm",
                "label": "CAPM",
                "summary": "E(R) = Rf + β·(E(Rm) - Rf).",
                "module": "capm",
                "function": "capm",
                "args": {"risk_free_rate": "risk_free_rate", "beta": "beta", "market_return": "market_return"},
            },
            {
                "key": "startup_capm",
                "label": "Startup-adjusted CAPM",
                "summary": "r = Rf + β·MRP + size premium + illiquidity premium.",
                "module": "capm",
                "function": "startup_adjusted_capm",
                "args": {
                    "risk_free_rate": "risk_free_rate",
                    "beta": "beta",
                    "market_risk_premium": "market_risk_premium",
                },
                "opt": {"size_premium": "size_premium", "illiquidity_premium": "liquidity_premium"},
            },
            {
                "key": "portfolio_beta",
                "label": "Portfolio beta",
                "summary": "βp = Σ wᵢ·βᵢ.",
                "module": "capm",
                "function": "portfolio_beta",
                "args": {"weights": "weights", "betas": "betas"},
            },
            {
                "key": "wacc",
                "label": "WACC",
                "summary": "WACC = (E/V)·Re + (D/V)·Rd·(1 − T).",
                "module": "capm",
                "function": "wacc",
                "args": {
                    "equity_value": "equity_value",
                    "debt_value": "debt_value",
                    "cost_of_equity": "cost_of_equity",
                    "cost_of_debt": "cost_of_debt",
                    "tax_rate": "tax_rate",
                },
            },
        ],
    },
    {
        "name": "valuation_core",
        "title": "Pre-Revenue Core Methods",
        "description": (
            "The textbook's pre-revenue methods: Scorecard, Berkus, Risk-Factor Summation, VC Method "
            "(post- and pre-money), and exit terminal value. Use these first for early-stage startups. "
            "Method selects the formula, and each method names its own parameters: scorecard needs "
            "average_valuation + weights + scores; berkus takes five factor awards; risk_factor needs "
            "base_valuation + risk_ratings; vc_post_money needs terminal_value + target_return; "
            "vc_pre_money needs post_money + investment; terminal_value needs projected_revenue + "
            "multiple; triangulated needs the scorecard inputs plus terminal_value/target_return/investment. "
            "Routing: for SAFEs, tokens, ESG, network effects, or data-moat methods use "
            "valuation_emerging; for options or bull/base/bear scenario tables use valuation_advanced; "
            "for public-comparable multiples use valuation_comparables."
        ),
        "tags": ["pre-revenue", "core", "scorecard", "berkus", "vc-method"],
        "methods": [
            {
                "key": "scorecard",
                "label": "Scorecard",
                "summary": "V = V_avg · Σ(wᵢ·sᵢ) across 7 factors.",
                "module": "core",
                "function": "scorecard_valuation",
                "args": {"average_valuation": "average_valuation", "weights": "weights", "scores": "scores"},
            },
            {
                "key": "berkus",
                "label": "Berkus",
                "summary": "V = Σ factor awards, each capped at $500K.",
                "module": "core",
                "function": "berkus_valuation",
                "opt": {
                    "sound_idea": "sound_idea",
                    "prototype": "prototype",
                    "quality_team": "quality_team",
                    "strategic_relationships": "strategic_relationships",
                    "product_rollout": "product_rollout",
                },
            },
            {
                "key": "risk_factor",
                "label": "Risk Factor Summation",
                "summary": "V = V_base + Σ(rᵢ·$250K) over 12 risks.",
                "module": "core",
                "function": "risk_factor_summation",
                "args": {"base_valuation": "base_valuation", "risk_ratings": "risk_ratings"},
            },
            {
                "key": "vc_post_money",
                "label": "VC Method (post-money)",
                "summary": "Post = Terminal / target ROI.",
                "module": "core",
                "function": "vc_method_post_money",
                "args": {"terminal_value": "terminal_value", "target_return": "target_return"},
            },
            {
                "key": "vc_pre_money",
                "label": "VC Method (pre-money)",
                "summary": "Pre = Post - Investment.",
                "module": "core",
                "function": "vc_method_pre_money",
                "args": {"post_money": "post_money", "investment": "investment"},
            },
            {
                "key": "terminal_value",
                "label": "Terminal value (exit multiple)",
                "summary": "Terminal = projected revenue × multiple.",
                "module": "core",
                "function": "terminal_value_multiple",
                "args": {"projected_revenue": "projected_revenue", "multiple": "multiple"},
            },
            {
                "key": "triangulated",
                "label": "Triangulated (Scorecard + VC Method mean)",
                "summary": "Runs Scorecard and the VC Method together and returns their mean.",
                "compound": True,
                "args": {
                    "average_valuation": "average_valuation",
                    "weights": "weights",
                    "scores": "scores",
                    "terminal_value": "terminal_value",
                    "target_return": "target_return",
                    "investment": "investment",
                },
            },
        ],
    },
    {
        "name": "valuation_advanced",
        "title": "Options & Scenario Analysis",
        "description": (
            "Advanced techniques: Black-Scholes call value, binomial-tree option value, and scenario "
            "analysis. Method selects the technique. For a quick expected value over arbitrary outcome "
            "lists, prefer valuation_probability with method 'probability_weighted'; scenario_analysis "
            "here is for explicit named bull/base/bear scenario tables. Parameters apply per method: "
            "black_scholes and binomial need underlying + strike + risk_free_rate + volatility + "
            "time_to_maturity (binomial adds steps); scenario_analysis needs scenarios. Not for plain "
            "discounted cash flow — for that use valuation_time_value."
        ),
        "tags": ["options", "black-scholes", "binomial", "scenarios"],
        "methods": [
            {
                "key": "black_scholes",
                "label": "Black-Scholes",
                "summary": "C = N(d₁)S - N(d₂)Ke^(-rT).",
                "module": "advanced",
                "function": "black_scholes",
                "args": {
                    "underlying": "underlying",
                    "strike": "strike",
                    "risk_free_rate": "risk_free_rate",
                    "volatility": "volatility",
                    "time_to_maturity": "time_to_maturity",
                },
            },
            {
                "key": "binomial",
                "label": "Binomial tree",
                "summary": "Cox-Ross-Rubinstein binomial option value.",
                "module": "advanced",
                "function": "binomial_valuation",
                "args": {
                    "underlying": "underlying",
                    "strike": "strike",
                    "risk_free_rate": "risk_free_rate",
                    "volatility": "volatility",
                    "time_to_maturity": "time_to_maturity",
                },
                "opt": {"steps": "steps"},
            },
            {
                "key": "scenario_analysis",
                "label": "Scenario analysis",
                "summary": "E[V] = Σ pᵢ·Vᵢ over named scenarios.",
                "module": "advanced",
                "function": "scenario_analysis",
                "args": {"scenarios": "scenarios"},
                "adapter": "scenarios",
            },
        ],
    },
    {
        "name": "valuation_comparables",
        "title": "Comparable Multiples",
        "description": (
            "Market multiples from comparables: P/E, P/S, EV/EBITDA, EV/Revenue, and a regression-adjusted "
            "multiple. Method selects the ratio. Use when public comparables exist; for pre-revenue or "
            "private startups use valuation_core. Parameters apply per method: pe_ratio needs market_cap "
            "+ net_income; ps_ratio needs market_cap + revenue; ev_ebitda needs enterprise_value + ebitda; "
            "ev_revenue needs enterprise_value + revenue; regression_multiple needs intercept + growth_rate "
            "+ growth_coefficient (plus optional maturity/stage/geography terms)."
        ),
        "tags": ["multiples", "comparables", "market"],
        "methods": [
            {
                "key": "pe_ratio",
                "label": "P/E ratio",
                "summary": "P/E = market cap / net income.",
                "module": "comparables",
                "function": "pe_ratio",
                "args": {"market_cap": "market_cap", "net_income": "net_income"},
            },
            {
                "key": "ps_ratio",
                "label": "P/S ratio",
                "summary": "P/S = market cap / revenue.",
                "module": "comparables",
                "function": "ps_ratio",
                "args": {"market_cap": "market_cap", "revenue": "revenue"},
            },
            {
                "key": "ev_ebitda",
                "label": "EV/EBITDA",
                "summary": "EV/EBITDA = enterprise value / EBITDA.",
                "module": "comparables",
                "function": "ev_ebitda",
                "args": {"enterprise_value": "enterprise_value", "ebitda": "ebitda"},
            },
            {
                "key": "ev_revenue",
                "label": "EV/Revenue",
                "summary": "EV/Revenue = enterprise value / revenue.",
                "module": "comparables",
                "function": "ev_revenue",
                "args": {"enterprise_value": "enterprise_value", "revenue": "revenue"},
            },
            {
                "key": "regression_multiple",
                "label": "Regression-adjusted multiple",
                "summary": "Multiple = β0 + β1·g + β2·M + β3·S + β4·G.",
                "module": "comparables",
                "function": "regression_adjusted_multiple",
                "args": {
                    "intercept": "intercept",
                    "growth_rate": "growth_rate",
                    "growth_coefficient": "growth_coefficient",
                },
                "opt": {
                    "market_maturity": "market_maturity",
                    "maturity_coefficient": "maturity_coefficient",
                    "stage": "stage",
                    "stage_coefficient": "stage_coefficient",
                    "geography": "geography",
                    "geography_coefficient": "geography_coefficient",
                },
            },
        ],
    },
    {
        "name": "valuation_saas",
        "title": "SaaS Metrics & Valuation",
        "description": (
            "SaaS unit economics and valuation: LTV, CAC, MRR, ARR, net revenue retention, magic number, "
            "Rule of 40, CAC payback, and ARR revenue-multiple valuation. Method selects the metric. Use "
            "for subscription software; for marketplace GMV metrics use valuation_marketplace and for "
            "payments/lending use valuation_fintech. Parameters apply per method: ltv needs arpu + "
            "gross_margin + churn_rate; cac needs sales_marketing_expense + new_customers; arr needs "
            "subscription_values; nrr needs starting_revenue + ending_revenue; revenue_multiple needs "
            "arr + revenue_multiple. Not for company-level pre-revenue value — for that use valuation_core."
        ),
        "tags": ["saas", "arr", "ltv", "cac", "retention"],
        "methods": [
            {
                "key": "ltv",
                "label": "LTV",
                "summary": "LTV = ARPU × gross margin / churn.",
                "module": "saas",
                "function": "ltv_saas",
                "args": {"arpu": "arpu", "gross_margin": "gross_margin", "churn_rate": "churn_rate"},
            },
            {
                "key": "cac",
                "label": "CAC",
                "summary": "CAC = S&M expense / new customers.",
                "module": "saas",
                "function": "cac",
                "args": {"sales_marketing_expense": "sales_marketing_expense", "new_customers": "new_customers"},
            },
            {
                "key": "mrr",
                "label": "MRR",
                "summary": "MRR = ARR / 12 (reverse of ARR).",
                "module": "saas",
                "function": "mrr",
                "args": {"arr_value": "arr_value"},
            },
            {
                "key": "arr",
                "label": "ARR",
                "summary": "ARR = Σ monthly subscriptions × 12.",
                "module": "saas",
                "function": "arr",
                "args": {"subscription_values": "subscription_values"},
            },
            {
                "key": "nrr",
                "label": "Net revenue retention",
                "summary": "NRR = (start + expansion) / start, net of churn.",
                "module": "saas",
                "function": "net_revenue_retention",
                "args": {"starting_revenue": "starting_revenue", "ending_revenue": "ending_revenue"},
                "opt": {"expansion_revenue": "expansion_revenue"},
            },
            {
                "key": "magic_number",
                "label": "Magic number",
                "summary": "Magic Number = net new ARR / prior-quarter S&M.",
                "module": "saas",
                "function": "magic_number",
                "args": {"net_new_arr": "net_new_arr", "sm_expense_prior": "sm_expense_prior"},
            },
            {
                "key": "rule_of_40",
                "label": "Rule of 40",
                "summary": "Score = growth rate + profit margin.",
                "module": "saas",
                "function": "rule_of_40",
                "args": {"growth_rate": "growth_rate", "profit_margin": "profit_margin"},
            },
            {
                "key": "cac_payback",
                "label": "CAC payback",
                "summary": "Months to recover CAC from gross profit.",
                "module": "saas",
                "function": "cac_payback_period",
                "args": {"cac": "cac", "mrr_per_customer": "mrr_per_customer", "gross_margin": "gross_margin"},
            },
            {
                "key": "revenue_multiple",
                "label": "ARR revenue multiple",
                "summary": "Valuation = ARR × multiple.",
                "module": "saas",
                "function": "saas_revenue_multiple_valuation",
                "args": {"arr": "arr", "multiple": "revenue_multiple"},
            },
        ],
    },
    {
        "name": "valuation_marketplace",
        "title": "Marketplace Metrics",
        "description": (
            "Marketplace health and valuation: take rate, GMV revenue-multiple valuation, buyer retention, "
            "and network density. Method selects the metric. Use for two-sided transaction marketplaces; "
            "for subscription software use valuation_saas. Parameters apply per method: take_rate needs "
            "revenue + gmv; gmv_multiple needs gmv + multiple; buyer_retention needs buyers_period_1 + "
            "buyers_repeat; network_density needs active_buyers + active_sellers + total_users."
        ),
        "tags": ["marketplace", "gmv", "network-effects"],
        "methods": [
            {
                "key": "take_rate",
                "label": "Take rate",
                "summary": "Take rate = revenue / GMV.",
                "module": "marketplace",
                "function": "take_rate",
                "args": {"revenue": "revenue", "gmv": "gmv"},
            },
            {
                "key": "gmv_multiple",
                "label": "GMV multiple valuation",
                "summary": "Valuation = GMV × multiple.",
                "module": "marketplace",
                "function": "gmv_multiple_valuation",
                "args": {"gmv": "gmv", "multiple": "multiple"},
            },
            {
                "key": "buyer_retention",
                "label": "Buyer retention",
                "summary": "Retention = repeat buyers / base-period buyers.",
                "module": "marketplace",
                "function": "buyer_retention",
                "args": {"buyers_period_1": "buyers_period_1", "buyers_repeat": "buyers_repeat"},
            },
            {
                "key": "network_density",
                "label": "Network density",
                "summary": "Density = active buyers × active sellers / total users.",
                "module": "marketplace",
                "function": "network_density",
                "args": {
                    "active_buyers": "active_buyers",
                    "active_sellers": "active_sellers",
                    "total_users": "total_users",
                },
            },
        ],
    },
    {
        "name": "valuation_fintech",
        "title": "Fintech Valuation",
        "description": (
            "Value and size fintech business models: payment revenue, lending valuation, payment-processor "
            "DCF, and neobank customer-based valuation. Method selects the model. Use for payments, "
            "lending, and neobanks; for SaaS-style unit economics use valuation_saas. Parameters apply "
            "per method: payment_revenue needs transaction_volume + take_rate; lending needs loan_book + "
            "roe + pe_multiple; payment_processor adds growth_rate + discount_rate + terminal_multiple; "
            "neobank needs customers + arpu + gross_margin + churn_rate + pe_multiple."
        ),
        "tags": ["fintech", "payments", "lending", "neobank"],
        "methods": [
            {
                "key": "payment_revenue",
                "label": "Payment revenue",
                "summary": "Revenue = volume × take rate.",
                "module": "fintech",
                "function": "payment_revenue",
                "args": {"transaction_volume": "transaction_volume", "take_rate": "take_rate"},
            },
            {
                "key": "lending",
                "label": "Lending valuation",
                "summary": "V = loan book × ROE × P/E - NPL reserves.",
                "module": "fintech",
                "function": "lending_fintech_valuation",
                "args": {"loan_book": "loan_book", "roe": "roe", "pe_multiple": "pe_multiple"},
                "opt": {"npl_reserves": "npl_reserves"},
            },
            {
                "key": "payment_processor",
                "label": "Payment processor (DCF)",
                "summary": "DCF of payment revenue with a terminal multiple.",
                "module": "fintech",
                "function": "payment_processor_valuation",
                "args": {
                    "transaction_volume": "transaction_volume",
                    "take_rate": "take_rate",
                    "growth_rate": "growth_rate",
                    "discount_rate": "discount_rate",
                    "terminal_multiple": "terminal_multiple",
                },
                "opt": {"years": "years"},
            },
            {
                "key": "neobank",
                "label": "Neobank valuation",
                "summary": "Customer LTV × P/E applied to the customer base.",
                "module": "fintech",
                "function": "neobank_valuation",
                "args": {
                    "customers": "customers",
                    "arpu": "arpu",
                    "gross_margin": "gross_margin",
                    "churn_rate": "churn_rate",
                    "pe_multiple": "pe_multiple",
                },
            },
        ],
    },
    {
        "name": "valuation_biotech",
        "title": "Biotech Pipeline Valuation",
        "description": (
            "Risk-adjusted biotech valuation: peak sales, decision-tree expected value, and full pipeline "
            "rNPV across drugs. Method selects the model. Use for pharma/drug pipelines; for hardware or "
            "deep tech use valuation_hardware. Parameters apply per method: peak_sales needs "
            "patient_population + penetration + price; decision_tree needs probabilities + terminal_value; "
            "pipeline needs drugs + discount_rate. Not for hardware or deep tech — for that use "
            "valuation_hardware."
        ),
        "tags": ["biotech", "pharma", "pipeline", "rnpv"],
        "methods": [
            {
                "key": "peak_sales",
                "label": "Peak sales",
                "summary": "Peak = population × penetration × price × compliance.",
                "module": "biotech",
                "function": "peak_sales",
                "args": {
                    "patient_population": "patient_population",
                    "penetration_rate": "penetration",
                    "price": "price",
                },
                "opt": {"compliance_rate": "compliance"},
            },
            {
                "key": "decision_tree",
                "label": "Decision-tree EV",
                "summary": "EV = Π pᵢ × terminal value.",
                "module": "biotech",
                "function": "decision_tree_ev",
                "args": {"probabilities": "probabilities", "terminal_value": "terminal_value"},
            },
            {
                "key": "pipeline",
                "label": "Pipeline rNPV",
                "summary": "V = Σ(peak sales × multiple × P_success) / (1+r)^n.",
                "module": "biotech",
                "function": "pipeline_valuation",
                "args": {"drugs": "drugs", "discount_rate": "discount_rate"},
            },
        ],
    },
    {
        "name": "valuation_hardware",
        "title": "Hardware & Unit Economics",
        "description": (
            "Hardware and deep-tech valuation: TRL-risk-adjusted valuation, gross margin, and break-even "
            "volume. Method selects the metric. Use for hardware and deep tech with technology-readiness "
            "risk; for drug pipelines use valuation_biotech. Parameters apply per method: trl needs "
            "market_size + market_share + margin + multiple + trl_discount; gross_margin needs asp + "
            "variable_cost; break_even_volume needs fixed_costs + asp + variable_cost. Not for drug "
            "pipelines — for those use valuation_biotech."
        ),
        "tags": ["hardware", "trl", "unit-economics"],
        "methods": [
            {
                "key": "trl",
                "label": "TRL-adjusted valuation",
                "summary": "V = market × share × margin × multiple × (1 - TRL discount).",
                "module": "hardware",
                "function": "trl_adjusted_valuation",
                "args": {
                    "market_size": "market_size",
                    "market_share": "market_share",
                    "margin": "margin",
                    "multiple": "multiple",
                    "trl_discount": "trl_discount",
                },
            },
            {
                "key": "gross_margin",
                "label": "Gross margin",
                "summary": "GM = (ASP - COGS) / ASP.",
                "module": "hardware",
                "function": "gross_margin_hardware",
                "args": {"asp": "asp", "cogs": "variable_cost"},
            },
            {
                "key": "break_even_volume",
                "label": "Break-even volume",
                "summary": "Units = fixed costs / (ASP - variable cost).",
                "module": "hardware",
                "function": "break_even_volume",
                "args": {"fixed_costs": "fixed_costs", "asp": "asp", "variable_cost": "variable_cost"},
            },
        ],
    },
    {
        "name": "valuation_international",
        "title": "International Valuation",
        "description": (
            "Cross-border adjustments: purchasing-power parity, country risk premium, and international "
            "CAPM. Method selects the adjustment. Use for cross-border cash flows and country risk; pair "
            "with valuation_capm and valuation_time_value. Parameters apply per method: ppp needs "
            "spot_rate + inflation_foreign + inflation_domestic; country_risk_premium needs sovereign_yield "
            "+ us_treasury_yield; intl_capm needs risk_free_rate + beta + mrp + crp. Not for the domestic "
            "cost of equity — for that use valuation_capm."
        ),
        "tags": ["international", "fx", "country-risk"],
        "methods": [
            {
                "key": "ppp",
                "label": "Purchasing power parity",
                "summary": "Eₜ = E₀·(1+π_foreign)/(1+π_domestic).",
                "module": "international",
                "function": "purchasing_power_parity",
                "args": {
                    "spot_rate": "spot_rate",
                    "inflation_foreign": "inflation_foreign",
                    "inflation_domestic": "inflation_domestic",
                },
            },
            {
                "key": "country_risk_premium",
                "label": "Country risk premium",
                "summary": "CRP = sovereign yield - US Treasury yield.",
                "module": "international",
                "function": "country_risk_premium",
                "args": {"sovereign_yield": "sovereign_yield", "us_treasury_yield": "us_treasury_yield"},
            },
            {
                "key": "intl_capm",
                "label": "International CAPM",
                "summary": "r = Rf + β·MRP + CRP.",
                "module": "international",
                "function": "adjusted_capm_international",
                "args": {
                    "risk_free_rate": "risk_free_rate",
                    "beta": "beta",
                    "market_risk_premium": "mrp",
                    "crp": "crp",
                },
            },
        ],
    },
    {
        "name": "valuation_stakeholder",
        "title": "Stakeholder & Equity Allocation",
        "description": (
            "Allocate value across stakeholders and equity classes: single-round dilution, OPM common stock, "
            "PWERM, liquidation value, M&A synergy, employee-option values, vesting adjustment, cash-vs-equity "
            "break-even, and asset-based loan capacity. Method selects the model. Use only after the "
            "company-level value is known (from valuation_core, valuation_saas, or valuation_comparables) to "
            "split that value across the cap table; for the company value itself do not use this tool. "
            "Parameters apply per method: dilution needs ownership_before + investment + post_money; opm "
            "needs enterprise_value + liquidation_pref + time_to_exit + volatility; pwerm and employee_option "
            "need scenarios; liquidation needs assets + recovery_rates; risk_adjusted_synergy needs "
            "revenue_synergies + cost_synergies; vesting_adjusted needs total_value + vested_fraction; "
            "max_asset_loan takes collateral values."
        ),
        "tags": ["dilution", "opm", "pwerm", "options", "cap-table"],
        "methods": [
            {
                "key": "dilution",
                "label": "Single-round dilution",
                "summary": "Ownership = before × (1 - investment / post-money).",
                "module": "stakeholders",
                "function": "single_round_dilution",
                "args": {
                    "ownership_before": "ownership_before",
                    "investment": "investment",
                    "post_money": "post_money",
                },
            },
            {
                "key": "opm",
                "label": "OPM common stock",
                "summary": "Option-pricing allocation of equity value to common shares.",
                "module": "stakeholders",
                "function": "opm_common_stock",
                "args": {
                    "enterprise_value": "enterprise_value",
                    "liquidation_preference": "liquidation_pref",
                    "time_to_exit": "time_to_exit",
                    "volatility": "volatility",
                },
            },
            {
                "key": "pwerm",
                "label": "PWERM",
                "summary": "Probability-weighted expected return method across exit scenarios.",
                "module": "stakeholders",
                "function": "pwerm",
                "args": {"scenarios": "scenarios"},
                "adapter": "scenarios",
            },
            {
                "key": "liquidation",
                "label": "Liquidation value",
                "summary": "V = Σ(asset × recovery rate).",
                "module": "stakeholders",
                "function": "liquidation_value",
                "args": {"assets": "assets", "recovery_rates": "recovery_rates"},
            },
            {
                "key": "risk_adjusted_synergy",
                "label": "Risk-adjusted synergy",
                "summary": "Probability-weighted, discounted M&A revenue + cost synergies.",
                "module": "stakeholders",
                "function": "risk_adjusted_synergy",
                "args": {"revenue_synergies": "revenue_synergies", "cost_synergies": "cost_synergies"},
                "opt": {
                    "prob_revenue": "prob_revenue",
                    "prob_cost": "prob_cost",
                    "discount_rate": "discount_rate",
                    "years": "years",
                },
            },
            {
                "key": "intrinsic_option",
                "label": "Intrinsic option value",
                "summary": "Intrinsic value = max(0, FMV - strike) × shares.",
                "module": "stakeholders",
                "function": "intrinsic_option_value",
                "args": {"strike_price": "strike_price", "fair_market_value": "fair_market_value", "shares": "shares"},
            },
            {
                "key": "employee_option",
                "label": "Employee option value",
                "summary": "Probability-weighted employee option value across scenarios.",
                "module": "stakeholders",
                "function": "probability_weighted_employee_value",
                "args": {"scenarios": "scenarios"},
                "adapter": "scenarios",
            },
            {
                "key": "vesting_adjusted",
                "label": "Vesting-adjusted value",
                "summary": "Option value adjusted for vesting schedule and retention probability.",
                "module": "stakeholders",
                "function": "vesting_adjusted_value",
                "args": {"total_value": "total_value", "vested_fraction": "vested_fraction"},
                "opt": {
                    "annual_vest_rate": "annual_vest_rate",
                    "retention_prob": "retention_prob",
                    "years_remaining": "years_remaining",
                },
            },
            {
                "key": "cash_equity_breakeven",
                "label": "Cash vs equity break-even",
                "summary": "Break-even comparing salary reduction against discounted equity.",
                "module": "stakeholders",
                "function": "cash_equity_breakeven",
                "args": {"salary_reduction": "salary_reduction", "equity_value": "equity_value"},
                "opt": {"tax_rate": "tax_rate", "discount_rate": "discount_rate", "years": "years"},
            },
            {
                "key": "max_asset_loan",
                "label": "Maximum asset-based loan",
                "summary": "Borrowing capacity from asset collateral values.",
                "module": "stakeholders",
                "function": "max_asset_based_loan",
                "opt": {
                    "cash": "cash",
                    "accounts_receivable": "accounts_receivable",
                    "inventory": "inventory",
                    "equipment": "equipment",
                    "real_estate": "real_estate",
                },
            },
        ],
    },
    {
        "name": "valuation_emerging",
        "title": "Emerging & Alternative Methods",
        "description": (
            "Modern and alternative valuation: SAFE conversion (discount, cap, expected value), token "
            "valuation (equation of exchange, NVT), ESG adjustments (rate, premium, discount), Metcalfe "
            "network value, data-moat value, and remote-first premium/NPV. Method selects the model. Use "
            "for SAFEs, tokens, ESG, network effects, data moats, and remote-first adjustments; for "
            "classic pre-revenue methods use valuation_core. Parameters apply per method: safe_discount "
            "needs series_a_price + discount; safe_cap needs cap + series_a_price; safe_expected needs "
            "investment + cap + discount + series_a_valuation + series_a_price; token_value needs "
            "transaction_volume + price_per_tx + velocity + supply; metcalfe needs n; esg_* need "
            "base_valuation + a score; data_moat needs data_volume + data_uniqueness + monetization_rate + "
            "competitive_advantage_years. Routing: for classic pre-revenue methods (Scorecard, Berkus, "
            "Risk-Factor Summation, VC Method) use valuation_core; for options or scenario tables use "
            "valuation_advanced; for public-comparable multiples use valuation_comparables."
        ),
        "tags": ["safe", "crypto", "esg", "network-effects", "data"],
        "methods": [
            {
                "key": "safe_discount",
                "label": "SAFE conversion price (discount)",
                "summary": "Price = Series A price × (1 - discount).",
                "module": "emerging",
                "function": "safe_conversion_discount",
                "args": {"series_a_price": "series_a_price", "discount": "discount"},
            },
            {
                "key": "safe_cap",
                "label": "SAFE conversion price (cap)",
                "summary": "Price = cap / pre-money shares (cap-based).",
                "module": "emerging",
                "function": "safe_conversion_cap",
                "args": {"cap": "cap", "series_a_price": "series_a_price"},
            },
            {
                "key": "safe_expected",
                "label": "SAFE expected value",
                "summary": "Expected SAFE value across cap and discount outcomes.",
                "module": "emerging",
                "function": "safe_expected_value",
                "args": {
                    "investment": "investment",
                    "cap": "cap",
                    "discount": "discount",
                    "series_a_valuation": "series_a_valuation",
                    "series_a_price": "series_a_price",
                },
            },
            {
                "key": "token_value",
                "label": "Token value (equation of exchange)",
                "summary": "Value = (volume × price) / (velocity × supply).",
                "module": "emerging",
                "function": "equation_of_exchange",
                "args": {
                    "transaction_volume": "transaction_volume",
                    "price_per_transaction": "price_per_tx",
                    "token_velocity": "velocity",
                    "token_supply": "supply",
                },
            },
            {
                "key": "nvt_ratio",
                "label": "NVT ratio",
                "summary": "NVT = market cap / daily transaction volume.",
                "module": "emerging",
                "function": "nvt_ratio",
                "args": {"market_cap": "market_cap", "daily_transaction_volume": "transaction_volume"},
            },
            {
                "key": "esg_rate",
                "label": "ESG-adjusted discount rate",
                "summary": "r = base + ESG risk premium - ESG opportunity discount.",
                "module": "emerging",
                "function": "esg_adjusted_discount_rate",
                "args": {"base_rate": "rate"},
                "opt": {"esg_risk_premium": "esg_risk_premium", "esg_opportunity_discount": "esg_opportunity_discount"},
            },
            {
                "key": "esg_premium",
                "label": "ESG premium",
                "summary": "Valuation uplift = base × (1 + score × premium per point).",
                "module": "emerging",
                "function": "esg_premium_valuation",
                "args": {"base_valuation": "base_valuation", "esg_score": "esg_score"},
                "opt": {"premium_per_point": "premium_per_point"},
            },
            {
                "key": "esg_discount",
                "label": "ESG risk discount",
                "summary": "Valuation reduction = base × (1 - risk score × discount per point).",
                "module": "emerging",
                "function": "esg_discount_valuation",
                "args": {"base_valuation": "base_valuation", "esg_risk_score": "esg_risk_score"},
                "opt": {"discount_per_point": "discount_per_point"},
            },
            {
                "key": "metcalfe",
                "label": "Metcalfe's law",
                "summary": "V = k · n².",
                "module": "emerging",
                "function": "metcalfes_law",
                "args": {"n": "n"},
                "opt": {"k": "k"},
            },
            {
                "key": "data_moat",
                "label": "Data moat value",
                "summary": "Discounted value of monetised proprietary data.",
                "module": "emerging",
                "function": "data_moat_value",
                "args": {
                    "data_volume": "data_volume",
                    "data_uniqueness": "data_uniqueness",
                    "monetization_rate": "monetization_rate",
                    "competitive_advantage_years": "competitive_advantage_years",
                },
                "opt": {"discount_rate": "discount_rate"},
            },
            {
                "key": "remote_npv",
                "label": "Remote cost-savings NPV",
                "summary": "Perpetuity NPV = annual savings / discount rate.",
                "module": "emerging",
                "function": "remote_cost_savings_npv",
                "args": {"annual_savings": "annual_savings", "discount_rate": "discount_rate"},
            },
            {
                "key": "remote_premium",
                "label": "Remote-first premium",
                "summary": "Valuation premium from cost savings, talent access, and productivity.",
                "module": "emerging",
                "function": "remote_first_premium",
                "args": {"base_valuation": "base_valuation"},
                "opt": {
                    "cost_savings_pct": "cost_savings_pct",
                    "talent_access_premium": "talent_access_premium",
                    "productivity_gain": "productivity_gain",
                },
            },
        ],
    },
]


# --------------------------------------------------------------------------
# Schema helpers
# --------------------------------------------------------------------------

_TYPE_MAP: dict[str, dict[str, Any]] = {
    "number": {"type": "number"},
    "integer": {"type": "integer"},
    "string": {"type": "string"},
    "object": {"type": "object"},
    "array:number": {"type": "array", "items": {"type": "number"}},
    "array:object": {"type": "array", "items": {"type": "object"}},
}


#: Behavioural clause appended to every tool description. The annotation hints
#: cover the safety profile; this covers *error* behaviour, which annotations and
#: the output schema do not — the TDQS Behavioral Transparency dimension asks for
#: consequences beyond the structured hints.
_RETURNS_NOTE = (
    " Returns value, method, inputs, assumptions, chapter, formula_number and calculation steps; pure "
    "arithmetic — no I/O and no external calls — rounded to 2 decimals, with no auth or rate limits. An "
    "unknown method, or a missing method-required parameter, returns an error instead of a value."
)


#: Completeness clause: callers routinely need to know that only `method` is
#: mandatory and the rest of the (large) parameter set is conditional.
_PARAMS_NOTE = (
    " Only method is required; all other parameters are method-dependent, so supply those the selected "
    "method names and omit the rest (defaults apply where defined). Rate and decimal inputs are fractions "
    "(0.10 = 10%); probability and weight lists are in [0,1] and sum to 1."
)


def describe(tool: dict[str, Any]) -> str:
    """Full description as advertised to clients (base text + shared clauses)."""
    return f"{tool['description']}{_PARAMS_NOTE}{_RETURNS_NOTE}"


def _param_schema(key: str) -> dict[str, Any]:
    spec = PARAMS[key]
    schema = dict(_TYPE_MAP[spec["type"]])
    schema["description"] = spec["description"]
    if "default" in spec:
        schema["default"] = spec["default"]
    return schema


def _tool_param_names(tool: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for method in tool.get("methods", []):
        for mapping in ("args", "opt"):
            for mcp_name in method.get(mapping, {}).values():
                if mcp_name not in names:
                    names.append(mcp_name)
    return names


def input_schema(tool: dict[str, Any]) -> dict[str, Any]:
    """Build the JSON Schema advertised for a tool."""
    enum = [m["key"] for m in tool["methods"]]
    props: dict[str, Any] = {
        "method": {
            "type": "string",
            "enum": enum,
            "description": "Formula to apply. Options: "
            + "; ".join(f"{m['key']} = {m['summary']}" for m in tool["methods"]),
        }
    }
    for name in _tool_param_names(tool):
        props[name] = _param_schema(name)
    return {"type": "object", "properties": props, "required": ["method"]}


def tool_definition(tool: dict[str, Any]) -> dict[str, Any]:
    """Full tools/list entry (name, title, description, schemas, annotations)."""
    return {
        "name": tool["name"],
        "title": tool["title"],
        "description": describe(tool),
        "inputSchema": input_schema(tool),
        "outputSchema": OUTPUT_SCHEMA,
        "annotations": COMMON_ANNOTATIONS,
        "tags": tool["tags"],
    }


def list_tools() -> list[dict[str, Any]]:
    """Return every tool definition, in stable order."""
    return [tool_definition(t) for t in TOOLS]


# --------------------------------------------------------------------------
# Dispatch
# --------------------------------------------------------------------------


def _resolve(module_name: str, function_name: str) -> tuple[Any, dict[str, Any]]:
    import importlib

    if function_name == "expected_value_continuous_std_normal":
        import scipy.stats

        mod = importlib.import_module("startup_valuation.probability")

        def curve(x: float) -> float:
            return float(scipy.stats.norm.pdf(x, loc=0, scale=1))

        return mod.expected_value_continuous, {"f": curve}
    mod = importlib.import_module(f"startup_valuation.{module_name}")
    return getattr(mod, function_name), {}


def _unwrap(result: Any) -> dict[str, Any]:
    if isinstance(result, dict):
        return result
    return {
        "value": result.value,
        "method": result.method,
        "inputs": getattr(result, "inputs", {}),
        "assumptions": getattr(result, "assumptions", []),
        "chapter": getattr(result, "chapter", ""),
        "formula_number": getattr(result, "formula_number", ""),
        "steps": getattr(result, "steps", []),
    }


def _find_method(tool: dict[str, Any], method_key: str) -> dict[str, Any]:
    for method in tool.get("methods", []):
        if method["key"] == method_key:
            found: dict[str, Any] = method
            return found
    raise ValueError(f"Unknown method '{method_key}' for tool '{tool['name']}'")


def _triangulated(arguments: dict[str, Any]) -> dict[str, Any]:
    """Compound method: mean of the Scorecard and VC pre-money valuations."""
    from startup_valuation import core

    for required in ("average_valuation", "weights", "scores", "terminal_value", "target_return", "investment"):
        if arguments.get(required) is None:
            raise ValueError(f"method 'triangulated' requires parameter '{required}'")
    scorecard = core.scorecard_valuation(arguments["average_valuation"], arguments["weights"], arguments["scores"])
    post_money = core.vc_method_post_money(arguments["terminal_value"], arguments["target_return"])
    pre_money = core.vc_method_pre_money(post_money.value, arguments["investment"])
    return {
        "value": (scorecard.value + pre_money.value) / 2,
        "method": "Triangulated (Scorecard + VC Method mean)",
        "scorecard": {"value": scorecard.value, "method": scorecard.method},
        "vc_post_money": {"value": post_money.value, "method": post_money.method},
        "vc_pre_money": {"value": pre_money.value, "method": pre_money.method},
    }


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute a tool by name. Raises ValueError for bad input."""
    tool = next((t for t in TOOLS if t["name"] == name), None)
    if tool is None:
        raise ValueError(f"Tool not found: {name}")

    method = _find_method(tool, arguments.get("method", ""))
    if method.get("compound"):
        return _triangulated(arguments)

    kwargs: dict[str, Any] = {}
    for fn_param, mcp_name in method.get("args", {}).items():
        if mcp_name not in arguments or arguments[mcp_name] is None:
            raise ValueError(f"method '{method['key']}' requires parameter '{mcp_name}'")
        kwargs[fn_param] = arguments[mcp_name]
    for fn_param, mcp_name in method.get("opt", {}).items():
        value = arguments.get(mcp_name)
        if value is not None:
            kwargs[fn_param] = value

    if method.get("adapter") == "scenarios":
        field = next(iter(method["args"]))
        kwargs[field] = [
            s if isinstance(s, Scenario) else Scenario(name=s["name"], probability=s["probability"], value=s["value"])
            for s in kwargs[field]
        ]

    fn, injected = _resolve(method["module"], method["function"])
    result = fn(**injected, **kwargs)
    return _unwrap(result)


def tool_count() -> int:
    return len(TOOLS)
