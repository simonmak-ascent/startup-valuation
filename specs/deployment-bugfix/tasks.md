# Task List: Deployment Bug Fixes

## Plan Reference
Implements: `specs/deployment-bugfix/plan.md`

## Tasks

- [ ] **TASK-01** [S] Fix pyproject.toml URLs to simonplmak-cloud
  - Updates: `pyproject.toml` Homepage, Documentation, Repository, Bug Tracker URLs
  - Depends on: none
  - Tests: AC-2

- [ ] **TASK-02** [S] Fix README.md URLs to simonplmak-cloud
  - Updates: `README.md` badges and links
  - Depends on: none
  - Tests: AC-2

- [ ] **TASK-03** [S] Fix CITATION.cff URLs to simonplmak-cloud
  - Updates: `CITATION.cff` repository-code URL
  - Depends on: none
  - Tests: AC-2

- [ ] **TASK-04** [S] Add mypy to dev dependencies
  - Updates: `pyproject.toml` `[project.optional-dependencies] dev`
  - Depends on: none
  - Tests: AC-3

- [ ] **TASK-05** [S] Add pymdown-extensions to docs dependencies
  - Updates: `pyproject.toml` `[project.optional-dependencies] docs`
  - Depends on: none
  - Tests: AC-4

- [ ] **TASK-06** [S] Remove standalone mypy install from CI
  - Updates: `.github/workflows/ci.yml` — remove `pip install mypy` line
  - Depends on: TASK-04
  - Tests: AC-3

- [ ] **TASK-07** [M] Verify docs build locally
  - Command: `pip install -e ".[docs]" && mkdocs build --strict`
  - Depends on: TASK-01 through TASK-06
  - Tests: AC-1

- [ ] **TASK-08** [S] Commit and push all fixes
  - Depends on: TASK-07
  - Tests: AC-1 through AC-4

## Legend
- `[S]` Small — under 30 min
- `[M]` Medium — 30–60 min
