"""Tests for hardware module."""

import pytest

from startup_valuation.hardware import (
    trl_adjusted_valuation, gross_margin_hardware,
    break_even_volume, probability_weighted_dcf,
)


def test_trl_adjusted_valuation():
    result = trl_adjusted_valuation(10_000_000_000, 0.05, 0.40, 15, 0.80)
    assert round(result.value / 1_000_000_000, 1) == pytest.approx(0.6, abs=0.1)


def test_gross_margin_hardware():
    result = gross_margin_hardware(1_000, 600)
    assert result.value == pytest.approx(0.40)


def test_break_even_volume():
    result = break_even_volume(1_000_000, 1_000, 600)
    assert result.value == pytest.approx(2_500)


def test_probability_weighted_dcf():
    result = probability_weighted_dcf([0.30, 0.40, 0.30], [60_000_000_000, 10_000_000_000, 0])
    assert result.value / 1_000_000_000 == pytest.approx(22.0)
