"""Tests for advanced valuation module."""

import pytest

from startup_valuation.advanced import (
    binomial_tree,
    binomial_valuation,
    black_scholes,
    ltv_cac_valuation,
    monte_carlo_valuation,
    scenario_analysis,
)
from startup_valuation.types import Distribution, Scenario


def test_black_scholes():
    result = black_scholes(20_000_000, 5_000_000, 0.05, 0.40, 1.0)
    assert round(result.value / 1_000_000, 2) == pytest.approx(15.24, abs=0.1)


def test_black_scholes_long_term():
    result = black_scholes(100_000_000, 30_000_000, 0.04, 0.60, 3.0)
    assert round(result.value / 1_000_000, 2) == pytest.approx(75.76, abs=0.5)


def test_binomial_tree():
    result = binomial_tree(20_000_000, 5_000_000, 0.05, 0.40, 1.0, steps=3)
    assert result.value > 0


def test_binomial_valuation():
    result = binomial_valuation(20_000_000, 5_000_000, 0.05, 0.40, 1.0, steps=50)
    assert round(result.value / 1_000_000, 2) == pytest.approx(15.24, abs=0.5)


def test_scenario_analysis():
    scenarios = [
        Scenario("bull", 0.20, 10_000_000),
        Scenario("base", 0.60, 5_000_000),
        Scenario("bear", 0.20, 1_000_000),
    ]
    result = scenario_analysis(scenarios)
    assert result.value == pytest.approx(5_200_000)


def test_scenario_analysis_four():
    scenarios = [
        Scenario("best", 0.15, 20_000_000),
        Scenario("base", 0.50, 8_000_000),
        Scenario("worst", 0.25, 3_000_000),
        Scenario("fail", 0.10, 500_000),
    ]
    result = scenario_analysis(scenarios)
    assert result.value == pytest.approx(7_800_000)


def test_monte_carlo_valuation():
    from startup_valuation.types import Distribution

    result = monte_carlo_valuation(
        market_size_dist=Distribution("uniform", {"min": 1_000_000, "max": 10_000_000}),
        market_share_dist=Distribution("uniform", {"min": 0.01, "max": 0.10}),
        margin_dist=Distribution("uniform", {"min": 0.10, "max": 0.40}),
        exit_multiple=10,
        discount_rate=0.15,
        years=5,
        num_simulations=1000,
        seed=42,
    )
    assert result.value > 0


def test_ltv_cac_valuation():
    result = ltv_cac_valuation(
        ltv_dist=Distribution("uniform", {"min": 1000, "max": 5000}),
        cac_dist=Distribution("uniform", {"min": 100, "max": 500}),
        market_size_dist=Distribution("uniform", {"min": 1_000_000, "max": 10_000_000}),
        num_simulations=1000,
        seed=42,
    )
    assert result.value > 0
