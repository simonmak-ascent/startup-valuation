# Constitution — Startup Valuation Model Project

**Version:** 1.0  
**Status:** Active  
**Created:** 2026-05-19

## Purpose

Project-level immutable constraints governing all work on converting and structuring the Startup Valuation textbook content.

---

## 1. Format Standards

### 1.1 Markdown Output
- All output files use `.md` extension with CommonMark-compliant syntax
- UTF-8 encoding, LF line endings
- Max line length: 120 characters (soft wrap)
- No trailing whitespace

### 1.2 Mathematical Notation
- All inline math uses `$...$` (LaTeX inline delimiters)
- All display/block math uses `$$...$$` on separate lines
- Variables in math blocks use italic LaTeX convention (default)
- Greek letters, subscripts, superscripts rendered via LaTeX syntax
- No image-based formulas — all math must be text/LaTeX

### 1.3 Tables
- Use GitHub-flavored markdown tables (`| header |` format)
- Complex multi-row tables split into sequential single-row tables if needed
- Column alignment markers (`:---`, `:---:`, `---:`) used consistently

### 1.4 Headings
- H1 (`#`) reserved for document title only
- H2 (`##`) for chapter-level sections
- H3 (`###`) for sub-sections
- H4+ for deeper nesting as needed
- No skipped heading levels

### 1.5 Lists
- Ordered lists for numbered sequences (exercises, steps)
- Unordered lists for non-sequential items
- Nested lists indented 2 spaces per level

---

## 2. Content Fidelity

### 2.1 Preservation Rules
- All numerical values, percentages, and dollar amounts preserved exactly
- All formulas and equations preserved with correct mathematical meaning
- Exercise numbering and solution mapping preserved
- Cross-references to chapters/sections preserved as markdown links

### 2.2 Structural Mapping
- Each chapter → separate `.md` file
- Front matter (title page, TOC) → `00_front_matter.md`
- Appendices → `appendix_*.md` files
- Glossary → `glossary.md`
- Bibliography → `bibliography.md`

### 2.3 No Content Loss
- Every paragraph in source must appear in output
- Every table in source must appear in output
- Every formula in source must appear in output
- No summarization or omission

---

## 3. Naming Conventions

### 3.1 File Names
- Lowercase with underscores: `chapter_01_introduction.md`
- Numbered prefix for ordering: `01_`, `02_`, etc.
- No spaces or special characters in filenames

### 3.2 Directory Structure
```
startup_valuation_model/
├── constitution.md
├── specs/
│   └── docx-to-md-conversion/
│       ├── spec.md
│       ├── plan.md
│       └── tasks.md
├── output/
│   ├── 00_front_matter.md
│   ├── chapter_01_*.md
│   ├── ...
│   ├── appendix_*.md
│   ├── glossary.md
│   └── bibliography.md
└── Startup_Valuation.docx  (source)
```

---

## 4. Quality Requirements

### 4.1 Validation
- All LaTeX math must render correctly (validate delimiters balanced)
- All tables must have consistent column counts per row
- All heading hierarchy must be valid (no skips)
- All cross-reference links must resolve to existing files/anchors

### 4.2 Review Gates
- Gate 1: Spec review before planning
- Gate 2: Plan review before task breakdown
- Gate 3: Task review before execution

---

## 5. Anti-Patterns (Banned)

- ❌ Converting formulas to images or screenshots
- ❌ Using HTML tables instead of markdown tables
- ❌ Summarizing or condensing source content
- ❌ Losing exercise/solution mappings
- ❌ Using Word-specific formatting artifacts (e.g., `&nbsp;`, `<o:p>`)
- ❌ Mixing markdown and HTML for formatting when markdown suffices
