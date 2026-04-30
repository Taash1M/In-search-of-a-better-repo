---
name: AI BI Tool
description: Internal AI-powered BI tool — multi-agent architecture (Supervisor + 5 Workers), SharePoint UI, PBI + OneDrive connectors, zero data storage. All 8 phases + 3-wave production hardening (38 fixes) complete. 386 tests at 80% coverage. 8 DOCX + 4 PPTX deliverables. GA-ready for pilot (2026-04-13).
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
## Project Directory
`<USER_HOME>/OneDrive - <ORG>\AI\AI BI Tool\`
Code: `fluke-ai-bi-tool/` subdirectory

**Why:** Internal BI assistant accessible via SharePoint. Users point at PBI models or OneDrive files, answer a 3-5 question interview, then conversationally create publication-quality BI reports. Zero data storage.
**How to apply:** 8-phase plan (16 weeks). All 8 phases complete as of 2026-04-11. E2E production review (10 critical fixes) + MCP metadata integration completed 2026-04-11. **3-wave production hardening completed 2026-04-13** — 38 issues fixed (7 critical, 11 high, 16 medium, 4 low). 386 tests at 80% code coverage. 8 markdown docs updated. 5 beautified deliverables generated (4 DOCX + 1 PPTX). GA-ready for pilot deployment.

## Architecture
Multi-agent: Supervisor (Sonnet 4.6) → Data Agent (Haiku), Analysis Agent (Sonnet), Visual Agent (Sonnet, Plotly+Fluke theme), Export Agent (Haiku), Session Agent (Haiku, Cosmos DB).

Backend: FastAPI + DuckDB in-memory (per-session isolation via DuckDBSessionManager). Frontend: Streamlit MVP → SharePoint SPFx. LLM: Azure AI Foundry (circuit breaker: 5 fail → 60s open). Auth: Entra ID delegated tokens (WebSocket first-message auth). API versioned: `/api/v1/` prefix, health unversioned. Structured JSON logging with X-Request-ID correlation IDs.

## Key Design Decisions
- **Anton fork**: Extract tool-call loop, use LLMProvider/Scratchpad/tools — NOT subclass ChatSession (5000+ LOC terminal code)
- **Standalone LLM models**: ToolCall, Usage, LLMResponse etc. in foundry_provider.py, decoupled from Anton
- **Delegated token pass-through**: User's Entra token forwarded to PBI/Graph for Row-Level Security
- **MCP reuse**: client.py 95%, guardrails.py 100%, metadata models 100%, registry+loader 100%
- **MCP metadata integration**: MetadataRegistry loaded from YAML at startup, enriches all agents with glossary, schemas, DAX examples, relationships
- **Multi-workspace config**: prod/dev/qa workspace IDs with configurable default
- **Zero data storage**: BytesIO only, no disk writes
- **DuckDB per-session**: DuckDBSessionManager with LRU eviction at 100 sessions, GC idle >1hr when count >500
- **Defense in depth**: TLS 1.3, CORS allowlist (no wildcard), Pydantic validation, 1MB request limit, DAX allowlist+blocklist, rate limit 30/min, token budget 50K/hr, export buffer 50MB
- **Circuit breaker**: LLM provider — 5 consecutive failures → 60s open → half-open probe
- **API versioning**: /api/v1/ for business endpoints, /api/health unversioned
- **Structured logging**: JSON in production (LOG_FORMAT=json), X-Request-ID correlation IDs
- **Staging approval gate**: Manual approval required between staging and production deploys

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
- 55+ source files, ~7,500 LOC (added rate_limit.py, models.py, logging.py, DuckDBSessionManager, circuit breaker)
- 24 test files, ~3,200 LOC, 386 tests at 80% code coverage (fail_under=80)
- 9 Bicep files (5 modules + 3 param files + orchestrator)
- 3 CI/CD workflows (backend-ci with Trivy+pip-audit, infra-deploy, release with staging approval gate)
- 8 markdown docs (api-reference, architecture-decisions 16 ADRs, admin-runbook, onboarding, troubleshooting, user-guide, pilot-onboarding, ga-checklist)
- 4 YAML metadata files (datasets, glossary, dax_examples, streams/so_backlog)
- 4 PPTX presentations (06-Solution-Overview master + v2-fixed + v3-fixed wide + Implementation_20260412)
- 8 beautified DOCX deliverables (02-Plan, 03-Runbook, 04-User-Guide, 05-Deployment-Guide, Approach_Design, Architecture, Deployment_Guide, User_Guide)
- 15 architecture diagram PNGs
- 1 Dockerfile + .dockerignore
- 11 scripts (run_tests.py with --integration/--load, validate_deployment.py, rotate_secrets.py, + 8 original)

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

## Production Hardening — 3 Waves (2026-04-12 to 2026-04-13)
Production readiness audit identified 38 issues (7 critical, 11 high, 16 medium, 4 low). All resolved.

### Wave 1 — Critical & High Code Fixes (18 items)
W1.1 WebSocket first-message auth pattern, W1.2 CORS wildcard removed, W1.3 Per-session DuckDB isolation (DuckDBSessionManager, LRU@100), W1.4 Per-user rate limiter (30 req/min, PerUserRateLimiter), W1.5 Token budget enforcement (50K/hr), W1.6 Pydantic request/response models (ChatRequest, ExportRequest), W1.7 DAX allowlist+blocklist, W1.8 Session state sync to Cosmos, W1.10 Config startup validation (@model_validator), W1.11 LLM circuit breaker (5 fail→60s open→half-open), W1.12 Export buffer limit (50MB), W1.13 Extended audit logging, W1.14 Hardened interview auto-skip (2+ keyword matches for required), W1.15 Sanitized error responses (generic 500s, no stack traces), W1.16 Fixed Cosmos health check (lightweight query), W1.17 TLS 1.3 in Bicep, W1.18 Session GC (idle>1hr when count>500)

### Wave 2 — Infrastructure & Testing (12 items)
W2.1 RequestSizeLimitMiddleware (1MB→413), W2.2 WebSocket tests, W2.3 API versioning (/api/v1/), W2.4 Structured JSON logging (CorrelationIDMiddleware), W2.5 Dependency pinning (~= compatible release), W2.6 Docker image pinning (digest), W2.7 Trivy container scanning + pip-audit in CI, W2.8 Staging approval gate (validate-staging job), W2.9 ACR workload identity, W2.10 Integration test scaffolding, W2.11 Locust load test scenarios, W2.12 Coverage increase to 80% (386 tests, 24 test files)

### Wave 3 — Deployment Prep (5 items)
W3.1 validate_deployment.py (health, TLS, CORS checks), W3.2 rotate_secrets.py (Key Vault expiry monitor), W3.3 Updated all 8 markdown docs, W3.4 Key Vault references in App Service Bicep, W3.5 GA readiness checklist (31 items, 7 categories)

### New/Modified Source Files (Production Hardening)
- `auth/rate_limit.py` — PerUserRateLimiter + check_rate_limit FastAPI dependency
- `routes/models.py` — ChatRequest, ExportRequest Pydantic models
- `monitoring/logging.py` — JSONFormatter, CorrelationIDMiddleware, configure_logging
- `connectors/duckdb_engine.py` — DuckDBSessionManager added
- `llm/foundry_provider.py` — CircuitBreaker class added
- `main.py` — RequestSizeLimitMiddleware, lifespan updated with all new components
- `agents/supervisor.py` — Per-session engine binding, token tracking, session GC

### New Test Files (Coverage Push)
test_main_app.py (24), test_export_agent.py (30), test_sources_routes.py (11), test_auth_middleware.py (12), test_rate_limit.py (9), test_cosmos_store.py (24), test_telemetry_and_main.py (7)

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
**Docs**: user-guide, admin-runbook, architecture-decisions (16 ADRs), troubleshooting, onboarding, api-reference, pilot-onboarding, ga-checklist

## Deliverables

### Phase 1-8 DOCX (in fluke-ai-bi-tool/docs/)
- `02-E2E-Development-Plan.md` + `.docx` — 8-phase plan (638 lines)
- `03-Architecture-Admin-Runbook.docx` — Fortive-branded tech runbook with Azure architecture diagram (160KB)
- `04-User-Guide.docx` — Executive-preset user guide (42KB)
- `05-Deployment-Guide.docx` — 8-step deployment guide with 4 embedded diagrams (430KB)
- `architecture_diagram.png` + 4x deploy diagram PNGs

### Phase 1-8 PPTX (in fluke-ai-bi-tool/)
- `docs/06-Solution-Overview.pptx` — Master 19-slide (PptxGenJS, Midnight Executive, 6 diagrams, 1.1MB)
- `AI-BI-Tool-Presentation-v3-fixed.pptx` — 26-slide LAYOUT_WIDE with azure_diagrams (2963 KB)
- `AI-BI-Tool-Presentation-v2-fixed.pptx` — 26-slide LAYOUT_WIDE (2551 KB)
- 10 embedded diagram PNGs (pptx_*.png + _fix_diagrams/s*.png)

### Production Hardening Deliverables (2026-04-13, in deliverables/)
- `AI_BI_Tool_Approach_Design_20260412.docx` — Executive preset, Fortive palette, 11 sections: exec summary, problem, solution, principles, agent arch, tech stack, MCP metadata, security, 16 ADRs, hardening waves, cost model (46KB)
- `AI_BI_Tool_Architecture_20260412.docx` — Technical preset, 3 Azure architecture diagrams (system, agent flow, data flow), 9 sections: system overview, agent arch, data flow, resource inventory, security layers, monitoring, scaling, CI/CD, cost (43KB)
- `AI_BI_Tool_Deployment_Guide_20260412.docx` — Technical preset, 12 sections: prerequisites, Bicep IaC, 24 env vars, Docker, CI/CD, secret management, staging validation, monitoring, rollback, scaling, troubleshooting, GA checklist (46KB)
- `AI_BI_Tool_User_Guide_20260412.docx` — Executive preset, 11 sections: welcome, getting started, data sources, interview, templates, examples, exporting, sessions, limits, tips, FAQ (43KB)
- `AI_BI_Tool_Implementation_20260412.pptx` — 20-slide deck (PptxGenJS, Fortive Corporate palette): title, agenda, 5 section dividers, problem comparison, agent architecture, 7-step pipeline, tech stack table, 8-layer security, 3-wave hardening, Wave 1 detail, test coverage, CI/CD pipeline, cost model, GA readiness (31/31), pilot roadmap, thank-you. 3-stage QA passed (505KB)

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

## Deployment Readiness Assessment (Updated 2026-04-13)

**Status: GA-READY for pilot deployment. 31/31 GA checklist items complete.**

**What's validated (code level):**
- 386 unit tests pass at 80% code coverage (fail_under=80)
- All security layers implemented (auth, CORS, validation, rate limits, isolation, audit)
- Integration test scaffolding ready (conftest + smoke tests)
- Locust load test scenarios defined (10 concurrent, 60s sustained)
- Deployment validation script (health, TLS, CORS checks)
- Secret rotation monitoring script (Key Vault expiry check)
- CI pipeline: lint + test + pip-audit + Trivy + staging gate

**What still needs real-world validation:**
- No real deployment to Azure has happened
- No integration tests against live PBI REST API, Graph API, Cosmos DB, Azure AI Foundry
- No real user has ever used it
- Foundry LLM provider has never made a real API call

**Scale bottlenecks for 1000 users:**
- LLM quota: Sonnet 1,625 TPM / Haiku 100 TPM — needs 10-50x increase
- App Service: P1v3 (2 vCPU, 8GB) — needs P2v3+ with auto-scale
- DuckDB: Per-session memory — 100 concurrent ≈ 10-50GB RAM (LRU eviction at 100)
- PBI API: Rate-limited per tenant — 429s guaranteed at scale

**Path to production:**
1. Deploy to staging, run validate_deployment.py
2. Pilot with 5-10 users (use pilot-onboarding.md)
3. Monitor App Insights (errors, latency, token usage)
4. Collect feedback, iterate (2 weeks)
5. Expand to 25 users
6. GA rollout (week 7-8)

## Phase 2 — Automated Deployment Wizard (Planned)
CLI wizard (deploy.py) wrapping all 8 manual deployment steps with Claude Code integration for troubleshooting. Modules: preflight, provision, auth_setup, secrets, container, app_config, verify, troubleshoot. Features: resume from any step, auto-diagnosis, .deploy-state.json persistence.
