# Marketplace Module

??? example "gmv"
    ```python
    from startup_valuation.marketplace import gmv

    result = gmv(transactions=10_000, average_order_value=100)
    print(f"GMV: ${result.value:,.0f}")  # $1,000,000
    ```

??? example "take_rate"
    ```python
    from startup_valuation.marketplace import take_rate

    result = take_rate(revenue=200_000, gmv=10_000_000)
    print(f"Take rate: {result.value:.2%}")  # 2.00%
    ```

??? example "liquidity"
    ```python
    from startup_valuation.marketplace import liquidity

    result = liquidity(successful_attempts=800, total_attempts=1_000)
    print(f"Liquidity: {result.value:.0%}")  # 80%
    ```

??? example "gmv_multiple_valuation"
    ```python
    from startup_valuation.marketplace import gmv_multiple_valuation

    result = gmv_multiple_valuation(gmv=100_000_000, multiple=2)
    print(f"Valuation: ${result.value:,.0f}")  # $200,000,000
    ```

??? example "network_value"
    ```python
    from startup_valuation.marketplace import network_value

    result = network_value(users=1_000_000, alpha=1.5, k=0.01)
    print(f"Network value: ${result.value:,.0f}")
    ```

??? example "buyer_retention"
    ```python
    from startup_valuation.marketplace import buyer_retention

    result = buyer_retention(buyers_period_1=1_000, buyers_repeat=600)
    print(f"Buyer retention: {result.value:.0%}")  # 60%
    ```

??? example "network_density"
    ```python
    from startup_valuation.marketplace import network_density

    result = network_density(active_buyers=500, active_sellers=300, total_users=1_000)
    print(f"Network density: {result.value:.4f}")
    ```

::: startup_valuation.marketplace
