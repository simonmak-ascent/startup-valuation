"""Tests for marketplace module."""

import pytest

from startup_valuation.marketplace import (
    buyer_retention,
    gmv,
    gmv_multiple_valuation,
    liquidity,
    network_density,
    network_value,
    take_rate,
)


def test_gmv():
    result = gmv([100, 200, 300])
    assert result.value == pytest.approx(600)


def test_take_rate():
    result = take_rate(2_900_000_000, 24_700_000_000)
    assert round(result.value, 4) == pytest.approx(0.1174, abs=0.001)


def test_liquidity():
    result = liquidity(350, 1000)
    assert result.value == pytest.approx(0.35)


def test_gmv_multiple_valuation():
    result = gmv_multiple_valuation(24_700_000_000, 2.4)
    assert round(result.value / 1_000_000_000, 2) == pytest.approx(59.28, abs=0.1)


def test_network_value():
    result = network_value(1_000_000, 1.0, 1.3)
    assert result.value > 0


def test_buyer_retention():
    result = buyer_retention(10_000, 3_500)
    assert result.value == pytest.approx(0.35)


def test_network_density():
    result = network_density(5_000, 3_000, 10_000)
    assert result.value > 0
