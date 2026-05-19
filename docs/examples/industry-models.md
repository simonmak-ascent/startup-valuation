# Industry-Specific Valuation Models

## SaaS: LTV and Rule of 40

```python
from startup_valuation.saas import ltv_saas, rule_of_40

ltv = ltv_saas(arpu=100, gross_margin=0.80, churn_rate=0.05)
print(f"LTV: ${ltv.value:,.0f}")  # $1,600

rule = rule_of_40(growth_rate=0.50, profit_margin=0.10)
print(f"Rule of 40: {rule.value:.0%}")  # 60% ✓
```

## Biotech: Pipeline Valuation

```python
from startup_valuation.biotech import pipeline_valuation

drugs = [
    {"peak_sales": 2_000_000_000, "multiple": 5, "p_success": 0.60, "years_to_peak": 2},
    {"peak_sales": 500_000_000, "multiple": 4, "p_success": 0.30, "years_to_peak": 4},
]
result = pipeline_valuation(drugs, discount_rate=0.12)
print(f"Pipeline value: ${result.value:,.0f}")
```

## Marketplace: GMV and Take Rate

```python
from startup_valuation.marketplace import gmv_multiple_valuation, take_rate

tr = take_rate(revenue=2_900_000_000, gmv=24_700_000_000)
print(f"Take rate: {tr.value:.1%}")  # 11.7%

val = gmv_multiple_valuation(gmv=24_700_000_000, multiple=2.4)
print(f"Valuation: ${val.value/1e9:.1f}B")  # $59.3B
```
