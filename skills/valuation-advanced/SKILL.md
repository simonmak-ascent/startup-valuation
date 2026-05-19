# Skill: Valuation Advanced Methods

Advanced techniques: Black-Scholes, Monte Carlo, Scenario Analysis, and Binomial Tree.

## When to Use

- **Black-Scholes**: Valuing startup as a real option, biotech clinical stage, common stock via OPM
- **Monte Carlo**: High uncertainty with multiple variables, need probability distribution
- **Scenario Analysis**: Discrete outcome scenarios (bull/base/bear), quick expected value
- **Binomial Tree**: American-style options, multi-stage decision processes

## Workflow

### Step 1: Assess Uncertainty Level
- Low uncertainty, single estimate → Use core methods instead
- High uncertainty, multiple variables → Monte Carlo
- Discrete scenarios → Scenario Analysis
- Option-like payoff → Black-Scholes

### Step 2: Gather Inputs
For Black-Scholes: underlying value, strike price, volatility, time to exit, risk-free rate
For Monte Carlo: distributions for market size, market share, margin
For Scenario: scenario names, probabilities (must sum to 1), values

### Step 3: Calculate
- `valuation_black_scholes(underlying, strike, risk_free_rate, volatility, time_to_maturity)`
- `valuation_scenario_analysis(scenarios)` where scenarios = [{name, probability, value}]

### Step 4: Interpret
- Black-Scholes: Higher volatility increases option value. Time value matters.
- Monte Carlo: Look at percentiles (P10, P50, P90), not just mean.
- Scenario: Expected value is probability-weighted. Check if probabilities are realistic.

## Reference
- Textbook Chapter 4: Advanced Techniques
- Textbook Chapter 13: OPM for common stock (stakeholders module)
