---
name: AI BI Tool
description: Internal AI-powered BI tool — multi-agent architecture (Supervisor + 5 Workers), SharePoint UI, PBI + OneDrive connectors, zero data storage. All 8 phases complete + MCP metadata integration (2026-04-11). E2E review + deployment guide + 19-slide master PPTX + 2 fixed wide presentations, 190 tests, 4 DOCX + 3 PPTX deliverables, 15 architecture diagrams.
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
## Project Directory
`C:\Users\tmanyang\OneDrive - Fortive\AI\AI BI Tool\`
Code: `fluke-ai-bi-tool/` subdirectory

**Why:** Internal BI assistant accessible via SharePoint. Users point at PBI models or OneDrive files, answer a 3-5 question interview, then conversationally create publication-quality BI reports. Zero data storage.
**How to apply:** 8-phase plan (16 weeks). All 8 phases complete as of 2026-04-11. E2E production review completed 2026-04-11 — 10 critical issues fixed. MCP metadata integration completed 2026-04-11 — MetadataRegistry from PBI MCP Server integrated into all agents. 190 tests passing (167 original + 23 metadata). Ready for pilot deployment.

## Architecture
Multi-agent: Supervisor (Sonnet 4.6) → Data Agent (Haiku), Analysis Agent (Sonnet), Visual Agent (Sonnet, Plotly+Fluke theme), Export Agent (Haiku), Session Agent (Haiku, Cosmos DB).

Backend: FastAPI + DuckDB in-memory. Frontend: Streamlit MVP → SharePoint SPFx. LLM: Azure AI Foundry. Auth: Entra ID delegated tokens.

## Key Design Decisions
- **Anton fork**: Extract tool-call loop, use LLMProvider/Scratchpad/tools — NOT subclass ChatSession (5000+ LOC terminal code)
- **Standalone LLM models**: ToolCall, Usage, LLMResponse etc. in foundry_provider.py, decoupled from Anton
- **Delegated token pass-through**: User's Entra token forwarded to PBI/Graph for Row-Level Security
- **MCP reuse**: client.py 95%, guardrails.py 100%, metadata models 100%, registry+loader 100%
- **MCP metadata integration**: MetadataRegistry loaded from YAML at startup, enriches all agents with glossary, schemas, DAX examples, relationships
- **Multi-workspace config**: prod/dev/qa workspace IDs with configurable default
- **Zero data storage**: BytesIO only, no disk writes
- **DuckDB per-session**: In-memory SQL for multi-source JOINs

## Phase Status
| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Foundation & Anton Adaptation | COMPLETE (2026-04-10) |
| 2 | Data Connectors | COMPLETE (2026-04-10) |
| 3 | Core Agents (Analysis, Visual, Interview) | COMPLETE (2026-04-11) |
| 4 | Export Engine & Session Persistence | COMPLETE (2026-04-11) |
| 5 | Monitoring, Security & Testing | COMPLETE (2026-04-11) |
| 6 | Streamlit Frontend Upgrade | COMPLETE (2026-04-11) |
| 7 | Infrastructure & Deployment | COMPLETE (2026-04-11) |
| 8 | Documentation Suite | COMPLETE (2026-04-11) |

## Project Stats
- 49 source files, ~6,030 LOC (added registry.py, loader.py)
- 19 test files, 1,890+ LOC, 190 tests (167 original + 23 metadata integration)
- 9 Bicep files (5 modules + 3 param files + orchestrator)
- 3 CI/CD workflows (backend-ci, infra-deploy, release)
- 6 markdown docs (updated with MCP metadata integration) + 4 beautified DOCX + 15 architecture diagram PNGs
- 4 YAML metadata files (datasets, glossary, dax_examples, streams/so_backlog)
- 3 PPTX presentations (06-Solution-Overview master + v2-fixed + v3-fixed wide format)
- 1 Dockerfile + .dockerignore
- 8 scripts (run_tests.py, generate_docs.py, generate_deploy_diagrams.py, generate_deployment_guide.py, generate_pptx_diagrams.py, gen_wide_diagrams.py, patch_pptx.py, audit_pptx.py)

## E2E Production Review (2026-04-11)
10 critical issues identified and fixed:
1. **CORS hardened** — settings-driven origins, no wildcard in prod
2. **Streaming tool name preservation** — current_tool_name tracking in foundry_provider.py
3. **WebSocket authentication** — full JWT validation per message in chat.py
4. **Data Agent query execution** — SQL extraction + DuckDB execution pipeline
5. **SQL injection prevention** — double-quote escaping in analysis_agent.py
6. **Cosmos health check** — 404 vs real error distinction in cosmos_store.py
7. **Token tracker memory cleanup** — auto-cleanup expired buckets in token_tracker.py
8. **Export format validation** — whitelist (csv, excel, html) in export.py
9. **Narrative extraction safety** — empty/missing/non-dict handling in export.py
10. **Inline test suite** — run_tests.py with --quick/--coverage/--security/--lint/--all modes

## Implemented Components
**Core**: config.py, main.py, __main__.py
**Auth**: entra.py, middleware.py, models.py
**LLM**: foundry_provider.py (standalone models, AsyncAnthropic)
**Agents**: base.py, supervisor.py (5-phase conversation flow), data_agent.py, analysis_agent.py, visual_agent.py, export_agent.py, session_agent.py
**Connectors**: pbi_client.py, pbi_guardrails.py, onedrive_client.py, duckdb_engine.py
**Metadata**: models.py, schema_discovery.py, registry.py (MCP-integrated), loader.py (YAML→Registry)
**Theme**: fluke_theme.py (Plotly template), templates.py (8 report templates)
**Interview**: engine.py (5-dimension, auto-skip)
**Export**: csv_export.py, excel_export.py (Fluke-branded), html_export.py (interactive Plotly)
**Session**: models.py, cosmos_store.py (graceful degradation)
**Monitoring**: token_tracker.py, usage.py, telemetry.py, health.py (5-component probes)
**Routes**: health.py, chat.py, sources.py, export.py, sessions.py
**Frontend**: streamlit/app.py (Fluke-branded, source browser, export, sessions)
**Infra**: main.bicep + modules (app-service, cosmos-db, key-vault, app-insights, container-registry)
**CI/CD**: backend-ci.yml, infra-deploy.yml, release.yml
**Docs**: user-guide, admin-runbook, architecture-decisions (11 ADRs), troubleshooting, onboarding, api-reference

## Deliverables
- `02-E2E-Development-Plan.md` — 8-phase plan (638 lines)
- `02-E2E-Development-Plan.docx` — Beautified DOCX version
- `docs/03-Architecture-Admin-Runbook.docx` — Fortive-branded tech runbook with embedded Azure architecture diagram (160KB)
- `docs/04-User-Guide.docx` — Executive-preset user guide (42KB)
- `docs/architecture_diagram.png` — Azure architecture diagram (10 services, 8 connections, azure_diagrams module)
- `docs/05-Deployment-Guide.docx` — Comprehensive 8-step deployment guide with 4 embedded diagrams, Phase 2 wizard design (430KB)
- `docs/deploy_01_resources.png` — Azure resource landscape diagram
- `docs/deploy_02_cicd.png` — CI/CD pipeline flow diagram
- `docs/deploy_03_auth_data.png` — Authentication & data flow diagram
- `docs/deploy_04_sequence.png` — 8-step deployment sequence diagram

- `docs/06-Solution-Overview.pptx` — Master 19-slide presentation (PptxGenJS, Midnight Executive palette, 6 embedded diagrams, 1.1MB)
- `docs/pptx_agent_arch.png` — Multi-agent architecture diagram
- `docs/pptx_data_flow.png` — E2E data flow diagram
- `docs/pptx_security.png` — Security architecture diagram
- `docs/pptx_tech_stack.png` — Technology stack flow diagram

- `AI-BI-Tool-Presentation-v3-fixed.pptx` — 26-slide LAYOUT_WIDE (13.3x7.5in) presentation, all blank slides filled with azure_diagrams, overflow fixes applied (2963 KB)
- `AI-BI-Tool-Presentation-v2-fixed.pptx` — 26-slide LAYOUT_WIDE, same fixes as v3 (2551 KB)
- `_fix_diagrams/s05_multi_agent.png` — Multi-agent architecture (8 services, 7 connections)
- `_fix_diagrams/s09_data_flow.png` — E2E data flow (8 stages)
- `_fix_diagrams/s12_user_flow.png` — User experience flow (6 stages)
- `_fix_diagrams/s16_viz_export.png` — Visualization & export pipeline (5 stages)
- `_fix_diagrams/s19_security_infra.png` — Security & infrastructure (8 services, 7 connections)
- `_fix_diagrams/s21_azure_arch.png` — Azure infrastructure (10 services, 10 connections)

## MCP Metadata Integration (2026-04-11)

Integrated PBI MCP Server's metadata layer directly into backend (no network dependency):

**New modules**: `metadata/registry.py`, `metadata/loader.py` (adapted from MCP, import paths changed)
**YAML data**: `data/datasets.yaml` (20 datasets), `data/glossary.yaml` (20+ terms), `data/dax_examples.yaml` (8 patterns), `data/streams/so_backlog.yaml` (6 tables, 4 measures, 5 relationships)

**6 integration points wired**:
1. **Data Agent** — glossary + schema + DAX examples injected into LLM prompt via `_build_registry_context()`
2. **Analysis Agent** — table relationships for smarter JOINs via `_build_relationship_context()`
3. **Supervisor** — dataset recommendation based on question keywords via `_build_registry_context()`
4. **Supervisor** — glossary passed to interview engine for enriched auto-detection
5. **Interview Engine** — glossary terms added as auto-skip keywords (KEY_METRICS + FOCUS_FILTER)
6. **Config** — multi-workspace (prod/dev/qa) + `metadata_dir` setting

**Modified files**: config.py, main.py, data_agent.py, analysis_agent.py, supervisor.py, interview/engine.py
**New test file**: `tests/unit/test_metadata_registry.py` (23 tests)
**Docs updated**: All 6 markdown docs (ADR-010/011 added, metadata config section, troubleshooting, user guide FAQ)

## Deployment Readiness Assessment (2026-04-11)

**Status: Solid prototype — NOT production-ready for scale**

**What's validated:**
- 190 unit tests pass (mocked dependencies)
- Code compiles, imports correctly, architecture is sound
- All 8 phases of development plan implemented

**What has NOT been validated:**
- No real deployment to Azure has happened
- No integration tests against live PBI REST API, Graph API, Cosmos DB, Azure AI Foundry
- No real user has ever used it
- Foundry LLM provider has never made a real API call
- DAX execution with delegated tokens untested E2E
- No load testing performed

**Scale bottlenecks for 1000 users:**
- LLM quota: Sonnet 1,625 TPM / Haiku 100 TPM — needs 10-50x increase
- App Service: P1v3 (2 vCPU, 8GB) — needs P2v3+ with auto-scale
- DuckDB: Per-session memory — 100 concurrent ≈ 10-50GB RAM
- PBI API: Rate-limited per tenant — 429s guaranteed at scale
- Cosmos DB: Serverless cold starts — needs provisioned throughput

**Path to production:**
1. Pilot with 5-10 users on dev — surface real integration bugs
2. Increase Foundry TPM quotas
3. Run real integration tests (PBI/Graph/Cosmos)
4. Load test with Locust
5. Security review + pen test
6. Scale infrastructure

## Phase 2 — Automated Deployment Wizard (Planned)
CLI wizard (deploy.py) wrapping all 8 manual deployment steps with Claude Code integration for troubleshooting. Modules: preflight, provision, auth_setup, secrets, container, app_config, verify, troubleshoot. Features: resume from any step, auto-diagnosis, .deploy-state.json persistence.
