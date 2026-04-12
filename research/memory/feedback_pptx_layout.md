---
name: PPTX layout discipline
description: Strict rules for PPTX slide layout — no overlaps, no OOB, contextual images only, aspect ratio preservation, mandatory 3-stage QA
type: feedback
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
Never place shapes or images that overflow slide boundaries. Every visual must fit within a safe content zone (inside margins, below title, above footer).

**Why:** First PPTX drafts had overlapping shapes, images extending past slide bottom, and randomly placed stock photos that weren't relevant to slide content. User called these out explicitly. A subsequent QA round (2026-04-10) caught Slide 2 initiative cards extending 0.08" past the slide bottom and footer text violating the 0.25" safe zone — both invisible in code review but caught by the programmatic layout QA script.

**How to apply:**
- Define a safe content zone (margins + title + footer clearance) and enforce it for every shape
- Use a `fit_image()` function that constrains to both max_width AND max_height while preserving aspect ratio — never set just width and let height blow out
- Only place downloaded images where they're contextually relevant to the slide topic (e.g., analytics_dashboard on CRM slides, manufacturing_floor on TechMentor)
- **MANDATORY 3-stage QA** after every PPTX build (see powerpoint-create skill, QA Workflow section):
  1. Content QA (markitdown text extraction)
  2. Programmatic Layout QA (python-pptx bounds/overlap/text-size check) — catches OOB, margin violations, tiny text, real overlaps while filtering intentional text-on-shape layering
  3. Visual QA (soffice rendering + subagent inspection when available)
- For grid/card layouts: always compute the bottom edge of the last row mathematically (`gridY + rows*(cardH+rowGap) - rowGap + cardH`) and verify it fits before writing code
- Standard gap (0.2") between elements, consistent margins across all slides
- When elements are dynamically positioned (callout bars, footers below grids), use computed positions relative to the grid end rather than hardcoded y values
