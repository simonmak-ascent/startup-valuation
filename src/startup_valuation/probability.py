"""Probability theory calculations for valuation under uncertainty.

Chapter 2: Mathematical Foundations — Probability Theory
"""

from __future__ import annotations

import math

from scipy import integrate, stats as scipy_stats

from startup_valuation.types import ValuationResult


def expected_value_discrete(
    outcomes: list[float],
    probabilities: list[float],
) -> ValuationResult:
    """Calculate expected value for a discrete random variable.

    Formula: E[X] = Σ xᵢ × P(X = xᵢ)

    Args:
        outcomes: Possible outcome values (xᵢ).
        probabilities: Probability of each outcome P(X = xᵢ).

    Returns:
        ValuationResult with expected value.

    Example:
        >>> result = expected_value_discrete([1, 0], [0.3, 0.7])
        >>> result.value
        0.3
    """
    if len(outcomes) != len(probabilities):
        raise ValueError("outcomes and probabilities must have the same length")

    ev = sum(o * p for o, p in zip(outcomes, probabilities))

    return ValuationResult(
        value=ev,
        method="Expected Value (Discrete)",
        inputs={"outcomes": outcomes, "probabilities": probabilities},
        assumptions=["Outcomes and probabilities are exhaustive (sum to 1)"],
        chapter="2",
    )


def joint_probability(probabilities: list[float]) -> ValuationResult:
    """Calculate joint probability of sequential independent events.

    Formula: P(total) = Π Pᵢ

    Args:
        probabilities: Probability of each sequential event.

    Returns:
        ValuationResult with joint probability.

    Example:
        >>> result = joint_probability([0.90, 0.70, 0.60, 0.85])
        >>> round(result.value, 4)
        0.3213
    """
    if not probabilities:
        raise ValueError("probabilities list cannot be empty")
    if not all(0 <= p <= 1 for p in probabilities):
        raise ValueError("all probabilities must be between 0 and 1")

    joint = math.prod(probabilities)

    return ValuationResult(
        value=joint,
        method="Joint Probability",
        inputs={"probabilities": probabilities},
        assumptions=["Events are independent"],
        chapter="2",
    )


def probability_weighted_value(
    probabilities: list[float],
    values: list[float],
) -> ValuationResult:
    """Calculate probability-weighted expected value.

    Formula: E[V] = Σ pᵢ × Vᵢ

    Args:
        probabilities: Probability of each scenario.
        values: Value in each scenario.

    Returns:
        ValuationResult with expected value.

    Example:
        >>> result = probability_weighted_value([0.20, 0.60, 0.20], [10_000_000, 5_000_000, 1_000_000])
        >>> result.value
        5200000.0
    """
    if len(probabilities) != len(values):
        raise ValueError("probabilities and values must have the same length")

    ev = sum(p * v for p, v in zip(probabilities, values))

    return ValuationResult(
        value=ev,
        method="Probability-Weighted Expected Value",
        inputs={"probabilities": probabilities, "values": values},
        assumptions=["Scenarios are mutually exclusive and exhaustive"],
        chapter="2",
    )


def portfolio_expected_return(
    probabilities: list[float],
    returns: list[float],
) -> ValuationResult:
    """Calculate expected return of a VC portfolio.

    Formula: E[R] = Σ pᵢ × Rᵢ

    Args:
        probabilities: Probability of each return outcome.
        returns: Return multiple for each outcome.

    Returns:
        ValuationResult with expected return.

    Example:
        >>> result = portfolio_expected_return([0.20, 0.30, 0.20, 0.30], [10, 2, 1, 0])
        >>> result.value
        2.8
    """
    if len(probabilities) != len(returns):
        raise ValueError("probabilities and returns must have the same length")

    er = sum(p * r for p, r in zip(probabilities, returns))

    return ValuationResult(
        value=er,
        method="Portfolio Expected Return",
        inputs={"probabilities": probabilities, "returns": returns},
        assumptions=["Return outcomes are mutually exclusive"],
        chapter="2",
    )


def poisson_probability(lambda_: float, k: int) -> ValuationResult:
    """Calculate Poisson probability P(X = k).

    Formula: P(X = k) = e^(-λ) × λ^k / k!

    Args:
        lambda_: Mean rate (λ).
        k: Target count.

    Returns:
        ValuationResult with probability.

    Example:
        >>> result = poisson_probability(500, 450)
        >>> round(result.value, 3)
        0.011
    """
    if lambda_ <= 0:
        raise ValueError("lambda must be positive")
    if k < 0:
        raise ValueError("k must be non-negative")

    if k > 170:  # factorial overflows float beyond 170
        prob = scipy_stats.poisson.pmf(k, lambda_)
    else:
        prob = math.exp(-lambda_) * (lambda_ ** k) / math.factorial(k)

    return ValuationResult(
        value=prob,
        method="Poisson Probability",
        inputs={"lambda": lambda_, "k": k},
        assumptions=["Events occur independently at constant average rate"],
        chapter="2",
    )


def expected_value_continuous(
    pdf_func,
    lower: float,
    upper: float,
) -> ValuationResult:
    """Calculate expected value for a continuous random variable.

    Formula: E[X] = ∫ x × f(x) dx over [lower, upper]

    Args:
        pdf_func: Probability density function f(x).
        lower: Lower bound of integration.
        upper: Upper bound of integration.

    Returns:
        ValuationResult with expected value.

    Example:
        >>> import scipy.stats
        >>> result = expected_value_continuous(scipy_stats.norm(0, 1).pdf, -10, 10)
        >>> round(result.value, 4)
        0.0
    """
    integrand = lambda x: x * pdf_func(x)
    ev, _ = integrate.quad(integrand, lower, upper, limit=200)

    return ValuationResult(
        value=ev,
        method="Expected Value (Continuous)",
        inputs={"lower": lower, "upper": upper},
        assumptions=["PDF is properly normalized (integrates to 1)"],
        chapter="2",
    )
