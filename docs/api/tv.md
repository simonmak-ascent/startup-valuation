# Time Value Module

??? example "present_value"
    ```python
    from startup_valuation.tv import present_value

    result = present_value(future_value=1_000_000, rate=0.10, periods=5)
    print(f"Present value: ${result.value:,.0f}")  # $620,921
    ```

??? example "net_present_value"
    ```python
    from startup_valuation.tv import net_present_value

    result = net_present_value(
        cash_flows=[-1_000_000, 300_000, 400_000, 500_000, 600_000],
        rate=0.10,
    )
    print(f"NPV: ${result.value:,.0f}")  # $348,941
    ```

??? example "annuity_present_value"
    ```python
    from startup_valuation.tv import annuity_present_value

    result = annuity_present_value(payment=100_000, rate=0.08, periods=10)
    print(f"Annuity PV: ${result.value:,.0f}")  # $671,008
    ```

::: startup_valuation.tv
