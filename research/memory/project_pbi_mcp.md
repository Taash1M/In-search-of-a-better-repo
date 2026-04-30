---
name: PBI Semantic Model MCP Server
description: FastMCP server for UBI Power BI semantic models — Phase 1 complete, 6 tools, 28 tests, 2 DOCX deliverables with azure_diagrams
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
## Overview

MCP server exposing UBI Power BI semantic models to Claude Code. Users connect and ask natural language questions about UBI data — the server provides schema, metadata, measures, relationships, lineage, and executes guarded DAX queries.

**Why:** Users need to ask questions about UBI data without knowing DAX syntax, PBI model structure, or which dataset to query. The MCP server bridges this gap.

**How to apply:** FastMCP Python server. PBI REST API for DAX execution. Pre-built YAML metadata from STM CSVs + Gold SQL. Both local (stdio) and shared (HTTP) deployment.

## Key Facts

- **Project dir**: `<USER_HOME>/OneDrive - <ORG>\Claude code\MCP\PBI MCP`
- **Package**: `pbi_semantic_mcp` (under `src/`)
- **PROJECT_MEMORY.md**: In project dir (detailed build log)
- **Plan file**: `<ADMIN_HOME>/.claude\plans\generic-hopping-coral.md`
- **Created**: 2026-04-10
- **Status**: Phase 1 foundation + docs complete — 6 tools, 28 tests, 2 DOCX deliverables with architecture diagrams
- **Metadata integrated into AI BI Tool** (2026-04-11): registry.py, loader.py, YAML data files copied + adapted into `fluke-ai-bi-tool/backend/app/metadata/` and `fluke-ai-bi-tool/data/`

## Phase Status

| Phase | Status |
|-------|--------|
| Phase 1 Week 1 (Foundation) | Complete |
| Phase 1 Week 2 (Core tools) | Complete (6 tools) |
| Phase 1 Week 3 (Resources + integration) | Pending |
| Phase 2 (Full metadata extraction) | Pending |
| Phase 3 (XMLA + advanced) | Pending |

## What's Built

- `config.py` — Pydantic Settings with Azure AD, workspace IDs, guardrail limits
- `client.py` — PowerBIClient with auto token refresh, multi-dataset, connection pooling
- `guardrails.py` — DAX validation (blocks 10 mutating keywords), TOPN injection, audit logger, rate limiter
- `server.py` — FastMCP instance with lifespan management
- `__main__.py` — CLI entry with transport selection
- `tools/datasets.py` — list_datasets, get_schema
- `tools/query.py` — query_data, get_sample_data
- `tools/measures.py` — get_measures, get_dax_examples
- `metadata/models.py` — Pydantic models (Dataset, Table, Column, Measure, Relationship, DAXExample)
- `metadata/loader.py` — YAML→Pydantic loader
- `metadata/registry.py` — In-memory registry with fuzzy search
- Bootstrap YAML: 20 datasets, SO Backlog full schema (6 tables, 4 measures, 5 relationships, 4 DAX examples), 8 shared DAX examples, 20 glossary terms
- 28 tests passing (guardrails + metadata)

## Documentation Deliverables

- **`What Was Deployed — PBI Semantic MCP Server.docx`** (443KB) — 6 azure_diagrams, executive preset, comprehensive deployment summary
- **`How to Use — PBI Semantic MCP Server.docx`** (324KB) — 3 azure_diagrams, installation + usage guide + troubleshooting
- Build script: `<USER_HOME>/AppData\Local\Temp\build_pbi_mcp_docs_v2.py`
