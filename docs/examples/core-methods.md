# Core Valuation Methods

## Scorecard Method

```python
from startup_valuation.core import scorecard_valuation

result = scorecard_valuation(
    average_valuation=1_500_000,
    weights=[0.30, 0.25, 0.15, 0.10, 0.10, 0.05, 0.05],
    scores=[1.25, 1.50, 1.20, 0.75, 1.00, 0.90, 1.00],
)
print(f"Scorecard: ${result.value:,.0f}")  # $1,800,000
```

## Berkus Method

```python
from startup_valuation.core import berkus_valuation

result = berkus_valuation(
    sound_idea=500_000,
    prototype=400_000,
    quality_team=500_000,
    strategic_relationships=500_000,
    product_rollout=0,
)
print(f"Berkus: ${result.value:,.0f}")  # $1,900,000
```

## VC Method

```python
from startup_valuation.core import vc_method_post_money, vc_method_pre_money

post = vc_method_post_money(terminal_value=500_000_000, target_return=10)
pre = vc_method_pre_money(post_money=post.value, investment=1_500_000)

print(f"Post-money: ${post.value:,.0f}")  # $50,000,000
print(f"Pre-money: ${pre.value:,.0f}")   # $48,500,000
```
