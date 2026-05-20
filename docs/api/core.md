# Core Methods Module

??? example "scorecard_valuation"
    ```python
    from startup_valuation.core import scorecard_valuation

    result = scorecard_valuation(
        average_valuation=1_500_000,
        weights=[0.30, 0.25, 0.15, 0.10, 0.10, 0.05, 0.05],
        scores=[1.25, 1.50, 1.20, 0.75, 1.00, 0.90, 1.00],
    )
    print(f"Scorecard: ${result.value:,.0f}")  # $1,800,000
    ```

??? example "berkus_valuation"
    ```python
    from startup_valuation.core import berkus_valuation

    result = berkus_valuation(
        sound_idea=500_000, prototype=400_000, quality_team=500_000,
        strategic_relationships=500_000, product_rollout=0,
    )
    print(f"Berkus: ${result.value:,.0f}")  # $1,900,000
    ```

??? example "risk_factor_summation"
    ```python
    from startup_valuation.core import risk_factor_summation

    result = risk_factor_summation(
        base_valuation=2_000_000,
        risk_ratings=[1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    )
    print(f"Risk-adjusted: ${result.value:,.0f}")  # $2,750,000
    ```

??? example "vc_method_post_money"
    ```python
    from startup_valuation.core import vc_method_post_money

    result = vc_method_post_money(terminal_value=500_000_000, target_return=10)
    print(f"Post-money: ${result.value:,.0f}")  # $50,000,000
    ```

??? example "vc_method_pre_money"
    ```python
    from startup_valuation.core import vc_method_pre_money

    result = vc_method_pre_money(post_money=50_000_000, investment=5_000_000)
    print(f"Pre-money: ${result.value:,.0f}")  # $45,000,000
    ```

??? example "terminal_value_multiple"
    ```python
    from startup_valuation.core import terminal_value_multiple

    result = terminal_value_multiple(projected_revenue=20_000_000, multiple=8)
    print(f"Terminal value: ${result.value:,.0f}")  # $160,000,000
    ```

::: startup_valuation.core
