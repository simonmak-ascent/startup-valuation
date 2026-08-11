# Worked Example: Valuing a Pre-Revenue SaaS Startup

> Method: Scorecard Method | Module: `core.py` | Textbook: Chapter 3, Section 3.1

---

## 1. Business Context

**The Situation:** CloudFlow, a pre-revenue B2B SaaS startup in Austin, Texas, is raising a Seed round. The founders have built an MVP with 3 design partners, but have zero revenue. They need to determine a defensible pre-money valuation for investor conversations.

**The Question:** What is CloudFlow worth today, before any investment?

**The Approach:** Use the Scorecard Method — the standard for pre-revenue startup valuation. It adjusts the average regional valuation based on CloudFlow's strengths and weaknesses across 7 factors.

---

## 2. Data Preparation

### Step 1: Find the Average Regional Valuation

AngelList and Crunchbase data show that pre-revenue B2B SaaS startups in Austin raised Seed rounds at an average pre-money valuation of **$2,000,000** in 2026.

### Step 2: Choose Factor Weights

We use Bill Payne's standard factor weights for pre-revenue startups, adjusted slightly for B2B SaaS:

| Factor | Weight | Rationale |
|---|---|---|
| Team | 30% | The founding team's experience is the #1 predictor at this stage |
| Product/Technology | 25% | Product maturity and technical differentiation matter for SaaS |
| Market Size & Growth | 15% | B2B SaaS market is large but competitive |
| Competitive Environment | 10% | Several established players exist |
| Marketing/Sales Channels | 10% | Enterprise sales require a defined GTM strategy |
| Need for Additional Investment | 5% | CloudFlow will need a Series A in 18 months |
| Other (Legal/Regulatory) | 5% | Standard SaaS considerations (GDPR, SOC 2) |

### Step 3: Score Each Factor

| Factor | Score | Justification |
|---|---|---|
| Team | **1.50** | Two founders: ex-Salesforce VP Engineering (10 yrs) + YC alum. Stronger than average. |
| Product | **1.25** | Working MVP with 3 design partners. Slightly ahead of average pre-revenue startups. |
| Market | **1.20** | Targeting $50B workflow automation market growing at 18% CAGR. Above average. |
| Competition | **0.75** | 5+ funded competitors including a unicorn. Below average competitive position. |
| Marketing | **1.00** | No dedicated marketing hire yet. Average for pre-revenue stage. |
| Funding Need | **0.90** | Will need $3M Series A in 18 months. Slightly above-average capital need. |
| Other | **1.00** | No unusual legal or regulatory risks. Average. |

---

## 3. Method Selection

We chose the **Scorecard Method** because:
- CloudFlow is **pre-revenue** (no revenue multiples to apply)
- Comparable **regional deal data** is available (Austin B2B SaaS Seed rounds)
- The method accounts for **qualitative factors** (team, product, market) that matter most at this stage

Alternatives considered:
- Berkus Method → too broad (5 binary milestones). CloudFlow has more nuanced strengths.
- VC Method → requires exit value projections, which are highly speculative for pre-revenue.
- Discounted Cash Flow → requires revenue forecasts; CloudFlow has none.

---

## 4. Step-by-Step Calculation

### Step 1: Check Weights Sum to 1.0

$$0.30 + 0.25 + 0.15 + 0.10 + 0.10 + 0.05 + 0.05 = 1.00 \checkmark$$

### Step 2: Compute Weighted Scores

| Factor | Weight | Score | $$w_i \times s_i$$ |
|---|---|---|---|
| Team | 0.30 | 1.50 | **0.450** |
| Product | 0.25 | 1.25 | **0.3125** |
| Market | 0.15 | 1.20 | **0.180** |
| Competition | 0.10 | 0.75 | **0.075** |
| Marketing | 0.10 | 1.00 | **0.100** |
| Funding Need | 0.05 | 0.90 | **0.045** |
| Other | 0.05 | 1.00 | **0.050** |
| **Total** | **1.00** | | **1.2125** |

### Step 3: Apply Multiplier

$$V = \$2{,}000{,}000 \times 1.2125 = \$2{,}425{,}000$$

**Result:** CloudFlow's estimated pre-money valuation is **$2,425,000**.

### Python Implementation

```python
from startup_valuation.core import scorecard_valuation

result = scorecard_valuation(
    average_valuation=2_000_000,
    weights=[0.30, 0.25, 0.15, 0.10, 0.10, 0.05, 0.05],
    scores=[1.50, 1.25, 1.20, 0.75, 1.00, 0.90, 1.00],
)

print(f"Scorecard Valuation: ${result.value:,.0f}")
# Scorecard Valuation: $2,425,000

print(f"Multiplier: {result.value / 2_000_000:.4f}x")
# Multiplier: 1.2125x

print(f"Assumptions: {result.assumptions}")
# ['Average valuation is from comparable regional deals',
#  'Scores are relative to average (1.0 = average)',
#  'Weights reflect factor importance for this stage']
```

---

## 5. Sensitivity Analysis

What if our scores were wrong? Let's test the extremes:

| Scenario | Team Score | Competition Score | Valuation | Change |
|---|---|---|---|---|
| **Bull** | 2.00 (elite team) | 1.00 (neutral) | $2,600,000 | +7.2% |
| **Base** | 1.50 | 0.75 | $2,425,000 | — |
| **Bear** | 1.00 (average team) | 0.50 (very weak) | $2,200,000 | -9.3% |

**Key insight:** Team score is the most impactful factor (30% weight). A full point swing in team score (1.0 → 2.0) changes the valuation by **$300,000** (15% of baseline).

---

## 6. Interpretation

**For the founders:**
- CloudFlow is worth **$2.4M pre-money** — 21% above the Austin B2B SaaS average
- The premium is driven by: strong founding team (+$300K) and solid product (+$62.5K)
- The discount is from: weak competitive position (-$50K) and high future capital need (-$10K)
- If raising $500K, they'd give up **~17% equity** ($500K / $2.925M post-money)

**For investors:**
- The 21% premium over average is justified by the team (ex-Salesforce VP, YC alum)
- The competitive risk is real — 5 funded competitors including a unicorn
- Market growth (18% CAGR) supports the above-average market score
- Recommendation: Validate team references and competitive landscape before committing

**What this valuation means:**
- It's a **starting point for negotiation**, not a final number
- The Scorecard Method is most useful for **structuring the conversation** around specific factors
- Combine with VC Method (working backward from exit) for a triangulated range

---

## Next Steps

- [Advanced Methods](https://simonplmak-cloud.github.io/startup-valuation/api/core/) — Try Black-Scholes for employee option valuation
- [How to Value a Startup](How-to-Value-a-Startup) — Full workflow from method selection to term sheet
- [Core Methods Wiki](Core-Methods) — Full mathematical derivation of the Scorecard formula

---

*Example uses hypothetical data for illustrative purposes. All formula implementations verified against the Startup Valuation textbook.*
