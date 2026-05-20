# Hardware Module

??? example "trl_adjusted_valuation"
    ```python
    from startup_valuation.hardware import trl_adjusted_valuation

    result = trl_adjusted_valuation(
        market_size=1_000_000_000, market_share=0.05,
        margin=0.30, multiple=5, trl_discount=0.40,
    )
    print(f"TRL-adjusted: ${result.value:,.0f}")  # $45,000,000
    ```

??? example "gross_margin_hardware"
    ```python
    from startup_valuation.hardware import gross_margin_hardware

    result = gross_margin_hardware(asp=500, cogs=200)
    print(f"Gross margin: {result.value:.0%}")  # 60%
    ```

??? example "break_even_volume"
    ```python
    from startup_valuation.hardware import break_even_volume

    result = break_even_volume(fixed_costs=1_000_000, asp=500, variable_cost=200)
    print(f"Break-even volume: {result.value:,.0f} units")  # 3,333 units
    ```

??? example "probability_weighted_dcf"
    ```python
    from startup_valuation.hardware import probability_weighted_dcf

    scenarios = [
        {"probability": 0.20, "cash_flows": [0, 0, 50_000_000, 100_000_000]},
        {"probability": 0.60, "cash_flows": [0, 0, 20_000_000, 40_000_000]},
        {"probability": 0.20, "cash_flows": [0, 0, -10_000_000, 0]},
    ]
    result = probability_weighted_dcf(scenarios, discount_rate=0.15)
    print(f"Expected value: ${result.value:,.0f}")
    ```

::: startup_valuation.hardware
