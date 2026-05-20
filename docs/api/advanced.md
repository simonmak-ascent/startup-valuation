# Advanced Module

??? example "black_scholes"
    ```python
    from startup_valuation.advanced import black_scholes

    result = black_scholes(
        underlying=20_000_000, strike=5_000_000,
        risk_free_rate=0.05, volatility=0.40, time_to_maturity=1.0,
    )
    print(f"Option value: ${result.value:,.0f}")  # $15,244,009
    ```

??? example "binomial_tree"
    ```python
    from startup_valuation.advanced import binomial_tree

    result = binomial_tree(
        underlying=100, strike=100, risk_free_rate=0.05,
        volatility=0.20, time_to_maturity=1.0, steps=3,
    )
    print(f"Binomial value: ${result.value:.2f}")
    ```

??? example "binomial_valuation"
    ```python
    from startup_valuation.advanced import binomial_valuation

    result = binomial_valuation(
        underlying=20_000_000, strike=5_000_000,
        risk_free_rate=0.05, volatility=0.40, time_to_maturity=1.0,
        steps=50,
    )
    print(f"High-res binomial: ${result.value:,.0f}")
    ```

??? example "monte_carlo_valuation"
    ```python
    from startup_valuation.advanced import monte_carlo_valuation
    from startup_valuation.types import Distribution

    result = monte_carlo_valuation(
        market_size_dist=Distribution("normal", {"mean": 1_000_000_000, "sd": 200_000_000}),
        market_share_dist=Distribution("uniform", {"min": 0.01, "max": 0.05}),
        margin_dist=Distribution("triangular", {"min": 0.20, "mode": 0.40, "max": 0.60}),
        exit_multiple=8, discount_rate=0.15, years=5, num_simulations=10_000,
    )
    print(f"Monte Carlo: ${result.value:,.0f}")
    ```

??? example "scenario_analysis"
    ```python
    from startup_valuation.advanced import scenario_analysis
    from startup_valuation.types import Scenario

    scenarios = [
        Scenario("bull", 0.20, 10_000_000),
        Scenario("base", 0.60, 5_000_000),
        Scenario("bear", 0.20, 1_000_000),
    ]
    result = scenario_analysis(scenarios)
    print(f"Expected value: ${result.value:,.0f}")  # $5,200,000
    ```

??? example "ltv_cac_valuation"
    ```python
    from startup_valuation.advanced import ltv_cac_valuation
    from startup_valuation.types import Distribution

    result = ltv_cac_valuation(
        ltv_dist=Distribution("normal", {"mean": 5_000, "sd": 1_000}),
        cac_dist=Distribution("normal", {"mean": 500, "sd": 100}),
        market_size_dist=Distribution("normal", {"mean": 100_000, "sd": 20_000}),
        num_simulations=10_000,
    )
    print(f"LTV/CAC valuation: ${result.value:,.0f}")
    ```

::: startup_valuation.advanced
