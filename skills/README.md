# Claude Code Custom Skill Framework

> Written for future-Taashi. Assumes Claude Code knowledge. Documents decisions, architecture, and methodology so any workstream can be picked up cold.

---

## Overview

Skills are custom markdown files placed in `~/.claude/commands/` that give Claude Code specialized domain knowledge and reusable workflows. When invoked with `/skill-name`, the markdown content is injected into the active conversation context — Claude reads it as authoritative instructions and executes accordingly.

This repo holds **41 skill files** across 5 categories. They cover everything from the UBI Databricks platform to multi-agent orchestration to document generation. Each skill encodes decisions that took hours to learn so you don't re-learn them cold.

---

## Architecture

```
~/.claude/commands/              ← Live location (what Claude Code reads)
├── ai-ucb/                      ← AI UCB reference files (subfolder)
│   └── *.md
└── *.md                         ← All other skills (flat)

skills/                          ← Repo copy (this directory)
├── README.md                    ← This file
├── ai-ucb/                      ← 21 files
├── standalone/                  ← 11 files
├── document/                    ← 7 files
└── knowledge-graph/             ← 2 files
```

The live location and the repo location are kept manually in sync. The repo is the source of truth for version history; the live location is what actually runs.

---

## Inventory

### 1. AI UCB System — 21 files (`ai-ucb/`)

The largest workstream. Builds AI use cases end-to-end across 8 domains. All 21 files upgraded to A+ grade on 2026-04-07.

| File | Role | Notes |
|------|------|-------|
| `ai-use-case-builder.md` | Orchestrator | Atomic state, step checkpoints, saga compensation |
| `ai-ucb-discover.md` | Sub-skill | Discovery and requirements phase |
| `ai-ucb-infra.md` | Sub-skill | Infrastructure provisioning |
| `ai-ucb-pipeline.md` | Sub-skill | Data pipeline construction |
| `ai-ucb-ai.md` | Sub-skill | AI/ML model integration |
| `ai-ucb-frontend.md` | Sub-skill | Frontend and UI patterns |
| `ai-ucb-test.md` | Sub-skill | Testing and validation |
| `ai-ucb-docs.md` | Sub-skill | Documentation generation |
| `ai-ucb-deploy.md` | Sub-skill | Deployment automation |
| `agentic-deploy.md` | Companion | Agentic deployment patterns |
| `doc-intelligence.md` | Companion | 3-tier document intelligence |
| `eval-framework.md` | Companion | Evaluation framework patterns |
| `rag-multimodal.md` | Companion | RAGAS eval + hybrid tuning |
| `web-ingest.md` | Companion | Web ingestion patterns |
| `archetypes.md` | Reference | Use case archetypes |
| `pricing.md` | Reference | Cost modeling reference |
| `governance.md` | Reference | AI governance patterns |
| `infra-templates.md` | Reference | Infrastructure templates |
| `pipeline-templates.md` | Reference | Pipeline templates |
| `frontend-templates.md` | Reference | Frontend templates |
| `doc-templates.md` | Reference | Document templates |

### 2. Standalone — 11 files (`standalone/`)

Domain-specific skills that don't belong to a larger system.

| File | What It Does |
|------|--------------|
| `ubi-dev.md` | Fluke UBI platform development across 3 repos (ADB, ADF, PBI); medallion architecture; STM format |
| `ubi-neo4j.md` | Neo4j knowledge graph construction from 431 UBI Gold layer tables |
| `audit-ubi.md` | Multi-agent codebase health audit; generates scored report |
| `polish-notebook.md` | Iterative Databricks notebook quality loop (lint → test → simplify → review) |
| `session-review.md` | Lesson extraction from a session with priority-ranked routing to memory files |
| `paperclip.md` | Multi-agent orchestration skill, A+ grade, 5 modules; cherry-picked from paperclipai/paperclip |
| `fluke-ai.md` | Fluke AI general patterns; Azure AI Foundry config; LLM Gateway |
| `flk-litellm.md` | LiteLLM gateway deployment on Azure App Service |
| `taashi-research.md` | 4-phase deep research methodology (scope → gather → synthesize → deliver) |
| `repo-eval.md` | Repository evaluation and pattern extraction for new skill creation |
| `521-assignment.md` | Academic assignment workflow (MSIS 521) |

### 3. Document — 7 files (`document/`)

All document generation skills. Each wraps a Python library and encodes hard-won formatting decisions.

| File | Library / Backend | Notes |
|------|-------------------|-------|
| `docx-beautify.md` | python-docx | 4 presets, 4 palettes, Mermaid/D2/matplotlib diagrams; v6 |
| `doc-extract.md` | ContextGem + RAG-Anything + agentic-doc | Unified extraction; 3-tier routing |
| `doc-extract-reference.md` | — | Extraction schema reference; companion to doc-extract |
| `excel-create.md` | openpyxl + xlsxwriter | Excel creation and beautification |
| `powerpoint-create.md` | python-pptx | PowerPoint creation; mirrors docx-beautify patterns |
| `powerbi-desktop.md` | Power BI Desktop automation | PBI file manipulation |
| `azure-diagrams.md` | cairosvg + matplotlib | Azure architecture diagrams; Azure icon SVG library |

### 4. Knowledge Graph — 2 files (`knowledge-graph/`)

| File | What It Does |
|------|--------------|
| `graphify.md` | KG builder using AST + semantic extraction, Leiden community clustering; based on safishamsi/graphify |
| `graphify-reference.md` | Extraction schema definitions and module reference; companion to graphify |

---

## How It Works

### Invocation

```
/skill-name
```

Claude Code reads `~/.claude/commands/skill-name.md` and treats the content as active instructions for the conversation. For skills in subfolders:

```
/ai-ucb/ai-use-case-builder
```

### Skill Anatomy

Every skill file follows this structure:

```markdown
---
name: skill-display-name
description: one-line description
when: conditions under which to auto-invoke
---

# Skill Title

## Overview
What this skill knows and when to use it.

## Decision Tree
Flowchart or conditional logic for the main workflow.

## Code Patterns
Production-grade code snippets with inline comments.

## Anti-Patterns
What NOT to do and why. Explicit don't-skip rules.

## Error Recovery
Table of error conditions, causes, and remediation steps.
```

**Target length: 200–600 lines.** Shorter than 200 lines lacks depth. Longer than 600 lines wastes context window and dilutes focus.

The `when` frontmatter field enables auto-invocation — Claude will activate the skill proactively when the field conditions match, without waiting to be asked.

---

## How to Create a New Skill

1. **Identify the domain.** What are the 3-5 workflows this skill needs to execute? What decisions does it need to make? What mistakes does it need to avoid?

2. **Research first.** Clone 2-3 authoritative repos. Run `repo-eval.md` or use 6 parallel agents to read the repos and extract patterns. Don't write from memory — read actual source code.

3. **Structure the file.**
   - Frontmatter: name, description, when
   - Overview: what it knows, when to use it
   - Decision tree: the main conditional logic
   - Code patterns: production-grade examples with comments
   - Anti-patterns: expanded list (target 10-15 entries)
   - Error recovery: table format, cover the 5-8 most common failures

4. **Target 200-600 lines.** If you're under 200, the skill is too shallow. If you're over 600, split it or move reference material to a companion file.

5. **Evaluate.** Run the Skill Judge rubric (see below). Aim for B+ minimum before placing in commands.

6. **Place and test.**
   ```
   cp new-skill.md ~/.claude/commands/new-skill.md
   ```
   Open a new conversation, invoke with `/new-skill`, and exercise the main workflows.

7. **Copy to repo.** Once validated, copy to `skills/<category>/` and commit.

---

## How to Evaluate: Skill Judge Rubric

The Skill Judge evaluates on 120 points across 6 dimensions. Use this to score any skill before promoting it.

| Dimension | Max Points | What It Checks |
|-----------|-----------|----------------|
| Structure | 20 | Frontmatter, section completeness, heading hierarchy |
| Domain Depth | 25 | Accuracy of domain knowledge, specificity of patterns |
| Decision Logic | 20 | Decision trees present, conditions cover edge cases |
| Code Quality | 20 | Production-grade snippets, error handling, no pseudocode |
| Anti-Patterns | 20 | Count (target 10-15), specificity, don't-skip rules |
| Error Recovery | 15 | Coverage of common failures, actionable remediation |

**Grade thresholds:**
- A+ : 108-120 (90%+)
- A  : 96-107 (80-89%)
- B+ : 84-95  (70-79%)
- B  : 72-83  (60-69%)
- Below B: needs revision before promoting

---

## A+ Quality Methodology

The 21 AI UCB files were upgraded to A+ in a single session on 2026-04-07. The methodology used:

1. **Research first.** 6 parallel agents reviewed GitHub repos and official docs before any edits touched a file.

2. **Work weakest first.** Grade all files first. Start with D/C-grade files, finish with B+ files. The weakest files benefit most from the strongest patterns you've already refined by the time you reach them.

3. **Tier progression.** Push each file from its current grade to the next tier. D→C is not the same work as C→B+. Plan the upgrades in rounds.

4. **Per-file additions:**
   - Anti-patterns: expanded from avg 8 → 12 per file
   - Error recovery: added to every file that lacked it
   - Code patterns: replaced pseudocode with production-grade snippets
   - Don't-skip rules: made explicit in every anti-patterns section

5. **Verify with Skill Judge.** Re-score after each round. Don't declare A+ without a numeric score.

---

## Turbo-Inspired Quality Patterns

Six patterns cherry-picked from `github.com/tobihagemann/turbo` and embedded across all production-grade skills:

| # | Pattern | What It Does |
|---|---------|--------------|
| 1 | **Task tracking at skill start** | `TaskCreate` per phase at invocation time; progress is never lost if conversation resets |
| 2 | **Severity levels P0-P3** | Explicit criteria per domain; P0 = blocks delivery, P3 = cosmetic |
| 3 | **Iterative polish loop** | lint → test → simplify → review cycle, max 3 iterations; prevents infinite loops |
| 4 | **Parallel agent fan-out** | partition work → launch agents concurrently → aggregate results; standard for research tasks |
| 5 | **Don't-skip rules** | Explicit anti-shortcut section; names the specific shortcuts that kill quality |
| 6 | **Session review / lesson extraction** | Priority-ranked routing of lessons to memory files; feeds future-Taashi |

---

## Sync Workflow

The live location and the repo are not auto-synced. The manual workflow:

```
# Edit live (iterate fast)
~/.claude/commands/skill-name.md

# Test in a fresh conversation
/skill-name

# When satisfied, copy to repo
cp ~/.claude/commands/skill-name.md \
   "C:\Users\tmanyang\OneDrive - Fortive\Claude code\In search of a more perfect repo\skills\<category>\skill-name.md"

# Commit and push
git add skills/<category>/skill-name.md
git commit -m "upgrade skill-name to A+"
git push

# On another device: pull and copy back to commands
git pull
cp skills/<category>/skill-name.md ~/.claude/commands/skill-name.md
```

**The live location is not the source of truth for history.** If you edit live and don't copy back to the repo, the change is not version-controlled. Copy back after every meaningful edit.

---

## Key Decisions

**Why markdown instead of Python or JSON?**
Markdown is injected directly into Claude's context as prose instructions. Python or JSON would need a loader layer and wouldn't benefit from Claude's instruction-following. Markdown keeps the loop tight: edit file → invoke skill → Claude reads it as instructions.

**Why 200-600 lines?**
Under 200 lines means the skill is too thin — it won't cover edge cases or anti-patterns. Over 600 lines wastes context window tokens on every invocation, and the signal-to-noise ratio drops. The sweet spot is deep enough to be authoritative without being bloated.

**Why the companion file pattern?**
Some skills have a natural core (the workflow) and a natural reference layer (schemas, templates, lookup tables). Splitting them keeps the core skill concise while making the reference material available when needed. See `doc-extract.md` + `doc-extract-reference.md` and `graphify.md` + `graphify-reference.md`.

**Why subfolders for AI UCB?**
The 21 AI UCB files would clutter the root commands directory. Subfolder invocation (`/ai-ucb/skill-name`) is supported by Claude Code and keeps related files grouped. The orchestrator (`ai-use-case-builder.md`) lives at the root and delegates to the subfolder skills.

**Why not auto-sync with a script?**
It was considered. The problem is that edits happen in both directions (live edits during a session, repo edits during review), and a naive rsync in either direction would stomp changes. The manual copy workflow forces a deliberate decision each time. Worth revisiting if the skill count grows past 60.

---

## Gotchas

**Frontmatter `when` field is powerful but silent.** If a skill auto-invokes and you don't notice, it can shift Claude's behavior unexpectedly. Check the `when` fields of any skill you place in commands if you're seeing unexpected behavior.

**Subfolder skills don't auto-complete in the CLI.** You have to type the full path: `/ai-ucb/ai-use-case-builder`. There's no tab-complete through subfolders. Document the exact invocation string in the skill's frontmatter description.

**Context window budget matters.** Invoking multiple large skills in the same conversation compounds context usage. If you're running a session with `ai-use-case-builder.md` (orchestrator) and several sub-skills, you're injecting thousands of tokens before your first message. On haiku (100 TPM), that budget is tight. Prefer targeted sub-skill invocation over broad orchestrator invocation when you know the specific phase.

**D2 diagram paths must use forward slashes.** The D2 CLI (`C:\Users\tmanyang\tools\d2\d2-v0.7.1\bin\d2.exe`) requires forward-slash paths in the diagram source. Backslash paths silently fail or produce empty output.

**`$` triggers shell substitution in heredocs.** When writing skill content that includes `$variables`, use single-quoted heredocs (`<<'EOF'`) or escape every `$`. This has bitten the docx-beautify and azure-diagrams skills during bash-based generation steps.

**Skill Judge scores drift.** A file scored B+ six months ago may score B today if the rubric tightened or the domain knowledge aged. Re-evaluate before referencing a score in documentation.

---

## File Counts by Category

| Category | Files | Status |
|----------|-------|--------|
| AI UCB System | 21 | All A+ (2026-04-07) |
| Standalone | 11 | Mixed grades |
| Document | 7 | Mixed grades |
| Knowledge Graph | 2 | Mixed grades |
| **Total** | **41** | — |
