"""Tests for TV, CAPM, core, advanced, comparables modules."""

import pytest
from startup_valuation.tv import present_value, net_present_value, annuity_present_value
from startup_valuation.capm import capm, portfolio_beta, startup_adjusted_capm
from startup_valuation.core import (
    scorecard_valuation,
    berkus_valuation,
    risk_factor_summation,
    vc_method_post_money,
    vc_method_pre_money,
    terminal_value_multiple,
)
from startup_valuation.comparables import ps_ratio, regression_adjusted_multiple, target_valuation_multiple


# TV tests
def test_present_value():
    result = present_value(11000, 0.08, 1)
    assert round(result.value, 2) == pytest.approx(10185.19)


def test_net_present_value():
    result = net_present_value([-100000, 30000, 40000, 50000], 0.10)
    assert round(result.value, 0) == pytest.approx(-2104, abs=2)


def test_annuity_present_value():
    result = annuity_present_value(50000, 0.10, 4)
    assert round(result.value, 0) == pytest.approx(158493, abs=5)


# CAPM tests
def test_capm():
    result = capm(0.03, 1.5, 0.10)
    assert round(result.value, 4) == pytest.approx(0.135)


def test_portfolio_beta():
    result = portfolio_beta([0.60, 0.40], [0.8, 1.2])
    assert result.value == pytest.approx(0.96)


def test_startup_adjusted_capm():
    result = startup_adjusted_capm(0.04, 1.3, 0.07, 0.03, 0.10)
    assert round(result.value, 4) == pytest.approx(0.261)


# Core tests
def test_scorecard_valuation():
    result = scorecard_valuation(
        1_500_000,
        [0.30, 0.25, 0.15, 0.10, 0.10, 0.05, 0.05],
        [1.25, 1.50, 1.20, 0.75, 1.00, 0.90, 1.00],
    )
    assert result.value == pytest.approx(1_800_000)


def test_berkus_valuation():
    result = berkus_valuation(500_000, 400_000, 500_000, 500_000, 0)
    assert result.value == pytest.approx(1_900_000)


def test_vc_method_post_money():
    result = vc_method_post_money(500_000_000, 10)
    assert result.value == pytest.approx(50_000_000)


def test_vc_method_pre_money():
    result = vc_method_pre_money(8_000_000, 1_500_000)
    assert result.value == pytest.approx(6_500_000)


def test_terminal_value_multiple():
    result = terminal_value_multiple(20_000_000, 8)
    assert result.value == pytest.approx(160_000_000)


# Comparables tests
def test_ps_ratio():
    result = ps_ratio(500_000_000, 100_000_000)
    assert result.value == pytest.approx(5.0)


def test_regression_adjusted_multiple():
    result = regression_adjusted_multiple(2.5, 0.30, 10, 1, 0.5, 0, -1.5, 0, -0.2)
    assert result.value == pytest.approx(6.0)


def test_target_valuation_multiple():
    result = target_valuation_multiple(5.5, 8_000_000)
    assert result.value == pytest.approx(44_000_000)
