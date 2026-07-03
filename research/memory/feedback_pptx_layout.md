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
- **Veritas clean header/footer pattern (proven 2026-04-21):**
  - `v_header()`: 34pt bold black title at (0.60, 0.30), "<ORG>" watermark 34pt light gray at right, 14pt gray subtitle, thin blue accent line at y=1.28
  - `v_footer()`: thin LGRAY line at y=7.12, 8pt silver centered text at y=7.16
  - Content safe zone: y=1.42 to y=7.05, x=0.60 to x=12.73
  - `add_dashed_rect()`: use XML `a:prstDash val="dash"` on the `a:ln` element (more reliable than `MSO_LINE_DASH_STYLE` enum import)
- **Title text overlap prevention (proven 2026-05-03):**
  - **#1 cause of PPTX overlap is oversized titles.** Slide titles at 34pt+ consistently collide with content below or adjacent shapes across all deck sizes.
  - **Cap all content slide titles at 20pt.** Only S1 cover (28pt) and Q&A/closing (34pt) go higher.
  - Font hierarchy (from user's manual Angle B rebuild, validated across 4 decks):
    - S1 title: 28pt, content titles (S2-S15): 20pt, subtitles: 14pt
    - Stat callouts: 36pt, market size numbers: 24pt, hero scores: 48pt, Q&A title: 34pt
  - Width estimation heuristic: 20pt Calibri ≈ 0.11" per character. If `len(title) * 0.11 > shape_width_inches`, reduce font or shorten text.
  - powerpoint-create.md skill updated: Build-Time Prevention #7 (title cap), QA check 3b (flags title-zone text > 22pt), `MAX_TITLE_PT = 22`, `MIN_FONT_PT = 8`.
- **python-pptx XML gotchas (proven 2026-04-19, extended 2026-05-03):**
  - `a:bodyPr anchor` accepts ONLY `t`, `ctr`, `b` — NOT `tl`, `tr`, `bl`, `br`. Using `tl` (from MSO_ANCHOR.TOP mapping) causes PowerPoint to reject the file on open.
  - Bullet `a:pPr indent` must be NEGATIVE (e.g., `-177800`) for hanging bullets. Positive indent pushes bullet+text together.
  - `str(PRGBColor)` happens to return `'003366'` format but this is fragile. Always use `f'{c[0]:02X}{c[1]:02X}{c[2]:02X}'` for `a:srgbClr val` attributes in manual XML construction.
  - When constructing `a:solidFill` → `a:srgbClr` for table cell fills, insert into `tcPr` — the element hierarchy must be `a:tcPr` → `a:solidFill` → `a:srgbClr`.
  - **Font size detection**: `.font.size` returns `None` when size is set via `defRPr` (paragraph-level default). Must use lxml to directly read `defRPr/@sz` and `rPr/@sz` attributes. Always set BOTH levels when changing font sizes programmatically.
- **D2 diagram embedding in PPTX (proven 2026-05-03):**
  - `replace_slide_with_diagram()` pattern: clear all shapes from `_spTree` (remove `sp`, `grpSp`, `cxnSp`, `pic` elements), add top bar + title textbox + D2 PNG with aspect-ratio-preserving fit
  - Use PIL `Image.open()` to get image dimensions, compute fit within content zone (x=0.40, y=1.20, max_w=12.5, max_h=5.9) preserving aspect ratio, center in zone
  - For DOCX: replace image blobs via `doc.part.rels[rel_id].target_part._blob = new_bytes` (by image index order) — avoids full document regeneration
  - See `update_all_diagrams.py` in UBI AI Integration project for full implementation
- **Veritas + Illustrated multi-version pattern (proven 2026-05-26, extended 2026-05-27):**
  - Generate content-complete Veritas Clean version first (text-only, ~1.4 MB)
  - Create illustrated variant that adds GPT Image 2 panels on right side of key slides (~7 MB)
  - Optionally create fully illustrated variant with images on every slide (~13 MB)
  - Content on illustrated slides is compacted to left ~7" to make room for ~4.5" image panel (x=8.20)
  - Use `add_picture_fit()` or `fit_image()` with dashed LGRAY border around image area
  - Run `validate.py` on ALL versions: data points, exhibits, speaker notes, bounds, font caps, cross-version note consistency
  - All versions share identical speaker notes and analytical content
  - **3-version tier proven on <ORG> AI Office Hours**: V1 Veritas (text), V2 Illustrated (8 key slides), V3 Full (all 14 slides with 17 images)
