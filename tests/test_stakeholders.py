"""Tests for stakeholders module."""

import pytest

from startup_valuation.stakeholders import (
    single_round_dilution, multi_round_dilution, acquisition_value,
    opm_common_stock, pwerm, common_stock_discount, liquidation_value,
    venture_debt_dilution, risk_adjusted_synergy, intrinsic_option_value,
    probability_weighted_employee_value, vesting_adjusted_value,
    cash_equity_breakeven, max_asset_based_loan,
)


def test_single_round_dilution():
    result = single_round_dilution(1.0, 5_000_000, 20_000_000)
    assert result.value == pytest.approx(0.75)


def test_multi_round_dilution():
    result = multi_round_dilution(1.0, [2_000_000, 5_000_000, 10_000_000, 20_000_000],
                                   [10_000_000, 25_000_000, 60_000_000, 150_000_000])
    assert round(result.value, 2) == pytest.approx(0.46, abs=0.02)


def test_acquisition_value():
    result = acquisition_value(100_000_000, 20_000_000, 15_000_000, 10_000_000, 0.4, 0.8)
    assert result.value == pytest.approx(110_000_000)


def test_opm_common_stock():
    result = opm_common_stock(100_000_000, 40_000_000, 3, 0.60)
    assert round(result.value / 1_000_000, 0) == pytest.approx(69, abs=5)


def test_pwerm():
    scenarios = [
        {"probability": 0.20, "common_value": 92_000_000},
        {"probability": 0.50, "common_value": 55_000_000},
        {"probability": 0.20, "common_value": 4_000_000},
        {"probability": 0.10, "common_value": 0},
    ]
    result = pwerm(scenarios)
    assert round(result.value / 1_000_000, 1) == pytest.approx(46.7, abs=0.5)


def test_common_stock_discount():
    result = common_stock_discount(100_000_000, 65_000_000)
    assert result.value == pytest.approx(0.35)


def test_liquidation_value():
    assets = {"cash": 5_000_000, "ar": 3_000_000, "equipment": 2_000_000}
    rates = {"cash": 1.0, "ar": 0.80, "equipment": 0.30}
    result = liquidation_value(assets, rates)
    assert result.value == pytest.approx(8_000_000)


def test_venture_debt_dilution():
    result = venture_debt_dilution(0.10, 3_000_000, 40_000_000)
    assert result.value == pytest.approx(0.0075)


def test_risk_adjusted_synergy():
    result = risk_adjusted_synergy(20_000_000, 15_000_000, 0.4, 0.8, 0.10, 3)
    assert round(result.value / 1_000_000, 1) == pytest.approx(49.7, abs=1)


def test_intrinsic_option_value():
    result = intrinsic_option_value(1.0, 5.0, 100_000)
    assert result.value == pytest.approx(400_000)


def test_probability_weighted_employee_value():
    scenarios = [
        {"probability": 0.20, "fmv": 10.0, "strike": 1.0, "shares": 50_000},
        {"probability": 0.50, "fmv": 5.0, "strike": 1.0, "shares": 50_000},
        {"probability": 0.30, "fmv": 1.0, "strike": 1.0, "shares": 50_000},
    ]
    result = probability_weighted_employee_value(scenarios)
    assert result.value == pytest.approx(190_000)


def test_vesting_adjusted_value():
    result = vesting_adjusted_value(400_000, 0.25, 0.25, 0.8, 3)
    assert round(result.value / 1000, 0) == pytest.approx(246, abs=5)


def test_cash_equity_breakeven():
    result = cash_equity_breakeven(50_000, 500_000, 0.30, 0.20, 4)
    assert round(result.value / 1000, 0) == pytest.approx(100, abs=10)


def test_max_asset_based_loan():
    result = max_asset_based_loan(1_000_000, 2_000_000, 500_000, 3_000_000)
    assert result.value == pytest.approx(4_750_000)
