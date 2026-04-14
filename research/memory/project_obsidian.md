---
name: Obsidian SecondBrain
description: Obsidian vault for Second Brain knowledge management, PARA method, OneDrive-synced, MCPVault MCP server configured
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
# Obsidian Second Brain

## Location
- **Vault**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Obsidian`
- **Obsidian app**: `C:\Program Files\Obsidian\Obsidian.exe`
- **Setup script**: `C:\Users\tmanyang\OneDrive - Fortive\AI\AI BI Tool\obsidian_setup.py`
- **Sync**: OneDrive (automatic)

## Setup Status
- **Date**: 2026-04-11
- **Status**: Fully validated and operational
- **Vault structure**: Complete (PARA method: 0-Inbox, 1-Projects, 2-Areas, 3-Resources, 4-Archive)
- **Templates**: 7 created (Daily, Project, Meeting, Fleeting, Literature, Permanent, Weekly Review)
- **Obsidian config**: `.obsidian/` pre-configured (app.json, appearance.json, core/community plugins)
- **Home dashboard**: Home.md with Dataview queries
- **Obsidian app**: Installed at `C:\Program Files\Obsidian\Obsidian.exe`
- **MCP server**: MCPVault v0.11.0 configured in `~/.claude/.mcp.json`

## MCP Server (MCPVault)
- **Package**: `@bitbonsai/mcpvault@latest` (v0.11.0)
- **Config**: `C:\Users\adm-tmanyang\.claude\.mcp.json` → `obsidian` entry
- **Mode**: Direct file access (no Obsidian app needed)
- **Security**: Path traversal protection, symlink blocking, `.obsidian`/`.git` auto-excluded
- **File types**: `.md`, `.markdown`, `.txt`, `.base`, `.canvas`
- **Tools**: vault stats, note read/write/search, tag listing, frontmatter management
- **Validated 2026-04-12**: vault path confirmed, `npx` process starts cleanly with no errors. If MCP tools don't appear in session, restart Claude Code — servers connect at startup.

## Community Plugins (13 installed)
1. Templater (templater-obsidian) -- advanced templates
2. Dataview (dataview) -- database queries
3. Calendar (calendar) -- daily notes calendar
4. Periodic Notes (periodic-notes) -- daily/weekly/monthly
5. QuickAdd (quickadd) -- rapid capture
6. Excalidraw (obsidian-excalidraw-plugin) -- visual thinking
7. Tasks (obsidian-tasks-plugin) -- task management
8. Kanban (obsidian-kanban) -- project boards
9. Obsidian Git (obsidian-git) -- version control
10. Omnisearch (omnisearch) -- full-text search
11. Obsidian Importer (obsidian-importer) -- import from other tools
12. Make.md (make-md) -- enhanced UI
13. Natural Language Dates (nldates-obsidian) -- date parsing

## Method
- **PARA** (Projects, Areas, Resources, Archive) for folder organization
- **Zettelkasten** for atomic notes and aggressive linking
- **Maps of Content** emerge naturally as the vault grows
- Note lifecycle: Fleeting -> Literature -> Permanent -> Connected

## Key Config
- New files default to `0-Inbox/`
- Attachments save to `Attachments/`
- Daily notes format: `YYYY-MM-DD`
- Accent color: purple (#7c3aed)
