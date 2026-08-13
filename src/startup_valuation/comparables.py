"""Market comparables and regression-adjusted multiples.

Chapter 5: Market Comparables
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def pe_ratio(market_cap: float, net_income: float) -> ValuationResult:
    """Calculate P/E ratio.

    Formula: P/E = Market Cap / Net Income
    """
    if net_income <= 0:
        raise ValueError("net_income must be positive for P/E ratio")
    return ValuationResult(
        value=market_cap / net_income,
        steps=[
            {
                "label": "P/E Ratio",
                "value": market_cap / net_income,
                "formula": r"P/E = market\_cap \div net\_income",
            },
        ],
        method="P/E Ratio",
        inputs={"market_cap": market_cap, "net_income": net_income},
        chapter="5",
        formula_number="5",
    )


def ps_ratio(market_cap: float, revenue: float) -> ValuationResult:
    """Calculate P/S ratio.

    Formula: P/S = Market Cap / Revenue

    Example:
        >>> result = ps_ratio(500_000_000, 100_000_000)
        >>> result.value
        5.0
    """
    if revenue <= 0:
        raise ValueError("revenue must be positive")
    return ValuationResult(
        value=market_cap / revenue,
        steps=[
            {
                "label": "P/S Ratio",
                "value": market_cap / revenue,
                "formula": r"P/S = market\_cap \div revenue",
            },
        ],
        method="P/S Ratio",
        inputs={"market_cap": market_cap, "revenue": revenue},
        chapter="5",
        formula_number="5",
    )


def ev_ebitda(enterprise_value: float, ebitda: float) -> ValuationResult:
    """Calculate EV/EBITDA ratio.

    Formula: EV/EBITDA = Enterprise Value / EBITDA
    """
    if ebitda <= 0:
        raise ValueError("ebitda must be positive")
    return ValuationResult(
        value=enterprise_value / ebitda,
        steps=[
            {
                "label": "EV/EBITDA",
                "value": enterprise_value / ebitda,
                "formula": r"EV/EBITDA = EV \div EBITDA",
            },
        ],
        method="EV/EBITDA",
        inputs={"enterprise_value": enterprise_value, "ebitda": ebitda},
        chapter="5",
        formula_number="5",
    )


def ev_revenue(enterprise_value: float, revenue: float) -> ValuationResult:
    """Calculate EV/Revenue ratio."""
    if revenue <= 0:
        raise ValueError("revenue must be positive")
    return ValuationResult(
        value=enterprise_value / revenue,
        steps=[
            {
                "label": "EV/Revenue",
                "value": enterprise_value / revenue,
                "formula": r"EV/Revenue = EV \div revenue",
            },
        ],
        method="EV/Revenue",
        inputs={"enterprise_value": enterprise_value, "revenue": revenue},
        chapter="5",
        formula_number="5",
    )


def regression_adjusted_multiple(
    intercept: float,
    growth_rate: float,
    growth_coefficient: float,
    market_maturity: float = 0,
    maturity_coefficient: float = 0,
    stage: float = 0,
    stage_coefficient: float = 0,
    geography: float = 0,
    geography_coefficient: float = 0,
) -> ValuationResult:
    """Calculate regression-adjusted valuation multiple.

    Formula: Multiple = β₀ + β₁×g + β₂×M + β₃×S + β₄×G + ε

    Args:
        intercept: Base multiple (β₀).
        growth_rate: Revenue growth rate (g).
        growth_coefficient: Coefficient for growth (β₁).
        market_maturity: Market maturity indicator (M).
        maturity_coefficient: Coefficient for maturity (β₂).
        stage: Company stage indicator (S).
        stage_coefficient: Coefficient for stage (β₃).
        geography: Geography indicator (G).
        geography_coefficient: Coefficient for geography (β₄).

    Returns:
        ValuationResult with adjusted multiple.

    Example:
        >>> result = regression_adjusted_multiple(2.5, 0.30, 10, 1, 0.5, 0, -1.5, 0, -0.2)
        >>> result.value
        6.0
    """
    multiple = (
        intercept
        + growth_coefficient * growth_rate
        + maturity_coefficient * market_maturity
        + stage_coefficient * stage
        + geography_coefficient * geography
    )

    return ValuationResult(
        value=multiple,
        steps=[
            {
                "label": "Regression-Adjusted Multiple",
                "value": multiple,
                "formula": r"Multiple = intercept + coef \times factor",
            },
        ],
        method="Regression-Adjusted Multiple",
        inputs={
            "intercept": intercept,
            "growth_rate": growth_rate,
            "growth_coefficient": growth_coefficient,
        },
        assumptions=["Regression coefficients are from comparable company analysis"],
        chapter="5",
        formula_number="5",
    )


def target_valuation_multiple(multiple: float, metric: float) -> ValuationResult:
    """Calculate target valuation using a comparable multiple.

    Formula: Valuation = Multiple × Metric

    Example:
        >>> result = target_valuation_multiple(5.5, 8_000_000)
        >>> result.value
        44000000.0
    """
    return ValuationResult(
        value=multiple * metric,
        steps=[
            {
                "label": "Target Valuation (Multiple)",
                "value": multiple * metric,
                "formula": r"V = multiple \times metric",
            },
        ],
        method="Target Valuation (Multiple)",
        inputs={"multiple": multiple, "metric": metric},
        assumptions=["Multiple is from comparable companies"],
        chapter="5",
        formula_number="5",
    )
