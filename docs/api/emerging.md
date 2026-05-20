# Emerging Module

??? example "safe_conversion_discount"
    ```python
    from startup_valuation.emerging import safe_conversion_discount

    result = safe_conversion_discount(series_a_price=1.00, discount=0.20)
    print(f"SAFE price: ${result.value:.2f}")  # $0.80
    ```

??? example "safe_conversion_cap"
    ```python
    from startup_valuation.emerging import safe_conversion_cap

    result = safe_conversion_cap(cap=10_000_000, series_a_price=1.00)
    print(f"Cap price: ${result.value:.2f}")
    ```

??? example "safe_expected_value"
    ```python
    from startup_valuation.emerging import safe_expected_value

    result = safe_expected_value(
        investment=1_000_000, cap=10_000_000, discount=0.20,
        series_a_valuation=20_000_000, series_a_price=1.00,
    )
    print(f"Expected SAFE value: ${result.value:,.0f}")
    ```

??? example "equation_of_exchange"
    ```python
    from startup_valuation.emerging import equation_of_exchange

    result = equation_of_exchange(
        transaction_volume=1_000_000, price_per_tx=100,
        velocity=10, supply=10_000_000,
    )
    print(f"Token value: ${result.value:.2f}")
    ```

??? example "nvt_ratio"
    ```python
    from startup_valuation.emerging import nvt_ratio

    result = nvt_ratio(market_cap=1_000_000_000, daily_transaction_volume=50_000_000)
    print(f"NVT ratio: {result.value:.1f}")  # 20.0
    ```

??? example "protocol_value"
    ```python
    from startup_valuation.emerging import protocol_value

    result = protocol_value(tvl=500_000_000, multiple=3)
    print(f"Protocol value: ${result.value:,.0f}")  # $1,500,000,000
    ```

??? example "esg_adjusted_discount_rate"
    ```python
    from startup_valuation.emerging import esg_adjusted_discount_rate

    result = esg_adjusted_discount_rate(
        base_rate=0.12, risk_premium=0.02, opp_discount=0.01,
    )
    print(f"ESG-adjusted rate: {result.value:.2%}")  # 13.00%
    ```

??? example "esg_premium_valuation"
    ```python
    from startup_valuation.emerging import esg_premium_valuation

    result = esg_premium_valuation(
        base_valuation=100_000_000, esg_score=8, premium_per_point=0.02,
    )
    print(f"ESG premium value: ${result.value:,.0f}")  # $116,000,000
    ```

??? example "esg_discount_valuation"
    ```python
    from startup_valuation.emerging import esg_discount_valuation

    result = esg_discount_valuation(
        base_valuation=100_000_000, esg_risk_score=5, discount_per_point=0.01,
    )
    print(f"ESG discount value: ${result.value:,.0f}")  # $95,000,000
    ```

??? example "metcalfes_law"
    ```python
    from startup_valuation.emerging import metcalfes_law

    result = metcalfes_law(n=1_000_000, k=0.00001)
    print(f"Network value: ${result.value:,.0f}")  # $10,000,000
    ```

??? example "modified_metcalfes"
    ```python
    from startup_valuation.emerging import modified_metcalfes

    result = modified_metcalfes(n=1_000_000, k=0.00001, alpha=1.5)
    print(f"Modified value: ${result.value:,.0f}")
    ```

??? example "network_density_valuation"
    ```python
    from startup_valuation.emerging import network_density_valuation

    result = network_density_valuation(
        users=1_000_000, connections=500_000, value_per_connection=10,
    )
    print(f"Network density value: ${result.value:,.0f}")
    ```

??? example "remote_cost_savings_npv"
    ```python
    from startup_valuation.emerging import remote_cost_savings_npv

    result = remote_cost_savings_npv(annual_savings=500_000, discount_rate=0.10)
    print(f"Savings NPV: ${result.value:,.0f}")  # $5,000,000
    ```

??? example "data_moat_value"
    ```python
    from startup_valuation.emerging import data_moat_value

    result = data_moat_value(
        data_volume=1_000_000, data_uniqueness=0.80, monetization_rate=0.05,
        competitive_advantage_years=5, discount_rate=0.15,
    )
    print(f"Data moat value: ${result.value:,.0f}")
    ```

??? example "remote_first_premium"
    ```python
    from startup_valuation.emerging import remote_first_premium

    result = remote_first_premium(
        base_valuation=100_000_000, cost_savings_pct=0.20,
        talent_access_premium=0.10, productivity_gain=0.05,
    )
    print(f"Remote-first value: ${result.value:,.0f}")  # $135,000,000
    ```

::: startup_valuation.emerging
