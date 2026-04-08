# Modules: Reusable Python Libraries

## Overview

This folder contains 2 reusable Python modules that underpin document generation and Azure diagram production across multiple skills. Both modules are designed to be imported directly by skill scripts or invoked via CLI.

| Module | Lines | Primary Use |
|--------|-------|-------------|
| `docx_beautify.py` | ~2,760 | Word document creation and formatting |
| `azure_diagrams.py` | ~1,200 | Azure architecture diagrams as PNG |

---

## docx_beautify.py

Word document generation with professional formatting, preset styles, and palette-driven color systems. Handles everything from basic Markdown-to-DOCX conversion to full documents with cover pages, headers/footers, tables of contents, and embedded diagrams.

### Presets

| Preset | Use Case |
|--------|----------|
| `executive` | C-suite deliverables — clean, minimal, large type |
| `technical` | Engineering specs — monospace code blocks, dense tables |
| `memo` | Internal communications — compact, header-first |
| `report` | Long-form reports — TOC, section numbering, footnotes |

### Palettes

Each palette defines 15 named colors (primary, secondary, accent, background, text variants, status colors).

| Palette | Character |
|---------|-----------|
| `fortive` | Fortive brand blues and grays |
| `executive` | Deep navy, gold, white |
| `modern` | Teal, slate, warm white |
| `minimal` | Near-black, near-white, single accent |

### Key Functions

| Function | Description |
|----------|-------------|
| `create_document(preset, palette)` | Initialize a document with preset styles applied |
| `md_to_docx(md_text, doc)` | Convert Markdown to styled DOCX paragraphs |
| `add_professional_table(doc, headers, rows)` | Formatted table with header row shading |
| `add_key_value_table(doc, data_dict)` | Two-column label/value table |
| `add_status_table(doc, items)` | Status table with colored RAG indicators |
| `add_code_block(doc, code, language)` | Monospace code block with background shading |
| `add_callout_box(doc, text, style)` | Highlighted callout (info, warning, success, danger) |
| `add_cover_page(doc, title, subtitle, meta)` | Full cover page with title, date, author block |
| `add_header_footer(doc, header_text, footer_text)` | Section header and page-numbered footer |
| `add_toc(doc)` | Table of contents placeholder (requires Word update) |
| `add_mermaid_diagram(doc, mermaid_src)` | Render Mermaid diagram and embed as PNG |

### CLI

```bash
python docx_beautify.py input.md -o output.docx -p executive --cover
python docx_beautify.py input.md -o output.docx -p technical --palette fortive
```

### Dependencies

```
python-docx>=1.1.0
lxml>=5.0.0
Pillow>=10.0.0
requests>=2.31.0   # for Mermaid rendering via API
```

---

## azure_diagrams.py (v1.1)

Generates Azure architecture and data flow diagrams as PNG files using real Azure SVG icons. Diagrams are sized for common embed targets (DOCX, PPTX, standalone) and support dashed boundary boxes and labeled connection arrows.

### Output Presets

| Preset | Dimensions | Use Case |
|--------|-----------|---------|
| `docx_portrait` | 6.5" x 4.5" @ 150 DPI | DOCX page body, portrait layout |
| `docx_landscape` | 9" x 6" @ 150 DPI | DOCX page body, landscape layout |
| `pptx_full` | 13.33" x 7.5" @ 150 DPI | Full PPTX slide |
| `pptx_half` | 6.5" x 7.5" @ 150 DPI | Half-slide PPTX layout |
| `standalone` | 16" x 9" @ 200 DPI | Standalone PNG, high resolution |

### Icon Registry

78+ Azure service icons mapped by logical name to SVG file path within `Azure_Public_Service_Icons_V23/`. Includes:

- Core: `blob_storage`, `data_lake`, `sql_database`, `cosmos_db`, `key_vault`, `service_bus`
- AI/ML: `machine_learning`, `cognitive_services`, `openai`, `ai_search`, `bot_service`
- Integration: `data_factory`, `logic_apps`, `api_management`, `event_hub`, `event_grid`
- Data: `synapse`, `databricks`, `purview`, `stream_analytics`
- Infra: `virtual_machine`, `app_service`, `container_registry`, `kubernetes`
- Special: `oracle_database`, `sharepoint`, `power_bi`, `teams`

### Features

- Icons rendered via cairosvg (SVG to PNG, then composited with matplotlib)
- Dashed boundary boxes for grouping components into logical zones
- Labeled connection arrows with directional control
- Auto-layout assists for grid and flow arrangements
- Text labels with configurable font size and wrapping

### Dependencies

```
cairosvg>=2.7.0
matplotlib>=3.8.0
Pillow>=10.0.0
```

### Cairo DLL Requirement (Windows)

cairosvg requires native Cairo libraries. On Windows, place the MSYS2 64-bit DLLs in a folder on `PATH`:

```
Location: C:\Users\tmanyang\tools\cairo-dlls\
```

See `research/memory/reference_cairosvg_windows.md` for the complete DLL list and installation steps.

### Usage Examples

```python
from azure_diagrams import AzureDiagramBuilder

builder = AzureDiagramBuilder(preset="docx_landscape")
builder.add_boundary("Ingestion Zone", x=0.05, y=0.1, w=0.3, h=0.8)
builder.add_icon("data_factory", label="ADF", x=0.1, y=0.4)
builder.add_icon("databricks", label="Databricks", x=0.45, y=0.4)
builder.add_arrow("data_factory", "databricks", label="raw files")
builder.save("architecture.png")
```

### Called By

- `docx-beautify` skill — embeds architecture diagrams in DOCX deliverables
- `powerpoint-create` skill — embeds diagrams in PPTX slides
- `ai-ucb-docs` skill — generates EA Document and Solution Design diagrams

---

## Installation

Both modules ship as single-file Python scripts with no package installation required. Copy the module file to your working directory or add the `modules/` folder to `PYTHONPATH`:

```bash
export PYTHONPATH="path/to/repo/modules:$PYTHONPATH"
```

---

## Sync Workflow

Module files live in two places:

1. **Canonical source**: `modules/` in this repo
2. **Active copy**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Document Beautification\`

When changes are made to the OneDrive copy (during active development), sync back to the repo:

```bash
cp "OneDrive/.../Document Beautification/docx_beautify.py" modules/
cp "OneDrive/.../Document Beautification/azure_diagrams.py" modules/
```

The repo copy is the version-controlled reference. The OneDrive copy is the working copy during active development.
