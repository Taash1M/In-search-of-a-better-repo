# Document Skills

7 skills covering the full document lifecycle — from raw extraction through professional formatting and export. Together they form a complete document pipeline for enterprise deliverables.

---

## Overview

The document skill group handles every stage of document work: extracting structured data from raw sources (PDFs, scans, images), generating professionally formatted outputs (Word, Excel, PowerPoint), building Azure architecture diagrams, and automating Power BI reports. Skills are designed to chain together but can each be invoked independently.

---

## Architecture

```
Raw Document (PDF / DOCX / image / scan / engineering drawing)
        │
        ▼
/doc-extract              Extract structured data (JSON, fields, tables, entities)
/doc-extract-reference    Advanced patterns reference (on-demand, loaded by doc-extract)
        │
        ├──────────────────────────────────────────────┐
        ▼                                              ▼
/docx-beautify            Professional Word docs      /excel-create
  4 presets, 4 palettes     Fortive-branded             openpyxl + xlsxwriter
  Mermaid + D2 + cairosvg   cover pages, TOC            sparklines, VBA macros
        │
        ▼
/powerpoint-create        Presentation decks
  python-pptx               slide templates, layouts
        │
        ├──────────────────────────────────────────────┐
        ▼                                              ▼
/azure-diagrams           Architecture diagrams       /powerbi-desktop
  78+ Azure icons           cairosvg rendering          Desktop automation
  5 output presets          mandatory quality gate       report generation
```

---

## File Inventory

| Skill | Purpose | Key Capabilities | Lines | Grade/Status |
|-------|---------|-----------------|------:|--------------|
| `docx-beautify.md` | Professional DOCX creation and formatting | 4 presets (executive/technical/memo/report), 4 palettes, Mermaid SVG + D2 + matplotlib + cairosvg diagram backends, cover pages, TOC auto-generation, Fortive branding | 1,086 | Production |
| `doc-extract.md` | Unified document extraction | ContextGem (7 concept types), RAG-Anything (multimodal), agentic-doc (batch patterns), PDF/DOCX/image/scan input | 589 | B+ (104/120) |
| `doc-extract-reference.md` | Advanced extraction patterns reference | Converter options, JsonObject patterns, batch pipeline design, engineering drawing schema, on-demand loading | 452 | Reference |
| `excel-create.md` | Excel workbook creation | openpyxl (read/write/modify), xlsxwriter (rich formatting), sparklines, charts, VBA macros, named ranges, conditional formatting | 2,005 | Production |
| `powerpoint-create.md` | PowerPoint presentation creation | python-pptx, slide templates, custom layouts, shape manipulation, image embedding, table formatting | 2,093 | Production |
| `powerbi-desktop.md` | Power BI Desktop automation | Report generation, DAX measures, data model manipulation, query generation, export automation | 4,749 | Production |
| `azure-diagrams.md` | Azure architecture diagrams | Module `azure_diagrams.py` v1.1, 78+ Azure icon registry, 5 output presets, mandatory visual quality gate (validate → fix → regenerate loop) | 474 | Production |

---

## Skill Details

### docx-beautify.md — Professional Word Documents
The primary output skill for Word documents. Backed by the `docx_beautify.py` module (~2,760 lines, 48+ functions). Presets:
- **executive** — clean, minimal, leadership-facing
- **technical** — dense, code-friendly, sidebar callouts
- **memo** — short-form internal communication
- **report** — full-length with cover page, TOC, appendices

Palettes: Fortive Blue, Slate Gray, Warm Neutral, High Contrast. Diagram backends are composable — Mermaid SVG for flowcharts, D2 (v0.7.1) for architecture diagrams, matplotlib for charts, cairosvg for SVG-to-PNG conversion.

### doc-extract.md — Unified Extraction (B+ 104/120)
Integrates three extraction approaches under a single interface:
- **ContextGem** — declarative concept extraction (aspects, events, statements, named entities, numeric data, boolean flags, relationships)
- **RAG-Anything** — multimodal extraction handling images, tables, equations, and scanned pages
- **agentic-doc** — batch pipeline patterns for high-volume processing

Tested against 18/19 PLM engineering drawings with 94% title block accuracy in technical validation.

### doc-extract-reference.md — Advanced Patterns (On-Demand)
Loaded by `doc-extract` when complex patterns are needed. Contains: detailed converter option tables, JsonObject schema patterns, batch pipeline architecture, engineering drawing extraction schema, and error recovery recipes. Not loaded by default to conserve context.

### excel-create.md — Excel Workbooks
Full Excel authoring skill with two library modes:
- **openpyxl** — for reading, modifying, and writing existing workbooks
- **xlsxwriter** — for rich new workbooks with sparklines, advanced charts, and VBA macros

Covers named ranges, conditional formatting, data validation, pivot tables, and multi-sheet workbook design.

### powerpoint-create.md — Presentation Decks
python-pptx skill for creating slide decks from scratch or templates. Handles custom slide layouts, shape and text box positioning, image embedding, table formatting, and slide master management. Largest skill in the document group by line count (2,093).

### powerbi-desktop.md — Power BI Automation
The most comprehensive skill in this group (4,749 lines). Covers Power BI Desktop automation including report structure, DAX measure generation, data model configuration, query folding patterns, and export pipelines. Integrates with the UBI curated dataset layer.

### azure-diagrams.md — Architecture Diagrams
Sub-skill that generates Azure architecture and data flow diagrams. Key components:
- **Module**: `azure_diagrams.py` v1.1 (called by docx-beautify and standalone)
- **Icon registry**: 78+ Azure service icons from Azure_Public_Service_Icons_V23 (SVG)
- **Output presets**: presentation, technical, executive, dark, high-contrast
- **Quality gate**: every diagram is validated for missing icons, overlap, and distortion before embedding — fix+regenerate loop until passing

---

## Pipeline Walkthrough

**Example: Convert a scanned PDF into a formatted executive report with architecture diagram**

```python
# Step 1 — Extract structured data from the raw document
/doc-extract input="Q1_Architecture_Review.pdf" mode="agentic-doc"
# Returns: JSON with sections, tables, key facts

# Step 2 — Generate architecture diagram from extracted topology
/azure-diagrams topology=extracted_topology preset="executive"
# Returns: PNG diagram file

# Step 3 — Compose the final Word document
/docx-beautify preset="executive" palette="Fortive Blue"
#   - Embeds extracted content
#   - Inserts architecture diagram
#   - Generates cover page and TOC
# Returns: formatted .docx file

# Step 4 (optional) — Produce a companion Excel data appendix
/excel-create data=extracted_tables style="formatted"
```

**Example: Build a Power BI report from a Gold layer view**

```python
/powerbi-desktop source="Gold.FactSOBacklog" measures=["Revenue", "Backlog"]
```

---

## Dependencies

| Package | Version | Used By |
|---------|---------|---------|
| `python-docx` | >=1.1 | docx-beautify |
| `openpyxl` | >=3.1 | excel-create |
| `xlsxwriter` | >=3.1 | excel-create |
| `python-pptx` | >=0.6 | powerpoint-create |
| `cairosvg` | >=2.7 | docx-beautify, azure-diagrams |
| `matplotlib` | >=3.8 | docx-beautify |
| `contextgem` | latest | doc-extract |
| `D2 CLI` | v0.7.1 | docx-beautify (diagram backend) |

**cairosvg on Windows** requires MSYS2 64-bit DLLs. See `reference_cairosvg_windows.md` in MEMORY for setup notes. Cairo DLLs are at `C:\Users\tmanyang\tools\cairo-dlls\`.

**D2 CLI** is at `C:\Users\tmanyang\tools\d2\d2-v0.7.1\bin\d2.exe`. Use forward-slash paths only; avoid `$` in labels (triggers substitution); `|md|` blocks break on `<`.

---

## Sync Workflow

Skills in this directory are the canonical versions. All 7 are promoted to `~/.claude/commands/` for global availability.

To sync after editing:

```bash
# Sync a specific skill
cp "skills/document/docx-beautify.md" "$HOME/.claude/commands/docx-beautify.md"

# Sync all document skills at once
for f in docx-beautify doc-extract doc-extract-reference excel-create powerpoint-create powerbi-desktop azure-diagrams; do
  cp "skills/document/${f}.md" "$HOME/.claude/commands/${f}.md"
done
```

To update `docx_beautify.py` (backing module):
- Source: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Document Beautification\docx_beautify.py`
- After changes, re-run the Skill Judge against `docx-beautify.md` to confirm grade is maintained
