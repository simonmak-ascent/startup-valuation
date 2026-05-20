# Fintech Module

??? example "payment_revenue"
    ```python
    from startup_valuation.fintech import payment_revenue

    result = payment_revenue(transaction_volume=1_000_000_000, take_rate=0.02)
    print(f"Revenue: ${result.value:,.0f}")  # $20,000,000
    ```

??? example "max_loan_portfolio"
    ```python
    from startup_valuation.fintech import max_loan_portfolio

    result = max_loan_portfolio(equity=10_000_000, capital_ratio=0.10)
    print(f"Max portfolio: ${result.value:,.0f}")  # $100,000,000
    ```

??? example "network_effects_value"
    ```python
    from startup_valuation.fintech import network_effects_value

    result = network_effects_value(users=1_000_000, alpha=1.5, k=0.01)
    print(f"Network value: ${result.value:,.0f}")
    ```

??? example "lending_fintech_valuation"
    ```python
    from startup_valuation.fintech import lending_fintech_valuation

    result = lending_fintech_valuation(
        loan_book=500_000_000, roe=0.15, pe_multiple=12, npl_reserves=10_000_000,
    )
    print(f"Valuation: ${result.value:,.0f}")  # $890,000,000
    ```

??? example "payment_processor_valuation"
    ```python
    from startup_valuation.fintech import payment_processor_valuation

    result = payment_processor_valuation(
        transaction_volume=1_000_000_000, take_rate=0.02,
        growth_rate=0.20, discount_rate=0.12, terminal_multiple=15, years=5,
    )
    print(f"Valuation: ${result.value:,.0f}")
    ```

??? example "neobank_valuation"
    ```python
    from startup_valuation.fintech import neobank_valuation

    result = neobank_valuation(
        customers=500_000, arpu=100, gross_margin=0.60,
        churn_rate=0.10, pe_multiple=15,
    )
    print(f"Neobank value: ${result.value:,.0f}")  # $45,000,000
    ```

::: startup_valuation.fintech
