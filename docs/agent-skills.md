# AI Agent Skills

AI Agent Skills provide domain-specific workflow guidance for valuation tasks. Each skill is a `SKILL.md` file that teaches an AI agent how to approach valuation problems step-by-step.

## What Are AI Agent Skills?

Skills are markdown files that define:
- **When to use** the skill (trigger conditions)
- **Step-by-step workflows** for valuation tasks
- **MCP tool mappings** — which tools to call and when
- **Best practices** and common pitfalls

There are 5 skills available:

| Skill | Covers |
|---|---|
| `valuation-core` | Scorecard, Berkus, VC Method, Risk Factor Summation |
| `valuation-advanced` | Black-Scholes, Binomial, Monte Carlo, Scenario Analysis |
| `valuation-industry` | SaaS, Biotech, Fintech, Marketplace, Hardware |
| `valuation-stakeholder` | Dilution, OPM, PWERM, Liquidation Preference |
| `valuation-emerging` | SAFE, Crypto (MV=PQ), ESG, Metcalfe's Law |

## Setup for OpenCode

1. Copy the `skills/` directory to your OpenCode skills folder:

```bash
cp -r /path/to/startup-valuation/skills ~/.config/opencode/skills/
```

2. Verify the skills are loaded:

```bash
ls ~/.config/opencode/skills/
# valuation-core  valuation-advanced  valuation-industry  valuation-stakeholder  valuation-emerging
```

3. Start a new OpenCode session — the skills are now available.

## Setup for Claude Desktop

Claude Desktop doesn't have a native skills folder. Instead, add the skill content to your custom instructions:

1. Open Claude Desktop settings
2. Go to **Custom Instructions**
3. Paste the content of the relevant `SKILL.md` file
4. Claude will now follow the workflow guidance

## Setup for Cursor

1. Open Cursor settings
2. Go to **Features** → **Custom Instructions**
3. Paste the content of the relevant `SKILL.md` file
4. Cursor will now follow the workflow guidance

## SKILL.md Schema

Each `SKILL.md` file follows this structure:

```markdown
# Skill: [skill-name]

## When to Use
[Conditions that trigger this skill]

## Workflow
1. [Step 1]
2. [Step 2]
3. [Step 3]

## MCP Tools
- `tool_name` — [when to use this tool]
- `tool_name` — [when to use this tool]

## Best Practices
- [Best practice 1]
- [Best practice 2]

## Common Pitfalls
- [Pitfall 1 and how to avoid it]
```

### Required Sections

| Section | Purpose |
|---|---|
| `When to Use` | Tells the agent when to activate this skill |
| `Workflow` | Step-by-step instructions for the valuation task |
| `MCP Tools` | Maps workflow steps to MCP tool calls |

### Optional Sections

| Section | Purpose |
|---|---|
| `Best Practices` | Domain-specific guidance |
| `Common Pitfalls` | Error prevention |

## Example: Writing a Custom Skill

Here's how to write a skill for a new valuation method:

```markdown
# Skill: Real Estate Valuation

## When to Use
- User asks to value a real estate startup
- User mentions property, REIT, or real estate metrics

## Workflow
1. Gather property details: location, type, square footage
2. Calculate NOI (Net Operating Income)
3. Apply cap rate: Value = NOI / Cap Rate
4. Compare with comparable property sales

## MCP Tools
- `valuation_present_value` — for discounted cash flow of rental income
- `valuation_capm` — for determining appropriate discount rate

## Best Practices
- Use local market cap rates, not national averages
- Factor in vacancy rates (typically 5-10%)
- Consider property management costs (3-8% of rent)

## Common Pitfalls
- Don't use residential cap rates for commercial properties
- Don't forget to account for property taxes and insurance
```

## How Skills Map to MCP Tools

Skills don't replace MCP tools — they guide when and how to use them:

```
User asks: "Value my SaaS startup"
    ↓
Agent checks skills → matches `valuation-industry` (SaaS section)
    ↓
Skill workflow says:
  1. Calculate ARR → use `valuation_saas_multiple` with arr parameter
  2. Calculate LTV/CAC → use `valuation_saas_ltv`
  3. Check Rule of 40 → use `valuation_rule_of_40`
    ↓
Agent calls MCP tools in sequence
    ↓
Agent synthesizes results into a valuation report
```
