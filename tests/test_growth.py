"""Tests for revenue growth and forecasting module."""

import pytest

from startup_valuation.growth import compound_annual_growth_rate, compound_growth


def test_compound_growth_projects_forward():
    result = compound_growth(1_000_000, 0.40, 3)
    assert round(result.value, 2) == pytest.approx(2_744_000.0, abs=1)


def test_compound_growth_zero_rate_is_identity():
    result = compound_growth(500_000, 0.0, 5)
    assert result.value == pytest.approx(500_000.0)


def test_compound_growth_negative_rate_models_decline():
    result = compound_growth(1_000_000, -0.10, 2)
    assert result.value == pytest.approx(810_000.0)


def test_compound_growth_rejects_rate_at_or_below_minus_one():
    with pytest.raises(ValueError, match="growth_rate"):
        compound_growth(1_000_000, -1.0, 3)


def test_compound_growth_rejects_negative_periods():
    with pytest.raises(ValueError, match="periods"):
        compound_growth(1_000_000, 0.1, -1)


def test_cagr_inverts_compound_growth():
    result = compound_annual_growth_rate(1_000_000, 2_744_000, 3)
    assert round(result.value, 4) == pytest.approx(0.40, abs=1e-4)


def test_cagr_rejects_non_positive_start():
    with pytest.raises(ValueError, match="starting_value"):
        compound_annual_growth_rate(0, 100, 3)


def test_cagr_rejects_non_positive_periods():
    with pytest.raises(ValueError, match="periods"):
        compound_annual_growth_rate(1_000, 2_000, 0)
