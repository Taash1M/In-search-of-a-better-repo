---
name: Diagram visual quality standard
description: Consulting-grade visual quality rules for all dataflow/process/tech stack diagrams — Veritas-derived, proven patterns with specific implementations
type: feedback
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---
All dataflow, process flow, and tech stack diagrams must meet these quality standards. Derived from Veritas Suite deck analysis and proven on Leadership Forum sample (2026-04-14).

**Why:** Early diagram outputs used all-rectangle nodes, thick colorful arrows, and cramped layouts that looked amateur. User established the Veritas Suite deck (44 slides, dark near-black theme, hexagonal nodes, layered zones) as the quality bar for professional diagrams.

**How to apply:**

### Mandatory Rules
1. **Node shape variety** — hexagons for agents/autonomous components, diamonds for decisions, cylinders for data stores, rounded rects for processes. Never all rectangles.
2. **Connection line discipline** — thin (1-1.5px), single muted color (#666666 or #888888), small arrowheads. Max 2 line colors per diagram.
3. **Color restraint** — max 3 accent colors per diagram + neutrals. Light fills (#E8xxxx) with dark borders. Never dark fill + dark text.
4. **Whitespace** — 60-70% content fill ratio. If >75% is shapes/lines, too dense.
5. **Layered zones** — multi-tier systems MUST use container nesting with distinct fill colors per zone. Zone labels 14pt+ bold.

### Proven Reusable Patterns (python-pptx)
- **Icon strip with bracket connectors** — colored OVAL circles, horizontal bracket bar + vertical drop lines, FLOWCHART_EXTRACT triangles rotated 90° as arrowheads. For tech stacks, toolchains, methodology stages (4-8 items).
- **Numbered vertical timeline** — navy OVAL circles with white numbers (1,2,3), gray RECTANGLE vertical connecting line drawn first (behind circles), title + description text to right. For delivery models, step sequences, callout panels.
- **Hierarchy tags** — ROUNDED_RECTANGLE items with distinct border colors per level, indented at each tier. For work item decomposition (Agent → Skill → Tool → Integration).

### Proven Reusable Patterns (Mermaid/D2 for DOCX)
- **Icon strip** → Mermaid `flowchart LR` with emoji-prefixed labels and `classDef` per node
- **Vertical timeline** → D2 `direction: down` with numbered containers and transparent child descriptions
- **Hierarchy tree** → Mermaid `flowchart TD` with distinct `classDef` per level, gray leaf nodes

### Reference Files
- Sample slide: `Leadership Forum/sample_veritas_slide18.pptx`
- Build script: `Leadership Forum/sample_slide18_adaptation.py`
- Source reference: `Presentation Beautification/U examples/veritassuite_pVrple.pptx` (slide 18)
- Skills updated: `powerpoint-create.md` (Diagram Visual Quality Standards section), `docx-beautify.md` (Proven Patterns section)

### Two Design Systems (2026-04-21)
These rules apply to BOTH systems. The visual execution differs:
1. **Bold Signal Light** (dark/navy theme) — proven on Leadership Forum deck. Navy #003366 backgrounds, Fluke Yellow #FFC000 accents, Arial Black headers. Use for: techno-functional audiences, internal leadership.
2. **Veritas Clean** (white/minimal theme) — proven on AI Next Steps v3. White backgrounds, large black titles, thin borders, monochrome + blue/gold. Use for: C-Suite, external stakeholders, strategy decks. Reference: `AI\Plan\build_next_steps_v3.py`.
