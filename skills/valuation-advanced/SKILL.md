# Skill: Valuation Advanced Methods

Advanced techniques: Black-Scholes, Monte Carlo, Scenario Analysis, and Binomial Tree.

## When to Use

- **Black-Scholes**: Valuing startup as a real option, biotech clinical stage, common stock via OPM
- **Monte Carlo**: High uncertainty with multiple variables, need probability distribution (library-only, not an MCP tool)
- **Scenario Analysis**: Discrete outcome scenarios (bull/base/bear), quick expected value
- **Binomial Tree**: American-style options, multi-stage decision processes (available via MCP)

## Workflow

### Step 1: Assess Uncertainty Level
- Low uncertainty, single estimate → Use core methods instead
- High uncertainty, multiple variables → Monte Carlo (use Python library directly)
- Discrete scenarios → Scenario Analysis
- Option-like payoff → Black-Scholes or Binomial

### Step 2: Gather Inputs
For Black-Scholes: underlying value, strike price, volatility, time to exit, risk-free rate
For Monte Carlo: distributions for market size, market share, margin (library: `monte_carlo_valuation`)
For Scenario: scenario names, probabilities (must sum to 1), values
For Binomial: same as Black-Scholes + number of steps (default 50)

### Step 3: Calculate
Use appropriate MCP tools (see MCP Tools section below for full signatures).
For Monte Carlo, import from library: `from startup_valuation.advanced import monte_carlo_valuation`

### Step 4: Interpret
- Black-Scholes: Higher volatility increases option value. Time value matters.
- Monte Carlo: Look at percentiles (P10, P50, P90), not just mean.
- Scenario: Expected value is probability-weighted. Check if probabilities are realistic.
- Binomial: Converges to Black-Scholes at high step counts (>50). Use for American-style options.

## MCP Tools

- `valuation_black_scholes(underlying, strike, risk_free_rate, volatility, time_to_maturity)` — European call option (real options)
- `valuation_scenario_analysis(scenarios)` — Discrete outcome scenarios [{name, probability, value}]
- `valuation_binomial(underlying, strike, risk_free_rate, volatility, time_to_maturity, steps=50)` — High-resolution binomial tree

Note: `monte_carlo_valuation` is available in the library but not exposed as an MCP tool.
Use `from startup_valuation.advanced import monte_carlo_valuation` directly.

## Best Practices

- For startup volatility estimates, use comparable public company data (not gut feel)
- `time_to_maturity` should be expected time to exit (typically 3-7 years for startups)
- Binomial tree with steps ≥ 50 provides convergence to Black-Scholes for European options
- Monte Carlo requires careful distribution selection — triangular is preferred for expert estimates
- Always run Monte Carlo with a fixed seed for reproducibility (`seed=42`)

## Common Pitfalls

- Don't use Black-Scholes for short time horizons — binomial tree is more accurate for startups
- Don't confuse Monte Carlo simulation with scenario analysis — Monte Carlo samples distributions, scenario uses fixed states
- Don't assume log-normal returns for pre-revenue startups — consider using uniform or triangular distributions
- Volatility of 40%+ is typical for early-stage startups; using public market volatility underestimates risk

## Reference
- Textbook Chapter 4: Advanced Techniques
- Textbook Chapter 13: OPM for common stock (stakeholders module)
