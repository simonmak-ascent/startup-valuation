# Spec: Deployment Bug Fixes

**Version:** 1.0
**Status:** Implemented — Gates 1, 2, 3 passed
**Feature Branch:** `deployment-bugfix`

---

## Overview

Fix deployment failures and configuration inconsistencies in the CI/CD workflows, documentation build, and package metadata.

---

## User Stories

| # | Story | Priority |
|---|-------|----------|
| US1 | As a maintainer, I want GitHub Pages docs to deploy successfully so users can access documentation | MUST |
| US2 | As a developer, I want consistent GitHub URLs across all config files so links don't break | MUST |
| US3 | As a developer, I want `pip install -e ".[dev]"` to include all CI dependencies so local matches CI | MUST |
| US4 | As a maintainer, I want docs dependencies to be explicit and stable so builds don't break unexpectedly | SHOULD |

---

## Acceptance Criteria

### AC-1: GitHub Pages Docs Deploy Successfully [MUST]
**Given** the docs workflow runs on push to main
**When** `mkdocs build --strict` executes
**Then** it completes with exit code 0 and the site deploys to GitHub Pages

### AC-2: Consistent Repository URLs [MUST]
**Given** all configuration files in the repository
**When** comparing GitHub URLs across `mkdocs.yml`, `pyproject.toml`, `README.md`, and `CITATION.cff`
**Then** all URLs reference the same repository owner (`simonplmak-cloud`) and the same Pages URL (`simonplmak-cloud.github.io/startup-valuation`)

### AC-3: Dev Dependencies Match CI [MUST]
**Given** the CI workflow installs `mypy`
**When** a developer runs `pip install -e ".[dev]"`
**Then** `mypy` is included and `mypy src/startup_valuation` runs without manual installation

### AC-4: Docs Dependencies Explicit [SHOULD]
**Given** the `docs` optional dependencies
**When** `pymdown-extensions` is used in `mkdocs.yml`
**Then** it is explicitly declared in `pyproject.toml` `[project.optional-dependencies] docs`

---

## Boundaries

### Always Do
- Keep all GitHub URLs consistent with the actual repository owner
- Declare all transitive dependencies explicitly when they are required for builds

### Ask First
- Whether to add `types-scipy` for complete mypy coverage

### Never Do
- Change the repository URL without updating all references
- Remove `--strict` from mkdocs build

---

## Out of Scope

- Adding new valuation functions
- Changing test coverage targets
- Modifying MCP server functionality

---

## Open Questions

| # | Question | Status |
|---|----------|--------|
| Q1 | Should we add `types-scipy` for complete mypy coverage? | [RESOLVED: No — scipy types are incomplete, `--ignore-missing-imports` is sufficient for now] |

---

## Validation Checklist (Pre-Gate 1)

- [ ] Every `[MUST]` AC is independently testable
- [ ] No implementation details in the spec
- [ ] All `[NEEDS CLARIFICATION]` items resolved
- [ ] Scope boundaries explicit
