# Comparables Module

??? example "pe_ratio"
    ```python
    from startup_valuation.comparables import pe_ratio

    result = pe_ratio(market_cap=1_000_000_000, net_income=100_000_000)
    print(f"P/E ratio: {result.value:.1f}x")  # 10.0x
    ```

??? example "ps_ratio"
    ```python
    from startup_valuation.comparables import ps_ratio

    result = ps_ratio(market_cap=500_000_000, revenue=50_000_000)
    print(f"P/S ratio: {result.value:.1f}x")  # 10.0x
    ```

??? example "ev_ebitda"
    ```python
    from startup_valuation.comparables import ev_ebitda

    result = ev_ebitda(enterprise_value=1_000_000_000, ebitda=150_000_000)
    print(f"EV/EBITDA: {result.value:.1f}x")  # 6.7x
    ```

??? example "ev_revenue"
    ```python
    from startup_valuation.comparables import ev_revenue

    result = ev_revenue(enterprise_value=500_000_000, revenue=50_000_000)
    print(f"EV/Revenue: {result.value:.1f}x")  # 10.0x
    ```

??? example "regression_adjusted_multiple"
    ```python
    from startup_valuation.comparables import regression_adjusted_multiple

    result = regression_adjusted_multiple(
        intercept=5.0, growth_rate=0.30, growth_coefficient=10.0,
        market_maturity=0.5, maturity_coefficient=-2.0,
    )
    print(f"Adjusted multiple: {result.value:.1f}x")  # 7.0x
    ```

??? example "target_valuation_multiple"
    ```python
    from startup_valuation.comparables import target_valuation_multiple

    result = target_valuation_multiple(multiple=8.0, metric=50_000_000)
    print(f"Valuation: ${result.value:,.0f}")  # $400,000,000
    ```

::: startup_valuation.comparables
