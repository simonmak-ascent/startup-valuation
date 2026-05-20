"""Tests for international module."""

import pytest

from startup_valuation.international import (
    adjusted_capm_international,
    after_tax_cash_flow,
    country_risk_premium,
    country_risk_premium_damodaran,
    currency_adjusted_dcf,
    interest_rate_parity,
    purchasing_power_parity,
    sum_of_parts_valuation,
)


def test_purchasing_power_parity():
    result = purchasing_power_parity(83, 0.05, 0.02)
    assert round(result.value, 1) == pytest.approx(85.4, abs=0.5)


def test_interest_rate_parity():
    result = interest_rate_parity(100, 0.05, 0.02)
    assert round(result.value, 2) == pytest.approx(102.94, abs=0.1)


def test_currency_adjusted_dcf():
    result = currency_adjusted_dcf([10_000_000, 12_000_000], [83, 85], 0.10)
    assert result.value > 0


def test_country_risk_premium():
    result = country_risk_premium(0.105, 0.045)
    assert result.value == pytest.approx(0.06)


def test_country_risk_premium_damodaran():
    result = country_risk_premium_damodaran(0.03, 0.25, 0.15)
    assert result.value == pytest.approx(0.05)


def test_adjusted_capm_international():
    result = adjusted_capm_international(0.045, 1.2, 0.06, 0.03)
    assert round(result.value, 4) == pytest.approx(0.147, abs=0.001)


def test_after_tax_cash_flow():
    result = after_tax_cash_flow(1_000_000, 0.25, 0.10)
    assert result.value == pytest.approx(675_000)


def test_sum_of_parts_valuation():
    result = sum_of_parts_valuation([100_000_000, 50_000_000], [0.80, 0.60])
    assert result.value == pytest.approx(110_000_000)
