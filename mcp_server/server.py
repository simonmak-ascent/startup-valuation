"""MCP Server for Startup Valuation Engine."""

from fastmcp import FastMCP

from startup_valuation import (
    advanced,
    biotech,
    capm,
    comparables,
    core,
    emerging,
    fintech,
    hardware,
    international,
    marketplace,
    probability,
    saas,
    stakeholders,
    tv,
)

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


# ── New Functions ────────────────────────────────────────────────────
@mcp.tool()
def valuation_expected_value_continuous(lower: float, upper: float) -> dict:
    """Calculate expected value for a continuous random variable using numerical integration."""
    import scipy.stats
    r = probability.expected_value_continuous(scipy.stats.norm(0, 1).pdf, lower, upper)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_binomial(
    underlying: float, strike: float, risk_free_rate: float,
    volatility: float, time_to_maturity: float, steps: int = 50,
) -> dict:
    """High-resolution binomial tree valuation for startup options."""
    r = advanced.binomial_valuation(underlying, strike, risk_free_rate, volatility, time_to_maturity, steps)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_payment_processor(
    transaction_volume: float, take_rate: float, growth_rate: float,
    discount_rate: float, terminal_multiple: float, years: int = 5,
) -> dict:
    """Value a payment processor using DCF of payment revenue."""
    r = fintech.payment_processor_valuation(
        transaction_volume, take_rate, growth_rate, discount_rate, terminal_multiple, years,
    )
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_neobank(
    customers: int, arpu: float, gross_margin: float,
    churn_rate: float, pe_multiple: float,
) -> dict:
    """Value a neobank using customer-based LTV × P/E model."""
    r = fintech.neobank_valuation(customers, arpu, gross_margin, churn_rate, pe_multiple)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_buyer_retention(buyers_period_1: int, buyers_repeat: int) -> dict:
    """Calculate marketplace buyer retention rate."""
    r = marketplace.buyer_retention(buyers_period_1, buyers_repeat)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_network_density(active_buyers: int, active_sellers: int, total_users: int) -> dict:
    """Calculate marketplace network density ratio."""
    r = marketplace.network_density(active_buyers, active_sellers, total_users)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_risk_adjusted_synergy(
    revenue_synergies: float, cost_synergies: float,
    prob_revenue: float = 0.4, prob_cost: float = 0.8,
    discount_rate: float = 0.10, years: int = 3,
) -> dict:
    """Calculate risk-adjusted synergy value for M&A."""
    r = stakeholders.risk_adjusted_synergy(
        revenue_synergies, cost_synergies, prob_revenue, prob_cost, discount_rate, years,
    )
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_intrinsic_option(strike_price: float, fair_market_value: float, shares: int) -> dict:
    """Calculate intrinsic value of equity options."""
    r = stakeholders.intrinsic_option_value(strike_price, fair_market_value, shares)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_employee_option(scenarios: list[dict]) -> dict:
    """Calculate employee option value using probability-weighted scenarios."""
    r = stakeholders.probability_weighted_employee_value(scenarios)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_vesting_adjusted(
    total_value: float, vested_fraction: float,
    annual_vest_rate: float = 0.25, retention_prob: float = 0.8,
    years_remaining: int = 3,
) -> dict:
    """Calculate option value adjusted for vesting schedule."""
    r = stakeholders.vesting_adjusted_value(
        total_value, vested_fraction, annual_vest_rate, retention_prob, years_remaining,
    )
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_cash_equity_breakeven(
    salary_reduction: float, equity_value: float,
    tax_rate: float = 0.30, discount_rate: float = 0.20, years: int = 4,
) -> dict:
    """Calculate breakeven for cash vs equity tradeoff."""
    r = stakeholders.cash_equity_breakeven(salary_reduction, equity_value, tax_rate, discount_rate, years)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_max_asset_loan(
    cash: float = 0, accounts_receivable: float = 0,
    inventory: float = 0, equipment: float = 0, real_estate: float = 0,
) -> dict:
    """Calculate maximum asset-based loan amount."""
    r = stakeholders.max_asset_based_loan(cash, accounts_receivable, inventory, equipment, real_estate)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_safe_cap(cap: float, series_a_price: float) -> dict:
    """Calculate SAFE conversion price using valuation cap."""
    r = emerging.safe_conversion_cap(cap, series_a_price)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_safe_expected(
    investment: float, cap: float, discount: float,
    series_a_valuation: float, series_a_price: float,
) -> dict:
    """Calculate expected SAFE value across cap and discount scenarios."""
    r = emerging.safe_expected_value(investment, cap, discount, series_a_valuation, series_a_price)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_nvt_ratio(market_cap: float, daily_transaction_volume: float) -> dict:
    """Calculate Network Value to Transactions ratio."""
    r = emerging.nvt_ratio(market_cap, daily_transaction_volume)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_esg_premium(base_valuation: float, esg_score: float, premium_per_point: float = 0.02) -> dict:
    """Calculate ESG premium impact on valuation."""
    r = emerging.esg_premium_valuation(base_valuation, esg_score, premium_per_point)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_esg_discount(base_valuation: float, esg_risk_score: float, discount_per_point: float = 0.01) -> dict:
    """Calculate ESG risk discount on valuation."""
    r = emerging.esg_discount_valuation(base_valuation, esg_risk_score, discount_per_point)
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_data_moat(
    data_volume: float, data_uniqueness: float, monetization_rate: float,
    competitive_advantage_years: float, discount_rate: float = 0.15,
) -> dict:
    """Calculate value of data as a competitive moat."""
    r = emerging.data_moat_value(
        data_volume, data_uniqueness, monetization_rate, competitive_advantage_years, discount_rate,
    )
    return {"value": r.value, "method": r.method}


@mcp.tool()
def valuation_remote_premium(
    base_valuation: float, cost_savings_pct: float = 0.20,
    talent_access_premium: float = 0.10, productivity_gain: float = 0.05,
) -> dict:
    """Calculate remote-first company valuation premium."""
    r = emerging.remote_first_premium(base_valuation, cost_savings_pct, talent_access_premium, productivity_gain)
    return {"value": r.value, "method": r.method}


if __name__ == "__main__":
    mcp.run()
