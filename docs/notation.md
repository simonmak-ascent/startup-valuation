# Notation — Canonical Symbol Table

> All Wiki derivations and docstrings reference this table. One notation system across the entire library.

## Valuation Variables

| Symbol | Meaning | Units | Code Variable | Module |
|---|---|---|---|---|
| $$V$$ | Valuation (output) | USD | `result.value` | all |
| $$V_{avg}$$ | Average regional pre-money valuation | USD | `average_valuation` | `core` |
| $$V_{pre}$$ | Pre-money valuation | USD | `result.value` | `core` |
| $$V_{post}$$ | Post-money valuation | USD | `result.value` | `core` |
| $$V_{base}$$ | Base valuation from comparables | USD | `base_valuation` | `core` |

## Scorecard Method

| Symbol | Meaning | Units | Code Variable |
|---|---|---|---|
| $$w_i$$ | Factor weight $$i$$ ($$\sum w_i = 1$$) | Dimensionless | `weights[i]` |
| $$s_i$$ | Factor score $$i$$ (1.0 = average) | Dimensionless | `scores[i]` |
| $$n$$ | Number of factors (typically 7) | Count | `len(weights)` |

## Time Value

| Symbol | Meaning | Units | Code Variable |
|---|---|---|---|
| $$r$$ | Discount rate (risk-free or WACC) | Annual % | `rate` |
| $$t$$ | Time (years) | Years | `time_to_maturity` |
| $$T$$ | Total time horizon | Years | `years` |
| $$CF_t$$ | Cash flow at time $$t$$ | USD | `cashflows[t]` |
| $$PV$$ | Present value | USD | `result.value` |
| $$NPV$$ | Net present value | USD | `result.value` |

## Option Pricing (Black-Scholes)

| Symbol | Meaning | Units | Code Variable |
|---|---|---|---|
| $$S$$ | Underlying asset value | USD | `underlying` |
| $$K$$ | Strike price | USD | `strike` |
| $$\sigma$$ | Volatility | Annual % | `volatility` |
| $$T$$ | Time to maturity | Years | `time_to_maturity` |
| $$r_f$$ | Risk-free rate | Annual % | `risk_free_rate` |
| $$N(d)$$ | Standard normal CDF | Probability | `scipy.stats.norm.cdf(d)` |
| $$d_1$$ | Intermediate term 1 | Dimensionless | (computed) |
| $$d_2$$ | Intermediate term 2 | Dimensionless | (computed) |
| $$C$$ | Call option value | USD | `result.value` |

## SaaS Metrics

| Symbol | Meaning | Units | Code Variable |
|---|---|---|---|
| $$ARR$$ | Annual Recurring Revenue | USD/year | `arr_value` |
| $$MRR$$ | Monthly Recurring Revenue | USD/month | `mrr_value` |
| $$CAC$$ | Customer Acquisition Cost | USD | `result.value` |
| $$LTV$$ | Lifetime Value | USD | `result.value` |
| $$NRR$$ | Net Revenue Retention | % | `result.value` |
| $$\text{Churn}$$ | Customer churn rate | %/period | `churn_rate` |

## Risk & Probability

| Symbol | Meaning | Units | Code Variable |
|---|---|---|---|
| $$P(X)$$ | Probability of event $$X$$ | [0, 1] | `probability` |
| $$\lambda$$ | Poisson rate parameter | Events/period | `lambda_` |
| $$E[X]$$ | Expected value of $$X$$ | Same as $$X$$ | `result.value` |
| $$\beta$$ | Portfolio beta | Dimensionless | `beta` |
| $$\alpha$$ | Jensen's alpha | % | `alpha` |

## Biotech

| Symbol | Meaning | Units | Code Variable |
|---|---|---|---|
| $$P_{success}$$ | Probability of clinical success | [0, 1] | `success_probability` |
| $$D_{cost}$$ | Development cost | USD | `development_cost` |
| $$rNPV$$ | Risk-adjusted net present value | USD | `result.value` |

## Formatting Rules

1. **Display math** on its own line: `$$V = V_{avg} \times \sum w_i \times s_i$$`
2. **Inline math** within text: `$$V_{avg}$$`
3. **Subscripts** for indices: `w_i` (not `wi`)
4. **Units** always stated explicitly
5. **Consistent notation** across all Wiki pages and docstrings — never switch between $$x_i$$ and `x[i]` without explanation
