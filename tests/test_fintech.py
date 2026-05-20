"""Tests for fintech module."""

import pytest

from startup_valuation.fintech import (
    lending_fintech_valuation,
    max_loan_portfolio,
    neobank_valuation,
    network_effects_value,
    payment_processor_valuation,
    payment_revenue,
)


def test_payment_revenue():
    result = payment_revenue(640_000_000_000, 0.0116)
    assert round(result.value / 1_000_000_000, 3) == pytest.approx(7.424, abs=0.01)


def test_max_loan_portfolio():
    result = max_loan_portfolio(100_000_000, 0.08)
    assert result.value == pytest.approx(1_250_000_000)


def test_network_effects_value():
    result = network_effects_value(1_000_000, 1.3)
    assert result.value > 0


def test_lending_fintech_valuation():
    result = lending_fintech_valuation(100_000_000, 0.15, 12)
    assert result.value == pytest.approx(180_000_000)


def test_payment_processor_valuation():
    result = payment_processor_valuation(
        640_000_000_000, 0.0116, 0.20, 0.15, 15, 5,
    )
    assert result.value > 0


def test_neobank_valuation():
    result = neobank_valuation(1_000_000, 50, 0.60, 0.10, 20)
    assert result.value == pytest.approx(6_000_000_000)
