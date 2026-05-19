# Task List: Model Enhancement, Detailed Testing & Publication

## Plan Reference
Implements: `specs/model-enhancement-publish/plan.md`

## Tasks

### Phase 1: Missing Function Implementations

- [ ] **TASK-01** [M] Implement `expected_value_continuous` in probability.py
  - Creates: adds function to `src/startup_valuation/probability.py`
  - Formula: numerical integration using scipy.integrate.quad
  - Depends on: none
  - Tests: AC-3

- [ ] **TASK-02** [M] Implement `binomial_valuation` in advanced.py
  - Creates: adds function to `src/startup_valuation/advanced.py`
  - Wrapper around binomial_tree with startup-specific defaults (steps=50)
  - Depends on: none
  - Tests: AC-3

- [ ] **TASK-03** [M] Implement fintech missing functions
  - Creates: adds `payment_processor_valuation`, `neobank_valuation` to `src/startup_valuation/fintech.py`
  - Depends on: none
  - Tests: AC-3

- [ ] **TASK-04** [S] Implement marketplace missing functions
  - Creates: adds `buyer_retention`, `network_density` to `src/startup_valuation/marketplace.py`
  - Depends on: none
  - Tests: AC-3

- [ ] **TASK-05** [L] Implement stakeholders missing functions
  - Creates: adds `risk_adjusted_synergy`, `intrinsic_option_value`, `probability_weighted_employee_value`, `vesting_adjusted_value`, `cash_equity_breakeven`, `max_asset_based_loan` to `src/startup_valuation/stakeholders.py`
  - Depends on: none
  - Tests: AC-3

- [ ] **TASK-06** [L] Implement emerging missing functions
  - Creates: adds `safe_conversion_cap`, `safe_expected_value`, `nvt_ratio`, `esg_premium_valuation`, `esg_discount_valuation`, `data_moat_value`, `remote_first_premium` to `src/startup_valuation/emerging.py`
  - Depends on: none
  - Tests: AC-3

### Phase 2: MCP Server Updates

- [ ] **TASK-07** [M] Register all new functions in MCP server
  - Creates: updates `mcp_server/server.py` with new tool definitions
  - Depends on: TASK-01 through TASK-06
  - Tests: AC-3

### Phase 3: Per-Module Test Files

- [ ] **TASK-08** [M] Create test_tv.py
  - Creates: `tests/test_tv.py` with tests for present_value, net_present_value, annuity_present_value
  - Depends on: none
  - Tests: AC-1

- [ ] **TASK-09** [M] Create test_capm.py
  - Creates: `tests/test_capm.py` with tests for capm, portfolio_beta, startup_adjusted_capm, portfolio_variance
  - Depends on: none
  - Tests: AC-1

- [ ] **TASK-10** [M] Create test_core.py
  - Creates: `tests/test_core.py` with tests for scorecard, berkus, risk_factor_summation, vc_method, terminal_value_multiple
  - Depends on: none
  - Tests: AC-1

- [ ] **TASK-11** [M] Create test_advanced.py
  - Creates: `tests/test_advanced.py` with tests for black_scholes, binomial_tree, monte_carlo, scenario_analysis, ltv_cac
  - Depends on: TASK-02
  - Tests: AC-1

- [ ] **TASK-12** [M] Create test_comparables.py
  - Creates: `tests/test_comparables.py` with tests for pe_ratio, ps_ratio, ev_ebitda, ev_revenue, regression_adjusted_multiple, target_valuation_multiple
  - Depends on: none
  - Tests: AC-1

- [ ] **TASK-13** [M] Create test_saas.py
  - Creates: `tests/test_saas.py` with tests for arr, mrr, cac, ltv_saas, nrr, cac_payback, magic_number, rule_of_40, saas_revenue_multiple
  - Depends on: none
  - Tests: AC-1

- [ ] **TASK-14** [M] Create test_biotech.py
  - Creates: `tests/test_biotech.py` with tests for rnPV, decision_tree, peak_sales, pipeline, overall_success_probability
  - Depends on: none
  - Tests: AC-1

- [ ] **TASK-15** [M] Create test_fintech.py
  - Creates: `tests/test_fintech.py` with tests for payment_revenue, max_loan_portfolio, network_effects_value, lending_fintech_valuation, payment_processor_valuation, neobank_valuation
  - Depends on: TASK-03
  - Tests: AC-1

- [ ] **TASK-16** [M] Create test_marketplace.py
  - Creates: `tests/test_marketplace.py` with tests for gmv, take_rate, liquidity, gmv_multiple, network_value, buyer_retention, network_density
  - Depends on: TASK-04
  - Tests: AC-1

- [ ] **TASK-17** [M] Create test_hardware.py
  - Creates: `tests/test_hardware.py` with tests for trl_adjusted, gross_margin, break_even, probability_weighted_dcf
  - Depends on: none
  - Tests: AC-1

- [ ] **TASK-18** [M] Create test_international.py
  - Creates: `tests/test_international.py` with tests for ppp, irp, currency_adjusted_dcf, crp, crp_damodaran, adjusted_capm, after_tax_cf, sum_of_parts
  - Depends on: none
  - Tests: AC-1

- [ ] **TASK-19** [M] Create test_stakeholders.py
  - Creates: `tests/test_stakeholders.py` with tests for single_round_dilution, multi_round_dilution, acquisition_value, opm, pwerm, common_stock_discount, liquidation_value, venture_debt_dilution, plus all new functions
  - Depends on: TASK-05
  - Tests: AC-1

- [ ] **TASK-20** [M] Create test_emerging.py
  - Creates: `tests/test_emerging.py` with tests for safe_conversion_discount, equation_of_exchange, protocol_value, esg_adjusted_rate, metcalfes, modified_metcalfes, network_density_valuation, remote_cost_savings_npv, plus all new functions
  - Depends on: TASK-06
  - Tests: AC-1

- [ ] **TASK-21** [S] Enhance test_probability.py
  - Updates: `tests/test_probability.py` with tests for expected_value_continuous
  - Depends on: TASK-01
  - Tests: AC-1

- [ ] **TASK-22** [S] Consolidate test suite — remove test_core_modules.py and test_all_modules.py
  - Deletes: `tests/test_core_modules.py`, `tests/test_all_modules.py` (tests migrated to per-module files)
  - Depends on: TASK-08 through TASK-21
  - Tests: AC-1

### Phase 4: GitHub Pages Documentation

- [ ] **TASK-23** [M] Set up MkDocs Material
  - Creates: `mkdocs.yml`, `docs/index.md`, `docs/api/`, `docs/examples/`, `docs/chapters.md`
  - Adds: `mkdocs`, `mkdocstrings[python]`, `mkdocs-material` to pyproject.toml optional deps
  - Depends on: none
  - Tests: AC-4

- [ ] **TASK-24** [S] Add docs deploy workflow
  - Creates: `.github/workflows/docs.yml` for GitHub Pages deployment
  - Depends on: TASK-23
  - Tests: AC-4

### Phase 5: SEO & Repository Optimization

- [ ] **TASK-25** [S] Optimize README for SEO
  - Updates: `README.md` with keywords, textbook reference, citing section, module table
  - Depends on: none
  - Tests: AC-5, AC-6

- [ ] **TASK-26** [S] Create CITATION.cff
  - Creates: `CITATION.cff` with authors, title, version, abstract
  - Depends on: none
  - Tests: AC-10

- [ ] **TASK-27** [S] Add mypy to CI
  - Updates: `.github/workflows/ci.yml` with mypy step, add mypy to dev deps
  - Depends on: none
  - Tests: AC-7

- [ ] **TASK-28** [S] Create CHANGELOG.md
  - Creates: `CHANGELOG.md` with Keep a Changelog format
  - Depends on: none
  - Tests: AC-9

### Phase 6: Validation & Publish

- [ ] **TASK-29** [M] Run full test suite and verify coverage
  - Command: `pytest --cov=startup_valuation --cov-report=term-missing -v`
  - Target: ≥ 90% coverage, all tests passing
  - Depends on: TASK-01 through TASK-28
  - Tests: AC-1, AC-3

- [ ] **TASK-30** [S] Commit and push all changes
  - Command: `git add -A && git commit && git push`
  - Depends on: TASK-29
  - Tests: AC-5

## Legend
- `[S]` Small — under 1 hour
- `[M]` Medium — 1–3 hours
- `[L]` Large — 3–6 hours (consider splitting)
- `[P]` Parallelizable — can run concurrently with other `[P]` tasks at same level

## Dependency Graph

```
TASK-01..06 (new functions, parallel)
    │
    ├── TASK-07 (MCP server updates)
    │
TASK-08..21 (test files, mostly parallel after function impl)
    │
    └── TASK-22 (consolidate tests)
        │
TASK-23..28 (docs, SEO, CI — parallel)
    │
    └── TASK-29 (validate)
        │
        └── TASK-30 (push)
```
