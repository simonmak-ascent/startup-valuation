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
Use appropriate MCP tools:
- SaaS: `valuation_saas_ltv`, `valuation_saas_multiple`, `valuation_rule_of_40`
- Biotech: `valuation_decision_tree`, `valuation_peak_sales`, `valuation_pipeline`
- Fintech: `valuation_payment_revenue`, `valuation_lending`
- Marketplace: `valuation_take_rate`, `valuation_gmv_multiple`
- Hardware: `valuation_trl`

### Step 4: Interpret
Compare results to industry benchmarks. Flag if metrics are outside normal ranges.

## Reference
- Textbook Chapter 11: Industry-Specific Valuation Frameworks
