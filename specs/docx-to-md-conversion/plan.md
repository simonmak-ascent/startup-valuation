# Plan: DOCX to Markdown Conversion

**Version:** 1.0  
**Status:** Draft — Awaiting Gate 2 Approval  
**Reads:** `spec.md`, `constitution.md`

---

## Architecture

### Approach: Python Script with `python-docx` + Manual LaTeX Mapping

The conversion uses a Python script that:
1. Parses the `.docx` with `python-docx` to extract paragraphs, tables, and runs
2. Identifies mathematical content patterns and converts to LaTeX
3. Maps document structure (chapters, sections, sub-sections) to markdown heading hierarchy
4. Writes output files following the naming convention in `constitution.md`

### Why This Approach
- `python-docx` provides direct access to paragraph text, table cells, and run-level formatting
- Mathematical notation in the source is primarily text-based (Unicode symbols like `∑`, `σ`, `²`, `×`) — detectable via pattern matching
- No need for external conversion tools (pandoc) since we need custom LaTeX mapping logic
- Full control over output format to meet all AC requirements

---

## Component Breakdown

### C1: Document Parser
**Responsibility:** Extract raw content from `.docx`
- Iterate paragraphs, detect chapter boundaries (heading styles, numbered patterns like "Chapter X:")
- Extract tables with cell-level content
- Detect code blocks (indented text with Python keywords)
- Track paragraph-to-chapter mapping

### C2: Math Notation Converter
**Responsibility:** Convert text-based math to LaTeX
- Detect inline math patterns: variable assignments (`X = Y`), formulas (`MV = PQ`), Greek letters (`σ`, `β`, `α`)
- Detect block math: standalone formula paragraphs, multi-step calculations
- Apply LaTeX transformations:
  - `²` → `^2`, `³` → `^3`
  - `×` → `\times`, `÷` → `\div`
  - `σ` → `\sigma`, `β` → `\beta`, `α` → `\alpha`, `Δ` → `\Delta`
  - `∑` → `\sum`, `∫` → `\int`
  - `≈` → `\approx`, `≤` → `\leq`, `≥` → `\geq`
  - `≠` → `\neq`, `∝` → `\propto`, `∞` → `\infty`
  - Subscript numbers: `Rf` → `R_f`, `CAC` stays as-is (acronym)
  - Superscript in context: `(1+r)^t` → `(1+r)^{t}`

### C3: Table Converter
**Responsibility:** Convert docx tables to GFM markdown tables
- Extract header row and data rows
- Handle merged cells by splitting into sequential tables
- Apply column alignment based on content type (numbers right-aligned, text left-aligned)
- Escape pipe characters `|` in cell content

### C4: Structure Mapper
**Responsibility:** Map document hierarchy to markdown headings
- Chapter titles → `## Chapter N: Title`
- Numbered sections (N.N) → `### N.N Title`
- Sub-sections (named, not numbered) → `#### Title`
- Learning Objectives → `### Learning Objectives`
- Key Takeaways → `### Key Takeaways`
- Exercises → `### Exercises for Chapter N`
- Solutions → `### Solutions for Chapter N`

### C5: Content Formatter
**Responsibility:** Apply markdown formatting to text content
- Bold/italic detection from run-level formatting
- List detection (bulleted, numbered)
- Code block detection (Python syntax)
- Checkbox detection (`☐` → `- [ ]`)
- Cross-reference detection ("Chapter X" → markdown link)
- Glossary term formatting

### C6: File Writer
**Responsibility:** Write output files with correct naming and structure
- One file per chapter following `constitution.md` naming
- Front matter, appendices, glossary, bibliography as separate files
- UTF-8 encoding, LF line endings
- 120-char soft wrap

---

## Technology Choices

| Component | Technology | Justification |
|-----------|-----------|---------------|
| DOCX parsing | `python-docx` | Already available, direct access to paragraphs/tables/runs |
| Math conversion | Custom regex + pattern matching | Source uses Unicode math symbols, not MathML or OLE objects |
| Output | Standard library (`pathlib`, `textwrap`) | No external dependencies needed |
| Validation | Manual verification scripts | Simple paragraph/table count comparison |

---

## Traceability: AC → Component

| AC | Components |
|----|-----------|
| AC1: File Structure | C4, C6 |
| AC2: Inline Math | C2 |
| AC3: Block Math | C2 |
| AC4: Tables | C3 |
| AC5: Heading Hierarchy | C4 |
| AC6: Content Fidelity | C1, C5 |
| AC7: Exercise/Solution | C4, C5 |
| AC8: Code Blocks | C1, C5 |
| AC9: Checklists | C5 |
| AC10: Cross-References | C5 |
| AC11: Glossary | C4, C5 |
| AC12: No Content Loss | C1, C6 |

---

## Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Math notation misinterpreted (e.g., variable vs. acronym) | High | Medium | Manual review of math-heavy chapters (Ch 2, 4, 13, 14) |
| Table merged cells lose data | High | Low | Split merged cells into sequential tables, verify row counts |
| Chapter boundary detection fails | High | Low | Use multiple signals: heading style, "Chapter X:" pattern, learning objectives |
| Unicode math symbols not fully covered | Medium | Medium | Comprehensive symbol mapping table, test against all 189 math paragraphs |
| Cross-reference links broken | Low | Medium | Post-conversion link validation script |

---

## Execution Strategy

1. **Phase A:** Build parser + structure mapper (C1, C4) — extract content and map hierarchy
2. **Phase B:** Build math converter (C2) — handle inline and block math
3. **Phase C:** Build table converter (C3) — handle all 35 tables
4. **Phase D:** Build content formatter (C5) — lists, code, checkboxes, cross-refs
5. **Phase E:** Build file writer (C6) — output files with correct naming
6. **Phase F:** Validation — verify all ACs pass

---

## Data Model (Content Structure)

### Document Entity
```
Document
├── title: str
├── chapters: List[Chapter]
├── appendices: List[Appendix]
├── glossary: List[GlossaryEntry]
└── bibliography: List[BibEntry]
```

### Chapter Entity
```
Chapter
├── number: int
├── title: str
├── sections: List[Section]
├── learning_objectives: List[str]
├── key_takeaways: List[str]
├── exercises: List[Exercise]
└── solutions: List[Solution]
```

### Section Entity
```
Section
├── number: str  # e.g., "14.1"
├── title: str
├── paragraphs: List[Paragraph]
├── tables: List[Table]
└── sub_sections: List[SubSection]
```

### Paragraph Entity
```
Paragraph
├── text: str
├── has_math: bool
├── math_type: "inline" | "block" | None
├── is_code: bool
├── is_list_item: bool
├── list_level: int
└── list_type: "bullet" | "number" | None
```

### Table Entity
```
Table
├── headers: List[str]
├── rows: List[List[str]]
└── has_merged_cells: bool
```
