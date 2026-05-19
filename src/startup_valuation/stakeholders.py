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

    common_value = enterprise_value * stats.norm.cdf(d1) - liquidation_preference * math.exp(-risk_free_rate * time_to_exit) * stats.norm.cdf(d2)
    discount = (enterprise_value - common_value) / enterprise_value

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
    scenarios: list[dict],
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
        inputs={"assets": assets, "recovery_rates": recovery_rates},
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
