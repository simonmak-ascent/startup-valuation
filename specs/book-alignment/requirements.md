# Requirements: Book Alignment Feature

## Context
The GitHub Pages documentation site (`https://simonplmak-cloud.github.io/startup-valuation/`) needs to be aligned with Simon Mak's "Startup Valuation" book on Amazon. The site currently has Ascent Partners branding but lacks any reference to the companion textbook.

## Book Details
- **Title**: Startup Valuation: A Comprehensive Guide to Valuing Fast-Growing Pre-Revenue Companies
- **Subtitle**: Theory, Methods, Regulation, and Practice
- **Series**: Valuation in Practice (Book 1 of 2)
- **Author**: Simon Mak
- **Publisher**: Ascent Partners
- **Publication Date**: November 1, 2025
- **Pages**: 338
- **ISBN/ASIN**: B0FYTGNVWS (Kindle), Paperback available
- **Price**: $38.80 Kindle (44% off $69.80), $69.65 Paperback
- **Amazon URL**: https://www.amazon.com/Startup-Valuation-Comprehensive-Fast-Growing-Pre-Revenue-ebook/dp/B0FYTGNVWS/

## User Stories
1. **As a visitor**, I want to see the book cover and description on the homepage so I know this is the companion site to the textbook.
2. **As a reader**, I want a direct link to purchase the book on Amazon so I can buy it easily.
3. **As a student**, I want to see how the library modules map to book chapters so I can find relevant code examples.
4. **As an instructor**, I want to know about instructor resources (slides, test bank) so I can adopt the book for my course.

## Functional Requirements
- FR1: Homepage must display book cover image prominently
- FR2: Homepage must include book title, author, and brief description
- FR3: Homepage must include a "Buy on Amazon" button with direct link
- FR4: Homepage must show chapter-to-module mapping table
- FR5: Footer must include book purchase link
- FR6: Book cover image must be hosted locally in `docs/assets/images/`

## Non-Functional Requirements
- NFR1: Book cover image must be optimized for web (max 200KB)
- NFR2: All existing Ascent Partners branding must be preserved
- NFR3: Site must continue to pass `mkdocs build --strict`
- NFR4: No breaking changes to existing navigation or content

## Acceptance Criteria
- AC1: Book cover visible on homepage above the fold
- AC2: "Buy on Amazon" button links to correct Amazon URL
- AC3: Chapter-to-module mapping table matches book contents
- AC4: Footer includes book reference with purchase link
- AC5: Docs build and deploy without errors
- AC6: Site remains responsive on mobile
