# Research: Claude Code Memory System

## Overview

This folder documents the Claude Code memory system — 23 files that persist context across conversations. Memory files live at `~/.claude/projects/<project>/memory/` and are loaded selectively by Claude Code to maintain continuity across sessions without re-explaining context every time.

The memory system replaces the anti-pattern of pasting wall-of-text context into every conversation. Instead, a single index file (`MEMORY.md`) is loaded into every conversation, and individual topic files are referenced on demand.

---

## Memory Types

| Type | When to Save | How Claude Uses It |
|------|-------------|-------------------|
| **User** | Role, goals, communication preferences, domain knowledge | Tailors tone, depth, and terminology to the person |
| **Feedback** | Corrections (what went wrong), confirmations (what worked) | Avoids repeating mistakes; reinforces successful patterns |
| **Project** | Ongoing work, key decisions, timelines, stakeholders, status | Picks up mid-project without re-briefing |
| **Reference** | Pointers to external systems, tools, configs, file paths | Finds things without asking where they live |

---

## File Anatomy

Every memory file uses the same frontmatter + body structure:

```markdown
---
name: {{memory name}}
description: {{one-line description}}
type: {{user, feedback, project, reference}}
---

{{content — for feedback/project: rule/fact, then Why: and How to apply: lines}}
```

Feedback files include a `Why:` line explaining the root cause and a `How to apply:` line describing the corrective behavior. Project files include a `Status:`, `Key Decisions:`, and `Next Steps:` section.

---

## File Inventory (23 Files)

### Index (1 file)

| File | Description |
|------|-------------|
| `MEMORY.md` | Loaded into every conversation. Max 200 lines. One-liner pointers to all individual files. |

### Project Files (17 files)

| File | Description |
|------|-------------|
| `project_customer_mdm.md` | 5-phase matching pipeline, CRM+EBS dedup |
| `project_ai_use_case_builder.md` | v2.0, 21 skill files all graded A+ |
| `project_team_ai_enablement.md` | Claude Code for 27 users across 4 nodes |
| `project_skill_framework.md` | 16 active skills, all AI UCB companions A+ |
| `project_daily_report.md` | Weekly status for 8 projects, DOCX close-out + Excel carry-forward |
| `project_ubi_gold_graph.md` | Neo4j knowledge graph from 431 Gold layer tables, Fabric Lakehouse |
| `project_pptx_beautify.md` | python-pptx skill with presets and palettes, mirrors docx_beautify |
| `project_llm_usage_tracking.md` | DuckDB on VM, HNS enabled, PBI v4 direct Delta, 12h cron |
| `project_paperclip.md` | Multi-agent orchestration skill, A+ grade, 5 modules |
| `project_579_writeup.md` | Two-pass case write-up workflow, JTBD framework |
| `project_rag_skills.md` | doc-intelligence (3-tier) + rag-multimodal (RAGAS eval + hybrid tuning) |
| `project_ai_bi_tool.md` | Multi-agent BI tool, Supervisor+5 Workers, SharePoint UI |
| `project_alex_b_fortive_gl.md` | Fortive corporate GL (co 11/13), Gold view SQL, DOCX report |
| `project_graphify.md` | Knowledge graph skill based on safishamsi/graphify repo |
| `project_doc_extract.md` | Unified doc-extract skill (ContextGem+RAG-Anything+agentic-doc) |
| `project_plm_drawing_extraction.md` | Technical validation: 18/19 drawings, 94% title block accuracy |

### Feedback Files (5 files)

| File | Description |
|------|-------------|
| `feedback_pbi_underlyingtype.md` | PBI encoding: 261=Double, 518=DateTime; used for axis formatting |
| `feedback_skill_invocation.md` | Always activate skills proactively; FYI user as you go |
| `feedback_rbac_rest_api.md` | `az role assignment create` fails on Fluke AI sub; always use REST API PUT |
| `feedback_arrow_direction.md` | Arrows point TOWARD the other section, not both in the same direction |
| `feedback_diagram_quality_gate.md` | Validate every diagram visually before embedding; fix+regenerate loop |

### Reference Files (1 file)

| File | Description |
|------|-------------|
| `reference_cairosvg_windows.md` | MSYS2 64-bit DLL setup for cairosvg on Windows |

---

## What NOT to Save

Not everything belongs in memory. Saving too much degrades signal-to-noise and wastes context budget.

- **Code patterns** — Derive from reading the code directly.
- **Git history** — Use `git log`; don't duplicate in memory.
- **Debugging solutions** — The fix is in the code; memory just adds noise.
- **Anything already in CLAUDE.md** — CLAUDE.md is always loaded; no need to duplicate.
- **Ephemeral task details** — One-off instructions, meeting notes, or ticket IDs that won't recur.

---

## Sync Workflow

Memory files live in two places:

1. **Live location** (loaded by Claude Code): `~/.claude/projects/<project>/memory/`
2. **Repo copy** (for version control and sharing): `research/memory/` in this repo

To sync from live to repo:

```bash
cp ~/.claude/projects/*/memory/*.md "path/to/repo/research/memory/"
```

The repo copy is the source of truth for documentation. The live location is the source of truth for Claude Code behavior.

---

## Key Decisions

**Why a single index file?** Claude Code loads `MEMORY.md` into every conversation automatically. Keeping it under 200 lines with one-liner pointers means the index is always present without consuming excessive context. Detailed content lives in topic files loaded only when relevant.

**Why 23 files instead of one large file?** Granularity allows Claude Code to load only the files relevant to the current task. A monolithic memory file would bloat every conversation.

**Why separate feedback files?** Feedback represents learned behavior corrections. Keeping them separate from project files ensures they are applied universally, not just in the context of the project where the feedback originated.
