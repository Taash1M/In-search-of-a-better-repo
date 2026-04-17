---
name: Skill Framework and Inventory
description: 40 skill files (was 37). +3 new from mattpocock/skills (qa-session, github-triage, ubiquitous-language), 6 patterns extracted, 5 frontmatter fixes (2026-04-16).
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
## Skill Inventory (updated 2026-04-16)

### mattpocock/skills Evaluation (2026-04-16)

Evaluated 19 skills from `https://github.com/mattpocock/skills.git`. Security: PASS (9/10). Quality: 7.5/10.

**New skills installed:**
| Skill | Source | Key Feature |
|---|---|---|
| `qa-session.md` | mattpocock/qa | Interactive bug filing with background codebase exploration, Fluke product labels |
| `github-triage.md` | mattpocock/github-triage | Label-based state machine for issue triage, HITL/AFK classification |
| `ubiquitous-language.md` | mattpocock/ubiquitous-language | DDD glossary extraction, pre-seeded with 10 Fluke domain terms |

**Patterns extracted and implemented:**
| Pattern | Source Skill | Applied To | Description |
|---|---|---|---|
| Parallel sub-agent design variants | design-an-interface | powerpoint-create.md | 3 divergent layout proofs before committing |
| Background exploration | qa, github-triage | powerpoint-create.md | Spawn Explore agent for content research while discussing |
| HITL/AFK classification | prd-to-issues | ai-ucb-discover.md | Agent-readiness markers on work items |
| 4 dependency categories | improve-codebase-architecture | ai-use-case-builder.md | In-process, local-substitutable, remote-owned, true-external |
| Durable issue templates | triage-issue, qa | eval-framework.md | No file paths/line numbers + TDD fix plan |
| Trigger descriptions | write-a-skill | 5 skills (frontmatter) | YAML frontmatter added to azure-diagrams, azure-logic-apps, powerbi-desktop, flk-litellm, taashi-research |

**Evaluation report:** `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Skill Evaluation\mattpocock_skills_evaluation.md`

---

## Prior Skill Inventory (as of 2026-04-07)

### Active Skills (`C:\Users\adm-tmanyang\.claude\commands\`)

**Standalone Skills (8):**

| Skill | Purpose | Enhanced |
|---|---|---|
| `ubi-dev.md` | UBI platform development (streams, notebooks, ADF, PBI) | Task tracking, workflow rules, severity levels (2026-03-30) |
| `audit-ubi.md` | Multi-agent UBI codebase health audit | NEW (2026-03-30) — parallel fan-out by stream, P0-P3 severity |
| `polish-notebook.md` | Iterative Databricks notebook quality loop | NEW (2026-03-30) — lint/test/simplify/review, max 3 iterations |
| `session-review.md` | Lesson extraction with priority-ranked routing | NEW (2026-03-30) — 7 priority levels, skill>project>memory routing |
| `powerpoint-create.md` | PPTX creation, PptxGenJS + python-pptx, design system | Enhanced (2026-04-10) — mandatory 3-stage QA (content + programmatic layout + visual) |
| `paperclip.md` | Multi-agent orchestration, task ticketing, budgets, scheduling | NEW (2026-04-01) — cherry-picked from paperclipai/paperclip, A+ grade |
| `ai-use-case-builder.md` | AI UCB orchestrator — atomic state, step checkpoints, saga compensation | v2.0 → A+ (2026-04-07) |
| `ai-ucb-*.md` (x8) | AI UCB sub-skills: discover, infra, pipeline, ai, frontend, test, docs, deploy | v2.0 → all A+ (2026-04-07) |

**AI UCB Companion Skills (5, also in commands dir):**

| Skill | Purpose | Added |
|---|---|---|
| `doc-intelligence.md` | 3-tier document parsing/extraction (OCR, declarative, Azure AI) | 2026-04-03, A+ |
| `rag-multimodal.md` | Cross-modal KG + VLM retrieval + RAGAS eval + hybrid search tuning | 2026-04-03 → A+ (2026-04-07) |
| `agentic-deploy.md` | Agent runtime: LangGraph, LLM fallback, evals, observability, ACA deploy | 2026-04-03, A+ |
| `eval-framework.md` | AI quality testing: DeepEval, RAGAS, Garak red-teaming, Phoenix observability | 2026-04-03, A+ |
| `web-ingest.md` | Web crawling + circuit breaker + state persistence + quality validation | 2026-04-03 → A+ (2026-04-07) |

**Knowledge Graph Skill (1 + 1 reference, in commands dir):**

| Skill | Purpose | Added |
|---|---|---|
| `graphify.md` | Knowledge graph builder — AST + semantic extraction, Leiden clustering, 13 languages, HTML/JSON/Neo4j/Obsidian export | 2026-04-06, v2 (B grade, 102/120) |
| `graphify-reference.md` | On-demand reference: extraction schema, subagent prompt, module table, optional export code blocks | 2026-04-06 |

Based on safishamsi/graphify v0.3.0 (MIT). 5,723 lines source, 3,256 lines tests. Two-pass extraction (tree-sitter AST + parallel Claude semantic). No embeddings — topology-based clustering. 71.5x token reduction. Repo clone at `Claude code\graphify\`. Skill Judge: D (79/120) → B (102/120) after frontmatter, redundancy cut, expert anti-patterns.

**Document Extraction Skill (1 + 1 reference, in commands dir):**

| Skill | Purpose | Added |
|---|---|---|
| `doc-extract.md` | Unified document extraction — ContextGem (7 concept types), RAG-Anything (multimodal), agentic-doc (batch patterns) | 2026-04-07, B+ (104/120) |
| `doc-extract-reference.md` | On-demand reference: converter options, JsonObject patterns, batch pipeline, engineering drawing schema | 2026-04-07 |

Cherry-picked from 5 repos: ContextGem (Apache 2.0), Taash1M/ContextGem fork, RAG-Anything (MIT), agentic-doc (legacy LandingAI), DocsMind (MIT). Skill replaces doc-intelligence for hands-on extraction; doc-intelligence retained for AI UCB integration.

**Diagram Sub-Skill (1, in commands dir):**

| Skill | Purpose | Added |
|---|---|---|
| `azure-diagrams.md` | Architecture/data flow/landscape diagrams with real Azure SVG icons via cairosvg + matplotlib | 2026-04-06 |

Module: `azure_diagrams.py` v1.2.1 in `Document Beautification\`. Called by docx-beautify, powerpoint-create, ai-ucb-docs. 5 output presets (docx portrait/landscape, pptx full/half, standalone). 78+ Azure icon registry (incl. data_factory, oracle_database). Mandatory Quality Gate: every diagram must be visually inspected for missing icons, text overlap, distortion, and arrow collisions before embedding. All 3 caller skills updated with quality gate reference (2026-04-06). v1.2: Added 8-category semantic service colors (Cocoon-AI source, 2026-04-16). v1.2.1: Troubleshooting decision tree + NEVER list → A+ grade (2026-04-16).

**AI UCB Reference Files (7, in commands/ai-ucb/):**
`archetypes.md`, `pricing.md` (+ live API validation), `governance.md`, `infra-templates.md`, `pipeline-templates.md`, `frontend-templates.md` (+ security hardening), `doc-templates.md` (+ ADR + Model Card)

**Versioned backup:** All 21 AI UCB files backed up in `C:\Users\tmanyang\OneDrive - Fortive\Claude code\AI UCB\skills\` (organized into orchestrator/, sub-skills/, companions/, reference/ subfolders).

## AI UCB Comprehensive Quality Upgrade (2026-04-07)

All 21 AI UCB skill files upgraded to A+ via research-first approach (6 parallel research agents + GitHub/docs review):

| Tier | Files | Key Additions |
|---|---|---|
| D (60-71) → A+ | docs, infra, deploy, test | ADR+Jinja2, Bicep AVM+RBAC, DABs+blue/green, DeepEval+Locust |
| C (71-78) → A+ | orchestrator, discover, frontend, ai | Atomic state+checkpoints+saga, decision tree+Retail Prices API, retrieval module+security, Content Safety SDK |
| B+ (80-87) → A+ | pipeline, frontend-templates, pricing, rag-multimodal, web-ingest, doc-templates | DQ gates+retry+rollback, ReactMarkdown+CSP headers, live price validation, RAGAS eval, circuit breaker+crawl state, ADR+Model Card |

Patterns added across all files: anti-patterns expanded (avg 8→12 per file), error recovery tables expanded, production-grade code.

### Project-Local Skills (not yet promoted to commands dir)
| Skill | Location | Enhanced |
|---|---|---|
| `pptx-beautify.md` | `Claude code\Presentation Beautification\` | Severity levels, 10 non-negotiable rules added (2026-03-30) |

Note: `docx-beautify.md` promoted to commands dir on 2026-04-06 with azure-diagrams integration.

## Turbo-Inspired Patterns (Implemented 2026-03-30)

Source: Review of github.com/tobihagemann/turbo (64 markdown skill files). Six patterns cherry-picked and adapted:

1. **Task tracking at skill start** — TaskCreate for each phase, mark in_progress/completed. Applied to: ubi-dev.md
2. **Severity levels (P0-P3)** — Explicit criteria for each level, tailored per skill domain. Applied to: ubi-dev.md, pptx-beautify.md, docx-beautify.md
3. **Iterative polish loop** — Lint/test/simplify/review/fix cycle with hard cap (3 iterations). Created: polish-notebook.md
4. **Parallel agent fan-out** — Partition work, launch agents per partition, aggregate findings. Created: audit-ubi.md
5. **Don't-skip rules** — Explicit anti-shortcut rules section. Applied to: ubi-dev.md (10 rules), pptx-beautify.md (10 rules), docx-beautify.md (8 rules)
6. **Session review / lesson extraction** — Priority-ranked routing to skill files, PROJECT_MEMORY, or auto memory. Created: session-review.md

## Skill Judge Evaluations

### 2026-03-12 (Initial)
- Report: `C:\Users\tmanyang\Claude\deliverebles\skill-judge-evaluation-report.md`
- Top: powerbi-desktop (A, 108), ubi-dev (B, 102), fluke-ai (B, 97)
- Need trimming: excel-create (D, 83 — 65% redundant), powerpoint-create (D, 75 — 70% redundant)

### 2026-04-16 (Re-Assessment — 4 skills)
- Report: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Skill Evaluation\skill-judge-4skills-evaluation.md`
- azure-diagrams: **A+ (111/120)** — troubleshooting tree + NEVER list added
- docx-beautify: **A (108/120)** — quick-start tree added; diagram split needed for A+
- ubi-dev: **A (106/120)** — task decision tree + trigger keywords added; file split needed for A+
- powerpoint-create: **B+ (100/120)** — up from D (75); file split needed for A
- Tier 2 remaining: progressive disclosure splits for all 3 non-A+ skills
