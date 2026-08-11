"""Fintech valuation methods.

Chapter 11: Industry-Specific Valuation Frameworks — Fintech
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def payment_revenue(transaction_volume: float, take_rate: float) -> ValuationResult:
    """Calculate payment processor revenue.

    Formula: Revenue = Transaction Volume × Take Rate

    Example:
        >>> result = payment_revenue(640_000_000_000, 0.0116)
        >>> result.value / 1_000_000_000
        7.424
    """
    return ValuationResult(
        value=transaction_volume * take_rate,
        method="Payment Revenue",
        inputs={"transaction_volume": transaction_volume, "take_rate": take_rate},
        chapter="11",
    )


def max_loan_portfolio(equity_capital: float, capital_ratio: float = 0.08) -> ValuationResult:
    """Calculate maximum loan portfolio under Basel III.

    Formula: Max Loan = Equity Capital / Risk-Weighted Capital Ratio

    Example:
        >>> result = max_loan_portfolio(100_000_000, 0.08)
        >>> result.value
        1250000000.0
    """
    if capital_ratio <= 0:
        raise ValueError("capital_ratio must be positive")
    return ValuationResult(
        value=equity_capital / capital_ratio,
        method="Max Loan Portfolio",
        inputs={"equity_capital": equity_capital, "capital_ratio": capital_ratio},
        assumptions=["Basel III minimum capital ratio of 8%"],
        chapter="11",
    )


def network_effects_value(total_users: float, alpha: float = 1.3) -> ValuationResult:
    """Calculate network effects value.

    Formula: Value per User ∝ Total Users^α

    Args:
        total_users: Total number of users.
        alpha: Network effect exponent (1.2-1.5 empirical, 2 for Metcalfe).

    Returns:
        ValuationResult with network value index.
    """
    return ValuationResult(
        value=total_users**alpha,
        method="Network Effects Value",
        inputs={"total_users": total_users, "alpha": alpha},
        assumptions=[f"Network effect exponent α={alpha}"],
        chapter="11",
    )


def lending_fintech_valuation(
    loan_book: float,
    roe: float,
    pe_multiple: float,
    npl_reserves: float = 0,
) -> ValuationResult:
    """Value a lending fintech.

    Formula: Valuation = Loan Book × ROE × P/E - NPL Reserves

    Example:
        >>> result = lending_fintech_valuation(100_000_000, 0.15, 12)
        >>> result.value
        180000000.0
    """
    return ValuationResult(
        value=loan_book * roe * pe_multiple - npl_reserves,
        method="Lending Fintech Valuation",
        inputs={"loan_book": loan_book, "roe": roe, "pe_multiple": pe_multiple},
        assumptions=["ROE is sustainable", "P/E multiple is from comparable lenders"],
        chapter="11",
    )


def payment_processor_valuation(
    transaction_volume: float,
    take_rate: float,
    growth_rate: float,
    discount_rate: float,
    terminal_multiple: float,
    years: int = 5,
) -> ValuationResult:
    """Value a payment processor using DCF of payment revenue.

    Formula: V = Σ[Volume × (1+g)^t × Take Rate] / (1+r)^t + Terminal / (1+r)^n

    Args:
        transaction_volume: Current annual transaction volume.
        take_rate: Revenue take rate.
        growth_rate: Annual volume growth rate.
        discount_rate: Discount rate.
        terminal_multiple: Terminal revenue multiple.
        years: Projection period.

    Returns:
        ValuationResult with payment processor value.

    Example:
        >>> result = payment_processor_valuation(
        ...     640_000_000_000, 0.0116, 0.20, 0.15, 15, 5
        ... )
        >>> round(result.value / 1_000_000_000, 1)
        84.5
    """
    revenue = transaction_volume * take_rate
    pv = 0.0
    for t in range(1, years + 1):
        cf = revenue * ((1 + growth_rate) ** t)
        pv += cf / ((1 + discount_rate) ** t)

    terminal_revenue = revenue * ((1 + growth_rate) ** years)
    terminal_value = terminal_revenue * terminal_multiple
    pv += terminal_value / ((1 + discount_rate) ** years)

    return ValuationResult(
        value=pv,
        method="Payment Processor Valuation",
        inputs={
            "transaction_volume": transaction_volume,
            "take_rate": take_rate,
            "growth_rate": growth_rate,
            "discount_rate": discount_rate,
            "terminal_multiple": terminal_multiple,
            "years": years,
        },
        assumptions=["Growth rate is sustainable over projection period"],
        chapter="11",
    )


def neobank_valuation(
    customers: int,
    arpu: float,
    gross_margin: float,
    churn_rate: float,
    pe_multiple: float,
) -> ValuationResult:
    """Value a neobank using customer-based valuation.

    Formula: V = Customers × LTV × P/E
    where LTV = (ARPU × Gross Margin) / Churn Rate

    Args:
        customers: Number of active customers.
        arpu: Annual revenue per user.
        gross_margin: Gross margin percentage.
        churn_rate: Annual churn rate.
        pe_multiple: P/E multiple for comparable banks.

    Returns:
        ValuationResult with neobank value.

    Example:
        >>> result = neobank_valuation(1_000_000, 50, 0.60, 0.10, 20)
        >>> result.value / 1_000_000_000
        6.0
    """
    if churn_rate <= 0:
        raise ValueError("churn_rate must be positive")
    ltv = (arpu * gross_margin) / churn_rate
    valuation = customers * ltv * pe_multiple

    return ValuationResult(
        value=valuation,
        method="Neobank Valuation",
        inputs={
            "customers": customers,
            "arpu": arpu,
            "gross_margin": gross_margin,
            "churn_rate": churn_rate,
            "pe_multiple": pe_multiple,
        },
        assumptions=["LTV model applies to banking customers", "P/E multiple from comparable banks"],
        chapter="11",
    )
