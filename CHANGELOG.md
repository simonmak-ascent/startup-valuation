# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] — 2026-05-20

### Added
- Book-aligned documentation site with Amazon purchase link
- Book hero section on homepage with cover image and description
- Chapter-to-module mapping table
- Ascent Partners branding (logo, `#0083AB` color, Titillium Web/Open Sans fonts)
- `expected_value_continuous` — numerical integration for continuous random variables
- `binomial_valuation` — high-resolution binomial tree (steps=50) for startup options
- `payment_processor_valuation` — DCF-based payment processor valuation
- `neobank_valuation` — customer-based LTV × P/E neobank valuation
- `buyer_retention` — marketplace buyer retention rate
- `network_density` — marketplace network density ratio
- `risk_adjusted_synergy` — PV of risk-adjusted M&A synergies
- `intrinsic_option_value` — intrinsic value of equity options
- `probability_weighted_employee_value` — employee option value across scenarios
- `vesting_adjusted_value` — option value adjusted for vesting schedule
- `cash_equity_breakeven` — salary vs equity tradeoff analysis
- `max_asset_based_loan` — collateral-based maximum loan calculation
- `safe_conversion_cap` — SAFE conversion with valuation cap
- `safe_expected_value` — expected SAFE value across cap/discount
- `nvt_ratio` — Network Value to Transactions ratio for crypto
- `esg_premium_valuation` — ESG premium impact on valuation
- `esg_discount_valuation` — ESG risk discount on valuation
- `data_moat_value` — DCF of data competitive advantage
- `remote_first_premium` — remote-first company valuation premium
- 19 new MCP server tools for all new functions
- Per-module test files (14 files, one per module)
- GitHub Pages documentation site (MkDocs Material)
- `CITATION.cff` for academic referencing
- mypy type checking in CI

### Changed
- Split monolithic test files into per-module test files
- Expanded test suite from 50 to 101 tests
- Bumped to production-stable release

## [0.1.0] — 2026-05-19

### Added
- Initial release: 80+ valuation formulas across 14 modules
- MCP server with 40+ tools
- 5 AI-Agent Skills
- 50 unit tests against textbook example values
- GitHub Actions CI workflow
