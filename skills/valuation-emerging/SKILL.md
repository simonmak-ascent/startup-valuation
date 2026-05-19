# Skill: Valuation Emerging Topics

Emerging valuation methods: SAFE, crypto/token, ESG, network effects, remote-first.

## When to Use

- **SAFE Conversion**: Early-stage financing with valuation cap or discount
- **Equation of Exchange (MV=PQ)**: Crypto/blockchain token valuation
- **ESG-Adjusted Rate**: Companies with significant ESG impact (positive or negative)
- **Metcalfe's Law**: Platform businesses with network effects
- **Remote NPV**: Remote-first company cost advantage valuation

## Workflow

### Step 1: Identify Topic
Ask about the startup's financing instrument, business model, or unique characteristics.

### Step 2: Calculate
- `valuation_safe_discount(series_a_price, discount)`
- `valuation_token_value(transaction_volume, price_per_tx, velocity, supply)`
- `valuation_esg_rate(base_rate, risk_premium, opp_discount)`
- `valuation_metcalfes(n, k)`
- `valuation_remote_npv(annual_savings, discount_rate)`

### Step 3: Interpret
- SAFE: Investors get the better of cap or discount. Typical expected return 2-5x.
- Token: Velocity is critical — higher velocity reduces token value.
- ESG: Strong ESG = 10-30% premium. High ESG risk = 20-50% discount.
- Metcalfe: Value ∝ n^1.2-1.5 (empirical), not n² (theoretical).
- Remote: $1-2M annual savings = $5-20M NPV at 10-20% discount rate.

## Reference
- Textbook Chapter 14: Emerging Topics in Startup Valuation
