---
name: LLM Gateway Usage Tracking
description: Usage tracking ETL for Team AI Enablement LLM Gateways — DuckDB on Azure VM, 12h cron, Delta Lake output
type: project
---

LLM Gateway usage tracking system captures request logs from 4 LiteLLM gateway nodes and transforms them into Delta tables for cost allocation and usage analytics.

**Why:** Enterprise requirement for tracking AI token usage and costs across 16 Claude Code team members on Azure AI Foundry Marketplace billing.

**How to apply:** When working on the LLM Gateway, AI Enablement, or usage dashboards, reference the plan at `C:\Users\tmanyang\OneDrive - Fortive\AI\Claude code deployment\LLM Gateway\LLM_Gateway_Usage_Tracking_Plan.md` and the project memory at `C:\Users\tmanyang\OneDrive - Fortive\AI\Claude code deployment\CLAUDE.md`.

## Architecture
- **NOT Databricks** — DuckDB on Azure VM (`llm-usage-duckdb-vm`, Standard_B2ms, Ubuntu 24.04)
- **Schedule**: Every 12 hours with full VM lifecycle (start -> ETL -> deallocate)
- **Storage**: `flkaienablement` storage account, `litellm-logs` container (**HNS enabled 2026-03-30** — ADLS Gen2)
- **Output**: Delta Lake tables at `litellm-logs/delta/{bronze,silver,gold,metadata}/`
- **VM cost**: ~$5.27/month (vs ~$30-50/month for Databricks)

## Status (2026-03-30)
- **Phases 1-7 ALL COMPLETE** — system is live and scheduled
- First scheduled run: 2026-03-27 00:00 UTC
- DOCX report: `LLM_Usage_Tracking_What_Was_Deployed_20260326.docx` (44KB)
- **HNS enabled on `flkaienablement`** (2026-03-30, irreversible) — unlocks `DeltaLake.Table()` in PBI
  - Blockers cleared: 2 soft-delete artifacts (snapshot + deleted CSV) purged before migration
  - All consumers verified post-migration: LiteLLM (DFS), DuckDB ETL (Blob+DFS), PBI (local→ADLS)
- **PBI Report (Option A)**: `LLM_Gateway_Usage_Tracking_v2.pbix` — 3 pages (README, Dashboard, Data Table), 11 DAX measures, star schema
  - Base file: `AI Usage Tracking new base.pbix`, Generator: `generate_pbi_report_optionA.py`
  - Key fixes applied: formatInformation `format` enum removed (PBI v2.152 rejects), Cost Per Request inlined (no inter-measure refs), underlyingType 261 not 518 (chart axis fix)
- **PBI Report (Option B — DirectLake)**: `LLM_Gateway_Usage_Tracking_DirectLake.pbix` — same 3 pages, 11 measures, star schema
  - Base file: `AI Usage Tracking fabric lakehouse base.pbix` (DirectQuery to Fabric Lakehouse SQL endpoint)
  - Generator: `generate_pbi_report_optionB.py` (~1600 lines)
  - Relationships configured in base file (2026-03-31): 4 star-schema joins (fact→dim_date/nodes/models/users) + 2 agg joins
  - Key differences from Option A: `dataType: 3` (not 6), `currencyFormat: null`, Fabric table names with schema prefix (`"llmUsage llm_usage"`), DAX uses single quotes
  - Dashboard has "Requests by Node" chart (swapped from "Requests by User")
- **Fabric Lakehouse (Option B POC)**: `llm_usage_poc` in workspace `599f352a-0626-441a-b320-d4d60cf360d9`, Lakehouse ID `15e35cf6-b12c-45f1-a45c-2bc6b45fb211`
  - SQL endpoint: server `599f352a-0626-441a-b320-d4d60cf360d9`, database `llm_usage_poc`
- **Power Query scripts**: v4 (`Power_Query_M_Scripts_v4.txt`) — direct ADLS Gen2 via `DeltaLake.Table()`, no local Parquet needed, cloud refresh without gateway
  - Uses `fnGetDeltaTable` helper function + `StorageAccountUrl`/`ContainerPath` parameters
  - Fallback for MetadataJobRuns (corrupt Delta log) reads from `pbi-snapshot/` Parquet

## Phase 4 Results
- 9 Delta tables created in `abfss://litellm-logs@flkaienablement.dfs.core.windows.net/delta/`
- Bronze (5 rows, 4 cols), Silver (5 rows, 24 cols), Gold Fact (5 rows, 28 cols), Gold Agg (4 rows, 19 cols)
- DimLLMNode (4), DimLLMUser (16), DimLLMModel (3), DimDate (121), MetadataJobRuns (2)
- ETL runs in 1.4s for 5 blobs
- **Key discovery**: deltalake 1.5.0 requires `abfss://` scheme (not `az://`) with `account_name`/`account_key` storage options

## Phase 5 Resources
- **Automation Account**: `flk-llm-etl-automation` (Basic, East US 2, System Assigned MI)
- **Managed Identity**: `851f094f-9646-4518-8eb2-eac560b4a453`
- **RBAC**: VM Contributor + Run Command Admin on `llm-usage-duckdb-vm`
- **Runbook**: `Invoke-LLMUsageETL` (PowerShell)
- **Schedule**: `Every12Hours` (0:00 and 12:00 UTC, starting 2026-03-27)

## Key Findings
- LiteLLM azure_blob callback: flat `YYYY/MM/DD/HH/` path, no node field in JSON
- LiteLLM `AzureBlobStorageLogger` is a **DFS-only writer** (uses `azure.storage.filedatalake` SDK, not Blob SDK)
- Node derived from `model` field suffix (e.g., `claude-haiku-4-5-2-node1`)
- `status` is string "success"/"failure", not HTTP int
- Azure Marketplace output pricing is 74% higher than Anthropic direct ($130.33/M vs $75/M for Opus)
- deltalake 1.5.0: `az://` scheme → `TableNotFoundError`, must use `abfss://` with explicit account_name/account_key
- HNS migration: soft-delete artifacts (snapshots, deleted blobs) block validation even if soft-delete policy is disabled — must purge them manually
- `flkaienablement` has 4 containers: `litellm-logs` (active), `claude-{opus,sonnet,haiku}-logs` (unused)
- `delta/gold/fact/llmusage/` is a stale duplicate of `delta/gold/fact/llm_usage/` — canonical path uses underscore
