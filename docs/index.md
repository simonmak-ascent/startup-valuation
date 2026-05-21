# Startup Valuation: A Comprehensive Guide

## Companion Library

This site is the companion documentation for the Python library implementing **80+ formulas** from the Startup Valuation textbook.

## Quick Start

```bash
pip install startup-valuation
```

```python
from startup_valuation.core import scorecard_valuation, vc_method_post_money
from startup_valuation.advanced import black_scholes

# Scorecard Method
result = scorecard_valuation(
    average_valuation=1_500_000,
    weights=[0.30, 0.25, 0.15, 0.10, 0.10, 0.05, 0.05],
    scores=[1.25, 1.50, 1.20, 0.75, 1.00, 0.90, 1.00],
)
print(f"Scorecard: ${result.value:,.0f}")  # $1,800,000

# Black-Scholes for real options
result = black_scholes(20_000_000, 5_000_000, 0.05, 0.40, 1.0)
print(f"Option value: ${result.value:,.0f}")  # $15,240,000
```

## Book Chapters → Library Modules

| Chapter | Topic | Library Module |
|---------|-------|----------------|
| 1 | Introduction to Startup Valuation | — |
| 2 | Probability, TVM, CAPM | `probability`, `tv`, `capm` |
| 3 | Core Valuation Methods | `core` |
| 4 | Advanced Methods | `advanced` |
| 5 | Comparables & Multiples | `comparables` |
| 6–10 | Specialized Topics | See textbook |
| 11 | Industry-Specific Models | `saas`, `biotech`, `fintech`, `marketplace`, `hardware` |
| 12 | International Valuation | `international` |
| 13 | Stakeholder Analysis | `stakeholders` |
| 14 | Emerging Methods | `emerging` |
| 15 | Conclusion & Best Practices | — |

## Features

- **80+ valuation formulas** across 14 modules covering every method in the textbook
- **Typed Python API** with structured `ValuationResult` returns (value + assumptions + sensitivity)
- **MCP Server** exposing all calculations as tools for AI agents (Claude, OpenCode, etc.)
- **AI-Agent Skills** with workflow guidance for 5 valuation domains
- **Every function tested** against textbook example values

## Modules

| Module | Methods | Chapter |
|--------|---------|---------|
| `probability` | Expected value, joint probability, Poisson | 2 |
| `tv` | PV, NPV, annuity | 2 |
| `capm` | CAPM, portfolio beta, startup-adjusted | 2 |
| `core` | Scorecard, Berkus, Risk Factor, VC Method | 3 |
| `advanced` | Black-Scholes, Binomial, Monte Carlo, Scenario | 4 |
| `comparables` | Multiples, regression-adjusted | 5 |
| `saas` | LTV, CAC, NRR, Magic Number, Rule of 40 | 11 |
| `biotech` | rNPV, decision tree, peak sales, pipeline | 11 |
| `fintech` | Payment revenue, lending, network effects | 11 |
| `marketplace` | GMV, take rate, liquidity, network density | 11 |
| `hardware` | TRL-adjusted, break-even, P-weighted DCF | 11 |
| `international` | PPP, CRP, currency-adjusted DCF | 12 |
| `stakeholders` | Dilution, OPM, PWERM, liquidation | 13 |
| `emerging` | SAFE, MV=PQ, ESG, Metcalfe's Law | 14 |

## MCP Server

```bash
cd mcp_server && python server.py
```

Connect with any MCP-compatible AI agent. All 60+ valuation tools are available.

## AI-Agent Skills

Copy the `skills/` directory to your agent's skills folder. Available skills:
- `valuation-core` — Scorecard, Berkus, VC Method, Risk Factor
- `valuation-advanced` — Black-Scholes, Monte Carlo, Scenario Analysis
- `valuation-industry` — SaaS, Biotech, Fintech, Marketplace, Hardware
- `valuation-stakeholder` — Dilution, OPM, PWERM, Liquidation
- `valuation-emerging` — SAFE, Crypto, ESG, Network Effects
- `valuation-foundations` — Probability, TVM, CAPM, Comparables, International

## Development

```bash
pip install -e ".[dev]"
pytest --cov=startup_valuation --cov-report=term-missing
ruff check .
```

## License

MIT
