"""MCP Server for Startup Valuation Engine."""

from fastmcp import FastMCP

from startup_valuation import probability, tv, capm, core, advanced, comparables
from startup_valuation import saas, biotech, fintech, marketplace, hardware, international
from startup_valuation import stakeholders, emerging

mcp = FastMCP("startup-valuation", version="0.1.0")


# ── Probability ──────────────────────────────────────────────────────
@mcp.tool()
def valuation_expected_value(outcomes: list[float], probabilities: list[float]) -> dict:
    """Calculate expected value for a discrete random variable. E[X] = Σ xᵢ × P(X=xᵢ)"""
    r = probability.expected_value_discrete(outcomes, probabilities)
    return {"value": r.value, "method": r.method, "inputs": r.inputs}


@mcp.tool()
def valuation_joint_probability(probabilities: list[float]) -> dict:
    """Calculate joint probability of sequential events. P(total) = Π Pᵢ"""
    r = probability.joint_probability(probabilities)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_probability_weighted(probabilities: list[float], values: list[float]) -> dict:
    """Calculate probability-weighted expected value. E[V] = Σ pᵢ × Vᵢ"""
    r = probability.probability_weighted_value(probabilities, values)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_portfolio_return(probabilities: list[float], returns: list[float]) -> dict:
    """Calculate VC portfolio expected return. E[R] = Σ pᵢ × Rᵢ"""
    r = probability.portfolio_expected_return(probabilities, returns)
    return {"value": r.value, "method": r.method}


# ── Time Value ───────────────────────────────────────────────────────
@mcp.tool()
def valuation_present_value(future_value: float, rate: float, periods: float) -> dict:
    """Calculate present value. PV = C / (1+r)^t"""
    r = tv.present_value(future_value, rate, periods)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_npv(cash_flows: list[float], rate: float) -> dict:
    """Calculate net present value. NPV = Σ Cₜ / (1+r)^t"""
    r = tv.net_present_value(cash_flows, rate)
    return {"value": r.value, "method": r.method}


# ── CAPM ─────────────────────────────────────────────────────────────
@mcp.tool()
def valuation_capm(risk_free_rate: float, beta: float, market_return: float) -> dict:
    """Calculate expected return using CAPM. E(R) = Rf + β(E(Rm) - Rf)"""
    r = capm.capm(risk_free_rate, beta, market_return)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_portfolio_beta(weights: list[float], betas: list[float]) -> dict:
    """Calculate portfolio beta. βp = Σ wᵢβᵢ"""
    r = capm.portfolio_beta(weights, betas)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_startup_capm(
    risk_free_rate: float, beta: float, market_risk_premium: float,
    size_premium: float = 0, startup_premium: float = 0,
) -> dict:
    """Calculate startup-adjusted CAPM with additional premiums."""
    r = capm.startup_adjusted_capm(risk_free_rate, beta, market_risk_premium, size_premium, startup_premium)
    return {"value": r.value, "method": r.method}


# ── Core Valuation ───────────────────────────────────────────────────
@mcp.tool()
def valuation_scorecard(average_valuation: float, weights: list[float], scores: list[float]) -> dict:
    """Scorecard valuation. V = V_avg × Σ(wᵢ × sᵢ)"""
    r = core.scorecard_valuation(average_valuation, weights, scores)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_berkus(
    sound_idea: float = 0, prototype: float = 0, quality_team: float = 0,
    strategic_relationships: float = 0, product_rollout: float = 0,
) -> dict:
    """Berkus valuation. V = Σ vᵢ (max $500K per factor)."""
    r = core.berkus_valuation(sound_idea, prototype, quality_team, strategic_relationships, product_rollout)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_risk_factor_summation(base_valuation: float, risk_ratings: list[float]) -> dict:
    """Risk Factor Summation. V = V_base + Σ(rᵢ × $250K)"""
    r = core.risk_factor_summation(base_valuation, risk_ratings)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_vc_post_money(terminal_value: float, target_return: float) -> dict:
    """VC Method post-money. Post = Terminal / ROI"""
    r = core.vc_method_post_money(terminal_value, target_return)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_vc_pre_money(post_money: float, investment: float) -> dict:
    """VC Method pre-money. Pre = Post - Investment"""
    r = core.vc_method_pre_money(post_money, investment)
    return {"value": r.value, "method": r.method}


# ── Advanced ─────────────────────────────────────────────────────────
@mcp.tool()
def valuation_black_scholes(
    underlying: float, strike: float, risk_free_rate: float,
    volatility: float, time_to_maturity: float,
) -> dict:
    """Black-Scholes call option value. C = N(d₁)S - N(d₂)Ke^(-rT)"""
    r = advanced.black_scholes(underlying, strike, risk_free_rate, volatility, time_to_maturity)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_scenario_analysis(scenarios: list[dict]) -> dict:
    """Scenario analysis expected value. E[V] = Σ pᵢ × Vᵢ. scenarios: [{name, probability, value}]"""
    from startup_valuation.types import Scenario
    s = [Scenario(name=s["name"], probability=s["probability"], value=s["value"]) for s in scenarios]
    r = advanced.scenario_analysis(s)
    return {"value": r.value, "method": r.method}


# ── Comparables ──────────────────────────────────────────────────────
@mcp.tool()
def valuation_regression_multiple(
    intercept: float, growth_rate: float, growth_coefficient: float,
    market_maturity: float = 0, maturity_coefficient: float = 0,
    stage: float = 0, stage_coefficient: float = 0,
    geography: float = 0, geography_coefficient: float = 0,
) -> dict:
    """Regression-adjusted multiple. Multiple = β₀ + β₁g + β₂M + β₃S + β₄G"""
    r = comparables.regression_adjusted_multiple(
        intercept, growth_rate, growth_coefficient,
        market_maturity, maturity_coefficient, stage, stage_coefficient, geography, geography_coefficient,
    )
    return {"value": r.value, "method": r.method}


# ── SaaS ─────────────────────────────────────────────────────────────
@mcp.tool()
def valuation_saas_ltv(arpu: float, gross_margin: float, churn_rate: float) -> dict:
    """SaaS LTV. LTV = (ARPU × Gross Margin) / Churn Rate"""
    r = saas.ltv_saas(arpu, gross_margin, churn_rate)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_rule_of_40(growth_rate: float, profit_margin: float) -> dict:
    """Rule of 40. Score = Growth Rate + Profit Margin"""
    r = saas.rule_of_40(growth_rate, profit_margin)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_saas_multiple(arr: float, multiple: float) -> dict:
    """SaaS revenue multiple valuation. Valuation = ARR × Multiple"""
    r = saas.saas_revenue_multiple_valuation(arr, multiple)
    return {"value": r.value, "method": r.method}


# ── Biotech ──────────────────────────────────────────────────────────
@mcp.tool()
def valuation_decision_tree(probabilities: list[float], terminal_value: float) -> dict:
    """Decision tree EV. EV = Π pᵢ × Terminal Value"""
    r = biotech.decision_tree_ev(probabilities, terminal_value)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_peak_sales(patient_population: float, penetration: float, price: float, compliance: float = 1.0) -> dict:
    """Peak sales. Peak = Population × Penetration × Price × Compliance"""
    r = biotech.peak_sales(patient_population, penetration, price, compliance)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_pipeline(drugs: list[dict], discount_rate: float) -> dict:
    """Biotech pipeline valuation. V = Σ(Peak Sales × Multiple × P_success) / (1+r)ⁿ"""
    r = biotech.pipeline_valuation(drugs, discount_rate)
    return {"value": r.value, "method": r.method}


# ── Fintech ──────────────────────────────────────────────────────────
@mcp.tool()
def valuation_payment_revenue(transaction_volume: float, take_rate: float) -> dict:
    """Payment revenue. Revenue = Volume × Take Rate"""
    r = fintech.payment_revenue(transaction_volume, take_rate)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_lending(loan_book: float, roe: float, pe_multiple: float, npl_reserves: float = 0) -> dict:
    """Lending fintech valuation. V = Loan Book × ROE × P/E - NPL Reserves"""
    r = fintech.lending_fintech_valuation(loan_book, roe, pe_multiple, npl_reserves)
    return {"value": r.value, "method": r.method}


# ── Marketplace ──────────────────────────────────────────────────────
@mcp.tool()
def valuation_take_rate(revenue: float, gmv: float) -> dict:
    """Marketplace take rate. Take Rate = Revenue / GMV"""
    r = marketplace.take_rate(revenue, gmv)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_gmv_multiple(gmv: float, multiple: float) -> dict:
    """GMV multiple valuation. Valuation = GMV × Multiple"""
    r = marketplace.gmv_multiple_valuation(gmv, multiple)
    return {"value": r.value, "method": r.method}


# ── Hardware ─────────────────────────────────────────────────────────
@mcp.tool()
def valuation_trl(market_size: float, market_share: float, margin: float, multiple: float, trl_discount: float) -> dict:
    """TRL-adjusted valuation. V = Market Size × Share × Margin × Multiple × (1 - TRL Discount)"""
    r = hardware.trl_adjusted_valuation(market_size, market_share, margin, multiple, trl_discount)
    return {"value": r.value, "method": r.method}


# ── International ────────────────────────────────────────────────────
@mcp.tool()
def valuation_ppp(spot_rate: float, inflation_foreign: float, inflation_domestic: float) -> dict:
    """Purchasing Power Parity. Eₜ = E₀ × (1+π_foreign)/(1+π_domestic)"""
    r = international.purchasing_power_parity(spot_rate, inflation_foreign, inflation_domestic)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_crp(sovereign_yield: float, us_treasury_yield: float) -> dict:
    """Country Risk Premium. CRP = Sovereign Yield - US Treasury Yield"""
    r = international.country_risk_premium(sovereign_yield, us_treasury_yield)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_intl_capm(risk_free_rate: float, beta: float, mrp: float, crp: float) -> dict:
    """International CAPM. r = Rf + β×MRP + CRP"""
    r = international.adjusted_capm_international(risk_free_rate, beta, mrp, crp)
    return {"value": r.value, "method": r.method}


# ── Stakeholders ─────────────────────────────────────────────────────
@mcp.tool()
def valuation_dilution(ownership_before: float, investment: float, post_money: float) -> dict:
    """Single round dilution. Ownership = Before × (1 - Investment/Post-Money)"""
    r = stakeholders.single_round_dilution(ownership_before, investment, post_money)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_opm(enterprise_value: float, liquidation_pref: float, time_to_exit: float, volatility: float) -> dict:
    """OPM common stock. C = V×N(d₁) - K×e^(-rT)×N(d₂)"""
    r = stakeholders.opm_common_stock(enterprise_value, liquidation_pref, time_to_exit, volatility)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_pwerm(scenarios: list[dict]) -> dict:
    """PWERM common stock. E[V] = Σ pᵢ × CommonValueᵢ"""
    r = stakeholders.pwerm(scenarios)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_liquidation(assets: dict, recovery_rates: dict) -> dict:
    """Liquidation value. V = Σ(Asset × Recovery Rate)"""
    r = stakeholders.liquidation_value(assets, recovery_rates)
    return {"value": r.value, "method": r.method}


# ── Emerging ─────────────────────────────────────────────────────────
@mcp.tool()
def valuation_safe_discount(series_a_price: float, discount: float) -> dict:
    """SAFE conversion price. Price = Series A × (1 - Discount)"""
    r = emerging.safe_conversion_discount(series_a_price, discount)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_token_value(transaction_volume: float, price_per_tx: float, velocity: float, supply: float) -> dict:
    """Token value via MV=PQ. Value = (Volume × Price) / (Velocity × Supply)"""
    r = emerging.equation_of_exchange(transaction_volume, price_per_tx, velocity, supply)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_esg_rate(base_rate: float, risk_premium: float = 0, opp_discount: float = 0) -> dict:
    """ESG-adjusted discount rate. r = base + risk_premium - opp_discount"""
    r = emerging.esg_adjusted_discount_rate(base_rate, risk_premium, opp_discount)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_metcalfes(n: float, k: float = 1.0) -> dict:
    """Metcalfe's Law. V = k × n²"""
    r = emerging.metcalfes_law(n, k)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_remote_npv(annual_savings: float, discount_rate: float) -> dict:
    """Remote cost savings NPV (perpetuity). NPV = Savings / r"""
    r = emerging.remote_cost_savings_npv(annual_savings, discount_rate)
    return {"value": r.value, "method": r.method}


# ── Compound Tool ────────────────────────────────────────────────────
@mcp.tool()
def valuation_full_analysis(
    average_valuation: float,
    weights: list[float],
    scores: list[float],
    terminal_value: float,
    target_return: float,
    investment: float,
) -> dict:
    """Run Scorecard + VC Method for comprehensive pre-revenue valuation.

    Returns triangulated valuation from multiple methods.
    """
    scorecard = core.scorecard_valuation(average_valuation, weights, scores)
    post_money = core.vc_method_post_money(terminal_value, target_return)
    pre_money = core.vc_method_pre_money(post_money.value, investment)

    return {
        "scorecard": {"value": scorecard.value, "method": scorecard.method},
        "vc_post_money": {"value": post_money.value, "method": post_money.method},
        "vc_pre_money": {"value": pre_money.value, "method": pre_money.method},
        "triangulated_mean": (scorecard.value + pre_money.value) / 2,
    }


if __name__ == "__main__":
    mcp.run()
