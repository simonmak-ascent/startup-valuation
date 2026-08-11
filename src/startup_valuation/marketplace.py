"""Marketplace valuation methods.

Chapter 11: Industry-Specific Valuation Frameworks — Marketplaces
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def gmv(transaction_values: list[float]) -> ValuationResult:
    """Calculate Gross Merchandise Value.

    Formula: GMV = Σ Transaction Valueᵢ
    """
    return ValuationResult(
        value=sum(transaction_values),
        method="GMV",
        inputs={"transaction_count": len(transaction_values)},
        chapter="11",
    )


def take_rate(revenue: float, gmv: float) -> ValuationResult:
    """Calculate marketplace take rate.

    Formula: Take Rate = Revenue / GMV

    Example:
        >>> result = take_rate(2_900_000_000, 24_700_000_000)
        >>> round(result.value, 4)
        0.1174
    """
    if gmv <= 0:
        raise ValueError("gmv must be positive")
    return ValuationResult(
        value=revenue / gmv,
        method="Take Rate",
        inputs={"revenue": revenue, "gmv": gmv},
        chapter="11",
    )


def liquidity(successful_transactions: int, total_attempts: int) -> ValuationResult:
    """Calculate marketplace liquidity.

    Formula: Liquidity = Successful Transactions / Total Attempts
    """
    if total_attempts <= 0:
        raise ValueError("total_attempts must be positive")
    return ValuationResult(
        value=successful_transactions / total_attempts,
        method="Liquidity",
        inputs={"successful_transactions": successful_transactions, "total_attempts": total_attempts},
        chapter="11",
    )


def gmv_multiple_valuation(gmv: float, multiple: float) -> ValuationResult:
    """Value a marketplace using GMV multiple.

    Formula: Valuation = GMV × Multiple

    Example:
        >>> result = gmv_multiple_valuation(24_700_000_000, 2.4)
        >>> result.value / 1_000_000_000
        59.28
    """
    return ValuationResult(
        value=gmv * multiple,
        method="GMV Multiple Valuation",
        inputs={"gmv": gmv, "multiple": multiple},
        assumptions=["Multiple depends on marketplace maturity and growth"],
        chapter="11",
    )


def network_value(active_users: float, k: float = 1.0, alpha: float = 1.3) -> ValuationResult:
    """Calculate network value using modified Metcalfe's Law.

    Formula: Valuation = k × Active Users^α

    Args:
        active_users: Number of active users.
        k: Value per connection constant.
        alpha: Network effect exponent (1.2-1.5 empirical).

    Returns:
        ValuationResult with network value.
    """
    return ValuationResult(
        value=k * (active_users**alpha),
        method="Network Value",
        inputs={"active_users": active_users, "k": k, "alpha": alpha},
        assumptions=[f"Network effect exponent α={alpha}"],
        chapter="11",
    )


def buyer_retention(
    buyers_period_1: int,
    buyers_repeat: int,
) -> ValuationResult:
    """Calculate marketplace buyer retention rate.

    Formula: Buyer Retention = Repeat Buyers / Buyers in Period 1

    Args:
        buyers_period_1: Number of buyers in period 1.
        buyers_repeat: Number of buyers who returned in period 2.

    Returns:
        ValuationResult with buyer retention rate.

    Example:
        >>> result = buyer_retention(10000, 3500)
        >>> result.value
        0.35
    """
    if buyers_period_1 <= 0:
        raise ValueError("buyers_period_1 must be positive")
    return ValuationResult(
        value=buyers_repeat / buyers_period_1,
        method="Buyer Retention",
        inputs={"buyers_period_1": buyers_period_1, "buyers_repeat": buyers_repeat},
        assumptions=["Period 1 and Period 2 are comparable time windows"],
        chapter="11",
    )


def network_density(
    active_buyers: int,
    active_sellers: int,
    total_users: int,
) -> ValuationResult:
    """Calculate marketplace network density.

    Formula: Density = Actual Connections / Potential Connections
    where Actual = buyers × sellers, Potential = total × (total - 1) / 2

    Args:
        active_buyers: Number of active buyers.
        active_sellers: Number of active sellers.
        total_users: Total number of users.

    Returns:
        ValuationResult with network density ratio.

    Example:
        >>> result = network_density(5000, 3000, 10000)
        >>> round(result.value, 6)
        0.0003
    """
    if total_users <= 1:
        raise ValueError("total_users must be greater than 1")
    actual = active_buyers * active_sellers
    potential = total_users * (total_users - 1) / 2
    return ValuationResult(
        value=actual / potential,
        method="Network Density",
        inputs={
            "active_buyers": active_buyers,
            "active_sellers": active_sellers,
            "total_users": total_users,
        },
        assumptions=["Network density measures marketplace liquidity potential"],
        chapter="11",
    )
