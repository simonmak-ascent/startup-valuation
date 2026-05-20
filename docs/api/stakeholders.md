# Stakeholders Module

??? example "single_round_dilution"
    ```python
    from startup_valuation.stakeholders import single_round_dilution

    result = single_round_dilution(
        ownership_before=1.0, investment=5_000_000, post_money=50_000_000,
    )
    print(f"Ownership after: {result.value:.0%}")  # 90%
    ```

??? example "multi_round_dilution"
    ```python
    from startup_valuation.stakeholders import multi_round_dilution

    rounds = [
        {"investment": 2_000_000, "post_money": 20_000_000},
        {"investment": 5_000_000, "post_money": 50_000_000},
        {"investment": 10_000_000, "post_money": 100_000_000},
    ]
    result = multi_round_dilution(ownership_before=1.0, rounds=rounds)
    print(f"Final ownership: {result.value:.0%}")  # 76.5%
    ```

??? example "acquisition_value"
    ```python
    from startup_valuation.stakeholders import acquisition_value

    result = acquisition_value(
        standalone_value=100_000_000, synergies=30_000_000,
        integration_costs=5_000_000,
    )
    print(f"Acquisition value: ${result.value:,.0f}")  # $125,000,000
    ```

??? example "opm_common_stock"
    ```python
    from startup_valuation.stakeholders import opm_common_stock

    result = opm_common_stock(
        enterprise_value=100_000_000, liquidation_preference=50_000_000,
        time_to_exit=5.0, volatility=0.40, risk_free_rate=0.04,
    )
    print(f"Common stock value: ${result.value:,.0f}")
    ```

??? example "pwerm"
    ```python
    from startup_valuation.stakeholders import pwerm

    scenarios = [
        {"probability": 0.20, "common_value": 80_000_000},
        {"probability": 0.60, "common_value": 40_000_000},
        {"probability": 0.20, "common_value": 0},
    ]
    result = pwerm(scenarios)
    print(f"PWERM value: ${result.value:,.0f}")  # $40,000,000
    ```

??? example "liquidation_value"
    ```python
    from startup_valuation.stakeholders import liquidation_value

    assets = {"cash": 5_000_000, "ar": 10_000_000, "inventory": 8_000_000}
    recovery_rates = {"cash": 1.0, "ar": 0.80, "inventory": 0.40}
    result = liquidation_value(assets, recovery_rates)
    print(f"Liquidation: ${result.value:,.0f}")  # $16,200,000
    ```

??? example "risk_adjusted_synergy"
    ```python
    from startup_valuation.stakeholders import risk_adjusted_synergy

    result = risk_adjusted_synergy(
        revenue_synergies=20_000_000, cost_synergies=10_000_000,
        prob_revenue=0.40, prob_cost=0.80, discount_rate=0.10, years=3,
    )
    print(f"Risk-adjusted synergy: ${result.value:,.0f}")
    ```

??? example "intrinsic_option_value"
    ```python
    from startup_valuation.stakeholders import intrinsic_option_value

    result = intrinsic_option_value(
        strike_price=10, fair_market_value=25, shares=100_000,
    )
    print(f"Intrinsic value: ${result.value:,.0f}")  # $1,500,000
    ```

??? example "probability_weighted_employee_value"
    ```python
    from startup_valuation.stakeholders import probability_weighted_employee_value

    scenarios = [
        {"probability": 0.10, "value_per_share": 50},
        {"probability": 0.60, "value_per_share": 20},
        {"probability": 0.30, "value_per_share": 0},
    ]
    result = probability_weighted_employee_value(scenarios, shares=10_000)
    print(f"Expected value: ${result.value:,.0f}")  # $170,000
    ```

??? example "vesting_adjusted_value"
    ```python
    from startup_valuation.stakeholders import vesting_adjusted_value

    result = vesting_adjusted_value(
        total_value=1_000_000, vested_fraction=0.25,
        annual_vest_rate=0.25, retention_prob=0.80, years_remaining=3,
    )
    print(f"Vesting-adjusted: ${result.value:,.0f}")
    ```

??? example "cash_equity_breakeven"
    ```python
    from startup_valuation.stakeholders import cash_equity_breakeven

    result = cash_equity_breakeven(
        salary_reduction=50_000, equity_value=500_000,
        tax_rate=0.30, discount_rate=0.20, years=4,
    )
    print(f"Breakeven equity: {result.value:.0%}")
    ```

??? example "max_asset_based_loan"
    ```python
    from startup_valuation.stakeholders import max_asset_based_loan

    result = max_asset_based_loan(
        cash=5_000_000, accounts_receivable=10_000_000,
        inventory=8_000_000, equipment=20_000_000, real_estate=50_000_000,
    )
    print(f"Max loan: ${result.value:,.0f}")
    ```

??? example "venture_debt_dilution"
    ```python
    from startup_valuation.stakeholders import venture_debt_dilution

    result = venture_debt_dilution(
        loan_amount=5_000_000, warrant_coverage=0.20, post_money=50_000_000,
    )
    print(f"Dilution: {result.value:.2%}")  # 2.00%
    ```

??? example "common_stock_discount"
    ```python
    from startup_valuation.stakeholders import common_stock_discount

    result = common_stock_discount(
        enterprise_value=100_000_000, liquidation_preference=50_000_000,
        time_to_exit=5.0, volatility=0.40, risk_free_rate=0.04,
    )
    print(f"Common discount: {result.value:.0%}")
    ```

::: startup_valuation.stakeholders
