# Biotech Module

??? example "rnPV"
    ```python
    from startup_valuation.biotech import rnPV

    result = rnPV(
        cash_flows=[0, 0, 50_000_000, 100_000_000],
        probabilities=[1.0, 0.60, 0.30, 0.15],
        discount_rate=0.12,
    )
    print(f"rNPV: ${result.value:,.0f}")
    ```

??? example "decision_tree_ev"
    ```python
    from startup_valuation.biotech import decision_tree_ev

    result = decision_tree_ev(
        probabilities=[0.60, 0.40, 0.20],
        terminal_value=500_000_000,
    )
    print(f"Decision tree EV: ${result.value:,.0f}")  # $24,000,000
    ```

??? example "peak_sales"
    ```python
    from startup_valuation.biotech import peak_sales

    result = peak_sales(
        patient_population=1_000_000, penetration=0.10,
        price=10_000, compliance=0.80,
    )
    print(f"Peak sales: ${result.value:,.0f}")  # $800,000,000
    ```

??? example "pipeline_valuation"
    ```python
    from startup_valuation.biotech import pipeline_valuation

    drugs = [
        {"peak_sales": 500_000_000, "multiple": 3, "p_success": 0.10, "years_to_peak": 8},
        {"peak_sales": 200_000_000, "multiple": 2, "p_success": 0.30, "years_to_peak": 5},
    ]
    result = pipeline_valuation(drugs, discount_rate=0.12)
    print(f"Pipeline value: ${result.value:,.0f}")
    ```

??? example "overall_success_probability"
    ```python
    from startup_valuation.biotech import overall_success_probability

    result = overall_success_probability([0.60, 0.40, 0.20])
    print(f"Overall success: {result.value:.2%}")  # 4.80%
    ```

::: startup_valuation.biotech
