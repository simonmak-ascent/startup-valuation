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

    Raises:
        ValueError: If weights don't sum to 1.0 or weights/scores lengths differ.

    Notes:
        The Scorecard Method adjusts the average regional pre-money valuation
        by a weighted sum of factor scores. Each factor (team, product, market,
        competition, marketing, funding need, other) is scored relative to average
        (1.0 = average). The formula is:

        $$V = V_{avg} \\times \\sum_{i=1}^{n} w_i \\times s_i$$

        where $$\\sum w_i = 1$$ and $$s_i > 0$$.

        Assumptions:
        - Scores are relative to comparable regional startups (1.0 = average)
        - Factors are additively independent (no interaction effects)
        - Linear scaling applies (no diminishing returns)
        - Weights reflect factor importance at the startup's current stage

    References:
        Startup Valuation textbook, Chapter 3, Section 3.1 (Scorecard Method).
        Bill Payne's factor framework (7 standard factors).

    See Also:
        berkus_valuation : Alternative pre-revenue method using milestone values.
        risk_factor_summation : Risk-based adjustment of baseline valuation.
        Theory: https://github.com/simonplmak-cloud/startup-valuation/wiki/Core-Methods

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
        formula_number="3.1",
        steps=[
            {
                "label": "Weighted score (Σ wᵢ × sᵢ)",
                "value": weighted_score,
                "formula": "\\sum_{i=1}^{n} w_i \\times s_i",
            },
            {
                "label": "Valuation (V_avg × weighted score)",
                "value": valuation,
                "formula": "V = V_{avg} \\times \\sum_{i=1}^{n} w_i \\times s_i",
            },
        ],
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

    Raises:
        ValueError: If any factor value is outside [0, max_per_factor].

    Notes:
        The Berkus Method assigns dollar values to five key risk-reduction
        milestones. Each milestone can contribute up to $500K (default),
        with a maximum valuation of $2.5M:

        $$V = \\sum_{i=1}^{5} \\text{Value}_i$$

        where $$0 \\leq \\text{Value}_i \\leq \\text{max\\_per\\_factor}$$.

        Factors: Sound Idea, Prototype, Quality Management Team,
        Strategic Relationships, Product Rollout/Sales.

        Assumptions:
        - Applicable to pre-revenue startups only
        - Maximum per-factor value is $500K (adjustable)
        - Each factor is independently assessed
        - Total valuation is additive (no interactions)

    References:
        Startup Valuation textbook, Chapter 3, Section 3.2 (Berkus Method).
        Dave Berkus, "The Berkus Method: Valuing an Early Stage Startup."

    See Also:
        scorecard_valuation : Factor-weighted adjustment of average valuation.
        Theory: https://github.com/simonplmak-cloud/startup-valuation/wiki/Core-Methods

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
        formula_number="3.2",
        steps=[
            {
                "label": "Total milestone value (Σ vᵢ)",
                "value": valuation,
                "formula": "V = \\sum_{i=1}^{5} \\text{Value}_i",
            },
        ],
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

    Raises:
        ValueError: If risk_ratings length != 12 or ratings outside [-2, +2].

    Notes:
        The Risk Factor Summation Method starts with a baseline valuation
        and adjusts up or down for each of 12 risk factors. Each risk unit
        adjusts the valuation by $250K (default):

        $$V = V_{base} + \\sum_{i=1}^{12} r_i \\times \\text{adjustment\\_per\\_unit}$$

        where $$-2 \\leq r_i \\leq 2$$.

        The 12 risk factors are: Management, Stage of Business,
        Legislation/Political Risk, Manufacturing Risk, Sales/Marketing Risk,
        Funding/Capital Raising Risk, Competition Risk, Technology Risk,
        Litigation Risk, International Risk, Reputation Risk,
        Exit Value Risk.

    References:
        Startup Valuation textbook, Chapter 3, Section 3.3
        (Risk Factor Summation Method).

    See Also:
        scorecard_valuation : Weighted-factor approach to valuation.
        Theory: https://github.com/simonplmak-cloud/startup-valuation/wiki/Core-Methods

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
        formula_number="3.3",
        steps=[
            {
                "label": "Total risk adjustment (Σ rᵢ × unit)",
                "value": total_adjustment,
                "formula": "\\sum_{i=1}^{12} r_i \\times \\text{adjustment\\_per\\_unit}",
            },
            {
                "label": "Adjusted valuation",
                "value": valuation,
                "formula": "V = V_{base} + \\sum_{i=1}^{12} r_i \\times \\text{adjustment\\_per\\_unit}",
            },
        ],
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

    Raises:
        ValueError: If target_return is not positive.

    Notes:
        The Venture Capital Method works backward from an expected exit
        value to determine today's post-money valuation:

        $$V_{post} = \\frac{\\text{Terminal Value}}{\\text{Target Return}}$$

        A target return of 10x means the investor expects to 10x their
        investment by exit. This method assumes a single liquidity event
        at a known future date.

    References:
        Startup Valuation textbook, Chapter 3, Section 3.4 (VC Method).

    See Also:
        vc_method_pre_money : Subtract investment to get pre-money value.
        terminal_value_multiple : Estimate terminal value from revenue.
        Theory: https://github.com/simonplmak-cloud/startup-valuation/wiki/Core-Methods

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
        formula_number="3.4",
        steps=[
            {
                "label": "Post-money valuation (TV ÷ target return)",
                "value": post_money,
                "formula": "V_{post} = \\frac{\\text{Terminal Value}}{\\text{Target Return}}",
            },
        ],
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

    Notes:
        Pre-money valuation is simply post-money minus the investment amount:

        $$V_{pre} = V_{post} - \\text{Investment}$$

        This is the valuation before new capital is injected.

    References:
        Startup Valuation textbook, Chapter 3, Section 3.4 (VC Method).

    See Also:
        vc_method_post_money : Calculate post-money from terminal value.
        Theory: https://github.com/simonplmak-cloud/startup-valuation/wiki/Core-Methods

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
        formula_number="3.4",
        steps=[
            {
                "label": "Pre-money valuation (post-money − investment)",
                "value": pre_money,
                "formula": "V_{pre} = V_{post} - \\text{Investment}",
            },
        ],
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

    Notes:
        Terminal value using a revenue multiple at exit:

        $$\\text{TV} = \\text{Revenue} \\times \\text{Multiple}$$

        Multiples vary by industry (3-10x for SaaS, 1-3x for services).
        Used as input to the VC Method for discounting back to present value.

    References:
        Startup Valuation textbook, Chapter 3, Section 3.4 (VC Method).

    See Also:
        vc_method_post_money : Discount terminal value to post-money.
        Theory: https://github.com/simonplmak-cloud/startup-valuation/wiki/Core-Methods

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
        formula_number="3.4",
        steps=[
            {
                "label": "Terminal value (revenue × multiple)",
                "value": tv,
                "formula": "\\text{TV} = \\text{Revenue} \\times \\text{Multiple}",
            },
        ],
    )
