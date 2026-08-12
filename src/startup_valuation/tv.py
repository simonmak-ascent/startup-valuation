"""Time value of money calculations.

Chapter 2: Mathematical Foundations — Time Value of Money
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def present_value(future_value: float, rate: float, periods: float) -> ValuationResult:
    """Calculate present value of a single future cash flow.

    Formula: PV = C / (1 + r)^t

    Args:
        future_value: Future cash flow (C).
        rate: Discount rate (r).
        periods: Number of periods (t).

    Returns:
        ValuationResult with present value.

    Raises:
        ValueError: If rate < -1.

    Notes:
        Present value discounts a single future cash flow to today's dollars:

        $$PV = \\frac{C}{(1 + r)^t}$$

        Foundation of all DCF and NPV calculations. Higher discount rates
        or longer time horizons reduce present value.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.2.

    See Also:
        net_present_value : Sum of discounted cash flows.
        annuity_present_value : Perpetual or fixed-period payments.

    Example:
        >>> result = present_value(11000, 0.08, 1)
        >>> round(result.value, 2)
        10185.19
    """
    if rate < -1:
        raise ValueError("rate must be >= -1")

    pv = future_value / ((1 + rate) ** periods)

    return ValuationResult(
        value=pv,
        method="Present Value",
        inputs={"future_value": future_value, "rate": rate, "periods": periods},
        assumptions=["Discount rate is constant over the period"],
        chapter="2",
        formula_number="2.2",
    )


def net_present_value(
    cash_flows: list[float],
    rate: float,
) -> ValuationResult:
    """Calculate net present value of a series of cash flows.

    Formula: NPV = Σ Cₜ / (1 + r)^t

    Args:
        cash_flows: Cash flows at each period (C₀, C₁, ..., Cₜ).
        rate: Discount rate (r).

    Returns:
        ValuationResult with NPV.

    Raises:
        ValueError: If rate < -1.

    Notes:
        Net present value sums all discounted cash flows:

        $$NPV = \\sum_{t=0}^{n} \\frac{CF_t}{(1 + r)^t}$$

        The first element is typically negative (initial investment).
        NPV > 0 indicates value creation. Used in DCF valuation
        and capital budgeting.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.3.

    See Also:
        present_value : Single cash flow discounting.
        dcf_valuation : Full DCF with terminal value.

    Example:
        >>> result = net_present_value([-100000, 30000, 40000, 50000], 0.10)
        >>> round(result.value, 0)
        -2103.0
    """
    if rate < -1:
        raise ValueError("rate must be >= -1")

    npv = sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cash_flows))

    return ValuationResult(
        value=npv,
        method="Net Present Value",
        inputs={"cash_flows": cash_flows, "rate": rate},
        assumptions=["Discount rate is constant across all periods"],
        chapter="2",
        formula_number="2.3",
    )


def annuity_present_value(
    payment: float,
    rate: float,
    periods: int,
) -> ValuationResult:
    """Calculate present value of an annuity.

    Formula: PV = C × [(1 - (1 + r)^(-n)) / r]

    Args:
        payment: Periodic payment (C).
        rate: Discount rate per period (r).
        periods: Number of periods (n).

    Returns:
        ValuationResult with present value.

    Notes:
        Present value of equal payments at end of each period:

        $$PV = C \\times \\left[\\frac{1 - (1 + r)^{-n}}{r}\\right]$$

        When r = 0, PV = C × n. Used for valuing fixed-payment
        streams like lease payments or subscription revenue.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.4.

    See Also:
        present_value : Single cash flow. net_present_value : Variable flows.

    Example:
        >>> result = annuity_present_value(50000, 0.10, 4)
        >>> round(result.value, 0)
        158495.0
    """
    if rate == 0:
        pv = payment * periods
    else:
        pv = payment * (1 - (1 + rate) ** (-periods)) / rate

    return ValuationResult(
        value=pv,
        method="Annuity Present Value",
        inputs={"payment": payment, "rate": rate, "periods": periods},
        assumptions=["Payments are equal and occur at end of each period"],
        chapter="2",
        formula_number="2.4",
    )
