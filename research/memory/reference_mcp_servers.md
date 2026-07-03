---
name: mcp-servers
description: "5 active MCP servers at ~/.claude/.mcp.json (context7, obsidian, azure, azure-devops, adf) + cloud-hosted (Databricks/Fabric) + ubi-mcp skill + the MCP_Servers package set"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

# MCP Servers (5 active — `~/.claude/.mcp.json`)

- **context7**: `@upstash/context7-mcp@latest` — library/framework documentation lookup
- **obsidian**: `@bitbonsai/mcpvault@latest` v0.11.0 — direct file access to Obsidian vault at `<USER_HOME>/OneDrive - <ORG>\Claude code\Obsidian` (no Obsidian app needed)
- **azure**: `@azure/mcp@latest` (npx.cmd) — ADLS Gen2, storage, ARM resources (UBI sub `52a1d076-...`)
- **azure-devops**: `@azure-devops/mcp@latest` (npx.cmd) — work items, PRs, builds (`dev.azure.com/flukeit`)
- **adf**: DataFactory.MCP (.NET 10) — ADF pipeline operations (`flkubi-adf-dev`)
- **Skill**: `ubi-mcp.md` (714 lines, A grade 109/120) — unified operational skill for all 6 MCP servers
- **Cloud-hosted (no local install)**: Databricks MCP (AI Gateway), Fabric Core MCP (Streamable HTTP)
- **Not yet available**: Power BI Modeling MCP (docs-only preview), ADLS community server (not on PyPI)
- **Packages**: 30 files in `MCP_Servers/` at UBI AI Integration folder (6 subfolders, each with README/skill/config/setup/env)

Related: [[ubi-ai-integration]] · [[miro-mcp]] · [[pbi-semantic-mcp]]
