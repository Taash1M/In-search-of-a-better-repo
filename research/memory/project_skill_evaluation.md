---
name: Skill Evaluation (mattpocock/skills + Cocoon-AI)
description: Evaluated mattpocock/skills (19 skills) + Cocoon-AI/architecture-diagram-generator — semantic color system added to 3 skills, dark arch pattern for PPTX, 6 patterns extracted. Skill Judge re-eval (revised 2026-04-17): azure-diagrams A+ (112), docx-beautify A+ (112), ubi-dev A (110), powerpoint-create A (106). D5 re-scored per no-split policy.
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

### powerpoint-create Decision Tree Added (2026-04-16)

7-branch decision tree added to powerpoint-create.md (the last of the 4 skills to get one). All 4 skills now have top-level decision trees. Pushed to GitHub (`f89482b`).
