---
name: Miro MCP Integration
description: Miro MCP (OAuth 2.1), 13 tools, 2 boards (Claude Code Deployment 16-diagram 7x3 grid + CPQ SMC RMC 17 artifacts), artifacts at AI\Miro\, no image upload (2026-04-30)
type: project
originSessionId: 9accd003-3d3b-4227-b58a-870575044110
---
## Project Directory
`<USER_HOME>/OneDrive - <ORG>\Claude code\MCP\Miro MCP\`

## Connection Status
- **MCP Server**: Official Miro MCP at `https://mcp.miro.com/` (HTTP transport)
- **Auth**: OAuth 2.1 — connected and authenticated as `<USER>@<ORG_DOMAIN>`
- **Enabled by**: Laura Williams (laura.williams@<ORG_PARENT>.com) on 2026-04-13 via <ORG_PARENT> admin (Miro Enterprise)
- **Config**: Already in Claude Code local MCP config (`claude mcp add --transport http miro https://mcp.miro.com`)
- **Status check**: `claude mcp list` — should show `miro: https://mcp.miro.com (HTTP) - Connected`

## Available MCP Tools (13)

### Content Creation (5)
| Tool | Purpose |
|------|---------|
| `diagram_get_dsl` | Get DSL format spec before creating diagrams |
| `diagram_create` | Create flowcharts, UML class/sequence, ERD from DSL |
| `doc_create` | Create markdown documents on boards |
| `table_create` | Create tables with text and select columns |
| `table_sync_rows` | Add or update table rows |

### Content Reading (6)
| Tool | Purpose |
|------|---------|
| `context_explore` | Discover frames, docs, prototypes, tables, diagrams on a board |
| `context_get` | Extract detailed text/content from specific board items |
| `board_list_items` | List items with filtering by type or container |
| `table_list_rows` | Read table data with column-based filtering |
| `image_get_data` | Get image content from boards |
| `image_get_url` | Get download URL for an image |

### Document Editing (2)
| Tool | Purpose |
|------|---------|
| `doc_get` | Read document content and version |
| `doc_update` | Edit document using find-and-replace |

## Diagram Types Supported
- **flowchart** — process flows, workflows, decision trees
- **uml_class** — class structures, inheritance
- **uml_sequence** — component interactions over time
- **entity_relationship** — database schemas, data models

## Board Coordinate System
- Center at (0, 0), positive X = right, positive Y = down
- Spacing: diagrams 2000-3000 apart, docs 500-1000, tables 1500-2000
- Use `moveToWidget` or `focusWidget` URL params to target specific items

## Repos Cloned
1. **app-examples**: `MCP\Miro MCP\app-examples\` — 31 example apps (OAuth, webhooks, AI, CSV, Python Flask, Next.js)
2. **miro-ai**: `MCP\Miro MCP\miro-ai\` — Official Miro AI developer tools
   - 4 skills: miro-mcp, miro-platform, miro-code-review, miro-spec-guide
   - 6 Claude Code plugins: miro, miro-tasks, miro-solutions, miro-research, miro-review, miro-spec
   - 5 slash commands: /browse, /diagram, /doc, /table, /summarize

## Key Learnings
- "Board access denied" means the authenticated account lacks access to that specific board, not an auth failure
- Enterprise Miro requires admin to enable MCP (Laura Williams did this)
- Don't add `https://mcp.miro.com/` manually if a plugin already manages the connection — causes duplicate tools
- doc_create without a miro_url creates a new board
- OAuth session is per-installation — one MCP connection per client

## Miro Boards
- **Claude Code Deployment**: `https://miro.com/app/board/uXjVHajHEbE=/`
  - **Presentation-ready grid** (reorganized 2026-04-30): 7 columns x 3 rows = 16 diagrams
  - **Columns** (left→right): Phase 1 (x=-5000), Phase 2 (x=500), Phase 3 (x=6000), Phase 4 (x=11500), Infrastructure (x=17000), Phase 5 (x=22500), PBI Mockups (x=28000)
  - **Rows** (top→bottom): Row 1 Architecture (y=-13844), Row 2 Flow Diagrams (y=-11279), Row 3 Drill-down Detail (y=-8713)
  - Row 1: 7 architecture diagrams (CLI, Gateway, ETL, Security, Resource Landscape, Content Logging, PBI Content Analysis wireframe)
  - Row 2: 7 flow diagrams (CLI Data Flow, Gateway Data Flow, ETL Data Flow, Security Data Flow, Provisioning Flow, Content Process Flow, PBI Content Alerts wireframe)
  - Row 3: 2 diagrams (Phase 5 Content Data Flow Detail, PBI README Safety wireframe)
  - All v2 content: 31 users, 19 tables, 6h ETL, PBI LIVE 10 pages, content logging, Haiku safety
  - 3 black sticky notes at x=-6055 mark row positions (user-placed anchors)
  - PBI mockup PNGs extracted to `Usage Tracking/pbi_mockups/` for optional drag-drop replacement
  - Old diagrams (y=-5000 to y=6000) preserved but superseded by grid layout
  - Color palette: `#fff6b6 #c6dcff #adf0c7 #ccf4ff #dedaff #ffc6c6 #f8d3af #ffd8f4 #c3faf5 #dbfaad #e7e7e7` (11 colors, indices 0-10)
  - Each diagram uses clusters for Azure boundaries (subscription, RG, service groups)
  - **Must click "Apply to canvas"** on each diagram to convert from draft to permanent shapes
- **CPQ SMC RMC Integration**: `https://miro.com/app/board/o9J_lAknUAk=/`
  - 17 artifacts: 5 docs, 6 flowcharts, 2 ER diagrams, 4 tables
  - 8 logical canvases in walkthrough sequence: Intro → Current State → Problem → Landscape → Architecture → Data Flow → Data Models → Implementation
  - All items at y=-800, x=80000 to 128947 (horizontal layout)
  - Pending: create frames to group related items; items currently free-floating

## Artifacts Folder
- **Location**: `<USER_HOME>/OneDrive - <ORG>\AI\Miro\`
- **Structure**: One subfolder per board/project → `architecture/` (Azure-icon PNGs), `dataflow-d2/` (D2 sources), `dataflow-svg/` (rendered SVGs)
- **Claude Code Deployment**: 5 PNGs + 5 .d2 + 5 .svg = 15 files
- See [reference_miro_artifacts.md](reference_miro_artifacts.md) for full tree

## Key Limitations
- **No image upload via MCP** — `image_get_data` and `image_get_url` are read-only. To get Azure-icon PNGs onto boards, must drag-drop from local `AI\Miro\` folder.
- **diagram_create only supports 4 flowchart shapes** (process, decision, data, terminator) — no custom icons, no Azure icon library access via DSL.
- **Diagrams require "Apply to canvas"** — API-created diagrams land in draft state; user must click to commit.

## Planned: Custom Miro Skill
- Wraps 13 MCP tools for <ORG>-specific workflows
- Architecture diagrams, project boards, meeting notes, sprint planning
- Skill file target: `~/.claude/commands/miro.md`
