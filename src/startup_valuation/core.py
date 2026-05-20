"""Core valuation models for pre-revenue startups.

Chapter 3: Core Valuation Models
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def scorecard_valuation(
    average_valuation: float,
    weights: list[float],
    scores: list[float],
) -> ValuationResult:
    """Valuation using the Scorecard Method.

    Formula: V = V_avg × Σ(wᵢ × sᵢ)

    Args:
        average_valuation: Average regional pre-money valuation (V_avg).
        weights: Factor weights (must sum to 1).
        scores: Factor scores (1.0 = average).

    Returns:
        ValuationResult with target valuation.

    Example:
        >>> result = scorecard_valuation(
        ...     1_500_000,
        ...     [0.30, 0.25, 0.15, 0.10, 0.10, 0.05, 0.05],
        ...     [1.25, 1.50, 1.20, 0.75, 1.00, 0.90, 1.00],
        ... )
        >>> result.value
        1800000.0
    """
    if abs(sum(weights) - 1.0) > 0.01:
        raise ValueError(f"weights must sum to 1.0, got {sum(weights)}")
    if len(weights) != len(scores):
        raise ValueError("weights and scores must have the same length")

    weighted_score = sum(w * s for w, s in zip(weights, scores))
    valuation = average_valuation * weighted_score

    return ValuationResult(
        value=valuation,
        method="Scorecard Method",
        inputs={
            "average_valuation": average_valuation,
            "weights": weights,
            "scores": scores,
        },
        assumptions=[
            "Average valuation is from comparable regional deals",
            "Scores are relative to average (1.0 = average)",
            "Weights reflect factor importance for this stage",
        ],
        chapter="3",
    )


def berkus_valuation(
    sound_idea: float = 0,
    prototype: float = 0,
    quality_team: float = 0,
    strategic_relationships: float = 0,
    product_rollout: float = 0,
    max_per_factor: float = 500_000,
) -> ValuationResult:
    """Valuation using the Berkus Method.

    Formula: V = Σ vᵢ, where each vᵢ ≤ $500K
    Maximum: $2.5M (5 factors × $500K)

    Args:
        sound_idea: Value for sound idea ($0-$500K).
        prototype: Value for prototype ($0-$500K).
        quality_team: Value for quality team ($0-$500K).
        strategic_relationships: Value for relationships ($0-$500K).
        product_rollout: Value for product rollout/sales ($0-$500K).
        max_per_factor: Maximum value per factor (default $500K).

    Returns:
        ValuationResult with Berkus valuation.

    Example:
        >>> result = berkus_valuation(500_000, 400_000, 500_000, 500_000, 0)
        >>> result.value
        1900000.0
    """
    factors = [sound_idea, prototype, quality_team, strategic_relationships, product_rollout]

    for i, v in enumerate(factors):
        if v < 0 or v > max_per_factor:
            raise ValueError(f"Factor {i} value {v} outside range [0, {max_per_factor}]")

    valuation = sum(factors)

    return ValuationResult(
        value=valuation,
        method="Berkus Method",
        inputs={
            "sound_idea": sound_idea,
            "prototype": prototype,
            "quality_team": quality_team,
            "strategic_relationships": strategic_relationships,
            "product_rollout": product_rollout,
        },
        assumptions=[
            f"Maximum valuation is ${5 * max_per_factor:,.0f}",
            "Applicable to pre-revenue startups only",
            "Each factor is independently assessed",
        ],
        chapter="3",
    )


def risk_factor_summation(
    base_valuation: float,
    risk_ratings: list[float],
    adjustment_per_unit: float = 250_000,
) -> ValuationResult:
    """Valuation using the Risk Factor Summation Method.

    Formula: V = V_base + Σ(rᵢ × adjustment_per_unit)

    Args:
        base_valuation: Base valuation for comparable companies.
        risk_ratings: Risk factor ratings (-2 to +2 for each of 12 factors).
        adjustment_per_unit: Dollar adjustment per risk unit (default $250K).

    Returns:
        ValuationResult with adjusted valuation.

    Example:
        >>> result = risk_factor_summation(2_000_000, [1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0])
        >>> result.value
        2750000.0
    """
    if len(risk_ratings) != 12:
        raise ValueError(f"Expected 12 risk ratings, got {len(risk_ratings)}")
    if not all(-2 <= r <= 2 for r in risk_ratings):
        raise ValueError("All risk ratings must be between -2 and +2")

    total_adjustment = sum(risk_ratings) * adjustment_per_unit
    valuation = base_valuation + total_adjustment

    return ValuationResult(
        value=valuation,
        method="Risk Factor Summation",
        inputs={
            "base_valuation": base_valuation,
            "risk_ratings": risk_ratings,
            "adjustment_per_unit": adjustment_per_unit,
        },
        assumptions=[
            "Base valuation is from comparable companies",
            "Each risk unit adjusts valuation by $250K",
            "12 risk factors are assessed independently",
        ],
        chapter="3",
    )


def vc_method_post_money(
    terminal_value: float,
    target_return: float,
) -> ValuationResult:
    """Calculate post-money valuation using the VC Method.

    Formula: Post-Money = Terminal Value / Target Return

    Args:
        terminal_value: Expected exit value.
        target_return: Target return multiple (e.g., 10 for 10x).

    Returns:
        ValuationResult with post-money valuation.

    Example:
        >>> result = vc_method_post_money(500_000_000, 10)
        >>> result.value
        50000000.0
    """
    if target_return <= 0:
        raise ValueError("target_return must be positive")

    post_money = terminal_value / target_return

    return ValuationResult(
        value=post_money,
        method="VC Method (Post-Money)",
        inputs={
            "terminal_value": terminal_value,
            "target_return": target_return,
        },
        assumptions=[
            "Terminal value is realistic exit valuation",
            "Target return reflects investor expectations for this stage",
        ],
        chapter="3",
    )


def vc_method_pre_money(
    post_money: float,
    investment: float,
) -> ValuationResult:
    """Calculate pre-money valuation.

    Formula: Pre-Money = Post-Money - Investment

    Args:
        post_money: Post-money valuation.
        investment: Investment amount.

    Returns:
        ValuationResult with pre-money valuation.

    Example:
        >>> result = vc_method_pre_money(8_000_000, 1_500_000)
        >>> result.value
        6500000.0
    """
    pre_money = post_money - investment

    return ValuationResult(
        value=pre_money,
        method="VC Method (Pre-Money)",
        inputs={"post_money": post_money, "investment": investment},
        assumptions=["Investment amount is accurate"],
        chapter="3",
    )


def terminal_value_multiple(
    projected_revenue: float,
    multiple: float,
) -> ValuationResult:
    """Calculate terminal value using a revenue multiple.

    Formula: Terminal Value = Revenue × Multiple

    Args:
        projected_revenue: Projected revenue at exit.
        multiple: Industry revenue multiple.

    Returns:
        ValuationResult with terminal value.

    Example:
        >>> result = terminal_value_multiple(20_000_000, 8)
        >>> result.value
        160000000.0
    """
    tv = projected_revenue * multiple

    return ValuationResult(
        value=tv,
        method="Terminal Value (Multiple)",
        inputs={"projected_revenue": projected_revenue, "multiple": multiple},
        assumptions=["Multiple is from comparable exits", "Revenue projection is achievable"],
        chapter="3",
    )
