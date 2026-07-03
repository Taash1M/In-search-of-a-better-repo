---
name: Presentation Beautification Skill Project
description: python-pptx module + skill for consulting-grade PPT with presets/palettes, 18+ functions, 5 palettes, template builds, OfficeCLI-sourced enhancement backlog
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
**Project**: Presentation Beautification Skill — python-pptx module + Claude Code skill for producing consulting-grade PowerPoint presentations.

**Why:** Existing powerpoint-create skill scored D (75/120, 70% redundant). No preset/palette cascade. Requires Node.js. New skill consolidates 5 GitHub sources into one python-pptx-only system with docx_beautify's proven architecture.

**How to apply:** All artifacts in `<USER_HOME>/OneDrive - <ORG>\Claude code\Presentation Beautification\`. Full project memory at `PROJECT_MEMORY.md` in that folder. GitHub research at `Github_Research.md` (5 repos documented). Standing instructions: always update Github_Research.md when consuming repos, always log sessions to PROJECT_MEMORY.md, always push gotchas to skill file.

**Key details:**
- Engine: python-pptx only (no Node.js/PptxGenJS)
- Architecture: mirrors docx_beautify (4 presets x 5 palettes, cascade system)
- Presets: executive, technical, pitch, report
- Palettes: fortive, executive, modern, minimal, fortive_ai
- 18 public functions, 11 internal helpers, 12 chart types
- Design rules: action titles, 3-second rule, 60-30-10, CRAP principles, Ghost Deck method
- Automated quality validation (font count, color count, text overflow, contrast)
- Sources: powerpoint-create.md, docx_beautify.py, ClaudeSkills PPT Designer, mcp-server-ppt, MarpToPptx, PptxGenJS, OfficeCLI
- Status: v2 complete + AI Blueprint recreation. Session 5 added OfficeCLI gap analysis with 13 PPTX + 10 DOCX backlog items. Session 7 added frontend-slides standalone, 2 new palettes, content density limits.
- Template-based builds proven (placeholder removal, image cropping, boundary overflow prevention)
- Test suite: 9 suites → 71 tests, ALL PASS (Session 7: +8 tests for new palettes + content density)
- Palettes expanded: +swiss_modern, +paper_ink (now 7 total)
- Content density enforcement: max 6 bullets per slide, auto-split to continuation slides
- frontend-slides standalone function for rapid diagram/content slides without full template
- Not yet promoted to active commands dir
- Note: The active `powerpoint-create.md` skill (in commands dir) was enhanced 2026-04-10 with mandatory 3-stage QA workflow (content + programmatic layout + visual). The programmatic layout QA uses python-pptx to check OOB, margins, tiny text, and real overlaps while filtering intentional text-on-shape layering.
- **2026-05-20 update (presenton analysis)**: Cloned `presenton/presenton` into project dir for competitive analysis. Key findings and improvement roadmap:
  - **P0 — Schema-driven layouts**: Presenton uses Zod schemas with character limits per field + TSX rendering. 193 templates across 14 families. Our skill has 14 patterns with no schema enforcement. → Port top 8 layouts to JSON Schema with char limits.
  - **P0 — Two-stage LLM pipeline**: Separate content generation + layout selection calls. Our skill does single-pass. → Add explicit layout selection step.
  - **P1 — OKLCH color science**: `utils/theme_utils.py` (357 lines, zero deps) generates palettes with WCAG 6:1+ contrast guaranteed. Our skill has 7 static palettes. → Port OKLCH generator.
  - **P1 — Semantic icon search**: fastembed vector store over ~5,000 SVG icons. → Consider pre-built icon keyword index.
  - **What we do better**: native editable PPTX (presenton renders HTML→screenshots), Azure architecture diagrams, consulting design system (Pyramid Principle, SCR, Ghost Deck), 3-stage QA, offline operation.
  - **Repo location**: `<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification\presenton\`
  - **Most portable asset**: `presenton/servers/fastapi/utils/theme_utils.py` — pure Python OKLCH color math, drop-in ready.
- **2026-05-20 update (GPT Image 2 integration)**: Successfully used GPT Image 2 (Azure AI Foundry) to generate 12 illustrated panels for PPTX slides. Style: flat 2D corporate, isometric, white background. ~170s per image at 1536x1024 high quality. User strongly prefers illustrated panels (Options C/D) over emoji cartoon strips (Options A/B) for consultant-grade decks.
- **2026-05-26 update (academic case competition)**: MSIS 550 Anthropic vs. Google — produced 3 PPTX versions (V2 FINAL, Veritas Clean, Illustrated) + DOCX write-up. Veritas + Illustrated dual-version approach proven: same content, Veritas for clean minimalism (82 KB), Illustrated for visual impact with 6 GPT Image 2 panels (3 MB). 3-stage validation script (`validate_pptx.py`) checks data points (30/30), exhibits (8/8), speaker notes (14/14), layout bounds, font caps, and cross-version note consistency. Both versions passed with 0 critical issues. Masters-writing-skill (userSettings) used for full 8-step workflow including PhD reviewer scoring (86→93/100).
- **2026-05-27 update (Fluke AI Office Hours — 3-version tier)**: Produced 3 PPTX versions on Fluke Template with Aptos fonts: V1 Veritas Clean (1.4 MB), V2 Illustrated with 10 images on 8 key slides (7.4 MB), V3 Fully Illustrated with 17 images on all 14 slides (13.2 MB). First use of Veritas Clean design adapted to Aptos font family (instead of Calibri). New patterns: `fit_image()` helper for right-side image panels (x=8.20, w=4.50), 3-stacked image layout for problem slides (3 images vertically in right panel), OneDrive template lock workaround (copy to `template_base.pptx`). GPT Image 2 generation across 2 batches (10+7 images, ~200s each). Validate.py expanded to cover 3 versions. All 3 passed QA with identical speaker notes and data points.
- **2026-04-14 update**: Skill enhanced with `add_picture_fit()` aspect-ratio-preserving image helper (python-pptx + PIL). Added to python-pptx Images section, PptxGenJS Images section (`sizing: contain`), and Build-Time Prevention rules #6 (D2 grid-row layout for wide diagrams) and #7 (mandatory aspect-ratio preservation). Proven on Phase 2 PPTX — fixed stretching on 4 diagram slides (architecture, execution flow, runbook, self-healing).
- **2026-04-14 update (visual quality)**: Added "Diagram Visual Quality Standards" section with node shape variety, layered zones, connection line discipline, whitespace ratios, color discipline, split layout pattern. Added proven "Icon Row with Bracket Connectors" pattern (FLOWCHART_EXTRACT triangle arrowheads, bracket bar + vertical drops) and "Numbered Vertical Timeline" pattern (navy circles, gray connecting line). All validated via Veritas Suite deck analysis + Leadership Forum sample slide. docx-beautify.md also updated with Mermaid/D2 equivalents.
- **2026-04-16 update**: Skill Judge re-eval scored powerpoint-create B+ (100/120). Added 7-branch decision tree at top. Added Pattern 13: Dark Architecture Diagram (semantic colors from Cocoon-AI). Decision: keep file intact (~2,900 lines) — no split needed. All 4 evaluated skills now have decision trees.
- **2026-04-21 update (Veritas clean design)**: New design language proven on AI Next Steps Plan v3. White backgrounds, large black ALL-CAPS titles (34pt) + "FLUKE" watermark top-right, thin blue accent line, thin borders (not filled panels), dashed blue borders for grouping (`add_dashed_rect()` via XML `a:prstDash val="dash"`), gold borders for recommended options. Two proven design systems now available: (1) Bold Signal Light (dark/navy, yellow accent — Leadership Forum), (2) Veritas Clean (white, monochrome + blue/gold accents — AI Next Steps v3).
- **2026-05-03 update (v3 Clean + title overlap fix)**: Third design variant proven on MSIS 579 IKEA presentations (4 decks × 16 slides). Key finding: **titles must be capped at 20pt** to prevent overlap — 34pt titles caused consistent text-to-text collisions across all 4 decks. Font hierarchy from user's manual Angle B rebuild: S1 title 28pt, content titles 20pt, subtitles 14pt, stat callouts 36pt, market numbers 24pt, hero scores 48pt, Q&A title 34pt. powerpoint-create.md skill updated with anti-overlap rules (Build-Time Prevention #7, QA check 3b, MAX_TITLE_PT=22). python-pptx font size gotcha: `.font.size` returns None when set via `defRPr` — must use lxml to read `defRPr/@sz` directly.
