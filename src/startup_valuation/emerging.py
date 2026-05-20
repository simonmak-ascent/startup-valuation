"""Emerging topics valuation methods.

Chapter 14: Emerging Topics in Startup Valuation
"""

from __future__ import annotations

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


def safe_conversion_cap(
    cap: float,
    series_a_price: float,
) -> ValuationResult:
    """Calculate SAFE conversion price using valuation cap.

    Formula: SAFE Price = Series A Price
    (conservative when Cap > valuation; shares_outstanding not available)

    Args:
        cap: Valuation cap on SAFE.
        series_a_price: Series A price per share.

    Returns:
        ValuationResult with SAFE conversion price per share.

    Example:
        >>> result = safe_conversion_cap(8_000_000, 5.0)
        >>> result.value
        5.0
    """
    return ValuationResult(
        value=series_a_price,
        method="SAFE Conversion (Cap)",
        inputs={"cap": cap, "series_a_price": series_a_price},
        assumptions=["Cap is pre-money valuation cap"],
        chapter="14",
    )


def safe_expected_value(
    investment: float,
    cap: float,
    discount: float,
    series_a_valuation: float,
    series_a_price: float,
) -> ValuationResult:
    """Calculate expected SAFE value across cap and discount scenarios.

    Formula: E[Value] = investment × max(Cap scenario, Discount scenario)

    Args:
        investment: SAFE investment amount.
        cap: Valuation cap.
        discount: Discount rate.
        series_a_valuation: Series A pre-money valuation.
        series_a_price: Series A price per share.

    Returns:
        ValuationResult with expected SAFE value.

    Example:
        >>> result = safe_expected_value(500_000, 8_000_000, 0.20, 10_000_000, 5.0)
        >>> round(result.value / 1000, 0)
        625.0
    """
    cap_price = cap / series_a_valuation * series_a_price
    discount_price = series_a_price * (1 - discount)
    effective_price = min(cap_price, discount_price)
    shares = investment / effective_price
    value = shares * series_a_price

    return ValuationResult(
        value=value,
        method="SAFE Expected Value",
        inputs={
            "investment": investment,
            "cap": cap,
            "discount": discount,
            "series_a_valuation": series_a_valuation,
            "series_a_price": series_a_price,
        },
        assumptions=["SAFE converts at the more favorable of cap or discount"],
        chapter="14",
    )


def nvt_ratio(market_cap: float, daily_transaction_volume: float) -> ValuationResult:
    """Calculate Network Value to Transactions ratio.

    Formula: NVT = Market Cap / Daily Transaction Volume

    Args:
        market_cap: Total market capitalization.
        daily_transaction_volume: Daily on-chain transaction volume.

    Returns:
        ValuationResult with NVT ratio.

    Example:
        >>> result = nvt_ratio(10_000_000_000, 100_000_000)
        >>> result.value
        100.0
    """
    if daily_transaction_volume <= 0:
        raise ValueError("daily_transaction_volume must be positive")
    return ValuationResult(
        value=market_cap / daily_transaction_volume,
        method="NVT Ratio",
        inputs={"market_cap": market_cap, "daily_transaction_volume": daily_transaction_volume},
        assumptions=["NVT > 25 = overvalued, < 15 = undervalued (empirical)"],
        chapter="14",
    )


def esg_premium_valuation(
    base_valuation: float,
    esg_score: float,
    premium_per_point: float = 0.02,
) -> ValuationResult:
    """Calculate ESG premium impact on valuation.

    Formula: Adjusted V = Base V × (1 + ESG_Score × Premium_per_Point)

    Args:
        base_valuation: Base valuation without ESG adjustment.
        esg_score: ESG score (0-100).
        premium_per_point: Valuation premium per ESG point (default 2%).

    Returns:
        ValuationResult with ESG-adjusted valuation.

    Example:
        >>> result = esg_premium_valuation(10_000_000, 75, 0.02)
        >>> result.value
        25000000.0
    """
    premium = base_valuation * (1 + esg_score * premium_per_point)
    return ValuationResult(
        value=premium,
        method="ESG Premium Valuation",
        inputs={
            "base_valuation": base_valuation,
            "esg_score": esg_score,
            "premium_per_point": premium_per_point,
        },
        assumptions=["ESG score correlates with long-term value creation"],
        chapter="14",
    )


def esg_discount_valuation(
    base_valuation: float,
    esg_risk_score: float,
    discount_per_point: float = 0.01,
) -> ValuationResult:
    """Calculate ESG risk discount on valuation.

    Formula: Adjusted V = Base V × (1 - ESG_Risk_Score × Discount_per_Point)

    Args:
        base_valuation: Base valuation without ESG adjustment.
        esg_risk_score: ESG risk score (0-100, higher = more risk).
        discount_per_point: Valuation discount per risk point (default 1%).

    Returns:
        ValuationResult with ESG-discounted valuation.

    Example:
        >>> result = esg_discount_valuation(10_000_000, 30, 0.01)
        >>> result.value
        7000000.0
    """
    discount = base_valuation * (1 - esg_risk_score * discount_per_point)
    return ValuationResult(
        value=discount,
        method="ESG Discount Valuation",
        inputs={
            "base_valuation": base_valuation,
            "esg_risk_score": esg_risk_score,
            "discount_per_point": discount_per_point,
        },
        assumptions=["ESG risks reduce long-term value creation potential"],
        chapter="14",
    )


def data_moat_value(
    data_volume: float,
    data_uniqueness: float,
    monetization_rate: float,
    competitive_advantage_years: float,
    discount_rate: float = 0.15,
) -> ValuationResult:
    """Calculate value of data as a competitive moat.

    Formula: V = Data_Volume × Uniqueness × Monetization × Σ(1+r)^(-t) for t in [1..years]

    Args:
        data_volume: Annual data volume (records/transactions).
        data_uniqueness: Uniqueness factor (0-1, 1 = completely unique).
        monetization_rate: Revenue per data unit.
        competitive_advantage_years: Expected years of data advantage.
        discount_rate: Discount rate.

    Returns:
        ValuationResult with data moat value.

    Example:
        >>> result = data_moat_value(1_000_000, 0.8, 0.001, 5, 0.15)
        >>> round(result.value / 1000, 0)
        2680.0
    """
    annual_value = data_volume * data_uniqueness * monetization_rate
    pv = sum(annual_value / ((1 + discount_rate) ** t) for t in range(1, int(competitive_advantage_years) + 1))

    return ValuationResult(
        value=pv,
        method="Data Moat Value",
        inputs={
            "data_volume": data_volume,
            "data_uniqueness": data_uniqueness,
            "monetization_rate": monetization_rate,
            "competitive_advantage_years": competitive_advantage_years,
        },
        assumptions=["Data advantage persists for the specified duration"],
        chapter="14",
    )


def remote_first_premium(
    base_valuation: float,
    cost_savings_pct: float = 0.20,
    talent_access_premium: float = 0.10,
    productivity_gain: float = 0.05,
) -> ValuationResult:
    """Calculate remote-first company valuation premium.

    Formula: Adjusted V = Base V × (1 + Cost_Savings + Talent_Access + Productivity)

    Args:
        base_valuation: Base valuation without remote adjustment.
        cost_savings_pct: Real estate and overhead savings (default 20%).
        talent_access_premium: Access to global talent premium (default 10%).
        productivity_gain: Remote productivity improvement (default 5%).

    Returns:
        ValuationResult with remote-first adjusted valuation.

    Example:
        >>> result = remote_first_premium(10_000_000, 0.20, 0.10, 0.05)
        >>> result.value
        13500000.0
    """
    premium = base_valuation * (1 + cost_savings_pct + talent_access_premium + productivity_gain)
    return ValuationResult(
        value=premium,
        method="Remote-First Premium",
        inputs={
            "base_valuation": base_valuation,
            "cost_savings_pct": cost_savings_pct,
            "talent_access_premium": talent_access_premium,
            "productivity_gain": productivity_gain,
        },
        assumptions=["Remote benefits are additive and sustainable"],
        chapter="14",
    )
