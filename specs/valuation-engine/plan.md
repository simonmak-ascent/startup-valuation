# Plan: Valuation Engine — Architecture & Implementation

**Version:** 1.0  
**Status:** Draft — Awaiting Gate 2 Approval  
**Reads:** `spec.md`, `constitution.md`

---

## Architecture

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────┐
│              AI-Agent Skills Layer               │
│  (OpenCode/Claude skill definitions + prompts)   │
├─────────────────────────────────────────────────┤
│              MCP Server Layer                    │
│  (FastMCP server exposing tools via stdio/SSE)   │
├─────────────────────────────────────────────────┤
│              Python Library Layer                │
│  (Pure computation, zero side effects, typed)    │
└─────────────────────────────────────────────────┘
```

### Layer 1: Python Library (`startup_valuation/`)

Pure computation library. No I/O, no side effects. Every function:
- Takes typed parameters
- Returns `ValuationResult` dataclass
- Has docstring with formula + example
- Has unit test against book values

### Layer 2: MCP Server (`mcp_server/`)

FastMCP server that wraps every library function as an MCP tool.
- Auto-generates tool schemas from function signatures
- Supports stdio and SSE transport
- Compound tools for multi-method analysis

### Layer 3: AI-Agent Skills (`skills/`)

OpenCode-compatible skill definitions:
- SKILL.md files with workflow guidance
- Parameter collection prompts
- Result interpretation guidance
- Cross-references to textbook chapters

### Layer 4: Documentation (`docs/`)

GitHub Pages site (MkDocs or Sphinx):
- Auto-generated API reference
- Interactive examples
- Book chapter index

---

## Component Breakdown

### C1: Core Data Types
- `ValuationResult` — structured return type
- `Distribution` — for Monte Carlo (normal, uniform, triangular)
- `Scenario` — for scenario analysis
- `Sensitivity` — sensitivity analysis results

### C2: Probability Module (`valuation/probability.py`)
- `expected_value_discrete()` — E[X] = Σ xᵢP(X=xᵢ)
- `expected_value_continuous()` — numerical integration
- `joint_probability()` — P(total) = Π Pᵢ
- `probability_weighted_value()` — E[V] = Σ pᵢVᵢ
- `portfolio_expected_return()` — E[R] = Σ pᵢRᵢ
- `poisson_probability()` — P(X=k) = e⁻λ·λᵏ/k!

### C3: Time Value Module (`valuation/tv.py`)
- `present_value()` — PV = C/(1+r)ᵗ
- `net_present_value()` — NPV = Σ Cₜ/(1+r)ᵗ
- `annuity_present_value()` — PV = C×[(1-(1+r)⁻ⁿ)/r]

### C4: CAPM Module (`valuation/capm.py`)
- `capm()` — E(Rᵢ) = Rf + βᵢ(E(Rm) - Rf)
- `portfolio_beta()` — βp = Σ wᵢβᵢ
- `startup_adjusted_capm()` — with size/startup premiums
- `portfolio_variance()` — Var(Rp) = ΣΣ wᵢwⱼCov(Rᵢ,Rⱼ)

### C5: Core Valuation Module (`valuation/core.py`)
- `scorecard_valuation()` — V = V_avg × Σ wᵢsᵢ
- `berkus_valuation()` — V = Σ vᵢ (max $2.5M)
- `risk_factor_summation()` — V = V_base × (1 + Σ rᵢ×0.025)
- `vc_method_post_money()` — Post = Terminal/ROI
- `vc_method_pre_money()` — Pre = Post - Investment
- `terminal_value_multiple()` — TV = Revenue × Multiple

### C6: Advanced Module (`valuation/advanced.py`)
- `black_scholes()` — C = N(d₁)S - N(d₂)Ke⁻ʳᵀ
- `binomial_tree()` — u, d, p factors + tree valuation
- `monte_carlo_valuation()` — simulation with distributions
- `scenario_analysis()` — expected value across scenarios
- `ltv_cac_valuation()` — (LTV/CAC) × Market Size × 0.1

### C7: Comparables Module (`valuation/comparables.py`)
- `pe_ratio()`, `ps_ratio()`, `ev_ebitda()`, `ev_revenue()`
- `regression_adjusted_multiple()` — Multiple = β₀ + β₁g + ...
- `target_valuation_multiple()` — Valuation = Multiple × Metric

### C8: SaaS Module (`valuation/saas.py`)
- `arr()`, `mrr()`, `cac()`, `ltv_saas()`
- `net_revenue_retention()`
- `cac_payback_period()`
- `magic_number()`
- `rule_of_40()`
- `saas_revenue_multiple_valuation()`

### C9: Biotech Module (`valuation/biotech.py`)
- `rnPV()` — risk-adjusted NPV
- `decision_tree_ev()` — EV = Π pᵢ × Terminal Value
- `peak_sales()` — Population × Penetration × Price × Compliance
- `pipeline_valuation()` — Σ(Peak Sales × Multiple × P_success)/(1+r)ⁿ
- `overall_success_probability()` — Π P_stage

### C10: Fintech Module (`valuation/fintech.py`)
- `payment_revenue()` — Volume × Take Rate
- `max_loan_portfolio()` — Equity / Capital Ratio
- `network_effects_value()` — Value ∝ Users^α
- `payment_processor_valuation()`
- `lending_fintech_valuation()`
- `neobank_valuation()`

### C11: Marketplace Module (`valuation/marketplace.py`)
- `gmv()`, `take_rate()`, `liquidity()`
- `network_density()`
- `buyer_retention()`
- `gmv_multiple_valuation()`
- `network_value()` — k × Users^α

### C12: Hardware Module (`valuation/hardware.py`)
- `trl_adjusted_valuation()`
- `gross_margin_hardware()`
- `break_even_volume()`
- `probability_weighted_dcf()`

### C13: International Module (`valuation/international.py`)
- `purchasing_power_parity()`
- `interest_rate_parity()`
- `currency_adjusted_dcf()`
- `local_discount_rate()`
- `country_risk_premium()` — sovereign spread, Damodaran, relative vol
- `adjusted_capm_international()`
- `after_tax_cash_flow()`
- `sum_of_parts_valuation()`

### C14: Stakeholders Module (`valuation/stakeholders.py`)
- `vc_method()` — post-money, pre-money
- `pe_valuation()` — EBITDA × Multiple
- `cvc_premium_valuation()`
- `single_round_dilution()`
- `multi_round_dilution()`
- `acquisition_value()` — Standalone + Synergies - Integration
- `risk_adjusted_synergy()`
- `opm_common_stock()` — Black-Scholes for common
- `pwerm()` — probability-weighted expected return
- `common_stock_discount()`
- `intrinsic_option_value()`
- `probability_weighted_employee_value()`
- `vesting_adjusted_value()`
- `cash_equity_breakeven()`
- `venture_debt_dilution()`
- `liquidation_value()`
- `max_asset_based_loan()`

### C15: Emerging Module (`valuation/emerging.py`)
- `safe_conversion_cap()`
- `safe_conversion_discount()`
- `safe_expected_value()`
- `equation_of_exchange()` — MV = PQ → token value
- `nvt_ratio()`
- `protocol_value()` — TVL × Multiple
- `esg_adjusted_discount_rate()`
- `esg_premium_valuation()`
- `esg_discount_valuation()`
- `metcalfes_law()` — V = k × n²
- `modified_metcalfes()` — V ∝ n^α
- `network_density_valuation()`
- `data_moat_value()`
- `ai_talent_premium()`
- `remote_cost_savings_npv()`
- `remote_first_premium()`

### C16: MCP Server (`mcp_server/server.py`)
- FastMCP server wrapping all functions
- Auto-generates tools from module functions
- stdio + SSE transport
- Compound tools for multi-method analysis

### C17: AI-Agent Skills (`skills/`)
- 5 skill definitions with SKILL.md
- Workflow guidance per skill
- Parameter collection prompts
- Result interpretation

### C18: Documentation (`docs/`)
- MkDocs with mkdocstrings
- Auto-generated API reference
- Examples per module
- Book chapter index

---

## Technology Choices

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Core library | Python 3.10+ | Data science ecosystem, textbook examples in Python |
| Type hints | `typing` + `dataclasses` | Built-in, no dependencies |
| Math | `math` (stdlib), `numpy` (optional) | stdlib for simple, numpy for Monte Carlo |
| MCP server | `fastmcp` | Simpler than raw MCP SDK, auto-generates schemas |
| Testing | `pytest` | Standard, fixtures, parametrization |
| Docs | `mkdocs` + `mkdocstrings` | Clean output, auto-generates from docstrings |
| CI | GitHub Actions | Free, integrated, matrix testing |
| Packaging | `pyproject.toml` + `hatch` | Modern Python packaging |

---

## Traceability: AC → Component

| AC | Components |
|----|-----------|
| AC1: Library Structure | C1-C15 |
| AC2: Function Signatures | C1 (ValuationResult) |
| AC3: All 80+ Formulas | C2-C15 |
| AC4: MCP Server | C16 |
| AC5: MCP Transport | C16 |
| AC6: AI-Agent Skills | C17 |
| AC7: GitHub Repo | All (repo structure) |
| AC8: GitHub Pages | C18 |
| AC9: Test Coverage | pytest across all modules |
| AC10: Package Distribution | pyproject.toml |

---

## Directory Structure

```
startup-valuation/
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── startup_valuation/
│       ├── __init__.py
│       ├── types.py              # C1: ValuationResult, Distribution, etc.
│       ├── probability.py        # C2
│       ├── tv.py                 # C3
│       ├── capm.py               # C4
│       ├── core.py               # C5
│       ├── advanced.py           # C6
│       ├── comparables.py        # C7
│       ├── saas.py               # C8
│       ├── biotech.py            # C9
│       ├── fintech.py            # C10
│       ├── marketplace.py        # C11
│       ├── hardware.py           # C12
│       ├── international.py      # C13
│       ├── stakeholders.py       # C14
│       └── emerging.py           # C15
├── tests/
│   ├── test_probability.py
│   ├── test_tv.py
│   ├── test_capm.py
│   ├── test_core.py
│   ├── test_advanced.py
│   ├── test_comparables.py
│   ├── test_saas.py
│   ├── test_biotech.py
│   ├── test_fintech.py
│   ├── test_marketplace.py
│   ├── test_hardware.py
│   ├── test_international.py
│   ├── test_stakeholders.py
│   └── test_emerging.py
├── mcp_server/
│   ├── __init__.py
│   ├── server.py                 # C16
│   └── tools.py                  # Auto-generated tool definitions
├── skills/
│   ├── valuation-core/
│   │   └── SKILL.md
│   ├── valuation-advanced/
│   │   └── SKILL.md
│   ├── valuation-industry/
│   │   └── SKILL.md
│   ├── valuation-stakeholder/
│   │   └── SKILL.md
│   └── valuation-emerging/
│       └── SKILL.md
└── docs/
    ├── index.md
    ├── api/
    │   ├── probability.md
    │   ├── tv.md
    │   └── ...
    └── examples/
        ├── core-methods.md
        ├── advanced-methods.md
        └── ...
```

---

## Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Formula implementation errors | High | Medium | Test every function against book examples with exact values |
| MCP server schema generation fails | Medium | Low | Manual schema fallback, test with MCP inspector |
| Monte Carlo performance | Low | Low | Use numpy vectorization, configurable iterations |
| GitHub Pages build failures | Low | Low | Use simple MkDocs config, test locally first |
| Scope creep (80+ formulas) | High | High | Implement core modules first, extend iteratively |

---

## Execution Strategy

1. **Phase A:** Core library foundation (types + probability + TV + CAPM + core)
2. **Phase B:** Advanced methods (Black-Scholes, Binomial, Monte Carlo, Scenario)
3. **Phase C:** Industry modules (SaaS, Biotech, Fintech, Marketplace, Hardware)
4. **Phase D:** International + Stakeholders + Emerging
5. **Phase E:** MCP Server
6. **Phase F:** AI-Agent Skills
7. **Phase G:** Documentation + GitHub Pages
8. **Phase H:** CI/CD + Package + Publish
