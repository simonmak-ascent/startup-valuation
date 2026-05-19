"""Emerging topics valuation methods.

Chapter 14: Emerging Topics in Startup Valuation
"""

from __future__ import annotations

import math

from startup_valuation.types import ValuationResult


def safe_conversion_discount(series_a_price: float, discount: float) -> ValuationResult:
    """Calculate SAFE conversion price using discount.

    Formula: SAFE Price = Series A Price × (1 - Discount)

    Example:
        >>> result = safe_conversion_discount(5.0, 0.20)
        >>> result.value
        4.0
    """
    return ValuationResult(
        value=series_a_price * (1 - discount),
        method="SAFE Conversion (Discount)",
        inputs={"series_a_price": series_a_price, "discount": discount},
        chapter="14",
    )


def equation_of_exchange(
    transaction_volume: float,
    price_per_transaction: float,
    token_velocity: float,
    token_supply: float,
) -> ValuationResult:
    """Calculate token value using equation of exchange.

    Formula: Token Value = (Transaction Volume × Price per Transaction) / (Velocity × Supply)

    Example:
        >>> result = equation_of_exchange(10_000_000_000, 1, 10, 100_000_000)
        >>> result.value
        10.0
    """
    if token_velocity <= 0 or token_supply <= 0:
        raise ValueError("velocity and supply must be positive")
    return ValuationResult(
        value=(transaction_volume * price_per_transaction) / (token_velocity * token_supply),
        method="Equation of Exchange (MV=PQ)",
        inputs={
            "transaction_volume": transaction_volume,
            "price_per_transaction": price_per_transaction,
            "token_velocity": token_velocity,
            "token_supply": token_supply,
        },
        chapter="14",
    )


def protocol_value(tvl: float, multiple: float) -> ValuationResult:
    """Calculate protocol value from TVL.

    Formula: Protocol Value = TVL × Multiple
    """
    return ValuationResult(
        value=tvl * multiple,
        method="Protocol Value",
        inputs={"tvl": tvl, "multiple": multiple},
        assumptions=["Multiple: established 0.3-0.5x, growing 0.5-1.0x, new 0.1-0.3x"],
        chapter="14",
    )


def esg_adjusted_discount_rate(
    base_rate: float,
    esg_risk_premium: float = 0,
    esg_opportunity_discount: float = 0,
) -> ValuationResult:
    """Calculate ESG-adjusted discount rate.

    Formula: r_ESG = r_base + ESG Risk Premium - ESG Opportunity Discount

    Example:
        >>> result = esg_adjusted_discount_rate(0.15, 0.02, 0.01)
        >>> result.value
        0.16
    """
    return ValuationResult(
        value=base_rate + esg_risk_premium - esg_opportunity_discount,
        method="ESG-Adjusted Discount Rate",
        inputs={
            "base_rate": base_rate,
            "esg_risk_premium": esg_risk_premium,
            "esg_opportunity_discount": esg_opportunity_discount,
        },
        chapter="14",
    )


def metcalfes_law(n: float, k: float = 1.0) -> ValuationResult:
    """Calculate network value using Metcalfe's Law.

    Formula: V = k × n²

    Example:
        >>> result = metcalfes_law(100_000)
        >>> result.value
        10000000000.0
    """
    return ValuationResult(
        value=k * n**2,
        method="Metcalfe's Law",
        inputs={"n": n, "k": k},
        assumptions=["Value grows with square of users"],
        chapter="14",
    )


def modified_metcalfes(n: float, alpha: float = 1.3, k: float = 1.0) -> ValuationResult:
    """Calculate network value using modified Metcalfe's Law.

    Formula: V = k × n^α

    Args:
        n: Number of users.
        alpha: Network effect exponent (1.2-1.5 empirical).
        k: Value constant.

    Returns:
        ValuationResult with network value.
    """
    return ValuationResult(
        value=k * n**alpha,
        method="Modified Metcalfe's Law",
        inputs={"n": n, "alpha": alpha, "k": k},
        chapter="14",
    )


def network_density_valuation(
    users: float,
    connections_per_user: float,
    value_per_connection: float,
) -> ValuationResult:
    """Calculate network value from density.

    Formula: Value = Users × Connections per User × Value per Connection

    Example:
        >>> result = network_density_valuation(10_000_000, 100, 1)
        >>> result.value / 1_000_000_000
        1.0
    """
    return ValuationResult(
        value=users * connections_per_user * value_per_connection,
        method="Network Density Valuation",
        inputs={
            "users": users,
            "connections_per_user": connections_per_user,
            "value_per_connection": value_per_connection,
        },
        chapter="14",
    )


def remote_cost_savings_npv(annual_savings: float, discount_rate: float) -> ValuationResult:
    """Calculate NPV of remote-first cost savings (perpetuity).

    Formula: NPV = Annual Savings / r

    Example:
        >>> result = remote_cost_savings_npv(1_200_000, 0.10)
        >>> result.value
        12000000.0
    """
    if discount_rate <= 0:
        raise ValueError("discount_rate must be positive")
    return ValuationResult(
        value=annual_savings / discount_rate,
        method="Remote Cost Savings NPV",
        inputs={"annual_savings": annual_savings, "discount_rate": discount_rate},
        chapter="14",
    )
