# Worked Examples

Narrative step-by-step valuation walkthroughs using real startup scenarios. Each example follows a standard 6-section format.

## Template Format

```markdown
# Worked Example: [Title]

> Method: [Method Name] | Module: `[module].py` | Textbook: Chapter [N], Section [N.N]

## 1. Business Context

**The Situation:** [2-3 sentences: who, what stage, what they need]

**The Question:** [1 sentence: what are we calculating?]

**The Approach:** [1 sentence: which method and why]

## 2. Data Preparation

[All input data with sources and justifications. Tables preferred.]

## 3. Method Selection

[Why this method over alternatives. What assumptions make it appropriate.]

## 4. Step-by-Step Calculation

[Show each calculation step with intermediate values. Include Python code.]

### Step 1: [Name]
### Step 2: [Name]

[Final result displayed prominently]

### Python Implementation

[Complete, copy-pasteable code block with imports and output]

## 5. Sensitivity Analysis

[Test extremes. What happens if key inputs change? Use a table.]

## 6. Interpretation

**For the founders:** [What does this valuation mean for equity, fundraising?]

**For investors:** [Is the valuation justified? What are the risks?]

**What this valuation means:** [Actionable takeaway]

## Next Steps

- [Link to related methods]
- [Link to Wiki theory page]
- [Link to full workflow]

---

*Example uses hypothetical data for illustrative purposes. All formula implementations verified against the Startup Valuation textbook.*
```

## Existing Examples

| Example | Method | Module |
|---|---|---|
| [Valuing a Pre-Revenue SaaS Startup](valuing-pre-revenue-saas.md) | Scorecard Method | `core.py` |

## Contributing

To add a new worked example:
1. Copy the template above
2. Fill in all 6 sections
3. Use real (or realistic) numbers with stated sources
4. Include copy-pasteable Python code that produces the stated result
5. Ensure all formula values match textbook examples (run `pytest` to verify)
6. Link to the relevant Wiki theory page and API docs
