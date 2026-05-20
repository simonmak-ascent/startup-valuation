# Plan: Book Alignment Feature

## Architecture
- **Book cover**: Download from Amazon, optimize, store in `docs/assets/images/book-cover.jpg`
- **Homepage**: Update `docs/index.md` to feature book prominently with cover, description, and purchase CTA
- **Footer**: Add book reference to `mkdocs.yml` extra section or via CSS
- **Chapter mapping**: Add table showing book chapters → library modules

## Implementation Steps

### 1. Book Cover Acquisition
- Download book cover from Amazon product page
- Optimize for web (resize to ~400px width, compress to <200KB)
- Save to `docs/assets/images/book-cover.jpg`

### 2. Homepage Redesign
- Add hero section with book cover (left) and description (right)
- Include "Buy on Amazon" button styled with Ascent Partners brand color
- Add chapter-to-module mapping table
- Preserve existing Quick Start, Modules, MCP Server, Skills sections below

### 3. Footer Enhancement
- Add book reference line to footer copyright area
- Include "Part of the Valuation in Practice Series" text

### 4. CSS Updates
- Add styles for book hero section
- Add styles for "Buy on Amazon" button
- Ensure responsive layout for mobile

### 5. Verification
- Run `mkdocs build --strict` locally
- Verify all links work
- Check mobile responsiveness

## Risks
- Book cover copyright: Using book cover for promotional purposes on companion site is standard practice
- Amazon URL changes: Use stable product URL format
- Image optimization: May need to manually resize if download is too large

## Dependencies
- None (all changes are to existing docs files)
