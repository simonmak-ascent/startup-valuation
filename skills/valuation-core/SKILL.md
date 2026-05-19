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
Use the appropriate MCP tool:
- `valuation_scorecard(average_valuation, weights, scores)`
- `valuation_berkus(sound_idea, prototype, quality_team, strategic_relationships, product_rollout)`
- `valuation_risk_factor_summation(base_valuation, risk_ratings)`
- `valuation_vc_post_money(terminal_value, target_return)`

### Step 4: Interpret Results
- Scorecard: Compare to regional average. Score > 1.0 means above average.
- Berkus: Max $2.5M. Each factor capped at $500K.
- VC Method: Post-money = Terminal / Target Return. Pre-money = Post - Investment.

### Step 5: Triangulate
Run multiple methods and compare. If results differ by > 50%, investigate assumptions.

## Reference
- Textbook Chapter 3: Core Valuation Models
- Appendix A: Formulas Quick Reference
