# Skill: Valuation Core Methods

Core startup valuation methods: Scorecard, Berkus, Risk Factor Summation, and VC Method.

## When to Use

- **Scorecard Method**: Pre-revenue startup with comparable regional deal data available
- **Berkus Method**: Very early stage (idea to prototype), max $2.5M valuation
- **Risk Factor Summation**: When you need granular risk assessment across 12 factors
- **VC Method**: When you have a projected exit value and target return multiple

## Workflow

### Step 1: Gather Inputs
Ask the user for:
- Company stage (pre-revenue, early revenue, growth)
- Available comparable data (regional valuations, exit multiples)
- Investment amount and target return expectations

### Step 2: Select Method
- Pre-revenue, < $2.5M → Berkus
- Pre-revenue, comparable data available → Scorecard
- Need risk breakdown → Risk Factor Summation
- Exit projection available → VC Method

### Step 3: Calculate
Use the appropriate MCP tool (see MCP Tools section below for full signatures).

### Step 4: Interpret Results
- Scorecard: Compare to regional average. Score > 1.0 means above average.
- Berkus: Max $2.5M. Each factor capped at $500K.
- VC Method: Post-money = Terminal / Target Return. Pre-money = Post - Investment.

### Step 5: Triangulate
Run multiple methods and compare. If results differ by > 50%, investigate assumptions.
Use `valuation_full_analysis` for one-shot triangulation.

## MCP Tools

- `valuation_scorecard(average_valuation, weights, scores)` — Pre-revenue with comparable regional deal data
- `valuation_berkus(sound_idea, prototype, quality_team, strategic_relationships, product_rollout)` — Very early stage, max $2.5M
- `valuation_risk_factor_summation(base_valuation, risk_ratings)` — Granular 12-factor risk assessment
- `valuation_vc_post_money(terminal_value, target_return)` — When exit projection is available
- `valuation_vc_pre_money(post_money, investment)` — Derive pre-money from post-money
- `valuation_full_analysis(average_valuation, weights, scores, terminal_value, target_return, investment)` — Triangulated Scorecard + VC

## Best Practices

- Use multiple methods and compare results — triangulation reduces single-method bias
- Weights must sum to exactly 1.0 for Scorecard Method
- Risk ratings must be between -2 and +2, exactly 12 factors required
- Berkus values are capped at $500K per factor; maximum total is $2.5M
- When triangulating, weight results by method appropriateness for the company's stage

## Common Pitfalls

- Don't confuse Scorecard scores (1.0 = average) with percentages (100% ≠ 1.0)
- Don't use Berkus Method for post-revenue companies — it's pre-revenue only
- Don't forget that VC Method pre-money = post-money − investment, not the other way around
- Risk Factor Summation uses additive adjustment (V = V_base + Σ adjustments), not multiplicative

## Reference
- Textbook Chapter 3: Core Valuation Models
- Appendix A: Formulas Quick Reference
