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
        value=total_users ** alpha,
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
