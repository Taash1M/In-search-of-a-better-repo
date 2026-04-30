---
name: Miro MCP Integration
description: Miro MCP server connected to <USER>@<ORG_DOMAIN>, official miro-ai repo cloned, 13 tools available, custom skill planned, project folder at Claude code\MCP\Miro MCP
type: project
originSessionId: 9accd003-3d3b-4227-b58a-870575044110
---
## Project Directory
`<USER_HOME>/OneDrive - <ORG>\Claude code\MCP\Miro MCP\`

## Connection Status
- **MCP Server**: Official Miro MCP at `https://mcp.miro.com/` (HTTP transport)
- **Auth**: OAuth 2.1 — connected and authenticated as `<USER>@<ORG_DOMAIN>`
- **Enabled by**: Laura Williams (laura.williams@<ORG_DOMAIN>) on 2026-04-13 via Fortive admin (Miro Enterprise)
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
  - 15 native flowchart diagrams (5 detailed arch at y=-5000, 5 simple arch at y=0, 5 data flows at y=3000)
  - Phases on x-axis: P1 CLI (x=0), P2 Gateway (x=5500), P3 ETL (x=11000), P4 Security (x=16500), Infra (x=22000)
  - Color coding: pink=users, green=compute, purple=storage, red=security, orange=orchestration, blue=AI, teal=deployments, yellow=planned, gray=containers
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
- Wraps 13 MCP tools for Fluke-specific workflows
- Architecture diagrams, project boards, meeting notes, sprint planning
- Skill file target: `~/.claude/commands/miro.md`
