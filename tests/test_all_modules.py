"""Tests for advanced, industry, international, stakeholders, emerging modules."""

import pytest
from startup_valuation.advanced import black_scholes, scenario_analysis
from startup_valuation.types import Scenario
from startup_valuation.saas import ltv_saas, rule_of_40, saas_revenue_multiple_valuation
from startup_valuation.biotech import decision_tree_ev, peak_sales, pipeline_valuation, overall_success_probability
from startup_valuation.fintech import payment_revenue, max_loan_portfolio, lending_fintech_valuation
from startup_valuation.marketplace import take_rate, gmv_multiple_valuation
from startup_valuation.hardware import trl_adjusted_valuation, probability_weighted_dcf
from startup_valuation.international import purchasing_power_parity, country_risk_premium, adjusted_capm_international
from startup_valuation.stakeholders import (
    single_round_dilution,
    opm_common_stock,
    pwerm,
    common_stock_discount,
    liquidation_value,
    venture_debt_dilution,
)
from startup_valuation.emerging import (
    safe_conversion_discount,
    equation_of_exchange,
    esg_adjusted_discount_rate,
    metcalfes_law,
    network_density_valuation,
    remote_cost_savings_npv,
)


# Advanced tests
def test_black_scholes():
    result = black_scholes(20_000_000, 5_000_000, 0.05, 0.40, 1.0)
    assert round(result.value / 1_000_000, 2) == pytest.approx(15.24, abs=0.1)


def test_scenario_analysis():
    scenarios = [
        Scenario("bull", 0.20, 10_000_000),
        Scenario("base", 0.60, 5_000_000),
        Scenario("bear", 0.20, 1_000_000),
    ]
    result = scenario_analysis(scenarios)
    assert result.value == pytest.approx(5_200_000)


# SaaS tests
def test_ltv_saas():
    result = ltv_saas(100, 0.80, 0.05)
    assert result.value == pytest.approx(1600)


def test_rule_of_40():
    result = rule_of_40(1.18, 0.01)
    assert round(result.value, 2) == pytest.approx(1.19)


def test_saas_revenue_multiple():
    result = saas_revenue_multiple_valuation(400_000_000, 23)
    assert result.value == pytest.approx(9_200_000_000)


# Biotech tests
def test_decision_tree_ev():
    result = decision_tree_ev([0.35, 0.60, 0.90], 500_000_000)
    assert result.value == pytest.approx(94_500_000)


def test_peak_sales():
    result = peak_sales(50_000, 0.40, 150_000, 0.90)
    assert result.value == pytest.approx(2_700_000_000)


def test_pipeline_valuation():
    drugs = [{"peak_sales": 2_000_000_000, "multiple": 5, "p_success": 0.60, "years_to_peak": 2}]
    result = pipeline_valuation(drugs, 0.12)
    assert round(result.value / 1_000_000_000, 2) == pytest.approx(4.78, abs=0.01)


def test_overall_success_probability():
    result = overall_success_probability([0.35, 0.60, 0.90])
    assert round(result.value, 4) == pytest.approx(0.189)


# Fintech tests
def test_payment_revenue():
    result = payment_revenue(640_000_000_000, 0.0116)
    assert result.value / 1_000_000_000 == pytest.approx(7.424)


def test_max_loan_portfolio():
    result = max_loan_portfolio(100_000_000, 0.08)
    assert result.value == pytest.approx(1_250_000_000)


def test_lending_fintech_valuation():
    result = lending_fintech_valuation(100_000_000, 0.15, 12)
    assert result.value == pytest.approx(180_000_000)


# Marketplace tests
def test_take_rate():
    result = take_rate(2_900_000_000, 24_700_000_000)
    assert round(result.value, 4) == pytest.approx(0.1174)


def test_gmv_multiple_valuation():
    result = gmv_multiple_valuation(24_700_000_000, 2.4)
    assert result.value / 1_000_000_000 == pytest.approx(59.28)


# Hardware tests
def test_trl_adjusted_valuation():
    result = trl_adjusted_valuation(10_000_000_000, 0.05, 0.40, 15, 0.80)
    assert result.value / 1_000_000_000 == pytest.approx(0.6)


def test_probability_weighted_dcf():
    result = probability_weighted_dcf([0.30, 0.40, 0.30], [60_000_000_000, 10_000_000_000, 0])
    assert result.value / 1_000_000_000 == pytest.approx(22.0)


# International tests
def test_purchasing_power_parity():
    result = purchasing_power_parity(83, 0.05, 0.02)
    assert round(result.value, 1) == pytest.approx(85.4)


def test_country_risk_premium():
    result = country_risk_premium(0.105, 0.045)
    assert result.value == pytest.approx(0.06)


def test_adjusted_capm_international():
    result = adjusted_capm_international(0.045, 1.2, 0.06, 0.03)
    assert round(result.value, 4) == pytest.approx(0.147)


# Stakeholders tests
def test_single_round_dilution():
    result = single_round_dilution(1.0, 5_000_000, 20_000_000)
    assert result.value == pytest.approx(0.75)


def test_opm_common_stock():
    result = opm_common_stock(100_000_000, 40_000_000, 3, 0.60)
    assert round(result.value / 1_000_000, 0) == pytest.approx(69, abs=5)


def test_pwerm():
    scenarios = [
        {"probability": 0.20, "common_value": 92_000_000},
        {"probability": 0.50, "common_value": 55_000_000},
        {"probability": 0.20, "common_value": 4_000_000},
        {"probability": 0.10, "common_value": 0},
    ]
    result = pwerm(scenarios)
    assert round(result.value / 1_000_000, 1) == pytest.approx(46.7)


def test_common_stock_discount():
    result = common_stock_discount(100_000_000, 65_000_000)
    assert result.value == pytest.approx(0.35)


def test_liquidation_value():
    assets = {"cash": 5_000_000, "ar": 3_000_000, "equipment": 2_000_000}
    rates = {"cash": 1.0, "ar": 0.80, "equipment": 0.30}
    result = liquidation_value(assets, rates)
    assert result.value == pytest.approx(8_000_000)


def test_venture_debt_dilution():
    result = venture_debt_dilution(0.10, 3_000_000, 40_000_000)
    assert result.value == pytest.approx(0.0075)


# Emerging tests
def test_safe_conversion_discount():
    result = safe_conversion_discount(5.0, 0.20)
    assert result.value == pytest.approx(4.0)


def test_equation_of_exchange():
    result = equation_of_exchange(10_000_000_000, 1, 10, 100_000_000)
    assert result.value == pytest.approx(10.0)


def test_esg_adjusted_discount_rate():
    result = esg_adjusted_discount_rate(0.15, 0.02, 0.01)
    assert result.value == pytest.approx(0.16)


def test_metcalfes_law():
    result = metcalfes_law(100_000)
    assert result.value == pytest.approx(10_000_000_000)


def test_network_density_valuation():
    result = network_density_valuation(10_000_000, 100, 1)
    assert result.value / 1_000_000_000 == pytest.approx(1.0)


def test_remote_cost_savings_npv():
    result = remote_cost_savings_npv(1_200_000, 0.10)
    assert result.value == pytest.approx(12_000_000)
