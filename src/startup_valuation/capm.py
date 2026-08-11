"""CAPM and risk-adjusted return calculations.

Chapter 2: Mathematical Foundations — Risk-Adjusted Discount Rates
"""

from __future__ import annotations

from startup_valuation.types import ValuationResult


def capm(
    risk_free_rate: float,
    beta: float,
    market_return: float,
) -> ValuationResult:
    """Calculate expected return using CAPM.

    Formula: E(Rᵢ) = Rf + βᵢ × (E(Rm) - Rf)

    Args:
        risk_free_rate: Risk-free rate (Rf).
        beta: Beta of the asset (βᵢ).
        market_return: Expected market return (E(Rm)).

    Returns:
        ValuationResult with expected return.

    Example:
        >>> result = capm(0.03, 1.5, 0.10)
        >>> round(result.value, 4)
        0.135
    """
    market_risk_premium = market_return - risk_free_rate
    expected_return = risk_free_rate + beta * market_risk_premium

    return ValuationResult(
        value=expected_return,
        method="CAPM",
        inputs={
            "risk_free_rate": risk_free_rate,
            "beta": beta,
            "market_return": market_return,
        },
        assumptions=[
            "Markets are efficient",
            "Beta captures all systematic risk",
            "Risk-free rate is accessible to investors",
        ],
        chapter="2",
    )


def portfolio_beta(
    weights: list[float],
    betas: list[float],
) -> ValuationResult:
    """Calculate portfolio beta as weighted average.

    Formula: βp = Σ wᵢ × βᵢ

    Args:
        weights: Portfolio weights (wᵢ).
        betas: Individual asset betas (βᵢ).

    Returns:
        ValuationResult with portfolio beta.

    Example:
        >>> result = portfolio_beta([0.60, 0.40], [0.8, 1.2])
        >>> result.value
        0.96
    """
    if len(weights) != len(betas):
        raise ValueError("weights and betas must have the same length")

    pb = sum(w * b for w, b in zip(weights, betas))

    return ValuationResult(
        value=pb,
        method="Portfolio Beta",
        inputs={"weights": weights, "betas": betas},
        assumptions=["Beta is stable and accurately estimated"],
        chapter="2",
    )


def startup_adjusted_capm(
    risk_free_rate: float,
    beta: float,
    market_risk_premium: float,
    size_premium: float = 0.0,
    startup_premium: float = 0.0,
) -> ValuationResult:
    """Calculate startup-adjusted CAPM with additional risk premiums.

    Formula: E(R) = Rf + β × MRP + Size Premium + Startup Premium

    Args:
        risk_free_rate: Risk-free rate.
        beta: Beta of the startup.
        market_risk_premium: Market risk premium.
        size_premium: Additional premium for small company size.
        startup_premium: Additional premium for startup-specific risks.

    Returns:
        ValuationResult with adjusted expected return.

    Example:
        >>> result = startup_adjusted_capm(0.04, 1.3, 0.07, 0.03, 0.10)
        >>> round(result.value, 4)
        0.261
    """
    expected_return = risk_free_rate + beta * market_risk_premium + size_premium + startup_premium

    return ValuationResult(
        value=expected_return,
        method="Startup-Adjusted CAPM",
        inputs={
            "risk_free_rate": risk_free_rate,
            "beta": beta,
            "market_risk_premium": market_risk_premium,
            "size_premium": size_premium,
            "startup_premium": startup_premium,
        },
        assumptions=[
            "Additional premiums are additive to CAPM",
            "Beta is estimated from comparable companies",
        ],
        chapter="2",
    )


def portfolio_variance(
    weights: list[float],
    covariances: list[list[float]],
) -> ValuationResult:
    """Calculate portfolio variance.

    Formula: Var(Rp) = ΣΣ wᵢ × wⱼ × Cov(Rᵢ, Rⱼ)

    Args:
        weights: Portfolio weights.
        covariances: Covariance matrix.

    Returns:
        ValuationResult with portfolio variance.
    """
    n = len(weights)
    if len(covariances) != n or any(len(row) != n for row in covariances):
        raise ValueError("covariances must be an n×n matrix")

    variance = sum(weights[i] * weights[j] * covariances[i][j] for i in range(n) for j in range(n))

    return ValuationResult(
        value=variance,
        method="Portfolio Variance",
        inputs={"weights": weights, "covariances": covariances},
        assumptions=["Covariance matrix is accurate and stable"],
        chapter="2",
    )
