# Standalone Skills

Catalog of 11 standalone Claude Code skills for the Fluke UBI platform, research, and general AI workflows. Each skill is a self-contained `.md` file that Claude Code activates when invoked via `/skill-name` or when the trigger conditions match.

---

## Overview

Standalone skills cover platform development (UBI, Neo4j, LiteLLM), code quality workflows, research methodology, orchestration, and academic work. They do not depend on each other and can be invoked independently.

---

## Inventory

| Skill | Purpose | Key Capabilities | Lines | Grade/Status |
|-------|---------|-----------------|------:|--------------|
| `ubi-dev.md` | Fluke UBI platform development | 3 repos (AzureDataBricks, ADF, Power BI), medallion architecture (Landing/Bronze/Silver/Gold), Oracle EBS transforms, Delta Lake, access control rules (never write to Prod/QA) | 1,970 | Production |
| `ubi-neo4j.md` | Neo4j knowledge graph for UBI Gold layer | 431 Gold tables, Fabric Lakehouse integration, Cypher generation, lineage traversal | 779 | Production |
| `audit-ubi.md` | Multi-agent UBI codebase health audit | Parallel fan-out by stream, P0–P3 severity classification, coverage across notebooks/ADF/Gold views | 191 | Production |
| `polish-notebook.md` | Iterative Databricks notebook quality loop | Lint → test → simplify → review cycle, max 3 iterations, halts on pass | 160 | Production |
| `session-review.md` | Lesson extraction with priority routing | 7 priority levels, routes findings to skill file / project memory / MEMORY.md | 140 | Production |
| `paperclip.md` | Multi-agent orchestration | Task ticketing, budget tracking, heartbeat scheduling, cherry-picked from paperclipai/paperclip | 622 | A+ |
| `fluke-ai.md` | Fluke AI general patterns | Azure AI services (AI Foundry, LLM Gateway, AI Search), Fluke-specific naming conventions and subscription topology | 475 | Production |
| `flk-litellm.md` | LiteLLM gateway deployment | Azure App Service, Docker containerization, rate limiting, model routing, cost tracking | 440 | Production |
| `taashi-research.md` | 4-phase deep research methodology | Discover → Analyze → Synthesize → Deliver; web search + repo analysis + structured deliverable generation | 200 | Production |
| `repo-eval.md` | Repository evaluation and skill extraction | Clone repo, analyze architecture, score on rubric, extract patterns into reusable skill files | 221 | Production |
| `521-assignment.md` | Academic assignment workflow | MSIS 521, 6-phase workflow, notebook generation, cheat sheet creation, submission formatting | 259 | Production |

---

## Skill Details

### ubi-dev.md — UBI Platform Development
The largest skill in the repo (1,970 lines). Governs all work against three UBI repositories:
- **AzureDataBricks** — notebook development (Python/Spark SQL), medallion layers
- **ADF** — pipeline authoring and trigger management
- **Power BI** — curated dataset management and DAX

Key rules embedded in the skill: never write directly to Prod or QA, always use all-purpose clusters for interactive work, Oracle VARCHAR2 fields land as STRING in Bronze, Silver layer owns type casting and JOIN logic, Gold layer exposes business-friendly aliases via views.

### ubi-neo4j.md — UBI Knowledge Graph
Covers the Neo4j graph built from 431 Gold layer tables sourced from Fabric Lakehouse. Provides Cypher query templates, schema conventions, lineage traversal patterns, and integration guidance.

### audit-ubi.md — Codebase Health Audit
Multi-agent skill that fans out workers by UBI stream (SO Backlog, GL, AR, etc.) and aggregates findings at P0–P3 severity. Produces a structured audit report with remediation recommendations.

### polish-notebook.md — Notebook Quality Loop
Runs a bounded quality improvement loop (max 3 iterations) on a Databricks notebook. Each iteration lints, runs tests, simplifies logic, and peer-reviews. Stops early when the notebook passes all checks.

### session-review.md — Lesson Extraction
Scans the current conversation for lessons learned and routes each to the appropriate persistence layer based on 7 priority levels: skill file update, project memory file, MEMORY.md index, or ephemeral note.

### paperclip.md — Multi-Agent Orchestration
Orchestration infrastructure cherry-picked from the paperclipai/paperclip open-source repo. Manages task tickets, assigns budgets per task, schedules heartbeats, and coordinates parallel agent workstreams. A+ grade.

### fluke-ai.md — Fluke AI Patterns
Reference skill for Azure AI work within the Fluke AI ML Technology subscription. Covers AI Foundry resource topology, LLM Gateway configuration, AI Search indexing conventions, and Fluke-specific naming.

### flk-litellm.md — LiteLLM Gateway
Step-by-step deployment skill for the LiteLLM proxy on Azure App Service with Docker. Covers rate limiting per team/user, model routing (Anthropic, OpenAI, Azure OpenAI), cost tracking, and health checks.

### taashi-research.md — Deep Research Methodology
Structures research work into four formal phases:
1. **Discover** — web search, repo discovery, source enumeration
2. **Analyze** — deep reading, pattern extraction, contradiction identification
3. **Synthesize** — cross-source integration, gap analysis
4. **Deliver** — structured report, actionable recommendations

### repo-eval.md — Repository Evaluation
Given a GitHub URL or local clone, evaluates a repo on architecture quality, test coverage, security posture, and production readiness. Extracts reusable patterns and generates a skill file for adopted repos.

### 521-assignment.md — Academic Workflow
Handles the MSIS 521 assignment lifecycle in 6 phases: parse prompt, research, outline, generate notebook/writeup, create cheat sheet, and format for submission.

---

## Usage Examples

```bash
# Invoke a skill by name
/ubi-dev
/paperclip
/taashi-research

# Skill auto-invokes when trigger conditions match —
# e.g., working on a Databricks notebook activates /ubi-dev automatically

# Research workflow
/taashi-research "Evaluate open-source LLM evaluation frameworks for RAG"

# Audit the UBI codebase
/audit-ubi

# Extract lessons from this session
/session-review

# Polish a specific notebook
/polish-notebook path/to/Refresh_FactSOBacklog.py

# Evaluate a new repo before adoption
/repo-eval https://github.com/some-org/some-repo
```

---

## Sync Workflow

Skills in this directory are the canonical versions. Promoted skills are also installed at `<ADMIN_HOME>/.claude\commands\` so Claude Code can resolve them globally.

To sync a skill after editing:

```bash
# Copy updated skill to global commands
cp "skills/standalone/ubi-dev.md" "$HOME/.claude/commands/ubi-dev.md"

# Verify the skill appears in the available list
# (Claude Code rescans commands on next session start)
```

To promote a new skill:
1. Develop and iterate the skill file in `skills/standalone/`
2. Run `/repo-eval` or manual Skill Judge scoring (target: B+ or above)
3. Copy to `~/.claude/commands/` once grade threshold is met
4. Update `skills/README.md` index and `MEMORY.md` skill framework entry
