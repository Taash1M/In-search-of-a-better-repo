---
name: docx-beautify
description: "Use this skill whenever the user wants to create, convert, format, or beautify Word documents (.docx files) using Python. Triggers include: any mention of 'Word doc', 'docx', 'document', 'report', 'memo', requests to convert Markdown to DOCX, format tables professionally, add cover pages, headers/footers, or produce polished deliverables. Also use when post-processing existing DOCX files to improve formatting. Do NOT use for PDFs, spreadsheets, or PowerPoint files."
---

# Document Beautification Skill (python-docx)

Create professional, consultant-grade Word documents using python-docx. This skill provides presets, color palettes, table formatting, Markdown conversion, and OXML patterns.

## Quick Start

```bash
pip install python-docx
```

### Reusable Module

A complete reusable module is available at:
`<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification\docx_beautify.py`

```python
from docx_beautify import create_document, md_to_docx, add_professional_table, add_cover_page

# Create a new document with preset styling
doc = create_document(preset="executive")

# Convert Markdown to a polished DOCX
md_to_docx("input.md", "output.docx", preset="technical", cover_page=True, author="Taashi Manyanga")
```

If the module is not importable (different working directory), copy the needed functions inline.

## Quick-Start Decision Tree

```
What do you need?
├─ Create a new document from scratch → create_document(preset=...) + add_*() functions
├─ Convert Markdown to DOCX → md_to_docx("input.md", "output.docx", preset=..., cover_page=True)
├─ Beautify an existing DOCX → Open with python-docx, apply preset styles, re-save
├─ Add diagrams to a document → Use azure-diagrams sub-skill (generate_for_docx)
└─ Format tables professionally → add_professional_table() with OXML shading/borders
```

## Architecture

```
Preset System          OXML Helpers           Content Engine
(palette + fonts +     (shading, borders,     (Markdown parser,
 margins + sizes)       field codes, margins)   inline formatting)
        |                      |                       |
        v                      v                       v
    create_document() -----> add_*() functions -----> md_to_docx()
                                                        |
                                                        v
                                                   .docx output
```

---

## Presets

Four built-in presets control the entire document appearance. Select one and override individual settings as needed.

| Preset | Use Case | Body Font | H1 Size | Palette |
|--------|----------|-----------|---------|---------|
| `executive` | Board decks, strategy docs | Calibri 11pt | 26pt | Deep navy + muted gold |
| `technical` | Engineering specs, STMs | Calibri 10pt | 24pt | Fortive navy + corporate blue |
| `memo` | Internal memos, quick notes | Calibri 11pt | 20pt | Minimal grayscale |
| `report` | Formal reports, deliverables | Calibri 11pt | 28pt | Fortive navy + gold accent |

### Preset Structure

```python
PRESETS = {
    "executive": {
        "palette": "executive",
        "font_body": "Calibri",
        "font_heading": "Calibri",
        "font_code": "Consolas",
        "size_body": 11,       # pt
        "size_h1": 26,
        "size_h2": 18,
        "size_h3": 14,
        "size_h4": 12,
        "size_code": 9,
        "size_table": 9,
        "margin_top": 2.5,     # cm
        "margin_bottom": 2.5,
        "margin_left": 2.5,
        "margin_right": 2.5,
        "line_spacing": 1.15,
        "space_after_para": 8, # pt
        "heading_color": True,
        "table_style": "professional",
    },
}
```

---

## Color Palettes

Four palettes available. Each has 15 named colors for consistent theming.

| Palette | Primary | Secondary | Accent | Best For |
|---------|---------|-----------|--------|----------|
| `fortive` | #003366 (Dark navy) | #005EB8 (Corporate blue) | #F3C13A (Gold) | Branded corporate docs |
| `executive` | #1A3A5C (Deep navy) | #2F5496 (Royal blue) | #C5A55A (Muted gold) | C-suite deliverables |
| `modern` | #4A90D9 (Bright blue) | #6C5CE7 (Purple) | #00B894 (Emerald) | Innovation / tech docs |
| `minimal` | #333333 (Charcoal) | #555555 (Gray) | #0066CC (Blue) | Clean, distraction-free |

### Palette Keys

Every palette provides these keys:

```python
{
    "primary":    "003366",  # Headings, title, accent bars
    "secondary":  "005EB8",  # Sub-headings, links
    "accent":     "F3C13A",  # Highlights, cover page rule
    "text":       "333333",  # Body text
    "light_text": "666666",  # Captions, footers
    "bg_light":   "F5F5F5",  # Key-value table key cells
    "bg_alt":     "EDF2F7",  # Alternating row tint
    "header_bg":  "003366",  # Table header background
    "header_fg":  "FFFFFF",  # Table header text
    "border":     "CCCCCC",  # Borders, rules
    "success":    "28A745",  # Green (pass, complete)
    "warning":    "F3C13A",  # Yellow (warn, caution)
    "danger":     "DC3545",  # Red (fail, error)
    "info":       "17A2B8",  # Teal (info, pending)
    "code_bg":    "F5F5F5",  # Code block background
}
```

---

## Document Creation

### New Document with Preset

```python
from docx_beautify import create_document

doc = create_document(preset="executive")
doc.add_heading("Quarterly Review", level=1)
doc.add_paragraph("Executive summary of Q1 performance.")
doc.save("report.docx")
```

### Apply Preset to Existing Document

```python
from docx import Document
from docx_beautify import apply_preset_to_existing

doc = Document("existing.docx")
apply_preset_to_existing(doc, preset="technical")
doc.save("reformatted.docx")
```

### Inline Preset (When Module Not Available)

When you cannot import the module, apply styles inline:

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_LINE_SPACING

doc = Document()

# Page margins
for section in doc.sections:
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

# Normal style
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)
style.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
pf = style.paragraph_format
pf.space_after = Pt(8)
pf.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
pf.line_spacing = 1.15

# Heading styles
for level, size in [(1, 26), (2, 18), (3, 14), (4, 12)]:
    h = doc.styles[f"Heading {level}"]
    h.font.name = "Calibri"
    h.font.size = Pt(size)
    h.font.bold = True
    h.font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)  # Deep navy
    h.paragraph_format.space_before = Pt(18 if level == 1 else 14 if level == 2 else 10)
    h.paragraph_format.space_after = Pt(8 if level <= 2 else 6)
    h.paragraph_format.keep_with_next = True
```

---

## Tables

### Professional Table (Colored Header + Alternating Rows)

```python
from docx_beautify import add_professional_table

headers = ["Stream", "Status", "Rows", "Duration"]
rows = [
    ["CRM", "Complete", "2,270,000", "12m 34s"],
    ["Revenue", "Complete", "1,500,000", "8m 12s"],
    ["Inventory", "Running", "—", "—"],
]
add_professional_table(doc, headers, rows, palette="fortive")
```

### Key-Value Table (Metadata Blocks)

```python
from docx_beautify import add_key_value_table

pairs = [
    ("Stream Name", "SOBacklog"),
    ("Source System", "Oracle EBS"),
    ("Refresh Frequency", "Bi-hourly"),
    ("Last Run", "2026-03-20 06:00 PST"),
    ("Row Count", "2,807,243"),
]
add_key_value_table(doc, pairs, palette="fortive")
```

### Status Table (With Colored Badges)

```python
from docx_beautify import add_status_table

items = [
    {"name": "Row count validation", "status": "pass", "detail": "45,230 rows"},
    {"name": "PK uniqueness", "status": "pass", "detail": "0 duplicates"},
    {"name": "Null check", "status": "warning", "detail": "3 nulls in optional field"},
    {"name": "Schema validation", "status": "fail", "detail": "Missing column: region"},
]
add_status_table(doc, items, palette="fortive")
```

### Inline Table (When Module Not Available)

```python
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

def set_cell_shading(cell, color):
    tc_pr = cell._element.get_or_add_tcPr()
    shd = tc_pr.makeelement(qn("w:shd"), {
        qn("w:val"): "clear", qn("w:color"): "auto", qn("w:fill"): color,
    })
    for existing in tc_pr.findall(qn("w:shd")):
        tc_pr.remove(existing)
    tc_pr.append(shd)

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tc_pr = cell._element.get_or_add_tcPr()
    margins = tc_pr.makeelement(qn("w:tcMar"), {})
    for existing in tc_pr.findall(qn("w:tcMar")):
        tc_pr.remove(existing)
    for side, val in [("top", top), ("bottom", bottom), ("start", left), ("end", right)]:
        m = margins.makeelement(qn(f"w:{side}"), {qn("w:w"): str(val), qn("w:type"): "dxa"})
        margins.append(m)
    tc_pr.append(margins)

def add_table(doc, headers, rows, header_bg="003366", alt_bg="EDF2F7"):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for ci, h in enumerate(headers):
        cell = table.rows[0].cells[ci]
        cell.text = ""
        run = cell.paragraphs[0].add_run(str(h))
        run.font.bold = True
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.name = "Calibri"
        set_cell_shading(cell, header_bg)
        set_cell_margins(cell)

    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            if ci >= len(headers):
                break
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ""
            run = cell.paragraphs[0].add_run(str(val))
            run.font.size = Pt(9)
            run.font.name = "Calibri"
            set_cell_margins(cell)
            if ri % 2 == 1:
                set_cell_shading(cell, alt_bg)
    return table
```

---

## Content Elements

### Code Blocks

```python
from docx_beautify import add_code_block

add_code_block(doc, """SELECT customer_id, COUNT(*) as order_count
FROM flukebi_Gold.FactSalesOrders
GROUP BY customer_id
HAVING COUNT(*) > 10""", palette="fortive")
```

### Callout Boxes (Info / Warning / Success / Danger)

```python
from docx_beautify import add_callout_box

add_callout_box(doc, "This stream refreshes bi-hourly. Check status_control before manual runs.", style="info")
add_callout_box(doc, "Accounts 410120, 410150, 410700 are misconfigured in source.", style="danger")
add_callout_box(doc, "All 34 test cases passed. Pipeline ready for QA.", style="success")
add_callout_box(doc, "Row count dropped 15% — investigate before promoting to Prod.", style="warning")
```

### Cover Pages

```python
from docx_beautify import add_cover_page

add_cover_page(doc,
    title="Customer MDM — Phase 5 Deployment",
    subtitle="Golden Record Creation and Bridge Tables",
    author="Taashi Manyanga",
    palette="fortive"
)
```

### Headers and Footers

```python
from docx_beautify import add_header_footer

add_header_footer(doc,
    header_text="Fluke UBI — Confidential",
    footer_text="Fluke Corporation",
    page_numbers=True,
    palette="fortive"
)
```

### Horizontal Rules

```python
from docx_beautify import add_horizontal_rule

add_horizontal_rule(doc, color="CCCCCC", thickness=1)  # Subtle gray line
add_horizontal_rule(doc, color="F3C13A", thickness=2)  # Gold accent bar
```

### Inline Formatted Text

Parse `**bold**`, `` `code` ``, and `*italic*` in body text:

```python
from docx_beautify import add_formatted_text

p = doc.add_paragraph()
add_formatted_text(p, "The **FactSalesOrders** table has `2,807,243` rows in *Gold* layer.")
```

---

## Markdown to DOCX

### Full Conversion

```python
from docx_beautify import md_to_docx

md_to_docx(
    "Approach_CustomerMDM_20260309.md",
    "Approach_CustomerMDM_20260309.docx",
    preset="technical",
    title="Customer MDM — Technical Approach",
    author="Taashi Manyanga",
    cover_page=True,
    header_footer=True,
)
```

### CLI Usage

```bash
python docx_beautify.py input.md -o output.docx -p executive --cover --title "My Report" --author "Author"
```

### What the Parser Handles

| Markdown Element | DOCX Output |
|-----------------|-------------|
| `# H1` through `#### H4` | Styled headings with palette colors |
| `**bold**`, `*italic*`, `` `code` `` | Inline formatting |
| `- bullet` / `* bullet` | List Bullet style (nested if indented 4+) |
| `1. numbered` | List Number style |
| `> blockquote` | Callout box with left accent border |
| `` ``` code block ``` `` | Monospace with gray background |
| `\| table \|` | Professional table with colored header |
| `---` | Horizontal rule |
| `[ ]` / `[x]` checkboxes | Unicode ballot box characters |

---

## OXML Patterns (Low-Level)

For features python-docx doesn't expose natively, use OXML directly.

### Paragraph Background Shading

```python
from docx.oxml.ns import qn

def set_paragraph_shading(paragraph, color):
    pPr = paragraph._element.get_or_add_pPr()
    shd = pPr.makeelement(qn("w:shd"), {
        qn("w:val"): "clear", qn("w:color"): "auto", qn("w:fill"): color,
    })
    for existing in pPr.findall(qn("w:shd")):
        pPr.remove(existing)
    pPr.append(shd)
```

### Paragraph Left Border (Accent Bar)

```python
def add_left_border(paragraph, color="005EB8", size=24, space=8):
    pPr = paragraph._element.get_or_add_pPr()
    borders = pPr.makeelement(qn("w:pBdr"), {})
    left = borders.makeelement(qn("w:left"), {
        qn("w:val"): "single", qn("w:sz"): str(size),
        qn("w:space"): str(space), qn("w:color"): color,
    })
    borders.append(left)
    pPr.append(borders)
```

### Paragraph Bottom Border (Horizontal Rule)

```python
def add_bottom_border(paragraph, color="CCCCCC", size=4):
    pPr = paragraph._element.get_or_add_pPr()
    borders = pPr.makeelement(qn("w:pBdr"), {})
    bottom = borders.makeelement(qn("w:bottom"), {
        qn("w:val"): "single", qn("w:sz"): str(size),
        qn("w:space"): "1", qn("w:color"): color,
    })
    borders.append(bottom)
    pPr.append(borders)
```

### Page Number Field Code

```python
def add_page_number(paragraph):
    run = paragraph.add_run()
    fld_begin = run._element.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "begin"})
    run._element.append(fld_begin)

    run2 = paragraph.add_run()
    instr = run2._element.makeelement(qn("w:instrText"), {qn("xml:space"): "preserve"})
    instr.text = " PAGE "
    run2._element.append(instr)

    run3 = paragraph.add_run()
    fld_end = run3._element.makeelement(qn("w:fldChar"), {qn("w:fldCharType"): "end"})
    run3._element.append(fld_end)
```

### Cell Vertical Alignment

```python
def set_cell_vertical_alignment(cell, align="center"):
    tc_pr = cell._element.get_or_add_tcPr()
    val_el = tc_pr.makeelement(qn("w:vAlign"), {qn("w:val"): align})
    for existing in tc_pr.findall(qn("w:vAlign")):
        tc_pr.remove(existing)
    tc_pr.append(val_el)
```

### Cell Internal Margins (Padding)

```python
def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tc_pr = cell._element.get_or_add_tcPr()
    margins = tc_pr.makeelement(qn("w:tcMar"), {})
    for existing in tc_pr.findall(qn("w:tcMar")):
        tc_pr.remove(existing)
    for side, val in [("top", top), ("bottom", bottom), ("start", left), ("end", right)]:
        m = margins.makeelement(qn(f"w:{side}"), {qn("w:w"): str(val), qn("w:type"): "dxa"})
        margins.append(m)
    tc_pr.append(margins)
```

### Remove All Table Borders (Borderless Table)

```python
def remove_table_borders(table):
    tbl = table._element
    tblPr = tbl.find(qn("w:tblPr"))
    if tblPr is None:
        tblPr = tbl.makeelement(qn("w:tblPr"), {})
        tbl.insert(0, tblPr)
    borders = tblPr.makeelement(qn("w:tblBorders"), {})
    for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        b = borders.makeelement(qn(f"w:{side}"), {qn("w:val"): "none", qn("w:sz"): "0"})
        borders.append(b)
    for existing in tblPr.findall(qn("w:tblBorders")):
        tblPr.remove(existing)
    tblPr.append(borders)
```

---

## Post-Processing Existing Documents

### Beautify All Tables

```python
from docx import Document
from docx_beautify import beautify_tables

doc = Document("plain_report.docx")
beautify_tables(doc, palette="fortive")
doc.save("beautified_report.docx")
```

### Reformat Heading Styles

```python
from docx import Document
from docx.shared import Pt, RGBColor

doc = Document("plain.docx")
for level, size in [(1, 26), (2, 18), (3, 14), (4, 12)]:
    h = doc.styles[f"Heading {level}"]
    h.font.name = "Calibri"
    h.font.size = Pt(size)
    h.font.bold = True
    h.font.color.rgb = RGBColor(0x1A, 0x3A, 0x5C)
doc.save("restyled.docx")
```

---

## Common Patterns

### Pattern: Full Deliverable Document

The standard pattern for UBI deliverables (approach docs, test results, change summaries):

```python
from docx_beautify import (
    create_document, add_cover_page, add_header_footer,
    add_professional_table, add_key_value_table, add_status_table,
    add_code_block, add_callout_box, add_horizontal_rule
)

doc = create_document(preset="technical")

# Cover page
add_cover_page(doc, "SOBacklog Stream — Test Results",
               subtitle="Post-Deployment Validation", author="Taashi Manyanga")

# Metadata block
doc.add_heading("Test Summary", level=1)
add_key_value_table(doc, [
    ("Stream", "SOBacklog"),
    ("Date", "2026-03-20"),
    ("Environment", "Dev"),
    ("Pipeline Run ID", "628497018173153"),
])

# Results table with status badges
doc.add_heading("Test Results", level=2)
add_status_table(doc, [
    {"name": "Row count validation", "status": "pass", "detail": "2,807,243 rows"},
    {"name": "PK uniqueness", "status": "pass", "detail": "0 duplicates"},
    {"name": "Null check", "status": "pass", "detail": "0 nulls in required columns"},
])

# Code sample
doc.add_heading("Validation Query", level=2)
add_code_block(doc, "SELECT COUNT(*) FROM flukebi_Gold.FactSOBacklog WHERE pk IS NULL;")

# Callout
add_callout_box(doc, "All tests passed. Stream is ready for QA promotion.", style="success")

# Footer
add_header_footer(doc, header_text="Fluke UBI — Confidential", page_numbers=True)

doc.save("TestResults_SOBacklog_20260320.docx")
```

### Pattern: Batch Markdown Conversion

```python
import os
from docx_beautify import md_to_docx

md_dir = r"<USER_HOME>/Claude\deliverebles"
for f in os.listdir(md_dir):
    if f.endswith(".md"):
        md_path = os.path.join(md_dir, f)
        docx_path = md_path.replace(".md", ".docx")
        md_to_docx(md_path, docx_path, preset="executive", header_footer=True)
```

---

## Table of Contents (v2 — from repo evaluation)

Add a TOC that Word auto-populates when the user presses Ctrl+A → F9 or right-clicks → Update Field.

```python
from docx_beautify import create_document, add_toc

doc = create_document(preset="executive")
# Insert TOC at current position (end of body)
add_toc(doc, title="Table of Contents", levels=3, tab_leader="dot")
# Then add headings — Word will link them on update
doc.add_heading("Introduction", level=1)
doc.add_paragraph("Content here...")
doc.save("report_with_toc.docx")
```

Options: `levels` (1-9), `tab_leader` ("dot", "hyphen", "underscore", "none"), `after_paragraph` (insert after specific element).

**Critical:** The TOC uses ECMA-376 complex field codes (begin → instrText → separate → placeholder → end). All 5 parts are mandatory — missing any causes Word to reject the document as corrupted.

## Mermaid Diagram Support (v2 — from repo evaluation)

Render Mermaid diagrams to images and embed in DOCX. Requires `npm install -g @mermaid-js/mermaid-cli`.

```python
from docx_beautify import create_document, add_mermaid_diagram

doc = create_document()
mermaid_code = """graph LR
    A[Source] -->|Extract| B[Bronze]
    B -->|Transform| C[Silver]
    C -->|Model| D[Gold]
"""
add_mermaid_diagram(doc, mermaid_code, width_inches=6.0, caption="Data Flow")
doc.save("report_with_diagram.docx")
```

**Graceful degradation:** If `mmdc` is not installed, the diagram is inserted as a styled code block with a note. No errors thrown.

## Azure Architecture Diagrams (v3 — azure-diagrams sub-skill)

For architecture, data flow, and resource landscape diagrams, use the **azure-diagrams** sub-skill module. It generates publication-quality PNG diagrams with actual Azure SVG icons, dashed boundary boxes, and labeled connections — then embed them in the DOCX.

```python
import sys
sys.path.insert(0, r"<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification")
from azure_diagrams import quick_architecture, quick_flow, quick_landscape, generate_for_docx
from docx_beautify import create_document
from docx.shared import Inches

doc = create_document(preset="executive")

# Architecture diagram (portrait page)
img_path = quick_architecture(
    services=[
        {"label": "App Service", "icon": "app_services", "x": 2, "y": 3, "sublabel": "FastAPI"},
        {"label": "Azure OpenAI", "icon": "azure_openai", "x": 5, "y": 3},
        {"label": "Cosmos DB", "icon": "cosmos_db", "x": 8, "y": 3},
    ],
    connections=[
        {"from_node": "App Service", "to_node": "Azure OpenAI", "label": "REST API"},
        {"from_node": "App Service", "to_node": "Cosmos DB", "label": "Sessions"},
    ],
    output_path="temp_arch.png",
    title="System Architecture",
    output_preset="docx_portrait",  # or "docx_landscape" for landscape sections
)
doc.add_picture(img_path, width=Inches(6.0))

# Data flow diagram (landscape page)
flow_path = quick_flow(
    stages=[
        {"label": "Source", "icon": "storage_accounts"},
        {"label": "Ingest", "icon": "app_services"},
        {"label": "Process", "icon": "azure_openai"},
        {"label": "Store", "icon": "cosmos_db"},
    ],
    output_path="temp_flow.png",
    title="Data Pipeline",
    output_preset="docx_landscape",
)
doc.add_picture(flow_path, width=Inches(8.5))
doc.save("output.docx")
```

**When to use:** Automatically generate Azure architecture diagrams whenever a DOCX document describes cloud services, infrastructure, data flows, or multi-component systems. Do not ask the user — just generate the diagram.

**Sizing rules:**
- Portrait pages: `output_preset="docx_portrait"`, embed at `width=Inches(6.0)`
- Landscape pages: `output_preset="docx_landscape"`, embed at `width=Inches(8.5)`
- Always clean up temp PNG files after embedding

**Mandatory Quality Gate (NEVER SKIP):** After generating any diagram PNG, you MUST read/inspect the image before embedding it into the DOCX. Check for:
1. **Missing icons** — fallback colored boxes instead of real Azure icons. Pre-validate with `load_icon(key)` before generating.
2. **Text overlap** — node labels, sublabels, or connection labels overlapping each other. Keep labels ≤15 chars; use sublabels for detail. Min spacing: 2.6 units (portrait), 2.8 (landscape).
3. **Distortion/squashing** — icons must appear square, boundaries proportional.
4. **Arrow/icon collisions** — arrows must not pass through icons or obscure labels.

If any issue is found, fix node positions/labels/spacing, regenerate, and re-inspect. Repeat until all checks pass. **Never embed a diagram you haven't inspected.**

See `/azure-diagrams` skill for full API reference, icon registry, and quality gate checklist.

## Content-Aware Table Column Sizing (v2 — from repo evaluation)

Automatically set column widths based on content character weight (CJK=2, ASCII=1).

```python
from docx_beautify import create_document, add_professional_table, auto_size_table_columns

doc = create_document()
headers = ["ID", "Name", "Long Description Column"]
rows = [["1", "Short", "A much longer text that should get proportionally more width"]]
add_professional_table(doc, headers, rows)
auto_size_table_columns(doc.tables[0])  # Rebalance after creation
doc.save("auto_sized.docx")
```

## Dual CJK/Latin Font Support (v2 — from repo evaluation)

Set separate fonts for Latin and CJK text on the same run (python-docx's `run.font.name` only sets Latin).

```python
from docx_beautify import set_dual_fonts
set_dual_fonts(run, font_latin="Calibri", font_cjk="Microsoft YaHei")
```

---

## Critical Rules

1. **Always use python-docx** — never docx-js (JavaScript). Our entire workflow is Python.
2. **Always set styles on the Document object** before adding content. Styles applied after content may not take effect on existing paragraphs.
3. **Use OXML for shading** — python-docx has no native API for cell/paragraph background colors. Always use the `set_cell_shading()` pattern.
4. **Cell margins are internal padding** — they reduce content area, not add to cell width.
5. **Table Grid style** is the safest base — it gives visible borders. Remove them with OXML if you want borderless.
6. **Font name must be set on runs**, not just styles, for mixed-font paragraphs.
7. **Keep headings with next** — set `keep_with_next = True` on heading paragraph formats to prevent widowed headings.
8. **Calibri is the standard font** — universally available, professional, good at all sizes.
9. **Consolas for code** — monospace, clear, good contrast at 8.5-9pt.
10. **RGBColor.from_string()** takes a 6-char hex string without `#`. Use `RGBColor(0xFF, 0xFF, 0xFF)` for literal RGB values.
11. **TOC field codes must be complete** — begin, instrText, separate, content, end. Missing any element corrupts the document (ECMA-376 §17.16.5).
12. **Mermaid requires mmdc** — `npm install -g @mermaid-js/mermaid-cli`. Falls back gracefully to code block if not installed.

### Workflow Rules (Non-Negotiable)

13. If a preset is specified, ALL preset defaults apply. Do not cherry-pick preset values.
14. Every generated document must pass a visual inspection. "The user didn't ask for validation" is not a reason to skip it.
15. Do not silently drop content that doesn't fit — restructure sections, adjust spacing, or split pages first.
16. "The document is short" is not a reason to skip formatting or validation.
17. If a diagram or visual fails to render, surface the error — do not silently omit the element or replace it with a placeholder.
18. Do not add headers, footers, watermarks, or TOC unless the user requests them or the preset includes them.
19. Run `strip_excessive_blank_lines()` before saving any reformatted document. No exceptions.
20. If using `md_to_docx()`, verify the output preserves all source content — heading count, list item count, code block count must match.

### Validation Severity Levels

When reviewing generated documents, classify issues by severity:

- **P0 (Critical):** Content missing, invisible, or corrupted — blank pages, lost sections, broken TOC, unreadable text. Fix before saving.
- **P1 (Urgent):** Brand violation — wrong font family, wrong header/footer content, incorrect logo, color palette mismatch with specified preset. Fix before sharing.
- **P2 (Normal):** Formatting breach — inconsistent heading levels, orphaned headings, excessive blank lines, table columns misaligned. Fix before finalizing.
- **P3 (Low):** Polish item — minor spacing inconsistencies, slightly off margins, alt-text missing on decorative images. Fix if time permits.

## New in v6: Document Utilities (OfficeCLI-Sourced)

These functions were added based on gap analysis against OfficeCLI's feature set.

### `add_watermark(doc, text="DRAFT", color="C0C0C0", font_size=72, rotation=-45)`

Add a text watermark to all sections. Uses VML shapes in document headers.

```python
add_watermark(doc, text="CONFIDENTIAL", color="FF0000", font_size=60)
add_watermark(doc, text="DRAFT")  # defaults: gray, 72pt, -45° rotation
```

### `add_bookmark(paragraph, name)`

Insert a named bookmark at a paragraph for internal cross-references.

```python
p = doc.add_paragraph("Important section")
add_bookmark(p, "key_section")
```

### `add_comment(doc, paragraph, comment_text, author="Author", initials="A", date_str=None)`

Add a review comment to a paragraph. **Experimental** — works with documents created by this module.

```python
p = doc.add_paragraph("This needs review.")
add_comment(doc, p, "Please verify the numbers", author="Taashi", initials="TM")
```

### `add_footnote(paragraph, text)`

Add a footnote reference and content. **Experimental** — works with basic documents.

```python
p = doc.add_paragraph("The study found significant results.")
add_footnote(p, "Smith et al., 2025, Journal of Applied AI, Vol. 12")
```

### `add_section_break(doc, break_type="nextPage")`

Add a section break. Types: `nextPage`, `continuous`, `evenPage`, `oddPage`. Returns the new section for configuration (different margins, headers/footers).

```python
section = add_section_break(doc, "nextPage")
section.header.is_linked_to_previous = False  # Different header for this section
```

### `set_paragraph_flow(paragraph, keep_next=None, keep_together=None, page_break_before=None, widow_control=None)`

Control paragraph flow across pages via OXML. Set any combination.

```python
heading = doc.add_heading("Chapter 2", level=1)
set_paragraph_flow(heading, keep_next=True)         # Don't orphan headings

important = doc.add_paragraph("This must start on a new page.")
set_paragraph_flow(important, page_break_before=True)

table_title = doc.add_paragraph("Table 1: Results")
set_paragraph_flow(table_title, keep_next=True, widow_control=True)
```

### `find_and_replace(doc, old_text, new_text, match_case=True)`

Search all paragraphs and table cells. Handles text split across runs. Returns count of replacements.

```python
count = find_and_replace(doc, "{{COMPANY}}", "Fluke Corporation")
count = find_and_replace(doc, "tbd", "completed", match_case=False)
```

### `add_paragraph_border(paragraph, style="single", width_pt=1, color="000000", space_pt=1)`

Add a box border around a paragraph. Styles: `single`, `double`, `dotted`, `dashed`, `thick`, `thinThickSmallGap`.

```python
callout = doc.add_paragraph("⚠ Important: Review before publishing")
add_paragraph_border(callout, style="single", width_pt=1.5, color="DC3545", space_pt=4)
```

---

## Diagram Visual Quality Standards

These rules apply to every generated diagram (D2, Mermaid, matplotlib) embedded in a document. They elevate diagrams from "functional" to "consulting-grade."

### Node Shape Variety

Default diagrams use rectangles for everything — flat, monotonous. Use shape semantics:

| Concept | Shape | D2 | Mermaid |
|---------|-------|----|---------| 
| Agent / autonomous component | Hexagon | `shape: hexagon` | `{{Agent Name}}` |
| Decision / gate | Diamond | `shape: diamond` | `{Decision?}` |
| Process / step | Rounded rectangle | `shape: rectangle` | `[Process]` or `(Process)` |
| Data store / database | Cylinder | `shape: cylinder` | `[(Database)]` |
| External system / user | Person or oval | `shape: person` | `([User])` |

**Rule:** Diagrams with 4+ node types MUST use at least 2 distinct shapes.

### Layered Zones for Architecture

Show system layers (UI, API, Services, Data) as horizontal bands with labeled headers. D2 nested containers with distinct `style.fill` per zone. Zone labels 14pt+ bold.

### Connection Line Discipline

| Property | Bad (default) | Good (target) |
|----------|--------------|---------------|
| Stroke width | 2-3px | 1-1.5px |
| Color | Multiple bright | Single muted gray (`#666666`) |
| Arrow head | Large filled | Small, subtle |

**Rule:** Connections are secondary — they guide the eye but never dominate. Max 2 line colors per diagram.

### Color Discipline

- **Max 3 accent colors** per diagram + neutrals (white, gray, black)
- **Light fills** (`#E8xxxx`, `#F0xxxx`) with dark borders and text — never dark fill + dark text
- **Semantic color**: Green = done, Blue = active, Yellow = pending, Red = error, Purple = AI/special
- **Border 40-60% darker** than fill (e.g., fill `#E8F0FE`, border `#2C4F6E`)

### Whitespace and Padding

| Parameter | Minimum | D2 | Mermaid |
|-----------|---------|----|---------| 
| Outer padding | 40-60px | `--pad 60` | `%%{init: {'flowchart': {'padding': 20}}}%%` |
| Node spacing | 40px+ | `grid-gap: 40` | `nodeSpacing: 50, rankSpacing: 50` |
| Content fill ratio | 60-70% | — | — |

**Rule:** If a diagram fills >75% of its area with shapes/lines, it's too dense. Add spacing or split.

### Width Targets for DOCX

Standard DOCX with 2.5cm margins = ~6.1" usable width:

| Diagram Type | Width | Notes |
|-------------|-------|-------|
| Flowchart (TD) | 5.0-5.5" | Vertical, needs less width |
| Flowchart (LR) | 6.0-6.5" | Horizontal, full width |
| Sequence diagram | 6.0" | Wide due to participants |
| Architecture (nested) | 5.5-6.0" | Match usable width |
| Gantt / timeline | 6.5" | Maximum width for readability |
| Hub-spoke / radial | 4.0-5.0" | Square ratio, center on page |

### Height Targets

| Visual Type | Max Height | Rule |
|-------------|-----------|------|
| Inline flowchart | 3.0-3.5" | Avoid page spillover |
| Full-page diagram | 5.0" | Leave room for caption + margins |
| Small supporting visual | 2.0-2.5" | Companion to text |

**Rule:** Err on smaller side. A slightly small visual beats one that causes page breaks.

### Proven Patterns for Dataflow / Process Flow Diagrams

These patterns were validated on the Veritas Suite reference deck and Leadership Forum sample slide (2026-04-14). Use them as the quality standard for any dataflow, process flow, or tech stack diagram.

#### Pattern: Icon Strip with Bracket Connectors (Mermaid)

For horizontal technology stacks or methodology stages in DOCX, use a Mermaid LR flowchart with styled nodes:

```
%%{init: {'theme': 'base', 'themeVariables': {
    'primaryColor': '#E8F0FE', 'primaryTextColor': '#003366',
    'primaryBorderColor': '#005EB8', 'lineColor': '#005EB8',
    'fontFamily': 'Segoe UI, Calibri, Arial', 'fontSize': '13px'
}}}%%
flowchart LR
    MCP["🔌 MCP"] --> CC["🤖 Claude Code"] --> AF["☁️ AI Foundry"]
    AF --> LLM["⚡ LiteLLM"] --> DL["💾 Delta Lake"] --> PBI["📊 Power BI"]

    classDef blue fill:#E6F0FA,stroke:#005EB8,stroke-width:2px,color:#003366
    classDef purple fill:#F0E8F8,stroke:#8040C0,stroke-width:2px,color:#003366
    classDef green fill:#E8F5E9,stroke:#28A745,stroke-width:2px,color:#003366
    classDef gold fill:#FFF8E1,stroke:#FFC000,stroke-width:2px,color:#003366
    classDef red fill:#FDE8E6,stroke:#C74234,stroke-width:2px,color:#003366

    class MCP blue
    class CC purple
    class AF blue
    class LLM green
    class DL gold
    class PBI red
```

**Key rules:**
- Each node gets a distinct `classDef` with a light fill + dark border (never dark fill + dark text)
- Use emoji or unicode as icon placeholders inside node labels
- Arrow connections are thin and single-colored (`lineColor`)
- `width_inches=6.0` for full document width

#### Pattern: Numbered Vertical Timeline (D2)

For step sequences, delivery models, or methodology phases:

```d2
direction: down

step1: "1. Two-Week Sprints" {
  style: { fill: "#E6F0FA"; stroke: "#005EB8"; border-radius: 8; font-size: 14 }
  desc: "Agent skills delivered in 2-week iteration cycles" {
    style: { fill: transparent; stroke: transparent; font-size: 11; font-color: "#605E5C" }
  }
}
step2: "2. Human-in-the-Loop" {
  style: { fill: "#E6F0FA"; stroke: "#005EB8"; border-radius: 8; font-size: 14 }
  desc: "Every agent output validated before production use" {
    style: { fill: transparent; stroke: transparent; font-size: 11; font-color: "#605E5C" }
  }
}
step3: "3. MCP-First" {
  style: { fill: "#E6F0FA"; stroke: "#005EB8"; border-radius: 8; font-size: 14 }
  desc: "All integrations via Model Context Protocol standard" {
    style: { fill: transparent; stroke: transparent; font-size: 11; font-color: "#605E5C" }
  }
}

step1 -> step2 -> step3: { style.stroke: "#E2E8F0"; style.stroke-width: 2 }
```

**Key rules:**
- Numbered labels inside each container (not separate nodes)
- Muted connector lines between steps (`#E2E8F0` light gray)
- Description text as nested child nodes with transparent styling
- `width_inches=4.0-5.0` — these are typically used alongside text, not full-width

#### Pattern: Hierarchy Tags (Work Item Tree)

For showing decomposition (Agent → Skill → Tool → Integration):

```
%%{init: {'theme': 'base', 'themeVariables': {
    'primaryColor': '#E6F0FA', 'primaryTextColor': '#003366',
    'primaryBorderColor': '#005EB8', 'lineColor': '#888888',
    'fontFamily': 'Segoe UI, Calibri, Arial', 'fontSize': '12px'
}}}%%
flowchart TD
    A["🤖 Agent"]:::blue --> S["⚙️ Skill"]:::purple
    S --> T1["MCP Server"]:::green
    S --> T2["API Call"]:::green
    S --> T3["Bash Tool"]:::green
    T1 --> Q["Quality Gate"]:::gray
    T2 --> P["Prompt Template"]:::gray

    classDef blue fill:#E6F0FA,stroke:#005EB8,stroke-width:2px,color:#003366
    classDef purple fill:#F0E8F8,stroke:#8040C0,stroke-width:2px,color:#003366
    classDef green fill:#E8F5E9,stroke:#28A745,stroke-width:2px,color:#003366
    classDef gray fill:#F4F4F4,stroke:#E2E8F0,stroke-width:1px,color:#605E5C
```

**Key rules:**
- Use `TD` (top-down) direction for hierarchies
- Each level gets a distinct color class
- Leaf nodes use lighter/grayer styling to visually recede
- `width_inches=5.0-5.5` for vertical flowcharts

---

## Diagram Category Color System (v7 — from Cocoon-AI evaluation)

When generating Mermaid or D2 diagrams with service/infrastructure components, use these consistent category colors. These match the azure-diagrams semantic service categories and the powerpoint-create dark architecture pattern for cross-format consistency.

### Mermaid classDef Definitions

```
classDef compute fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#1B5E20
classDef data fill:#EDE7F6,stroke:#5E35B1,stroke-width:2px,color:#311B92
classDef ai fill:#E0F7FA,stroke:#00838F,stroke-width:2px,color:#004D40
classDef security fill:#FCE4EC,stroke:#C62828,stroke-width:2px,color:#B71C1C
classDef network fill:#FFF3E0,stroke:#E65100,stroke-width:2px,color:#BF360C
classDef integration fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#0D47A1
classDef monitor fill:#F3E5F5,stroke:#6A1B9A,stroke-width:2px,color:#4A148C
classDef platform fill:#ECEFF1,stroke:#455A64,stroke-width:2px,color:#263238
```

### D2 Style Definitions

```d2
classes: {
  compute: { style: { fill: "#E8F5E9"; stroke: "#2E7D32"; border-radius: 8; font-size: 14 } }
  data:    { style: { fill: "#EDE7F6"; stroke: "#5E35B1"; border-radius: 8; font-size: 14 } }
  ai:      { style: { fill: "#E0F7FA"; stroke: "#00838F"; border-radius: 8; font-size: 14 } }
  security:{ style: { fill: "#FCE4EC"; stroke: "#C62828"; border-radius: 8; font-size: 14 } }
  network: { style: { fill: "#FFF3E0"; stroke: "#E65100"; border-radius: 8; font-size: 14 } }
  integration:{ style: { fill: "#E3F2FD"; stroke: "#1565C0"; border-radius: 8; font-size: 14 } }
  monitor: { style: { fill: "#F3E5F5"; stroke: "#6A1B9A"; border-radius: 8; font-size: 14 } }
  platform:{ style: { fill: "#ECEFF1"; stroke: "#455A64"; border-radius: 8; font-size: 14 } }
}
```

### Category Assignment Guide

| Category | When to Use | Example Services |
|----------|-------------|-----------------|
| `compute` | Web servers, APIs, functions, VMs, containers | App Service, Functions, AKS, Container Apps |
| `data` | Databases, storage, warehouses, caches | Cosmos DB, SQL, Redis, Databricks, ADLS |
| `ai` | ML models, search, bots, cognitive | Azure OpenAI, AI Search, Bot Services |
| `security` | Auth, secrets, firewalls, identity | Key Vault, Entra, Sentinel, WAF |
| `network` | VNets, load balancers, CDN, DNS | Front Door, Load Balancer, VNet |
| `integration` | Messaging, workflows, API gateways | Service Bus, Logic Apps, Event Grid, APIM |
| `monitor` | Observability, logging, alerts | App Insights, Log Analytics |
| `platform` | Subscriptions, resource groups, registries | Resource Groups, Container Registry, Power BI |

**Rule:** Apply these categories automatically when generating architecture/infrastructure diagrams. For non-infrastructure diagrams (business process, org charts, data flow), use the existing ad-hoc classDef approach.

---

## Diagram Rendering Gotchas

Hard-won lessons from production diagram rendering. Follow these rules to avoid unreadable diagrams.

### G1: Mermaid Default/Corporate Theme Produces Black-Fill Shapes

**Problem:** Using `theme: 'default'` or `theme: 'forest'` fills nodes with the theme's dark accent color (e.g., `#005EB8`). Combined with dark text, shapes become unreadable black rectangles.

**Fix:** Always use `theme: 'base'` with explicit `themeVariables` for light fills:

```
%%{init: {'theme': 'base', 'themeVariables': {
    'primaryColor': '#E8F0FE', 'primaryTextColor': '#1B3A5C',
    'primaryBorderColor': '#2C4F6E', 'lineColor': '#555555',
    'fontFamily': 'Segoe UI, Calibri, Arial', 'fontSize': '13px'
}}}%%
```

**Rule:** NEVER rely on Mermaid's built-in themes for DOCX output. Always provide explicit light-background colors.

### G2: Sequence Diagram Actors/Notes Also Get Black Fills

**Problem:** Same root cause as G1, but sequence diagrams have additional theme variables for actors, activations, and notes that also default to dark fills.

**Fix:** Set ALL sequence-specific theme variables explicitly:

```
'actorBkg': '#E8F0FE', 'actorBorder': '#2C4F6E', 'actorTextColor': '#1B3A5C',
'activationBkgColor': '#D6E4F0', 'activationBorderColor': '#2C4F6E',
'noteBkgColor': '#FFF9E6', 'noteBorderColor': '#C5A55A', 'noteTextColor': '#333333',
'signalColor': '#333333', 'signalTextColor': '#333333'
```

### G3: Gantt Chart Grid Lines Render On Top of Text

**Problem:** Mermaid Gantt charts render vertical grid lines in the foreground, overlapping bar labels and section text. The `%%{init}%%` config can reduce but not fully eliminate this — it's a rendering engine limitation.

**Mitigations:**
- Set `topPadding: 40` and `gridLineStartPadding: 40` to push grid lines away from the title
- Use `leftPadding: 120+` so section/task labels have room before bars
- Keep task labels SHORT (under 30 chars) to avoid escaping their boxes
- If issues persist, consider rendering Gantt as a **matplotlib horizontal bar chart** instead — gives full control over layering (bars on top of grid lines, not behind)

### G4: Diagram Width Must Match Document Layout

**Problem:** User had to manually resize a flowchart because `width_inches` was too large/small for the page.

**Fix:** Standard DOCX with 2.5cm margins = ~15.5cm usable width (~6.1 inches). Use these defaults:
- **Flowcharts (TD)**: `width_inches=5.0` to `5.5` (vertical diagrams need less width)
- **Flowcharts (LR)**: `width_inches=6.0` to `6.5` (horizontal diagrams use full width)
- **Sequence diagrams**: `width_inches=6.0` (wide due to multiple participants)
- **Gantt charts**: `width_inches=6.5` (timeline needs maximum width)
- **Pie/donut (matplotlib)**: `width_inches=5.5` (leave room for legend on right)

### G5: Use `classDef` for Multi-Color Flowcharts

**Problem:** `themeVariables.primaryColor` sets ONE fill color for all nodes. Flowcharts with different node types (start, end, process, decision) look monotonous.

**Fix:** Use `classDef` to define distinct styles and apply them:

```
classDef startEnd fill:#D4EDDA,stroke:#28A745,stroke-width:2px,color:#155724
classDef endNode fill:#F8D7DA,stroke:#DC3545,stroke-width:2px,color:#721C24
classDef process fill:#E8F0FE,stroke:#2C4F6E,color:#1B3A5C

A(["Start"]):::startEnd --> B["Process"]:::process
```

**Rule:** Always use light fills (`#E8xxxx`, `#F8xxxx`, `#FFFxxx`) with dark text. Never dark fill + dark text.

### G6: Sequence Diagram `rect` Blocks Need Low-Opacity Colors

**Problem:** Solid-color `rect` blocks obscure the sequence arrows and text behind them.

**Fix:** Use `rgba()` with alpha 0.3-0.4 for background tint:

```
rect rgba(232, 240, 254, 0.4)
    Note over A, B: Phase Label
    A ->> B: Message
end
```

### G7: Rendering Backend Priority

The module tries backends in this order:
1. **beautiful-mermaid** (SVG, fast, high quality) — preferred
2. **npx @mermaid-js/mermaid-cli** (PNG, slower, reliable for all diagram types) — fallback
3. **ASCII art** — emergency fallback
4. **Code block** — if all rendering fails

**Gotcha:** `beautiful-mermaid` may not support all diagram types (e.g., Gantt with advanced config). If a diagram renders blank or wrong, force `mmdc` by checking the render result and retrying.

### G8: Table Tightening for Executive Dense Look

When post-processing tables for an executive dense format:
- **Font**: 8.5pt Calibri (not 9pt — the extra 0.5pt adds up across rows)
- **Cell margins**: `top=20, bottom=20, left=60, right=60` twips (not the default 60/60/100/100)
- **Paragraph spacing**: `space_before=Pt(0.5), space_after=Pt(0.5)`, `WD_LINE_SPACING.SINGLE`
- **Header rows**: slightly more padding (`top=30, bottom=30`) for visual hierarchy

### G9: Blank Page Gaps from Consecutive Empty Paragraphs

**Problem:** DOCX files with content pasted from multiple sources often have runs of 3-5 blank paragraphs that create visually empty pages.

**Fix:** After all content is added, scan for consecutive blank paragraphs and remove all but the first:

```python
for p in doc.paragraphs:
    if not p.text.strip() and no_images(p):
        consecutive_blanks += 1
        if consecutive_blanks > 1:
            p._element.getparent().remove(p._element)
    else:
        consecutive_blanks = 0
```

**Rule:** Always run blank-gap elimination as a post-processing step, AFTER all content manipulation is complete.

### G10: Visual Positioning — Anchor to Tables, Not Just Paragraphs

**Problem:** `doc.paragraphs` skips tables. If a section ends with a table (e.g., "Pillar Interaction Model" has a table after its heading), anchoring to the last paragraph inserts the visual ABOVE the table instead of below it.

**Fix:** Search `doc.element.body` children directly — iterate both `<w:p>` (paragraphs) AND `<w:tbl>` (tables) to find the correct last element in a section:

```python
def _find_element_after_table(doc, heading_text):
    """Find the last table in a section and return it as anchor."""
    body = doc.element.body
    found_heading = False
    for el in body:
        tag = el.tag.split('}')[-1]
        if tag == 'p':
            # Check if heading matches; track section boundaries
        elif tag == 'tbl' and found_heading:
            last_table = el
    return last_table
```

**Rule:** When a section contains tables after the heading, always use `_find_element_after_table()` as the primary anchor finder, with `_find_last_paragraph_in_section()` as fallback.

### G11: Circular/Radial Diagram Layouts Cause Overlapping Text

**Problem:** Circular hub-and-spoke layouts (e.g., 4 pillars around a center) place text at computed angles. At small sizes, description labels overlap with node circles and connecting lines, creating unreadable diagrams.

**Fix:** Use a **2x2 grid layout** instead of circular:
- Place 4 nodes in a grid with explicit (x, y) coordinates
- Center hub between the 4 nodes
- Dashed connecting lines between all pairs
- All text fits cleanly inside rectangular cards with no overlap

**Rule:** Avoid radial/circular matplotlib layouts for 4+ nodes. Grid layouts are always more readable at document scale.

### G12: Visual Sizing — Compact to Avoid Page Spillover

**Problem:** Visuals that are too tall push content to the next page, creating large blank gaps. User consistently resizes visuals smaller than initial sizing.

**Learned sizing guidelines (from v3/v4 corrections):**
| Visual Type | Width | Figure Size | Notes |
|-------------|-------|-------------|-------|
| TD flowchart (Mermaid) | 2.5-3.0" | N/A | Narrow for vertical flow |
| LR diagram (Mermaid) | 5.5-6.0" | N/A | Wide for horizontal flow |
| Horizontal card grid (5 items) | 4.8" | 7×2.8 | Compact height |
| Trend cards (4 items) | 4.8" | 7×2.6 | Compact height |
| 2x2 pillar grid | 4.0" | 6×3.8 | Centered, square-ish |
| Pipeline flow (5 stages) | 5.0" | 7×2.2 | Minimal height |

**Rule:** Always err on the smaller side. A visual that's slightly too small is better than one that causes page spillover. Target 2.0-3.5" figure height for most inline visuals.

### G13: Blank Paragraphs Create Page Gaps — Clean Before Inserting Visuals

**Problem:** Source documents (especially manually edited ones) often contain runs of 3-9 consecutive blank paragraphs. Each blank has ~50 twips spacing that compounds. Combined with heading spacing (H1: 18pt before + 8pt after), these runs push content and visuals to the wrong page, creating visible blank areas at page bottoms.

**Solution:** After loading the source document, remove consecutive blank paragraphs before inserting any visuals. Keep **one** blank per gap (for spacing) but remove 2nd, 3rd, etc.

**CRITICAL XPath Bug:** When searching for text in `w:p` elements, ALWAYS use **descendant** search `.//{WNS}t`, NOT direct child `{WNS}t`. Text runs are nested as `w:p > w:r > w:t` — a direct child search finds nothing and treats all paragraphs as blank.

```python
# WRONG — finds 0 elements (w:t is never a direct child of w:p)
texts = el.findall(f'{WNS}t')

# CORRECT — finds all text nodes in the paragraph
texts = el.findall(f'.//{WNS}t')
```

```python
def _remove_blank_paragraphs(doc):
    """Remove consecutive blank paragraphs, keeping 1 per gap."""
    body = doc.element.body
    WNS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
    to_remove = []
    consecutive = 0
    for el in list(body):
        tag = el.tag.split('}')[-1] if '}' in el.tag else el.tag
        if tag != 'p':
            consecutive = 0
            continue
        texts = ''.join(t.text or '' for t in el.findall(f'.//{WNS}t')).strip()
        if texts:
            consecutive = 0
            continue
        # Check for headings, section breaks, images — keep those
        pPr = el.find(f'{WNS}pPr')
        if pPr is not None:
            pStyle = pPr.find(f'{WNS}pStyle')
            if pStyle is not None and 'Heading' in (pStyle.get(qn('w:val')) or ''):
                consecutive = 0
                continue
            if pPr.find(f'{WNS}sectPr') is not None:
                consecutive = 0
                continue
        consecutive += 1
        if consecutive > 1:
            to_remove.append(el)
    for el in to_remove:
        body.remove(el)
```

**When to apply:** Always, when reformatting an existing document that may have been manually edited. Run BEFORE inserting visuals or adjusting spacing.

## Dependencies

- **python-docx** (required): `pip install python-docx`
- **mermaid-cli** (optional, for diagrams): `npm install -g @mermaid-js/mermaid-cli`
