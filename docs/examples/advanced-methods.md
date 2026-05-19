# Advanced Valuation Methods

## Black-Scholes for Real Options

```python
from startup_valuation.advanced import black_scholes

result = black_scholes(
    underlying=20_000_000,
    strike=5_000_000,
    risk_free_rate=0.05,
    volatility=0.40,
    time_to_maturity=1.0,
)
print(f"Option value: ${result.value:,.0f}")  # $15,240,000
```

## Scenario Analysis

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
