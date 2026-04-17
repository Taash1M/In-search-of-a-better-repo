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
- Use `add_picture_fit()` helper (PIL + python-pptx) that constrains to both max_width AND max_height while preserving aspect ratio, centered in bounding box — never use raw `add_picture()` with fixed w+h for generated images
- For PptxGenJS, always use `sizing: { type: "contain" }` for diagrams/charts/screenshots
- Only place downloaded images where they're contextually relevant to the slide topic (e.g., analytics_dashboard on CRM slides, manufacturing_floor on TechMentor)
- **MANDATORY 3-stage QA** after every PPTX build (see powerpoint-create skill, QA Workflow section):
  1. Content QA (markitdown text extraction)
  2. Programmatic Layout QA (python-pptx bounds/overlap/text-size check) — catches OOB, margin violations, tiny text, real overlaps while filtering intentional text-on-shape layering
  3. Visual QA (soffice rendering + subagent inspection when available)
- For grid/card layouts: always compute the bottom edge of the last row mathematically (`gridY + rows*(cardH+rowGap) - rowGap + cardH`) and verify it fits before writing code
- Standard gap (0.2") between elements, consistent margins across all slides
- When elements are dynamically positioned (callout bars, footers below grids), use computed positions relative to the grid end rather than hardcoded y values
- **Dataflow/process flow visual quality standard** (proven 2026-04-14 via Veritas Suite reference):
  - Use bracket connectors (horizontal bar + vertical drops) + triangle arrowheads between icon strips — not text arrows or plain lines
  - Use numbered vertical timelines (navy circles + gray connecting line) for callout panels — not accent-bar cards
  - Node shape variety: hexagons for agents, diamonds for decisions, cylinders for data stores — never all rectangles
  - Max 3 accent colors per diagram + neutrals; light fills with dark borders
  - Connection lines: thin (1-1.5px), single muted color, small arrowheads
  - 60-70% content fill ratio — if >75% is shapes/lines, too dense
- **Architecture bubble connectors (proven 2026-04-16):**
  - PIL reads image dims to compute fitted position (aspect-ratio-aware) within bounding box
  - Bubbles in fixed margin columns: LEFT at x=0.13, RIGHT at x=6.95 (flush with walkthrough divider)
  - Tuple format: `(label, desc, img_fx, img_fy, side)` where img_fx/fy = fraction within FITTED image
  - `draw_dotted_segment()` must use NO fill (`seg.fill.background()`) + border-only `a:ln` with `prstDash val="dot"` for thin dotted connectors — never solid fill + dotted border (looks thick)
  - Horizontal connector from bubble edge to agent's (x, y) position in diagram
