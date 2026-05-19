# Skill: Valuation Stakeholder Perspectives

Stakeholder-specific methods: dilution, OPM, PWERM, liquidation, acquisition synergies.

## When to Use

- **Dilution**: Founder ownership across funding rounds
- **OPM**: Common stock discount for 409A valuations
- **PWERM**: Common stock value across exit scenarios
- **Liquidation**: Downside protection, lender perspective
- **Acquisition Value**: M&A analysis with synergies

## Workflow

### Step 1: Identify Stakeholder
- Founder → Dilution analysis, option value
- VC/Investor → Return analysis, dilution impact
- Acquirer → Synergy-adjusted acquisition value
- Lender → Liquidation value, asset coverage
- Employee → Option value with vesting

### Step 2: Calculate
- `valuation_dilution(ownership_before, investment, post_money)`
- `valuation_opm(enterprise_value, liquidation_pref, time_to_exit, volatility)`
- `valuation_pwerm(scenarios)` where scenarios = [{probability, common_value}]
- `valuation_liquidation(assets, recovery_rates)`

### Step 3: Interpret
- Dilution compounds across rounds. After 4 rounds, founders typically own 30-40%.
- OPM: Common stock typically 30-80% discount to preferred.
- PWERM: Weight scenarios by realistic exit probabilities.
- Liquidation: Cash 100%, AR 70-90%, inventory 30-60%, equipment 20-40%, IP 0-10%.

## Reference
- Textbook Chapter 13: Valuation for Different Stakeholders
