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
    """Calculate expected return using the Capital Asset Pricing Model.

    Formula: E[R] = Rf + β × (Rm - Rf)

    Args:
        risk_free_rate: Risk-free rate (Rf), typically 10-year Treasury yield.
        beta: Systematic risk measure relative to market (β).
        market_return: Expected market return (Rm).

    Returns:
        ValuationResult with expected return as value.

    Notes:
        The CAPM is the foundational model for risk-adjusted discount rates:

        $$E[R] = R_f + \\beta (R_m - R_f)$$

        Beta > 1: more volatile than market. Beta < 1: less volatile.
        Typical startup beta: 1.5-3.0 due to illiquidity and business risk.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.5.
        Sharpe, W. (1964). Capital Asset Prices. Journal of Finance.

    See Also:
        startup_adjusted_capm : Adds size/illiquidity premiums.
        portfolio_beta : Weighted beta for multiple assets.
    """
    return ValuationResult(
        value=risk_free_rate + beta * (market_return - risk_free_rate),
        method="CAPM",
        inputs={"risk_free_rate": risk_free_rate, "beta": beta, "market_return": market_return},
        assumptions=["CAPM assumptions hold (efficient markets, diversified investors)"],
        chapter="2",
        formula_number="2.5",
    )


def portfolio_beta(weights: list[float], betas: list[float]) -> ValuationResult:
    """Calculate weighted portfolio beta.

    Formula: β_portfolio = Σ wᵢ × βᵢ

    Args:
        weights: Portfolio weights (must sum to 1).
        betas: Individual asset betas.

    Returns:
        ValuationResult with portfolio beta.

    Notes:
        $$\\beta_p = \\sum_{i=1}^{n} w_i \\beta_i$$

        Portfolio beta is the weighted average of individual betas.
        Used to estimate the systematic risk of a diversified
        startup portfolio or fund.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.5.

    See Also:
        capm : Expected return using CAPM.
    """
    if abs(sum(weights) - 1.0) > 0.01:
        raise ValueError("weights must sum to 1.0")
    return ValuationResult(
        value=sum(w * b for w, b in zip(weights, betas)),
        method="Portfolio Beta",
        inputs={"weights": weights, "betas": betas},
        assumptions=["Weights sum to 1.0", "Betas are additive (no correlation adjustment)"],
        chapter="2",
        formula_number="2.6",
    )


def startup_adjusted_capm(
    risk_free_rate: float,
    beta: float,
    market_risk_premium: float,
    size_premium: float = 0.05,
    illiquidity_premium: float = 0.03,
) -> ValuationResult:
    """Calculate startup-specific CAPM with size and illiquidity adjustments.

    Formula: E[R] = Rf + β × MRP + Size Premium + Illiquidity Premium

    Args:
        risk_free_rate: Risk-free rate.
        beta: Systematic risk.
        market_risk_premium: Market risk premium.
        size_premium: Additional premium for small companies (default 5%).
        illiquidity_premium: Premium for illiquid investments (default 3%).

    Returns:
        ValuationResult with risk-adjusted discount rate.

    Notes:
        Startup-adjusted CAPM extends the standard model with:

        $$E[R] = R_f + \\beta(R_m - R_f) + SP + IP$$

        Size premium: small companies have higher risk (typically 2-10%).
        Illiquidity premium: private companies have no ready market.
        Total discount rate for startups: 15-25%+.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.5.
        Damodaran, A. — Annual size premium studies.

    See Also:
        capm : Standard CAPM without adjustments.
        international.adjusted_capm_international : Adds country risk.
    """
    return ValuationResult(
        value=risk_free_rate + beta * market_risk_premium + size_premium + illiquidity_premium,
        method="Startup-Adjusted CAPM",
        inputs={
            "risk_free_rate": risk_free_rate,
            "beta": beta,
            "market_risk_premium": market_risk_premium,
            "size_premium": size_premium,
            "illiquidity_premium": illiquidity_premium,
        },
        assumptions=[
            "Size premium reflects small-company risk",
            "Illiquidity premium reflects lack of marketability",
            "CAPM assumptions hold for base rate",
        ],
        chapter="2",
        formula_number="2.7",
    )


def portfolio_variance(
    weights: list[float],
    covariance_matrix: list[list[float]],
) -> ValuationResult:
    """Calculate portfolio variance from a covariance matrix.

    Formula: σ²_p = wᵀ Σ w

    Args:
        weights: Portfolio allocation weights.
        covariance_matrix: N×N covariance matrix.

    Notes:
        $$\\sigma^2_p = \\sum_i \\sum_j w_i w_j \\sigma_{ij}$$

        Full covariance matrix captures both individual variances and
        inter-asset correlations. Used in modern portfolio theory.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.5.
    """
    n = len(weights)
    var = sum(weights[i] * weights[j] * covariance_matrix[i][j] for i in range(n) for j in range(n))
    return ValuationResult(
        value=var,
        method="Portfolio Variance",
        inputs={"weights": weights, "covariance_matrix": covariance_matrix},
        assumptions=["Variances and covariances are accurately estimated"],
        chapter="2",
        formula_number="2.8",
    )
