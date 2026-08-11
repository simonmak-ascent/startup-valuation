# Glossary

> Canonical reference for all terminology, notation, and abbreviations used across the Startup Valuation Engine.

## Valuation Terms

| Term | Definition |
|---|---|
| **Pre-money valuation** | Company value before new investment capital is injected. |
| **Post-money valuation** | Company value after new investment: $$V_{post} = V_{pre} + \text{Investment}$$. |
| **Terminal value** | Estimated company value at a future exit event (IPO, acquisition). |
| **Discount rate** | Rate used to convert future cash flows to present value. Reflects risk and time preference. |
| **Risk-free rate** | Return on a zero-risk investment (typically US Treasury bonds). |

## Valuation Methods

| Method | Category | Description |
|---|---|---|
| **Scorecard Method** | Core | Adjusts average regional valuation by weighted factor scores (team, product, market, etc.). See [Core Methods](Core-Methods). |
| **Berkus Method** | Core | Assigns dollar values to five risk-reduction milestones. Max $2.5M pre-revenue. |
| **Risk Factor Summation** | Core | Adjusts base valuation by 12 risk factors, each ±$250K per unit. |
| **VC Method** | Core | Works backward from expected exit value, discounting for target return. |
| **Black-Scholes** | Advanced | Option pricing model for startup equity as real options. Uses $$N(d)$$ cumulative normal. |
| **Binomial Tree** | Advanced | Discrete-time option pricing with up/down steps. Converges to Black-Scholes. |
| **Monte Carlo** | Advanced | Simulates thousands of scenarios for probabilistic valuation ranges. |
| **Scenario Analysis** | Advanced | Discrete probability-weighted scenarios (bull/base/bear). |

## Industry Metrics

| Term | Industry | Definition |
|---|---|---|
| **ARR** | SaaS | Annual Recurring Revenue — committed subscription revenue per year. |
| **MRR** | SaaS | Monthly Recurring Revenue — ARR ÷ 12. |
| **CAC** | SaaS | Customer Acquisition Cost — sales & marketing spend ÷ new customers. |
| **LTV** | SaaS | Lifetime Value — average revenue per customer over their lifetime. |
| **NRR** | SaaS | Net Revenue Retention — revenue retained from existing customers (includes expansion). |
| **Churn Rate** | SaaS | Percentage of customers lost per period. |
| **Magic Number** | SaaS | SaaS efficiency: quarterly ARR growth ÷ prior-quarter S&M spend. |
| **Rule of 40** | SaaS | Growth rate + profit margin should exceed 40%. |
| **GMV** | Marketplace | Gross Merchandise Value — total transaction value through the platform. |
| **Take Rate** | Marketplace | Platform's revenue as % of GMV. |
| **rNPV** | Biotech | Risk-adjusted Net Present Value — clinical-stage asset valuation. |
| **TRL** | Hardware | Technology Readiness Level — 1 (basic principles) to 9 (proven in operation). |

## Financial Mathematics

| Term | Symbol | Definition |
|---|---|---|
| **Present Value** | $$PV$$ | Current value of future cash flows: $$PV = CF_t / (1 + r)^t$$. |
| **Net Present Value** | $$NPV$$ | Sum of all discounted cash flows minus initial investment. |
| **Expected Value** | $$E[X]$$ | Probability-weighted average: $$E[X] = \sum x_i \cdot P(X=x_i)$$. |
| **Standard Normal CDF** | $$N(d)$$ | Cumulative probability up to $$d$$ under standard normal. Used in Black-Scholes. |
| **Poisson Distribution** | $$P(k;\lambda)$$ | Probability of $$k$$ events in fixed interval: $$(\lambda^k e^{-\lambda}) / k!$$. |
| **CAPM** | — | Capital Asset Pricing Model: $$r = r_f + \beta(r_m - r_f)$$. |
| **Beta** | $$\beta$$ | Measure of systematic risk relative to market. |
| **Alpha** | $$\alpha$$ | Excess return over CAPM-predicted return (Jensen's alpha). |
| **Country Risk Premium** | $$CRP$$ | Additional return demanded for investing in a specific country. |
| **PPP** | — | Purchasing Power Parity — exchange rate adjustment for inflation differentials. |

## Abbreviations

| Abbreviation | Full Name |
|---|---|
| **API** | Application Programming Interface |
| **CAPM** | Capital Asset Pricing Model |
| **CI** | Continuous Integration |
| **CRP** | Country Risk Premium |
| **DCF** | Discounted Cash Flow |
| **IPO** | Initial Public Offering |
| **MCP** | Model Context Protocol |
| **M&A** | Mergers and Acquisitions |
| **OPM** | Option Pricing Model |
| **P/E** | Price-to-Earnings ratio |
| **P/S** | Price-to-Sales ratio |
| **PWERM** | Probability-Weighted Expected Return Method |
| **SAFE** | Simple Agreement for Future Equity |
| **SaaS** | Software as a Service |
| **VC** | Venture Capital |
| **WACC** | Weighted Average Cost of Capital |

---

*See [Notation](https://github.com/simonplmak-cloud/startup-valuation/blob/main/docs/notation.md) for the canonical symbol table mapping mathematics to code.*
