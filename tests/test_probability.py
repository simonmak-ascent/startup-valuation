"""Tests for probability module."""

import pytest
import scipy.stats

from startup_valuation.probability import (
    expected_value_discrete, joint_probability, probability_weighted_value,
    portfolio_expected_return, poisson_probability, expected_value_continuous,
)


def test_expected_value_discrete():
    result = expected_value_discrete([1, 0], [0.3, 0.7])
    assert result.value == pytest.approx(0.3)


def test_joint_probability():
    result = joint_probability([0.90, 0.70, 0.60, 0.85])
    assert round(result.value, 4) == pytest.approx(0.3213, abs=0.001)


def test_probability_weighted_value():
    result = probability_weighted_value([0.20, 0.60, 0.20], [10_000_000, 5_000_000, 1_000_000])
    assert result.value == pytest.approx(5_200_000)


def test_portfolio_expected_return():
    result = portfolio_expected_return([0.20, 0.30, 0.20, 0.30], [10, 2, 1, 0])
    assert result.value == pytest.approx(2.8)


def test_poisson_probability():
    result = poisson_probability(500, 450)
    assert round(result.value, 3) == pytest.approx(0.001, abs=0.001)


def test_expected_value_continuous():
    result = expected_value_continuous(scipy.stats.norm(0, 1).pdf, -10, 10)
    assert round(result.value, 4) == pytest.approx(0.0, abs=0.01)
