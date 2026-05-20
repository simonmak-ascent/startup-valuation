# SaaS Module

??? example "arr"
    ```python
    from startup_valuation.saas import arr

    result = arr(monthly_recurring_revenue=100_000)
    print(f"ARR: ${result.value:,.0f}")  # $1,200,000
    ```

??? example "mrr"
    ```python
    from startup_valuation.saas import mrr

    result = mrr(customers=500, arpu=200)
    print(f"MRR: ${result.value:,.0f}")  # $100,000
    ```

??? example "cac"
    ```python
    from startup_valuation.saas import cac

    result = cac(marketing_spend=100_000, new_customers=200)
    print(f"CAC: ${result.value:,.0f}")  # $500
    ```

??? example "ltv_saas"
    ```python
    from startup_valuation.saas import ltv_saas

    result = ltv_saas(arpu=200, gross_margin=0.80, churn_rate=0.05)
    print(f"LTV: ${result.value:,.0f}")  # $3,200
    ```

??? example "net_revenue_retention"
    ```python
    from startup_valuation.saas import net_revenue_retention

    result = net_revenue_retention(revenue_start=1_000_000, revenue_end=1_200_000)
    print(f"NRR: {result.value:.0%}")  # 120%
    ```

??? example "cac_payback_period"
    ```python
    from startup_valuation.saas import cac_payback_period

    result = cac_payback_period(cac=500, mrr=200, gross_margin=0.80)
    print(f"Payback: {result.value:.1f} months")  # 3.1 months
    ```

??? example "magic_number"
    ```python
    from startup_valuation.saas import magic_number

    result = magic_number(net_new_arr=300_000, sales_marketing_expense=200_000)
    print(f"Magic number: {result.value:.2f}")  # 1.50
    ```

??? example "rule_of_40"
    ```python
    from startup_valuation.saas import rule_of_40

    result = rule_of_40(growth_rate=0.30, profit_margin=0.15)
    print(f"Rule of 40: {result.value:.0%}")  # 45%
    ```

??? example "saas_revenue_multiple_valuation"
    ```python
    from startup_valuation.saas import saas_revenue_multiple_valuation

    result = saas_revenue_multiple_valuation(arr=1_200_000, multiple=10)
    print(f"Valuation: ${result.value:,.0f}")  # $12,000,000
    ```

::: startup_valuation.saas
