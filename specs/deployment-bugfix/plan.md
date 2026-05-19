# Technical Plan: Deployment Bug Fixes

## Spec Reference
Implements: `specs/deployment-bugfix/spec.md`

## Architecture Overview

Fix four configuration inconsistencies across the repository:
1. Align all GitHub URLs to `simonplmak-cloud` (the actual repo owner)
2. Add `mypy` to dev dependencies
3. Add `pymdown-extensions` to docs dependencies
4. Verify docs build succeeds

## Component Breakdown

### C1: URL Alignment
- **Location:** `pyproject.toml`, `mkdocs.yml`, `README.md`, `CITATION.cff`
- **Changes:** Replace `simonmak` with `simonplmak-cloud` in all GitHub URLs and Pages URLs
- **AC Coverage:** AC-2

### C2: Dev Dependencies
- **Location:** `pyproject.toml`
- **Changes:** Add `mypy>=1.0.0` to `[project.optional-dependencies] dev`
- **AC Coverage:** AC-3

### C3: Docs Dependencies
- **Location:** `pyproject.toml`
- **Changes:** Add `pymdown-extensions>=10.0` to `[project.optional-dependencies] docs`
- **AC Coverage:** AC-4

### C4: CI Workflow Cleanup
- **Location:** `.github/workflows/ci.yml`
- **Changes:** Remove standalone `pip install mypy` step (now in dev deps)
- **AC Coverage:** AC-3

## AC Coverage Map

| AC | Component(s) | Notes |
|----|-------------|-------|
| AC-1: Docs Deploy | C1-C4 | Verified by running `mkdocs build --strict` |
| AC-2: URL Consistency | C1 | 4 files updated |
| AC-3: Dev Deps Match CI | C2, C4 | mypy added to dev deps, CI simplified |
| AC-4: Docs Deps Explicit | C3 | pymdown-extensions declared |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| mkdocs build fails on missing dependency | Low | High | Test locally before pushing |
| URL changes break existing links | Low | Medium | Only internal references changed; external links will redirect |
