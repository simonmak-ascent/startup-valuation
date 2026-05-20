# Task List: Ascent Partners Branding

## Plan Reference
Implements: `specs/ascent-partners-branding/plan.md`

## Tasks

- [ ] **TASK-01** [S] Download Ascent Partners logo
  - Creates: `docs/assets/images/ascent-logo.png`
  - Source: `https://ascent-partners.com/wp-content/uploads/slider-logo.png`
  - Depends on: none
  - Tests: AC-2

- [ ] **TASK-02** [S] Create custom CSS stylesheet
  - Creates: `docs/assets/stylesheets/extra.css`
  - Color overrides, font imports, header/footer branding
  - Depends on: TASK-01
  - Tests: AC-1, AC-3, AC-4

- [ ] **TASK-03** [M] Update mkdocs.yml configuration
  - Updates: `mkdocs.yml` — theme colors, fonts, logo, extra CSS, footer
  - Depends on: TASK-01, TASK-02
  - Tests: AC-1, AC-2, AC-3, AC-4

- [ ] **TASK-04** [M] Verify docs build and preview
  - Command: `mkdocs build --strict`
  - Verify logo, colors, fonts, footer in built site
  - Depends on: TASK-03
  - Tests: AC-1 through AC-4

- [ ] **TASK-05** [S] Commit and push
  - Depends on: TASK-04
  - Tests: AC-1 through AC-4

## Legend
- `[S]` Small — under 30 min
- `[M]` Medium — 30–60 min
