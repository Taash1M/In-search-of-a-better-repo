---
name: document-beautification-skill
description: "docx-beautify skill/module — project dir, v6, docx_beautify.py (~2760 lines, 48+ funcs, 4 presets/palettes, diagram backends), D2 CLI path + gotchas, Azure icons V23, cairosvg via sitecustomize, promoted to ~/.claude/commands/"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

# Document Beautification Skill

- **Project dir**: `<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification\`
- **Created**: 2026-03-20, **v6**: 2026-03-29
- **Files**: `docx-beautify.md` (skill), `docx_beautify.py` (module, ~2760 lines), `PROJECT_MEMORY.md`
- **Module**: 48+ functions, 4 presets, 4 palettes, diagram backends (Mermaid SVG, D2, matplotlib, cairosvg)
- **D2 CLI**: v0.7.1 at `<USER_HOME>/tools\d2\d2-v0.7.1\bin\d2.exe`
- **Azure icons**: `Azure_Public_Service_Icons_V23` in project dir (V23, SVG)
- **D2 gotchas**: full list in `PROJECT_MEMORY.md` (project dir). Highlights: forward-slash paths only; `|md|` SVG-only; theme 0 (light) for DOCX; grid-rows/columns for aspect ratio; grid children don't support edges
- **cairosvg**: working via `sitecustomize.py` auto-preload (2026-06-08), see [[cairosvg-windows-setup]]
- **Promoted** to `~/.claude/commands/docx-beautify.md` on 2026-04-06

**GOTCHA — python-docx column widths are IGNORED under auto/percent table layout (2026-06-25):** setting `cell.width`/`column.width` or `tblW type=pct` does NOT control column widths — Word distributes columns evenly, which silently blows up thin accent-bar columns (e.g. a 0.12cm gold left-bar) and narrow number columns to ~50%. Symptom: giant colored blocks / huge whitespace gaps in the rendered DOCX even though the code "set" small widths. FIX: force a **fixed grid** per table — `w:tblLayout type=fixed` + explicit `w:tblGrid`/`w:gridCol` (twips, 567/cm) + per-cell `w:tcW` in dxa. Verify by reading back `tblGrid` gridCol widths. To visually QA a DOCX: convert to PDF via Word COM (`SaveAs ... wdFormatPDF=17`) and Read the PDF (LibreOffice not installed on this box). Used for the Claude Code seat-nomination email DOCX (HTML→table-based DOCX with gold accent bars).

Related: [[presentation-beautification]] · [[diagram-quality-gate]] · [[diagram-visual-quality-standard]] · [[html-for-outlook-email]]
