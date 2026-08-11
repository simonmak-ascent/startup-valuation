# Core Methods — Theory & Derivation

> Textbook: Chapter 3 | Module: `startup_valuation.core` | Last verified: 2026-08-11

---

## Contents

1. [Scorecard Method](#scorecard-method) ⬅ *Complete 13-step derivation*
2. [Berkus Method](#berkus-method)
3. [Risk Factor Summation](#risk-factor-summation)
4. [VC Method](#vc-method)

---

## Scorecard Method

### 1. Learning Objective

Derive the **Scorecard Valuation Method** for pre-revenue startups. By the end of this section, you will be able to:
- Compute a target valuation from an average regional valuation
- Apply factor weights and scores to adjust for startup-specific strengths and weaknesses
- Understand the assumptions behind the method
- Implement the calculation in Python

### 2. Prerequisites

- Understanding of pre-money vs post-money valuation
- Basic algebra (weighted averages)
- Familiarity with the [Glossary](Glossary) notation

### 3. Definitions

| Symbol | Meaning | Units | Code Variable |
|---|---|---|---|
| $$V_{avg}$$ | Average pre-money valuation for comparable startups in the region | USD | `average_valuation` |
| $$w_i$$ | Weight assigned to factor $$i$$ (importance of each factor) | Dimensionless (sum = 1.0) | `weights[i]` |
| $$s_i$$ | Score for factor $$i$$ relative to average (1.0 = average) | Dimensionless | `scores[i]` |
| $$n$$ | Number of factors (typically 7) | Count | `len(weights)` |
| $$V$$ | Target valuation (output) | USD | `result.value` |

### 4. Assumptions

1. **Average valuation is from comparable regional deals** — The $$V_{avg}$$ baseline is derived from actual funding rounds of similar-stage startups in the same geography and industry.
2. **Scores are relative to average (1.0 = average)**: A score of 1.0 means the startup is average on that factor. Scores > 1.0 indicate above-average strength. Scores < 1.0 indicate below-average.
3. **Weights reflect factor importance for this stage**: The seven standard factors (Team, Product, Market, etc.) are weighted according to their importance at the startup's current stage.
4. **Factors are independent**: The method assumes additive independence — each factor contributes independently to the adjustment.
5. **Linear scaling**: The valuation adjustment is linear with respect to the weighted score. No diminishing returns or interaction effects.

### 5. Starting Equation

The Scorecard Method adjusts the average regional valuation by a weighted sum of factor scores:

$$V = V_{avg} \times \sum_{i=1}^{n} w_i \times s_i$$

Where $$\sum w_i = 1$$ and $$s_i > 0$$.

**Source:** Startup Valuation textbook, Chapter 3, Section 3.1, Formula 3.1.

### 6. Derivation

**Step 1 — Baseline.** Start with the average pre-money valuation $$V_{avg}$$ for comparable startups in the same region and industry.

**Step 2 — Factor identification.** Identify $$n$$ factors that influence startup valuation. Typical factors (Bill Payne's framework):

| Factor | Typical Weight | Rationale |
|---|---|---|
| Team | 30% | The team's experience and track record are the strongest predictors of startup success |
| Product/Technology | 25% | Product maturity, IP protection, and technical differentiation |
| Market Size & Growth | 15% | Addressable market size and growth rate |
| Competitive Environment | 10% | Number and strength of competitors |
| Marketing/Sales | 10% | Go-to-market strategy and sales channels |
| Need for Additional Investment | 5% | Future capital requirements |
| Other Factors | 5% | Legal, regulatory, or other considerations |

**Step 3 — Scoring.** For each factor, assign a score $$s_i$$ relative to the average comparable startup:

$$s_i = \begin{cases} > 1.0 & \text{Above average} \\ 1.0 & \text{Average} \\ < 1.0 & \text{Below average} \end{cases}$$

Scores typically range from 0.5 (significantly below average) to 2.0 (significantly above average).

**Step 4 — Weighted score.** Compute the weighted sum of scores:

$$\text{Weighted Score} = \sum_{i=1}^{n} w_i \times s_i$$

This produces a single multiplier. A result of 1.0 means the startup is average across all factors (valuation = $$V_{avg}$$).

**Step 5 — Apply multiplier.** Multiply the average valuation by the weighted score:

$$V = V_{avg} \times \text{Weighted Score}$$

### 7. Intermediate Checks

**Check 1 — Weight normalization:** $$\sum w_i = 1.0$$ (within tolerance of 0.01).

**Check 2 — Score bounds:** All $$s_i > 0$$. Negative scores are undefined (you can't have negative strength).

**Check 3 — Multiplier range:** For typical scores (0.5 to 2.0), the weighted score ranges from 0.5 to 2.0, meaning the valuation ranges from $$0.5 \times V_{avg}$$ to $$2.0 \times V_{avg}$$.

### 8. Final Computational Form

The library implements this directly:

```python
weighted_score = sum(w * s for w, s in zip(weights, scores))
valuation = average_valuation * weighted_score
```

This is the stable computational form — no numerical issues for typical inputs.

### 9. Algorithm Mapping

| Mathematical Step | Python Call | Source |
|---|---|---|
| Weight normalization check | `abs(sum(weights) - 1.0) > 0.01` | `core.py:37` |
| Score-weights length check | `len(weights) != len(scores)` | `core.py:39` |
| Weighted sum | `sum(w * s for w, s in zip(weights, scores))` | `core.py:42` |
| Final valuation | `average_valuation * weighted_score` | `core.py:43` |

### 10. Worked Numerical Example

**Scenario:** A pre-revenue SaaS startup in the Bay Area. Comparable startups in the region raise at an average pre-money valuation of **$1,500,000**.

| Factor | Weight | Score | Weighted Score |
|---|---|---|---|
| Team | 0.30 | 1.25 | 0.375 |
| Product | 0.25 | 1.50 | 0.375 |
| Market | 0.15 | 1.20 | 0.180 |
| Competition | 0.10 | 0.75 | 0.075 |
| Marketing | 0.10 | 1.00 | 0.100 |
| Funding Need | 0.05 | 0.90 | 0.045 |
| Other | 0.05 | 1.00 | 0.050 |
| **Total** | **1.00** | | **1.200** |

$$V = \$1{,}500{,}000 \times 1.200 = \$1{,}800{,}000$$

The startup's target pre-money valuation is **$1,800,000** — 20% above the regional average, driven primarily by a strong team (1.25) and superior product (1.50), partially offset by a weak competitive position (0.75).

**Python verification:**

```python
from startup_valuation.core import scorecard_valuation

result = scorecard_valuation(
    average_valuation=1_500_000,
    weights=[0.30, 0.25, 0.15, 0.10, 0.10, 0.05, 0.05],
    scores=[1.25, 1.50, 1.20, 0.75, 1.00, 0.90, 1.00],
)
print(f"${result.value:,.0f}")  # $1,800,000
```

### 11. Numerical Limitations

- **Weight precision:** Weights must sum to 1.0. A tolerance of ±0.01 is enforced. Inputs with sum outside this range raise `ValueError`.
- **Score domain:** Scores must be strictly positive. Zero or negative scores are undefined.
- **No confidence interval:** The method produces a point estimate. For probabilistic output, use Scenario Analysis or Monte Carlo simulation.
- **Stage sensitivity:** Factor weights change by startup stage (pre-seed weights differ from Series A weights). The method does not auto-adjust weights.

### 12. Validation

The textbook reports a target valuation of **$1,800,000** for the example above. The library produces:

```python
assert result.value == pytest.approx(1_800_000)  # Exact match within tolerance
```

The library's test suite validates this against the textbook example (see `tests/test_core.py:15-21`).

### 13. References and Related Pages

- **Textbook:** Startup Valuation, Chapter 3, Section 3.1 — Scorecard Method
- **API:** [`scorecard_valuation()`](https://simonplmak-cloud.github.io/startup-valuation/api/core/#startup_valuation.core.scorecard_valuation)
- **Source:** [`core.py:11-59`](https://github.com/simonplmak-cloud/startup-valuation/blob/main/src/startup_valuation/core.py#L11)
- **Test:** [`tests/test_core.py:15-21`](https://github.com/simonplmak-cloud/startup-valuation/blob/main/tests/test_core.py#L15)
- **Next:** [Berkus Method](#berkus-method) | [Advanced Methods](Advanced-Methods)

---

## Berkus Method

> *Full derivation coming in Phase 2. See [API docs](https://simonplmak-cloud.github.io/startup-valuation/api/core/#startup_valuation.core.berkus_valuation) for the Python interface.*

The Berkus Method assigns dollar values to five key risk-reduction milestones: Sound Idea, Prototype, Quality Management Team, Strategic Relationships, and Product Rollout/Sales. The valuation is the sum of the values achieved.

$$V = \sum_{i=1}^{5} \text{Value}_i$$

---

## Risk Factor Summation

> *Full derivation coming in Phase 2. See [API docs](https://simonplmak-cloud.github.io/startup-valuation/api/core/#startup_valuation.core.risk_factor_summation) for the Python interface.*

The Risk Factor Summation method starts with a baseline valuation and adjusts up or down for each of 12 risk factors.

$$V = V_{base} \times \left(1 + \sum_{i=1}^{12} \Delta_i\right)$$

---

## VC Method

> *Full derivation coming in Phase 2. See [API docs](https://simonplmak-cloud.github.io/startup-valuation/api/core/#startup_valuation.core.vc_method_post_money) for the Python interface.*

The Venture Capital Method works backward from an expected exit value, discounting for the target return rate and accounting for dilution.

$$V_{post} = \frac{\text{Exit Value}}{(1 + \text{Target Return})^{\text{Years}}}$$

$$V_{pre} = V_{post} - \text{Investment}$$
