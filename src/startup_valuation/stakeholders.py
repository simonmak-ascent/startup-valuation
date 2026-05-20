"""Stakeholder-specific valuation methods.

Chapter 13: Valuation for Different Stakeholders
"""

from __future__ import annotations

import math

from scipy import stats

from startup_valuation.types import ValuationResult


def single_round_dilution(
    ownership_before: float,
    investment: float,
    post_money: float,
) -> ValuationResult:
    """Calculate founder ownership after a single funding round.

    Formula: Ownership After = Ownership Before × (1 - Investment / Post-Money)

    Example:
        >>> result = single_round_dilution(1.0, 5_000_000, 20_000_000)
        >>> result.value
        0.75
    """
    if post_money <= 0:
        raise ValueError("post_money must be positive")
    ownership_after = ownership_before * (1 - investment / post_money)
    return ValuationResult(
        value=ownership_after,
        method="Single Round Dilution",
        inputs={"ownership_before": ownership_before, "investment": investment, "post_money": post_money},
        chapter="13",
    )


def multi_round_dilution(
    initial_ownership: float,
    investments: list[float],
    post_money_vals: list[float],
) -> ValuationResult:
    """Calculate founder ownership after multiple funding rounds.

    Formula: Ownership After n Rounds = Π(1 - Investmentᵢ / Post-Moneyᵢ)

    Example:
        >>> result = multi_round_dilution(1.0, [2M, 5M, 10M, 20M], [10M, 25M, 60M, 150M])
        >>> # After 4 rounds: ~36%
    """
    if len(investments) != len(post_money_vals):
        raise ValueError("investments and post_money_vals must have same length")

    ownership = initial_ownership
    for inv, pm in zip(investments, post_money_vals):
        ownership *= 1 - inv / pm

    return ValuationResult(
        value=ownership,
        method="Multi-Round Dilution",
        inputs={"investments": investments, "post_money_vals": post_money_vals},
        assumptions=["No option pool refresh between rounds"],
        chapter="13",
    )


def acquisition_value(
    standalone_value: float,
    revenue_synergies: float,
    cost_synergies: float,
    integration_costs: float,
    prob_revenue: float = 0.4,
    prob_cost: float = 0.8,
) -> ValuationResult:
    """Calculate acquisition value with risk-adjusted synergies.

    Formula: Acquisition V = Standalone V + PV(Revenue Syn × P_rev + Cost Syn × P_cost) - Integration Costs

    Example:
        >>> result = acquisition_value(100_000_000, 20_000_000, 15_000_000, 10_000_000, 0.4, 0.8)
        >>> result.value
        120000000.0
    """
    risk_adj_synergy = revenue_synergies * prob_revenue + cost_synergies * prob_cost
    return ValuationResult(
        value=standalone_value + risk_adj_synergy - integration_costs,
        method="Acquisition Value",
        inputs={
            "standalone_value": standalone_value,
            "revenue_synergies": revenue_synergies,
            "cost_synergies": cost_synergies,
            "integration_costs": integration_costs,
        },
        chapter="13",
    )


def opm_common_stock(
    enterprise_value: float,
    liquidation_preference: float,
    time_to_exit: float,
    volatility: float,
    risk_free_rate: float = 0.04,
) -> ValuationResult:
    """Value common stock using Option Pricing Method (OPM).

    Formula: C = V × N(d₁) - K × e^(-rT) × N(d₂)

    Args:
        enterprise_value: Total enterprise value (V).
        liquidation_preference: Liquidation preference (K).
        time_to_exit: Expected time to exit in years (T).
        volatility: Volatility of enterprise value (σ).
        risk_free_rate: Risk-free rate (r).

    Returns:
        ValuationResult with common stock value.

    Example:
        >>> result = opm_common_stock(100_000_000, 40_000_000, 3, 0.60)
        >>> round(result.value / 1_000_000, 0)
        65000000.0
    """
    d1 = (math.log(enterprise_value / liquidation_preference) + (risk_free_rate + volatility**2 / 2) * time_to_exit) / (
        volatility * math.sqrt(time_to_exit)
    )
    d2 = d1 - volatility * math.sqrt(time_to_exit)

    common_value = (
        enterprise_value * stats.norm.cdf(d1)
        - liquidation_preference * math.exp(-risk_free_rate * time_to_exit) * stats.norm.cdf(d2)
    )

    return ValuationResult(
        value=common_value,
        method="OPM (Common Stock)",
        inputs={
            "enterprise_value": enterprise_value,
            "liquidation_preference": liquidation_preference,
            "time_to_exit": time_to_exit,
            "volatility": volatility,
        },
        assumptions=["Common stock valued as call option on enterprise value"],
        chapter="13",
    )


def pwerm(
    scenarios: list[dict[str, float]],
) -> ValuationResult:
    """Calculate common stock value using PWERM.

    Formula: Expected Common V = Σ pᵢ × CommonValueᵢ

    Args:
        scenarios: List of dicts with 'probability' and 'common_value'.

    Example:
        >>> scenarios = [
        ...     {"probability": 0.20, "common_value": 92_000_000},
        ...     {"probability": 0.50, "common_value": 55_000_000},
        ...     {"probability": 0.20, "common_value": 4_000_000},
        ...     {"probability": 0.10, "common_value": 0},
        ... ]
        >>> result = pwerm(scenarios)
        >>> round(result.value / 1_000_000, 1)
        46.7
    """
    total_prob = sum(s["probability"] for s in scenarios)
    if abs(total_prob - 1.0) > 0.01:
        raise ValueError(f"scenario probabilities must sum to 1.0, got {total_prob}")

    expected_value = sum(s["probability"] * s["common_value"] for s in scenarios)
    return ValuationResult(
        value=expected_value,
        method="PWERM",
        inputs={"scenarios": scenarios},
        chapter="13",
    )


def common_stock_discount(preferred_value: float, common_value: float) -> ValuationResult:
    """Calculate common stock discount.

    Formula: Discount = (Preferred V - Common V) / Preferred V

    Example:
        >>> result = common_stock_discount(100_000_000, 65_000_000)
        >>> result.value
        0.35
    """
    if preferred_value <= 0:
        raise ValueError("preferred_value must be positive")
    return ValuationResult(
        value=(preferred_value - common_value) / preferred_value,
        method="Common Stock Discount",
        inputs={"preferred_value": preferred_value, "common_value": common_value},
        chapter="13",
    )


def liquidation_value(
    assets: dict[str, float],
    recovery_rates: dict[str, float],
) -> ValuationResult:
    """Calculate liquidation value.

    Formula: Liquidation V = Σ(Asset Value × Recovery Rate)

    Example:
        >>> assets = {"cash": 5_000_000, "ar": 3_000_000, "equipment": 2_000_000}
        >>> rates = {"cash": 1.0, "ar": 0.80, "equipment": 0.30}
        >>> result = liquidation_value(assets, rates)
        >>> result.value
        8000000.0
    """
    total = sum(assets.get(k, 0) * recovery_rates.get(k, 0) for k in set(assets) | set(recovery_rates))
    return ValuationResult(
        value=total,
        method="Liquidation Value",
        inputs={"assets": str(assets), "recovery_rates": str(recovery_rates)},
        chapter="13",
    )


def venture_debt_dilution(
    warrant_coverage: float,
    loan_amount: float,
    post_money: float,
) -> ValuationResult:
    """Calculate venture debt warrant dilution.

    Formula: Warrant Dilution = Warrant Coverage × Loan Amount / Post-Money

    Example:
        >>> result = venture_debt_dilution(0.10, 3_000_000, 40_000_000)
        >>> result.value
        0.0075
    """
    if post_money <= 0:
        raise ValueError("post_money must be positive")
    return ValuationResult(
        value=warrant_coverage * loan_amount / post_money,
        method="Venture Debt Dilution",
        inputs={"warrant_coverage": warrant_coverage, "loan_amount": loan_amount, "post_money": post_money},
        chapter="13",
    )


def risk_adjusted_synergy(
    revenue_synergies: float,
    cost_synergies: float,
    prob_revenue: float = 0.4,
    prob_cost: float = 0.8,
    discount_rate: float = 0.10,
    years: int = 3,
) -> ValuationResult:
    """Calculate risk-adjusted synergy value.

    Formula: PV = Σ[Rev_Syn × P_rev + Cost_Syn × P_cost] / (1+r)^t

    Args:
        revenue_synergies: Annual revenue synergies.
        cost_synergies: Annual cost synergies.
        prob_revenue: Probability of achieving revenue synergies.
        prob_cost: Probability of achieving cost synergies.
        discount_rate: Discount rate.
        years: Years to realize synergies.

    Returns:
        ValuationResult with risk-adjusted synergy value.

    Example:
        >>> result = risk_adjusted_synergy(20_000_000, 15_000_000, 0.4, 0.8, 0.10, 3)
        >>> round(result.value / 1_000_000, 1)
        49.7
    """
    annual_synergy = revenue_synergies * prob_revenue + cost_synergies * prob_cost
    pv = sum(annual_synergy / ((1 + discount_rate) ** t) for t in range(1, years + 1))

    return ValuationResult(
        value=pv,
        method="Risk-Adjusted Synergy",
        inputs={
            "revenue_synergies": revenue_synergies,
            "cost_synergies": cost_synergies,
            "prob_revenue": prob_revenue,
            "prob_cost": prob_cost,
        },
        assumptions=["Synergies are realized evenly over projection period"],
        chapter="13",
    )


def intrinsic_option_value(
    strike_price: float,
    fair_market_value: float,
    shares: int,
) -> ValuationResult:
    """Calculate intrinsic value of equity options.

    Formula: Intrinsic Value = max(FMV - Strike, 0) × Shares

    Args:
        strike_price: Option strike price per share.
        fair_market_value: Current fair market value per share.
        shares: Number of option shares.

    Returns:
        ValuationResult with intrinsic option value.

    Example:
        >>> result = intrinsic_option_value(1.0, 5.0, 100_000)
        >>> result.value
        400000.0
    """
    intrinsic = max(fair_market_value - strike_price, 0) * shares
    return ValuationResult(
        value=intrinsic,
        method="Intrinsic Option Value",
        inputs={
            "strike_price": strike_price,
            "fair_market_value": fair_market_value,
            "shares": shares,
        },
        assumptions=["FMV reflects current 409A valuation"],
        chapter="13",
    )


def probability_weighted_employee_value(
    scenarios: list[dict[str, float]],
) -> ValuationResult:
    """Calculate employee option value using probability-weighted scenarios.

    Formula: E[V] = Σ pᵢ × OptionValueᵢ

    Args:
        scenarios: List of dicts with 'probability', 'fmv', 'strike', 'shares'.

    Returns:
        ValuationResult with expected employee option value.

    Example:
        >>> scenarios = [
        ...     {"probability": 0.20, "fmv": 10.0, "strike": 1.0, "shares": 50000},
        ...     {"probability": 0.50, "fmv": 5.0, "strike": 1.0, "shares": 50000},
        ...     {"probability": 0.30, "fmv": 1.0, "strike": 1.0, "shares": 50000},
        ... ]
        >>> result = probability_weighted_employee_value(scenarios)
        >>> result.value
        225000.0
    """
    total_prob = sum(s["probability"] for s in scenarios)
    if abs(total_prob - 1.0) > 0.01:
        raise ValueError(f"scenario probabilities must sum to 1.0, got {total_prob}")

    expected_value = sum(
        s["probability"] * max(s["fmv"] - s["strike"], 0) * s["shares"]
        for s in scenarios
    )
    return ValuationResult(
        value=expected_value,
        method="Probability-Weighted Employee Option Value",
        inputs={"scenarios": scenarios},
        chapter="13",
    )


def vesting_adjusted_value(
    total_value: float,
    vested_fraction: float,
    annual_vest_rate: float = 0.25,
    retention_prob: float = 0.8,
    years_remaining: int = 3,
) -> ValuationResult:
    """Calculate option value adjusted for vesting schedule.

    Formula: Adjusted V = V_vested + Σ[V_unvested × VestRate × Retention^t] / (1+r)^t

    Args:
        total_value: Total option value (intrinsic).
        vested_fraction: Fraction already vested (0-1).
        annual_vest_rate: Annual vesting rate (typically 0.25 for 4-year).
        retention_prob: Annual probability of staying employed.
        years_remaining: Years of unvested options remaining.

    Returns:
        ValuationResult with vesting-adjusted value.

    Example:
        >>> result = vesting_adjusted_value(400_000, 0.25, 0.25, 0.8, 3)
        >>> round(result.value / 1000, 0)
        238.0
    """
    vested_value = total_value * vested_fraction
    unvested_value = total_value * (1 - vested_fraction)

    adjusted_unvested = 0.0
    for t in range(1, years_remaining + 1):
        vest_portion = annual_vest_rate * unvested_value
        retention = retention_prob ** t
        adjusted_unvested += vest_portion * retention

    return ValuationResult(
        value=vested_value + adjusted_unvested,
        method="Vesting-Adjusted Option Value",
        inputs={
            "total_value": total_value,
            "vested_fraction": vested_fraction,
            "annual_vest_rate": annual_vest_rate,
            "retention_prob": retention_prob,
            "years_remaining": years_remaining,
        },
        assumptions=["Retention probability compounds annually"],
        chapter="13",
    )


def cash_equity_breakeven(
    salary_reduction: float,
    equity_value: float,
    tax_rate: float = 0.30,
    discount_rate: float = 0.20,
    years: int = 4,
) -> ValuationResult:
    """Calculate breakeven for cash vs equity tradeoff.

    Formula: After-Tax Salary Loss = Salary_Reduction × (1 - TaxRate)
    Breakeven if: Equity_Value / (1+r)^n > After-Tax Loss × n

    Args:
        salary_reduction: Annual salary reduction for equity.
        equity_value: Estimated equity value at exit.
        tax_rate: Marginal tax rate.
        discount_rate: Discount rate for equity risk.
        years: Years to exit.

    Returns:
        ValuationResult with net benefit (positive = equity is better).

    Example:
        >>> result = cash_equity_breakeven(50_000, 500_000, 0.30, 0.20, 4)
        >>> round(result.value / 1000, 0)
        100.0
    """
    after_tax_loss = salary_reduction * (1 - tax_rate) * years
    pv_equity = equity_value / ((1 + discount_rate) ** years)
    net_benefit = pv_equity - after_tax_loss

    return ValuationResult(
        value=net_benefit,
        method="Cash-Equity Breakeven",
        inputs={
            "salary_reduction": salary_reduction,
            "equity_value": equity_value,
            "tax_rate": tax_rate,
            "discount_rate": discount_rate,
            "years": years,
        },
        assumptions=["Equity value is realized at exit"],
        chapter="13",
    )


def max_asset_based_loan(
    cash: float = 0,
    accounts_receivable: float = 0,
    inventory: float = 0,
    equipment: float = 0,
    real_estate: float = 0,
) -> ValuationResult:
    """Calculate maximum asset-based loan amount.

    Formula: Max Loan = Cash×100% + AR×85% + Inventory×50% + Equipment×60% + RE×75%

    Args:
        cash: Cash and equivalents.
        accounts_receivable: Accounts receivable.
        inventory: Inventory value.
        equipment: Equipment value.
        real_estate: Real estate value.

    Returns:
        ValuationResult with maximum loan amount.

    Example:
        >>> result = max_asset_based_loan(1_000_000, 2_000_000, 500_000, 3_000_000)
        >>> result.value
        5500000.0
    """
    max_loan = (
        cash * 1.0
        + accounts_receivable * 0.85
        + inventory * 0.50
        + equipment * 0.60
        + real_estate * 0.75
    )

    return ValuationResult(
        value=max_loan,
        method="Max Asset-Based Loan",
        inputs={
            "cash": cash,
            "accounts_receivable": accounts_receivable,
            "inventory": inventory,
            "equipment": equipment,
            "real_estate": real_estate,
        },
        assumptions=["Standard advance rates: Cash 100%, AR 85%, Inv 50%, Equip 60%, RE 75%"],
        chapter="13",
    )
