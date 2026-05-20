# Technical Plan: Ascent Partners Branding

## Spec Reference
Implements: `specs/ascent-partners-branding/spec.md`

## Architecture Overview

Customize MkDocs Material theme using:
1. `mkdocs.yml` — theme palette, font configuration, extra CSS
2. `docs/assets/stylesheets/extra.css` — custom CSS overrides for colors, typography, logo, footer
3. `docs/assets/images/` — Ascent Partners logo (downloaded from CDN)

## Component Breakdown

### C1: Logo Asset
- **Location:** `docs/assets/images/ascent-logo.png`
- **Source:** Downloaded from `https://ascent-partners.com/wp-content/uploads/slider-logo.png`
- **AC Coverage:** AC-2, AC-4

### C2: MkDocs Theme Configuration
- **Location:** `mkdocs.yml`
- **Changes:**
  - Set primary color to `#0083AB`
  - Set accent color to `#0083AB`
  - Configure font: "Titillium Web" for headings, "Open Sans" for text
  - Add `extra_css` pointing to custom stylesheet
  - Configure `logo` and `favicon` to Ascent Partners logo
  - Add `extra` section for copyright and social links
- **AC Coverage:** AC-1, AC-2, AC-3, AC-4

### C3: Custom CSS Overrides
- **Location:** `docs/assets/stylesheets/extra.css`
- **Changes:**
  - Override header background to white (`#FFFFFF`)
  - Override text color to `#2D2D2D`
  - Override heading color to `#373737`
  - Override link/primary color to `#0083AB`
  - Override footer to dark (`#1A1A1A`) with white text
  - Add Ascent Partners logo to header via CSS
  - Add Ascent Partners branding to footer
  - Import Google Fonts (Titillium Web, Open Sans)
- **AC Coverage:** AC-1, AC-3, AC-4

## AC Coverage Map

| AC | Component(s) | Notes |
|----|-------------|-------|
| AC-1: Brand Colors | C2, C3 | MkDocs palette + CSS overrides |
| AC-2: Logo in Header | C1, C2, C3 | Logo asset + mkdocs.yml config |
| AC-3: Typography | C2, C3 | Google Fonts + CSS |
| AC-4: Footer Branding | C2, C3 | MkDocs extra config + CSS |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Logo CDN unavailable | Low | Medium | Download and host locally |
| CSS overrides conflict with Material theme | Medium | Medium | Test with `mkdocs build --strict` and preview |
| Font loading slow | Low | Low | Use Google Fonts with `display=swap` |
