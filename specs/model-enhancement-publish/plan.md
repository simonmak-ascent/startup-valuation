# Technical Plan: Model Enhancement, Detailed Testing & Publication

## Spec Reference
Implements: `specs/model-enhancement-publish/spec.md`

## Architecture Overview

Enhance the existing three-layer architecture (library → MCP server → skills) by:
1. Filling gaps in module implementations (missing functions from original plan)
2. Adding sensitivity analysis to all valuation functions
3. Splitting tests into per-module files with comprehensive coverage
4. Adding GitHub Pages documentation via MkDocs Material
5. Optimizing repository metadata for SEO and discoverability

## Component Breakdown

### C1: Missing Function Implementations
- **Responsibility:** Add functions from original plan.md that were not implemented
- **Location:** Existing module files in `src/startup_valuation/`
- **Functions to add:**
  - `probability.expected_value_continuous` — numerical integration using scipy
  - `advanced.binomial_valuation` — wrapper around binomial_tree with startup-specific params
  - `fintech.payment_processor_valuation` — full valuation combining payment revenue + growth
  - `fintech.neobank_valuation` — customer-based valuation for neobanks
  - `marketplace.buyer_retention` — buyer retention rate calculation
  - `marketplace.network_density` — ratio of actual to potential connections
  - `stakeholders.risk_adjusted_synergy` — synergy value with probability adjustment
  - `stakeholders.intrinsic_option_value` — intrinsic value of equity options
  - `stakeholders.probability_weighted_employee_value` — employee option value with vesting
  - `stakeholders.vesting_adjusted_value` — option value adjusted for vesting schedule
  - `stakeholders.cash_equity_breakeven` — salary tradeoff analysis
  - `stakeholders.max_asset_based_loan` — maximum loan based on collateral
  - `emerging.safe_conversion_cap` — SAFE conversion with cap
  - `emerging.safe_expected_value` — expected value across cap vs discount
  - `emerging.nvt_ratio` — Network Value to Transactions ratio
  - `emerging.esg_premium_valuation` — ESG premium impact on valuation
  - `emerging.esg_discount_valuation` — ESG discount impact on valuation
  - `emerging.data_moat_value` — data advantage valuation
  - `emerging.remote_first_premium` — remote-first company valuation premium
- **AC Coverage:** AC-3

### C2: Sensitivity Analysis Integration
- **Responsibility:** Add sensitivity analysis to every valuation function's return
- **Location:** All 14 module files
- **Approach:** Add `_compute_sensitivity()` helper that calculates ±10% impact on value for each numeric input, populate `ValuationResult.sensitivity` dict
- **AC Coverage:** AC-2

### C3: Per-Module Test Files
- **Responsibility:** Split tests into one file per module with comprehensive coverage
- **Location:** `tests/test_*.py` (one per module)
- **Files:**
  - `test_probability.py` — already exists, enhance
  - `test_tv.py` — new
  - `test_capm.py` — new
  - `test_core.py` — new
  - `test_advanced.py` — new
  - `test_comparables.py` — new
  - `test_saas.py` — new
  - `test_biotech.py` — new
  - `test_fintech.py` — new
  - `test_marketplace.py` — new
  - `test_hardware.py` — new
  - `test_international.py` — new
  - `test_stakeholders.py` — new
  - `test_emerging.py` — new
- **AC Coverage:** AC-1

### C4: GitHub Pages Documentation
- **Responsibility:** MkDocs Material site with API reference, examples, chapter index
- **Location:** `docs/` directory + `mkdocs.yml`
- **Pages:**
  - `index.md` — homepage with overview, quick start, features
  - `api/` — auto-generated API reference via mkdocstrings
  - `examples/` — interactive code examples per category
  - `chapters.md` — textbook chapter cross-reference index
- **CI:** Add deploy workflow to `.github/workflows/docs.yml`
- **AC Coverage:** AC-4

### C5: SEO & Repository Optimization
- **Responsibility:** Optimize README, pyproject.toml, and repo metadata for discoverability
- **Location:** `README.md`, `pyproject.toml`, GitHub repo topics
- **Changes:**
  - README: Add keywords, textbook reference, "Citing This Project" section
  - pyproject.toml: Add comprehensive keywords and classifiers
  - GitHub topics: startup, valuation, finance, python, mcp, ai-agent, vc, black-scholes, saas, biotech
  - Create `CITATION.cff`
- **AC Coverage:** AC-5, AC-6, AC-10

### C6: Type Checking in CI
- **Responsibility:** Add mypy to CI workflow
- **Location:** `.github/workflows/ci.yml`, `pyproject.toml`
- **AC Coverage:** AC-7

### C7: CHANGELOG & Release Tags
- **Responsibility:** Create CHANGELOG.md, set up release tagging
- **Location:** `CHANGELOG.md`, GitHub release workflow
- **AC Coverage:** AC-9

## AC Coverage Map

| AC | Component(s) | Notes |
|----|-------------|-------|
| AC-1: Per-Module Tests | C3 | 14 test files, one per module |
| AC-2: Sensitivity Analysis | C2 | All functions return sensitivity dict |
| AC-3: Missing Formulas | C1 | 19 new functions across 6 modules |
| AC-4: GitHub Pages | C4 | MkDocs Material + mkdocstrings |
| AC-5: SEO Repo | C5 | README, pyproject.toml, topics, CITATION.cff |
| AC-6: Cross-References | C5 | Chapter refs in all docstrings |
| AC-7: Type Checking | C6 | mypy in CI |
| AC-8: PyPI | Deferred | Requires PyPI credentials, manual step |
| AC-9: CHANGELOG | C7 | Keep a Changelog format |
| AC-10: CITATION.cff | C5 | Academic citation file |

## Technology Choices

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Type checker | mypy | Widely used, simpler setup than pyright |
| Docs framework | MkDocs Material | Better search, theming, navigation |
| API docs | mkdocstrings | Auto-generates from docstrings |
| CI deploy | GitHub Actions pages | Free, integrated, no external services |

## Integration Points

- Existing modules: new functions must follow same `ValuationResult` return pattern
- MCP server: new functions must be registered as tools in `mcp_server/server.py`
- Tests: must use same `pytest.approx` tolerance pattern as existing tests

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Sensitivity analysis slows down tests | Low | Low | Only compute sensitivity on explicit request, not in hot path |
| MkDocs build fails on complex docstrings | Low | Medium | Test locally before deploying, simplify docstrings if needed |
| Missing function formulas ambiguous | Medium | High | Cross-reference with textbook output markdown in `output/` |
| Scope creep with 19 new functions | Medium | Medium | Implement in priority order, defer non-critical ones |

## Out of Scope (Technical)

- No PyPI publish in this iteration (requires credentials setup)
- No web-based calculator UI
- No database persistence
- No changes to existing function signatures
