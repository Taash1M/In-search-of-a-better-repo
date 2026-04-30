---
name: AI Use Case Builder Project
description: Orchestrator + 8 sub-skills + 5 companions for building end-to-end AI solutions on Azure. v2.0, 21 skill files, all A+ grade after comprehensive upgrade (2026-04-07).
type: project
---

## Project Directory (Primary)
`<USER_HOME>/OneDrive - <ORG>\Claude code\AI UCB\`

**Why:** Consolidated from 3 scattered locations on 2026-04-03. This is the versioned backup and documentation home.
**How to apply:** Always update live skills in `~/.claude/commands/` first, then sync to this folder. See `FILE_MAP.md` in root.

## Folder Structure
```
AI UCB/
├── AI_UCB_PROJECT_MEMORY.md    (project memory)
├── FILE_MAP.md                 (complete file inventory)
├── skills/
│   ├── orchestrator/           (1 file)
│   ├── sub-skills/             (8 phase files)
│   ├── companions/             (5 companion files)
│   └── reference/              (7 template/ref files)
├── docs/
│   ├── suite/                  (5 numbered docs, MD+DOCX)
│   ├── design/                 (spec, design, build plan, platform)
│   └── presentations/          (summary deck)
├── deliverables/               (What Was Done reports + decks)
├── scripts/                    (Python generators)
├── assets/                     (report diagram PNGs, v1 + v2)
└── source-repos/               (cloned reference repos)
```

## Key Files
- **File map**: `FILE_MAP.md` in root (complete inventory)
- **Project memory**: `AI_UCB_PROJECT_MEMORY.md` in root
- **Spec**: `docs/design/ai-use-case-builder-spec.md` (v1.0, APPROVED)
- **Design doc**: `docs/design/fluke-ai-usecase-builder-design.md` (v1.0)
- **Build plan**: `docs/design/fluke-ai-usecase-builder-build-plan.md` (v1.1)
- **Doc suite**: `docs/suite/01-*.md` through `05-*.md` (v2.0)
- **Summary deck**: `docs/presentations/AI-Use-Case-Builder-Summary.pptx`

## Structure
1 orchestrator + 8 sub-skills + 5 companions + 7 reference files = 21 skill files total.

## Status
Sprint 12 COMPLETE — All 12 sprints done, all deliverables in project folder. ~11,500+ lines across 21 files, all A+ grade after comprehensive upgrade (2026-04-07).

## Key Decisions
Hybrid subscription (UBI+AI), CLI dev + Bicep artifacts, Fabric included, Neo4j+Cosmos both, Copilot Studio + web apps, Azure DevOps only, full cost estimation, multi-region day 1, MD+DOCX docs, orchestrator+sub-skills, JSON+MD state.

## MVP Archetypes
ALL 8 archetypes now FULL — zero STUBs remaining (2026-04-07).
Doc Intelligence: FULL via /doc-intelligence (2026-04-03). RAG: +multimodal (2026-04-03).
Predictive ML, Knowledge Graph, Voice/Text, Computer Vision: upgraded to FULL (2026-04-07).
Document Vision sub-variant added to Computer Vision archetype with PLM extraction learnings.

## Sprint 12 (Final)
Documentation suite: 5 docs (EA, Solution Design, Approach, Mappings, How-To) in MD+DOCX. Project folder total: 31 artifacts.

## Post-Sprint: RAG Skills Integration (2026-04-03)
- 2 new skills integrated: `/doc-intelligence` (3-tier) and `/rag-multimodal` (cross-modal graph + VLM)
- 5 AI UCB files edited, 13 total edits across discover, pipeline, ai, archetypes, orchestrator
- 3 new state contract flags: `multimodal_rag`, `enhanced_parsing`, `doc_intelligence_tier`
- Doc Intelligence archetype: STUB → FULL (3-tier architecture from Doctra + ContextGem patterns)
- RAG archetype: +multimodal option (9-field AI Search index, VLM-enhanced retrieval)
- "What Was Done" report + presentation generated in `<USER_HOME>/OneDrive - <ORG>\Claude code\AI UCB\`
- AI UCB project memory created at same location for continuity

## Post-Sprint: Agentic Deploy Integration (2026-04-03)
- 1 new skill integrated: `/agentic-deploy` (5-module agent runtime, cherry-picked from AI-agentic-system-dev-to-prod repo)
- 6 AI UCB files edited: discover, pipeline, ai, archetypes, orchestrator + new skill file
- 5 new state contract flags: `agent_runtime`, `agent_framework`, `llm_fallback_strategy`, `eval_framework`, `observability`
- Multi-Agent archetype (Archetype 7): fully rewritten with LangGraph runtime architecture, circular fallback, eval framework
- Pipeline dispatcher: multi-agent upgraded from STUB to FULL
- AI dispatcher: multi-agent enhanced with LLM registry + memory + eval conditionals
- `eval_framework: true` works independently on ANY archetype (cross-cutting enhancement for Phase 5)
- Source repo: `<USER_HOME>/OneDrive - <ORG>\Claude code\AI UCB\AI-agentic-system-dev-to-prod-\`

## Post-Sprint: AI Engineering Toolkit Evaluation (2026-04-03)
- Cloned ai-engineering-toolkit (github.com/Taash1M/ai-engineering-toolkit) — awesome-list of 100+ tools across 14 categories
- Gap analysis: 5 of 14 categories had coverage gaps (Evaluation, Web Scraping, Guardrails, Prompt Optimization, App Frameworks)
- P0 — 2 new companion skills: `/eval-framework` (~400 lines, 4 modules: DeepEval, RAGAS, Garak, Phoenix) and `/web-ingest` (~350 lines, 3-stage pipeline: Discover, Crawl, Structure)
- P0 — 3 files enhanced: `ai-ucb-test.md` (enhanced Step 4 with eval integration), `ai-use-case-builder.md` (companion skills table), `ai-ucb-discover.md` (eval/web/chunking requirements)
- P1 — 4 files enhanced: `agentic-deploy.md` (Module 6: Guardrails AI + NeMo), `ai-ucb-ai.md` (Step 9: DSPy + Promptflow), `rag-multimodal.md` (4 chunking strategies), orchestrator updates
- P2 — 1 file enhanced: `ai-ucb-frontend.md` (Gradio scaffold for internal demos)
- 6 new state contract flags: `eval_tier`, `red_team`, `observability`, `synthetic_test_size`, `web_sources[]`, `chunking_strategy`
- Companion skills total: 5 (doc-intelligence, rag-multimodal, agentic-deploy, eval-framework, web-ingest)
- "What Was Done" v2 report + presentation generated in AI UCB folder

## Consolidation & Documentation Refresh (2026-04-05)
- Consolidated files from 3 scattered locations into AI UCB folder with meaningful subfolder structure
- Created `FILE_MAP.md` — complete inventory of all 50+ files with purpose and cross-references
- Skills organized: `skills/orchestrator/`, `skills/sub-skills/`, `skills/companions/`, `skills/reference/`
- Docs organized: `docs/suite/` (5 numbered v2.0), `docs/design/` (spec, design, build plan), `docs/presentations/`
- Deliverables, scripts, assets, source-repos each in own subfolder
- Regenerated all 5 documentation suite DOCX files from updated v2.0 MDs (Fluke-branded styling)
- Added `regenerate_suite_docx.py` script for future DOCX refreshes
- Rule: update live skills in `~/.claude/commands/` first, then sync to AI UCB folder

## Post-Sprint: Archetype Expansion — All STUBs Eliminated (2026-04-07)
- Triggered by PLM drawing extraction validation (18/19 drawings, 94% title block accuracy)
- PLM learnings applied to `/doc-intelligence` companion skill (vision extraction section + gotchas table)
- **18 STUBs upgraded to FULL across 5 files:**
  - `ai-ucb-pipeline.md`: 10 notebook template STUBs (entity-extraction, feature-eng, transcription, image-labeling, training-datasets, graph-triples, graph-load, ml-training, index-population, multi-model)
  - `ai-ucb-pipeline.md`: 4 dispatcher archetypes (predictive-ml, knowledge-graph, voice-text, computer-vision)
  - `ai-ucb-ai.md`: 2 dispatcher archetypes (voice-text, computer-vision)
  - `ai-ucb-frontend.md`: 2 frontend types (copilot-studio, power-apps)
  - `frontend-templates.md`: 3 templates (Dashboard, Document Viewer, Copilot Studio)
- `archetypes.md`: Document Vision sub-variant added to Computer Vision archetype
- Production patterns sourced from: Neo4j best practices, Azure ML/Vision/Speech/NER OEM docs, graphify repo, cloned repos
- E2E validation suite created: `scripts/validate_ai_ucb.py` — 174/176 checks pass, 0 failures
- All STUB references cleaned from project memory, report templates, anti-pattern rules

## Comprehensive Quality Upgrade — All Files to A+ (2026-04-07)
- **Scope**: All 21 skill files upgraded from D-A range to A+ quality
- **Approach**: Research-first (6 parallel agents + GitHub/docs review), then systematic edits D→C→B+
- **D-tier (60-71) → A+**: ai-ucb-docs, ai-ucb-infra, ai-ucb-deploy, ai-ucb-test
  - ADR + Jinja2 doc gen, Bicep AVM + RBAC matrix, DABs + blue/green deploy, DeepEval + Locust + archetype test suites
- **C-tier (71-78) → A+**: ai-use-case-builder, ai-ucb-discover, ai-ucb-frontend, ai-ucb-ai
  - Atomic state writes + step checkpoints + saga compensation, programmatic decision tree + Azure Retail Prices API, retrieval module + 3-tier health + security hardening, full Content Safety SDK (Prompt Shields + groundedness + PII + blocklists)
- **B+ tier (80-87) → A+**: pipeline, frontend-templates, pricing, rag-multimodal, web-ingest, doc-templates
  - Data quality gates + retry + rollback + idempotency, ReactMarkdown/rehype-sanitize + ErrorBoundary + security headers + input validation + liveness/readiness, live price API validation + drift detection, RAGAS eval framework + hybrid search tuning, circuit breaker + crawl state persistence + post-crawl validation, ADR + Model Card templates
- **Key patterns added across all files**: anti-patterns expanded (avg 8→12 per file), error recovery tables expanded, production-grade code patterns, security hardening
- All files synced to `~/.claude/commands/` on 2026-04-07
