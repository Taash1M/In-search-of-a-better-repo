---
name: LLM Gateway Usage Tracking
description: Usage tracking ETL v3 — DuckDB on VM, 13 Delta tables, 5 gateways, .pbip report (6 pages), User Tracking page with AAD diagnostic data (real names/emails), 14 relationships, 5 dim_models (incl. Claude Code), 7 dim_nodes (incl. catch-all), Fabric shortcuts live for diagnostic_user_activity + dim_aad_users (2026-04-29)
type: project
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---
LLM Gateway usage tracking system captures request logs from 5 LiteLLM gateway nodes (was 4 — node-0 added 2026-04-23) and transforms them into Delta tables for cost allocation and usage analytics.

**Why:** Enterprise requirement for tracking AI token usage and costs across 16+ Claude Code team members on Azure AI Foundry Marketplace billing. Current gateway-level tracking identifies nodes but not individual users.

**How to apply:** When working on the LLM Gateway, AI Enablement, or usage dashboards, reference the plan at `<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\LLM Gateway\LLM_Gateway_Usage_Tracking_Plan.md` and the project memory at `<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\CLAUDE.md`.

## Per-User Tracking via Azure Diagnostic Logs (2026-04-27, was Phase 0 only on 2026-04-24)

The gateway-level ETL (LiteLLM logs → DuckDB → Delta) continues as-is for cost/token tracking. Diagnostic log processing is now **integrated into the ETL** (v3) for per-user identity resolution:

- **Data source**: `RequestResponse` diagnostic category → NDJSON blobs in `flkaienablement` storage (`insights-logs-requestresponse` container)
- **Record types**: Type A (callerIpAddress, objectId) + Type B (modelDeploymentName, modelName), joined by `correlationId`
- **Key insight**: `objectId` is blank with API key auth, populated with AAD auth → AAD migration enables per-user tracking
- **Resolution**: `objectId` → `dim_aad_users` cache (primary) → Graph API fallback (if token available)
- **Plan**: `Usage Tracking/Per_User_Usage_Tracking_Plan.md` (741 lines, 6 phases)
- **Implementation guide**: `Usage Tracking/Per_User_Usage_Tracking_Implementation_Guide.docx` (206 paragraphs, 14 tables, 6 D2 diagrams)
- **Coexistence**: Both API key and AAD auth work simultaneously (`disableLocalAuth=false`) — no disruption to existing users

### ETL v3 (deployed 2026-04-27, updated 2026-04-29)
- **Script**: `llm_usage_etl_v2.py` (~980 lines, v3 despite filename)
- **VM path**: `<VM_HOME>/llm_usage_etl.py`
- **New functions**: `_process_diagnostic_logs()`, `_resolve_object_ids()`, `_load_aad_user_cache()`, `_load_diag_watermark()`/`_save_diag_watermark()`, `_detect_node_from_deployment()`
- **New Delta tables**: `gold/audit/diagnostic_user_activity` (joined Type A+B records), `gold/dimensions/dim_aad_users` (objectId→name/email cache)
- **13 Delta tables total** (was 11): added `diagnostic_user_activity` + `dim_aad_users`
- **Integration**: Non-blocking — diagnostic log failure doesn't prevent rest of ETL
- **2026-04-29 updates**:
  - DIM_NODES: 7 entries (added "Shared" + "Unassigned" catch-all for orphan node_keys)
  - DIM_MODELS: 5 entries (added "Claude Code (Sonnet)" for `claude-code` deployment + "Unknown" catch-all)
  - VALID_NODE_KEYS: Silver processing validates node_key against valid set
  - user_activity email enrichment: post-query step joins DIM_USERS to populate user_email for node-level groups, also reads dim_aad_users Delta for AAD users
  - `schema_mode="overwrite"` on dim_date and user_activity Delta writes

### AAD User Sync (pre-ETL, deployed 2026-04-27)
- **Script**: `sync_aad_users.py` (standalone, repeatable)
- **VM path**: `<VM_HOME>/sync_aad_users.py`
- **Process**: Reads RBAC assignments on `flk-team-ai-enablement-ai` → resolves each objectId via Graph API → writes to `dim_aad_users` Delta table
- **Initial seed**: 35 rows (34 RBAC users + 1 Foundry Portal SP)
- **Runbook integration**: Step 4/7 in `Invoke-LLMUsageETL.ps1`, requires ARM + Graph tokens
- **Graph API permission**: MI needs `User.Read.All` (app permission) for automated resolution — pending tenant admin approval. Until then, sync works with interactive Graph token or pre-seeded cache.

### Confirmed AAD Users Flowing (2026-04-27)
| User | ObjectId | Auth | Operation | Status |
|------|----------|------|-----------|--------|
| Julian Knabe | `214fc112-34a5-4989-84de-d10234097b8d` | AAD | `Root_Wildcard_Post` (CLI inference) | Flowing |
| Danny Pouley | `c90a18b6-e85e-4bc7-9359-a7ca9c222275` | AAD | `Root_Wildcard_Post` (CLI inference) | Flowing |
| Kevin Davison | `e8853352-cea0-46a7-a3e5-617f156c2fdc` | AAD | Portal browsing | Flowing |
| Taashi Manyanga | `3ad87ec1-67e9-442d-9518-fb86b65a8393` | AAD | Portal browsing | Flowing |
| Sanjay Kalra | `fcfde7a6-41a7-404b-84c3-839abd5e437b` | AAD | (setup confirmed, pending log flush) | Pending |

### Key Technical Details
- **NDJSON `properties` field**: JSON-encoded **string**, not dict — must `json.loads(rec["properties"])` before accessing
- **`Root_Wildcard_Post`**: This is actual CLI model inference (confirmed)
- **HNS storage**: `flkaienablement` has HNS enabled (ADLS Gen2) — `azure-storage-file-datalake` SDK or account key needed for listing; `DefaultAzureCredential` blob API returns AuthorizationPermissionMismatch
- **Blob transfer to VM**: `az vm run-command` heredoc approach fails for large scripts — use blob upload + Python SDK download on VM instead
- **Azure CLI 2.85.0**: Installed on VM (2026-04-27) for future use

### VM Operational Reference (CRITICAL — avoid repeat troubleshooting)
- **Python venv**: `<VM_HOME>/etl_env/` — NOT system Python. System pip locked by PEP 668.
- **Activation**: `. etl_env/bin/activate` (POSIX dot-source). Do NOT use `source` — VM `az vm run-command` uses `sh`, not `bash`.
- **Installed packages** (in venv): `duckdb 1.2.2`, `pandas 3.0.1`, `deltalake 1.5.0`, `azure-storage-blob 12.28.0`, `azure-core 1.39.0`
- **NOT installed**: `azure-storage-file-datalake` — use `azure-storage-blob` or account key for ADLS access
- **`etl_env.sh`**: On VM at `<VM_HOME>/etl_env.sh` — exports `AZURE_STORAGE_CONNECTION_STRING` and `AZURE_BLOB_CONTAINER_NAME`. Sourced by `run_etl.sh` if conn string not already in env.
- **Querying Delta tables from VM**: Use `deltalake` Python library with `abfss://` scheme + account_key. Do NOT use DuckDB `delta_scan` — it can't authenticate to ADLS (returns `Identity not found`).
- **Gold Fact column names**: `model_deployment` (not `model_deployment_name`), `total_tokens`, `request_id`, `date_key`
- **Job metadata column names**: `run_start_time`, `run_duration_seconds`, `new_blobs_processed`, `bronze_rows_written`, `total_tokens_processed`, `correlation_id`

### Wrapper Script: `run_etl.sh` (deployed 2026-04-28, TESTED & VALIDATED)
- **VM path**: `<VM_HOME>/run_etl.sh`
- **Local path**: `LLM Gateway/run_etl.sh`
- **Purpose**: Single entry point — handles HOME, venv, etl_env.sh, runs sync + ETL + query
- **Flags**: `--sync`, `--etl`, `--query DATE_KEY`, `--all` (no args = --all)
- **Companion**: `<VM_HOME>/query_usage.py` — reports usage by node, diagnostic users, dimensions, last ETL run
- **Script deployment**: Upload to blob `_scripts/` → download on VM via Python Azure SDK

#### Ad-hoc ETL — THE COMMAND (copy-paste, no assembly needed):
```bash
# 1. Ensure correct subscription
az account set --subscription 77a0108c-5a42-42e7-8b7a-79367dbfc6a1

# 2. Start VM if needed
az vm start --resource-group flk-team-ai-enablement-rg --name llm-usage-duckdb-vm

# 3. Get tokens
ARM_TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)
GRAPH_TOKEN=$(az account get-access-token --resource https://graph.microsoft.com --query accessToken -o tsv)

# 4. Run full pipeline (sync + ETL + query)
az vm run-command invoke --resource-group flk-team-ai-enablement-rg --name llm-usage-duckdb-vm \
  --command-id RunShellScript --scripts \
  "export HOME=<VM_HOME>/ ARM_ACCESS_TOKEN='$ARM_TOKEN' GRAPH_ACCESS_TOKEN='$GRAPH_TOKEN' && <VM_HOME>/run_etl.sh --all" \
  --query "value[0].message" -o tsv

# 5. Deallocate VM
az vm deallocate --resource-group flk-team-ai-enablement-rg --name llm-usage-duckdb-vm --no-wait
```

#### Query-only (no tokens needed, reads from etl_env.sh):
```bash
az vm run-command invoke --resource-group flk-team-ai-enablement-rg --name llm-usage-duckdb-vm \
  --command-id RunShellScript --scripts \
  "export HOME=<VM_HOME>/ && . <VM_HOME>/etl_env.sh && <VM_HOME>/run_etl.sh --query 20260428" \
  --query "value[0].message" -o tsv
```

## PBI Report .pbip Updates (2026-04-29)

### Changes Made
- **POC → Node 4**: Renamed in ETL `DIM_NODES` (line 113 of `llm_usage_etl_v2.py`)
- **Month-Year slicer**: Added dropdown slicers using `dim_date.month_name` on all 4 data pages (Dashboard, Data Table, User Tracking, Usage & Health). Uses `month_name` (e.g., "April") not `year_month` — see Pending below.
- **User Tracking page**: New Page 4 (`c4d5e6f7a8b9c0d1e2f3/`) with 11 visuals:
  - Header shape, 3 slicers (month_name, full_date, node_display_name)
  - 4 KPI cards: Total Users (COUNTA), Total Requests (SUM), Total Cost USD (SUM), Total Tokens (SUM) — all from `user_activity`
  - Detail table: 9 columns (user_identifier, user_email, node_key, total_requests, total_cost_usd, total_tokens, primary_model, active_days, avg_cost_per_request)
  - 2 bar charts: Requests by User, Cost by User
- **ETL changes deployed to VM**: `year_month` added to `_generate_dim_date()`, `date_key` derived from `etl_timestamp` on `user_activity`, `schema_mode="overwrite"` on dim_date and user_activity writes
- **README page updated**: Page list includes User Tracking, architecture mentions 5 nodes + diagnostic logs
- **Page order**: README, Dashboard, Data Table, User Tracking, Infrastructure Health, Usage & Health Insights, Page 1
- **Relationships**: `user_activity.etl_run_id → job_runs.run_id` set to `isActive: false` to prevent ambiguous path through bidirectional `job_runs ↔ health_checks`

### Issues Encountered & Resolved
1. **Delta schema mismatch**: New columns caused `write_deltalake` failure → fixed with `schema_mode="overwrite"`
2. **PFE_XL_USERELATIONSHIP_AMBIGUOUS_PATH**: `user_activity→dim_date` created second path via `user_activity→job_runs↔health_checks→dim_date` → fixed by setting `etl_run_id→run_id` to inactive
3. **"Invalid column name 'year_month'"**: Fabric Lakehouse shortcut didn't sync new Delta column → attempted M query workaround
4. **M query folding failures**: `Table.AddColumn`/`Table.SelectColumns` don't fold in Fabric DirectQuery → reverted all M queries to simple table references
5. **diagnostic_user_activity not in Fabric**: No Lakehouse shortcut exists → removed TMDL entirely, reverted User Tracking to `user_activity` table
6. **Blob upload auth**: `--auth-mode login` failed → use `--auth-mode key`

### Current State (2026-04-29, fully deployed)
- All M queries are simple `Source{[Schema="llmUsage",Item="table_name"]}[Data]` — no computed columns
- **Fabric shortcuts LIVE** for `diagnostic_user_activity` + `dim_aad_users` (user added to Fabric portal + report)
- **14 relationships** in semantic model (was 11), no ambiguous paths
- **3 new relationships added**: diagnostic→dim_aad_users (object_id), diagnostic→dim_date (date_key), diagnostic→dim_nodes (node_key)
- User Tracking page detail table + requests bar chart now show **real AAD user names/emails** from `diagnostic_user_activity`
- AAD Users card: DISTINCTCOUNT(diagnostic_user_activity.user_name)
- Cost bar chart + cost/token KPI cards remain on `user_activity` (diagnostic has no cost data)
- Date + node slicers filter diagnostic data via the new relationships
- Month slicers use `month_name` (not chronological — shows "April", "March")
- **DIM_MODELS: 5 entries** (was 3) — added "Claude Code (Sonnet)" for `claude-code` deployment + "Unknown" catch-all
- **DIM_NODES: 7 entries** (was 5) — added "Shared" + "Unassigned" catch-all entries
- `claude-code` is the Claude Code CLI deployment name (~95% of traffic), mapped to Sonnet rates
- Silver processing validates node_key against VALID_NODE_KEYS set
- user_activity email enrichment from DIM_USERS for node-level groups
- README detail bar updated: "3 Facts + 1 Diagnostic + 5 Dimensions"
- **11 tables in semantic model**: llm_usage, daily_llm_usage, user_activity, diagnostic_user_activity, dim_date, dim_nodes, dim_models, dim_users, dim_aad_users, job_runs, health_checks

### Remaining Pending
1. **Fabric Lakehouse schema refresh for year_month/date_key**: New Delta columns (`year_month` on dim_date, `date_key` on user_activity) exist in Delta but Fabric may not have synced. Refresh table schemas in Fabric portal.
2. **After Fabric syncs**: Re-add `year_month` to dim_date TMDL, `date_key` to user_activity TMDL, add `user_activity→dim_date` relationship, switch month slicers from `month_name` to `year_month` for chronological "2026-04" format.

## Architecture Diagrams
- **Miro board**: `https://miro.com/app/board/uXjVHajHEbE=/` — Phase 3 ETL at x=11000
- **Azure-icon PNG**: `AI\Miro\Claude Code Deployment\architecture\phase3_azure_arch.png` (15 nodes: gateways → blob → VM → Bronze/Silver/Gold star schema)
- **D2 data flow**: `AI\Miro\Claude Code Deployment\dataflow-d2\phase3_etl_dataflow.d2` + `.svg`
- **Generator**: `diagrams/generate_azure_arch_v2.py` (uses azure_diagrams.py skill)

## Architecture
- **NOT Databricks** — DuckDB on Azure VM (`llm-usage-duckdb-vm`, Standard_B2ms, Ubuntu 24.04)
- **Schedule**: Every 12 hours with full VM lifecycle (start -> ETL -> deallocate)
- **Storage**: `flkaienablement` storage account, `litellm-logs` container (**HNS enabled 2026-03-30** — ADLS Gen2)
- **Output**: Delta Lake tables at `litellm-logs/delta/{bronze,silver,gold,metadata}/`
- **VM cost**: ~$5.27/month (vs ~$30-50/month for Databricks)

## Status (2026-04-23)
- **Phases 1-8 ALL COMPLETE** — system is live and scheduled
- **Phase 9: User Audit Table DEPLOYED & VALIDATED** (2026-04-23)
- **Phase 2 (Agentic AI Layer): PLAN COMPLETE** (2026-04-13) — see [project_phase2_agentic.md](project_phase2_agentic.md) and `Usage Tracking/Phase 2/` folder
- **Phase 8: Infrastructure Health Check COMPLETE** (2026-04-13)
  - Automated health check runs as Step 3 of existing `Invoke-LLMUsageETL` runbook (same 12h schedule)
  - Script: `infra_health_check.py` on VM, accepts ARM token from runbook's Managed Identity
  - 6 check categories: RG status, AI Services, 15 model deployments (was 12), RBAC (25 users), 5 gateway web apps (was 4), Anthropic endpoint
  - Verdict logic: HEALTHY / DEGRADED / UNHEALTHY
  - Results → Delta table at `delta/metadata/health_checks/` (merge on check_run_id)
  - Non-blocking: health check failure does NOT prevent ETL from running
  - Runbook updated from 5 steps to 6 steps, published to Azure Automation (2026-04-13)
- **Health Check MI Permissions Fix (2026-04-22)**
  - **Root cause**: Automation Account MI (`851f094f-9646-4518-8eb2-eac560b4a453`, `flk-llm-etl-automation`) only had VM Contributor + VM Administrator Login on the VM — no Reader on the resource group. All ARM API calls in health check returned 403 Forbidden.
  - **Impact**: 22 of 24 health check records were UNHEALTHY (false alarms). Only 2 HEALTHY runs (Apr 13, manual token during development).
  - **Fix**: Assigned **Reader** role on `flk-team-ai-enablement-rg` to MI `flk-llm-etl-automation`. Validated with manual runbook trigger — returned HEALTHY 6/6 checks, 12/12 deployments, 25 RBAC users.
  - **MI roles now**: VM Contributor (VM), VM Administrator Login (VM), Reader (RG)
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
  - Bug fix (2026-04-13): Cyclic reference on llm_usage — injected DataModel had dim_date→health_checks relationship, TREATAS created cycle. Removed DataModel injection + CROSSFILTER. TREATAS alone is one-way, no cycle.
  - Bug fix (2026-04-13): Removed DataModel injection entirely — import-mode base DataModel in DirectLake report caused publish failures (UnknownError). Script now only modifies Report/Layout.
  - **BUG RESOLVED (2026-04-22): PBIX ZIP manipulation is impossible in PBI 2.153+.** Any byte change to Report/Layout triggers MashupValidationError. Root cause: PBI Desktop validates an internal content hash on open. Fix: use .pbip format (Save As → Power BI Project). Decomposed JSON files are freely editable.
  - **PBIP approach (2026-04-22)**: Saved known-good .pbix as .pbip, added Page 4 + Page 5 + 10 measures via JSON file edits. Report opens in Desktop.
  - **PBIP fixes (2026-04-22)**: (1) Inlined all DAX bracket refs (report-level measures can't use `[MeasureName]`), (2) Fixed column names: deployments_found→deployments_total, rbac_users_found→rbac_user_count, total_check_duration_seconds→check_duration_seconds, (3) Derived date_key from check_timestamp via `INT(SUBSTITUTE(LEFT(check_timestamp,10),"-",""))` — health_checks has NO date_key column, (4) Page 4 slicer+bar chart switched from dim_date.full_date to health_checks.check_timestamp (no relationship between tables).
  - **Known limitation**: Page 5 combo chart `Avg Latency (ms)` line from health_checks won't filter by date since health_checks is an island table (no dim_date relationship). Would require adding relationship in semantic model.
  - **PUBLISHED SUCCESSFULLY (2026-04-22)**: All 5 pages working, 21 measures evaluating, report published to PBI Service.
  - Total: 21 reportExtensions measures (11 KPI + 6 HC + 5 Insight, minus 1 shared Total Requests)
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
- **Runbook**: `Invoke-LLMUsageETL` (PowerShell, 7 steps — updated 2026-04-27)
  - Steps: 1. Start VM → 2. Wait for running → 3. Health check → 4. AAD user sync → 5. ETL → 6. Deallocate → 7. Summary
- **Schedule**: `Every12Hours` (0:00 and 12:00 UTC, starting 2026-03-27)

## Phase 8 Resources (Health Check)
- **Script**: `infra_health_check.py` (on VM at `<VM_HOME>/`, local at `LLM Gateway/`)
- **Delta table**: `delta/metadata/health_checks/` (28 columns, merge on `check_run_id`)
- **ARM token flow**: Runbook MI → `Get-AzAccessToken` → env var `ARM_ACCESS_TOKEN` → Python `requests`
- **Runbook step**: [3/7] non-blocking, wrapped in try/catch
- **13 Delta tables total** (was 11): added `gold/audit/diagnostic_user_activity` + `gold/dimensions/dim_aad_users` (2026-04-27)

## Key Findings
- LiteLLM azure_blob callback: flat `YYYY/MM/DD/HH/` path, no node field in JSON
- LiteLLM `AzureBlobStorageLogger` is a **DFS-only writer** (uses `azure.storage.filedatalake` SDK, not Blob SDK)
- Node derived from `model` field suffix (e.g., `claude-haiku-4-5-2-node1`)
- `status` is string "success"/"failure", not HTTP int
- Azure Marketplace output pricing is 74% higher than Anthropic direct ($130.33/M vs $75/M for Opus)
- deltalake 1.5.0: `az://` scheme → `TableNotFoundError`, must use `abfss://` with explicit account_name/account_key
- HNS migration: soft-delete artifacts (snapshots, deleted blobs) block validation even if soft-delete policy is disabled — must purge them manually
- `flkaienablement` has 4 containers: `litellm-logs` (active), `claude-{opus,sonnet,haiku}-logs` (unused)

## User Audit Delta Table (DEPLOYED & VALIDATED — 2026-04-23)
- **Location**: `delta/gold/audit/user_activity/`
- **Purpose**: Per-user/per-key activity summary for adoption tracking, model preference, cost allocation, security/compliance, load balancing
- **Schema**: 37 columns across 6 categories:
  - **Identity (5)**: user_identifier, user_api_key_hash, user_email, node_key, is_known_user
  - **Activity Period (4)**: period_start, period_end, first_seen, last_seen
  - **Activity Metrics (6)**: total/successful/failed requests, active_days, avg_requests_per_day, avg/max duration
  - **Token & Cost (10)**: prompt/completion/total/cache tokens, total/input/output/cache costs, avg_tokens_per_request, avg_cost_per_request
  - **Model Preference (6)**: primary_model, unique_models_used, opus/sonnet/haiku requests, opus_pct
  - **Load Balancing (1)**: peak_hour_utc
  - **Metadata (2)**: etl_timestamp, etl_run_id
- **Grouping**: By `user_api_key_hash` (unique per gateway token); falls back to `node:{node_key}` when hash is empty
- **Rebuild strategy**: Full overwrite each ETL run (same as Gold Aggregate — table is small)
- **Non-blocking**: Failure does not prevent rest of ETL from completing
- **Implementation**: DuckDB SQL CTE in `llm_usage_etl_v2.py` (lines ~514-582)
- 11 Delta tables total (was 10): Bronze, Silver, Gold Fact, Gold Agg, **Gold Audit**, 4 Dims, 2 Metadata

### Deployment (2026-04-23)
- **Method**: Uploaded script to blob storage (`_scripts/llm_usage_etl_v2.py`), VM downloaded via `az vm run-command invoke`
- **VM path**: `<VM_HOME>/llm_usage_etl.py` (939 lines v3, was 642 v2)
- **Backup**: `<VM_HOME>/llm_usage_etl.py.bak` (original v2)

### Validation Results (manual ETL run, 2026-04-23)
- **Run ID**: `54d37278-36b0-4e62-9c83-f6a76304740f`
- **All 11 tables OK**: Bronze (5,178), Silver (5,178), Gold Fact (5,178), Gold Agg (76), **Gold Audit (8)**, DimNodes (5), DimUsers (16), DimModels (3), DimDate (121), JobRuns (66), HealthChecks (27)
- **274 new blobs** processed, 21.9M tokens, $56.33 estimated cost
- **8 user groups identified**:
  - 4 node-level groups (`node:{node_key}`, `is_known_user=False`) — bulk of traffic (node1: 2,979 reqs/$464, node2: 1,334/$295, node3: 416/$106, poc: 142/$22)
  - 4 key-level groups (hashed API keys, `is_known_user=True`) — lower volume, distinct gateway token users (node1: 138 reqs, node2: 91, node3: 47, poc: 31)
- **Insight**: Most traffic (96%) comes through without `user_api_key_hash`, meaning the LiteLLM callback doesn't consistently log the key hash. The 4 "known" users correspond to the 4 distinct gateway master keys.
- **DimLLMNode**: Correctly updated to 5 rows (poc, node0, node1, node2, node3)
- `delta/gold/fact/llmusage/` is a stale duplicate of `delta/gold/fact/llm_usage/` — canonical path uses underscore
