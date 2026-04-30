# AI Use Case Builder (AI UCB) — v2.0

**For future-Taashi:** This is the canonical reference for the AI Use Case Builder skill system. Read this before touching any of these files.

---

## Overview

AI UCB is a 21-file orchestrated skill system that guides Claude Code through every phase of building a production-grade AI solution on Azure — from initial discovery through deployment and operations. It is not a monolithic prompt; it is a structured pipeline with an orchestrator, eight phase sub-skills, five cross-cutting companion skills, and seven reference files.

**Version:** 2.0  
**Grade:** A+ across all 21 files (comprehensive quality upgrade completed 2026-04-07)  
**Scope:** Discovery → Infrastructure → Data Pipeline → AI/ML → Frontend → Testing → Documentation → Deployment

The system is invoked via a single entry point (`/ai-use-case-builder`) and dispatches autonomously to the appropriate phase sub-skills based on a shared JSON state contract. Each phase writes atomic state checkpoints. If a phase fails, saga compensation logic rolls back partial changes before surfacing the error.

---

## Architecture

```
User invokes /ai-use-case-builder
        │
        ▼
┌─────────────────────────────┐
│  Orchestrator                │  ← Atomic state writes, step checkpoints, saga compensation
│  ai-use-case-builder.md     │
└──────────┬──────────────────┘
           │ dispatches to phase sub-skills
           ▼
┌──────────────────────────────────────────────────────────┐
│  Phase 0: /ai-ucb-discover   → Requirements + archetype  │
│  Phase 1: /ai-ucb-infra      → Azure infrastructure      │
│  Phase 2: /ai-ucb-pipeline   → Data pipeline notebooks   │
│  Phase 3: /ai-ucb-ai         → AI/ML model integration   │
│  Phase 4: /ai-ucb-frontend   → UI scaffolding             │
│  Phase 5: /ai-ucb-test       → Testing + evaluation       │
│  Phase 6: /ai-ucb-docs       → Documentation suite        │
│  Phase 7: /ai-ucb-deploy     → Deployment + operations    │
└──────────┬───────────────────────────────────────────────┘
           │ enhanced by companions (cross-cutting)
           ▼
┌──────────────────────────────────────────────────────────┐
│  /agentic-deploy     → Agent runtime, LangGraph, evals   │
│  /doc-intelligence   → 3-tier document parsing            │
│  /eval-framework     → DeepEval, RAGAS, Garak, Phoenix    │
│  /rag-multimodal     → Cross-modal KG + VLM retrieval     │
│  /web-ingest         → Web crawling + circuit breaker      │
└──────────┬───────────────────────────────────────────────┘
           │ draws from reference files
           ▼
┌──────────────────────────────────────────────────────────┐
│  archetypes.md          → 8 solution archetypes           │
│  pricing.md             → Azure cost estimation + live API │
│  governance.md          → Security, compliance, RBAC       │
│  infra-templates.md     → Bicep/ARM templates              │
│  pipeline-templates.md  → Databricks notebook templates    │
│  frontend-templates.md  → React/Streamlit/Copilot Studio   │
│  doc-templates.md       → ADR, Model Card, doc suite       │
└──────────────────────────────────────────────────────────┘
```

The orchestrator is the only entry point. Sub-skills are never invoked directly by the user — the orchestrator dispatches to them. Companions are cross-cutting and can be invoked by multiple phases (e.g., `eval-framework` is called by both Phase 3 and Phase 5; `doc-intelligence` is called by Phase 2 and Phase 3).

---

## 8 Solution Archetypes

All eight archetypes are FULL implementations — zero STUBs. Each archetype drives conditional logic throughout every phase (infrastructure choices, pipeline patterns, AI service selection, frontend scaffolding, eval strategy, deployment topology).

| # | Archetype | Core Services | Key Feature |
|---|-----------|---------------|-------------|
| 1 | **RAG** (Retrieval-Augmented Generation) | Azure AI Search, Azure OpenAI, Cosmos DB | Multimodal option (VLM + cross-modal KG) |
| 2 | **Document Intelligence** | Azure AI Document Intelligence, Form Recognizer | 3-tier: OCR → declarative extraction → full AI |
| 3 | **Predictive ML** | Azure ML, Databricks, Feature Store | Feature engineering + MLflow model registry |
| 4 | **Knowledge Graph** | Neo4j, Cosmos DB (Gremlin API) | Entity extraction + graph traversal |
| 5 | **Voice & Text Analytics** | Azure Speech Services, Azure Language, Cognitive Services | NER + sentiment + speaker diarization |
| 6 | **Computer Vision** | Azure AI Vision, Custom Vision | Custom models + Document Vision sub-variant |
| 7 | **Multi-Agent Systems** | LangGraph, Azure OpenAI, Azure Container Apps | Circular fallback, agent runtime, eval harness |
| 8 | **Conversational AI** | Copilot Studio, Azure Bot Service | Copilot Studio + custom web app paths |

Archetype selection happens in Phase 0 (discover) via a structured decision tree and is written to state. Every downstream phase branches on the `archetype` field.

---

## State Contract

Phases communicate through a shared JSON state file (`ucb-state.json`) written atomically between each phase. The orchestrator reads and validates state at each transition. If state is corrupt or missing required fields, the orchestrator halts and surfaces the issue before proceeding.

### Core Fields

```json
{
  "run_id": "uuid",
  "archetype": "rag | doc-intelligence | predictive-ml | knowledge-graph | voice-text | computer-vision | multi-agent | conversational",
  "azure_region": "eastus2",
  "subscription_id": "...",
  "resource_group": "...",
  "current_phase": 0,
  "phase_checkpoints": {},

  "multimodal_rag": true,
  "enhanced_parsing": false,
  "doc_intelligence_tier": "ocr | declarative | ai",

  "agent_runtime": "langgraph | semantic-kernel | autogen",
  "agent_framework": "supervisor | hierarchical | peer",
  "llm_fallback_strategy": "circular | static | none",

  "eval_framework": "deepeval | ragas | garak | phoenix",
  "eval_tier": "basic | standard | full",
  "red_team": true,

  "web_sources": [],
  "chunking_strategy": "fixed | semantic | hierarchical",

  "fabric_enabled": false,
  "neo4j_enabled": false,
  "cosmos_enabled": false,
  "devops_pipeline": "azure-devops",
  "deployment_strategy": "blue-green | rolling | canary",
  "multi_region": true,
  "doc_output_format": ["md", "docx"]
}
```

The orchestrator validates required fields before each phase dispatch. Saga compensation is triggered when a phase writes a `rollback_required: true` flag — the orchestrator walks back completed phases in reverse order.

---

## Phase Flow

### Phase 0: Discover (`/ai-ucb-discover`)
- Structured interview to capture requirements, constraints, and success criteria
- Decision tree logic → selects archetype from the 8 options
- Calls Azure Retail Prices API for preliminary cost range
- Outputs: populated state JSON + `discovery-report.md`

### Phase 1: Infrastructure (`/ai-ucb-infra`)
- Bicep AVM modules for all Azure resources (not raw ARM)
- RBAC assignments at resource group + service level
- Multi-region topology scaffolded day 1
- Draws from `infra-templates.md`
- Outputs: `infra/` directory with Bicep modules + parameter files

### Phase 2: Data Pipeline (`/ai-ucb-pipeline`)
- Databricks notebook templates for ingestion, transformation, feature engineering
- DQ gates, retry logic, and rollback hooks at each stage
- Fabric Lakehouse integration if `fabric_enabled: true`
- Draws from `pipeline-templates.md`
- Outputs: `notebooks/` directory + pipeline README

### Phase 3: AI/ML (`/ai-ucb-ai`)
- Model integration, prompt engineering, content safety
- Content Safety SDK integration (Azure AI Content Safety)
- MLflow experiment tracking + model registry for Predictive ML archetype
- Calls `eval-framework` companion for eval harness setup
- Calls `rag-multimodal` companion for RAG archetype
- Calls `doc-intelligence` companion for Document Intelligence archetype
- Calls `agentic-deploy` companion for Multi-Agent archetype
- Outputs: `ai/` directory with model configs, prompt templates, eval setup

### Phase 4: Frontend (`/ai-ucb-frontend`)
- React (TypeScript), Streamlit, or Copilot Studio scaffolding based on archetype
- Security headers, CSP, MSAL authentication
- Retrieval module for RAG-backed frontends
- Draws from `frontend-templates.md`
- Outputs: `frontend/` directory with scaffolded app

### Phase 5: Testing (`/ai-ucb-test`)
- Unit, integration, and load testing
- DeepEval for LLM eval, Locust for load/performance
- Garak red-teaming if `red_team: true`
- Phoenix tracing integration
- Outputs: `tests/` directory + `test-report.md`

### Phase 6: Documentation (`/ai-ucb-docs`)
- Full documentation suite: ADR, Model Card, runbook, architecture doc
- Jinja2 templating for consistent doc generation
- MD + DOCX output based on `doc_output_format` state field
- Draws from `doc-templates.md`
- Outputs: `docs/` directory with complete suite

### Phase 7: Deploy (`/ai-ucb-deploy`)
- Azure DevOps pipeline YAML (only — no GitHub Actions)
- Databricks Asset Bundles (DABs) for notebook deployment
- Blue/green deployment with traffic shifting
- Smoke tests post-deploy
- Outputs: `.azuredevops/` directory + deployment runbook

---

## File Inventory

All 21 files, their category, approximate line count, and the key additions that brought each file to A+ grade.

| # | File | Category | ~Lines | Key A+ Additions |
|---|------|----------|--------|------------------|
| 1 | `ai-use-case-builder.md` | Orchestrator | 400–450 | Atomic state writes, step checkpoints, saga compensation |
| 2 | `ai-ucb-discover.md` | Sub-skill | 350–400 | Decision tree, Retail Prices API call, archetype confidence scoring |
| 3 | `ai-ucb-infra.md` | Sub-skill | 400–450 | Bicep AVM modules, RBAC at resource + service level, multi-region day 1 |
| 4 | `ai-ucb-pipeline.md` | Sub-skill | 400–450 | DQ gates, retry logic, rollback hooks, Fabric integration |
| 5 | `ai-ucb-ai.md` | Sub-skill | 450–500 | Content Safety SDK, retrieval module, MLflow, full archetype branching |
| 6 | `ai-ucb-frontend.md` | Sub-skill | 350–400 | Security headers, CSP, MSAL, Copilot Studio + web app paths |
| 7 | `ai-ucb-test.md` | Sub-skill | 400–450 | DeepEval, Locust, Garak red-team, Phoenix tracing |
| 8 | `ai-ucb-docs.md` | Sub-skill | 350–400 | ADR template, Jinja2 generation, Model Card, MD + DOCX output |
| 9 | `ai-ucb-deploy.md` | Sub-skill | 400–450 | DABs, blue/green deployment, smoke tests, Azure DevOps only |
| 10 | `agentic-deploy.md` | Companion | 450–500 | LangGraph runtime, circular fallback, eval harness, agent topology |
| 11 | `doc-intelligence.md` | Companion | 400–450 | 3-tier parsing logic, OCR/declarative/AI routing, confidence thresholds |
| 12 | `eval-framework.md` | Companion | 400–450 | DeepEval + RAGAS + Garak + Phoenix unified, eval tier gating |
| 13 | `rag-multimodal.md` | Companion | 450–500 | RAGAS eval, cross-modal KG, VLM retrieval, hybrid tuning |
| 14 | `web-ingest.md` | Companion | 350–400 | Circuit breaker, politeness policy, chunking strategy selection |
| 15 | `archetypes.md` | Reference | 500–600 | All 8 archetypes FULL — zero STUBs, decision matrix, tradeoffs |
| 16 | `pricing.md` | Reference | 300–350 | Live Azure Retail Prices API validation, cost model per archetype |
| 17 | `governance.md` | Reference | 300–350 | RBAC matrix, compliance checklist, data classification |
| 18 | `infra-templates.md` | Reference | 500–600 | Bicep AVM module library, parameter file patterns |
| 19 | `pipeline-templates.md` | Reference | 500–600 | Databricks notebook templates per archetype, DQ patterns |
| 20 | `frontend-templates.md` | Reference | 400–500 | React/Streamlit/Copilot Studio templates, security headers |
| 21 | `doc-templates.md` | Reference | 400–450 | ADR, Model Card, architecture doc, runbook templates |

---

## Quality Upgrade History

### v1.0 — Initial Build
21 files created as a working system. Functional but uneven — reference files were strong (B+), core sub-skills were inconsistent (C–D tier).

### v2.0 — Comprehensive Quality Upgrade (2026-04-07)

The upgrade used a research-first approach: 6 parallel research agents reviewed GitHub repos, Azure docs, and LLM eval literature before any edits were made. Every file was graded, tiered, and upgraded systematically.

#### D-Tier (60–71) → A+
Files that had functional skeletons but were missing production patterns:

- **`ai-ucb-docs.md`** — Added ADR template, Jinja2-based generation, Model Card, dual MD/DOCX output
- **`ai-ucb-infra.md`** — Replaced raw ARM with Bicep AVM modules, added RBAC assignments, multi-region topology
- **`ai-ucb-deploy.md`** — Added Databricks Asset Bundles (DABs), blue/green with traffic shifting, smoke tests
- **`ai-ucb-test.md`** — Added DeepEval integration, Locust load testing, Garak red-team harness

#### C-Tier (71–78) → A+
Files with good structure but weak decision logic and missing integrations:

- **`ai-use-case-builder.md`** — Added atomic state writes, phase checkpoints, saga compensation for rollback
- **`ai-ucb-discover.md`** — Added structured decision tree, Azure Retail Prices API call, confidence scoring
- **`ai-ucb-frontend.md`** — Added retrieval module, security hardening, Copilot Studio + web app branching
- **`ai-ucb-ai.md`** — Added Content Safety SDK, full archetype branching, MLflow model registry

#### B+-Tier (80–87) → A+
Files that were mostly complete but had gaps in specific dimensions:

- **`ai-ucb-pipeline.md`** — Added DQ gates, retry with exponential backoff, rollback hooks
- **`frontend-templates.md`** — Added security headers (HSTS, CSP, X-Frame-Options), MSAL patterns
- **`pricing.md`** — Added live Retail Prices API validation, cost model validation against real quotes
- **`rag-multimodal.md`** — Added RAGAS eval loop, cross-modal KG wiring, hybrid retrieval tuning
- **`web-ingest.md`** — Added circuit breaker pattern, politeness policy, configurable retry
- **`doc-templates.md`** — Added ADR decision log, Model Card per ML archetype, runbook template

---

## How to Extend

### Adding a new archetype
1. Add the archetype entry to `archetypes.md` (decision matrix row, full description, tradeoffs)
2. Add a branch in `ai-ucb-discover.md` decision tree
3. Add state fields in the state contract section of `ai-use-case-builder.md`
4. Add conditional blocks in each phase sub-skill (`ai-ucb-infra.md`, `ai-ucb-pipeline.md`, etc.)
5. Add Bicep modules to `infra-templates.md`, notebook templates to `pipeline-templates.md`
6. Update `pricing.md` with cost model for the new archetype

### Adding a new companion
1. Create the companion skill file in `companions/`
2. Register it in the orchestrator (`ai-use-case-builder.md`) companion manifest
3. Add dispatch logic in the relevant phase sub-skills that should call it
4. Add state fields the companion reads/writes to the state contract

### Modifying a reference file
Reference files are read-only from the orchestrator's perspective — they are templates and lookup tables, not executable logic. Modifying them does not require changes to the orchestrator, but does require updating the phase sub-skills that draw from them if the structure changes.

---

## Sync Workflow

There are three copies of these files. Keep them in sync manually after significant changes.

| Location | Path | Contents |
|----------|------|----------|
| **Live (main skills)** | `~/.claude/commands/` | `ai-use-case-builder.md` + 8 sub-skills + 5 companions |
| **Live (reference)** | `~/.claude/commands/ai-ucb/` | 7 reference files |
| **Repo** | `skills/ai-ucb/` | Full 21-file set, organized by category |
| **Backup** | `<USER_HOME>/OneDrive - <ORG>\Claude code\AI UCB\skills\` | Timestamped snapshots |

### Sync order (live → repo)
1. Edit live files in `~/.claude/commands/` (this is what Claude Code uses)
2. Copy updated files to the repo (`skills/ai-ucb/`) matching the directory structure
3. Snapshot to backup folder with date suffix if changes are substantial

### Repo directory structure
```
skills/ai-ucb/
├── README.md                        ← this file
├── orchestrator/
│   └── ai-use-case-builder.md
├── sub-skills/
│   ├── ai-ucb-discover.md
│   ├── ai-ucb-infra.md
│   ├── ai-ucb-pipeline.md
│   ├── ai-ucb-ai.md
│   ├── ai-ucb-frontend.md
│   ├── ai-ucb-test.md
│   ├── ai-ucb-docs.md
│   └── ai-ucb-deploy.md
├── companions/
│   ├── agentic-deploy.md
│   ├── doc-intelligence.md
│   ├── eval-framework.md
│   ├── rag-multimodal.md
│   └── web-ingest.md
└── reference/
    ├── archetypes.md
    ├── pricing.md
    ├── governance.md
    ├── infra-templates.md
    ├── pipeline-templates.md
    ├── frontend-templates.md
    └── doc-templates.md
```

---

## Key Design Decisions

These are the decisions that shaped the system. Before changing any of them, understand the rationale.

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Entry point | Orchestrator + sub-skills (not monolithic) | Monolithic prompts hit context limits and are hard to maintain independently; sub-skills can be versioned and tested in isolation |
| State format | JSON + MD checkpoints | JSON for machine-readable state passing; MD checkpoint summaries for human-readable audit trail |
| Azure subscription | Hybrid (UBI subscription for data, AI subscription for services) | Organizational reality — UBI infra lives in one sub, AI services in another |
| IaC tooling | Bicep AVM modules only (no raw ARM, no Terraform) | AVM gives consistent module interface, built-in RBAC, and stays current with Azure resource APIs |
| CI/CD | Azure DevOps only (no GitHub Actions) | Fortive standard; GitHub Actions not approved for production workloads |
| Notebook deployment | Databricks Asset Bundles (DABs) | DABs are the Databricks-recommended deployment unit; replaces older DBFS-based approaches |
| Deployment strategy | Blue/green as default | Safest for AI systems where rollback must be instant; canary available as option |
| Cost estimation | Azure Retail Prices API (live) | Static price tables go stale within weeks; live API call at discover time gives accurate estimates |
| Multi-region | Day 1, not day 2 | Retrofitting multi-region into existing infrastructure is painful; topology decisions at Phase 1 are much cheaper |
| Frontend options | Copilot Studio + React/Streamlit (not just one) | Different archetypes have different UI needs; Conversational AI fits Copilot Studio, RAG/ML fit React or Streamlit |
| Graph DB | Neo4j + Cosmos DB (Gremlin) both supported | Different deployment contexts — Neo4j for on-prem/VM, Cosmos for fully managed Azure-native |
| Eval framework | DeepEval + RAGAS + Garak + Phoenix unified | No single framework covers all needs: RAGAS for RAG, DeepEval for general LLM, Garak for safety, Phoenix for tracing |
| Doc output | MD + DOCX | Internal consumers prefer DOCX for sharing; MD for version control and rendering in docs sites |
| Companion pattern | Cross-cutting skills invoked by multiple phases | Avoids duplicating complex logic (e.g., eval setup) in every phase that needs it |
