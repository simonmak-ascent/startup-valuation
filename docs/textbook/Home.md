# Startup Valuation Engine

**80+ valuation formulas. Scientific rigor. Open source.**

A production-grade Python library implementing every formula from the *Startup Valuation* textbook. Designed for analysts, developers, students, and AI agents who need auditable, transparent valuation computations.

---

## Who are you?

| If you want to... | Start here |
|---|---|
| **Learn how startup valuation works** | [Start Here](Start-Here) — installation, 5-minute example |
| **Understand a specific valuation method** | [Methods](#methods) — pick a method below |
| **Value a real startup** | [How to Value a Startup](How-to-Value-a-Startup) — step-by-step workflow |
| **Use the Python library** | [API Reference](https://simonplmak-cloud.github.io/startup-valuation/) — auto-generated docs |
| **Use the MCP server with AI agents** | [MCP Server](https://github.com/simonplmak-cloud/startup-valuation/tree/main/mcp_server) — 60+ tools |
| **Contribute a new method** | [Contributing](https://github.com/simonplmak-cloud/startup-valuation/blob/main/CONTRIBUTING.md) |

## Methods

### Foundation
- [Probability & Time Value](Probability-and-Time-Value) — Expected value, NPV, Poisson, annuities
- [CAPM](CAPM) — Capital Asset Pricing Model, startup-adjusted beta

### Core Valuation
- [Core Methods](Core-Methods) — Scorecard, Berkus, Risk Factor Summation, VC Method

### Advanced
- [Advanced Methods](Advanced-Methods) — Black-Scholes, Binomial Trees, Monte Carlo, Scenario Analysis
- [Comparables](Comparables) — P/E, P/S, EV/EBITDA, regression-adjusted multiples

### Industry-Specific
- [SaaS Metrics](SaaS-Metrics) — LTV, CAC, NRR, Magic Number, Rule of 40
- [Biotech](Biotech) — rNPV, decision trees, peak sales, pipeline valuation
- [Fintech](Fintech) — Payment revenue, lending, neobank, network effects
- [Marketplace](Marketplace) — GMV, take rate, liquidity, network density
- [Hardware](Hardware) — TRL-adjusted, break-even, probability-weighted DCF

### Cross-Cutting
- [International](International) — PPP, CRP, currency-adjusted DCF
- [Stakeholders](Stakeholders) — Dilution, OPM, PWERM, liquidation preferences
- [Emerging](Emerging) — SAFE, MV=PQ (crypto), ESG, Metcalfe's Law

## Resources

| Resource | Link |
|---|---|
| 📦 PyPI | [pypi.org/project/startup-valuation](https://pypi.org/project/startup-valuation/) |
| 📖 API Docs | [simonplmak-cloud.github.io/startup-valuation](https://simonplmak-cloud.github.io/startup-valuation/) |
| 💻 Source Code | [github.com/simonplmak-cloud/startup-valuation](https://github.com/simonplmak-cloud/startup-valuation) |
| 📚 Textbook | [Startup Valuation on Amazon](https://www.amazon.com/Startup-Valuation-Comprehensive-Fast-Growing-Pre-Revenue-ebook/dp/B0FYTGNVWS/) |
| 🛠️ MCP Server | [`mcp_server/server.py`](https://github.com/simonplmak-cloud/startup-valuation/blob/main/mcp_server/server.py) |
| 📝 Changelog | [CHANGELOG.md](https://github.com/simonplmak-cloud/startup-valuation/blob/main/CHANGELOG.md) |

## Notation

See the [Glossary](Glossary) for the canonical symbol table mapping mathematical notation to code variables.

---

*Last verified: 2026-08-11 | Version: 1.0.2*
