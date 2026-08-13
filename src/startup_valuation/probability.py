"""Probability theory calculations for valuation under uncertainty.

Chapter 2: Mathematical Foundations — Probability Theory
"""

from __future__ import annotations

import math
from collections.abc import Callable

from scipy import integrate, stats

from startup_valuation.types import ValuationResult


def expected_value_discrete(
    outcomes: list[float],
    probabilities: list[float],
) -> ValuationResult:
    """Calculate expected value for a discrete random variable.

    Formula: E[X] = Σ xᵢ · P(X = xᵢ)

    Args:
        outcomes: Possible outcome values.
        probabilities: Probability of each outcome.

    Returns:
        ValuationResult with expected value.

    Raises:
        ValueError: If outcomes and probabilities differ in length.

    Notes:
        $$E[X] = \\sum_{i=1}^{n} x_i \\cdot P(X = x_i)$$

        Foundation of expected value analysis. Assumes probabilities
        are mutually exclusive and exhaustive (should sum to ~1.0).
        Used in scenario analysis, decision trees, and PWERM.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.1.

    See Also:
        expected_value_continuous : For continuous distributions.
        scenario_analysis : For bull/base/bear scenarios.
    """
    if len(outcomes) != len(probabilities):
        raise ValueError("outcomes and probabilities must have the same length")

    ev = sum(o * p for o, p in zip(outcomes, probabilities))

    return ValuationResult(
        value=ev,
        steps=[
            {
                "label": "Expected Value (Discrete)",
                "value": ev,
                "formula": r"E[X] = \sum x_i p_i",
            },
        ],
        method="Expected Value (Discrete)",
        inputs={"outcomes": outcomes, "probabilities": probabilities},
        assumptions=["Probabilities sum to 1.0", "Outcomes are mutually exclusive"],
        chapter="2",
        formula_number="2.1",
    )


def joint_probability(probabilities: list[float]) -> ValuationResult:
    """Calculate joint probability of sequential independent events.

    Formula: P(total) = Π Pᵢ

    Args:
        probabilities: Independent event probabilities.

    Notes:
        $$P(\\text{total}) = \\prod_{i=1}^{n} P_i$$

        For startup valuation: probability of passing multiple
        milestones (e.g., Series A AND Series B AND exit).
        Assumes independence between events. Each Pᵢ ∈ [0,1].

    References:
        Startup Valuation textbook, Chapter 2, Section 2.1.

    See Also:
        expected_value_discrete : Weighted by probabilities.
    """
    jp = math.prod(probabilities)
    return ValuationResult(
        value=jp,
        steps=[
            {
                "label": "Joint Probability",
                "value": jp,
                "formula": r"P(A \cap B) = \prod p_i",
            },
        ],
        method="Joint Probability",
        inputs={"probabilities": probabilities},
        assumptions=["Events are independent", "Probabilities are between 0 and 1"],
        chapter="2",
        formula_number="2.2",
    )


def probability_weighted_value(
    outcomes: list[float],
    probabilities: list[float],
) -> ValuationResult:
    """Probability-weighted sum of multiple scenarios.

    Formula: PW = Σ pᵢ × vᵢ

    Notes:
        Direct application of expected value to valuation.
        Returns the weighted sum — same formula as expected_value_discrete
        but named for valuation context.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.1.
    """
    if len(outcomes) != len(probabilities):
        raise ValueError("outcomes and probabilities must have the same length")
    return ValuationResult(
        value=sum(o * p for o, p in zip(outcomes, probabilities)),
        steps=[
            {
                "label": "Probability-Weighted Value",
                "value": sum(o * p for o, p in zip(outcomes, probabilities)),
                "formula": r"V = \sum v_i p_i",
            },
        ],
        method="Probability-Weighted Value",
        inputs={"outcomes": outcomes, "probabilities": probabilities},
        assumptions=["Probabilities sum to 1.0"],
        chapter="2",
        formula_number="2.3",
    )


def portfolio_expected_return(
    weights: list[float],
    returns: list[float],
) -> ValuationResult:
    """Calculate expected portfolio return from individual asset returns.

    Formula: E[R_p] = Σ wᵢ × E[Rᵢ]

    Args:
        weights: Portfolio allocation weights.
        returns: Expected return for each asset.

    Notes:
        $$E[R_p] = \\sum_{i=1}^{n} w_i \\cdot E[R_i]$$

        Weighted average of expected returns. Used in portfolio
        construction and fund-level valuation analysis.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.1.
    """
    if abs(sum(weights) - 1.0) > 0.01:
        raise ValueError("weights must sum to 1.0")
    return ValuationResult(
        value=sum(w * r for w, r in zip(weights, returns)),
        steps=[
            {
                "label": "Portfolio Expected Return",
                "value": sum(w * r for w, r in zip(weights, returns)),
                "formula": r"E[R_p] = \sum w_i r_i",
            },
        ],
        method="Portfolio Expected Return",
        inputs={"weights": weights, "returns": returns},
        assumptions=["Weights sum to 1.0", "Expected returns are forward-looking estimates"],
        chapter="2",
        formula_number="2.4",
    )


def poisson_probability(lambda_: float, k: int) -> ValuationResult:
    """Calculate Poisson probability P(X = k) for event count k.

    Formula: P(X = k) = (λ^k · e^(-λ)) / k!

    Args:
        lambda_: Expected number of events (λ).
        k: Actual number of events.

    Notes:
        $$P(X = k) = \\frac{\\lambda^k e^{-\\lambda}}{k!}$$

        Uses scipy.stats.poisson.pmf for numerical stability.
        Models count of rare events in fixed interval: patent
        filings, FDA approvals, customer arrivals.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.1.

    See Also:
        expected_value_continuous : For continuous distributions.
    """
    return ValuationResult(
        value=float(stats.poisson.pmf(k, lambda_)),
        steps=[
            {
                "label": "Poisson Probability",
                "value": float(stats.poisson.pmf(k, lambda_)),
                "formula": r"P(k) = \frac{\lambda^k e^{-\lambda}}{k!}",
            },
        ],
        method="Poisson Probability",
        inputs={"lambda": lambda_, "k": k},
        assumptions=["Events occur independently", "Constant rate λ"],
        chapter="2",
        formula_number="2.5",
    )


def expected_value_continuous(
    f: Callable[[float], float],
    a: float,
    b: float,
    tol: float = 1.49e-8,
) -> ValuationResult:
    """Calculate expected value of a continuous random variable.

    Formula: E[X] = ∫ x · f(x) dx over [a, b]

    Args:
        f: Probability density function f(x).
        a: Lower bound.
        b: Upper bound.
        tol: Integration tolerance.

    Notes:
        $$E[X] = \\int_a^b x \\cdot f(x) \\,dx$$

        Uses scipy.integrate.quad for adaptive numerical integration.
        Tolerances: 1.49e-8 (default, ~machine epsilon).
        Used when closed-form expectation is not available.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.1.

    See Also:
        expected_value_discrete : For discrete distributions.
    """
    val, _ = integrate.quad(lambda x: x * f(x), a, b, epsabs=tol)

    return ValuationResult(
        value=val,
        steps=[
            {
                "label": "Expected Value (Continuous)",
                "value": val,
                "formula": r"E[X] = \int_a^b x f(x) dx",
            },
        ],
        method="Expected Value (Continuous)",
        inputs={"a": a, "b": b, "tol": tol},
        assumptions=["f(x) is integrable over [a, b]", "f(x) ≥ 0 over domain"],
        chapter="2",
        formula_number="2.6",
    )
