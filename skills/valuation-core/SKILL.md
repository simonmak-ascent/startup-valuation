---
name: valuation-core
description: >-
  Value pre-revenue startups with the Scorecard, Berkus, Risk-Factor Summation and VC methods, plus exit terminal value and a triangulated blend. Use when there is no revenue yet and the question is which early-stage method the available data supports.
license: MIT
---

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
Use `valuation_core` with `method: "triangulated"` for one-shot triangulation.

## MCP Tools

Each tool takes `method` plus that method's own parameters — the arguments below are the ones
the tool validates, and an unknown method or a missing parameter returns an error instead of a value.

### `valuation_core`

The textbook's pre-revenue methods: Scorecard, Berkus, Risk-Factor Summation, VC Method (post- and pre-money), and exit terminal value.

- `method: "scorecard"` — average_valuation, weights, scores
- `method: "berkus"` — all optional: sound_idea, prototype, quality_team, strategic_relationships, product_rollout
- `method: "risk_factor"` — base_valuation, risk_ratings
- `method: "vc_post_money"` — terminal_value, target_return
- `method: "vc_pre_money"` — post_money, investment
- `method: "terminal_value"` — projected_revenue, multiple
- `method: "triangulated"` — average_valuation, weights, scores, terminal_value, target_return, investment

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
