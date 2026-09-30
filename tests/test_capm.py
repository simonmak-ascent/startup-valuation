"""Tests for CAPM module."""

import pytest

from startup_valuation.capm import capm, portfolio_beta, portfolio_variance, startup_adjusted_capm


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


def test_wacc_blends_after_tax_costs():
    from startup_valuation.capm import wacc

    result = wacc(700_000, 300_000, 0.18, 0.08, 0.25)
    assert round(result.value, 4) == pytest.approx(0.144, abs=1e-6)


def test_wacc_rejects_zero_capital():
    from startup_valuation.capm import wacc

    with pytest.raises(ValueError, match="must be > 0"):
        wacc(0, 0, 0.18, 0.08, 0.25)
