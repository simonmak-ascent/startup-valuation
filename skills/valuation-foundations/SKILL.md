---
name: valuation-foundations
description: >-
  The building blocks: probability-weighted expected value, time value and DCF, CAPM/WACC discount rates, market comparables, and cross-border adjustments. Use to derive a discount rate or discount cash flows before a method that consumes them.
license: MIT
---

# Skill: Valuation Foundations

Foundational mathematical tools: Probability, Time Value of Money, CAPM, Market Comparables, International Valuation.

## When to Use

- **Probability**: Need expected values, joint probabilities, or Poisson events for any valuation
- **Time Value**: Discounting cash flows, computing present value or NPV
- **CAPM**: Determining risk-adjusted discount rates for startups
- **Comparables**: Building regression-adjusted multiples from peer companies
- **International**: Cross-border adjustments (PPP, country risk, currency-adjusted DCF)

These are the building blocks used by all other valuation skills.

## Workflow

### Step 1: Identify the Foundation Needed
- Any valuation → Determine discount rate (CAPM)
- Any DCF → Compute present values and NPV (Time Value)
- Uncertain outcomes → Expected value or joint probability (Probability)
- Peer benchmarking → Multiples and regression (Comparables)
- Cross-border → PPP, country risk premium (International)

### Step 2: Select Tool
Use appropriate MCP tools (see MCP Tools section below for full signatures by module).

### Step 3: Interpret
- Probability tools return values between 0-1 or expected monetary values
- Time value tools return dollar amounts discounted to present
- CAPM returns percentage discount rates (multiply by 100 for display)
- Comparables return multiples (P/E, P/S, EV/EBITDA) or regression-adjusted multiples
- International returns exchange rates, risk premiums, or adjusted discount rates

## MCP Tools

Each tool takes `method` plus that method's own parameters — the arguments below are the ones
the tool validates, and an unknown method or a missing parameter returns an error instead of a value.

### `valuation_probability`

Compute expected value and probability-weighted outcomes for startup scenarios: discrete E[X], joint probability of sequential events, probability-weighted value, VC portfolio expected return, Poisson event probability, and continuous E[X] over a range.

- `method: "expected_value_discrete"` — outcomes, probabilities
- `method: "joint_probability"` — probabilities
- `method: "probability_weighted"` — outcomes, probabilities
- `method: "portfolio_return"` — weights, returns
- `method: "poisson"` — mean_events, k
- `method: "expected_value_continuous"` — lower, upper

### `valuation_time_value`

Discount, compound, and forecast value over time: single future value PV, net present value of a cash-flow stream, annuity present value, discounted cash flow with a Gordon terminal value, constant-rate compound growth of revenue or cash flow, and the implied compound annual growth rate (CAGR).

- `method: "present_value"` — future_value, rate, periods
- `method: "npv"` — cash_flows, rate
- `method: "annuity"` — payment, rate, periods
- `method: "compound_growth"` — starting_value, growth_rate, periods
- `method: "cagr"` — starting_value, ending_value, periods
- `method: "dcf"` — cash_flows, rate (optional: terminal_growth)

### `valuation_capm`

Estimate the cost of capital: standard CAPM, startup-adjusted CAPM with size and illiquidity premiums, portfolio beta from weighted asset betas, and WACC blending after-tax cost of equity and debt.

- `method: "capm"` — risk_free_rate, beta, market_return
- `method: "startup_capm"` — risk_free_rate, beta, market_risk_premium (optional: size_premium, liquidity_premium)
- `method: "portfolio_beta"` — weights, betas
- `method: "wacc"` — equity_value, debt_value, cost_of_equity, cost_of_debt, tax_rate

### `valuation_comparables`

Market multiples from comparables: P/E, P/S, EV/EBITDA, EV/Revenue, and a regression-adjusted multiple.

- `method: "pe_ratio"` — market_cap, net_income
- `method: "ps_ratio"` — market_cap, revenue
- `method: "ev_ebitda"` — enterprise_value, ebitda
- `method: "ev_revenue"` — enterprise_value, revenue
- `method: "regression_multiple"` — intercept, growth_rate, growth_coefficient (optional: market_maturity, maturity_coefficient, stage, stage_coefficient, geography, geography_coefficient)

### `valuation_international`

Cross-border adjustments: purchasing-power parity, country risk premium, and international CAPM.

- `method: "ppp"` — spot_rate, inflation_foreign, inflation_domestic
- `method: "country_risk_premium"` — sovereign_yield, us_treasury_yield
- `method: "intl_capm"` — risk_free_rate, beta, mrp, crp

## Best Practices

- Probabilities must sum to 1.0 (or close within 0.01 tolerance) for expected value calculations
- Use the startup-adjusted CAPM, not standard CAPM, for early-stage companies — add size + startup premiums
- For international valuations, always apply country risk premium AFTER base CAPM calculation
- Regression-adjusted multiples are only as good as the peer data — validate coefficients before use
- When computing joint probability, ensure events are actually independent (multiplying correlated events overestimates risk)

## Common Pitfalls

- Don't use standard CAPM for pre-revenue startups — betas from public markets underestimate startup risk
- Don't confuse joint probability (product of probabilities) with expected value (weighted sum)
- NPV requires consistent time periods — mixing annual and monthly cash flows produces wrong results
- Country Risk Premium from sovereign yield spreads assumes bond market efficiency — validate with CDS spreads for emerging markets
- Don't use Purchasing Power Parity for short-term exchange rate forecasts (PPP is a long-run equilibrium concept)

## Reference
- Textbook Chapter 2: Mathematical Foundations (Probability, TVM, CAPM)
- Textbook Chapter 5: Market Comparables
- Textbook Chapter 12: International Valuation
