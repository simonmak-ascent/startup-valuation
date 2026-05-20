# Spec: Ascent Partners Branding for GitHub Pages

**Version:** 1.0
**Status:** Implemented — Gates 1, 2, 3 passed
**Feature Branch:** `ascent-partners-branding`

---

## Overview

Customize the GitHub Pages documentation site to match the Ascent Partners website design (https://www.ascent-partners.com), including color scheme, typography, logo, and footer branding.

---

## User Stories

| # | Story | Priority |
|---|-------|----------|
| US1 | As a user, I want the docs site to use Ascent Partners' brand colors so it feels consistent with their website | MUST |
| US2 | As a user, I want to see the Ascent Partners logo in the header so I know this is their project | MUST |
| US3 | As a user, I want the typography to match Ascent Partners' style so the experience is cohesive | MUST |
| US4 | As a user, I want the footer to include Ascent Partners branding and copyright | MUST |

---

## Acceptance Criteria

### AC-1: Brand Color Scheme [MUST]
**Given** the docs site
**When** viewed in a browser
**Then** it uses Ascent Partners' color palette:
- Primary color: `#0083AB` (teal/cyan blue — used for links, accents, navigation)
- Text color: `#2D2D2D` (dark gray — body text)
- Heading color: `#373737` (dark gray — headings)
- Header background: `#FFFFFF` (white)
- Footer background: `#1A1A1A` (dark) with white text

### AC-2: Ascent Partners Logo in Header [MUST]
**Given** the docs site
**When** viewed in a browser
**Then** the Ascent Partners logo appears in the top-left of the navigation bar, linking to the homepage

### AC-3: Typography Matches Ascent Partners [MUST]
**Given** the docs site
**When** viewed in a browser
**Then** it uses:
- Headings: "Titillium Web" (sans-serif)
- Body text: "Open Sans" (sans-serif)
- Code: monospace (default)

### AC-4: Footer with Ascent Partners Branding [MUST]
**Given** the docs site
**When** scrolled to the bottom
**Then** the footer includes:
- Ascent Partners logo
- Copyright: "© 2026 Ascent Partners Group Ltd, All rights reserved."
- Link to Ascent Partners website (https://www.ascent-partners.com)

---

## Boundaries

### Always Do
- Use the official Ascent Partners logo from their CDN
- Maintain accessibility (WCAG AA contrast ratios)
- Keep the site functional (search, navigation, API docs)

### Ask First
- Whether to include social media links (LinkedIn, Facebook) in footer

### Never Do
- Change the site structure or content
- Remove MkDocs functionality (search, navigation)
- Use images not hosted on Ascent Partners' CDN

---

## Out of Scope

- Changing the documentation content
- Adding new pages or sections
- Modifying the CI/CD workflows

---

## Open Questions

| # | Question | Status |
|---|----------|--------|
| Q1 | Should we download the logo and host it locally or link from Ascent Partners CDN? | [RESOLVED: Download and host locally in docs/assets/ for reliability] |

---

## Validation Checklist (Pre-Gate 1)

- [ ] Every `[MUST]` AC is independently testable
- [ ] No implementation details in the spec
- [ ] All `[NEEDS CLARIFICATION]` items resolved
- [ ] Scope boundaries explicit
