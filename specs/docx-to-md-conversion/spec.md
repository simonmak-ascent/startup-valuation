# Spec: DOCX to Markdown Conversion — Startup Valuation Textbook

**Version:** 1.0  
**Status:** Draft — Awaiting Gate 1 Approval  
**Feature Branch:** `docx-to-md-conversion`

---

## Overview

Convert the `Startup_Valuation.docx` textbook (~3300 paragraphs, 35 tables, 189 math-heavy passages, 15 chapters, appendices, glossary, bibliography) into a structured set of Markdown (`.md`) files with full fidelity, preserving all mathematical notation as LaTeX, all tables as GFM tables, and all document structure as markdown heading hierarchy.

---

## User Stories

| # | Story | Priority |
|---|-------|----------|
| US1 | As a reader, I want each chapter in its own `.md` file so I can navigate and reference content easily | MUST |
| US2 | As a student, I want all mathematical formulas rendered as LaTeX so they display correctly in any Markdown viewer | MUST |
| US3 | As an instructor, I want all tables preserved as markdown tables so I can copy data into spreadsheets | MUST |
| US4 | As a researcher, I want all numerical values and calculations preserved exactly as in the source | MUST |
| US5 | As a reader, I want exercise/solution mappings preserved so I can verify answers | MUST |
| US6 | As a developer, I want a consistent file naming convention so I can programmatically reference files | MUST |
| US7 | As a reader, I want the glossary as a separate file so I can quickly look up terms | SHOULD |
| US8 | As a reader, I want cross-references between chapters as markdown links so I can navigate | SHOULD |
| US9 | As a reader, I want checkbox lists for regulatory checklists so they are interactive | COULD |
| US10 | As a reader, I want code blocks for Python examples so they are syntax-highlighted | SHOULD |

---

## Acceptance Criteria

### AC1: File Structure [MUST]
**Given** the source `Startup_Valuation.docx` contains 15 chapters, front matter, appendices, glossary, and bibliography  
**When** the conversion is complete  
**Then** the `output/` directory contains:
- `00_front_matter.md` (title page, table of contents)
- `chapter_01_*.md` through `chapter_15_*.md` (one file per chapter)
- `appendix_a_formulas.md`, `appendix_b_compliance.md`, `appendix_c_court_cases.md`, `appendix_d_data_sources.md`, `appendix_e_certifications.md`, `appendix_f_teaching.md`
- `glossary.md`
- `bibliography.md`

### AC2: Mathematical Notation — Inline [MUST]
**Given** a paragraph contains inline mathematical expressions (e.g., `MV = PQ`, `E(Ri) = Rf + βi(E(Rm) - Rf)`, `n²`)  
**When** converted to markdown  
**Then** all inline math is wrapped in `$...$` LaTeX delimiters with correct syntax:
- Variables italicized by default in LaTeX
- Subscripts use `_` (e.g., `$R_f$`, `$\beta_i$`)
- Superscripts use `^` (e.g., `$n^2$`, `$(1+r)^t$`)
- Greek letters use LaTeX commands (e.g., `$\sigma$`, `$\alpha$`, `$\Delta$`)
- Multiplication uses `\times` (e.g., `$5 \times 10^6$`)
- Division uses `\div` or fraction notation (e.g., `$\frac{A}{B}$`)

### AC3: Mathematical Notation — Display/Block [MUST]
**Given** a paragraph contains a standalone formula or equation block  
**When** converted to markdown  
**Then** the formula is wrapped in `$$...$$` on its own lines with proper LaTeX formatting:
- Multi-line equations use `aligned` or `gathered` environments
- Summations use `\sum` with limits (e.g., `$$\sum_{i=1}^{n} w_i$$`)
- Fractions use `\frac{numerator}{denominator}`
- Square roots use `\sqrt{...}`
- Black-Scholes, binomial, DCF formulas use proper LaTeX notation

### AC4: Tables [MUST]
**Given** the source contains 35 tables  
**When** converted to markdown  
**Then** each table is rendered as a GitHub-flavored markdown table:
- Header row with `|` delimiters
- Separator row with alignment markers
- All data rows with consistent column counts
- No merged cells (split into sequential tables if source has merges)
- Numerical values preserved exactly (e.g., `$3.915M`, `1.305`, `0.30×1.4`)

### AC5: Heading Hierarchy [MUST]
**Given** the source has chapter titles, section numbers (e.g., "14.1 SAFEs and Convertible Notes"), and sub-sections  
**When** converted to markdown  
**Then**:
- Document title → `#`
- Chapter titles → `##`
- Numbered sections (e.g., "14.1") → `###`
- Sub-sections (e.g., "SAFE Mechanics") → `####`
- No heading level is skipped

### AC6: Content Fidelity [MUST]
**Given** the source contains ~3300 paragraphs  
**When** conversion is complete  
**Then**:
- Every non-empty paragraph from the source appears in the output
- No paragraph is summarized, condensed, or omitted
- All numerical values, percentages, and dollar amounts are identical to source
- All exercise numbers and solution mappings are preserved

### AC7: Exercise/Solution Mapping [MUST]
**Given** each chapter has exercises (⭐ Basic, ⭐⭐ Intermediate, ⭐⭐⭐ Advanced, 💭 Discussion, 🔬 Research) with corresponding solutions  
**When** converted  
**Then**:
- Exercise sections use markdown lists with preserved numbering
- Solution sections are clearly separated with heading
- Star indicators (⭐) preserved as unicode or markdown text
- Solution numbers map 1:1 to exercise numbers

### AC8: Code Blocks [SHOULD]
**Given** the source contains Python code examples (e.g., Monte Carlo simulation code)  
**When** converted  
**Then** code is wrapped in fenced code blocks with language identifier:
```python
import numpy as np
...
```

### AC9: Checklists [COULD]
**Given** appendices contain regulatory checklists with ☐ checkboxes  
**When** converted  
**Then** checkboxes are rendered as markdown task lists:
- `- [ ]` for unchecked items
- `- [x]` for checked items (if applicable)

### AC10: Cross-References [SHOULD]
**Given** the source references other chapters (e.g., "see Chapter 4")  
**When** converted  
**Then** cross-references are markdown links to the target file:
- `[Chapter 4](chapter_04_advanced_techniques.md)`
- Anchor links for specific sections within a file

### AC11: Glossary Format [SHOULD]
**Given** the source contains a glossary with term: definition pairs  
**When** converted  
**Then** glossary entries use definition list or bold-term format:
- `**Term:** Definition text`
- Entries sorted alphabetically

### AC12: No Content Loss [MUST]
**Given** the complete source document  
**When** all output files are concatenated  
**Then** the combined content contains every piece of information from the source, verifiable by:
- Paragraph count in output ≥ paragraph count in source (excluding empty)
- Table count in output = 35
- All 15 chapter learning objectives present
- All exercises and solutions present
- All appendix content present

---

## Boundaries

### Always Do
- Preserve exact numerical values and calculations
- Convert all math to LaTeX (inline `$...$`, block `$$...$$`)
- One chapter per output file
- Use GFM-compliant markdown only

### Ask First
- How to handle the "150+ academic papers" placeholder in bibliography
- Whether to include the separate "Bibliography document" referenced in the source
- Whether to add a table of contents with links at the top of each file

### Never Do
- Convert formulas to images
- Summarize or condense any content
- Use HTML formatting when markdown suffices
- Lose any exercise/solution mapping
- Introduce formatting artifacts from Word (e.g., `&nbsp;`, `<o:p>`)

---

## Out of Scope

- Creating a website or documentation site from the markdown
- Adding new content or examples not in the source
- Translating content to other languages
- Creating interactive calculators for the formulas
- Converting to other formats (PDF, HTML, EPUB) — markdown only

---

## Open Questions

| # | Question | Status |
|---|----------|--------|
| Q1 | Should Python code examples include syntax highlighting language tags? | [RESOLVED: Yes, use `python`] |
| Q2 | How to handle the "150+ academic papers would be listed here" placeholder? | [NEEDS CLARIFICATION] |
| Q3 | Should cross-references between chapters use relative file paths or anchor-only links? | [NEEDS CLARIFICATION] |
| Q4 | Should the document include a master table of contents file linking all chapters? | [NEEDS CLARIFICATION] |
| Q5 | How to handle the "Appendix C: Court Cases Summary" which appears to have no content in the source? | [NEEDS CLARIFICATION] |

---

## Validation Checklist (Pre-Gate 1)

- [ ] Every `[MUST]` AC is independently testable
- [ ] No implementation details in the spec (no tool names, no function names)
- [ ] Error and edge case ACs exist (math parsing failures, table merge handling)
- [ ] No vague terms ("accurate", "complete" — replaced with measurable criteria)
- [ ] Scope boundaries explicitly listed
- [ ] All `[NEEDS CLARIFICATION]` items identified
