"""Tests for CAPM module."""

import pytest

from startup_valuation.capm import capm, portfolio_beta, startup_adjusted_capm, portfolio_variance


def test_capm():
    result = capm(0.03, 1.5, 0.10)
    assert round(result.value, 4) == pytest.approx(0.135, abs=0.001)


def test_portfolio_beta():
    result = portfolio_beta([0.60, 0.40], [0.8, 1.2])
    assert result.value == pytest.approx(0.96)


def test_startup_adjusted_capm():
    result = startup_adjusted_capm(0.04, 1.3, 0.07, 0.03, 0.10)
    assert round(result.value, 4) == pytest.approx(0.261, abs=0.001)


def test_portfolio_variance():
    result = portfolio_variance([0.5, 0.5], [[0.04, 0.01], [0.01, 0.09]])
    assert result.value == pytest.approx(0.0375)
