---
name: valuation-stakeholder
description: >-
  What each stakeholder's slice is worth: dilution, the option pricing method, PWERM, liquidation preferences, employee options, vesting, and asset-backed lending.
license: MIT
---

# Skill: Valuation Stakeholder Perspectives

Stakeholder-specific methods: dilution, OPM, PWERM, liquidation, acquisition synergies.

## When to Use

- **Dilution**: Founder ownership across funding rounds, employee equity planning
- **OPM**: Common stock discount for 409A valuations, option pricing for preferred/common split
- **PWERM**: Common stock value across exit scenarios, employee option value
- **Liquidation**: Downside protection analysis, lender/creditor perspective
- **Acquisition Value**: M&A analysis with synergies, strategic buyer perspective
- **Vesting**: Employee equity value adjusted for retention probability and vesting schedule
- **Cash-Equity Tradeoff**: Startup compensation structure analysis

## Workflow

### Step 1: Identify Stakeholder
- Founder → Dilution analysis, option value, vesting schedule
- VC/Investor → Return analysis, dilution impact, liquidation preference
- Acquirer → Synergy-adjusted acquisition value
- Lender → Liquidation value, asset coverage, max loan calculation
- Employee → Option value with vesting, cash vs equity breakeven

### Step 2: Calculate
Use appropriate MCP tools (see MCP Tools section below for full signatures by stakeholder).

### Step 3: Interpret
- Dilution compounds across rounds. After 4 rounds, founders typically own 30-40%.
- OPM: Common stock typically 30-80% discount to preferred.
- PWERM: Weight scenarios by realistic exit probabilities.
- Liquidation: Cash 100%, AR 70-90%, inventory 30-60%, equipment 20-40%, IP 0-10%.
- Vesting: 4-year vest with 1-year cliff is standard; retention probability compounds annually.

## MCP Tools

Each tool takes `method` plus that method's own parameters — the arguments below are the ones
the tool validates, and an unknown method or a missing parameter returns an error instead of a value.

### `valuation_stakeholder`

Allocate value across stakeholders and equity classes: single-round dilution, OPM common stock, PWERM, liquidation value, M&A synergy, employee-option values, vesting adjustment, cash-vs-equity break-even, and asset-based loan capacity.

- `method: "dilution"` — ownership_before, investment, post_money
- `method: "opm"` — enterprise_value, liquidation_pref, time_to_exit, volatility
- `method: "pwerm"` — pwerm_scenarios
- `method: "liquidation"` — assets, recovery_rates
- `method: "risk_adjusted_synergy"` — revenue_synergies, cost_synergies (optional: prob_revenue, prob_cost, discount_rate, years)
- `method: "intrinsic_option"` — strike_price, fair_market_value, shares
- `method: "employee_option"` — employee_option_scenarios
- `method: "vesting_adjusted"` — total_value, vested_fraction (optional: annual_vest_rate, retention_prob, years_remaining)
- `method: "cash_equity_breakeven"` — salary_reduction, equity_value (optional: tax_rate, discount_rate, years)
- `method: "max_asset_loan"` — all optional: cash, accounts_receivable, inventory, equipment, real_estate

## Best Practices

- Model multi-round dilution over 3-5 rounds with realistic round sizes and valuations
- OPM: use company-specific volatility (not industry average) for 409A defensibility
- PWERM: use at least 3 scenarios (IPO, acquisition, dissolution) with current market probabilities
- Liquidation: be conservative on recovery rates — startups rarely recover more than 20% of IP value
- Vesting: standard is 4-year with 1-year cliff (25% cliff, then monthly) — adjust assumptions accordingly

## Common Pitfalls

- Don't forget option pool refresh between rounds — typically adds 10-20% additional dilution
- Don't use Black-Scholes for common stock without a discount for lack of marketability (DLOM)
- Don't assume 100% recovery on accounts receivable in startup liquidation (typically 30-50%)
- Synergy probabilities should be conservative (revenue synergies: 30-50%, cost synergies: 70-90%)
- Don't forget that equity value is pre-tax — after-tax analysis needed for cash-equity breakeven

## Reference
- Textbook Chapter 13: Valuation for Different Stakeholders
