"""Biotech and pharmaceutical valuation methods.

Chapter 11: Industry-Specific Valuation Frameworks — Biotech
"""

from __future__ import annotations

import math

from startup_valuation.types import ValuationResult


def rnPV(
    cash_flows: list[float],
    probabilities: list[float],
    discount_rate: float,
    development_costs: float = 0,
) -> ValuationResult:
    """Calculate risk-adjusted NPV for biotech.

    Formula: rNPV = Σ[P_success × CFₜ / (1+r)ᵗ] - Development Costs

    Args:
        cash_flows: Cash flows at each period.
        probabilities: Cumulative probability of success at each period.
        discount_rate: Discount rate.
        development_costs: Remaining development costs.

    Returns:
        ValuationResult with rNPV.
    """
    if len(cash_flows) != len(probabilities):
        raise ValueError("cash_flows and probabilities must have same length")

    rnpv = sum(
        p * cf / ((1 + discount_rate) ** t)
        for t, (cf, p) in enumerate(zip(cash_flows, probabilities))
    ) - development_costs

    return ValuationResult(
        value=rnpv,
        method="Risk-Adjusted NPV (rNPV)",
        inputs={
            "cash_flows": cash_flows,
            "probabilities": probabilities,
            "discount_rate": discount_rate,
            "development_costs": development_costs,
        },
        assumptions=["Probabilities are cumulative success probabilities"],
        chapter="11",
    )


def decision_tree_ev(
    probabilities: list[float],
    terminal_value: float,
) -> ValuationResult:
    """Calculate expected value from decision tree.

    Formula: EV = Π pᵢ × Terminal Value

    Example:
        >>> result = decision_tree_ev([0.35, 0.60, 0.90], 500_000_000)
        >>> result.value
        94500000.0
    """
    joint_prob = math.prod(probabilities)
    return ValuationResult(
        value=joint_prob * terminal_value,
        method="Decision Tree Expected Value",
        inputs={"probabilities": probabilities, "terminal_value": terminal_value},
        assumptions=["All stages must succeed sequentially"],
        chapter="11",
    )


def peak_sales(
    patient_population: float,
    penetration_rate: float,
    price: float,
    compliance_rate: float = 1.0,
) -> ValuationResult:
    """Calculate peak sales for a drug.

    Formula: Peak Sales = Population × Penetration × Price × Compliance

    Example:
        >>> result = peak_sales(50_000, 0.40, 150_000, 0.90)
        >>> result.value
        2700000000.0
    """
    return ValuationResult(
        value=patient_population * penetration_rate * price * compliance_rate,
        method="Peak Sales",
        inputs={
            "patient_population": patient_population,
            "penetration_rate": penetration_rate,
            "price": price,
            "compliance_rate": compliance_rate,
        },
        chapter="11",
    )


def pipeline_valuation(
    drugs: list[dict[str, float]],
    discount_rate: float,
) -> ValuationResult:
    """Value a biotech pipeline.

    Formula: V = Σ(Peak Sales × Multiple × P_success) / (1+r)ⁿ

    Args:
        drugs: List of dicts with keys: peak_sales, multiple, p_success, years_to_peak.
        discount_rate: Discount rate.

    Returns:
        ValuationResult with pipeline value.

    Example:
        >>> drugs = [{"peak_sales": 2_000_000_000, "multiple": 5, "p_success": 0.60, "years_to_peak": 2}]
        >>> result = pipeline_valuation(drugs, 0.12)
        >>> round(result.value / 1_000_000_000, 2)
        4.78
    """
    total_value = 0
    for drug in drugs:
        ps = drug["peak_sales"]
        m = drug["multiple"]
        p = drug["p_success"]
        n = drug["years_to_peak"]
        total_value += (ps * m * p) / ((1 + discount_rate) ** n)

    return ValuationResult(
        value=total_value,
        method="Biotech Pipeline Valuation",
        inputs={"num_drugs": len(drugs), "discount_rate": discount_rate},
        assumptions=["Multiple is 3-5x peak sales for approved drugs"],
        chapter="11",
    )


def overall_success_probability(
    stage_probabilities: list[float],
) -> ValuationResult:
    """Calculate overall probability of success across all stages.

    Formula: P_total = Π P_stage

    Example:
        >>> result = overall_success_probability([0.35, 0.60, 0.90])
        >>> round(result.value, 4)
        0.189
    """
    return ValuationResult(
        value=math.prod(stage_probabilities),
        method="Overall Success Probability",
        inputs={"stage_probabilities": stage_probabilities},
        assumptions=["Stages are sequential and independent"],
        chapter="11",
    )
