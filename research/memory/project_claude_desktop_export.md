---
name: claude-code-desktop-export
description: "Full export of custom skills, hooks, MCP config and workflows to OneDrive for portability and LLM-readable installation."
metadata: 
  node_type: memory
  type: project
  originSessionId: c1d905c0-570c-45e8-977f-1a8e6feedd23
---

Export of all custom Claude Code assets to `<USER_HOME>/OneDrive - <ORG>\Claude Code Desktop\`.

**Why:** Portability — another LLM or developer can cold-read any subfolder, understand the skill/hook, and install it. Also serves as a human-readable backup of the full Claude Code configuration.

**How to apply:** When someone asks to share, export, or document any skill/hook, point them here. When installing on a new machine, copy `skills/{N}-{name}/skill.md` to `~/.claude/commands/{name}.md` and hooks as documented in each hook's README.

## Structure (2026-06-29)

```
Claude Code Desktop/
├── README.md                          ← master index + quick-install + tables
├── config/
│   ├── settings.json                  ← model, hooks wiring, env vars, plugins
│   └── mcp.json                       ← 5 MCP server definitions
├── workflows/
│   └── 3-persona-review-qa/README.md  ← standalone SA+EA+DE adversarial review cycle
├── hooks/  (11 hooks, each with README)
└── skills/ (40 skills, each with README, numbered by priority)
    ├── 01-data-engineering/ ★★★
    ├── 02-ubi-dev/ ★★★
    ├── 03-excel-create/ ★★★
    ├── 04-powerpoint-create/ ★★★
    ├── 05-docx-beautify/ ★★★
    ├── 06-data-dev-planning/ ★★★
    ├── 07-fluke-ai/ ★★★
    ├── 08-flk-litellm/ ★★★
    ├── 09–15: powerbi-desktop, azure-diagrams, ubi-mcp, ai-use-case-builder, aws-dev, paperclip, taashi-research ★★
    ├── 16–26: eval-framework, rag-multimodal, doc-extract, web-ingest, ubi-neo4j, polish-notebook, audit-ubi, azure-logic-apps, agentic-deploy, graphify, session-review ★
    ├── 27–33: masters-writing, repo-eval, github-triage, qa-session, ubiquitous-language, markitdown-bench, 521-assignment
    ├── 34-ai-ucb/ (8 sub-skills + templates)
    └── 35–40: plm-graph, doc-intelligence, doc-extract-reference, graphify-reference, frontend-slides, notebooklm
```

## Status (2026-06-29) — COMPLETE

All assets exported, QA'd, and documented.

- **62 README files** — every skill, hook, config, and the 3-persona workflow
- **47 skill.md files** — all 40 skills + AI UCB sub-skills and templates
- **11 hook .py files** — all hooks
- **PROJECT_MEMORY.md** — complete project summary at the root of the export folder

### QA Results
- Structural audit: 106 PASS, 0 issues (3 missing READMEs for skills 33/37/38 written)
- Content QA: 4 findings, all resolved:
  1. All 11 hook READMEs had hardcoded admin paths in JSON snippets → replaced with `~/.claude/` portable paths
  2. plm-graph README — added portability warning
  3. frontend-slides README — expanded multi-file installation instructions
  4. ubi-mcp README triggers — 3 extra triggers vs skill.md (README is richer, acceptable)

### Portability notes
- Hook READMEs now use `~/.claude/hooks/` (portable)
- Fluke-specific skills (ubi-dev, fluke-ai, flk-litellm, plm-graph, ubi-mcp, audit-ubi, polish-notebook) contain hardcoded subscription IDs and file paths — require updates for non-Fluke installs
- obsidian-session-logger and obsidian-memory-sync contain the Obsidian vault path — update `VAULT_PATH` in each script when installing on a different machine
