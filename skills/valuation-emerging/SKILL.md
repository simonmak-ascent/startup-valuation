---
name: valuation-emerging
description: >-
  Instruments and effects outside the textbook's core chapters: SAFEs, token and network valuations, ESG adjustments, data moats and remote-first premia.
license: MIT
---

# Skill: Valuation Emerging Topics

Emerging valuation methods: SAFE, crypto/token, ESG, network effects, remote-first.

## When to Use

- **SAFE Conversion**: Early-stage financing with valuation cap or discount
- **Equation of Exchange (MV=PQ)**: Crypto/blockchain token valuation
- **ESG-Adjusted Rate**: Companies with significant ESG impact (positive or negative)
- **Metcalfe's Law**: Platform businesses with network effects
- **Remote NPV**: Remote-first company cost advantage valuation
- **Data Moat**: Companies with proprietary data as competitive advantage

## Workflow

### Step 1: Identify Topic
Ask about the startup's financing instrument, business model, or unique characteristics.

### Step 2: Calculate
Use appropriate MCP tools (see MCP Tools section below for full signatures by topic).

### Step 3: Interpret
- SAFE: Investors get the better of cap or discount. Typical expected return 2-5x.
- Token: Velocity is critical — higher velocity reduces token value.
- ESG: Strong ESG = 10-30% premium. High ESG risk = 20-50% discount.
- Metcalfe: Value ∝ n^1.2-1.5 (empirical), not n² (theoretical).
- Remote: $1-2M annual savings = $5-20M NPV at 10-20% discount rate.

## MCP Tools

Each tool takes `method` plus that method's own parameters — the arguments below are the ones
the tool validates, and an unknown method or a missing parameter returns an error instead of a value.

### `valuation_emerging`

Modern and alternative valuation: SAFE conversion (discount, cap, expected value), token valuation (equation of exchange, NVT), ESG adjustments (rate, premium, discount), Metcalfe network value, data-moat value, and remote-first premium/NPV.

- `method: "safe_discount"` — series_a_price, discount
- `method: "safe_cap"` — cap, series_a_price
- `method: "safe_expected"` — investment, cap, discount, series_a_valuation, series_a_price
- `method: "token_value"` — transaction_volume, price_per_tx, velocity, supply
- `method: "nvt_ratio"` — market_cap, transaction_volume
- `method: "esg_rate"` — rate (optional: esg_risk_premium, esg_opportunity_discount)
- `method: "esg_premium"` — base_valuation, esg_score (optional: premium_per_point)
- `method: "esg_discount"` — base_valuation, esg_risk_score (optional: discount_per_point)
- `method: "metcalfe"` — n (optional: k)
- `method: "data_moat"` — data_volume, data_uniqueness, monetization_rate, competitive_advantage_years (optional: discount_rate)
- `method: "remote_npv"` — annual_savings, discount_rate
- `method: "remote_premium"` — base_valuation (optional: cost_savings_pct, talent_access_premium, productivity_gain)

## Best Practices

- SAFE: always compare both cap and discount scenarios; use `valuation_emerging` with `method: "safe_expected"` for the combined analysis
- Token velocity should be based on actual on-chain transaction data, not theoretical assumptions
- ESG premium calibration: use industry-standard frameworks (SASB, GRI, MSCI) for score consistency
- Metcalfe's Law: for real platforms, use α = 1.2-1.5 (empirical), not n² (theoretical)
- NVT ratio interpretation: NVT < 15 = undervalued, NVT > 25 = overvalued, 30+ = speculative

## Common Pitfalls

- Don't use SAFE cap price without factoring in dilution from the option pool (typically 10-20%)
- Don't confuse on-chain transaction volume with speculative exchange trading volume for token valuation
- Don't apply ESG premium to companies without verified third-party ESG ratings
- Network effects are not uniform — Metcalfe's Law overestimates value for platforms with weak retention
- Don't double-count cost savings and productivity gains in remote-first premium (they overlap)

## Reference
- Textbook Chapter 14: Emerging Topics in Startup Valuation
