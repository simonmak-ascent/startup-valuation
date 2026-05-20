# CAPM Module

??? example "capm"
    ```python
    from startup_valuation.capm import capm

    result = capm(risk_free_rate=0.04, beta=1.5, market_return=0.10)
    print(f"Expected return: {result.value:.2%}")  # 13.00%
    ```

??? example "portfolio_beta"
    ```python
    from startup_valuation.capm import portfolio_beta

    result = portfolio_beta(
        weights=[0.40, 0.30, 0.30],
        betas=[1.2, 0.8, 1.5],
    )
    print(f"Portfolio beta: {result.value:.2f}")  # 1.17
    ```

??? example "startup_adjusted_capm"
    ```python
    from startup_valuation.capm import startup_adjusted_capm

    result = startup_adjusted_capm(
        risk_free_rate=0.04, beta=1.5, market_risk_premium=0.06,
        size_premium=0.03, startup_premium=0.05,
    )
    print(f"Startup CAPM: {result.value:.2%}")  # 21.00%
    ```

??? example "portfolio_variance"
    ```python
    from startup_valuation.capm import portfolio_variance
    import numpy as np

    cov_matrix = np.array([[0.04, 0.01], [0.01, 0.09]])
    result = portfolio_variance(weights=[0.60, 0.40], cov_matrix=cov_matrix)
    print(f"Portfolio variance: {result.value:.4f}")  # 0.0288
    ```

::: startup_valuation.capm
