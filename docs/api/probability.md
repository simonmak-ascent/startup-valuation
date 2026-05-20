# Probability Module

??? example "expected_value_discrete"
    ```python
    from startup_valuation.probability import expected_value_discrete

    result = expected_value_discrete(
        outcomes=[1_000_000, 5_000_000, 10_000_000],
        probabilities=[0.20, 0.60, 0.20],
    )
    print(f"Expected value: ${result.value:,.0f}")  # $5,200,000
    ```

??? example "expected_value_continuous"
    ```python
    import scipy.stats
    from startup_valuation.probability import expected_value_continuous

    result = expected_value_continuous(
        pdf_func=scipy.stats.norm(0, 1).pdf,
        lower=-10,
        upper=10,
    )
    print(f"Expected value: {result.value:.4f}")  # 0.0000
    ```

??? example "joint_probability"
    ```python
    from startup_valuation.probability import joint_probability

    result = joint_probability([0.80, 0.70, 0.90])
    print(f"Joint probability: {result.value:.4f}")  # 0.5040
    ```

??? example "probability_weighted_value"
    ```python
    from startup_valuation.probability import probability_weighted_value

    result = probability_weighted_value(
        probabilities=[0.10, 0.70, 0.20],
        values=[0, 5_000_000, 20_000_000],
    )
    print(f"Weighted value: ${result.value:,.0f}")  # $7,500,000
    ```

??? example "portfolio_expected_return"
    ```python
    from startup_valuation.probability import portfolio_expected_return

    result = portfolio_expected_return(
        probabilities=[0.10, 0.60, 0.20, 0.10],
        returns=[-1.00, 0.10, 0.50, 2.00],
    )
    print(f"Expected return: {result.value:.2%}")  # 15.00%
    ```

??? example "poisson_probability"
    ```python
    from startup_valuation.probability import poisson_probability

    result = poisson_probability(lambda_rate=3, k=2)
    print(f"P(X=2) with λ=3: {result.value:.4f}")  # 0.2240
    ```

::: startup_valuation.probability
