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

**SaaS:**
- `valuation_saas_ltv(arpu, gross_margin, churn_rate)` — Lifetime value per customer
- `valuation_rule_of_40(growth_rate, profit_margin)` — Health check: growth + profit ≥ 40%
- `valuation_saas_multiple(arr, multiple)` — ARR-based valuation

**Biotech:**
- `valuation_decision_tree(probabilities, terminal_value)` — Stage-gate expected value
- `valuation_peak_sales(patient_population, penetration, price, compliance)` — Peak sales estimate
- `valuation_pipeline(drugs, discount_rate)` — Multi-drug pipeline valuation

**Fintech:**
- `valuation_payment_revenue(transaction_volume, take_rate)` — Payment processor revenue
- `valuation_lending(loan_book, roe, pe_multiple, npl_reserves)` — Lending fintech valuation
- `valuation_payment_processor(transaction_volume, take_rate, growth_rate, discount_rate, terminal_multiple, years)` — DCF-based processor valuation
- `valuation_neobank(customers, arpu, gross_margin, churn_rate, pe_multiple)` — Customer-based neobank valuation

**Marketplace:**
- `valuation_take_rate(revenue, gmv)` — Revenue as percentage of GMV
- `valuation_gmv_multiple(gmv, multiple)` — GMV-based valuation
- `valuation_buyer_retention(buyers_period_1, buyers_repeat)` — Cohort retention metric
- `valuation_network_density(active_buyers, active_sellers, total_users)` — Marketplace engagement ratio

**Hardware:**
- `valuation_trl(market_size, market_share, margin, multiple, trl_discount)` — TRL-adjusted valuation

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
