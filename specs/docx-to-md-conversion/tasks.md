# Tasks: DOCX to Markdown Conversion

**Version:** 1.0  
**Status:** Draft — Awaiting Gate 3 Approval  
**Reads:** `plan.md`, `contracts/` (N/A), `spec.md`, `constitution.md`

---

## Task List

### T1: Setup Output Directory Structure [P]
**Dependencies:** None  
**Complexity:** S  
**AC:** AC1

- Create `output/` directory
- Create placeholder files for all expected outputs per constitution.md naming
- Verify directory structure matches spec

**Test:** Run `ls output/` and verify 22+ expected `.md` files exist (15 chapters, 6 appendices, glossary, bibliography, front matter)

---

### T2: Build DOCX Parser — Extract Paragraphs and Chapters
**Dependencies:** T1  
**Complexity:** M  
**AC:** AC1, AC5, AC6

- Write Python script to parse `Startup_Valuation.docx` with `python-docx`
- Detect chapter boundaries using: heading styles, "Chapter X:" pattern, "Learning Objectives" section
- Map each paragraph to its parent chapter
- Extract chapter titles, section numbers, sub-section names

**Test:** Script outputs chapter count = 15, total paragraph count matches source (~3300), each paragraph assigned to a chapter

---

### T3: Build Structure Mapper — Heading Hierarchy
**Dependencies:** T2  
**Complexity:** M  
**AC:** AC5

- Implement heading level detection:
  - `#` for document title
  - `##` for chapter titles
  - `###` for numbered sections (regex: `^\d+\.\d+\s+`)
  - `####` for named sub-sections
- Handle special sections: Learning Objectives, Key Takeaways, Exercises, Solutions
- Verify no heading level skips

**Test:** Output heading hierarchy for all 15 chapters, verify no level skips (e.g., no `##` directly to `####`)

---

### T4: Build Math Notation Converter — Unicode to LaTeX
**Dependencies:** T2  
**Complexity:** L  
**AC:** AC2, AC3

- Build symbol mapping table for all Unicode math symbols found in source:
  - `²` → `^2`, `³` → `^3`, `×` → `\times`, `÷` → `\div`
  - `σ` → `\sigma`, `β` → `\beta`, `α` → `\alpha`, `Δ` → `\Delta`
  - `∑` → `\sum`, `∫` → `\int`, `√` → `\sqrt`
  - `≈` → `\approx`, `≤` → `\leq`, `≥` → `\geq`, `≠` → `\neq`
  - `∝` → `\propto`, `∞` → `\infty`, `±` → `\pm`, `π` → `\pi`
- Detect inline vs block math context
- Wrap inline math in `$...$`, block math in `$$...$$`
- Handle subscripts: detect patterns like `Rf` → `R_f`, `Wi` → `W_i` in math context
- Handle superscripts: `(1+r)^t` → `(1+r)^{t}`

**Test:** Convert all 189 math-heavy paragraphs, verify LaTeX delimiters balanced, verify symbol conversion accuracy

---

### T5: Build Table Converter — DOCX to GFM Tables
**Dependencies:** T2  
**Complexity:** M  
**AC:** AC4

- Extract all 35 tables from docx
- Convert to GFM format: `| header | header |` + separator row + data rows
- Detect and handle merged cells (split into sequential tables)
- Apply column alignment: text left (`:---`), numbers right (`---:`), center (`:---:`)
- Escape pipe characters in cell content

**Test:** Output all 35 tables, verify column count consistency per table, verify header row present

---

### T6: Build Content Formatter — Lists, Code, Checkboxes
**Dependencies:** T2, T4, T5  
**Complexity:** M  
**AC:** AC6, AC7, AC8, AC9

- Detect and format bullet lists (lines starting with `-`, `•`, `·`)
- Detect and format numbered lists (lines starting with `1.`, `2.`, etc.)
- Detect Python code blocks (lines with `import`, `def`, `print(`, indentation patterns)
- Convert `☐` checkboxes to `- [ ]` task list items
- Preserve exercise star indicators (⭐, ⭐⭐, ⭐⭐⭐, 💭, 🔬)
- Detect bold/italic from run-level formatting in docx

**Test:** Verify all lists formatted correctly, Python code in fenced blocks, checkboxes as task lists, exercise indicators preserved

---

### T7: Build Cross-Reference Resolver
**Dependencies:** T3  
**Complexity:** S  
**AC:** AC10

- Detect "Chapter X" references in text
- Convert to markdown links: `[Chapter X](chapter_XX_name.md)`
- Detect section references within chapters
- Convert to anchor links: `[Section N.N](#nn-title)`

**Test:** Find all cross-references in output, verify all links resolve to existing files/anchors

---

### T8: Build File Writer — Output Generation
**Dependencies:** T3, T4, T5, T6, T7  
**Complexity:** M  
**AC:** AC1, AC6, AC11, AC12

- Write each chapter to its own `.md` file following naming convention
- Write front matter, appendices, glossary, bibliography
- Apply UTF-8 encoding, LF line endings
- Format glossary as `**Term:** Definition`
- Ensure no content loss (all paragraphs written)

**Test:** Count output paragraphs ≥ source paragraphs, verify all 22+ files created, verify glossary format

---

### T9: Validation — Content Fidelity Check
**Dependencies:** T8  
**Complexity:** M  
**AC:** AC6, AC12

- Write validation script that:
  - Counts paragraphs in source vs output
  - Counts tables in source vs output (must be 35)
  - Verifies all 15 chapter learning objectives present
  - Verifies all exercises and solutions present
  - Verifies all appendix content present
  - Checks LaTeX delimiter balance in all output files
  - Checks heading hierarchy validity (no skips)

**Test:** Validation script passes with zero errors

---

### T10: Manual Review — Math-Heavy Chapters
**Dependencies:** T9  
**Complexity:** L  
**AC:** AC2, AC3

- Manually review converted output for chapters with heaviest math:
  - Chapter 2 (Mathematical foundations)
  - Chapter 4 (Advanced techniques — Black-Scholes, binomial, Monte Carlo)
  - Chapter 13 (Investor perspectives — calculations)
  - Chapter 14 (Emerging topics — MV=PQ, Metcalfe's Law)
  - Appendix A (Formulas quick reference)
- Fix any LaTeX conversion errors
- Verify complex formulas (Black-Scholes, DCF, portfolio variance) render correctly

**Test:** All reviewed formulas display correctly in a Markdown viewer

---

### T11: Final Integration — Complete Output Verification
**Dependencies:** T10  
**Complexity:** S  
**AC:** All

- Concatenate all output files and verify completeness
- Spot-check 10 random paragraphs against source for fidelity
- Verify file naming matches constitution.md
- Verify no Word artifacts remain (`&nbsp;`, `<o:p>`, etc.)
- Create summary report of conversion results

**Test:** Summary report shows: paragraphs converted, tables converted, math expressions converted, zero content loss, zero artifacts

---

## Dependency Graph

```
T1 [P]
 └─ T2
     ├─ T3 ── T7
     ├─ T4
     ├─ T5
     │   └─ T6
     │       └─ T8 ── T9 ── T10 ── T11
     └─ (T4, T5, T6 all feed into T8)
```

**Parallelizable:** T4, T5 can start after T2 completes (independent components)  
**Sequential:** T8 requires T3+T4+T5+T6+T7, T9 requires T8, T10 requires T9, T11 requires T10

---

## Estimated Effort

| Task | Complexity | Est. Time |
|------|-----------|-----------|
| T1 | S | 5 min |
| T2 | M | 20 min |
| T3 | M | 15 min |
| T4 | L | 30 min |
| T5 | M | 15 min |
| T6 | M | 20 min |
| T7 | S | 10 min |
| T8 | M | 20 min |
| T9 | M | 15 min |
| T10 | L | 30 min |
| T11 | S | 10 min |
| **Total** | | **~3 hours** |
