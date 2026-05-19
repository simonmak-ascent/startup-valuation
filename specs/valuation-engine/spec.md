# Spec: Startup Valuation Engine — AI-Agent Skills, MCP Server & Python Library

**Version:** 1.0  
**Status:** Draft — Awaiting Gate 1 Approval  
**Feature Branch:** `valuation-engine`

---

## Overview

Build a comprehensive Python library, MCP server, and AI-Agent Skills package that implements all 80+ valuation calculations from the Startup Valuation textbook, published as an open-source GitHub repository with GitHub Pages documentation.

---

## User Stories

| # | Story | Priority |
|---|-------|----------|
| US1 | As a developer, I want a Python library with typed functions for every valuation formula so I can compute valuations programmatically | MUST |
| US2 | As an AI agent, I want an MCP server exposing all calculations as tools so I can perform valuation computations during conversations | MUST |
| US3 | As a startup founder, I want AI-Agent Skills (OpenCode/Claude) that guide me through valuation workflows using the book's methodology | MUST |
| US4 | As a student, I want GitHub Pages documentation with interactive examples for every formula so I can learn by doing | MUST |
| US5 | As a contributor, I want a well-structured monorepo with tests, CI, and clear contribution guidelines so I can extend the library | MUST |
| US6 | As a financial analyst, I want every function to return structured results (value + assumptions + sensitivity) so I can audit computations | MUST |
| US7 | As a developer, I want the Python package installable via pip so I can integrate it into my projects | SHOULD |
| US8 | As an AI agent, I want compound tools (e.g., "full valuation" that runs Scorecard + VC Method + Monte Carlo) so I can provide comprehensive analysis | SHOULD |
| US9 | As a user, I want a CLI tool for quick calculations from the terminal | COULD |
| US10 | As a researcher, I want Monte Carlo simulation with configurable distributions so I can model uncertainty | SHOULD |

---

## Acceptance Criteria

### AC1: Python Library — Core Structure [MUST]
**Given** a developer installs the package  
**When** they import it  
**Then** they have access to a typed, documented Python library organized by chapter:
- `valuation.probability` — expected value, probability-weighted scenarios, Poisson
- `valuation.tv` — present value, NPV, annuity
- `valuation.capm` — CAPM, portfolio beta, startup-adjusted CAPM
- `valuation.core` — Scorecard, Berkus, Risk Factor Summation, VC Method
- `valuation.advanced` — Black-Scholes, Binomial Tree, Monte Carlo, Scenario Analysis
- `valuation.comparables` — multiples, regression-adjusted multiples
- `valuation.saas` — LTV, CAC, NRR, Magic Number, Rule of 40
- `valuation.biotech` — rNPV, decision tree, peak sales, pipeline valuation
- `valuation.fintech` — payment revenue, lending, network effects
- `valuation.marketplace` — GMV, take rate, liquidity, network density
- `valuation.hardware` — TRL-adjusted, break-even, probability-weighted DCF
- `valuation.international` — PPP, IRP, currency-adjusted DCF, CRP
- `valuation.stakeholders` — dilution, OPM, PWERM, liquidation preference, synergy
- `valuation.emerging` — SAFE conversion, MV=PQ, Metcalfe's Law, ESG-adjusted rate

### AC2: Python Library — Function Signatures [MUST]
**Given** any valuation function  
**When** called with valid parameters  
**Then** it returns a `ValuationResult` dataclass containing:
- `value: float` — the computed valuation
- `method: str` — the method name
- `inputs: dict` — all input parameters used
- `assumptions: list[str]` — key assumptions made
- `sensitivity: dict[str, float]` — sensitivity to key inputs (±10%)

### AC3: Python Library — All 80+ Formulas [MUST]
**Given** the formula catalog from the textbook  
**When** the library is complete  
**Then** every formula has a corresponding function that:
- Matches the mathematical formula exactly (verified against book examples)
- Produces the same numerical result as book examples (within 0.01% tolerance)
- Has docstrings with formula, parameters, and example usage
- Has unit tests with book example values

### AC4: MCP Server [MUST]
**Given** the MCP server is running  
**When** an AI agent connects  
**Then** it exposes all 80+ calculations as MCP tools with:
- Tool names: `valuation_scorecard`, `valuation_berkus`, `valuation_black_scholes`, etc.
- Input schemas matching the Python function signatures
- Output matching `ValuationResult` as JSON
- Compound tools: `valuation_full_analysis` runs multiple methods

### AC5: MCP Server — Transport [MUST]
**Given** the MCP server  
**When** configured  
**Then** it supports:
- stdio transport (for local AI agents)
- SSE transport (for web-based agents)
- Configuration via `mcp.json` or environment variables

### AC6: AI-Agent Skills [MUST]
**Given** the Skills package  
**When** loaded by an AI agent (OpenCode/Claude)  
**Then** it provides:
- `valuation-core` — Core methods (Scorecard, Berkus, VC Method, Risk Factor)
- `valuation-advanced` — Advanced methods (Black-Scholes, Monte Carlo, Scenario Analysis)
- `valuation-industry` — Industry-specific (SaaS, Biotech, Fintech, Marketplace, Hardware)
- `valuation-stakeholder` — Stakeholder perspectives (dilution, OPM, PWERM, synergy)
- `valuation-emerging` — Emerging topics (SAFE, crypto, ESG, network effects)
Each skill includes:
- Workflow guidance (which method to use when)
- Parameter collection prompts
- Interpretation guidance for results
- Cross-references to textbook chapters

### AC7: GitHub Repository [MUST]
**Given** the project is published on GitHub  
**When** a user visits the repo  
**Then** they see:
- Professional README with overview, installation, quick start
- Repository structure matching the architecture
- License file (MIT)
- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- CI workflow (GitHub Actions) running tests on push

### AC8: GitHub Pages Documentation [MUST]
**Given** the GitHub Pages site is published  
**When** a user visits it  
**Then** they see:
- Homepage with project overview
- API reference for every function (auto-generated from docstrings)
- Interactive examples for each formula category
- Book chapter cross-reference index
- Search functionality

### AC9: Test Coverage [MUST]
**Given** the test suite  
**When** run with `pytest`  
**Then**:
- Every function has at least one unit test
- All book examples are tested with exact numerical values
- Test coverage ≥ 90%
- Tests run in < 30 seconds

### AC10: Package Distribution [SHOULD]
**Given** the package  
**When** published  
**Then**:
- Installable via `pip install startup-valuation`
- `pyproject.toml` with proper metadata
- Version follows semantic versioning
- Changelog maintained

---

## Boundaries

### Always Do
- Match textbook formulas exactly (verified against book examples)
- Return structured results (ValuationResult) for auditability
- Include docstrings with formula, parameters, and examples
- Use type hints on all public functions
- Test every function against book example values

### Ask First
- Whether to include a web-based calculator UI
- Whether to add database persistence for valuation sessions
- Whether to support additional output formats (PDF reports)

### Never Do
- Hard-code book example values as defaults
- Return bare numbers without context (always return ValuationResult)
- Use floating-point comparisons without tolerance
- Mix business logic with presentation logic
- Expose internal implementation details in MCP tool schemas

---

## Out of Scope

- Web application / SaaS product
- Real-time market data integration
- Portfolio management features
- Multi-currency real-time conversion
- User authentication or accounts
- Payment processing

---

## Open Questions

| # | Question | Status |
|---|----------|--------|
| Q1 | Should the GitHub repo be under a personal account or organization? | [RESOLVED: personal account, can transfer later] |
| Q2 | Should we use FastMCP or raw MCP SDK for the server? | [RESOLVED: FastMCP for simpler development] |
| Q3 | Should Monte Carlo use numpy or scipy for distributions? | [RESOLVED: numpy for core, scipy optional for advanced distributions] |
| Q4 | What Python version minimum? | [RESOLVED: Python 3.10+] |

---

## Validation Checklist (Pre-Gate 1)

- [ ] Every `[MUST]` AC is independently testable
- [ ] No implementation details in the spec (no specific library names in ACs)
- [ ] Error and edge case ACs exist (invalid inputs, edge cases)
- [ ] No vague terms — replaced with measurable criteria
- [ ] Scope boundaries explicit
- [ ] All `[NEEDS CLARIFICATION]` items resolved
