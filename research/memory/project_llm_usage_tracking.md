---
name: LLM Gateway Usage Tracking
description: Usage tracking ETL for Team AI Enablement LLM Gateways — DuckDB on Azure VM, 12h cron, Delta Lake output
type: project
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
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

## Status (2026-04-13)
- **Phases 1-7 ALL COMPLETE** — system is live and scheduled
- **Phase 8: Infrastructure Health Check COMPLETE** (2026-04-13)
  - Automated health check runs as Step 3 of existing `Invoke-LLMUsageETL` runbook (same 12h schedule)
  - Script: `infra_health_check.py` on VM, accepts ARM token from runbook's Managed Identity
  - 6 check categories: RG status, AI Services, 12 model deployments, RBAC (25 users), 4 gateway web apps, Anthropic endpoint
  - Verdict logic: HEALTHY / DEGRADED / UNHEALTHY
  - Results → Delta table at `delta/metadata/health_checks/` (merge on check_run_id)
  - Non-blocking: health check failure does NOT prevent ETL from running
  - Runbook updated from 5 steps to 6 steps, published to Azure Automation (2026-04-13)
- First scheduled run: 2026-03-27 00:00 UTC
- DOCX report: `LLM_Usage_Tracking_What_Was_Deployed_20260326.docx` (44KB)
- **HNS enabled on `flkaienablement`** (2026-03-30, irreversible) — unlocks `DeltaLake.Table()` in PBI
  - Blockers cleared: 2 soft-delete artifacts (snapshot + deleted CSV) purged before migration
  - All consumers verified post-migration: LiteLLM (DFS), DuckDB ETL (Blob+DFS), PBI (local→ADLS)
- **DimDate full_date fix** (2026-04-13): changed from Python `date` → `strftime("%Y-%m-%d")` string. PyArrow `date32` was causing PBI DirectLake slicer to show empty. Schema overwritten with explicit `pa.string()` type.
- **PBI Health Check Page** (2026-04-13): Added Page 4 "Infrastructure Health" to DirectLake report via `add_health_check_page.py`. Script also fixes full_date slicers and README page.
  - 18 visuals: title banner, 2 slicers, explainer bar, 6 KPI cards (200px, gap=8), 2 charts (622px each), separator, header, 15-col detail table
  - 6 DAX measures: Total Checks, Healthy Runs, Health Rate, Avg Latency (ms), Deploys OK, RBAC Users
  - Key fixes in v2: (1) modelExtensions inside `layout["config"]` not top-level, (2) full_date slicers rebuilt as Dropdown with MMM-dd-yyyy format + underlying=519, (3) layout captured from user's manual PBI Desktop fixes (Y-band grid, high z-values 4000-19000), (4) README rewritten: Contents (5 pages) + Overview (health monitoring context) + Health/Insight docs sections, (5) shorter measure names to fit 200px cards, (6) no subtitle/slicer bg shape (removed per user preference)
  - Generator: `add_health_check_page.py` in `Usage Tracking/`, input: `_v2.pbix` (with user-added relationships), output: `_v2_new.pbix`
- **PBI Insights Page** (2026-04-13): Added Page 5 "Usage & Health Insights" — cross-table correlation between llm_usage and health_checks via dim_date relationships
  - 14 visuals: title banner, 2 slicers (date + verdict), 4 KPI cards (305px), combo chart + bar chart, separator, header, 10-col detail table
  - 4 new DAX measures on T_FACT: Total Requests, Requests (Healthy), Requests (Issues), Issue Impact Rate
  - Combo chart (`lineClusteredColumnComboChart`): bars=requests, line=latency, category=dim_date.full_date; multi-entity Extension block
  - Bar chart: health_checks.overall_verdict × llm_usage request count (cross-table via model relationships)
  - Bug fix: README textbox search must skip `contents_idx` to prevent insight docs overwriting the page list
  - Bug fix (2026-04-13): "Requests by Verdict" Missing_References — measure referenced by bar chart was never in modelExtensions. Added as 5th insight measure.
  - Bug fix (2026-04-13): Insight measures used stale non-TREATAS DAX because skip-if-exists logic preserved old expressions. Changed to replace-or-add.
  - Bug fix (2026-04-13): DataModel CRC corruption — `_replace_entry` deflated method=0 (stored) entries. Now respects original compression method.
  - Bug fix (2026-04-13): README update now preserves user's manual PBI Desktop position tweaks (updates text only, not positions)
  - Verdict explanation textbox added to Page 5 bottom (y=585-715): HEALTHY/DEGRADED/UNHEALTHY definitions with triggers
  - Total: 21 modelExtensions measures (11 KPI + 6 HC + 5 Insight, minus 1 shared Total Requests)
- **Backend Retrofit** (2026-04-13): Added `date_key` (int YYYYMMDD) + `etl_run_id` (correlation UUID) to health_checks Delta table; `correlation_id` to job_runs
  - Correlation flow: PowerShell `$CorrelationId` -> `ETL_CORRELATION_ID` env var -> both Python scripts
  - Backfill script: `backfill_historical_records.py` (idempotent, must run BEFORE first new ETL run to prevent schema overwrite fallback)
  - Critical: `_delta_merge_or_create` fallback is `write_deltalake(mode="overwrite")` which deletes history if schema mismatch occurs
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
- **Runbook**: `Invoke-LLMUsageETL` (PowerShell, 6 steps — updated 2026-04-13)
- **Schedule**: `Every12Hours` (0:00 and 12:00 UTC, starting 2026-03-27)

## Phase 8 Resources (Health Check)
- **Script**: `infra_health_check.py` (on VM at `/home/azureuser/`, local at `LLM Gateway/`)
- **Delta table**: `delta/metadata/health_checks/` (28 columns, merge on `check_run_id`)
- **ARM token flow**: Runbook MI → `Get-AzAccessToken` → env var `ARM_ACCESS_TOKEN` → Python `requests`
- **Runbook step**: [3/6] non-blocking, wrapped in try/catch
- **10 Delta tables total** (was 9): added `health_checks` alongside existing `job_runs` in metadata

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
