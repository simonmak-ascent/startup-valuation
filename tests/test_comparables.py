"""Tests for comparables module."""

import pytest

from startup_valuation.comparables import (
    ev_ebitda,
    ev_revenue,
    pe_ratio,
    ps_ratio,
    regression_adjusted_multiple,
    target_valuation_multiple,
)


def test_pe_ratio():
    result = pe_ratio(500_000_000, 50_000_000)
    assert result.value == pytest.approx(10.0)


def test_ps_ratio():
    result = ps_ratio(500_000_000, 100_000_000)
    assert result.value == pytest.approx(5.0)


def test_ev_ebitda():
    result = ev_ebitda(1_000_000_000, 100_000_000)
    assert result.value == pytest.approx(10.0)


def test_ev_revenue():
    result = ev_revenue(500_000_000, 100_000_000)
    assert result.value == pytest.approx(5.0)


def test_regression_adjusted_multiple():
    result = regression_adjusted_multiple(2.5, 0.30, 10, 1, 0.5, 0, -1.5, 0, -0.2)
    assert result.value == pytest.approx(6.0)


def test_target_valuation_multiple():
    result = target_valuation_multiple(5.5, 8_000_000)
    assert result.value == pytest.approx(44_000_000)
