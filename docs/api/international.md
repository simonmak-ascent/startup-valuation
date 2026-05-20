# International Module

??? example "purchasing_power_parity"
    ```python
    from startup_valuation.international import purchasing_power_parity

    result = purchasing_power_parity(
        spot_rate=7.80, inflation_foreign=0.03, inflation_domestic=0.02,
    )
    print(f"PPP rate: {result.value:.4f}")  # 7.8765
    ```

??? example "interest_rate_parity"
    ```python
    from startup_valuation.international import interest_rate_parity

    result = interest_rate_parity(
        spot_rate=1.10, rate_foreign=0.02, rate_domestic=0.04,
    )
    print(f"Forward rate: {result.value:.4f}")  # 1.0788
    ```

??? example "currency_adjusted_dcf"
    ```python
    from startup_valuation.international import currency_adjusted_dcf

    cash_flows_local = [0, 10_000_000, 20_000_000, 30_000_000]
    exchange_rates = [7.80, 7.85, 7.90, 7.95]
    result = currency_adjusted_dcf(cash_flows_local, exchange_rates, discount_rate=0.10)
    print(f"USD PV: ${result.value:,.0f}")
    ```

??? example "country_risk_premium"
    ```python
    from startup_valuation.international import country_risk_premium

    result = country_risk_premium(sovereign_yield=0.06, us_treasury_yield=0.04)
    print(f"CRP: {result.value:.2%}")  # 2.00%
    ```

??? example "country_risk_premium_damodaran"
    ```python
    from startup_valuation.international import country_risk_premium_damodaran

    result = country_risk_premium_damodaran(
        default_spread=0.02, equity_volatility=0.25, bond_volatility=0.10,
    )
    print(f"Damodaran CRP: {result.value:.2%}")  # 5.00%
    ```

??? example "adjusted_capm_international"
    ```python
    from startup_valuation.international import adjusted_capm_international

    result = adjusted_capm_international(
        risk_free_rate=0.04, beta=1.2, mrp=0.06, crp=0.03,
    )
    print(f"International CAPM: {result.value:.2%}")  # 14.20%
    ```

??? example "after_tax_cash_flow"
    ```python
    from startup_valuation.international import after_tax_cash_flow

    result = after_tax_cash_flow(
        pre_tax_cash_flow=10_000_000, tax_local=0.25, tax_withholding=0.10,
    )
    print(f"After-tax: ${result.value:,.0f}")  # $6,750,000
    ```

??? example "sum_of_parts_valuation"
    ```python
    from startup_valuation.international import sum_of_parts_valuation

    markets = [
        {"value": 100_000_000, "p_success": 0.60},
        {"value": 50_000_000, "p_success": 0.40},
        {"value": 20_000_000, "p_success": 0.20},
    ]
    result = sum_of_parts_valuation(markets)
    print(f"Sum of parts: ${result.value:,.0f}")  # $84,000,000
    ```

::: startup_valuation.international
