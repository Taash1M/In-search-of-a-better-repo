---
name: Skill Evaluation (mattpocock/skills)
description: Evaluated 19 skills from mattpocock/skills repo — extracted 6 patterns, upgraded 4 skills, installed 3 new skills, added YAML frontmatter to 5 skills (2026-04-16)
type: project
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---
## Overview

Cloned and evaluated `https://github.com/mattpocock/skills.git` (19 skills) for security, quality, and applicability to the Fluke AI team's 40-skill framework.

**Why:** Identify valuable patterns and capabilities to upgrade existing skills or create new ones. Standing initiative to keep the skill framework competitive.

**How to apply:** Source patterns are attributed in each modified skill with `**Source pattern:** mattpocock/skills` tags. Evaluation report at `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Skill Evaluation\mattpocock_skills_evaluation.md`.

## Key Facts

- **Project dir**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Skill Evaluation\`
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
