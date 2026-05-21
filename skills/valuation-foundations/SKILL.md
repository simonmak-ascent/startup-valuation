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

**Probability:**
- `valuation_expected_value(outcomes, probabilities)` — Discrete random variable: E[X] = Σ xᵢ × P(xᵢ)
- `valuation_expected_value_continuous(lower, upper)` — Continuous random variable via numerical integration
- `valuation_joint_probability(probabilities)` — Sequential event chain: P(total) = Π Pᵢ
- `valuation_probability_weighted(probabilities, values)` — Scenario-weighted value: E[V] = Σ pᵢ × Vᵢ
- `valuation_portfolio_return(probabilities, returns)` — VC portfolio expected return: E[R] = Σ pᵢ × Rᵢ

**Time Value:**
- `valuation_present_value(future_value, rate, periods)` — Single cash flow: PV = C / (1+r)^t
- `valuation_npv(cash_flows, rate)` — Series of cash flows: NPV = Σ Cₜ / (1+r)^t

**CAPM:**
- `valuation_capm(risk_free_rate, beta, market_return)` — Standard CAPM: E(R) = Rf + β × (Rm - Rf)
- `valuation_portfolio_beta(weights, betas)` — Portfolio-weighted beta: βp = Σ wᵢβᵢ
- `valuation_startup_capm(risk_free_rate, beta, market_risk_premium, size_premium, startup_premium)` — Startup-adjusted CAPM with size and stage premiums

**Comparables:**
- `valuation_regression_multiple(intercept, growth_rate, growth_coefficient, market_maturity, maturity_coefficient, stage, stage_coefficient, geography, geography_coefficient)` — Regression-adjusted multiple from peer data

**International:**
- `valuation_ppp(spot_rate, inflation_foreign, inflation_domestic)` — Purchasing Power Parity exchange rate
- `valuation_crp(sovereign_yield, us_treasury_yield)` — Country Risk Premium from sovereign spreads
- `valuation_intl_capm(risk_free_rate, beta, mrp, crp)` — International CAPM: r = Rf + β×MRP + CRP

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
