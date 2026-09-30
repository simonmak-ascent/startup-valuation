"""Revenue growth and forecasting calculations.

Chapter 2: Mathematical Foundations — Time Value of Money
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def compound_growth(starting_value: float, growth_rate: float, periods: float) -> ValuationResult:
    """Project a value forward at a constant compound growth rate.

    Formula: V_n = V_0 (1 + g)^n

    Args:
        starting_value: Value at t=0 (revenue or cash flow, in currency units).
        growth_rate: Constant per-period growth rate (g) as a decimal.
        periods: Number of periods (n) to project forward.

    Returns:
        ValuationResult with the projected value at t=n.

    Raises:
        ValueError: If growth_rate <= -1 or periods < 0.

    Notes:
        Compounding projects a starting revenue or cash flow forward under a
        constant growth assumption:

        $$V_n = V_0 (1 + g)^n$$

        The inverse of discounting; a positive growth rate raises the future
        value, a negative rate models decline.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.2.

    See Also:
        compound_annual_growth_rate : Implied rate between two values.
        present_value : Discount a future value back to today.

    Example:
        >>> result = compound_growth(1_000_000, 0.4, 3)
        >>> round(result.value, 2)
        2744000.0
    """
    if growth_rate <= -1:
        raise ValueError("growth_rate must be > -1")
    if periods < 0:
        raise ValueError("periods must be >= 0")

    value = starting_value * (1 + growth_rate) ** periods

    return ValuationResult(
        value=value,
        method="Compound Growth",
        inputs={"starting_value": starting_value, "growth_rate": growth_rate, "periods": periods},
        assumptions=["Constant growth rate applied over the full horizon"],
        chapter="Chapter 2",
        formula_number="2.1",
        steps=[
            {
                "label": "Compound value",
                "value": value,
                "formula": r"V_n = V_0 (1+g)^n",
            },
        ],
    )


def compound_annual_growth_rate(starting_value: float, ending_value: float, periods: float) -> ValuationResult:
    """Compute the compound annual growth rate (CAGR) implied by two values.

    Formula: CAGR = (V_n / V_0)^(1/n) - 1

    Args:
        starting_value: Value at t=0 (V_0), must be > 0.
        ending_value: Value at t=n (V_n), must be >= 0.
        periods: Number of periods (n) between the two values, must be > 0.

    Returns:
        ValuationResult with CAGR as a decimal.

    Raises:
        ValueError: If starting_value <= 0, ending_value < 0, or periods <= 0.

    Notes:
        CAGR is the single constant rate that would grow ``starting_value`` into
        ``ending_value`` over ``periods``:

        $$CAGR = \\left(\\frac{V_n}{V_0}\\right)^{1/n} - 1$$

        Used to normalise revenue growth across unequal time spans before
        applying a growth-based multiple.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.2.

    See Also:
        compound_growth : Project a value forward at a given rate.

    Example:
        >>> result = compound_annual_growth_rate(1_000_000, 2_744_000, 3)
        >>> round(result.value, 4)
        0.4
    """
    if starting_value <= 0:
        raise ValueError("starting_value must be > 0")
    if ending_value < 0:
        raise ValueError("ending_value must be >= 0")
    if periods <= 0:
        raise ValueError("periods must be > 0")

    value = (ending_value / starting_value) ** (1 / periods) - 1

    return ValuationResult(
        value=value,
        method="Compound Annual Growth Rate (CAGR)",
        inputs={"starting_value": starting_value, "ending_value": ending_value, "periods": periods},
        assumptions=["Growth is smooth and compounded annually"],
        chapter="Chapter 2",
        formula_number="2.1",
        steps=[
            {
                "label": "CAGR",
                "value": value,
                "formula": r"CAGR = (V_n / V_0)^{1/n} - 1",
            },
        ],
    )
