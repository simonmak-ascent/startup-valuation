# Tasks: Valuation Engine Implementation

**Version:** 1.0  
**Status:** Draft — Awaiting Gate 3 Approval  
**Reads:** `plan.md`, `spec.md`, `constitution.md`

---

## Task List

### Phase A: Core Library Foundation

#### T1: Project Scaffolding [P]
**Dependencies:** None  
**Complexity:** S  
**AC:** AC7

- Create `pyproject.toml` with hatch build system
- Create `src/startup_valuation/__init__.py`
- Create `tests/` directory with `conftest.py`
- Create `.github/workflows/ci.yml` (pytest on push)
- Create `README.md`, `LICENSE` (MIT), `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`

**Test:** `pip install -e .` succeeds, `pytest` runs (empty suite passes)

---

#### T2: Core Data Types [P]
**Dependencies:** T1  
**Complexity:** M  
**AC:** AC2

- Create `src/startup_valuation/types.py`
- Define `ValuationResult` dataclass (value, method, inputs, assumptions, sensitivity)
- Define `Distribution` dataclass (type, params)
- Define `Scenario` dataclass (name, probability, value)
- Define `SensitivityResult` dataclass

**Test:** All dataclasses instantiate correctly, type hints validate

---

#### T3: Probability Module
**Dependencies:** T2  
**Complexity:** M  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/probability.py`
- Implement: `expected_value_discrete`, `joint_probability`, `probability_weighted_value`, `portfolio_expected_return`, `poisson_probability`
- Each function: typed params, ValuationResult return, docstring with formula + example

**Test:** Unit tests against book examples:
- E[X] = 1×0.3 + 0×0.7 = 0.3
- Moderna: 0.90×0.70×0.60×0.85 = 0.32
- VC portfolio: 0.20(10)+0.30(2)+0.20(1)+0.30(0) = 2.8x

---

#### T4: Time Value Module
**Dependencies:** T2  
**Complexity:** S  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/tv.py`
- Implement: `present_value`, `net_present_value`, `annuity_present_value`

**Test:**
- PV = $11,000/(1.08)¹ = $10,185.19
- NPV = -$100K + $30K/1.1 + $40K/1.1² + $50K/1.1³ = -$2,103
- Annuity: $50K × 3.1699 = $158,495

---

#### T5: CAPM Module
**Dependencies:** T2  
**Complexity:** S  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/capm.py`
- Implement: `capm`, `portfolio_beta`, `startup_adjusted_capm`, `portfolio_variance`

**Test:**
- CAPM: 3% + 1.5(10%-3%) = 13.5%
- Portfolio beta: 0.60×0.8 + 0.40×1.2 = 0.96
- Startup CAPM: 4% + 1.3(7%) + 3% + 10% = 26.1%

---

#### T6: Core Valuation Module
**Dependencies:** T2, T3, T5  
**Complexity:** M  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/core.py`
- Implement: `scorecard_valuation`, `berkus_valuation`, `risk_factor_summation`, `vc_method_post_money`, `vc_method_pre_money`, `terminal_value_multiple`

**Test:**
- Scorecard: $1.5M × 1.200 = $1.8M
- Berkus: $500K + $400K + $500K + $500K + $0 = $1.9M
- VC Post-Money: $500M / 10 = $50M
- VC Pre-Money: $8M - $1.5M = $6.5M

---

### Phase B: Advanced Methods

#### T7: Black-Scholes & Binomial
**Dependencies:** T2  
**Complexity:** L  
**AC:** AC1, AC3, AC9

- Add to `src/startup_valuation/advanced.py`
- Implement: `black_scholes`, `binomial_tree`, `binomial_valuation`
- Use `math.erf` for N(d) calculation

**Test:**
- BS: S=$20M, K=$5M, r=5%, σ=40%, T=1yr → C=$15.24M
- BS: S=$100M, K=$30M, r=4%, σ=60%, T=3yr → C=$75.76M
- BS: S=$500M, K=$100M, r=4%, σ=60%, T=5yr → C=$427.62M

---

#### T8: Monte Carlo & Scenario Analysis
**Dependencies:** T2, T7  
**Complexity:** L  
**AC:** AC1, AC3, AC9, AC10

- Add to `src/startup_valuation/advanced.py`
- Implement: `monte_carlo_valuation`, `scenario_analysis`, `ltv_cac_valuation`
- Support numpy distributions (normal, uniform, triangular)

**Test:**
- Scenario: 0.20×$10M + 0.60×$5M + 0.20×$1M = $5.2M
- Four-scenario: 0.15×$20M + 0.50×$8M + 0.25×$3M + 0.10×$0.5M = $7.8M
- Monte Carlo: mean ≈ $3.5M (with seed for reproducibility)

---

### Phase C: Industry Modules

#### T9: Comparables Module
**Dependencies:** T2, T3  
**Complexity:** M  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/comparables.py`
- Implement: `pe_ratio`, `ps_ratio`, `ev_ebitda`, `ev_revenue`, `regression_adjusted_multiple`, `target_valuation_multiple`

**Test:**
- P/S: $500M/$100M = 5.0x
- Regression: 2.5 + 10(0.30) + 0.5(1) - 1.5(0) - 0.2(0) = 6.0x
- Snowflake: 10 + 0.25(121) + 0.15(158) = 64x

---

#### T10: SaaS Module
**Dependencies:** T2, T3  
**Complexity:** M  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/saas.py`
- Implement: `arr`, `mrr`, `cac`, `ltv_saas`, `net_revenue_retention`, `cac_payback_period`, `magic_number`, `rule_of_40`, `saas_revenue_multiple_valuation`

**Test:**
- LTV: (ARPU × Gross Margin) / Churn Rate
- Rule of 40: 118% + 1% = 119% ≥ 40% ✓
- Zoom: $400M ARR × 23x = $9.2B

---

#### T11: Biotech Module
**Dependencies:** T2, T3, T4  
**Complexity:** M  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/biotech.py`
- Implement: `rnPV`, `decision_tree_ev`, `peak_sales`, `pipeline_valuation`, `overall_success_probability`

**Test:**
- Decision tree: 0.35 × 0.60 × 0.90 × $500M = $94.5M
- Peak sales: 50K × 40% × $150K × 90% = $2.7B
- Pipeline: $2B × 5 × 0.60 / (1.12)² = $4.78B

---

#### T12: Fintech + Marketplace Modules
**Dependencies:** T2  
**Complexity:** M  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/fintech.py` and `marketplace.py`
- Fintech: `payment_revenue`, `max_loan_portfolio`, `network_effects_value`, `lending_fintech_valuation`
- Marketplace: `gmv`, `take_rate`, `liquidity`, `gmv_multiple_valuation`, `network_value`

**Test:**
- Payment: $640B × 1.16% = $7.4B
- Max loan: $100M / 0.08 = $1.25B
- Take rate: $2.9B / $24.7B = 11.7%
- DoorDash: $24.7B × 2.4x = $60B

---

#### T13: Hardware Module
**Dependencies:** T2, T3, T4  
**Complexity:** S  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/hardware.py`
- Implement: `trl_adjusted_valuation`, `gross_margin_hardware`, `break_even_volume`, `probability_weighted_dcf`

**Test:**
- TRL: $10B × 5% × 40% × 15 × (1 - 0.80) = $600M
- P-weighted DCF: 0.30($60B) + 0.40($10B) + 0.30($0) = $22B

---

### Phase D: International + Stakeholders + Emerging

#### T14: International Module
**Dependencies:** T2, T3, T4, T5  
**Complexity:** L  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/international.py`
- Implement: `purchasing_power_parity`, `interest_rate_parity`, `currency_adjusted_dcf`, `country_risk_premium`, `adjusted_capm_international`, `after_tax_cash_flow`, `sum_of_parts_valuation`

**Test:**
- PPP: 83 × (1.05/1.02) = 85.4 USD/INR
- CRP: 10.5% - 4.5% = 6.0%
- Adj CAPM: 4.5% + 1.2(6%) + 3% = 14.7%

---

#### T15: Stakeholders Module
**Dependencies:** T2, T3, T4, T7  
**Complexity:** L  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/stakeholders.py`
- Implement: `single_round_dilution`, `multi_round_dilution`, `acquisition_value`, `risk_adjusted_synergy`, `opm_common_stock`, `pwerm`, `common_stock_discount`, `intrinsic_option_value`, `probability_weighted_employee_value`, `vesting_adjusted_value`, `cash_equity_breakeven`, `venture_debt_dilution`, `liquidation_value`, `max_asset_based_loan`

**Test:**
- Dilution: 100% × (1 - $5M/$20M) = 75%
- OPM: V=$100M, K=$40M, T=3yr, σ=60% → Common=$65M (35% discount)
- Liquidation: $5M×100% + $3M×80% + $2M×30% = $8M
- Warrant: $300K/$40M = 0.75%

---

#### T16: Emerging Module
**Dependencies:** T2, T3, T4, T7, T8  
**Complexity:** L  
**AC:** AC1, AC3, AC9

- Create `src/startup_valuation/emerging.py`
- Implement: `safe_conversion_cap`, `safe_conversion_discount`, `safe_expected_value`, `equation_of_exchange`, `nvt_ratio`, `protocol_value`, `esg_adjusted_discount_rate`, `metcalfes_law`, `modified_metcalfes`, `network_density_valuation`, `data_moat_value`, `remote_cost_savings_npv`

**Test:**
- SAFE discount: $5 × (1 - 0.20) = $4/share
- MV=PQ: $10B / (10 × 100M) = $10/token
- Metcalfe: 100K users → index 10B; 200K → 40B
- ESG rate: 15% + 2% - 1% = 16%
- Remote NPV: $1.2M / 10-20% = $6-12M

---

### Phase E: MCP Server

#### T17: MCP Server Core
**Dependencies:** T6, T8, T9, T10, T11, T12, T13, T14, T15, T16  
**Complexity:** L  
**AC:** AC4, AC5

- Create `mcp_server/server.py`
- Set up FastMCP server
- Auto-register all library functions as MCP tools
- Implement stdio and SSE transport
- Create compound tool `valuation_full_analysis`

**Test:** Connect with MCP inspector, verify all tools appear with correct schemas

---

### Phase F: AI-Agent Skills

#### T18: AI-Agent Skills
**Dependencies:** T6, T8, T10, T11, T12, T13, T14, T15, T16  
**Complexity:** M  
**AC:** AC6

- Create 5 skill directories with SKILL.md files
- Each skill: workflow guidance, parameter prompts, interpretation guidance
- Cross-reference to textbook chapters

**Test:** Load each skill in OpenCode, verify workflow guidance is actionable

---

### Phase G: Documentation + GitHub Pages

#### T19: Documentation Site
**Dependencies:** T1-T16  
**Complexity:** M  
**AC:** AC8

- Set up MkDocs with mkdocstrings
- Configure auto-generated API reference
- Create examples pages
- Create book chapter index
- Configure GitHub Pages deployment

**Test:** `mkdocs build` succeeds, local preview renders correctly

---

### Phase H: CI/CD + Package + Publish

#### T20: CI/CD + Package + Publish
**Dependencies:** T1-T19  
**Complexity:** M  
**AC:** AC7, AC9, AC10

- Configure GitHub Actions CI (test on push, build docs on main)
- Set up `pyproject.toml` for PyPI publishing
- Create `CHANGELOG.md`
- Tag release v0.1.0
- Push to GitHub

**Test:** CI passes on push, package installs via `pip install -e .`, GitHub Pages deploys

---

## Dependency Graph

```
T1 ── T2 ──┬── T3 ──┬── T4 ──┬── T5 ──┬── T6 ──┐
           │        │        │        │        │
           │        │        │        │        ├── T7 ── T8
           │        │        │        │        ├── T9
           │        │        │        │        ├── T10
           │        │        │        │        ├── T11
           │        │        │        │        ├── T12
           │        │        │        │        ├── T13
           │        │        │        │        ├── T14
           │        │        │        │        ├── T15
           │        │        │        │        └── T16
           │        │        │        │              │
           │        │        │        │              └── T17 ── T18
           │        │        │        │                    │
           │        │        │        │                    └── T19 ── T20
           │        │        │        │
           │        │        │        └── T14 (also depends on T3,T4,T5)
           │        │        │
           │        │        └── T11 (also depends on T3,T4)
           │        │
           │        └── T10 (also depends on T3)
           │
           └── T9 (also depends on T3)

Parallel groups:
- T3, T4, T5 can run in parallel after T2
- T9-T16 can run in parallel after their dependencies
- T17 requires all library modules
- T18 requires all library modules
- T19 requires all library modules
- T20 requires everything
```

---

## Estimated Effort

| Task | Complexity | Est. Time |
|------|-----------|-----------|
| T1 | S | 10 min |
| T2 | M | 15 min |
| T3 | M | 20 min |
| T4 | S | 10 min |
| T5 | S | 10 min |
| T6 | M | 20 min |
| T7 | L | 30 min |
| T8 | L | 25 min |
| T9 | M | 15 min |
| T10 | M | 20 min |
| T11 | M | 20 min |
| T12 | M | 20 min |
| T13 | S | 10 min |
| T14 | L | 30 min |
| T15 | L | 35 min |
| T16 | L | 30 min |
| T17 | L | 30 min |
| T18 | M | 20 min |
| T19 | M | 20 min |
| T20 | M | 15 min |
| **Total** | | **~7 hours** |
