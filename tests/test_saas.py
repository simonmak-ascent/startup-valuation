"""Tests for SaaS module."""

import pytest

from startup_valuation.saas import (
    arr, mrr, cac, ltv_saas, net_revenue_retention,
    cac_payback_period, magic_number, rule_of_40, saas_revenue_multiple_valuation,
)


def test_arr():
    result = arr([100_000, 200_000, 300_000])
    assert result.value == pytest.approx(600_000)


def test_mrr():
    result = mrr(1_200_000)
    assert result.value == pytest.approx(100_000)


def test_cac():
    result = cac(500_000, 100)
    assert result.value == pytest.approx(5_000)


def test_ltv_saas():
    result = ltv_saas(100, 0.80, 0.05)
    assert result.value == pytest.approx(1_600)


def test_net_revenue_retention():
    result = net_revenue_retention(1_000_000, 1_100_000)
    assert result.value == pytest.approx(1.1)


def test_cac_payback_period():
    result = cac_payback_period(5_000, 500, 0.80)
    assert result.value == pytest.approx(12.5)


def test_magic_number():
    result = magic_number(300_000, 200_000)
    assert result.value == pytest.approx(1.5)


def test_rule_of_40():
    result = rule_of_40(1.18, 0.01)
    assert round(result.value, 2) == pytest.approx(1.19)


def test_saas_revenue_multiple_valuation():
    result = saas_revenue_multiple_valuation(400_000_000, 23)
    assert result.value == pytest.approx(9_200_000_000)
