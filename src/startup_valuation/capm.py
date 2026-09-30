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
        steps=[
            {
                "label": "CAPM",
                "value": risk_free_rate + beta * (market_return - risk_free_rate),
                "formula": r"E(R) = R_f + \beta(R_m - R_f)",
            },
        ],
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
        steps=[
            {
                "label": "Portfolio Beta",
                "value": sum(w * b for w, b in zip(weights, betas)),
                "formula": r"\beta_p = \sum w_i \beta_i",
            },
        ],
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
        steps=[
            {
                "label": "Startup-Adjusted CAPM",
                "value": risk_free_rate + beta * market_risk_premium + size_premium + illiquidity_premium,
                "formula": r"E(R) = R_f + \beta MRP + size + illiquidity",
            },
        ],
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
        steps=[
            {
                "label": "Portfolio Variance",
                "value": var,
                "formula": r"\sigma^2_p = w^T \Sigma w",
            },
        ],
        method="Portfolio Variance",
        inputs={"weights": weights, "covariance_matrix": covariance_matrix},
        assumptions=["Variances and covariances are accurately estimated"],
        chapter="2",
        formula_number="2.8",
    )


def wacc(
    equity_value: float,
    debt_value: float,
    cost_of_equity: float,
    cost_of_debt: float,
    tax_rate: float,
) -> ValuationResult:
    """Calculate the weighted average cost of capital (WACC).

    Formula: WACC = (E/V)·Re + (D/V)·Rd·(1 − T)

    Args:
        equity_value: Market value of equity (E), in currency units.
        debt_value: Market value of debt (D), in currency units.
        cost_of_equity: After-tax cost of equity (Re) as a decimal.
        cost_of_debt: Pre-tax cost of debt (Rd) as a decimal.
        tax_rate: Marginal corporate tax rate (T) as a decimal.

    Returns:
        ValuationResult with WACC as value.

    Raises:
        ValueError: If equity_value or debt_value is negative, or E + D <= 0.

    Notes:
        WACC blends the after-tax cost of each capital source by its market-value
        weight, and is the discount rate used to value the whole firm:

        $$WACC = \\frac{E}{V} R_e + \\frac{D}{V} R_d (1 - T)$$

        The interest tax shield is captured by ``(1 - T)`` on the debt term.

    References:
        Startup Valuation textbook, Chapter 2, Section 2.5.

    See Also:
        capm : Estimate the cost of equity (Re).

    Example:
        >>> result = wacc(700000, 300000, 0.18, 0.08, 0.25)
        >>> round(result.value, 4)
        0.144
    """
    if equity_value < 0 or debt_value < 0:
        raise ValueError("equity_value and debt_value must be >= 0")
    total = equity_value + debt_value
    if total <= 0:
        raise ValueError("equity_value + debt_value must be > 0")

    equity_weight = equity_value / total
    debt_weight = debt_value / total
    value = equity_weight * cost_of_equity + debt_weight * cost_of_debt * (1 - tax_rate)

    return ValuationResult(
        value=value,
        method="Weighted Average Cost of Capital",
        inputs={
            "equity_value": equity_value,
            "debt_value": debt_value,
            "cost_of_equity": cost_of_equity,
            "cost_of_debt": cost_of_debt,
            "tax_rate": tax_rate,
        },
        assumptions=["Capital structure weights use market values and stay constant"],
        chapter="2",
        formula_number="2.5",
        steps=[
            {"label": "Equity weight × Re", "value": equity_weight * cost_of_equity, "formula": r"(E/V)\cdot R_e"},
            {
                "label": "Debt weight × Rd × (1−T)",
                "value": debt_weight * cost_of_debt * (1 - tax_rate),
                "formula": r"(D/V)\cdot R_d(1-T)",
            },
            {"label": "WACC", "value": value, "formula": r"WACC = (E/V)R_e + (D/V)R_d(1-T)"},
        ],
    )
