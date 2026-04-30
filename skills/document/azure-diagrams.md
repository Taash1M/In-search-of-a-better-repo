---
name: azure-diagrams
description: "Generate publication-quality Azure architecture, data flow, and resource landscape diagrams using actual Azure SVG icons and python-pptx/Pillow. Sub-skill for docx-beautify and powerpoint-create. Use when creating cloud architecture diagrams, data flow diagrams, Azure resource landscapes, authentication flows, or sequence-style interaction diagrams. Trigger on: 'architecture diagram', 'data flow', 'Azure diagram', 'resource landscape', 'service map'."
---

# Azure Architecture & Data Flow Diagram Skill

> Sub-skill called by docx-beautify and pptx-beautify. Generates publication-quality architecture, data flow, and resource landscape diagrams using actual Azure SVG icons.

---

## When to Use This Skill

Use this skill **automatically** whenever a document or presentation needs:
- Cloud architecture diagrams (multi-service, multi-agent, infrastructure)
- Data flow / pipeline diagrams (sequential stages with arrows)
- Azure resource landscape diagrams (subscription → resource group → services)
- Authentication / security flow diagrams
- Sequence-style interaction diagrams

**Do not ask the user** — if the content calls for a diagram, generate one. FYI the user as you go.

---

## Module Location

```
<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification\azure_diagrams.py
```

**Import pattern:**
```python
import sys
sys.path.insert(0, r"<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification")
from azure_diagrams import (
    quick_architecture, quick_flow, quick_landscape,
    generate_architecture_diagram, generate_data_flow_diagram,
    generate_resource_landscape, generate_sequence_flow,
    generate_for_docx, generate_for_pptx,
    Node, Connection, Boundary, DiagramConfig,
    load_icon, COLORS, OUTPUT_PRESETS,
)
```

The module handles cairosvg bootstrap automatically — no manual DLL path setup needed by callers.

---

## Quick API (Preferred — Pass Dicts)

### `quick_architecture(services, connections, output_path, title, output_preset, boundaries)`

```python
quick_architecture(
    services=[
        {"label": "App Service", "icon": "app_services", "x": 2, "y": 3, "sublabel": "FastAPI"},
        {"label": "Azure OpenAI", "icon": "azure_openai", "x": 5, "y": 3, "sublabel": "Sonnet"},
        {"label": "Cosmos DB", "icon": "cosmos_db", "x": 8, "y": 3, "sublabel": "Sessions"},
    ],
    connections=[
        {"from_node": "App Service", "to_node": "Azure OpenAI", "label": "REST API"},
        {"from_node": "App Service", "to_node": "Cosmos DB", "label": "Session Store"},
    ],
    boundaries=[
        {"label": "Azure Subscription", "x": 0.5, "y": 1.5, "width": 9, "height": 3.5,
         "style": "dashed", "fill_type": "subscription"},
    ],
    output_path="architecture.png",
    title="System Architecture",
    output_preset="pptx",  # or "docx_portrait", "docx_landscape", "pptx_half", "standalone"
)
```

### `quick_flow(stages, output_path, title, output_preset, direction, connections)`

```python
quick_flow(
    stages=[
        {"label": "SharePoint", "icon": "static_apps", "sublabel": "UI"},
        {"label": "FastAPI", "icon": "app_services", "sublabel": "Backend"},
        {"label": "Azure OpenAI", "icon": "azure_openai", "sublabel": "LLM"},
        {"label": "Cosmos DB", "icon": "cosmos_db", "sublabel": "Sessions"},
    ],
    output_path="data_flow.png",
    title="End-to-End Data Flow",
    output_preset="docx_landscape",
    direction="horizontal",  # or "vertical"
)
```

Auto-connects stages in order if `connections` is not provided.

### `quick_landscape(subscriptions, output_path, title, output_preset)`

```python
quick_landscape(
    subscriptions=[{
        "name": "Fluke AI ML Technology",
        "resource_groups": [{
            "name": "rg-ai-bi-tool-dev",
            "services": [
                {"label": "App Service", "icon": "app_services", "sublabel": "FastAPI Backend"},
                {"label": "Azure OpenAI", "icon": "azure_openai", "sublabel": "Sonnet + Haiku"},
                {"label": "Cosmos DB", "icon": "cosmos_db", "sublabel": "Session Store"},
                {"label": "Key Vault", "icon": "key_vaults", "sublabel": "Secrets"},
                {"label": "Container Registry", "icon": "container_registries", "sublabel": "Docker"},
                {"label": "App Insights", "icon": "application_insights", "sublabel": "Monitoring"},
            ]
        }]
    }],
    output_path="landscape.png",
    title="Azure Resource Landscape",
    output_preset="docx_landscape",
)
```

Auto-layouts services in a grid within nested subscription/RG boundaries.

---

## Full API (Dataclass-Based)

For complex diagrams requiring fine-grained control:

```python
from azure_diagrams import Node, Connection, Boundary, DiagramConfig

nodes = [
    Node(label="App Service", icon="app_services", x=2, y=3, sublabel="FastAPI"),
    Node(label="LiteLLM", icon="", x=5, y=3, style="hexagon", color="#ED7D31"),
    Node(label="Azure OpenAI", icon="azure_openai", x=8, y=3),
]

connections = [
    Connection(from_node="App Service", to_node="LiteLLM", label="OpenAI Format", style="solid"),
    Connection(from_node="LiteLLM", to_node="Azure OpenAI", label="Anthropic Format", style="dashed"),
]

boundaries = [
    Boundary(label="Azure Subscription", x=0.5, y=1, width=9.5, height=4,
             style="solid", fill_type="subscription", nest_level=0),
    Boundary(label="rg-production", x=1, y=1.5, width=8.5, height=3,
             style="dashed", fill_type="resource_group", nest_level=1),
]

config = DiagramConfig(
    output_preset="pptx",
    title="LLM Gateway Architecture",
    subtitle="Protocol Translation Layer",
    show_title=True,
)

generate_architecture_diagram(nodes, connections, "gateway_arch.png", boundaries, config)
```

---

## Integration with Beautification Skills

### From docx_beautify scripts:

```python
from azure_diagrams import generate_for_docx, generate_architecture_diagram
from docx_beautify import create_document
from docx.shared import Inches

doc = create_document(preset="executive")

# Generate diagram sized for portrait DOCX
img_path = generate_for_docx(
    generate_architecture_diagram,
    output_path="temp_arch.png",
    landscape=False,  # or True for landscape sections
    nodes=[...],
    connections=[...],
    boundaries=[...],
)

# Embed in document
doc.add_picture(img_path, width=Inches(6.0))
doc.add_paragraph("Figure 1: System Architecture", style="Caption")
```

### From pptx_beautify scripts:

```python
from azure_diagrams import generate_for_pptx, generate_architecture_diagram
from pptx_beautify import add_image_slide

# Generate diagram sized for full slide
img_path = generate_for_pptx(
    generate_architecture_diagram,
    output_path="temp_arch.png",
    half_slide=False,  # True for side-by-side layouts
    nodes=[...],
    connections=[...],
)

# Embed in presentation
add_image_slide(prs, "System Architecture", img_path, layout="center")
```

---

## Output Presets

| Preset | Figure Size | DPI | Icon Size | Use Case |
|--------|-------------|-----|-----------|----------|
| `docx_portrait` | 6.5" × 4.5" | 200 | 48px | Portrait DOCX pages |
| `docx_landscape` | 9.5" × 5.5" | 200 | 56px | Landscape DOCX pages |
| `pptx` | 11.5" × 5.8" | 200 | 56px | Full widescreen slide |
| `pptx_half` | 5.5" × 5.0" | 200 | 40px | Half-slide (side-by-side) |
| `standalone` | 12" × 8" | 200 | 64px | Large standalone image |

---

## Node Styles

| Style | Description | When to Use |
|-------|-------------|-------------|
| `"icon"` (default) | Azure SVG icon with label below | Azure services with official icons |
| `"box"` | Colored rounded rectangle with text | Custom services, external systems |
| `"hexagon"` | Hexagonal shape | Middleware, proxies, translators |
| `"pill"` | Capsule/pill shape | Actions, steps, processes |
| `"circle"` | Circular node | Endpoints, users, abstract concepts |

---

## Icon Registry (Common Services)

### AI + Machine Learning
| Key | Service |
|-----|---------|
| `azure_openai` | Azure OpenAI |
| `ai_services` | Azure AI Services |
| `cognitive_search` / `ai_search` | Azure AI Search |
| `bot_services` | Bot Services |
| `machine_learning` | Machine Learning |

### Compute
| Key | Service |
|-----|---------|
| `app_services` | App Services |
| `function_apps` | Function Apps |
| `virtual_machine` | Virtual Machine |
| `kubernetes` | AKS |

### Containers
| Key | Service |
|-----|---------|
| `container_registries` | Container Registries |
| `container_instances` | Container Instances |
| `container_apps` | Container Apps |

### Databases
| Key | Service |
|-----|---------|
| `cosmos_db` | Cosmos DB |
| `sql_database` | SQL Database |
| `cache_redis` | Azure Cache for Redis |
| `mysql` | Azure Database for MySQL |
| `postgresql` | Azure Database for PostgreSQL |

### Identity
| Key | Service |
|-----|---------|
| `users` | Users |
| `entra_connect` | Entra Connect |
| `managed_identities` | Managed Identities |
| `app_registrations` | App Registrations |

### Integration
| Key | Service |
|-----|---------|
| `service_bus` | Service Bus |
| `logic_apps` | Logic Apps |
| `event_grid` | Event Grid |
| `app_configuration` | App Configuration |

### Monitoring & Security
| Key | Service |
|-----|---------|
| `application_insights` | Application Insights |
| `key_vaults` | Key Vault |
| `log_analytics` | Log Analytics |
| `sentinel` | Sentinel |

### Networking
| Key | Service |
|-----|---------|
| `virtual_networks` | Virtual Networks |
| `load_balancers` | Load Balancers |
| `front_door` | Front Door |
| `firewall` | Azure Firewall |
| `waf` | WAF |
| `nsg` | Network Security Group |

### Storage & Analytics
| Key | Service |
|-----|---------|
| `storage_accounts` | Storage Accounts |
| `databricks` | Databricks |
| `synapse` | Synapse Analytics |
| `power_bi` | Power BI Embedded |
| `event_hubs` | Event Hubs |

### Other
| Key | Service |
|-----|---------|
| `resource_groups` | Resource Groups |
| `subscriptions` | Subscriptions |
| `api_management` | API Management |
| `app_service_plan` | App Service Plans |
| `cdn_profiles` | CDN Profiles |
| `static_apps` | Static Web Apps |

For the full registry, call `list_icons()` or check `ICON_REGISTRY` in the module.

---

## Connection Styles

| Property | Options | Default |
|----------|---------|---------|
| `style` | `"solid"`, `"dashed"`, `"dotted"` | `"solid"` |
| `arrow_style` | `"-\|>"`, `"->"`, `"<\|-\|>"`, `"fancy"` | `"-\|>"` |
| `bidirectional` | `True` / `False` | `False` |
| `curve` | Float (-0.5 to 0.5, 0=straight) | `0.0` |
| `color` | Hex color | `#555555` |

---

## Boundary Box Types

| `fill_type` | Color | Use Case |
|-------------|-------|----------|
| `subscription` | Light blue | Azure subscriptions |
| `resource_group` | Light blue (darker) | Resource groups |
| `vnet` | Light green | Virtual networks |
| `agent_group` | Light gold | Agent groupings |
| `security` | Light red | Security boundaries |
| `data` | Light purple | Data zones |
| `user` | Light orange | User groups |
| `default` | Light gray | Generic grouping |

---

## Semantic Service Categories (v1.2 — from Cocoon-AI evaluation)

When no explicit `color` is set on a node, the module auto-assigns a category color based on the icon key. This makes diagrams instantly scannable — databases are always violet, security is always rose, etc.

| Category | Fill (Light) | Stroke | Icon Keys |
|----------|-------------|--------|-----------|
| **Compute** | `#E8F5E9` | `#2E7D32` | `app_services`, `function_apps`, `virtual_machine`, `kubernetes`, `container_apps`, `container_instances`, `app_service_plan` |
| **Data/Storage** | `#EDE7F6` | `#5E35B1` | `cosmos_db`, `sql_database`, `cache_redis`, `mysql`, `postgresql`, `storage_accounts`, `databricks`, `synapse`, `event_hubs` |
| **AI/ML** | `#E0F7FA` | `#00838F` | `azure_openai`, `ai_services`, `cognitive_search`, `ai_search`, `bot_services`, `machine_learning` |
| **Security/Identity** | `#FCE4EC` | `#C62828` | `key_vaults`, `sentinel`, `firewall`, `waf`, `nsg`, `users`, `entra_connect`, `managed_identities`, `app_registrations` |
| **Networking** | `#FFF3E0` | `#E65100` | `virtual_networks`, `load_balancers`, `front_door`, `cdn_profiles` |
| **Integration** | `#E3F2FD` | `#1565C0` | `service_bus`, `logic_apps`, `event_grid`, `app_configuration`, `api_management` |
| **Monitoring** | `#F3E5F5` | `#6A1B9A` | `application_insights`, `log_analytics` |
| **Platform** | `#ECEFF1` | `#455A64` | `resource_groups`, `subscriptions`, `static_apps`, `container_registries`, `power_bi` |

**How it works:** If a node uses `icon="cosmos_db"` and no explicit `color`, the node box/fallback will use the Data/Storage palette (violet fill + stroke). If you set an explicit `color`, that overrides the category color.

**Cross-skill consistency:** These same category colors are used in docx-beautify Mermaid `classDef` and D2 `style` blocks, and in powerpoint-create's dark architecture slide pattern. This ensures diagrams look consistent across all output formats.

---

## Fluke Brand Colors

Available via `COLORS` dict:

| Key | Hex | Use |
|-----|-----|-----|
| `primary` | `#1E2761` | Titles, main boundaries |
| `secondary` | `#4472C4` | Secondary elements, links |
| `accent` | `#ED7D31` | Highlights, callouts |
| `success` | `#70AD47` | Success states, approvals |
| `warning` | `#FFC220` | Warning states |
| `danger` | `#C00000` | Error states, critical |
| `info` | `#17A2B8` | Info elements |

---

## Sizing Guidelines

### DOCX Portrait
- Max usable width: ~6.1" (with 1" margins)
- Recommended: `width_inches=6.0` for full-width diagrams
- Use `output_preset="docx_portrait"` — produces 6.5" × 4.5" figures
- Keep to 4-6 nodes for readability

### DOCX Landscape
- Max usable width: ~9.0" (with 1" margins)
- Recommended: `width_inches=8.5` for full-width diagrams
- Use `output_preset="docx_landscape"` — produces 9.5" × 5.5" figures
- Ideal for data flow diagrams and resource landscapes

### PPTX Widescreen (16:9)
- Slide dimensions: 13.333" × 7.5"
- Content area (after title + margins): ~11" × 5.5"
- Use `output_preset="pptx"` — produces 11.5" × 5.8" figures
- Full slide diagrams: 8-12 nodes comfortable

### PPTX Half-Slide
- For two-column layouts or side-by-side diagrams
- Use `output_preset="pptx_half"` — produces 5.5" × 5.0" figures
- Keep to 3-5 nodes

---

## Mandatory Quality Gate (NEVER SKIP)

**Every diagram must pass this checklist BEFORE embedding into any DOCX or PPTX.** If any check fails, fix and regenerate. Repeat until all pass.

### Pre-Generation Checks
1. **Verify all icons exist** — before generating, call `load_icon(key)` for every icon key you plan to use. If it returns `None`, the node will render as a fallback colored box with initials instead of the real Azure icon. Fix by using a registered key from the Icon Registry tables above, or add the missing icon to `ICON_REGISTRY` in the module.
2. **Unique labels** — every node label within a single diagram must be unique. If you need multiple Databricks nodes, qualify them: "Bronze Layer", "Silver Layer", "Gold Layer" — not three nodes all labeled "Databricks".
3. **Short labels** — keep node labels ≤15 characters. Use `sublabel` for additional detail. Long labels cause text overlap.

### Post-Generation Checks (inspect the PNG)
4. **No text overlap** — read the generated PNG image and verify that no label, sublabel, or connection label overlaps with any other text or icon. If overlap exists, increase node spacing or shorten labels.
5. **No distortion/squashing** — icons should appear square (not stretched). Boundaries should have reasonable proportions. If the diagram looks squashed, check that `set_aspect("equal")` is active and adjust the x/y coordinate ranges.
6. **No arrow/icon collision** — arrows should not pass through icons or obscure labels. If they do, increase `shrinkA`/`shrinkB` (≥30), add `curve` offset to separate parallel arrows, or reposition nodes.
7. **Proper sizing for target** — diagram should fill the content area without excessive whitespace. Use the correct `output_preset` for the target format.

### Minimum Spacing Rules
| Preset | Min horizontal spacing | Min vertical spacing |
|--------|----------------------|---------------------|
| `docx_portrait` | 2.6 units | 2.0 units |
| `docx_landscape` | 2.8 units | 2.0 units |
| `pptx` | 3.0 units | 2.2 units |
| `pptx_half` | 2.2 units | 1.8 units |
| `standalone` | 3.0 units | 2.5 units |

### Validation Loop
```
generate diagram PNG
read/inspect the PNG image
while any quality issue found:
    fix spacing / labels / icons / positioning
    regenerate diagram PNG
    re-inspect
embed into document
```

**This quality gate applies to ALL callers**: docx-beautify, powerpoint-create, ai-ucb-docs, and any future skill that generates diagrams.

### Troubleshooting Decision Tree

```
Diagram looks wrong?
├─ Icons missing/fallback boxes → Pre-validate icon keys (G9), check ICON_REGISTRY
├─ Text overlapping → Increase node spacing (min spacing table above), shorten labels to ≤15 chars
├─ Arrows through icons → Increase shrinkA/shrinkB ≥30, add curve offset
├─ Diagram too small/large → Wrong output_preset — match to target format (G1)
└─ Colors inconsistent → Use semantic service categories — auto-color by icon key
```

---

## Gotchas & Rules

### NEVER List (Quick Reference)
- **NEVER** hardcode `figsize` — always use `output_preset`
- **NEVER** embed a diagram without visually inspecting the PNG first
- **NEVER** use duplicate node labels in the same diagram
- **NEVER** skip the Quality Gate checks — even for "quick" diagrams
- **NEVER** use icon keys without pre-validating against `ICON_REGISTRY`
- **NEVER** exceed 15 characters in node labels — use `sublabel` for details

### G1: Always use output_preset for sizing
Never hardcode `figsize` — always use the preset system so diagrams fit their target format.

### G2: Node positioning is in diagram units (not inches)
Coordinates are abstract units. The figure auto-scales. Typical range: x=0-10, y=0-6.

### G3: Connection labels need space
If arrows are close together, offset labels with the `curve` parameter or adjust node positions.

### G4: Icon fallback
If an icon isn't found, the module renders a colored box with initials. Check `list_icons()` to verify availability. **Always pre-check icons before generating** — see Quality Gate above.

### G5: cairosvg bootstrap is automatic
The module handles DLL path setup on import. If you see "cairosvg not available" warnings, check that `<USER_HOME>/tools\cairo-dlls\` exists with the MSYS2 64-bit DLLs.

### G6: Clean up temp files
When generating diagrams for embedding in DOCX/PPTX, use `tempfile.mktemp(suffix='.png')` and delete after embedding.

### G7: Boundary nest_level controls z-order
Outer boundaries (subscription) should have `nest_level=0`, inner (RG) should have `nest_level=1`, etc.

### G8: For non-Azure services, use style="box" or style="hexagon"
DuckDB, Plotly, custom services — use box/hexagon/pill styles with a custom `color` instead of an icon.

### G9: Always pre-validate icon keys
Before calling `quick_architecture` or `quick_flow`, verify every `icon` value is either a valid key in `ICON_REGISTRY` or empty (for box/pill/hexagon styles). Missing keys produce fallback boxes that look unprofessional.

### G10: Read the generated PNG before embedding
After generating any diagram, use the Read tool to visually inspect the PNG. Check for overlap, missing icons, distortion. Fix and regenerate if needed. **Never embed a diagram you haven't inspected.**

---

## Dependencies

```
pip install matplotlib Pillow cairosvg cairocffi
```

Plus MSYS2 64-bit cairo DLLs at `<USER_HOME>/tools\cairo-dlls\` (38 DLLs from MSYS2 mingw64 packages).

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-04-06 | Initial release — icon registry, 4 diagram types, 5 output presets, docx/pptx integration |
| 1.1.0 | 2026-04-06 | Added `data_factory`/`adf`, `oracle_database` icons. Fixed text overlap (spacing 2.0→2.6, label font reduced, arrow shrink 25→30). Added mandatory Quality Gate with pre/post-generation checks (G9, G10). |
| 1.2.0 | 2026-04-16 | Added semantic service categories (8 categories, auto-color by icon key). Sourced from Cocoon-AI architecture-diagram-generator evaluation. Cross-skill color consistency with docx-beautify and powerpoint-create. |
| 1.2.1 | 2026-04-16 | Added troubleshooting decision tree and NEVER quick-reference list. Skill-judge fixes for A+ rating. |
