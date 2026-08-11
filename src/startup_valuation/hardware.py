"""Hardware and deep tech valuation methods.

Chapter 11: Industry-Specific Valuation Frameworks — Hardware
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def trl_adjusted_valuation(
    market_size: float,
    market_share: float,
    margin: float,
    multiple: float,
    trl_discount: float,
) -> ValuationResult:
    """Calculate TRL-adjusted valuation.

    Formula: Valuation = Market Size × Market Share × Margin × Multiple × (1 - TRL Discount)

    TRL discount: TRL 1-5: 70-95%, TRL 6-7: 40-60%, TRL 8-9: 10-30%

    Example:
        >>> result = trl_adjusted_valuation(10_000_000_000, 0.05, 0.40, 15, 0.80)
        >>> result.value / 1_000_000_000
        0.6
    """
    return ValuationResult(
        value=market_size * market_share * margin * multiple * (1 - trl_discount),
        method="TRL-Adjusted Valuation",
        inputs={
            "market_size": market_size,
            "market_share": market_share,
            "margin": margin,
            "multiple": multiple,
            "trl_discount": trl_discount,
        },
        assumptions=[
            "TRL discount reflects technology maturity risk",
            "Market size, share, and margin estimates are accurate",
            "Revenue multiple is from comparable hardware exits",
        ],
        chapter="11",
    )


def gross_margin_hardware(asp: float, cogs: float) -> ValuationResult:
    """Calculate hardware gross margin.

    Formula: Gross Margin = (ASP - COGS) / ASP
    """
    if asp <= 0:
        raise ValueError("asp must be positive")
    return ValuationResult(
        value=(asp - cogs) / asp,
        method="Hardware Gross Margin",
        inputs={"asp": asp, "cogs": cogs},
        chapter="11",
        assumptions=[
            "ASP reflects market pricing for comparable products",
            "COGS includes all direct manufacturing costs",
            "No volume discounts or economies of scale in COGS",
        ],
    )


def break_even_volume(fixed_costs: float, asp: float, variable_cost: float) -> ValuationResult:
    """Calculate break-even volume.

    Formula: Break-Even Volume = Fixed Costs / (ASP - Variable Cost per Unit)
    """
    contribution = asp - variable_cost
    if contribution <= 0:
        raise ValueError("ASP must exceed variable cost for break-even")
    return ValuationResult(
        value=fixed_costs / contribution,
        method="Break-Even Volume",
        inputs={"fixed_costs": fixed_costs, "asp": asp, "variable_cost": variable_cost},
        chapter="11",
        assumptions=[
            "Fixed costs are accurately estimated",
            "ASP and variable costs are stable at volume",
            "Production can scale linearly to meet volume",
        ],
    )


def probability_weighted_dcf(
    probabilities: list[float],
    values: list[float],
) -> ValuationResult:
    """Calculate probability-weighted DCF.

    Formula: E[V] = Σ pᵢ × Vᵢ

    Example:
        >>> result = probability_weighted_dcf([0.30, 0.40, 0.30], [60_000_000_000, 10_000_000_000, 0])
        >>> result.value / 1_000_000_000
        22.0
    """
    if len(probabilities) != len(values):
        raise ValueError("probabilities and values must have same length")
    return ValuationResult(
        value=sum(p * v for p, v in zip(probabilities, values)),
        method="Probability-Weighted DCF",
        inputs={"probabilities": probabilities, "values": values},
        chapter="11",
        assumptions=[
            "Probabilities sum to approximately 1.0",
            "Scenario values are independently estimated",
            "No intermediate or partial-success outcomes",
        ],
    )
