---
name: Skill Framework and Inventory
description: Claude Code custom skills inventory, Turbo-inspired quality patterns, skill enhancement history. All 21 AI UCB files upgraded to A+ (2026-04-07).
type: project
---

## Skill Inventory (as of 2026-04-07)

### Active Skills (`C:\Users\adm-tmanyang\.claude\commands\`)

**Standalone Skills (8):**

| Skill | Purpose | Enhanced |
|---|---|---|
| `ubi-dev.md` | UBI platform development (streams, notebooks, ADF, PBI) | Task tracking, workflow rules, severity levels (2026-03-30) |
| `audit-ubi.md` | Multi-agent UBI codebase health audit | NEW (2026-03-30) — parallel fan-out by stream, P0-P3 severity |
| `polish-notebook.md` | Iterative Databricks notebook quality loop | NEW (2026-03-30) — lint/test/simplify/review, max 3 iterations |
| `session-review.md` | Lesson extraction with priority-ranked routing | NEW (2026-03-30) — 7 priority levels, skill>project>memory routing |
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

Module: `azure_diagrams.py` v1.1 in `Document Beautification\`. Called by docx-beautify, powerpoint-create, ai-ucb-docs. 5 output presets (docx portrait/landscape, pptx full/half, standalone). 78+ Azure icon registry (incl. data_factory, oracle_database). Mandatory Quality Gate: every diagram must be visually inspected for missing icons, text overlap, distortion, and arrow collisions before embedding. All 3 caller skills updated with quality gate reference (2026-04-06).

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

## Skill Judge Evaluation (2026-03-12)
- Report: `C:\Users\tmanyang\Claude\deliverebles\skill-judge-evaluation-report.md`
- Top: powerbi-desktop (A, 108), ubi-dev (B, 102), fluke-ai (B, 97)
- Need trimming: excel-create (D, 83 — 65% redundant), powerpoint-create (D, 75 — 70% redundant)
