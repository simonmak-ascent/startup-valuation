# Spec: Model Enhancement, Detailed Testing & Publication

**Version:** 1.0
**Status:** Draft — Awaiting Gate 1 Approval
**Feature Branch:** `model-enhancement-publish`

---

## Overview

Enhance the startup valuation library with additional formulas, comprehensive test coverage, GitHub Pages documentation, and SEO-optimized publication materials that reference the source textbook.

---

## User Stories

| # | Story | Priority |
|---|-------|----------|
| US1 | As a developer, I want every module to have per-module test files so I can run focused tests | MUST |
| US2 | As a financial analyst, I want sensitivity analysis on every valuation function so I can understand input impact | MUST |
| US3 | As a user, I want GitHub Pages documentation with API reference and examples so I can learn the library | MUST |
| US4 | As a potential contributor, I want SEO-optimized README and repo metadata so I can discover the project | MUST |
| US5 | As a student, I want clear cross-references to the textbook chapters so I can correlate code with book content | MUST |
| US6 | As a developer, I want missing formulas from the original plan implemented so the library is complete | MUST |
| US7 | As a user, I want the package published to PyPI so I can install via `pip install` | SHOULD |
| US8 | As a developer, I want type checking (mypy or pyright) in CI so I can catch type errors early | SHOULD |
| US9 | As a maintainer, I want a CHANGELOG and release tags so users can track versions | SHOULD |
| US10 | As a researcher, I want a citation file (CITATION.cff) so I can reference the project academically | COULD |

---

## Acceptance Criteria

### AC-1: Per-Module Test Coverage [MUST]
**Given** the test suite
**When** run with `pytest --cov=startup_valuation --cov-report=term-missing`
**Then**:
- Each of the 14 modules has its own test file (`test_probability.py`, `test_tv.py`, etc.)
- Every public function has at least one unit test
- All textbook example values are tested with `pytest.approx` tolerance
- Coverage ≥ 90% across all modules
- Tests run in < 30 seconds

### AC-2: Sensitivity Analysis on All Functions [MUST]
**Given** any valuation function
**When** called
**Then** the returned `ValuationResult` includes a `sensitivity` dict with ±10% impact on `value` for each numeric input

### AC-3: Missing Formula Implementation [MUST]
**Given** the original plan.md component list (C1-C15)
**When** compared to current codebase
**Then** all planned functions are implemented:
- `probability`: `expected_value_continuous` (numerical integration)
- `capm`: `portfolio_variance`
- `core`: `terminal_value_multiple`
- `advanced`: `binomial_tree`, `binomial_valuation`
- `comparables`: `pe_ratio`, `ps_ratio`, `ev_ebitda`, `ev_revenue`
- `saas`: `arr`, `mrr`, `cac`, `net_revenue_retention`, `cac_payback_period`, `magic_number`
- `biotech`: `rnPV`, `overall_success_probability`
- `fintech`: `max_loan_portfolio`, `network_effects_value`, `payment_processor_valuation`, `neobank_valuation`
- `marketplace`: `gmv`, `liquidity`, `network_density`, `buyer_retention`
- `hardware`: `gross_margin_hardware`
- `international`: `interest_rate_parity`, `currency_adjusted_dcf`, `local_discount_rate`, `after_tax_cash_flow`, `sum_of_parts_valuation`
- `stakeholders`: `multi_round_dilution`, `acquisition_value`, `risk_adjusted_synergy`, `common_stock_discount`, `intrinsic_option_value`, `probability_weighted_employee_value`, `vesting_adjusted_value`, `cash_equity_breakeven`, `venture_debt_dilution`, `max_asset_based_loan`
- `emerging`: `safe_conversion_cap`, `safe_expected_value`, `nvt_ratio`, `protocol_value`, `esg_premium_valuation`, `esg_discount_valuation`, `modified_metcalfes`, `network_density_valuation`, `data_moat_value`, `remote_first_premium`

### AC-4: GitHub Pages Documentation [MUST]
**Given** the GitHub Pages site is published
**When** a user visits it
**Then** they see:
- Homepage with project overview and quick start
- API reference for every function (auto-generated from docstrings via MkDocs)
- Examples page with interactive code snippets
- Book chapter cross-reference index mapping each function to its chapter
- Search functionality

### AC-5: SEO-Optimized Repository [MUST]
**Given** a user searches GitHub or Google for "startup valuation python"
**When** they find this repository
**Then**:
- README.md includes keywords: startup valuation, VC method, Scorecard, Berkus, Black-Scholes, MCP, AI agent
- `pyproject.toml` has descriptive keywords and classifiers
- Repository has a topic list: `startup`, `valuation`, `finance`, `python`, `mcp`, `ai-agent`, `vc`, `black-scholes`, `saas`, `biotech`
- README links to the source textbook
- README includes a "Citing This Project" section

### AC-6: Textbook Cross-References [MUST]
**Given** any module or function
**When** viewing its docstring or documentation
**Then** it includes a "Chapter X" reference to the corresponding textbook chapter

### AC-7: Type Checking in CI [SHOULD]
**Given** the CI workflow
**When** a PR is opened
**Then** `mypy` or `pyright` runs and passes with zero errors

### AC-8: PyPI Publication [SHOULD]
**Given** the package
**When** published to PyPI
**Then**:
- `pip install startup-valuation` works
- Package metadata includes description, license, Python version, homepage
- Source distribution and wheel are both published

### AC-9: CHANGELOG and Release Tags [SHOULD]
**Given** the repository
**When** a release is made
**Then**:
- `CHANGELOG.md` follows Keep a Changelog format
- Git tag matches the version in `pyproject.toml`
- GitHub release includes auto-generated notes

### AC-10: CITATION.cff [COULD]
**Given** the repository root
**When** a researcher wants to cite the project
**Then** a valid `CITATION.cff` file exists with authors, title, version, DOI placeholder, and abstract

---

## Boundaries

### Always Do
- Match textbook formulas exactly (verified against book examples)
- Return `ValuationResult` from every function (never bare numbers)
- Include chapter reference in every docstring
- Test every function against book example values
- Use `pytest.approx` with appropriate tolerance for floating-point comparisons

### Ask First
- Whether to add a web-based calculator UI
- Whether to add database persistence for valuation sessions
- Whether to support additional output formats (PDF reports)

### Never Do
- Hard-code book example values as defaults
- Return bare numbers without context
- Use floating-point comparisons without tolerance
- Mix business logic with presentation logic
- Expose internal implementation details in MCP tool schemas
- Modify existing function signatures without deprecation notice

---

## Out of Scope

- Web application / SaaS product
- Real-time market data integration
- Portfolio management features
- Multi-currency real-time conversion
- User authentication or accounts
- Payment processing
- Mobile app

---

## Open Questions

| # | Question | Status |
|---|----------|--------|
| Q1 | Should we use mypy or pyright for type checking? | [RESOLVED: mypy — simpler setup, widely used in Python ecosystem] |
| Q2 | Should GitHub Pages use MkDocs Material or plain MkDocs? | [RESOLVED: MkDocs Material — better search, theming] |
| Q3 | Should PyPI publish happen via GitHub Actions or manually? | [RESOLVED: GitHub Actions with trusted publishing] |
| Q4 | What tolerance should we use for floating-point comparisons? | [RESOLVED: pytest.approx(abs=1) for dollar values, abs=0.01 for ratios] |

---

## Non-Functional Requirements

- Performance: All 50+ tests must complete in < 30 seconds
- Coverage: ≥ 90% line coverage across all modules
- Type safety: Zero mypy errors on strict mode
- Documentation: Every public function must have a docstring with formula, parameters, example, and chapter reference

---

## Validation Checklist (Pre-Gate 1)

- [ ] Every `[MUST]` AC is independently testable
- [ ] No implementation details in the spec (no specific library names in ACs)
- [ ] Error and edge case ACs exist (invalid inputs, edge cases)
- [ ] No vague terms — replaced with measurable criteria
- [ ] Scope boundaries explicit
- [ ] All `[NEEDS CLARIFICATION]` items resolved
