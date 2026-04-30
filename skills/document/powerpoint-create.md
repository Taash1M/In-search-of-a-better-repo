---
name: powerpoint-create
description: "Use this skill any time a .pptx file is involved — creating slide decks, pitch decks, or presentations; reading, parsing, or extracting text from .pptx files; editing, modifying, or updating existing presentations; combining or splitting slide files; working with templates, layouts, speaker notes, or comments. Trigger whenever the user mentions 'deck', 'slides', 'presentation', 'PowerPoint', or references a .pptx filename."
---

# PowerPoint Creation & Beautification Skill

## Decision Tree

```
What do you need?
├─ Read/extract content from .pptx → markitdown (no creation needed)
├─ Edit an existing presentation → Unpack XML → Edit → Repack (§Editing Existing)
├─ Create a new deck from scratch
│   ├─ Node.js available → PptxGenJS (§PptxGenJS Primary)
│   └─ Python only → python-pptx (§python-pptx Alternative)
├─ Add architecture/data flow diagrams → azure-diagrams sub-skill (generate_for_pptx)
├─ Dark-themed technical slide → Pattern 13: Dark Architecture Diagram
├─ Design exploration (multiple concepts) → 3 divergent layout proofs (§Design Exploration)
└─ QA an existing deck → 3-stage workflow: content → programmatic layout → visual (§QA Workflow)
```

## Quick Reference

| Task | Tool | Guide |
|------|------|-------|
| Read/analyze content | `python -m markitdown presentation.pptx` | [Reading Content](#reading-content) |
| Edit existing presentation | Unpack → Edit XML → Pack | [Editing Existing Presentations](#editing-existing-presentations) |
| Create from scratch (primary) | PptxGenJS (Node.js) | [PptxGenJS](#pptxgenjs-primary) |
| Create from scratch (alternative) | python-pptx (Python) | [python-pptx](#python-pptx-alternative) |
| Visual QA | soffice + pdftoppm + subagent | [QA Workflow](#qa-workflow) |

---

## Creation Engines

### PptxGenJS (Primary)

JavaScript/Node.js library. Produces clean .pptx files with a straightforward API.

#### Setup

```javascript
const pptxgen = require("pptxgenjs");

let pres = new pptxgen();
pres.layout = "LAYOUT_16x9";  // 10" x 5.625"
pres.author = "Your Name";
pres.title = "Presentation Title";

let slide = pres.addSlide();
slide.addText("Hello World!", { x: 0.5, y: 0.5, fontSize: 36, color: "363636" });

pres.writeFile({ fileName: "output.pptx" });
```

**Layout dimensions (inches):**
- `LAYOUT_16x9`: 10" x 5.625" (default, recommended)
- `LAYOUT_16x10`: 10" x 6.25"
- `LAYOUT_4x3`: 10" x 7.5"
- `LAYOUT_WIDE`: 13.3" x 7.5"

#### Text & Formatting

```javascript
// Basic text box
slide.addText("Title Text", {
  x: 0.5, y: 0.5, w: 9, h: 1,
  fontSize: 36, fontFace: "Arial", color: "1E2761",
  bold: true, align: "left", valign: "middle"
});

// Character spacing (use charSpacing, NOT letterSpacing)
slide.addText("SPACED HEADING", { x: 0.5, y: 0.5, w: 9, h: 0.5, charSpacing: 6 });

// Rich text arrays (mixed formatting in one text box)
slide.addText([
  { text: "Bold part ", options: { bold: true, fontSize: 16 } },
  { text: "normal part ", options: { fontSize: 16 } },
  { text: "colored part", options: { color: "0078D4", fontSize: 16 } }
], { x: 0.5, y: 2, w: 9, h: 1 });

// Multi-line text (requires breakLine: true between lines)
slide.addText([
  { text: "Line 1", options: { breakLine: true } },
  { text: "Line 2", options: { breakLine: true } },
  { text: "Line 3" }
], { x: 0.5, y: 3, w: 9, h: 2 });

// Text box margin (internal padding) — set to 0 for precise alignment
slide.addText("Aligned Title", {
  x: 0.5, y: 0.3, w: 9, h: 0.6,
  margin: 0  // Required when aligning text edge with shapes/icons
});
```

#### Lists & Bullets

```javascript
// Bulleted list
slide.addText([
  { text: "First point", options: { bullet: true, breakLine: true } },
  { text: "Second point", options: { bullet: true, breakLine: true } },
  { text: "Third point", options: { bullet: true } }
], { x: 0.5, y: 1, w: 8, h: 3, fontSize: 16 });

// Sub-items (indented)
{ text: "Sub-item", options: { bullet: true, indentLevel: 1, breakLine: true } }

// Numbered list
{ text: "Step one", options: { bullet: { type: "number" }, breakLine: true } }
```

#### Shapes

```javascript
// Rectangle
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.5, w: 3, h: 2,
  fill: { color: "1E2761" }
});

// Rounded rectangle
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 0.5, y: 0.5, w: 3, h: 2,
  fill: { color: "FFFFFF" }, rectRadius: 0.1
});

// Line
slide.addShape(pres.shapes.LINE, {
  x: 0.5, y: 3, w: 9, h: 0,
  line: { color: "E2E8F0", width: 1 }
});

// With shadow (factory function to avoid mutation bug)
const makeShadow = () => ({
  type: "outer", color: "000000", blur: 6, offset: 2, angle: 135, opacity: 0.15
});
slide.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: "FFFFFF" }, shadow: makeShadow()
});

// With transparency
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 10, h: 5.625,
  fill: { color: "000000", transparency: 40 }
});
```

**Shadow properties:**

| Property | Type | Range | Notes |
|----------|------|-------|-------|
| `type` | string | `"outer"`, `"inner"` | |
| `color` | string | 6-char hex | No `#` prefix |
| `blur` | number | 0-100 pt | |
| `offset` | number | 0-200 pt | Must be non-negative |
| `angle` | number | 0-359 | 135 = bottom-right, 270 = upward |
| `opacity` | number | 0.0-1.0 | Never encode in color string |

#### Images

```javascript
// From file
slide.addImage({ path: "images/photo.png", x: 1, y: 1, w: 5, h: 3 });

// From base64 (faster, no file I/O)
slide.addImage({ data: "image/png;base64,iVBORw0KGgo...", x: 1, y: 1, w: 5, h: 3 });

// Circular crop
slide.addImage({ path: "headshot.jpg", x: 1, y: 1, w: 1.5, h: 1.5, rounding: true });

// Sizing modes — USE "contain" FOR ALL GENERATED DIAGRAMS
{ sizing: { type: "contain", w: 4, h: 3 } }  // Fit inside, preserve ratio (PREFERRED)
{ sizing: { type: "cover", w: 4, h: 3 } }    // Fill area, may crop

// MANDATORY for diagrams/charts/screenshots — prevents stretching:
slide.addImage({
  path: "diagram.png", x: 0.3, y: 1.1, w: 12.7, h: 6,
  sizing: { type: "contain", w: 12.7, h: 6 }
});
```

#### Icons (react-icons)

```javascript
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const { FaCheckCircle } = require("react-icons/fa");

function renderIconSvg(IconComponent, color = "#000000", size = 256) {
  return ReactDOMServer.renderToStaticMarkup(
    React.createElement(IconComponent, { color, size: String(size) })
  );
}

async function iconToBase64Png(IconComponent, color, size = 256) {
  const svg = renderIconSvg(IconComponent, color, size);
  const pngBuffer = await sharp(Buffer.from(svg)).png().toBuffer();
  return "image/png;base64," + pngBuffer.toString("base64");
}

// Usage
const iconData = await iconToBase64Png(FaCheckCircle, "#0078D4", 256);
slide.addImage({ data: iconData, x: 1, y: 1, w: 0.4, h: 0.4 });
```

**Icon libraries:** `react-icons/fa` (Font Awesome), `react-icons/md` (Material), `react-icons/hi` (Heroicons), `react-icons/bi` (Bootstrap)

#### Slide Backgrounds

```javascript
slide.background = { color: "1E2761" };                    // Solid color
slide.background = { color: "000000", transparency: 50 };  // With transparency
slide.background = { path: "images/bg.jpg" };              // Image
slide.background = { data: "image/png;base64,..." };       // Base64 image
```

#### Tables

```javascript
// Simple table
slide.addTable([
  [
    { text: "Header 1", options: { fill: { color: "1E2761" }, color: "FFFFFF", bold: true } },
    { text: "Header 2", options: { fill: { color: "1E2761" }, color: "FFFFFF", bold: true } }
  ],
  ["Cell 1", "Cell 2"],
  ["Cell 3", "Cell 4"]
], {
  x: 0.5, y: 1, w: 9, colW: [4.5, 4.5],
  border: { pt: 0.5, color: "E2E8F0" },
  fontSize: 12, fontFace: "Calibri"
});
```

#### Charts

```javascript
// Column chart (modern styling)
slide.addChart(pres.charts.BAR, [{
  name: "Revenue", labels: ["Q1", "Q2", "Q3", "Q4"], values: [4500, 5500, 6200, 7100]
}], {
  x: 0.5, y: 1, w: 6, h: 3.5, barDir: "col",
  chartColors: ["0078D4"],
  chartArea: { fill: { color: "FFFFFF" }, roundedCorners: true },
  catAxisLabelColor: "64748B", valAxisLabelColor: "64748B",
  valGridLine: { color: "E2E8F0", size: 0.5 },
  catGridLine: { style: "none" },
  showValue: true, dataLabelPosition: "outEnd", dataLabelColor: "1E293B",
  showLegend: false
});

// Line chart
slide.addChart(pres.charts.LINE, [{
  name: "Trend", labels: ["Jan", "Feb", "Mar", "Apr"], values: [32, 35, 42, 48]
}], {
  x: 0.5, y: 1, w: 6, h: 3.5,
  lineSize: 3, lineSmooth: true,
  chartColors: ["0078D4"]
});

// Pie/doughnut chart
slide.addChart(pres.charts.DOUGHNUT, [{
  name: "Share", labels: ["Product A", "Product B", "Other"], values: [45, 35, 20]
}], {
  x: 6, y: 1, w: 3.5, h: 3.5,
  chartColors: ["0078D4", "1E2761", "CADCFC"],
  showPercent: true
});
```

#### Slide Masters

```javascript
pres.defineSlideMaster({
  title: "TITLE_SLIDE",
  background: { color: "1E2761" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 1, y: 1.5, w: 8, h: 2 } } },
    { placeholder: { options: { name: "subtitle", type: "body", x: 1, y: 3.5, w: 8, h: 1 } } }
  ]
});

let titleSlide = pres.addSlide({ masterName: "TITLE_SLIDE" });
titleSlide.addText("Presentation Title", { placeholder: "title", color: "FFFFFF", fontSize: 44 });
```

---

### python-pptx (Alternative)

Python-native library. No Node.js required. Good for data-driven presentations.

#### Setup

```python
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9 widescreen
prs.slide_height = Inches(7.5)

slide_layout = prs.slide_layouts[6]  # Blank layout
slide = prs.slides.add_slide(slide_layout)
```

**Unit system:** python-pptx uses EMU (English Metric Units). 914,400 EMU = 1 inch. Use helpers:
- `Inches(1)` = 914,400 EMU
- `Pt(12)` = 12 points (font size)
- `Emu(914400)` = 1 inch

#### Object Hierarchy

```
Presentation
  └── Slides
       └── Slide
            └── Shapes (collection)
                 ├── Shape (rectangle, oval, etc.)
                 │    └── TextFrame → Paragraphs → Runs
                 ├── Picture
                 ├── Table
                 ├── Chart
                 └── GroupShape
```

#### Adding Text

```python
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

# Add text box
txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(1))
tf = txBox.text_frame
tf.word_wrap = True

# First paragraph (auto-created)
p = tf.paragraphs[0]
p.alignment = PP_ALIGN.LEFT
run = p.add_run()
run.text = "Title Text"
run.font.size = Pt(36)
run.font.bold = True
run.font.color.rgb = RGBColor(0x1E, 0x27, 0x61)
run.font.name = "Arial"

# Add another paragraph
p2 = tf.add_paragraph()
p2.alignment = PP_ALIGN.LEFT
run2 = p2.add_run()
run2.text = "Subtitle text here"
run2.font.size = Pt(16)
run2.font.color.rgb = RGBColor(0x60, 0x5E, 0x5C)
```

#### Adding Shapes

```python
from pptx.enum.shapes import MSO_SHAPE

# Rectangle
shape = slide.shapes.add_shape(
    MSO_SHAPE.RECTANGLE,
    Inches(0), Inches(0), Inches(13.333), Inches(1.2)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0x1E, 0x27, 0x61)
shape.line.fill.background()  # No border

# Rounded rectangle
shape = slide.shapes.add_shape(
    MSO_SHAPE.ROUNDED_RECTANGLE,
    Inches(1), Inches(2), Inches(3), Inches(2)
)
shape.fill.solid()
shape.fill.fore_color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

# Oval (for icon circles)
circle = slide.shapes.add_shape(
    MSO_SHAPE.OVAL,
    Inches(1), Inches(2), Inches(0.6), Inches(0.6)
)
circle.fill.solid()
circle.fill.fore_color.rgb = RGBColor(0x00, 0x78, 0xD4)
```

#### Adding Images

```python
slide.shapes.add_picture("photo.png", Inches(5), Inches(1), Inches(4), Inches(3))

# From bytes/stream
from io import BytesIO
img_stream = BytesIO(image_bytes)
slide.shapes.add_picture(img_stream, Inches(5), Inches(1), Inches(4), Inches(3))
```

#### Adding Images — Aspect-Ratio Preserving (MANDATORY for diagrams)

**ALWAYS use this helper when placing generated images (D2 diagrams, azure_diagrams, matplotlib charts, screenshots).** The raw `add_picture(path, left, top, width, height)` stretches the image to the exact dimensions you specify, ignoring the source aspect ratio. This produces distorted/stretched visuals that look unprofessional.

```python
from PIL import Image
from pptx.util import Inches

def add_picture_fit(slide, img_path, left, top, max_width, max_height):
    """Add picture preserving aspect ratio within a bounding box, centered.
    
    Args:
        slide: pptx slide object
        img_path: path to image file (str or Path)
        left: left edge of bounding box (EMU, e.g. Inches(0.3))
        top: top edge of bounding box (EMU, e.g. Inches(1.1))
        max_width: max width of bounding box (EMU, e.g. Inches(12.7))
        max_height: max height of bounding box (EMU, e.g. Inches(6.0))
    """
    with Image.open(img_path) as img:
        img_w, img_h = img.size
    aspect = img_w / img_h
    box_aspect = max_width / max_height
    if aspect > box_aspect:
        # Image is wider than box — constrain by width
        w = max_width
        h = max_width / aspect
    else:
        # Image is taller than box — constrain by height
        h = max_height
        w = max_height * aspect
    # Center in the bounding box
    x = left + (max_width - w) / 2
    y = top + (max_height - h) / 2
    slide.shapes.add_picture(str(img_path), int(x), int(y), int(w), int(h))
```

**Usage:**
```python
# Instead of this (STRETCHES the image):
slide.shapes.add_picture(png_path, Inches(0.3), Inches(1.1), Inches(12.7), Inches(6.0))

# Use this (preserves aspect ratio, centered in bounding box):
add_picture_fit(slide, png_path, Inches(0.3), Inches(1.1), Inches(12.7), Inches(6.0))
```

**When to use which:**
| Scenario | Method |
|----------|--------|
| Generated diagrams (D2, azure_diagrams, matplotlib) | `add_picture_fit()` — ALWAYS |
| Screenshots, photos with unknown dimensions | `add_picture_fit()` — ALWAYS |
| Icons/logos where you control exact pixel size | `add_picture()` is OK |
| Pre-cropped images with known matching ratio | `add_picture()` is OK |

#### Adding Tables

```python
rows, cols = 4, 3
table_shape = slide.shapes.add_table(rows, cols, Inches(0.5), Inches(1.5), Inches(9), Inches(3))
table = table_shape.table

# Set column widths
table.columns[0].width = Inches(3)
table.columns[1].width = Inches(3)
table.columns[2].width = Inches(3)

# Header row
for i, header in enumerate(["Name", "Role", "Location"]):
    cell = table.cell(0, i)
    cell.text = header
    cell.fill.solid()
    cell.fill.fore_color.rgb = RGBColor(0x1E, 0x27, 0x61)
    for paragraph in cell.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            run.font.bold = True
            run.font.size = Pt(11)

# Data rows
data = [["Alice", "Engineer", "Seattle"], ["Bob", "Designer", "Portland"]]
for row_idx, row_data in enumerate(data, start=1):
    for col_idx, value in enumerate(row_data):
        table.cell(row_idx, col_idx).text = value
```

#### Adding Charts

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

chart_data = CategoryChartData()
chart_data.categories = ["Q1", "Q2", "Q3", "Q4"]
chart_data.add_series("Revenue", (4500, 5500, 6200, 7100))

chart_frame = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED,
    Inches(0.5), Inches(1.5), Inches(6), Inches(4),
    chart_data
)
chart = chart_frame.chart
chart.has_legend = False

# Style the chart
plot = chart.plots[0]
series = plot.series[0]
series.format.fill.solid()
series.format.fill.fore_color.rgb = RGBColor(0x00, 0x78, 0xD4)
```

#### Slide Layouts

```python
# Common layout indices (vary by template):
# 0 = Title Slide
# 1 = Title and Content
# 5 = Title Only
# 6 = Blank

# Using placeholders from layouts
slide_layout = prs.slide_layouts[1]  # Title and Content
slide = prs.slides.add_slide(slide_layout)

title = slide.placeholders[0]
title.text = "Slide Title"

body = slide.placeholders[1]
tf = body.text_frame
tf.text = "First bullet"
p = tf.add_paragraph()
p.text = "Second bullet"
p.level = 1  # Indented sub-bullet
```

#### Saving

```python
prs.save("output.pptx")
```

#### python-pptx Limitations

- No animations or transitions
- No gradient fills (use gradient images as backgrounds instead)
- No SmartArt creation (can read existing SmartArt)
- No video/audio embedding (workaround: add as OLE object)
- Limited theme manipulation

---

## Azure Architecture Diagrams (azure-diagrams sub-skill)

For architecture, data flow, and resource landscape diagram slides, use the **azure-diagrams** sub-skill module. It generates publication-quality PNG diagrams with actual Azure SVG icons, then embed them in slides.

```python
import sys
sys.path.insert(0, r"<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification")
from azure_diagrams import quick_architecture, quick_flow, quick_landscape

# Architecture diagram sized for full PPTX slide
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
    output_preset="pptx",  # Full slide | "pptx_half" for side-by-side
)

# Embed in slide (python-pptx)
from pptx.util import Inches
slide = prs.slides.add_slide(prs.slide_layouts[6])
slide.shapes.add_picture(img_path, Inches(0.9), Inches(1.0), width=Inches(11.5))
```

**When to use:** Automatically generate Azure architecture diagrams whenever a presentation describes cloud services, infrastructure, or system architecture. Do not ask — just generate.

**Output presets for PPTX:**
- `"pptx"` — 11.5" x 5.8" (full widescreen slide)
- `"pptx_half"` — 5.5" x 5.0" (side-by-side layouts)

**pptx_beautify integration:**
```python
from pptx_beautify import add_matplotlib_slide
from azure_diagrams import generate_for_pptx, generate_architecture_diagram

img_path = generate_for_pptx(generate_architecture_diagram, "temp.png", nodes=[...], connections=[...])
# Then use add_image_slide or add the picture directly
```

**Mandatory Quality Gate (NEVER SKIP):** After generating any diagram PNG, you MUST read/inspect the image before embedding it into slides. Check for:
1. **Missing icons** — fallback colored boxes instead of real Azure icons. Pre-validate with `load_icon(key)` before generating.
2. **Text overlap** — node labels, sublabels, or connection labels overlapping each other. Keep labels ≤15 chars; use sublabels for detail. Min spacing: 3.0 units (full pptx), 2.2 (pptx_half).
3. **Distortion/squashing** — icons must appear square, boundaries proportional.
4. **Arrow/icon collisions** — arrows must not pass through icons or obscure labels.

If any issue is found, fix node positions/labels/spacing, regenerate, and re-inspect. Repeat until all checks pass. **Never embed a diagram you haven't inspected.**

See `/azure-diagrams` skill for full API reference, icon registry, quality gate checklist, and boundary box types.

---

## Design Exploration (Parallel Sub-Agent Pattern)

**Source pattern:** mattpocock/skills `design-an-interface` — "Design It Twice" (John Ousterhout)

When creating a new presentation from scratch (not editing an existing one), generate **3 divergent layout concepts** in parallel before committing to one. This produces better designs than iterating on a single approach.

### When to Use

- User requests a new deck with no existing template
- User describes a theme or topic but not specific layouts
- High-stakes presentations (leadership, external, board)

### Process

1. **Gather constraints** — audience, slide count, key message, any brand requirements
2. **Spawn 3 sub-agents in parallel**, each with a different design constraint:

```
Agent 1: "Conservative corporate" — Navy/white, minimal shapes, heavy text hierarchy
Agent 2: "Visual storytelling" — Image-dominant, bold colors, hero slides with data viz
Agent 3: "Consulting grade" — McKinsey/BCG style, action titles, SCR narrative, split layouts
```

Each sub-agent should produce:
- A **2-slide proof** (title slide + one content slide)
- A **rationale** (why this approach suits the audience)
- A **trade-off note** (what this approach sacrifices)

3. **Present all 3 to the user** with a comparison:

| Dimension | Conservative | Visual | Consulting |
|-----------|-------------|--------|------------|
| Audience fit | ... | ... | ... |
| Information density | ... | ... | ... |
| Production speed | ... | ... | ... |

4. **User picks one** (or a hybrid) — proceed with full build using the chosen direction

### Anti-Patterns

- Generating 3 minor variations of the same layout (must be genuinely different approaches)
- Spending more than 5 minutes per proof (these are quick sketches, not final slides)
- Skipping this step when the user has already specified a design system (e.g., "use Bold Signal Light")

## Background Exploration for Content Slides

**Source pattern:** mattpocock/skills `qa` and `github-triage`

When creating presentation content about a codebase, project, or system the user works on, **spawn a background Explore agent** to gather context while discussing the deck structure with the user.

### When to Use

- User says "make a deck about our TechMentor architecture"
- User wants slides summarizing a project's status or technical design
- Content requires understanding code, config, or project structure

### Process

1. **While talking to the user** about slide structure, kick off:
```
Agent(subagent_type=Explore, run_in_background=True):
  "Explore [project area] to understand: architecture, key components,
   domain terminology, recent changes, and any documentation.
   Report: component names, relationships, and user-facing behaviors."
```

2. **Use the exploration results** to:
   - Adopt the project's domain language in slide titles and body text
   - Identify the right level of abstraction for the audience
   - Catch any factual errors before they make it into the deck

3. **Never reference file paths or line numbers** in slide content — describe behaviors and architecture, not code locations (durable description principle from mattpocock/skills)

---

## Design System

### Design Philosophy

**Every slide must tell a story.** A presentation is not a document — it is a visual argument. Each slide should have a single clear message that the audience can grasp in 3 seconds.

**Core principles:**

1. **Action titles, not topic titles.** The slide headline IS the takeaway.
   - Bad: "Q3 Revenue Results"
   - Good: "Q3 revenue grew 18% driven by APAC expansion"

2. **One idea per slide.** If you need "and" in your title, split into two slides.

3. **Pyramid Principle.** Lead with the conclusion. Support with evidence below. The audience should understand your point before seeing the data.

4. **Visual dominance.** Every slide needs a visual element — chart, icon, image, or shape. Text-only slides are forgettable.

5. **SCR narrative arc.** Structure the overall deck as:
   - **Situation** — context the audience already knows
   - **Complication** — the problem or change
   - **Resolution** — your recommendation

6. **Dominance over equality.** One element should dominate each slide (a large chart, a big number, a hero image). Never give all elements equal visual weight.

7. **Ghost Deck Method.** Plan action titles on blank slides first. Read all titles in sequence — they should tell a complete story without any body content. Then add evidence.

8. **"So What?" test.** Every slide must pass this test. If you cannot articulate why the slide matters to the overall recommendation, cut it.

9. **3-Second Rule.** The audience should grasp the slide's main point in 3 seconds. If the key insight requires reading body text, promote it to the title.

10. **Gestalt Proximity.** Items placed close together are perceived as related. Keep titles close to their paragraphs (0.1" gap), and separate unrelated sections with larger gaps (0.5"+).

### Color Palettes

**The 60-30-10 Rule:** 60% dominant color (backgrounds, large areas), 30% secondary (supporting elements, cards), 10% accent (CTAs, highlights, key data).

**Pick a palette that matches your topic.** If swapping your colors into a different presentation would still "work," your choices aren't specific enough.

| Theme | Primary | Secondary | Accent | Best For |
|-------|---------|-----------|--------|----------|
| **Midnight Executive** | `1E2761` | `CADCFC` | `FFFFFF` | Corporate, finance, strategy |
| **Forest & Moss** | `2C5F2D` | `97BC62` | `F5F5F5` | Sustainability, growth, nature |
| **Coral Energy** | `F96167` | `F9E795` | `2F3C7E` | Marketing, creative, launches |
| **Warm Terracotta** | `B85042` | `E7E8D1` | `A7BEAE` | Culture, people, wellness |
| **Ocean Gradient** | `065A82` | `1C7293` | `21295C` | Technology, data, analytics |
| **Charcoal Minimal** | `36454F` | `F2F2F2` | `212121` | Minimal, modern, premium |
| **Teal Trust** | `028090` | `00A896` | `02C39A` | Healthcare, trust, reliability |
| **Berry & Cream** | `6D2E46` | `A26769` | `ECE2D0` | Luxury, fashion, premium |
| **Sage Calm** | `84B59F` | `69A297` | `50808E` | Calm, nature, mindfulness |
| **Cherry Bold** | `990011` | `FCF6F5` | `2F3C7E` | Bold statements, alerts, urgency |
| **Fortive Corporate** | `005EB8` | `F4F4F4` | `00A3E0` | Fortive brand presentations |

**Dark Mode Palettes (2026 trend — premium tech feel):**

| Style | Background | Surface | Text | Accent 1 | Accent 2 |
|-------|-----------|---------|------|----------|----------|
| **Tech Neon** | `0D0D0D` | `1A1A2E` | `F5F5F7` | `39FF14` | `00D4FF` |
| **Corporate Dark** | `1B1B2F` | `2D2B55` | `E8E8E8` | `6C63FF` | `FF6584` |
| **GitHub Dark** | `0D1117` | `161B22` | `C9D1D9` | `58A6FF` | `3FB950` |
| **Apple Dark** | `1C1C1E` | `2C2C2E` | `F5F5F7` | `0A84FF` | `30D158` |
| **White & Gold** | `FFFFFF` | `F5F3EF` | `2C2C2C` | `C9A84C` | `8B7532` |

**Dark/light sandwich:** Use dark backgrounds for title + conclusion slides, light for content slides. Or commit to dark throughout for a premium feel.

**Building a corporate palette from one brand color:**
1. Start with the brand's primary color (e.g., `005EB8`)
2. Derive a tint at 10-15% opacity for backgrounds (e.g., `E6F0FA`)
3. Derive a shade at 70% luminance for text (e.g., `003D7A`)
4. Pick a complementary accent (opposite on color wheel or analogous)
5. Use pure white and a warm gray (`F4F4F4`) for card backgrounds

### Typography

**Choose an interesting font pairing.** Don't default to Arial. Pick a header font with personality and pair it with a clean body font.

| Header Font | Body Font | Vibe |
|-------------|-----------|------|
| Georgia | Calibri | Classic corporate |
| Arial Black | Arial | Bold and clean |
| Calibri | Calibri Light | Modern Microsoft |
| Cambria | Calibri | Elegant professional |
| Trebuchet MS | Calibri | Friendly tech |
| Impact | Arial | Bold statement |
| Palatino | Garamond | Premium editorial |
| Consolas | Calibri | Technical/engineering |

**Size hierarchy:**

| Element | Size | Weight |
|---------|------|--------|
| Slide title | 36-44pt | Bold |
| Section header | 20-24pt | Bold |
| Body text | 14-16pt | Regular |
| Captions/labels | 10-12pt | Regular or Light |
| Large stat callout | 60-72pt | Bold |
| Stat label | 12-14pt | Regular |

**Rules:**
- Maximum 2 font families per presentation (1 header + 1 body)
- Left-align body text (center only titles and single-line callouts)
- Use weight contrast (bold headers, regular body) not just size
- Minimum 14pt for any text that must be readable

### Layout Patterns

All dimensions for 16:9 (10" x 5.625"). Margins: 0.5" from all edges.

#### Pattern 1: Title Slide (Dark)

Full-color background with centered title and subtitle.

```javascript
slide.background = { color: "1E2761" };
slide.addText("Presentation Title", {
  x: 1, y: 1.5, w: 8, h: 1.5,
  fontSize: 44, fontFace: "Georgia", color: "FFFFFF",
  bold: true, align: "center", valign: "middle"
});
slide.addText("Subtitle or Date", {
  x: 1, y: 3.2, w: 8, h: 0.8,
  fontSize: 18, fontFace: "Calibri", color: "CADCFC",
  align: "center", valign: "top"
});
```

#### Pattern 2: Section Divider

Bold heading with accent bar. Use to separate major sections.

```javascript
slide.background = { color: "F4F4F4" };
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 2.2, w: 0.08, h: 1.2, fill: { color: "0078D4" }
});
slide.addText("Section Title", {
  x: 0.8, y: 2.2, w: 8, h: 1.2,
  fontSize: 36, fontFace: "Georgia", color: "1E2761",
  bold: true, align: "left", valign: "middle", margin: 0
});
```

#### Pattern 3: Two-Column (Text + Visual)

Content on left, image/chart on right. Most versatile layout.

```javascript
slide.background = { color: "FFFFFF" };
// Left column: action title + bullets
slide.addText("Revenue grew 18% in Q3", {
  x: 0.5, y: 0.4, w: 4.5, h: 0.8,
  fontSize: 24, bold: true, color: "1E2761", margin: 0
});
slide.addText([
  { text: "APAC led with 32% growth", options: { bullet: true, breakLine: true } },
  { text: "New product line contributed $2.1M", options: { bullet: true, breakLine: true } },
  { text: "Customer retention at 94%", options: { bullet: true } }
], { x: 0.5, y: 1.4, w: 4.5, h: 3, fontSize: 14, color: "323130" });

// Right column: chart or image
slide.addChart(pres.charts.BAR, chartData, {
  x: 5.5, y: 0.5, w: 4, h: 4.5, barDir: "col",
  chartColors: ["0078D4"], showLegend: false
});
```

#### Pattern 4: Icon + Text Rows

3-4 rows, each with a colored icon circle, bold header, and description.

```javascript
slide.background = { color: "FFFFFF" };
slide.addText("Key Capabilities", {
  x: 0.5, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, bold: true, color: "1E2761", margin: 0
});

const items = [
  { icon: FaChartLine, title: "Analytics", desc: "Real-time dashboards with drill-through" },
  { icon: FaShieldAlt, title: "Security", desc: "Enterprise-grade encryption and RBAC" },
  { icon: FaCogs, title: "Automation", desc: "ML-powered workflow optimization" }
];

for (let i = 0; i < items.length; i++) {
  const y = 1.3 + i * 1.3;
  // Icon circle
  slide.addShape(pres.shapes.OVAL, {
    x: 0.5, y: y, w: 0.6, h: 0.6, fill: { color: "0078D4" }
  });
  slide.addImage({ data: await iconToBase64Png(items[i].icon, "#FFFFFF"), x: 0.6, y: y + 0.1, w: 0.4, h: 0.4 });
  // Title + description
  slide.addText(items[i].title, {
    x: 1.4, y: y, w: 7.5, h: 0.35,
    fontSize: 16, bold: true, color: "1E2761", margin: 0
  });
  slide.addText(items[i].desc, {
    x: 1.4, y: y + 0.35, w: 7.5, h: 0.35,
    fontSize: 13, color: "605E5C", margin: 0
  });
}
```

#### Pattern 5: Large Stat Callout

Big numbers (60-72pt) with small labels. For KPIs, headline metrics.

```javascript
slide.background = { color: "FFFFFF" };
slide.addText("Impact at a Glance", {
  x: 0.5, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, bold: true, color: "1E2761", margin: 0
});

const stats = [
  { value: "$4.2M", label: "Revenue" },
  { value: "18%", label: "YoY Growth" },
  { value: "94%", label: "Retention" }
];

for (let i = 0; i < stats.length; i++) {
  const x = 0.5 + i * 3.1;
  slide.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.3, w: 2.8, h: 3.2,
    fill: { color: "F4F4F4" }, rectRadius: 0
  });
  slide.addText(stats[i].value, {
    x: x, y: 1.6, w: 2.8, h: 1.5,
    fontSize: 60, bold: true, color: "0078D4", align: "center"
  });
  slide.addText(stats[i].label, {
    x: x, y: 3.2, w: 2.8, h: 0.6,
    fontSize: 14, color: "605E5C", align: "center"
  });
}
```

#### Pattern 6: Comparison Columns

Side-by-side comparison (before/after, pros/cons, Option A vs B).

```javascript
slide.background = { color: "FFFFFF" };
slide.addText("Current State vs. Target State", {
  x: 0.5, y: 0.3, w: 9, h: 0.7,
  fontSize: 24, bold: true, color: "1E2761", margin: 0
});

// Left column
slide.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.2, w: 4.3, h: 0.5, fill: { color: "D13438" } });
slide.addText("Current State", {
  x: 0.5, y: 1.2, w: 4.3, h: 0.5,
  fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle"
});
slide.addText([
  { text: "Manual data entry", options: { bullet: true, breakLine: true } },
  { text: "3-day processing time", options: { bullet: true, breakLine: true } },
  { text: "15% error rate", options: { bullet: true } }
], { x: 0.7, y: 1.9, w: 3.9, h: 3, fontSize: 14, color: "323130" });

// Right column
slide.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 1.2, w: 4.3, h: 0.5, fill: { color: "107C10" } });
slide.addText("Target State", {
  x: 5.2, y: 1.2, w: 4.3, h: 0.5,
  fontSize: 16, bold: true, color: "FFFFFF", align: "center", valign: "middle"
});
slide.addText([
  { text: "Automated pipeline", options: { bullet: true, breakLine: true } },
  { text: "Real-time processing", options: { bullet: true, breakLine: true } },
  { text: "<1% error rate", options: { bullet: true } }
], { x: 5.4, y: 1.9, w: 3.9, h: 3, fontSize: 14, color: "323130" });
```

#### Pattern 7: Timeline / Process Flow

Horizontal timeline with numbered circles and milestones.

```javascript
slide.background = { color: "FFFFFF" };
slide.addText("Implementation Roadmap", {
  x: 0.5, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, bold: true, color: "1E2761", margin: 0
});

const steps = ["Discovery", "Design", "Build", "Test", "Launch"];
const lineY = 2.5;

// Connecting line
slide.addShape(pres.shapes.LINE, {
  x: 1.2, y: lineY + 0.25, w: 7.6, h: 0,
  line: { color: "E2E8F0", width: 3 }
});

for (let i = 0; i < steps.length; i++) {
  const x = 0.8 + i * 1.9;
  // Circle
  slide.addShape(pres.shapes.OVAL, {
    x: x, y: lineY, w: 0.5, h: 0.5,
    fill: { color: "0078D4" }
  });
  // Number
  slide.addText(String(i + 1), {
    x: x, y: lineY, w: 0.5, h: 0.5,
    fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle"
  });
  // Label
  slide.addText(steps[i], {
    x: x - 0.3, y: lineY + 0.7, w: 1.1, h: 0.5,
    fontSize: 12, color: "1E2761", align: "center", bold: true
  });
}
```

#### Pattern 8: Half-Bleed Image

Full-height image on one side, text content on the other.

```javascript
slide.background = { color: "FFFFFF" };
// Image fills right half
slide.addImage({
  path: "hero-image.jpg",
  x: 5, y: 0, w: 5, h: 5.625,
  sizing: { type: "cover", w: 5, h: 5.625 }
});
// Text on left
slide.addText("Transform Your\nWorkflow", {
  x: 0.5, y: 1, w: 4, h: 2,
  fontSize: 36, bold: true, color: "1E2761", margin: 0
});
slide.addText("Our platform automates the manual processes that slow your team down.", {
  x: 0.5, y: 3.2, w: 4, h: 1.5,
  fontSize: 16, color: "605E5C"
});
```

#### Pattern 9: 2x2 Grid

Four content blocks in a grid. Good for categorization, quadrants, feature groups.

```javascript
slide.background = { color: "F4F4F4" };
slide.addText("Four Pillars of Growth", {
  x: 0.5, y: 0.3, w: 9, h: 0.7,
  fontSize: 28, bold: true, color: "1E2761", margin: 0
});

const quadrants = [
  { title: "Innovation", desc: "R&D investment up 25%", x: 0.5, y: 1.2 },
  { title: "Expansion", desc: "3 new markets entered", x: 5.15, y: 1.2 },
  { title: "Efficiency", desc: "OpEx reduced by 12%", x: 0.5, y: 3.2 },
  { title: "Talent", desc: "200 new hires in 2025", x: 5.15, y: 3.2 }
];

for (const q of quadrants) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: q.x, y: q.y, w: 4.35, h: 1.8,
    fill: { color: "FFFFFF" },
    shadow: { type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.08 }
  });
  slide.addText(q.title, {
    x: q.x + 0.3, y: q.y + 0.3, w: 3.75, h: 0.5,
    fontSize: 18, bold: true, color: "1E2761", margin: 0
  });
  slide.addText(q.desc, {
    x: q.x + 0.3, y: q.y + 0.9, w: 3.75, h: 0.7,
    fontSize: 14, color: "605E5C", margin: 0
  });
}
```

#### Pattern 10: Bento Grid

Modern asymmetric grid with varying card sizes. Premium, editorial feel.

```javascript
slide.background = { color: "F4F4F4" };

// Large card (left, spans full height)
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 0.5, w: 4.5, h: 4.625,
  fill: { color: "1E2761" }
});
slide.addText("$12.4M\nTotal Revenue", {
  x: 0.8, y: 1.5, w: 3.9, h: 2,
  fontSize: 48, bold: true, color: "FFFFFF", align: "left", valign: "middle"
});

// Top-right card
slide.addShape(pres.shapes.RECTANGLE, {
  x: 5.2, y: 0.5, w: 4.3, h: 2.1,
  fill: { color: "FFFFFF" }
});
slide.addText("18%", { x: 5.5, y: 0.8, w: 3.7, h: 1.0, fontSize: 44, bold: true, color: "0078D4" });
slide.addText("Year-over-Year Growth", { x: 5.5, y: 1.8, w: 3.7, h: 0.5, fontSize: 13, color: "605E5C" });

// Bottom-right cards (two side-by-side)
slide.addShape(pres.shapes.RECTANGLE, { x: 5.2, y: 2.8, w: 2.0, h: 2.325, fill: { color: "FFFFFF" } });
slide.addText("94%", { x: 5.4, y: 3.2, w: 1.6, h: 0.8, fontSize: 32, bold: true, color: "107C10" });
slide.addText("Retention", { x: 5.4, y: 4.0, w: 1.6, h: 0.4, fontSize: 11, color: "605E5C" });

slide.addShape(pres.shapes.RECTANGLE, { x: 7.5, y: 2.8, w: 2.0, h: 2.325, fill: { color: "FFFFFF" } });
slide.addText("1.2K", { x: 7.7, y: 3.2, w: 1.6, h: 0.8, fontSize: 32, bold: true, color: "0078D4" });
slide.addText("New Customers", { x: 7.7, y: 4.0, w: 1.6, h: 0.4, fontSize: 11, color: "605E5C" });
```

#### Pattern 11: Data Dashboard

Charts + KPI cards on one slide. Dense but organized.

```javascript
slide.background = { color: "F4F4F4" };
slide.addText("Performance Dashboard — Q3 2025", {
  x: 0.5, y: 0.3, w: 9, h: 0.5,
  fontSize: 22, bold: true, color: "1E2761", margin: 0
});

// KPI cards row (4 across top)
const kpis = [
  { value: "$4.2M", label: "Revenue", color: "0078D4" },
  { value: "+18%", label: "Growth", color: "107C10" },
  { value: "94%", label: "CSAT", color: "0078D4" },
  { value: "1,247", label: "Orders", color: "0078D4" }
];
for (let i = 0; i < 4; i++) {
  const x = 0.5 + i * 2.3;
  slide.addShape(pres.shapes.RECTANGLE, { x: x, y: 0.9, w: 2.1, h: 1.1, fill: { color: "FFFFFF" } });
  slide.addText(kpis[i].value, { x: x, y: 0.95, w: 2.1, h: 0.65, fontSize: 28, bold: true, color: kpis[i].color, align: "center" });
  slide.addText(kpis[i].label, { x: x, y: 1.6, w: 2.1, h: 0.3, fontSize: 10, color: "605E5C", align: "center" });
}

// Chart area below
slide.addChart(pres.charts.BAR, chartData, {
  x: 0.5, y: 2.2, w: 5.5, h: 3.2, barDir: "col",
  chartColors: ["0078D4"], showLegend: false,
  valGridLine: { color: "E2E8F0", size: 0.5 }, catGridLine: { style: "none" }
});
slide.addChart(pres.charts.DOUGHNUT, pieData, {
  x: 6.5, y: 2.2, w: 3, h: 3.2,
  chartColors: ["0078D4", "1E2761", "CADCFC", "E2E8F0"],
  showPercent: true
});
```

#### Pattern 12: Quote / Testimonial

Large quote with attribution. Good for customer quotes, vision statements.

```javascript
slide.background = { color: "1E2761" };

// Large opening quote mark
slide.addText("\u201C", {
  x: 0.5, y: 0.5, w: 1, h: 1.5,
  fontSize: 120, color: "CADCFC", fontFace: "Georgia", margin: 0
});

// Quote text
slide.addText("This platform transformed how we approach data-driven decisions across the organization.", {
  x: 1.5, y: 1.2, w: 7, h: 2.5,
  fontSize: 28, color: "FFFFFF", fontFace: "Georgia", italic: true, align: "left"
});

// Attribution
slide.addText("— Sarah Chen, VP of Analytics", {
  x: 1.5, y: 4, w: 7, h: 0.5,
  fontSize: 16, color: "CADCFC", fontFace: "Calibri"
});
```

#### Pattern 13: Dark Architecture Diagram (from Cocoon-AI evaluation)

Dark-background slide with semantically colored component boxes, connecting arrows, and optional boundary groups. For simple architectures (3-8 nodes), draws directly on the slide instead of embedding a PNG. Premium "tech keynote" feel.

**When to use:** Technical deep-dives, engineering presentations, demo slides. Not for executive audiences who expect light backgrounds.

**Category colors (match azure-diagrams and docx-beautify):**

| Category | Fill | Stroke | Text |
|----------|------|--------|------|
| Compute | `1A3B2A` | `34D399` | `E8F5E9` |
| Data | `2A1A3B` | `A78BFA` | `EDE7F6` |
| AI/ML | `0A3B3B` | `22D3EE` | `E0F7FA` |
| Security | `3B1A2A` | `FB7185` | `FCE4EC` |
| Networking | `3B2A0A` | `FBBF24` | `FFF3E0` |
| Integration | `0A2A3B` | `60A5FA` | `E3F2FD` |

```javascript
slide.background = { color: "0D1117" };

// Title
slide.addText("System Architecture", {
  x: 0.5, y: 0.2, w: 9, h: 0.6,
  fontSize: 24, bold: true, color: "F5F5F7", fontFace: "Consolas", margin: 0
});
slide.addText("Production Environment", {
  x: 0.5, y: 0.75, w: 9, h: 0.3,
  fontSize: 12, color: "94A3B8", fontFace: "Consolas", margin: 0
});

// Boundary box (dashed region)
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0.3, y: 1.2, w: 9.4, h: 4.0,
  fill: { color: "FBBF24", transparency: 95 },
  line: { color: "FBBF24", width: 1, dashType: "dash" }
});
slide.addText("Azure Subscription", {
  x: 0.5, y: 1.3, w: 3, h: 0.3,
  fontSize: 10, color: "FBBF24", fontFace: "Consolas", margin: 0
});

// Helper: draw one component box
function addComponent(slide, label, sublabel, x, y, fill, stroke, textColor) {
  const w = 2.2, h = 1.1;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.06,
    fill: { color: fill }, line: { color: stroke, width: 1.5 }
  });
  slide.addText(label, {
    x, y: y + 0.25, w, h: 0.35,
    fontSize: 13, bold: true, color: textColor, align: "center", fontFace: "Consolas", margin: 0
  });
  slide.addText(sublabel, {
    x, y: y + 0.6, w, h: 0.3,
    fontSize: 10, color: "94A3B8", align: "center", fontFace: "Consolas", margin: 0
  });
}

// Components (category colored)
addComponent(slide, "App Service", "FastAPI :8000", 0.7, 2.5, "1A3B2A", "34D399", "E8F5E9");   // compute
addComponent(slide, "Azure OpenAI", "Sonnet 4.6",   3.9, 2.5, "0A3B3B", "22D3EE", "E0F7FA");   // ai
addComponent(slide, "Cosmos DB", "Sessions",         7.1, 2.5, "2A1A3B", "A78BFA", "EDE7F6");   // data

// Connection arrows (gray, subtle)
slide.addShape(pres.shapes.LINE, {
  x: 2.9, y: 3.05, w: 1.0, h: 0,
  line: { color: "64748B", width: 1.5 }
});
slide.addText("REST API", {
  x: 2.9, y: 2.75, w: 1.0, h: 0.25,
  fontSize: 8, color: "94A3B8", align: "center", fontFace: "Consolas", margin: 0
});
slide.addShape(pres.shapes.LINE, {
  x: 6.1, y: 3.05, w: 1.0, h: 0,
  line: { color: "64748B", width: 1.5 }
});
slide.addText("Sessions", {
  x: 6.1, y: 2.75, w: 1.0, h: 0.25,
  fontSize: 8, color: "94A3B8", align: "center", fontFace: "Consolas", margin: 0
});

// Legend (bottom-left)
const legendY = 4.5;
const cats = [
  { label: "Compute", fill: "1A3B2A", stroke: "34D399" },
  { label: "AI/ML", fill: "0A3B3B", stroke: "22D3EE" },
  { label: "Data", fill: "2A1A3B", stroke: "A78BFA" },
];
for (let i = 0; i < cats.length; i++) {
  const lx = 0.7 + i * 2.0;
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: lx, y: legendY, w: 0.3, h: 0.2, rectRadius: 0.03,
    fill: { color: cats[i].fill }, line: { color: cats[i].stroke, width: 1 }
  });
  slide.addText(cats[i].label, {
    x: lx + 0.4, y: legendY, w: 1.2, h: 0.2,
    fontSize: 9, color: "94A3B8", fontFace: "Consolas", valign: "middle", margin: 0
  });
}
```

**Rules for dark architecture slides:**
- Use `Consolas` font (monospace = technical authority)
- Max 2 line colors: `64748B` for data flow, `FB7185` dashed for auth flow
- Boundary boxes: 95% transparent fill + dashed stroke
- Component boxes: dark fill + bright stroke (never bright fill + dark text)
- Connection labels: 8pt gray, above the line
- Keep to 3-8 components; beyond that, use azure-diagrams PNG embed instead

### Spacing Rules

- **0.5" minimum margins** from all slide edges
- **0.3-0.5" gaps** between content blocks (pick one and be consistent)
- **Leave breathing room** — don't fill every inch. White space is a design element.
- **Consistent vertical rhythm** — align elements to a grid (e.g., every 0.5" or 0.3")
- **Card padding** — 0.2-0.3" internal padding inside card shapes

### Common Design Mistakes

1. **Don't repeat the same layout** — vary columns, cards, and callouts across slides
2. **Don't center body text** — left-align paragraphs and lists; center only titles and single-line callouts
3. **Don't skimp on size contrast** — titles need 36pt+ to stand out from 14-16pt body
4. **Don't default to blue** — pick colors that reflect the specific topic
5. **Don't mix spacing randomly** — choose 0.3" or 0.5" gaps and use consistently
6. **Don't style one slide and leave the rest plain** — commit fully or keep it simple throughout
7. **Don't create text-only slides** — add images, icons, charts, or visual elements
8. **Don't forget text box padding** — when aligning text with shapes, set `margin: 0`
9. **Don't use low-contrast elements** — icons AND text need strong contrast against backgrounds
10. **NEVER use accent lines under titles** — these are a hallmark of AI-generated slides; use whitespace or background color instead
11. **Don't use more than 2 font families** — 1 header + 1 body is ideal
12. **Don't use more than 5 colors** — stick to the 60-30-10 palette
13. **Don't mix rounded and sharp corners** — pick one shape style and commit
14. **Don't cram slides full** — leave at least 40% of the slide as empty space; whitespace signals confidence and premium quality
15. **Don't use the same color intensity for all data** — highlight the ONE key data point in your accent color and gray everything else out
16. **Don't skip the source line** — especially on data slides; a small gray source citation at the bottom adds credibility (consulting standard)

---

## Slide Type Templates

Ready-to-use complete slide code for common presentation needs.

### Executive Summary

```javascript
slide.background = { color: "FFFFFF" };

// Action title
slide.addText("APAC expansion drove 18% revenue growth, exceeding target by 3 points", {
  x: 0.5, y: 0.3, w: 9, h: 0.8,
  fontSize: 22, bold: true, color: "1E2761", margin: 0
});

// Separator line
slide.addShape(pres.shapes.LINE, {
  x: 0.5, y: 1.2, w: 9, h: 0, line: { color: "E2E8F0", width: 1 }
});

// Three key points with icons
const points = [
  { title: "Revenue", detail: "$4.2M in Q3, up from $3.6M YoY" },
  { title: "Growth Driver", detail: "APAC contributed 42% of new revenue" },
  { title: "Next Steps", detail: "Expand LATAM presence in Q4" }
];

for (let i = 0; i < points.length; i++) {
  const y = 1.5 + i * 1.2;
  slide.addShape(pres.shapes.OVAL, { x: 0.5, y: y + 0.05, w: 0.4, h: 0.4, fill: { color: "0078D4" } });
  slide.addText(String(i + 1), {
    x: 0.5, y: y + 0.05, w: 0.4, h: 0.4,
    fontSize: 14, bold: true, color: "FFFFFF", align: "center", valign: "middle"
  });
  slide.addText(points[i].title, {
    x: 1.1, y: y, w: 3, h: 0.3, fontSize: 16, bold: true, color: "1E2761", margin: 0
  });
  slide.addText(points[i].detail, {
    x: 1.1, y: y + 0.35, w: 8, h: 0.3, fontSize: 14, color: "605E5C", margin: 0
  });
}
```

### Agenda

```javascript
slide.background = { color: "FFFFFF" };
slide.addText("Agenda", {
  x: 0.5, y: 0.3, w: 9, h: 0.8,
  fontSize: 36, bold: true, color: "1E2761", margin: 0
});

const agenda = [
  "Market overview and competitive landscape",
  "Q3 financial performance",
  "Product roadmap update",
  "Go-to-market strategy for Q4",
  "Discussion and next steps"
];

for (let i = 0; i < agenda.length; i++) {
  const y = 1.4 + i * 0.75;
  // Number
  slide.addText(String(i + 1).padStart(2, "0"), {
    x: 0.5, y: y, w: 0.6, h: 0.5,
    fontSize: 20, bold: true, color: "0078D4", align: "right", valign: "middle", margin: 0
  });
  // Item text
  slide.addText(agenda[i], {
    x: 1.3, y: y, w: 7.5, h: 0.5,
    fontSize: 18, color: "323130", valign: "middle", margin: 0
  });
  // Separator
  if (i < agenda.length - 1) {
    slide.addShape(pres.shapes.LINE, {
      x: 1.3, y: y + 0.6, w: 7.5, h: 0,
      line: { color: "EDEBE9", width: 0.5 }
    });
  }
}
```

### Thank You / Q&A

```javascript
slide.background = { color: "1E2761" };

slide.addText("Thank You", {
  x: 1, y: 1.2, w: 8, h: 1.5,
  fontSize: 48, bold: true, color: "FFFFFF", fontFace: "Georgia",
  align: "center", valign: "middle"
});

slide.addText("Questions?", {
  x: 1, y: 2.8, w: 8, h: 0.8,
  fontSize: 24, color: "CADCFC", align: "center"
});

// Contact info
slide.addShape(pres.shapes.LINE, {
  x: 3, y: 3.8, w: 4, h: 0, line: { color: "CADCFC", width: 0.5 }
});
slide.addText("name@company.com  |  linkedin.com/in/name", {
  x: 1, y: 4.1, w: 8, h: 0.5,
  fontSize: 14, color: "CADCFC", align: "center"
});
```

### SWOT / 2x2 Matrix

```javascript
slide.background = { color: "FFFFFF" };
slide.addText("SWOT Analysis", {
  x: 0.5, y: 0.2, w: 9, h: 0.6,
  fontSize: 28, bold: true, color: "1E2761", margin: 0
});

const swot = [
  { title: "Strengths", items: ["Strong brand", "Loyal customers"], color: "107C10", x: 0.5, y: 1.0 },
  { title: "Weaknesses", items: ["Legacy systems", "High OpEx"], color: "D13438", x: 5.15, y: 1.0 },
  { title: "Opportunities", items: ["APAC expansion", "AI integration"], color: "0078D4", x: 0.5, y: 3.2 },
  { title: "Threats", items: ["New competitors", "Regulation"], color: "B85042", x: 5.15, y: 3.2 }
];

for (const q of swot) {
  // Card background
  slide.addShape(pres.shapes.RECTANGLE, {
    x: q.x, y: q.y, w: 4.35, h: 2.0, fill: { color: "F4F4F4" }
  });
  // Color bar at top
  slide.addShape(pres.shapes.RECTANGLE, {
    x: q.x, y: q.y, w: 4.35, h: 0.06, fill: { color: q.color }
  });
  // Title
  slide.addText(q.title, {
    x: q.x + 0.2, y: q.y + 0.15, w: 3.95, h: 0.4,
    fontSize: 16, bold: true, color: q.color, margin: 0
  });
  // Items
  const bulletText = q.items.map((item, idx) => ({
    text: item,
    options: { bullet: true, breakLine: idx < q.items.length - 1 }
  }));
  slide.addText(bulletText, {
    x: q.x + 0.2, y: q.y + 0.6, w: 3.95, h: 1.2, fontSize: 13, color: "323130"
  });
}
```

### KPI Dashboard

```javascript
slide.background = { color: "F4F4F4" };
// Header bar
slide.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.7, fill: { color: "1E2761" } });
slide.addText("Monthly Performance Report — February 2026", {
  x: 0.5, y: 0, w: 9, h: 0.7,
  fontSize: 18, bold: true, color: "FFFFFF", valign: "middle", margin: 0
});

// 6 KPI cards (3x2 grid)
const kpis = [
  { value: "$12.4M", label: "Total Revenue", trend: "+18% YoY", up: true },
  { value: "1,247", label: "Orders", trend: "+8% MoM", up: true },
  { value: "94.2%", label: "Customer Satisfaction", trend: "+2.1pts", up: true },
  { value: "$3,420", label: "Avg Order Value", trend: "-3% MoM", up: false },
  { value: "12.5", label: "Days to Close", trend: "-2.1 days", up: true },
  { value: "87%", label: "Target Attainment", trend: "On track", up: true }
];

for (let i = 0; i < 6; i++) {
  const col = i % 3;
  const row = Math.floor(i / 3);
  const x = 0.5 + col * 3.1;
  const y = 1.0 + row * 2.2;

  slide.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 2.8, h: 1.9, fill: { color: "FFFFFF" },
    shadow: { type: "outer", blur: 3, offset: 1, angle: 135, color: "000000", opacity: 0.06 }
  });
  slide.addText(kpis[i].value, {
    x: x, y: y + 0.25, w: 2.8, h: 0.8,
    fontSize: 32, bold: true, color: "1E2761", align: "center"
  });
  slide.addText(kpis[i].label, {
    x: x, y: y + 1.0, w: 2.8, h: 0.35,
    fontSize: 11, color: "605E5C", align: "center"
  });
  slide.addText(kpis[i].trend, {
    x: x, y: y + 1.35, w: 2.8, h: 0.3,
    fontSize: 11, bold: true, color: kpis[i].up ? "107C10" : "D13438", align: "center"
  });
}
```

---

## Advanced Techniques

Elite-level techniques that separate amateur from professional presentations. Each technique includes specific implementation code.

### Consulting Slide Anatomy (McKinsey/BCG Style)

Every consulting slide follows a three-part structure:

```
┌──────────────────────────────────────────────┐
│ ACTION TITLE (1-2 lines, complete sentence   │  ← The takeaway
│ stating the "so what")                       │
├──────────────────────────────────────────────┤
│                                              │
│            BODY (evidence)                   │  ← Charts, tables, frameworks
│      Charts, data, frameworks that           │
│      PROVE the action title                  │
│                                              │
├──────────────────────────────────────────────┤
│ Source: Company data, FY2024           pg 12 │  ← Source + page number
└──────────────────────────────────────────────┘
```

**Rules:**
- Title IS the conclusion — not a topic label ("Revenue grew 18%" not "Revenue Results")
- Body contains only evidence that supports the title
- Source line cites data origin (8-10pt, gray)
- One accent color highlights the key data point; everything else is black/gray

```javascript
// McKinsey-style slide master
pres.defineSlideMaster({
  title: "CONSULTING",
  background: { color: "FFFFFF" },
  objects: [
    // Title zone separator
    { rect: { x: 0.5, y: 0.85, w: 9, h: 0.01, fill: { color: "D0D0D0" } } },
    // Source line placeholder
    { text: {
      text: "",
      options: { x: 0.5, y: 5.1, w: 7, h: 0.3, fontSize: 8, color: "999999" }
    }},
    // Page number
    { text: {
      text: "",
      options: { x: 9, y: 5.1, w: 0.5, h: 0.3, fontSize: 8, color: "999999", align: "right" }
    }}
  ]
});

let slide = pres.addSlide({ masterName: "CONSULTING" });

// Action title (complete sentence — the takeaway)
slide.addText(
  "Customer acquisition costs rose 34% YoY, driven by digital ad competition",
  { x: 0.5, y: 0.15, w: 9, h: 0.65, fontSize: 16, bold: true, color: "1A1A1A", fontFace: "Arial" }
);
```

**Ghost Deck Method:** Plan action titles first on blank slides. Read all titles in sequence — they should tell a complete story. Then add body evidence.

### Dark Mode Design

Dark backgrounds on modern LED/OLED screens make colors pop and give presentations a cinematic, premium feel. This is the dominant trend in 2025-2026 template design.

**Key rules:**
- Never use pure white (`FFFFFF`) text on dark — use off-white (`F5F5F7`) to reduce harshness
- Cards/panels use a slightly lighter surface color than the background to create depth layers
- Neon/electric accent colors (lime, blue, pink) at full saturation create focus points
- Thin borders at `48484A` separate elements subtly

```javascript
// Dark mode slide with layered surfaces
slide.background = { color: "0D1117" };

// Surface card (slightly lighter than background)
const makeDarkShadow = () => ({
  type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.3
});
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 0.5, y: 1.0, w: 4.2, h: 3.5,
  fill: { color: "161B22" },
  rectRadius: 0.15,
  line: { color: "21262D", width: 0.5 },
  shadow: makeDarkShadow()
});

// Neon accent metric inside the card
slide.addText("$4.2M", {
  x: 0.8, y: 1.5, w: 3.6, h: 1.5,
  fontSize: 56, bold: true, color: "58A6FF", fontFace: "Arial Black"
});
slide.addText("Annual Revenue", {
  x: 0.8, y: 3.0, w: 3.6, h: 0.5,
  fontSize: 14, color: "8B949E"
});
```

### Image Overlays & Duotone

Layer a semi-transparent colored rectangle over a full-bleed photo. This guarantees text legibility while preserving the image's atmosphere.

```javascript
// Full-bleed image with dark scrim overlay
slide.addImage({ path: "hero.jpg", x: 0, y: 0, w: "100%", h: "100%" });

// Semi-transparent overlay (70% opaque navy)
slide.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: "100%", h: "100%",
  fill: { color: "1B1B2F", transparency: 30 }
});

// Text is now always readable regardless of image content
slide.addText("Section Title", {
  x: 0.75, y: 2.0, w: 7, h: 1.5,
  fontSize: 48, bold: true, color: "FFFFFF"
});
```

**For duotone effect:** Pre-process the image to grayscale (using Sharp, PIL, or an online tool), then overlay a colored rectangle at 30-40% transparency. Two overlapping colored rectangles at different transparencies create a two-tone effect.

### Glassmorphism (Frosted Glass Panels)

Semi-transparent panels floating over a vibrant background. Creates depth and premium feel.

**Design parameters:**
- Panel fill: white at 85-90% transparency (10-15% opaque)
- Border: 0.5pt white at 60% transparency
- Shadow: outer, blur 20, offset 8, black at 12% opacity
- Background: dark with subtle color blobs or a blurred image

```javascript
slide.background = { color: "0F0A1A" };

// Subtle color blob behind the glass (decorative)
slide.addShape(pres.shapes.OVAL, {
  x: 2, y: 0.5, w: 6, h: 5,
  fill: { color: "6C63FF", transparency: 85 }
});

// Frosted glass panel
const makeGlassShadow = () => ({
  type: "outer", blur: 20, offset: 8, angle: 135, color: "000000", opacity: 0.12
});
slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x: 1.5, y: 1.0, w: 7.0, h: 3.5,
  fill: { color: "FFFFFF", transparency: 85 },
  rectRadius: 0.2,
  line: { color: "FFFFFF", width: 0.5, transparency: 60 },
  shadow: makeGlassShadow()
});

// Content on the glass panel
slide.addText("Key Insight", {
  x: 2.0, y: 1.5, w: 6.0, h: 0.8,
  fontSize: 32, bold: true, color: "FFFFFF"
});
```

**python-pptx approach:** Pre-blur the background image with PIL (`GaussianBlur(radius=30)`) before inserting, then layer transparent shapes on top.

### Typography as Hero Element

Use massive text (80-120pt) as the dominant visual. Forces extreme clarity — every word must earn its place.

```javascript
// Giant hero text with split color
slide.background = { color: "0A0A0A" };

slide.addText([
  { text: "THINK ", options: { fontSize: 96, bold: true, color: "FFFFFF", fontFace: "Arial Black" } },
  { text: "BIGGER", options: { fontSize: 96, bold: true, color: "58A6FF", fontFace: "Arial Black" } }
], { x: 0.8, y: 1.5, w: 8.5, h: 2.5 });

slide.addText("Why incremental improvement is the enemy of transformation", {
  x: 0.8, y: 4.2, w: 6.0, h: 0.8,
  fontSize: 18, color: "8B949E"
});
```

**Text as watermark:** Place enormous text (200-300pt) at 95% transparency behind content to create a subtle textural background.

```javascript
// Watermark behind content
slide.addText("2026", {
  x: -1.0, y: -0.5, w: 12.0, h: 7.0,
  fontSize: 250, fontFace: "Arial Black", color: "FFFFFF",
  bold: true, align: "center", valign: "middle", transparency: 95
});
```

### Kinetic / Dynamic Layouts

Create a sense of motion in static slides through staggering, diagonal energy, and motion trails.

**Motion trail:** 3 copies of a shape at decreasing opacity, offset slightly.

```javascript
// Motion trail effect
const offsets = [
  { dx: 0, dy: 0, transparency: 0 },      // Fully opaque (destination)
  { dx: -0.4, dy: 0.2, transparency: 60 }, // Fading
  { dx: -0.8, dy: 0.4, transparency: 88 }  // Nearly invisible (origin)
];

// Draw in reverse order (faintest first, solid last)
for (let i = offsets.length - 1; i >= 0; i--) {
  const o = offsets[i];
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 3.0 + o.dx, y: 2.0 + o.dy, w: 3.0, h: 1.8,
    fill: { color: "0078D4", transparency: o.transparency },
    rectRadius: 0.1
  });
}
```

**Staggered cards:** Each card progressively offset downward to imply sequence and movement.

```javascript
const metrics = [
  { value: "12.4K", label: "Users", color: "58A6FF" },
  { value: "$2.1M", label: "Revenue", color: "3FB950" },
  { value: "+127%", label: "Growth", color: "F778BA" }
];

metrics.forEach((m, i) => {
  const x = 0.8 + i * 3.0;
  const y = 1.5 + i * 0.3;  // Each card 0.3" lower — implies motion

  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: x, y: y, w: 2.5, h: 2.0,
    fill: { color: "161B22" }, rectRadius: 0.1,
    shadow: { type: "outer", blur: 8, offset: 3, angle: 135, color: "000000", opacity: 0.2 }
  });
  slide.addText(m.value, {
    x: x + 0.2, y: y + 0.3, w: 2.1, h: 1.0,
    fontSize: 36, bold: true, color: m.color, fontFace: "Arial Black"
  });
  slide.addText(m.label, {
    x: x + 0.2, y: y + 1.3, w: 2.1, h: 0.5,
    fontSize: 14, color: "8B949E"
  });
});
```

### Professional Data Visualization

#### Waffle Chart (Shape Grid)

A 10x10 grid where filled squares represent a percentage. More intuitive than pie charts for part-of-whole data.

```javascript
function addWaffleChart(slide, pres, { x, y, cellSize, gap, pct, filledColor, emptyColor }) {
  const filled = Math.round(pct);
  for (let i = 0; i < 100; i++) {
    const col = i % 10;
    const row = Math.floor(i / 10);
    slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x + col * (cellSize + gap),
      y: y + (9 - row) * (cellSize + gap),  // Fill from bottom up
      w: cellSize, h: cellSize,
      fill: { color: i < filled ? filledColor : emptyColor },
      rectRadius: 0.02
    });
  }
}

// Usage
addWaffleChart(slide, pres, {
  x: 0.5, y: 1.0, cellSize: 0.22, gap: 0.04,
  pct: 73, filledColor: "0078D4", emptyColor: "21262D"
});
slide.addText("73%", {
  x: 3.5, y: 2.0, w: 2.0, h: 1.0,
  fontSize: 48, bold: true, color: "0078D4", fontFace: "Arial Black"
});
slide.addText("Customer Satisfaction", {
  x: 3.5, y: 3.0, w: 2.0, h: 0.5,
  fontSize: 14, color: "8B949E"
});
```

#### Donut Chart with Center KPI

A doughnut chart with a large number in the center hole. Cleaner than a pie chart.

```javascript
slide.addChart(pres.charts.DOUGHNUT, [{
  name: "Progress", labels: ["Complete", "Remaining"], values: [78, 22]
}], {
  x: 2.0, y: 1.0, w: 4.0, h: 4.0,
  showTitle: false, showLegend: false,
  chartColors: ["0078D4", "21262D"],
  dataLabelPosition: "none",
  holeSize: 70  // Large center hole for the KPI number
});

// KPI number centered inside the donut
slide.addText("78%", {
  x: 2.8, y: 2.2, w: 2.4, h: 1.5,
  fontSize: 54, bold: true, color: "0078D4",
  align: "center", valign: "middle"
});
```

#### Sparkline (Built from Line Segments)

A tiny trend line that fits next to a metric card.

```javascript
function addSparkline(slide, pres, { x, y, w, h, data, color }) {
  const max = Math.max(...data), min = Math.min(...data);
  const range = max - min || 1;
  const step = w / (data.length - 1);

  for (let i = 0; i < data.length - 1; i++) {
    const x1 = x + i * step;
    const y1 = y + h - ((data[i] - min) / range) * h;
    const x2 = x + (i + 1) * step;
    const y2 = y + h - ((data[i + 1] - min) / range) * h;
    slide.addShape(pres.shapes.LINE, {
      x: x1, y: y1, w: x2 - x1, h: y2 - y1,
      line: { color: color, width: 1.5 }
    });
  }
  // Endpoint dot
  const lastY = y + h - ((data[data.length - 1] - min) / range) * h;
  slide.addShape(pres.shapes.OVAL, {
    x: x + w - 0.06, y: lastY - 0.06, w: 0.12, h: 0.12,
    fill: { color: color }
  });
}

// Usage
addSparkline(slide, pres, {
  x: 7.0, y: 2.0, w: 2.5, h: 0.8,
  data: [12, 15, 11, 18, 22, 19, 25, 28, 24, 31],
  color: "3FB950"
});
```

#### Data Highlight Principle

Use color to isolate the single most important data point. Make everything else gray. This improves comprehension by up to 40%.

```javascript
// Highlight one bar in a chart — the key insight
slide.addChart(pres.charts.BAR, [{
  name: "Revenue", labels: ["Q1", "Q2", "Q3", "Q4"], values: [1.2, 1.8, 2.4, 3.1]
}], {
  x: 0.5, y: 1.0, w: 9.0, h: 4.0, barDir: "col",
  chartColors: ["D0D0D0", "D0D0D0", "D0D0D0", "0078D4"],  // Only Q4 is blue
  valueBarColors: true,
  showValue: true, dataLabelPosition: "outEnd",
  valGridLine: { color: "E2E8F0", size: 0.5 },
  catGridLine: { style: "none" },
  showLegend: false
});
```

### Circle-Cropped Profiles with Border Ring

Professional team slides use circular photos with a colored border ring.

```javascript
const team = [
  { name: "Alice Chen", role: "CEO", img: "alice.png" },
  { name: "Bob Smith", role: "CTO", img: "bob.png" },
  { name: "Carol Wu", role: "CFO", img: "carol.png" },
  { name: "Dan Lee", role: "COO", img: "dan.png" }
];

const circleSize = 2.0;
const startX = 1.0;
const spacing = 2.3;

team.forEach((p, i) => {
  const x = startX + i * spacing;

  // Border ring (slightly larger circle behind the image)
  slide.addShape(pres.shapes.OVAL, {
    x: x - 0.05, y: 1.5 - 0.05,
    w: circleSize + 0.1, h: circleSize + 0.1,
    fill: { color: "0078D4" }
  });

  // Circular profile photo
  slide.addImage({
    path: p.img, x: x, y: 1.5, w: circleSize, h: circleSize, rounding: true
  });

  // Name + role
  slide.addText(p.name, {
    x: x - 0.3, y: 3.8, w: circleSize + 0.6, h: 0.5,
    fontSize: 16, bold: true, color: "1E2761", align: "center"
  });
  slide.addText(p.role, {
    x: x - 0.3, y: 4.25, w: circleSize + 0.6, h: 0.4,
    fontSize: 13, color: "605E5C", align: "center"
  });
});
```

### White & Gold Luxury Style

Elegant serif typography with gold accents. Signals premium quality and trust.

```javascript
slide.background = { color: "FFFFFF" };

// Gold accent line
slide.addShape(pres.shapes.RECTANGLE, {
  x: 2.0, y: 2.5, w: 1.5, h: 0.03, fill: { color: "C9A84C" }
});

// Section number
slide.addText("01", {
  x: 2.0, y: 2.7, w: 2.0, h: 0.8,
  fontSize: 14, fontFace: "Garamond", color: "C9A84C", charSpacing: 4
});

// Section title (serif font)
slide.addText("Executive Summary", {
  x: 2.0, y: 3.2, w: 6.0, h: 1.2,
  fontSize: 42, fontFace: "Georgia", color: "2C2C2C"
});

// Bottom gold line (longer)
slide.addShape(pres.shapes.RECTANGLE, {
  x: 2.0, y: 4.6, w: 3.0, h: 0.03, fill: { color: "C9A84C" }
});

// Subtitle (italic serif)
slide.addText("A comprehensive overview of our strategic direction", {
  x: 2.0, y: 4.9, w: 6.0, h: 0.6,
  fontSize: 16, fontFace: "Georgia", color: "888888", italic: true
});
```

### Negative Space as Design

Leave at least 40-50% of the slide empty. Whitespace signals confidence and premium quality.

**Single-stat slide:** One massive number, one sentence, vast emptiness.

```javascript
slide.background = { color: "0D1117" };

// The one number — positioned in the left third
slide.addText("$4.2B", {
  x: 0.8, y: 1.5, w: 5.0, h: 2.5,
  fontSize: 96, fontFace: "Arial Black", color: "FFFFFF", bold: true
});

// Single supporting line
slide.addText("Total addressable market by 2028", {
  x: 0.8, y: 4.0, w: 5.0, h: 0.6,
  fontSize: 18, color: "8B949E"
});

// Source (very small)
slide.addText("Source: McKinsey Global Report, 2025", {
  x: 0.8, y: 5.0, w: 5.0, h: 0.3,
  fontSize: 9, color: "484F58"
});

// THE ENTIRE RIGHT HALF IS EMPTY — this is the negative space at work
```

### Visual Psychology Layouts

#### Z-Pattern (Minimal Content)

The eye follows: top-left → top-right → diagonal → bottom-left → bottom-right.

```javascript
// Top-left: brand
slide.addText("ACME", {
  x: 0.5, y: 0.4, w: 2.0, h: 0.4,
  fontSize: 12, fontFace: "Arial Black", color: "484F58"
});

// Top-right: section label
slide.addText("Market Analysis", {
  x: 7.0, y: 0.4, w: 2.5, h: 0.4,
  fontSize: 12, color: "484F58", align: "right"
});

// Center: hero content (where the diagonal crosses)
slide.addText("$12.4B", {
  x: 2.0, y: 1.5, w: 6.0, h: 2.5,
  fontSize: 96, fontFace: "Arial Black", color: "FFFFFF",
  align: "center", bold: true
});

// Bottom-left: context
slide.addText("Projected market size, 2028", {
  x: 0.5, y: 4.5, w: 4.0, h: 0.5, fontSize: 16, color: "8B949E"
});

// Bottom-right: page number
slide.addText("12", {
  x: 9.0, y: 5.0, w: 0.5, h: 0.3, fontSize: 10, color: "484F58", align: "right"
});
```

#### F-Pattern (Text-Heavy)

Top row gets the most scanning, then progressively shorter horizontal scans. Place the most important content at the top.

### Designing for Morph Transitions

Design slide pairs where the same element appears at different positions/sizes. When Morph is applied in PowerPoint, the element smoothly animates between states.

**Ken Burns (image pan):** Same oversized image shifted between two slides.

```javascript
// Slide 1: show left portion
const s1 = pres.addSlide();
s1.addImage({ path: "panorama.jpg", x: 0, y: -1, w: 16, h: 9 });
s1.addText("Our Journey", { x: 0.5, y: 2, w: 5, h: 1.5, fontSize: 44, bold: true, color: "FFFFFF" });

// Slide 2: shifted to show right portion
const s2 = pres.addSlide();
s2.addImage({ path: "panorama.jpg", x: -6, y: -1, w: 16, h: 9 });
s2.addText("Where We're Going", { x: 4, y: 2, w: 5, h: 1.5, fontSize: 44, bold: true, color: "FFFFFF" });
```

**Zoom focus:** Small card on slide 1 expands to fill slide 2.

### Wave / Curve Decorative Footer

Organic curved shapes at the bottom add visual interest to geometric slides. Generate wave SVGs at getwaves.io, convert to PNG, then overlay.

```javascript
// Pre-rendered wave PNG at slide bottom
slide.addImage({
  path: "wave-footer.png",  // or data: "image/png;base64,..."
  x: 0, y: 4.0, w: 10, h: 1.625
});
```

For python-pptx, use `build_freeform()` to create wave shapes programmatically.

### Geometric Pattern Backgrounds

Subtle repeating patterns (dots, lines) at very low opacity add texture without overwhelming content. Pre-render as transparent PNG for performance (shape loops add many objects).

```javascript
// Dot pattern overlay — pre-rendered PNG preferred for performance
// If using shapes (small presentations only):
slide.background = { color: "1B1B2F" };
for (let row = 0; row < 12; row++) {
  for (let col = 0; col < 20; col++) {
    slide.addShape(pres.shapes.OVAL, {
      x: 0.25 + col * 0.5, y: 0.25 + row * 0.5,
      w: 0.05, h: 0.05,
      fill: { color: "FFFFFF", transparency: 93 }
    });
  }
}
```

---

## Reading Content

```bash
# Text extraction
python -m markitdown presentation.pptx

# Visual overview (thumbnail grid)
python scripts/thumbnail.py presentation.pptx

# Raw XML inspection
python scripts/office/unpack.py presentation.pptx unpacked/
```

---

## Editing Existing Presentations

### Template-Based Workflow

1. **Analyze** the template:
   ```bash
   python scripts/thumbnail.py template.pptx     # Visual overview
   python -m markitdown template.pptx             # Text content
   ```

2. **Plan slide mapping** — for each content section, choose a template slide. Use varied layouts:
   - Multi-column layouts, image + text combos, stat callouts, section dividers
   - Match content type to layout style
   - Avoid repeating the same text-heavy layout for every slide

3. **Unpack**: `python scripts/office/unpack.py template.pptx unpacked/`

4. **Build presentation** (structural changes):
   - Delete unwanted slides (remove from `<p:sldIdLst>` in `ppt/presentation.xml`)
   - Duplicate slides: `python scripts/add_slide.py unpacked/ slide2.xml`
   - Reorder `<p:sldId>` elements
   - Complete ALL structural changes before editing content

5. **Edit content** — update text in each `slide{N}.xml`:
   - Use subagents for parallel editing (each slide is a separate XML file)
   - Use the Edit tool, not sed or Python scripts
   - Bold all headers with `b="1"` on `<a:rPr>`
   - Never use unicode bullets (use `<a:buChar>` or `<a:buAutoNum>`)

6. **Clean**: `python scripts/clean.py unpacked/`

7. **Pack**: `python scripts/office/pack.py unpacked/ output.pptx --original template.pptx`

### Script Reference

| Script | Purpose |
|--------|---------|
| `scripts/office/unpack.py` | Extract PPTX, pretty-print XML |
| `scripts/add_slide.py` | Duplicate slide or create from layout |
| `scripts/clean.py` | Remove orphaned slides/media/rels |
| `scripts/office/pack.py` | Repack with validation |
| `scripts/thumbnail.py` | Create visual grid of slides |

### XML Editing Rules

**Formatting:**
- Bold headers: add `b="1"` to `<a:rPr>`
- Multi-item content: create separate `<a:p>` elements (never concatenate into one paragraph)
- Copy `<a:pPr>` from original paragraphs to preserve line spacing

**Smart quotes:** Use XML entities in new text:

| Character | XML Entity |
|-----------|------------|
| " (left double) | `&#x201C;` |
| " (right double) | `&#x201D;` |
| ' (left single) | `&#x2018;` |
| ' (right single) | `&#x2019;` |

**Whitespace:** Use `xml:space="preserve"` on `<a:t>` with leading/trailing spaces.

**XML parsing:** Use `defusedxml.minidom`, not `xml.etree.ElementTree` (corrupts namespaces).

**Template cleanup:** When source has fewer items than template, remove excess elements entirely — don't just clear text.

---

## Build-Time Prevention Checklist (MANDATORY)

Before generating a PPTX, verify these patterns in your build script. These are the most common causes of broken presentations — catching them at build time is 10x cheaper than fixing them in QA.

### 1. Text Line Breaks — NEVER use `\n` in `.text` assignments

python-pptx does NOT render `\n` as a line break — it renders as a replacement character box (`⎕`). This silently corrupts every slide that has multi-line text.

```python
# WRONG — shows broken character in PowerPoint
p.text = "Phase 2: Agentic AI-Powered\nLLM Usage Tracking"

# CORRECT — split into paragraphs
lines = text.split("\n")
for i, line in enumerate(lines):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = line
    p.font.size = Pt(font_size)
    # ... apply formatting to each paragraph
```

**Prevention**: Any helper function that accepts text must split on `\n` and create separate paragraphs. Wrap this in your `add_textbox()` utility so it's impossible to forget.

### 2. D2 Diagrams — Use Native PNG, NOT cairosvg

D2 generates SVGs with embedded base64 web fonts (`@font-face` with WOFF data). cairosvg cannot render these fonts — all text disappears, leaving tiny black boxes on a white canvas.

```python
# WRONG — cairosvg can't render D2's embedded fonts
subprocess.run([D2_EXE, ..., str(d2_file), str(svg_file)])
cairosvg.svg2png(bytestring=svg_file.read_bytes(), write_to=str(png_file))

# CORRECT — D2 natively renders PNG with proper fonts
subprocess.run([D2_EXE, "--theme", "0", "--pad", "60", str(d2_file), str(png_file)])
```

**When to use cairosvg**: Only for SVGs you generate yourself (matplotlib, azure_diagrams) where you control the fonts. Never for third-party SVG generators that embed fonts.

### 3. D2 Theme Selection

D2 theme 200 is dark (dark background). Use theme 0 (default/light) for slides with white backgrounds, unless you specifically want a dark diagram.

### 4. RGBA Transparency in Embedded Images

PNG images with RGBA mode have transparent regions that render as black in some viewers and QA tools. If you control the image pipeline, composite onto a white background before embedding:

```python
if img.mode == 'RGBA':
    bg = Image.new('RGB', img.size, (255, 255, 255))
    bg.paste(img, mask=img.split()[3])
    bg.save(output_path)
```

### 5. Shape Transparency via XML

python-pptx's `fill.solid()` creates a `_SolidFill` object that doesn't expose `.find()`. To set transparency/alpha on a solid fill, traverse the shape's XML element tree:

```python
def set_shape_fill(shape, color, transparency=0):
    fill = shape.fill
    fill.solid()
    fill.fore_color.rgb = color
    if transparency > 0:
        for sf in shape._element.iter(qn('a:solidFill')):
            if len(sf) > 0:
                alpha = sf[0].makeelement(qn('a:alpha'),
                    {'val': str(int((1 - transparency) * 100000))})
                sf[0].append(alpha)
            break
```

### 6. D2 Output Dimensions and Layout

D2 native PNG output matches the diagram's natural size. `direction: right` with many nodes produces extremely wide, thin images (e.g., 7302x678px — aspect ratio 10:1) that shrink to unreadable strips when fit to a slide.

**Fix**: Use `grid-rows: 2` to split long flows into a 2-row grid:

```d2
# WRONG — produces 10:1 aspect ratio, unreadable on slide
direction: right
step1 -> step2 -> step3 -> step4 -> step5 -> step6 -> step7 -> step8

# CORRECT — 2-row grid produces ~3:1 aspect ratio, fits slide well
grid-rows: 2
grid-gap: 40

row1: "" {
  direction: right
  style: { fill: transparent; stroke: transparent }
  step1 -> step2 -> step3 -> step4
}
row2: "" {
  direction: right
  style: { fill: transparent; stroke: transparent }
  step5 -> step6 -> step7 -> step8
}
row1.step4 -> row2.step5: { style.stroke-dash: 5 }
```

**Target aspect ratios**: 2:1 to 4:1 for landscape slides. If a diagram exceeds ~5:1, split into rows.

### 7. Image Placement — ALWAYS Preserve Aspect Ratio

**NEVER use raw `add_picture(path, left, top, width, height)` for generated images.** It stretches the image to the exact dimensions you specify, ignoring the source aspect ratio. This produces visually distorted diagrams.

```python
# WRONG — stretches image to 12.7" x 6.0" regardless of actual ratio
slide.shapes.add_picture(png_path, Inches(0.3), Inches(1.1), Inches(12.7), Inches(6.0))

# CORRECT — preserves aspect ratio, centers in bounding box
add_picture_fit(slide, png_path, Inches(0.3), Inches(1.1), Inches(12.7), Inches(6.0))
```

Use the `add_picture_fit()` helper from the [Adding Images — Aspect-Ratio Preserving](#adding-images--aspect-ratio-preserving-mandatory-for-diagrams) section. For PptxGenJS, use `sizing: { type: "contain" }`.

---

## Diagram Visual Quality Standards

These rules apply to every generated diagram (D2, Mermaid, matplotlib, azure_diagrams) embedded in a presentation. They are the difference between "diagram on a slide" and "consulting-grade visual."

### Node Shape Variety — Break the Rectangle Trap

Default diagrams use rectangles for everything. This produces flat, monotonous visuals that all look the same. Use shape semantics:

| Concept | Shape | D2 | Mermaid |
|---------|-------|----|---------| 
| Agent / autonomous component | Hexagon | `shape: hexagon` | `{{Agent Name}}` |
| Decision / gate | Diamond | `shape: diamond` | `{Decision?}` |
| Process / step | Rounded rectangle | `shape: rectangle` (default) | `[Process]` or `(Process)` |
| Data store / database | Cylinder | `shape: cylinder` | `[(Database)]` |
| External system / user | Person or oval | `shape: person` | `([User])` |
| Start / end | Circle or stadium | `shape: circle` | `([Start])` |

**Rule:** Every diagram with 4+ node types MUST use at least 2 distinct shapes. Never make all nodes rectangles.

### Layered Zones — Show Architecture Depth

Complex systems have layers (UI → API → Services → Data). Show them as horizontal or vertical bands with labeled headers:

```d2
# D2: Layered zone architecture
direction: down

ui_layer: "UI Layer" {
  style: {
    fill: "#E8F4FD"
    stroke: "#B3D9F2"
    border-radius: 8
    font-size: 16
    bold: true
  }
  web_app: "React Web App" { shape: rectangle }
  mobile: "Mobile App" { shape: rectangle }
}

api_layer: "API Gateway" {
  style: {
    fill: "#E8F0FE"
    stroke: "#A8C4E8"
    border-radius: 8
    font-size: 16
    bold: true
  }
  gateway: "LiteLLM Proxy" { shape: hexagon }
}

data_layer: "Data Layer" {
  style: {
    fill: "#F0F4E8"
    stroke: "#C8D8A8"
    border-radius: 8
    font-size: 16
    bold: true
  }
  delta: "Delta Lake" { shape: cylinder }
  cosmos: "Cosmos DB" { shape: cylinder }
}

ui_layer.web_app -> api_layer.gateway
api_layer.gateway -> data_layer.delta
```

**Rule:** Any diagram showing a multi-tier system MUST use container nesting with distinct fill colors per zone. Zone labels must be 14pt+ bold.

### Connection Line Discipline

Default thick, colorful arrows make diagrams look like subway maps. Use restraint:

| Property | Default (bad) | Target (good) |
|----------|--------------|---------------|
| Stroke width | 2-3px | 1-1.5px |
| Color | Multiple bright colors | Single muted gray (`#666666` or `#888888`) |
| Arrow head | Large filled | Small, subtle |
| Label placement | On the line | Near the line, not overlapping |

**D2:** `style.stroke-width: 1` + `style.stroke: "#666666"` on connections
**Mermaid:** Use `linkStyle` to set stroke color/width, or `%%{init}%%` `lineColor`

**Rule:** Connection lines are secondary visual elements — they guide the eye but should never dominate. Max 2 colors for connections in any diagram.

### Whitespace and Padding

Cramped diagrams look amateur. Professional diagrams breathe.

| Parameter | Minimum | D2 setting | Mermaid setting |
|-----------|---------|-----------|-----------------|
| Outer padding | 40-60px | `--pad 60` | `%%{init: {'flowchart': {'padding': 20}}}%%` |
| Node spacing | 40px+ | `grid-gap: 40` | `%%{init: {'flowchart': {'nodeSpacing': 50, 'rankSpacing': 50}}}%%` |
| Container padding | 20px+ | `style.padding: 20` | N/A (auto) |
| Content-to-edge ratio | 60-70% content | — | — |

**Rule:** If a diagram fills more than 75% of its bounding area with shapes/lines, it's too dense. Add padding, increase spacing, or split into two diagrams.

### Color Discipline for Diagrams

| Principle | Rule |
|-----------|------|
| **Max accent colors** | 3 per diagram + neutrals (white, gray, black) |
| **Fill lightness** | Use light fills (`#E8xxxx`, `#F0xxxx`) with dark borders and text |
| **Semantic color** | Green = done/success, Blue = active/in-progress, Yellow/Amber = warning/pending, Red = error/blocked, Purple = special/AI, Gray = inactive |
| **Background** | White or very light gray (`#FAFAFA`) for slide embedding; dark backgrounds only if the slide itself is dark-themed |
| **Border vs fill contrast** | Border should be 40-60% darker than fill (e.g., fill `#E8F0FE`, border `#2C4F6E`) |

**Rule:** Never use saturated/dark fills with dark text — always light fill + dark text or dark fill + white text. Test readability at 50% zoom.

### Split Layout Pattern — Diagram + Callout

For complex diagrams, don't force everything into the image. Use a split layout:

```
┌──────────────────────────────────────────────┐
│  ACTION TITLE                                │
├───────────────────────┬──────────────────────┤
│                       │                      │
│   DIAGRAM             │   KEY TAKEAWAYS      │
│   (65% width)         │   • Point 1          │
│                       │   • Point 2          │
│                       │   • Point 3          │
│                       │                      │
├───────────────────────┴──────────────────────┤
│  Source line                                 │
└──────────────────────────────────────────────┘
```

This avoids cramming explanatory text into the diagram itself, keeps labels short, and gives the audience a reading path: title → diagram (visual) → takeaways (verbal).

### Icon Row with Bracket Connectors (Proven Pattern)

For slides showing a toolchain, tech stack, or methodology stages. Proven on Leadership Forum sample (Veritas slide 18 adaptation).

**Visual structure:**
```
         ┌──────────────────────────────────────┐   ← bracket bar
         │                                      │   ← vertical drops
         ▼                                      ▼
      [icon1] ──▶ [icon2] ──▶ [icon3] ──▶ [icon4]   ← colored circles + arrow segments
      Label 1     Label 2     Label 3     Label 4    ← 2-line labels below
```

**Implementation (python-pptx):**

```python
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.oxml.ns import qn
from lxml import etree

# --- Config ---
items = [("MCP", "#005EB8"), ("Claude Code", "#8040C0"), ("AI Foundry", "#0078D4"),
         ("LiteLLM", "#28A745"), ("Delta Lake", "#FFC000"), ("Power BI", "#C74234")]
start_x, icon_y, diameter, spacing = 1.0, 1.85, 0.75, 1.95
CONN_COLOR = RGBColor(0x00, 0x5E, 0xB8)

# --- Colored icon circles ---
for i, (label, hex_color) in enumerate(items):
    x = start_x + i * spacing
    r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
    circle = slide.shapes.add_shape(MSO_SHAPE.OVAL,
        Inches(x), Inches(icon_y), Inches(diameter), Inches(diameter))
    circle.fill.solid()
    circle.fill.fore_color.rgb = RGBColor(r, g, b)
    circle.line.fill.background()
    # Label initial inside circle (centered)
    tf = circle.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = label[0]  # First character
    run.font.size = Pt(14); run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    # Vertical center via XML
    bodyPr = circle._element.find('.//' + qn('a:bodyPr'))
    if bodyPr is not None: bodyPr.set('anchor', 'ctr')

# --- Bracket frame (top bar + vertical drops) ---
first_cx = start_x + diameter / 2
last_cx = start_x + (len(items) - 1) * spacing + diameter / 2
bracket_y = icon_y - 0.15

# Top bar
bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(first_cx), Inches(bracket_y), Inches(last_cx - first_cx), Pt(1.5))
bar.fill.solid(); bar.fill.fore_color.rgb = CONN_COLOR; bar.line.fill.background()
# Left drop
ld = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(first_cx), Inches(bracket_y), Pt(1.5), Inches(icon_y - bracket_y))
ld.fill.solid(); ld.fill.fore_color.rgb = CONN_COLOR; ld.line.fill.background()
# Right drop
rd = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(last_cx), Inches(bracket_y), Pt(1.5), Inches(icon_y - bracket_y))
rd.fill.solid(); rd.fill.fore_color.rgb = CONN_COLOR; rd.line.fill.background()

# --- Arrow segments between icons (with triangle arrowheads) ---
for i in range(len(items) - 1):
    x_from = start_x + i * spacing + diameter + 0.05
    x_to = start_x + (i + 1) * spacing - 0.05
    mid_y = icon_y + diameter / 2
    # Horizontal bar
    seg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Inches(x_from), Inches(mid_y - 0.01), Inches(x_to - x_from), Pt(1.5))
    seg.fill.solid(); seg.fill.fore_color.rgb = CONN_COLOR; seg.line.fill.background()
    # Triangle arrowhead (FLOWCHART_EXTRACT rotated 90°)
    tri_sz = 0.12
    tri = slide.shapes.add_shape(MSO_SHAPE.FLOWCHART_EXTRACT,
        Inches(x_to - 0.02), Inches(mid_y - tri_sz/2), Inches(tri_sz), Inches(tri_sz))
    tri.fill.solid(); tri.fill.fore_color.rgb = CONN_COLOR; tri.line.fill.background()
    tri.rotation = 90.0  # Point right
```

**Key details:**
- `FLOWCHART_EXTRACT` is a triangle shape; rotate 90° to point right
- Bracket bar sits 0.15" above the icon row top
- Arrow segments span the gap between icon edges (with 0.05" padding)
- Works for 4-8 items on LAYOUT_WIDE; for LAYOUT_16x9, reduce spacing to ~1.4"

### Numbered Vertical Timeline (Proven Pattern)

For callout panels, delivery models, or step sequences alongside a diagram. Proven on Leadership Forum sample.

**Visual structure:**
```
     ①  Title One
     │   Description text here
     │
     ②  Title Two
     │   Description text here
     │
     ③  Title Three
         Description text here
```

**Implementation (python-pptx):**

```python
callouts = [
    ("2-Week Sprints", "Agent skills delivered in 2-week iteration cycles"),
    ("Human-in-the-Loop", "Every agent output validated before production use"),
    ("MCP-First", "All integrations via Model Context Protocol standard"),
]

panel_x = 8.5   # Right side of slide
panel_y = 3.55
circle_x = panel_x + 0.15
circle_d = 0.45
text_x = panel_x + 0.8
step_spacing = 0.95

# Vertical connecting line (behind circles)
line_top = panel_y + 0.55 + circle_d / 2
line_bot = panel_y + 0.55 + (len(callouts) - 1) * step_spacing + circle_d / 2
vline = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Inches(circle_x + circle_d/2 - 0.01), Inches(line_top),
    Pt(2), Inches(line_bot - line_top))
vline.fill.solid()
vline.fill.fore_color.rgb = RGBColor(0xE2, 0xE8, 0xF0)  # Light gray
vline.line.fill.background()

for i, (title, desc) in enumerate(callouts):
    cy = panel_y + 0.55 + i * step_spacing

    # Numbered circle (navy)
    nc = slide.shapes.add_shape(MSO_SHAPE.OVAL,
        Inches(circle_x), Inches(cy), Inches(circle_d), Inches(circle_d))
    nc.fill.solid()
    nc.fill.fore_color.rgb = RGBColor(0x00, 0x33, 0x66)  # Navy
    nc.line.fill.background()
    tf = nc.text_frame
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = str(i + 1)
    run.font.size = Pt(16); run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    bodyPr = nc._element.find('.//' + qn('a:bodyPr'))
    if bodyPr is not None: bodyPr.set('anchor', 'ctr')

    # Title (bold) + Description (gray) to the right
    # ... add_text helper calls for title at (text_x, cy+0.02) and desc at (text_x, cy+0.25)
```

**Key details:**
- Draw the vertical line FIRST so circles render on top
- `step_spacing` of 0.95" works for 3 items; use 0.75" for 4-5 items
- Pair with the Icon Row on the left side for a balanced split layout
- Navy circles + white numbers is the default; use pillar accent colors for variety

### Aspect Ratio Targets for Diagram Types

| Diagram Type | Target Ratio | Max Width (LAYOUT_WIDE) | Notes |
|-------------|-------------|------------------------|-------|
| Flowchart (top-down) | 3:4 to 1:1 | 8" | Tall, leave room for title + footer |
| Flowchart (left-right) | 2:1 to 3:1 | 12" | Use grid-rows if exceeds 4:1 |
| Sequence diagram | 1:1 to 3:2 | 10" | Width grows with participants |
| Architecture (nested) | 4:3 to 16:9 | 12" | Match slide aspect ratio |
| Gantt / timeline | 3:1 to 4:1 | 12" | Horizontal emphasis |
| Hub-spoke | 1:1 | 6" | Square, use in split layout |

---

## QA Workflow

**Assume there are problems. Your job is to find them.**

The first render is almost never correct. Approach QA as a bug hunt, not a confirmation step.

**IMPORTANT: This QA workflow is MANDATORY and AUTOMATIC.** After every PPTX generation or beautification, run all 3 stages programmatically. Do not ask the user for permission — just run it. Do not declare a presentation complete until all stages pass with zero issues. If issues are found, fix them in the build script, regenerate, and re-run QA until clean.

**MANDATORY: Every PPTX must pass all three QA stages before delivery.** Do not skip any stage. Do not declare success until all three report zero issues.

### Stage 1: Content QA

```bash
python -m markitdown output.pptx
```

Check for missing content, typos, wrong order.

**Check for leftover placeholder text:**
```bash
python -m markitdown output.pptx | grep -iE "xxxx|lorem|ipsum|placeholder|this.*(page|slide).*layout"
```

### Stage 2: Programmatic Layout QA (MANDATORY — run before visual QA)

This catches layout bugs that are invisible in code but obvious in the output: shapes past the slide edge, margin violations, tiny unreadable text, and elements colliding. Run this **every time** after building a PPTX — even for single-slide decks.

```python
"""
Programmatic Layout QA for PPTX files.
Checks: Hard OOB, safe-zone margins, tiny text, real overlaps.
Filters out intentional text-on-shape layering (PptxGenJS pattern).
Exit code 0 = all clear, 1 = issues found.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pptx import Presentation
from pptx.util import Pt

PPTX_PATH = sys.argv[1] if len(sys.argv) > 1 else "output.pptx"
SAFE_MARGIN = 0.25           # inches from slide edge for content
SAFE_FOOTER = 0.08           # tighter allowance for footer-zone text
MIN_FONT_PT = 6              # minimum readable font size
OVERLAP_THRESHOLD = 0.30     # 30% of smaller shape's area

prs = Presentation(PPTX_PATH)
sw = prs.slide_width / 914400
sh = prs.slide_height / 914400
issues = []

for si, slide in enumerate(prs.slides, 1):
    shapes = []
    for shape in slide.shapes:
        l = shape.left/914400; t = shape.top/914400
        w = shape.width/914400; h = shape.height/914400
        txt = shape.text_frame.text.strip() if shape.has_text_frame else ''
        min_font = 999
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                for r in p.runs:
                    if r.font.size:
                        min_font = min(min_font, r.font.size / 12700)
        shapes.append({'l':l,'t':t,'w':w,'h':h,'r':l+w,'b':t+h,
                       'txt':txt,'name':shape.name,'font':min_font})

        # --- Check 1: Hard OOB (past slide edges) ---
        if l < -0.02 or t < -0.02 or l+w > sw+0.02 or t+h > sh+0.02:
            issues.append(f'S{si} HARD-OOB: "{shape.name}" bounds=[{l:.2f},{t:.2f},{l+w:.2f},{t+h:.2f}] slide=[{sw:.2f},{sh:.2f}] | "{txt[:40]}"')

        # --- Check 2: Safe-zone margin violations ---
        is_fullbleed = w > sw*0.9 or h > sh*0.9
        is_thin = w < 0.03 or h < 0.03
        if not is_fullbleed and not is_thin:
            is_footer = t > sh - 0.8 and h < 0.3
            max_b = sh - (SAFE_FOOTER if is_footer else SAFE_MARGIN)
            if l+w > sw - SAFE_MARGIN and w < sw*0.5:
                issues.append(f'S{si} RIGHT-MARGIN: "{shape.name}" right={l+w:.3f}" (max={sw-SAFE_MARGIN:.2f}")')
            if l < SAFE_MARGIN and w < sw*0.5:
                issues.append(f'S{si} LEFT-MARGIN: "{shape.name}" left={l:.3f}" (safe={SAFE_MARGIN}")')
            if t+h > max_b:
                issues.append(f'S{si} BOTTOM-MARGIN: "{shape.name}" bottom={t+h:.3f}" (max={max_b:.2f}") | "{txt[:40]}"')

        # --- Check 3: Tiny unreadable text ---
        if min_font < 999 and min_font < MIN_FONT_PT:
            issues.append(f'S{si} TINY-TEXT(<{MIN_FONT_PT}pt): "{shape.name}" font={min_font:.1f}pt | "{txt[:30]}"')

    # --- Check 4: Real overlaps (filter intentional text-on-shape layering) ---
    content = [s for s in shapes if s['w'] > 0.15 and s['h'] > 0.1 and s['w'] < sw*0.9]
    for i, a in enumerate(content):
        for j, b in enumerate(content):
            if j <= i: continue
            ox = max(0, min(a['r'],b['r'])-max(a['l'],b['l']))
            oy = max(0, min(a['b'],b['b'])-max(a['t'],b['t']))
            if ox < 0.1 or oy < 0.1: continue
            area = ox * oy
            smaller = min(a['w']*a['h'], b['w']*b['h'])
            if smaller <= 0 or area/smaller < OVERLAP_THRESHOLD: continue
            # Intentional: background shape (no text) with content on top
            if not a['txt'] or not b['txt']: continue
            # Intentional: same-y footer pair (left-aligned + right-aligned)
            if abs(a['t']-b['t']) < 0.05 and abs(a['h']-b['h']) < 0.05 and a['t'] > sh-1.0: continue
            issues.append(f'S{si} OVERLAP({area/smaller:.0%}): "{a["name"]}"("{a["txt"][:25]}") vs "{b["name"]}"("{b["txt"][:25]}")')

    # --- Summary: bottom-most elements for spatial awareness ---
    bots = sorted(shapes, key=lambda s: s['b'], reverse=True)[:3]
    print(f'Slide {si}: {len(slide.shapes)} shapes | Bottom: {", ".join(f"{s[\"name\"]}@{s[\"b\"]:.2f}" for s in bots)}')

print(f'\n{"="*50}')
if issues:
    print(f'{len(issues)} ISSUES FOUND:')
    for iss in issues:
        print(f'  - {iss}')
    sys.exit(1)
else:
    print('ALL CLEAR — no layout issues detected.')
    sys.exit(0)
```

**How to run:**
```bash
python qa_layout.py "path/to/output.pptx"
```

**What it catches:**

| Check | What | Threshold |
|-------|------|-----------|
| Hard OOB | Shapes past slide edges | > 0.02" past edge |
| Safe zone | Content too close to edges | < 0.25" margin (0.08" for footers) |
| Tiny text | Unreadable font sizes | < 6pt |
| Real overlaps | Two text elements colliding | > 30% of smaller shape's area |

**What it filters out (not bugs):**
- **Text-on-shape layering** — PptxGenJS pattern where an empty background shape has text/badges placed on top (100% overlap, one shape has no text → intentional)
- **Footer pairs** — Left-aligned source + right-aligned team label at the same y position
- **Full-bleed backgrounds** — Shapes covering > 90% of slide width/height
- **Thin decorative lines** — Shapes < 0.03" in either dimension

**If issues are found:** Fix the build script, rebuild, and re-run this check. Do NOT proceed to visual QA until this passes with zero issues. Common fixes:
- **OOB**: Reduce element heights/gaps, or move content up
- **Margin**: Push footers/content inward by adjusting y or h values
- **Overlap**: Redistribute elements across columns, reduce card heights, increase gaps
- **Tiny text**: Increase font size to at least 7pt (8pt preferred for body text)

### Stage 3: Visual QA

**Use subagents** — even for 2-3 slides. You've been staring at the code and will see what you expect, not what's there.

1. Convert slides to images:
   ```bash
   python scripts/office/soffice.py --headless --convert-to pdf output.pptx
   pdftoppm -jpeg -r 150 output.pdf slide
   ```

2. Inspect with subagent using this prompt:
   ```
   Visually inspect these slides. Assume there are issues — find them.

   Look for:
   - Overlapping elements (text through shapes, lines through words)
   - Text overflow or cut off at edges/box boundaries
   - Elements too close (< 0.3" gaps) or nearly touching
   - Uneven gaps (large empty area in one place, cramped in another)
   - Insufficient margin from slide edges (< 0.5")
   - Columns or elements not aligned consistently
   - Low-contrast text or icons against backgrounds
   - Text boxes too narrow causing excessive wrapping
   - Leftover placeholder content
   - Decorative elements positioned for single-line text but title wrapped to two lines

   For each slide, list issues or areas of concern, even if minor.

   Read and analyze these images:
   1. /path/to/slide-01.jpg (Expected: [brief description])
   2. /path/to/slide-02.jpg (Expected: [brief description])
   ```

### Verification Loop

1. Build PPTX → Content QA → **Programmatic Layout QA** → Visual QA
2. **List issues found** (if zero found, look again more critically)
3. Fix issues in the build script
4. **Rebuild and re-run all three QA stages** — one fix often creates another problem
5. Repeat until a full pass reveals no new issues across all three stages

**Do not declare success until you've completed at least one fix-and-verify cycle with zero issues across all stages.**

To re-render specific slides after fixes:
```bash
pdftoppm -jpeg -r 150 -f N -l N output.pdf slide-fixed
```

---

## Dependencies

### Python
```bash
pip install "markitdown[pptx]"   # Text extraction
pip install Pillow               # Thumbnail grids
pip install python-pptx          # Python creation engine
```

### Node.js
```bash
npm install -g pptxgenjs         # Primary creation engine
npm install -g react-icons react react-dom sharp  # Icon generation
```

### System
- **LibreOffice** (`soffice`) — PDF conversion for visual QA
- **Poppler** (`pdftoppm`) — PDF to individual slide images

---

## Gotchas & Troubleshooting

### 1. PptxGenJS Hex Colors — No # Prefix

```javascript
color: "FF0000"      // CORRECT
color: "#FF0000"     // WRONG — corrupts file
```

### 2. PptxGenJS 8-Char Hex Colors Corrupt Files

Never encode opacity in the color string. Use the `opacity` property instead.

```javascript
// WRONG — corrupts file
shadow: { color: "00000020" }

// CORRECT
shadow: { color: "000000", opacity: 0.12 }
```

### 3. PptxGenJS Object Mutation

PptxGenJS mutates option objects in-place (converting values to EMU). Sharing one object between multiple calls corrupts the second shape.

```javascript
// WRONG — second call gets already-converted values
const shadow = { type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 };
slide.addShape(pres.shapes.RECTANGLE, { shadow, ... });
slide.addShape(pres.shapes.RECTANGLE, { shadow, ... });

// CORRECT — factory function creates fresh object each time
const makeShadow = () => ({ type: "outer", blur: 6, offset: 2, color: "000000", opacity: 0.15 });
slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow(), ... });
slide.addShape(pres.shapes.RECTANGLE, { shadow: makeShadow(), ... });
```

### 4. Shadow Negative Offset Corruption

Negative `offset` values corrupt the .pptx file. To cast a shadow upward (e.g., on a footer bar), use `angle: 270` with a positive offset.

### 5. Unicode Bullet Double-Rendering

Never use "•" characters for bullets. PptxGenJS adds its own bullet, resulting in "••".

```javascript
// WRONG
slide.addText("• First item", { ... });

// CORRECT
slide.addText("First item", { bullet: true, ... });
```

### 6. ROUNDED_RECTANGLE with Accent Bars

Rectangular accent overlay bars don't cover rounded corners. Use `RECTANGLE` instead when adding accent bars.

### 7. breakLine Required for Multi-Line

Without `breakLine: true`, rich text array items render on the same line.

### 8. lineSpacing with Bullets

`lineSpacing` causes excessive gaps with bulleted lists. Use `paraSpaceAfter` instead.

### 9. python-pptx EMU Confusion

Always use helpers (`Inches()`, `Pt()`) instead of raw EMU values. Common mistake: using pixel values where EMU is expected.

```python
# WRONG — 100 EMU is microscopic
shape.left = 100

# CORRECT
shape.left = Inches(1)
```

### 10. python-pptx Gradient Fills Are Limited

python-pptx has basic gradient fill support (`fill.gradient()` + `gradient_stops`), but alpha/transparency on gradient stops requires XML manipulation via `lxml`. For complex gradients, pre-render as a PNG image.

### 10b. PptxGenJS Has No Gradient Fills

PptxGenJS does not support gradient fills on shapes (open GitHub issue #102). Workarounds:
- Pre-render gradient as PNG and use as background image
- Layer multiple thin semi-transparent rectangles to approximate a gradient
- Use python-pptx instead when gradients are critical

### 10c. PptxGenJS Inner Shadow Is Broken

`shadow.type: "inner"` does not render correctly (issue #1293). Only use `"outer"` shadows.

### 11. Fresh pptxgen Instance Per File

Don't reuse `new pptxgen()` objects across multiple files. Create a fresh instance for each presentation.

### 12. Font Availability

Presentations use system fonts. If a font isn't installed on the viewer's machine, PowerPoint substitutes a default. Stick to system-safe fonts (Arial, Calibri, Georgia, Times New Roman) for maximum compatibility. Custom fonts require embedding or font installation.

### 13. Large File Performance

- Optimize images before embedding (compress to 150-300 DPI for screen presentations)
- Use base64 for small icons, file paths for large images
- Limit to ~50 slides per file for responsive editing

### Troubleshooting Quick Reference

| Symptom | Cause | Fix |
|---------|-------|-----|
| File won't open | 8-char hex color or negative shadow offset | Use 6-char hex, positive offset |
| Double bullets | Unicode "•" + library bullet | Remove unicode, use `bullet: true` |
| Second shape looks wrong | Object mutation from first call | Use factory function for shared options |
| Text not aligned with shapes | Text box default margin | Set `margin: 0` |
| Rounded corners visible behind accent bar | ROUNDED_RECTANGLE with rectangular overlay | Use RECTANGLE instead |
| python-pptx shape is invisible | Used raw number instead of EMU | Use `Inches()` or `Pt()` |
| Font looks different on other machine | Font not installed | Use system-safe fonts |
| Inner shadow not rendering | PptxGenJS inner shadow bug | Use only `type: "outer"` |
| Gradient fill not working (pptxgenjs) | Not supported | Pre-render gradient as PNG image |
| Shape loop makes file huge | Too many shapes (patterns/grids) | Pre-render pattern as single PNG |
| Text barely visible on dark slide | Using pure white (#FFFFFF) | Use off-white (#F5F5F7) for softer contrast |
| Slide feels cluttered | Too much content, no breathing room | Remove content until 40%+ is empty space |
