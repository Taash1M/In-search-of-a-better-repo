---
name: Presentation Beautification Skill Project
description: python-pptx module + skill for consulting-grade PPT with presets/palettes, 18+ functions, 5 palettes, template builds, OfficeCLI-sourced enhancement backlog
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
**Project**: Presentation Beautification Skill — python-pptx module + Claude Code skill for producing consulting-grade PowerPoint presentations.

**Why:** Existing powerpoint-create skill scored D (75/120, 70% redundant). No preset/palette cascade. Requires Node.js. New skill consolidates 5 GitHub sources into one python-pptx-only system with docx_beautify's proven architecture.

**How to apply:** All artifacts in `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Presentation Beautification\`. Full project memory at `PROJECT_MEMORY.md` in that folder. GitHub research at `Github_Research.md` (5 repos documented). Standing instructions: always update Github_Research.md when consuming repos, always log sessions to PROJECT_MEMORY.md, always push gotchas to skill file.

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
- **2026-04-14 update**: Skill enhanced with `add_picture_fit()` aspect-ratio-preserving image helper (python-pptx + PIL). Added to python-pptx Images section, PptxGenJS Images section (`sizing: contain`), and Build-Time Prevention rules #6 (D2 grid-row layout for wide diagrams) and #7 (mandatory aspect-ratio preservation). Proven on Phase 2 PPTX — fixed stretching on 4 diagram slides (architecture, execution flow, runbook, self-healing).
- **2026-04-14 update (visual quality)**: Added "Diagram Visual Quality Standards" section with node shape variety, layered zones, connection line discipline, whitespace ratios, color discipline, split layout pattern. Added proven "Icon Row with Bracket Connectors" pattern (FLOWCHART_EXTRACT triangle arrowheads, bracket bar + vertical drops) and "Numbered Vertical Timeline" pattern (navy circles, gray connecting line). All validated via Veritas Suite deck analysis + Leadership Forum sample slide. docx-beautify.md also updated with Mermaid/D2 equivalents.
- **2026-04-16 update**: Skill Judge re-eval scored powerpoint-create B+ (100/120). Added 7-branch decision tree at top. Added Pattern 13: Dark Architecture Diagram (semantic colors from Cocoon-AI). Decision: keep file intact (~2,900 lines) — no split needed. All 4 evaluated skills now have decision trees.
- **2026-04-21 update (Veritas clean design)**: New design language proven on AI Next Steps Plan v3. White backgrounds, large black ALL-CAPS titles (34pt) + "FLUKE" watermark top-right, thin blue accent line, thin borders (not filled panels), dashed blue borders for grouping (`add_dashed_rect()` via XML `a:prstDash val="dash"`), gold borders for recommended options. Two proven design systems now available: (1) Bold Signal Light (dark/navy, yellow accent — Leadership Forum), (2) Veritas Clean (white, monochrome + blue/gold accents — AI Next Steps v3).
