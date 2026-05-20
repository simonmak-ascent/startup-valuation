"""Tests for biotech module."""

import pytest

from startup_valuation.biotech import (
    decision_tree_ev,
    overall_success_probability,
    peak_sales,
    pipeline_valuation,
    rnPV,
)


def test_rnPV():  # noqa: N802
    result = rnPV(
        cash_flows=[0, 0, 50_000_000, 100_000_000],
        probabilities=[0.35, 0.21, 0.19, 0.19],
        discount_rate=0.12,
        development_costs=10_000_000,
    )
    assert result.value > 0


def test_decision_tree_ev():
    result = decision_tree_ev([0.35, 0.60, 0.90], 500_000_000)
    assert result.value == pytest.approx(94_500_000)


def test_peak_sales():
    result = peak_sales(50_000, 0.40, 150_000, 0.90)
    assert result.value == pytest.approx(2_700_000_000)


def test_pipeline_valuation():
    drugs = [{"peak_sales": 2_000_000_000, "multiple": 5, "p_success": 0.60, "years_to_peak": 2}]
    result = pipeline_valuation(drugs, 0.12)
    assert round(result.value / 1_000_000_000, 2) == pytest.approx(4.78, abs=0.05)


def test_overall_success_probability():
    result = overall_success_probability([0.35, 0.60, 0.90])
    assert round(result.value, 4) == pytest.approx(0.189, abs=0.001)
