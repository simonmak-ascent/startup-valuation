"""Tests for core valuation module."""

import pytest

from startup_valuation.core import (
    scorecard_valuation, berkus_valuation, risk_factor_summation,
    vc_method_post_money, vc_method_pre_money, terminal_value_multiple,
)


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


def test_risk_factor_summation():
    result = risk_factor_summation(2_000_000, [1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0])
    assert result.value == pytest.approx(2_750_000)


def test_vc_method_post_money():
    result = vc_method_post_money(500_000_000, 10)
    assert result.value == pytest.approx(50_000_000)


def test_vc_method_pre_money():
    result = vc_method_pre_money(8_000_000, 1_500_000)
    assert result.value == pytest.approx(6_500_000)


def test_terminal_value_multiple():
    result = terminal_value_multiple(20_000_000, 8)
    assert result.value == pytest.approx(160_000_000)
