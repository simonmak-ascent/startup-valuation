"""Tests for emerging module."""

import pytest

from startup_valuation.emerging import (
    data_moat_value,
    equation_of_exchange,
    esg_adjusted_discount_rate,
    esg_discount_valuation,
    esg_premium_valuation,
    metcalfes_law,
    modified_metcalfes,
    network_density_valuation,
    nvt_ratio,
    protocol_value,
    remote_cost_savings_npv,
    remote_first_premium,
    safe_conversion_cap,
    safe_conversion_discount,
    safe_expected_value,
)


def test_safe_conversion_discount():
    result = safe_conversion_discount(5.0, 0.20)
    assert result.value == pytest.approx(4.0)


def test_safe_conversion_cap():
    result = safe_conversion_cap(8_000_000, 5.0)
    assert result.value > 0


def test_safe_expected_value():
    result = safe_expected_value(500_000, 8_000_000, 0.20, 10_000_000, 5.0)
    assert result.value > 0


def test_equation_of_exchange():
    result = equation_of_exchange(10_000_000_000, 1, 10, 100_000_000)
    assert result.value == pytest.approx(10.0)


def test_nvt_ratio():
    result = nvt_ratio(10_000_000_000, 100_000_000)
    assert result.value == pytest.approx(100.0)


def test_protocol_value():
    result = protocol_value(1_000_000_000, 0.5)
    assert result.value == pytest.approx(500_000_000)


def test_esg_adjusted_discount_rate():
    result = esg_adjusted_discount_rate(0.15, 0.02, 0.01)
    assert result.value == pytest.approx(0.16)


def test_esg_premium_valuation():
    result = esg_premium_valuation(10_000_000, 75, 0.02)
    assert result.value == pytest.approx(25_000_000)


def test_esg_discount_valuation():
    result = esg_discount_valuation(10_000_000, 30, 0.01)
    assert result.value == pytest.approx(7_000_000)


def test_metcalfes_law():
    result = metcalfes_law(100_000)
    assert result.value == pytest.approx(10_000_000_000)


def test_modified_metcalfes():
    result = modified_metcalfes(100_000, 1.3)
    assert result.value > 0


def test_network_density_valuation():
    result = network_density_valuation(10_000_000, 100, 1)
    assert result.value / 1_000_000_000 == pytest.approx(1.0)


def test_remote_cost_savings_npv():
    result = remote_cost_savings_npv(1_200_000, 0.10)
    assert result.value == pytest.approx(12_000_000)


def test_data_moat_value():
    result = data_moat_value(1_000_000, 0.8, 0.001, 5, 0.15)
    assert round(result.value, 0) == pytest.approx(2682, abs=10)


def test_remote_first_premium():
    result = remote_first_premium(10_000_000, 0.20, 0.10, 0.05)
    assert result.value == pytest.approx(13_500_000)
