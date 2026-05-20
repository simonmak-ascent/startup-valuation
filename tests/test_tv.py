"""Tests for time value of money module."""

import pytest

from startup_valuation.tv import annuity_present_value, net_present_value, present_value


def test_present_value():
    result = present_value(11_000, 0.08, 1)
    assert round(result.value, 2) == pytest.approx(10_185.19, abs=1)


def test_net_present_value():
    result = net_present_value([-100_000, 30_000, 40_000, 50_000], 0.10)
    assert round(result.value, 0) == pytest.approx(-2_104, abs=2)


def test_annuity_present_value():
    result = annuity_present_value(50_000, 0.10, 4)
    assert round(result.value, 0) == pytest.approx(158_493, abs=5)
