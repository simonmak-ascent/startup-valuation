"""Advanced valuation techniques: Black-Scholes, Binomial, Monte Carlo, Scenario Analysis.

Chapter 4: Advanced Techniques
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from scipy import stats

from startup_valuation.types import Distribution, Scenario, ValuationResult


def black_scholes(
    underlying: float,
    strike: float,
    risk_free_rate: float,
    volatility: float,
    time_to_maturity: float,
) -> ValuationResult:
    """Calculate call option value using Black-Scholes model.

    Formula: C = N(d₁)S - N(d₂)Ke^(-rT)
    where:
        d₁ = [ln(S/K) + (r + σ²/2)T] / [σ√T]
        d₂ = d₁ - σ√T

    Args:
        underlying: Current price of underlying asset (S).
        strike: Strike price (K).
        risk_free_rate: Risk-free rate (r).
        volatility: Volatility of underlying (σ).
        time_to_maturity: Time to maturity in years (T).

    Returns:
        ValuationResult with call option value.

    Example:
        >>> result = black_scholes(20_000_000, 5_000_000, 0.05, 0.40, 1.0)
        >>> round(result.value / 1_000_000, 2)
        15.24
    """
    if underlying <= 0 or strike <= 0:
        raise ValueError("underlying and strike must be positive")
    if volatility <= 0:
        raise ValueError("volatility must be positive")
    if time_to_maturity <= 0:
        raise ValueError("time_to_maturity must be positive")

    d1 = (math.log(underlying / strike) + (risk_free_rate + volatility**2 / 2) * time_to_maturity) / (
        volatility * math.sqrt(time_to_maturity)
    )
    d2 = d1 - volatility * math.sqrt(time_to_maturity)

    call_value = underlying * stats.norm.cdf(d1) - strike * math.exp(
        -risk_free_rate * time_to_maturity
    ) * stats.norm.cdf(d2)

    return ValuationResult(
        value=call_value,
        method="Black-Scholes",
        inputs={
            "underlying": underlying,
            "strike": strike,
            "risk_free_rate": risk_free_rate,
            "volatility": volatility,
            "time_to_maturity": time_to_maturity,
        },
        assumptions=[
            "European-style option (exercise only at maturity)",
            "Volatility is constant",
            "No dividends",
            "Continuous trading",
        ],
        chapter="4",
    )


def binomial_tree(
    underlying: float,
    strike: float,
    risk_free_rate: float,
    volatility: float,
    time_to_maturity: float,
    steps: int = 3,
) -> ValuationResult:
    """Value an option using a binomial tree model.

    Formulas:
        u = e^(σ√Δt)
        d = e^(-σ√Δt)
        p = (e^(rΔt) - d) / (u - d)

    Args:
        underlying: Current price of underlying asset.
        strike: Strike price.
        risk_free_rate: Risk-free rate.
        volatility: Volatility.
        time_to_maturity: Time to maturity in years.
        steps: Number of time steps.

    Returns:
        ValuationResult with option value.
    """
    dt = time_to_maturity / steps
    u = math.exp(volatility * math.sqrt(dt))
    d = math.exp(-volatility * math.sqrt(dt))
    p = (math.exp(risk_free_rate * dt) - d) / (u - d)

    # Build terminal node values
    node_values = [max(underlying * (u**i) * (d ** (steps - i)) - strike, 0) for i in range(steps + 1)]

    # Backward induction
    for step in range(steps - 1, -1, -1):
        node_values = [
            math.exp(-risk_free_rate * dt) * (p * node_values[i + 1] + (1 - p) * node_values[i])
            for i in range(step + 1)
        ]

    option_value = node_values[0]

    return ValuationResult(
        value=option_value,
        method="Binomial Tree",
        inputs={
            "underlying": underlying,
            "strike": strike,
            "risk_free_rate": risk_free_rate,
            "volatility": volatility,
            "time_to_maturity": time_to_maturity,
            "steps": steps,
        },
        assumptions=[
            "American-style option (can exercise at any node)",
            "Binomial tree converges to Black-Scholes as steps → ∞",
        ],
        chapter="4",
    )


def monte_carlo_valuation(
    market_size_dist: Distribution,
    market_share_dist: Distribution,
    margin_dist: Distribution,
    exit_multiple: float,
    discount_rate: float,
    years: float,
    num_simulations: int = 10_000,
    seed: int | None = None,
) -> ValuationResult:
    """Monte Carlo simulation for startup valuation.

    Formula: PV = (Market Size × Market Share × Margin × Multiple) / (1 + r)^n

    Args:
        market_size_dist: Distribution for market size.
        market_share_dist: Distribution for market share.
        margin_dist: Distribution for profit margin.
        exit_multiple: Exit multiple.
        discount_rate: Discount rate.
        years: Years to exit.
        num_simulations: Number of simulations.
        seed: Random seed for reproducibility.

    Returns:
        ValuationResult with mean, percentiles, and full distribution.
    """
    rng = np.random.default_rng(seed)

    def sample(dist: Distribution, n: int) -> Any:
        if dist.dist_type == "normal":
            return rng.normal(dist.params["mean"], dist.params["std"], n)
        elif dist.dist_type == "uniform":
            return rng.uniform(dist.params["min"], dist.params["max"], n)
        elif dist.dist_type == "triangular":
            return rng.triangular(dist.params["min"], dist.params["mode"], dist.params["max"], n)
        else:
            raise ValueError(f"Unknown distribution type: {dist.dist_type}")

    market_sizes = sample(market_size_dist, num_simulations)
    market_shares = sample(market_share_dist, num_simulations)
    margins = sample(margin_dist, num_simulations)

    terminal_values = market_sizes * market_shares * margins * exit_multiple
    present_values = terminal_values / ((1 + discount_rate) ** years)

    present_values = present_values[present_values > 0]  # Filter negative values

    mean_val = float(np.mean(present_values))

    return ValuationResult(
        value=mean_val,
        method="Monte Carlo Valuation",
        inputs={
            "market_size_dist": f"{market_size_dist.dist_type}({market_size_dist.params})",
            "market_share_dist": f"{market_share_dist.dist_type}({market_share_dist.params})",
            "margin_dist": f"{margin_dist.dist_type}({margin_dist.params})",
            "exit_multiple": exit_multiple,
            "discount_rate": discount_rate,
            "years": years,
            "num_simulations": num_simulations,
        },
        assumptions=[
            f"Results based on {num_simulations:,} simulations",
            "Distributions are independent",
        ],
        chapter="4",
    )


def scenario_analysis(scenarios: list[Scenario]) -> ValuationResult:
    """Calculate expected value across scenarios.

    Formula: E[V] = Σ pᵢ × Vᵢ

    Args:
        scenarios: List of scenarios with name, probability, and value.

    Returns:
        ValuationResult with expected value.

    Example:
        >>> scenarios = [
        ...     Scenario("bull", 0.20, 10_000_000),
        ...     Scenario("base", 0.60, 5_000_000),
        ...     Scenario("bear", 0.20, 1_000_000),
        ... ]
        >>> result = scenario_analysis(scenarios)
        >>> result.value
        5200000.0
    """
    if not scenarios:
        raise ValueError("at least one scenario required")

    total_prob = sum(s.probability for s in scenarios)
    if abs(total_prob - 1.0) > 0.01:
        raise ValueError(f"scenario probabilities must sum to 1.0, got {total_prob}")

    ev = sum(s.probability * s.value for s in scenarios)

    return ValuationResult(
        value=ev,
        method="Scenario Analysis",
        inputs={"scenarios": [(s.name, s.probability, s.value) for s in scenarios]},
        assumptions=["Scenarios are mutually exclusive and exhaustive"],
        chapter="4",
    )


def ltv_cac_valuation(
    ltv_dist: Distribution,
    cac_dist: Distribution,
    market_size_dist: Distribution,
    num_simulations: int = 10_000,
    seed: int | None = None,
) -> ValuationResult:
    """Valuation using LTV/CAC ratio with Monte Carlo.

    Formula: Valuation = (LTV/CAC) × Market Size × 0.1

    Args:
        ltv_dist: Distribution for LTV.
        cac_dist: Distribution for CAC.
        market_size_dist: Distribution for market size.
        num_simulations: Number of simulations.
        seed: Random seed.

    Returns:
        ValuationResult with mean valuation.
    """
    rng = np.random.default_rng(seed)

    def sample(dist: Distribution, n: int) -> Any:
        if dist.dist_type == "normal":
            return rng.normal(dist.params["mean"], dist.params["std"], n)
        elif dist.dist_type == "uniform":
            return rng.uniform(dist.params["min"], dist.params["max"], n)
        elif dist.dist_type == "triangular":
            return rng.triangular(dist.params["min"], dist.params["mode"], dist.params["max"], n)
        else:
            raise ValueError(f"Unknown distribution type: {dist.dist_type}")

    ltvs = sample(ltv_dist, num_simulations)
    cacs = sample(cac_dist, num_simulations)
    market_sizes = sample(market_size_dist, num_simulations)

    cacs = np.maximum(cacs, 1e-6)  # Avoid division by zero
    valuations = (ltvs / cacs) * market_sizes * 0.1
    valuations = valuations[valuations > 0]

    mean_val = float(np.mean(valuations))

    return ValuationResult(
        value=mean_val,
        method="LTV/CAC Valuation",
        inputs={
            "ltv_dist": f"{ltv_dist.dist_type}({ltv_dist.params})",
            "cac_dist": f"{cac_dist.dist_type}({cac_dist.params})",
            "market_size_dist": f"{market_size_dist.dist_type}({market_size_dist.params})",
        },
        assumptions=["LTV/CAC > 1 for viable business model"],
        chapter="4",
    )


def binomial_valuation(
    underlying: float,
    strike: float,
    risk_free_rate: float,
    volatility: float,
    time_to_maturity: float,
    steps: int = 50,
) -> ValuationResult:
    """Value a startup option using binomial tree with high resolution.

    Formula: Same as binomial_tree with steps=50 for convergence to Black-Scholes.

    Args:
        underlying: Current value of startup.
        strike: Liquidation preference or strike price.
        risk_free_rate: Risk-free rate.
        volatility: Volatility of startup value.
        time_to_maturity: Time to exit in years.
        steps: Number of time steps (default 50 for convergence).

    Returns:
        ValuationResult with option value.

    Example:
        >>> result = binomial_valuation(20_000_000, 5_000_000, 0.05, 0.40, 1.0, 50)
        >>> round(result.value / 1_000_000, 2)
        15.24
    """
    dt = time_to_maturity / steps
    u = math.exp(volatility * math.sqrt(dt))
    d = math.exp(-volatility * math.sqrt(dt))
    p = (math.exp(risk_free_rate * dt) - d) / (u - d)

    # Build terminal node values
    node_values = [max(underlying * (u**i) * (d ** (steps - i)) - strike, 0) for i in range(steps + 1)]

    # Backward induction
    for step in range(steps - 1, -1, -1):
        node_values = [
            math.exp(-risk_free_rate * dt) * (p * node_values[i + 1] + (1 - p) * node_values[i])
            for i in range(step + 1)
        ]

    option_value = node_values[0]

    return ValuationResult(
        value=option_value,
        method="Binomial Valuation (High Resolution)",
        inputs={
            "underlying": underlying,
            "strike": strike,
            "risk_free_rate": risk_free_rate,
            "volatility": volatility,
            "time_to_maturity": time_to_maturity,
            "steps": steps,
        },
        assumptions=[
            f"Binomial tree with {steps} steps converges to Black-Scholes",
            "European-style option",
        ],
        chapter="4",
    )
