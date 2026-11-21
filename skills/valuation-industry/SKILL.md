---
name: valuation-industry
description: >-
  Industry models priced on the metrics their vertical actually uses: SaaS, marketplace, fintech, biotech and hardware. Use once revenue exists and the business model is known.
license: MIT
---

# Skill: Valuation Industry Methods

Industry-specific methods: SaaS, Biotech, Fintech, Marketplace, Hardware.

## When to Use

Select method based on the startup's industry:

| Industry | Key Metrics | Primary Method |
|----------|------------|----------------|
| SaaS | ARR, LTV, CAC, NRR, Churn | Revenue multiple, LTV/CAC |
| Biotech | Clinical stages, peak sales | rNPV, decision tree, pipeline |
| Fintech | Transaction volume, take rate | Payment revenue, lending valuation |
| Marketplace | GMV, liquidity, take rate | GMV multiple, network effects |
| Hardware | TRL, COGS, break-even | TRL-adjusted, probability-weighted DCF |

## Workflow

### Step 1: Identify Industry
Ask the user about the startup's business model and revenue type.

### Step 2: Gather Industry-Specific Metrics
- SaaS: ARR, gross margin, churn rate, CAC
- Biotech: Stage probabilities, peak sales estimate, development costs
- Fintech: Transaction volume, take rate, capital requirements
- Marketplace: GMV, take rate, active users
- Hardware: TRL level, ASP, COGS, fixed costs

### Step 3: Calculate
Use appropriate MCP tools (see MCP Tools section below for full signatures by industry).

### Step 4: Interpret
Compare results to industry benchmarks. Flag if metrics are outside normal ranges.

## MCP Tools

Each tool takes `method` plus that method's own parameters — the arguments below are the ones
the tool validates, and an unknown method or a missing parameter returns an error instead of a value.

### `valuation_saas`

SaaS unit economics and valuation: LTV, CAC, MRR, ARR, net revenue retention, magic number, Rule of 40, CAC payback, and ARR revenue-multiple valuation.

- `method: "ltv"` — arpu, gross_margin, churn_rate
- `method: "cac"` — sales_marketing_expense, new_customers
- `method: "mrr"` — arr_value
- `method: "arr"` — subscription_values
- `method: "nrr"` — starting_revenue, ending_revenue (optional: expansion_revenue)
- `method: "magic_number"` — net_new_arr, sm_expense_prior
- `method: "rule_of_40"` — growth_rate, profit_margin
- `method: "cac_payback"` — cac, mrr_per_customer, gross_margin
- `method: "revenue_multiple"` — arr, revenue_multiple

### `valuation_biotech`

Risk-adjusted biotech valuation: peak sales, decision-tree expected value, and full pipeline rNPV across drugs.

- `method: "peak_sales"` — patient_population, penetration, price (optional: compliance)
- `method: "decision_tree"` — probabilities, terminal_value
- `method: "pipeline"` — drugs, discount_rate

### `valuation_fintech`

Value and size fintech business models: payment revenue, lending valuation, payment-processor DCF, and neobank customer-based valuation.

- `method: "payment_revenue"` — transaction_volume, take_rate
- `method: "lending"` — loan_book, roe, pe_multiple (optional: npl_reserves)
- `method: "payment_processor"` — transaction_volume, take_rate, growth_rate, discount_rate, terminal_multiple (optional: years)
- `method: "neobank"` — customers, arpu, gross_margin, churn_rate, pe_multiple

### `valuation_marketplace`

Marketplace health and valuation: take rate, GMV revenue-multiple valuation, buyer retention, and network density.

- `method: "take_rate"` — revenue, gmv
- `method: "gmv_multiple"` — gmv, multiple
- `method: "buyer_retention"` — buyers_period_1, buyers_repeat
- `method: "network_density"` — active_buyers, active_sellers, total_users

### `valuation_hardware`

Hardware and deep-tech valuation: TRL-risk-adjusted valuation, gross margin, and break-even volume.

- `method: "trl"` — market_size, market_share, margin, multiple, trl_discount
- `method: "gross_margin"` — asp, variable_cost
- `method: "break_even_volume"` — fixed_costs, asp, variable_cost

## Best Practices

- Use industry-specific multiples (SaaS: 5-15x ARR, fintech: 3-5x revenue, marketplace: 0.3-0.5x GMV)
- Biotech pipeline: use conservative success probabilities from published clinical trial data
- Fintech lending: verify regulatory capital requirements before running lending valuations
- Marketplace: buyer retention below 30% signals fundamental unit economics problem
- Hardware: TRL discounts range from 95% (TRL 1-2) down to 10% (TRL 8-9)

## Common Pitfalls

- Don't apply SaaS ARR multiples to non-recurring or usage-based revenue streams
- Don't forget compliance rate in biotech peak sales (typically 70-90% of theoretical)
- Don't use GMV multiples for marketplaces with take rates below 5% — use revenue multiples instead
- Fintech neobank churn rates are typically higher than SaaS (15-25% vs 5-10%)

## Reference
- Textbook Chapter 11: Industry-Specific Valuation Frameworks
