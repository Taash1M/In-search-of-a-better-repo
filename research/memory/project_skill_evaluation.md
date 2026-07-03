---
name: Skill Evaluation (skills + repos)
description: Skill evaluations (mattpocock/skills, Cocoon-AI, ubi-mcp) + repo evaluations (microsoft/rayfin 2.8/10, Azure-Samples/agentic-app-with-fabric 6.3/10). Skill Judge scores and repo-eval reports in Skill Evaluation folder (2026-06-16).
metadata:
  type: project
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---
## Overview

Cloned and evaluated `https://github.com/mattpocock/skills.git` (19 skills) for security, quality, and applicability to the Fluke AI team's 40-skill framework.

**Why:** Identify valuable patterns and capabilities to upgrade existing skills or create new ones. Standing initiative to keep the skill framework competitive.

**How to apply:** Source patterns are attributed in each modified skill with `**Source pattern:** mattpocock/skills` tags. Evaluation report at `<USER_HOME>/OneDrive - <ORG>\Claude code\Skill Evaluation\mattpocock_skills_evaluation.md`.

## Key Facts

- **Project dir**: `<USER_HOME>/OneDrive - <ORG>\Claude code\Skill Evaluation\`
- **Repo cloned to**: `skills/` subdirectory (19 skill directories)
- **Evaluated**: 2026-04-16
- **Security**: PASS (9/10) — no credentials, no injection, one hardcoded path (obsidian-vault)
- **Quality**: 7.5/10 — strong patterns but many skills below 1,000-word quality floor
- **Skills before**: 37 files (32 with YAML frontmatter, 5 without)
- **Skills after**: 40 files (all with YAML frontmatter)

## Changes Made (2026-04-16)

### 1. YAML Frontmatter Added (5 skills)

| Skill | Lines | What was added |
|-------|-------|---------------|
| azure-diagrams.md | 474 | name, description with trigger phrases |
| azure-logic-apps.md | 950 | name, description with trigger phrases |
| powerbi-desktop.md | 4,798 | name, description with trigger phrases |
| flk-litellm.md | 440 | name, description with trigger phrases |
| taashi-research.md | ~260 | name, description with trigger phrases |

### 2. Patterns Extracted and Implemented (4 skills modified)

| Target Skill | Pattern Source | What Was Added | Lines Added |
|-------------|---------------|----------------|-------------|
| powerpoint-create.md | design-an-interface | Parallel sub-agent design variants (3 divergent layout proofs) | +45 |
| powerpoint-create.md | qa, github-triage | Background Explore agent for content research | +30 |
| ai-ucb-discover.md | prd-to-issues | HITL/AFK classification for work items | +49 |
| ai-use-case-builder.md | improve-codebase-architecture | 4 dependency categories (in-process, local-substitutable, remote-owned, true-external) | +38 |
| eval-framework.md | triage-issue, qa | Durable issue templates + TDD fix plan for evaluation failures | +71 |

### 3. New Skills Installed (3 skills)

| Skill | Source | Adaptation | Lines |
|-------|--------|-----------|-------|
| qa-session.md | mattpocock/qa | Added Fluke product labels (6 products), HITL/AFK markers, `gh issue create` with labels | 148 |
| github-triage.md | mattpocock/github-triage | Added product labels, HITL/AFK assessment in triage, Fluke-specific label taxonomy | 151 |
| ubiquitous-language.md | mattpocock/ubiquitous-language | Pre-seeded 10 Fluke domain terms (Agent, Skill, Tool, Account, Customer, etc.) | 86 |

### 4. Progressive Disclosure Audit (documented, not executed)

Top 3 mega-skills identified for future splitting:
- powerbi-desktop.md: 4,798 lines (split into SKILL.md + references/)
- powerpoint-create.md: 2,776 lines (split into SKILL.md + references/)
- excel-create.md: 2,005 lines (split into SKILL.md + references/)

## Evaluation Ratings (A-D scale)

**A tier (adopt):** qa, github-triage, improve-codebase-architecture, tdd
**B+ tier (extract patterns):** design-an-interface, triage-issue, ubiquitous-language
**B tier:** prd-to-issues, prd-to-plan, write-a-prd, write-a-skill, request-refactor-plan
**C tier (skip):** grill-me, git-guardrails, setup-pre-commit
**D tier (skip):** edit-article, migrate-to-shoehorn, obsidian-vault, scaffold-exercises

## Skill-Reviewer Rubric Applied

Used `skill-reviewer` agent from `claude-plugins-official/plugins/plugin-dev/` to grade each skill on:
- Description quality (trigger phrases, third person, specificity, length)
- Content quality (word count 1,000-3,000 ideal, imperative writing style)
- Progressive disclosure (reference files split from SKILL.md)
- Organization (clear phases, templates, anti-patterns)

Key finding: the 3 highest-rated skills all use progressive disclosure. Our skills that exceed 500 lines should split content into reference files.

## Cocoon-AI Evaluation (2026-04-16)

**Repo:** `https://github.com/Cocoon-AI/architecture-diagram-generator` (3.1k stars, MIT)
**Grade:** B- (72/100) — well-crafted for scope but far simpler than our existing skills
**Verdict:** No new skill needed. Cherry-picked enhancements into 3 existing skills.
**Report:** `<USER_HOME>/OneDrive - <ORG>\Claude code\Skill Evaluation\cocoon-ai-architecture-diagram-evaluation.md`

### Changes Made

| Target Skill | Enhancement | Priority |
|-------------|-------------|----------|
| azure-diagrams.md (v1.2) | 8-category semantic service color system (auto-color by icon key) | P1 |
| docx-beautify.md (v7) | Diagram category color map — Mermaid classDef + D2 style definitions for 8 categories | P2 |
| powerpoint-create.md | Pattern 13: Dark Architecture Diagram — dark bg, semantic colors, Consolas font, drawn on-slide | P2 |

**Key pattern adopted:** Semantic category coloring (compute=green, data=violet, AI=cyan, security=rose, network=amber, integration=blue, monitor=purple, platform=slate). Consistent across all 3 skills for cross-format diagram coherence.

## Skill Judge 8-Dimension Re-Evaluation (revised 2026-04-17)

**Report:** `<USER_HOME>/OneDrive - <ORG>\Claude code\Skill Evaluation\skill-judge-4skills-evaluation.md`

| Skill | 2026-04-16 Score | 2026-04-17 Revised | Grade | D5 Change |
|---|---|---|---|---|
| azure-diagrams | 112/120 | **112/120** | **A+** | D5 unchanged (15/15) |
| docx-beautify | 109/120 | **112/120** | **A+** | D5: 11→14 (decision tree + clear sections) |
| powerpoint-create | 101/120 | **106/120** | **A** | D5: 7→12 (decision tree, but API docs dilute signal) |
| ubi-dev | 107/120 | **110/120** | **A** | D5: 11→14 (best decision tree of all 4 skills) |

**D5 re-score rationale:** Original scores penalized file length and recommended splits. Per user policy (2026-04-16), skills are slash commands loaded on-demand (~2% context). D5 now evaluates navigation quality only. powerpoint-create still penalized because ~500 lines of known API docs dilute signal (content relevance issue, not length issue).

### Tier 1 Quick Wins Implemented (5/5 complete)
1. azure-diagrams: Troubleshooting decision tree (5-branch) after Quality Gate
2. azure-diagrams: NEVER quick-reference list (6 rules) at top of Gotchas
3. docx-beautify: Quick-start decision tree (5-branch) before Architecture
4. ubi-dev: Top-level task decision tree (7-branch) after Access Control
5. ubi-dev: Expanded description with 10 trigger keywords

### Decision: Keep Files Intact (2026-04-16)

User decided against progressive disclosure splits. Rationale: skills are slash commands (pay-per-use context), not ambient. A 2,885-line file is ~2% of 200k context window. Decision trees at the top provide fast routing without file management overhead. Only revisit if context limits hit in practice.

### ubi-mcp.md Evaluation (2026-05-12)

New standalone MCP operations skill — peer to ubi-dev (not sub-skill). 714 lines after 5 quality fixes.

| Dimension | Score | Notes |
|---|---|---|
| D1 Knowledge Delta (20) | 17 | Operational discoveries, anti-patterns, cross-server workflows |
| D2 Mindset+Procedures (15) | 13 | Master decision tree (9 branches), diagnostic reasoning in walkthrough |
| D3 Anti-Patterns (15) | 13 | 8 gotchas (G1-G8) with BAD/GOOD examples |
| D4 Spec Compliance (15) | 14 | YAML frontmatter, imperative voice, env context |
| D5 Progressive Disclosure (15) | 14 | Decision tree routing, section independence |
| D6 Freedom Calibration (15) | 13 | Env-gated writes (Dev only), explicit read-only for Prod/QA |
| D7 Pattern Recognition (10) | 9 | SOBacklog walkthrough, cross-server chaining |
| D8 Practical Usability (15) | 13 | Installation status, auth troubleshooting, env table |
| **TOTAL** | **109/120** | **A** |

**5 fixes applied** (96→109): operational discoveries section, cross-server diagnostic reasoning, severity markers on gotchas, end-to-end walkthrough, expanded anti-patterns with BAD/GOOD.

**5 additional improvements identified** for A+ (115): UBI-specific pipeline mappings (D1+2), severity markers on remaining gotchas (D3+1), error recovery in walkthrough (D8+1), diagnostic reasoning on remaining workflows (D2+1), MCP vs Local decision heuristic (D6+1).

### powerpoint-create Decision Tree Added (2026-04-16)

7-branch decision tree added to powerpoint-create.md (the last of the 4 skills to get one). All 4 skills now have top-level decision trees. Pushed to GitHub (`f89482b`).

## Repo Evaluations (2026-06-16)

Used `/repo-eval` skill for full evaluations. Reports in `Skill Evaluation/` folder. Repos cloned to `rayfin-review/` and `agentic-app-with-fabric-review/`.

### microsoft/rayfin — 2.8/10 — Not Recommended

- **What:** Microsoft BaaS platform for Fabric — define data models with TS decorators, get DB/auth/APIs/storage/hosting
- **State:** Hub repo with zero source code. All 15 packages published on npm (v1.33.2) but repo is README stubs only ("source code coming soon")
- **License:** MIT
- **Interesting:** Claude Code plugin skill (SKILL.md) uses "route, don't improvise" anti-hallucination pattern — always defers to version-locked in-project docs
- **Action:** Star and revisit when source is opened. Test `npm create @microsoft/rayfin@latest` against our Fabric workspace
- **Report:** `rayfin-evaluation.md`

### Azure-Samples/agentic-app-with-fabric — 6.3/10 — Conditional (study only)

- **What:** Full-stack multi-agent banking demo (LangGraph + Flask + React + Fabric)
- **Stack:** Python/Flask (11,890 LOC), React/Vite/TS (19 files), LangGraph (5 agents), Fabric SQL DB + Cosmos DB + Lakehouse + Semantic Model + PBI Report + Eventhouse + Data Agent MCP
- **License:** MIT
- **Strengths:** Architecture (8/10), feature completeness (9/10), documentation (8/10), deployment automation (`setup_workspace.py` — 1,602 lines, 14-step idempotent provisioner)
- **Gaps:** Zero tests (0/10), wide-open CORS, user impersonation via X-User-Id header, SQL keyword blacklist bypassable, no CI/CD
- **Valuable patterns for Fluke:**
  - LangGraph coordinator -> specialist routing with graceful fallback (fabric_agent -> account_agent)
  - Fabric workspace deployment automation (idempotent, retry loops, token injection, interactive/CI modes)
  - Real-time monitoring: App events -> Eventstream -> Eventhouse -> KQL Dashboard
  - Fabric Data Agent as MCP tool in LangGraph workflow
- **Action:** Study patterns, extract `setup_workspace.py` for UBI Fabric automation. Do not deploy as-is.
- **Report:** `agentic-app-with-fabric-evaluation.md`

### microsoft/markitdown — 8.7/10 — Approved for Adoption

- **What:** Python utility + CLI for converting files to Markdown, optimized for LLM ingestion
- **Stack:** Python 3.10+ (12,558 LOC), 20 built-in converters, Hatch build system, 3 packages (core, MCP, OCR)
- **Version:** 0.1.6, 309 commits, MIT license, built by Microsoft AutoGen team
- **Strengths:** Architecture (9/10), code quality (9/10), security (8/10), feature completeness (10/10 — 20 converters), deployment (9/10 — Dockerfile+MCP+CLI+PyPI), testing (7/10 — 14 test files, CI on PRs), documentation (9/10)
- **Formats:** PDF, DOCX, PPTX, XLSX/XLS, HTML, CSV, RSS/XML, EPUB, images (EXIF+OCR), audio, Outlook .msg, Jupyter notebooks, ZIP, YouTube URLs, Wikipedia, Bing SERP, Azure Doc Intel, Azure Content Understanding
- **Key patterns:** Converter `accepts()`/`convert()` contract, priority-based registration, Magika content-type detection, defusedxml for all XML, plugin system via entry_points, frozen StreamInfo dataclass
- **Security:** defusedxml, html.escape, JS stripping, Docker non-root, SSRF documented as caller responsibility, ExifTool path restricted
- **MCP server:** `markitdown-mcp` — STDIO + SSE + Streamable HTTP, single `convert_to_markdown(uri)` tool
- **Valuable for Fluke:** Direct doc-extract replacement, MCP server for Claude Code fleet, Azure CU integration for PLM drawings, plugin system for Fluke-specific converters, PDF table extraction with adaptive column clustering
- **Action:** Install (`pip install markitdown[all]`), add MCP server, evaluate as doc-extract replacement, test Azure CU integration
- **Benchmark (2026-06-16):** Product 5594650 (FLUKE-II905), 18 docs, 11 components. **24x faster, 5.5x cheaper** than Claude Vision. 5 EXCELLENT, 3 GOOD, 7 WEAK, 3 FAIL (image-only). Hybrid routing recommended: >=2K chars use MarkItDown, <500 chars fall back to vision. 80% cost reduction projected. Results at `Technical Validation\MarkItDown\`.
- **Reports:** `markitdown-evaluation.md` (repo eval), `Technical Validation\MarkItDown\benchmark_report.md` (benchmark)
