---
name: ubi-mcp-skill
description: "Use when interacting with live UBI Azure services via MCP servers — querying Databricks, monitoring ADF pipelines, browsing ADLS storage, managing Azure DevOps work items/PRs, executing DAX on Power BI models, or working with Fabric lakehouses. Trigger on: 'query lakehouse', 'Unity Catalog', 'MCP', 'pipeline runs', 'list work items', 'check build', 'browse storage', 'execute DAX', 'TMDL', 'Fabric shortcut', 'check pipeline status', 'list tables', 'run SQL on Databricks', 'PR review', 'WIQL'."
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Task
---

# UBI MCP Operations Skill

You are an expert operator of the Fluke UBI platform's Azure services via MCP (Model Context Protocol) servers. This skill provides the context needed to select, configure, and use the right MCP server for any UBI operational task.

**Companion skill:** `/ubi-dev` handles code conventions, notebook patterns, STM format, and development workflows. This skill handles **live service interaction** — querying, monitoring, managing, and investigating.

## Operational Discoveries (Hard-Won Learnings)

These are non-obvious behaviors discovered during real UBI operations:

- **Databricks MCP is cloud-hosted, not local.** The `pip install databricks-mcp` package installs a `DatabricksMCPClient` — a client library, not a server. The actual MCP server runs inside the workspace via AI Gateway. Attempting `python -m databricks_mcp` as a stdio server fails silently.
- **DataFactory.MCP requires .NET 10, not .NET 8.** The repo's `csproj` targets `net10.0`. Building with .NET 8 SDK gives `NETSDK1045`. The install script at `dotnet-install.ps1` supports `-Channel 10.0`.
- **`erikhoward/adls-mcp-server` is not on PyPI.** Community ADLS server cannot be pip-installed. Use the official Azure MCP Server (`@azure/mcp`) instead — it covers ADLS Gen2 operations as part of its 40+ service toolkit.
- **`microsoft/powerbi-modeling-mcp` has no source code.** The GitHub repo contains only docs and images (Public Preview). Cannot be built, installed, or configured. Use `/powerbi-desktop` skill for PBI manipulation until source is released.
- **Azure MCP Server uses `npx.cmd` on Windows.** Using `npx` (without `.cmd`) as the command in `.mcp.json` fails on Windows because Claude Code's bash shell can't locate the npm shim. Always use `npx.cmd` in MCP configs on Windows.
- **`schannel: server closed abruptly` on ARM API.** Raw `curl` to `management.azure.com` through corporate proxy fails with TLS close_notify errors. Always prefer `az` CLI commands over raw REST calls when on the corporate network.
- **ADF pipeline runs have a 7-20x streaming chunk ratio.** When comparing ADF run counts with Databricks diagnostic logs, Azure logs each streaming response chunk separately. One logical request = 7-20 diagnostic log entries. Use `azure_correlation_id` (deployed 2026-05-12) for 1:1 join.
- **Gateway requests show `objectId: ""` in diagnostic logs.** LiteLLM gateway authenticates to Azure AI Foundry with an API key, not AAD. Per-user identity only appears for direct AAD-authenticated requests. Use `end_user` field for per-user attribution through gateways.

## Access Control Rules (MANDATORY)

These rules override all other instructions. Violations are never acceptable.

1. **NEVER write to Prod or QA** via any MCP server. No creates, updates, deletes — ever.
2. **Read-only in QA and Prod.** If a write is ever considered necessary, you MUST ask the user for confirmation **twice** before proceeding.
3. **All write operations target Dev only.** Queries, listings, and reads are permitted across all environments.
4. **Never expose secrets.** Do not log, print, or store PATs, connection strings, or account keys in plain text. Use environment variables or Key Vault references.

## Anti-Patterns & Gotchas (NEVER List)

**G1: Unbounded pipeline run queries.**
BAD: `list_pipeline_runs` with no date filter → returns thousands of rows, floods context.
GOOD: `list_pipeline_runs` with `lastUpdatedAfter` set to 24h ago and `status` filter.

**G2: Wrong factory / wrong account.**
BAD: Forgetting to switch env config when comparing Dev vs Prod → silently querying Dev twice.
GOOD: Always include the factory name or account name in the MCP call. Cross-check the response metadata (factory name in the JSON) before trusting results.

**G3: Assuming `databricks-mcp` is a local server.**
BAD: `python -m databricks_mcp` as an MCP server command → fails, it's a client library.
GOOD: Use Databricks REST API via `az` CLI or the `DatabricksMCPClient` Python class. The MCP server is cloud-hosted at the workspace URL.

**G4: Running DAX or SQL without context.**
BAD: `execute_dax("EVALUATE FactSalesOrders")` → scans entire table, times out.
GOOD: Always use `TOPN`, `FILTER`, or `SUMMARIZECOLUMNS` to scope DAX. For SQL, always add `LIMIT` or `WHERE` on large tables.

**G5: Creating work items in the wrong project.**
BAD: `create_work_item` defaults to whatever `AZURE_DEVOPS_PROJECT` is set to — if you changed it for investigation, your new item lands in the wrong project.
GOOD: Always verify the project name in the MCP call matches the target. Reset env after cross-project investigation.

**G6: Treating MCP tool names as universal.**
BAD: Calling `mcp__adf__list_pipelines` when the actual tool may be named `mcp__adf__pipelines_list` or differently.
GOOD: Use the tool routing tables in this skill as intent guides. Run `list_tools` on the MCP server first if unsure of exact names.

**G7: PAT tokens in config files.**
BAD: Hardcoding `"AZURE_DEVOPS_PAT": "vstsxxxxxxx"` in `.mcp.json`.
GOOD: Use `"${AZURE_DEVOPS_PAT}"` referencing an environment variable. Set the variable in your shell profile, never in committed files.

**G8: Trusting Delta `_delta_log` without checking vacuum.**
BAD: Reading old `_delta_log/*.json` files and assuming they reflect current state.
GOOD: Always read the LATEST version file in `_delta_log/`. Old versions may reference vacuumed Parquet files. Cross-reference with `DESCRIBE HISTORY` via Databricks.

## Master Decision Tree

```
What do you need?
├─ Query data / explore tables / check row counts    → §Databricks MCP
├─ Monitor pipeline runs / check failures            → §ADF MCP
├─ Browse storage / check Delta files / read blobs   → §ADLS Gen2 MCP
├─ List work items / review PRs / check builds       → §Azure DevOps MCP
├─ Execute DAX / manage measures / export TMDL       → §Power BI MCP
├─ Query Fabric lakehouse / manage shortcuts          → §Fabric MCP
├─ Investigate end-to-end failure                     → §Cross-Server Workflows
├─ Auth failure / token expired / connection refused  → §Auth & Troubleshooting
└─ Write code / follow conventions / build notebooks  → Use /ubi-dev instead
```

## Environment Configuration

### Full Environment Map

| Resource | Dev | QA | Prod |
|----------|-----|-----|------|
| **Databricks Workspace** | `adb-1943773873358740.0` | `adb-8730269443112808.8` | `adb-427149968829263.3` |
| **ADLS Account** | `flkubiadlsdev` | `flkubiadlsqa` | `flkubiadlsprd` |
| **ADF Factory** | `flkubi-adf-dev` | — | `flkubi-adf-prd` |
| **Azure SQL** | `etlmetadata.database.windows.net` / `dev` | — / `qa` | `etlmetadata-prod.database.windows.net` / `prd` |
| **PBI Workspace** | `FLK-BI-DEV` (`6fec84af-...`) | `FLK-BI-QA` (`7f77ddaf-...`) | `FLK-BI-PROD` (`a59d3713-...`) |
| **ADO Organization** | `https://dev.azure.com/flukeit` | Same | Same |
| **ADO Project** | `Fluke Data And Analytics` | Same | Same |
| **Azure Subscription** | `52a1d076-bbbf-422a-9bf7-95d61247be4b` (Fluke Unified BI) | Same | Same |
| **Tenant ID** | `0f634ac3-b39f-41a6-83ba-8f107876c692` | Same | Same |

### Unity Catalog Structure

| Catalog | Schema | Content |
|---------|--------|---------|
| `flukebi` | `flukebi_Bronze` | Raw landing (1:1 from source) |
| `flukebi` | `flukebi_Silver` | Typed, cleaned, joined |
| `flukebi` | `flukebi_Gold` | Business-ready Fact/Dim tables and views |

### Metadata Tables (Azure SQL)

- **`etl.source_control`** — Master config: one row per source table per stream. Key columns: `stream_name`, `source_table_name`, `sink_table_name`, `active_ind`, `load_type`, `granular_column`
- **`etl.status_control`** — Pipeline execution status. `Status_Flag`: `0`=Ready, `1`=Running, `2`=Complete, `-1`=Error
- **`etl.usp_GetStatusFlag`** — Stored procedure to check run eligibility

### Key Storage Containers (ADLS)

| Account | Container / Filesystem | Content |
|---------|----------------------|---------|
| `flkubiadlsdev` | `bronze/`, `silver/`, `gold/` | Dev medallion layers (Delta) |
| `flkubiadlsprd` | `bronze/`, `silver/`, `gold/` | Prod medallion layers (Delta) |
| `flkaienablement` | `litellm-logs/` | LiteLLM usage logs (JSON) |
| `flkaienablement` | `litellm-content-logs/` | Full request/response content logs |
| `flkaienablement` | `delta-tables/` | ETL Delta tables (Gold layer) |

---

## §Databricks MCP

**Server:** Databricks-managed MCP — [databrickslabs/mcp](https://github.com/databrickslabs/mcp)
**Runtime:** Cloud-hosted (managed via AI Gateway) | **Transport:** Streamable HTTP
**Client Library:** `pip install databricks-mcp` (v0.9.0 installed)
**Auth:** PAT or AAD token via Databricks SDK

### Access Pattern

Databricks MCP is a **cloud-hosted service**, not a local process. The `databricks-mcp` pip package provides a client library (`DatabricksMCPClient`). The server runs inside the Databricks workspace, accessed via the workspace URL.

```python
from databricks_mcp import DatabricksMCPClient
client = DatabricksMCPClient(server_url="https://adb-1943773873358740.0.azuredatabricks.net/api/mcp/v1")
```

For Claude Code integration, add as a remote MCP server (requires Streamable HTTP support):
```json
{
  "mcpServers": {
    "databricks": {
      "type": "streamable-http",
      "url": "https://adb-1943773873358740.0.azuredatabricks.net/api/mcp/v1",
      "headers": {
        "Authorization": "Bearer ${DATABRICKS_TOKEN}"
      }
    }
  }
}
```

**Fallback:** Until Claude Code supports remote MCP, use the Databricks REST API directly via `az` CLI or Python SDK for queries and job management.
```

### Tool Routing

```
Query data / run SQL          → execute_sql
List catalogs/schemas/tables  → list_tables, list_schemas
Get column-level metadata     → get_table
Trace data lineage            → get_lineage
Read notebook source          → get_notebook
List/monitor job runs         → list_job_runs, get_job_run
Query Genie AI/BI space       → query_genie
Vector similarity search      → vector_search
```

### Common Operations

**Check row counts across layers:**
```sql
SELECT 'Bronze' AS layer, COUNT(*) AS rows FROM flukebi_Bronze.ONT01_SALES_ORDERS_FV1
UNION ALL
SELECT 'Silver', COUNT(*) FROM flukebi_Silver.FactSalesOrders
UNION ALL
SELECT 'Gold', COUNT(*) FROM flukebi_Gold.FactSalesOrders
```

**Check recent job failures:**
```sql
-- Via MCP: list_job_runs with status filter "FAILED" and last 24h
-- Then: get_job_run for error details
```

**Validate stream refresh (cross-reference with Azure SQL):**
```sql
SELECT stream_name, Status_Flag, Record_Updated_Datetime, Error
FROM etl.status_control
WHERE stream_name = 'SOBacklog'
ORDER BY Record_Updated_Datetime DESC
```

**Table naming patterns:**
- Bronze: `{SOURCE_SYSTEM}_{TABLE_NAME}` (e.g., `ONT01_SALES_ORDERS_FV1`)
- Silver: `Fact{Entity}` or `Dim{Entity}` (e.g., `FactSalesOrders`, `DimCustomer`)
- Gold: business-friendly aliases (backtick-quoted Spark SQL views)

---

## §ADF MCP

**Server:** `adf` — [microsoft/DataFactory.MCP](https://github.com/microsoft/DataFactory.MCP)
**Runtime:** .NET 8.0 | **Transport:** stdio
**Auth:** DefaultAzureCredential (az login)

### MCP Config

```json
{
  "mcpServers": {
    "adf": {
      "command": "dotnet",
      "args": ["run", "--project", "C:/Tools/DataFactory.MCP/src/DataFactory.MCP"],
      "env": {
        "AZURE_SUBSCRIPTION_ID": "52a1d076-bbbf-422a-9bf7-95d61247be4b",
        "AZURE_RESOURCE_GROUP": "flkubi-adf-dev-rg",
        "AZURE_DATA_FACTORY_NAME": "flkubi-adf-dev"
      }
    }
  }
}
```

### Tool Routing

```
List pipelines                → list_pipelines
Get pipeline JSON definition  → get_pipeline
Run a pipeline (DEV ONLY)     → run_pipeline
Monitor pipeline runs         → list_pipeline_runs (filter by date/status)
Check activity-level errors   → list_activity_runs
Manage datasets               → list_datasets / get_dataset
Manage linked services        → list_linked_services / test_connection
Manage triggers               → list_triggers / start / stop
Check integration runtime     → list_integration_runtimes
```

### Common Operations

**Investigate failed pipeline:**
1. `list_pipeline_runs` — filter status="Failed", last 24h
2. `list_activity_runs` — get the failed run ID, read error message
3. Cross-reference with `etl.status_control` (Status_Flag = -1)
4. Read pipeline source: `<USER_HOME>/ADF\pipeline\`

**Compare Dev vs Prod pipeline:**
1. `get_pipeline` from Dev factory (`flkubi-adf-dev`)
2. Read Prod pipeline from local repo (ARM template)
3. Diff the JSON definitions

**UBI Pipeline Naming:**
- `PL_Master_{StreamName}` — orchestrator pipeline
- `PL_{StreamName}_{Stage}` — stage-specific (e.g., `PL_SOBacklog_Bronze`)
- `PL_Utility_{Function}` — shared utilities
- `TR_{StreamName}_{Schedule}` — triggers

---

## §ADLS Gen2 MCP

**Server:** `azure` — [microsoft/mcp](https://github.com/microsoft/mcp) (GA 1.0)
**Runtime:** Node.js 18+ (npx) | **Transport:** stdio | **Status:** Installed
**Auth:** DefaultAzureCredential (az login)
**Coverage:** ADLS Gen2 + Blob Storage + 40 other Azure services

The `azure` MCP server handles all ADLS operations. Already configured in `.mcp.json`.

### Tool Routing

```
List containers/filesystems   → list_containers
List blobs/paths              → list_blobs / list_paths
Read blob content             → read_blob
Write blob (DEV ONLY)         → write_blob
Create directory (DEV ONLY)   → create_directory
Check blob properties         → get_blob_properties
Delete blob (DEV ONLY)        → delete_blob
```

### Common Operations

**Verify Delta table health:**
1. `list_blobs` — check `gold/{TableName}/_delta_log/` for recent commits
2. `read_blob` — latest `_delta_log/*.json` for row counts and schema
3. Cross-reference with Databricks: `DESCRIBE HISTORY flukebi_Gold.{TableName}`

**Audit LiteLLM logs (on `flkaienablement`):**
1. `list_blobs` in `litellm-logs/` container, filter by node/date
2. `read_blob` — download specific usage log JSON
3. Check `azure_correlation_id` field (deployed 2026-05-12)

**Delta path conventions:**
- Tables: `{layer}/{TableName}/part-*.snappy.parquet`
- Transaction log: `{layer}/{TableName}/_delta_log/{version}.json`
- LiteLLM logs: `{node}/{YYYY}/{MM}/{DD}/{HH}/{request_id}_{timestamp}.json`

---

## §Azure DevOps MCP

**Server:** `azure-devops` — [microsoft/azure-devops-mcp](https://github.com/microsoft/azure-devops-mcp)
**Runtime:** Node.js 18+ | **Transport:** stdio
**Auth:** Personal Access Token (PAT)

### MCP Config

```json
{
  "mcpServers": {
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp@latest"],
      "env": {
        "AZURE_DEVOPS_ORG_URL": "https://dev.azure.com/flukeit",
        "AZURE_DEVOPS_PROJECT": "Fluke Data And Analytics",
        "AZURE_DEVOPS_PAT": "${AZURE_DEVOPS_PAT}"
      }
    }
  }
}
```

### Tool Routing

```
List/search work items        → query_work_items (WIQL)
Create work item              → create_work_item (DEV context only)
Update work item              → update_work_item
List open PRs                 → list_pull_requests
Get PR details/diff           → get_pull_request
Add PR review comment         → add_pr_comment
Approve/reject PR             → review_pull_request
Browse repo files             → get_file_content
Get commit history            → list_commits
Queue/run a build             → queue_build (DEV pipelines only)
Check build status            → get_build
List pipelines                → list_pipelines
Manage wiki pages             → get_wiki_page / update_wiki_page
```

### UBI Repositories

| Repository | Content | Local Path |
|-----------|---------|------------|
| `AzureDataBricks` | Databricks notebooks (PySpark, SQL) — 646 files | `<USER_HOME>/AzureDataBricks` |
| `ADF` | ADF ARM templates (pipelines, datasets, triggers) — ~300 files | `<USER_HOME>/ADF` |
| `Power BI UBI Curated Datasets` | PBI project files, semantic models | `<USER_HOME>/Power BI UBI Curated Datasets` |

### Common Operations

**Find work items for a stream:**
```sql
SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo]
FROM WorkItems
WHERE [System.TeamProject] = 'Fluke Data And Analytics'
  AND [System.Title] CONTAINS 'SOBacklog'
  AND [System.State] <> 'Closed'
```

**AI Code Review flow (Pillar 1 of UBI AI Integration):**
1. `list_pull_requests` — find new/open PRs in AzureDataBricks repo
2. `get_pull_request` — get diff and linked work items
3. Analyze code against UBI conventions from `/ubi-dev`
4. `add_pr_comment` — post inline review comments
5. `review_pull_request` — approve or request changes

**Check recent commits:**
1. `list_commits` — filter by repo and date range
2. `get_file_content` — read specific file at a commit

---

## §Power BI MCP

**Server:** `powerbi` — [microsoft/powerbi-modeling-mcp](https://github.com/microsoft/powerbi-modeling-mcp)
**Runtime:** .NET 8.0 | **Transport:** stdio
**Auth:** Local (PBI Desktop localhost) or XMLA endpoint (AAD)

### MCP Config

```json
{
  "mcpServers": {
    "powerbi": {
      "command": "dotnet",
      "args": ["run", "--project", "C:/Tools/powerbi-modeling-mcp/src/PowerBIModelingMCP"],
      "env": {
        "PBI_CONNECTION_MODE": "local"
      }
    }
  }
}
```

For cloud access via XMLA:
```json
{
  "PBI_CONNECTION_MODE": "xmla",
  "PBI_XMLA_ENDPOINT": "powerbi://api.powerbi.com/v1.0/myorg/FLK-BI-DEV",
  "PBI_DATASET_NAME": "UBI Curated Datasets"
}
```

### Tool Routing

```
Execute DAX query             → execute_dax
List tables/columns           → list_tables
List measures                 → list_measures
Create/update measure (DEV)   → create_measure / update_measure
Delete measure (DEV)          → delete_measure
Export model to TMDL          → export_tmdl
Import TMDL changes (DEV)    → import_tmdl
View relationships            → list_relationships
Get model metadata            → get_model_info
Generate documentation        → document_model
```

### Companion Skills

| Task | Use This |
|------|---------|
| DAX development, measure CRUD, TMDL export | This MCP (`powerbi`) |
| Binary .pbix manipulation, report-level measures, visual creation | `/powerbi-desktop` skill |
| Report layout, pages, visual containers | `/powerbi-desktop` skill |

### Common DAX Patterns

```dax
-- Year-to-Date Revenue
TOTALYTD([Total Revenue], 'DimDate'[Date])

-- Rolling 12-Month Average
AVERAGEX(
    DATESINPERIOD('DimDate'[Date], MAX('DimDate'[Date]), -12, MONTH),
    [Monthly Revenue]
)

-- Backlog Aging Buckets
SWITCH(TRUE(),
    [Days Outstanding] <= 30, "0-30",
    [Days Outstanding] <= 60, "31-60",
    [Days Outstanding] <= 90, "61-90",
    "90+"
)
```

---

## §Fabric MCP

Two complementary servers:

### Option A: Fabric Core (Cloud-Hosted)

**Endpoint:** `https://api.fabric.microsoft.com/v1/mcp/core`
**Transport:** Streamable HTTP (SSE) | **Auth:** Entra ID (AAD OAuth 2.0)

```json
{
  "mcpServers": {
    "fabric-core": {
      "type": "streamable-http",
      "url": "https://api.fabric.microsoft.com/v1/mcp/core",
      "headers": {
        "Authorization": "Bearer ${FABRIC_TOKEN}"
      }
    }
  }
}
```

### Option B: Fabric Pro-Dev (Local)

**Runtime:** Python 3.10+ | **Transport:** stdio

```json
{
  "mcpServers": {
    "fabric-prodev": {
      "command": "python",
      "args": ["-m", "fabric_prodev_mcp"],
      "env": {
        "FABRIC_WORKSPACE_ID": "${FABRIC_WORKSPACE_ID}",
        "FABRIC_LAKEHOUSE_ID": "${FABRIC_LAKEHOUSE_ID}"
      }
    }
  }
}
```

### Tool Routing

```
List/manage workspaces        → list_workspaces
Query lakehouse SQL           → execute_sql
Create OneLake shortcut       → create_shortcut
Run/manage notebooks          → run_notebook
Execute DAX on semantic model → execute_dax
Refresh semantic model        → refresh_dataset
List reports/pages            → list_reports
Run data pipelines            → run_pipeline
```

### UBI Fabric Strategy

| Phase | Description | Status |
|-------|-------------|--------|
| Current | Databricks + ADLS Gen2 (medallion) | Active |
| Phase 5 | Fabric Lakehouse via ADLS shortcuts | Planned |
| Future | Full Fabric migration (pipelines + models) | Roadmap |

**Key constraint:** Fabric shortcuts don't auto-sync Delta schema changes — if Gold layer columns change, shortcuts must be manually refreshed.

### Common Operations

**Set up ADLS shortcut to Gold layer:**
1. `list_workspaces` — find target workspace
2. `create_shortcut` — point to `abfss://gold@flkubiadlsprd.dfs.core.windows.net/`
3. `execute_sql` — validate data is accessible

---

## §Cross-Server Workflows

These investigation patterns span multiple MCP servers. Follow them in order, with these flexibility rules:

- **Skip steps when the answer is already clear.** If step 1 shows "Oracle connection refused," you don't need to check Databricks or ADLS — the root cause is source connectivity.
- **Add steps when something doesn't add up.** If ADF shows success but ADLS has no output files, investigate the publish stage specifically — don't just report "success."
- **Switch servers when a dead end appears.** If ADF MCP times out or returns empty, fall back to `az datafactory pipeline-run` CLI or read the local ARM templates at `<USER_HOME>/ADF\pipeline\`.
- **Combine with `/ubi-dev` when the fix requires code changes.** Investigation via MCP, remediation via ubi-dev conventions.

### Investigate Failed Stream Refresh

1. **ADF MCP** → `list_pipeline_runs` (status="Failed", last 24h) → get run ID and error
   - If no failed runs found: the pipeline may not have triggered at all → check trigger status with `list_triggers`
   - If error is "StatusFlag check failed": pipeline skipped because previous run is stuck → check `status_control`
2. **ADF MCP** → `list_activity_runs` → identify which activity failed
   - If the Databricks notebook activity failed: suspect data issue or cluster timeout → proceed to step 3
   - If the Copy activity failed: suspect source connectivity (Oracle down, SFTP unreachable) → check linked service with `test_connection`
3. **Databricks MCP** → `list_job_runs` → check if the Databricks job completed or failed
   - If job succeeded but ADF shows failure: suspect timeout mismatch (ADF timeout < Databricks runtime)
   - If job failed with `DRIVER_UNREACHABLE`: cluster was terminated mid-run → check cluster auto-termination settings
4. **Databricks MCP** → `execute_sql` → check `etl.status_control` for Status_Flag
   - If Status_Flag = 1 (Running) with stale timestamp: previous run is stuck → needs manual reset to 0
   - If Status_Flag = -1 (Error): read the `Error` column for root cause
5. **ADLS MCP** → `list_blobs` → check if output files were written to Gold
   - If Gold files exist with recent timestamps but status_control shows error: partial write occurred → data quality risk
   - If no Gold files: the pipeline failed before the publish stage
6. **ADO MCP** → `create_work_item` → log the issue if root cause identified
   - **When to stop:** If steps 1-2 reveal a transient error (network timeout, temporary cluster issue), suggest a re-run instead of a work item
   - **When to escalate:** If the same pipeline has failed 3+ times in 24h, or if the error involves schema changes or missing source tables

### Validate End-to-End Data Flow

1. **Databricks MCP** → `execute_sql` → row count at Bronze
2. **Databricks MCP** → `execute_sql` → row count at Silver
3. **Databricks MCP** → `execute_sql` → row count at Gold
4. **ADLS MCP** → `list_blobs` → verify Delta files exist at `gold/{TableName}/`
5. **Power BI MCP** → `execute_dax` → verify report-level totals match Gold

### Audit User Changes (Code Review)

1. **ADO MCP** → `list_pull_requests` → recent PRs in AzureDataBricks or ADF repo
2. **ADO MCP** → `get_pull_request` → read the diff
3. **ADO MCP** → `get_file_content` → read full file for context
4. Review against UBI conventions (invoke `/ubi-dev` for pattern reference)
5. **ADO MCP** → `add_pr_comment` → post review findings

### Compare Dev vs Prod State

1. **ADF MCP** → `get_pipeline` (Dev) → get pipeline definition
2. **ADF MCP** → `get_pipeline` (Prod, read-only) → compare
3. **Databricks MCP** → `execute_sql` on Dev → row counts, schema
4. **Databricks MCP** → `execute_sql` on Prod → compare
5. **ADLS MCP** → `list_blobs` on both accounts → compare file timestamps

### End-to-End Example: "SOBacklog didn't refresh last night"

Here's a complete investigation walkthrough showing how the servers chain together:

```
User: "SOBacklog didn't refresh last night"

Step 1 — ADF: What happened?
→ mcp__adf__list_pipeline_runs(
    pipelineName="PL_Master_SOBacklog",
    lastUpdatedAfter="2026-05-11T00:00:00Z",
    status="Failed"
  )
← Result: Run ID abc123, failed at 02:15 UTC, error: "Notebook execution timed out"

Step 2 — ADF: Which activity?
→ mcp__adf__list_activity_runs(runId="abc123")
← Result: Activity "Refresh_FactSOBacklog" failed after 7200s timeout

Step 3 — Databricks: Did the job finish?
→ mcp__databricks__list_job_runs(job_name="SOBacklog_Refresh", start_time="2026-05-11")
← Result: Job ran for 7,450s (exceeded ADF's 7,200s timeout), actually SUCCEEDED in Databricks

  Diagnosis: ADF killed the pipeline at 2h, but Databricks finished 4 min later.
  Data likely wrote to Gold. Verify:

Step 4 — ADLS: Is the data there?
→ mcp__azure__list_blobs(
    account="flkubiadlsprd",
    container="gold",
    prefix="FactSOBacklog/_delta_log/"
  )
← Result: Latest commit at 02:19 UTC (4 min after ADF timeout) — data IS there

Step 5 — Databricks: Confirm row counts
→ mcp__databricks__execute_sql(
    "SELECT COUNT(*) FROM flukebi_Gold.FactSOBacklog"
  )
← Result: 2,807,243 rows — matches expected count

Step 6 — Databricks: Reset status_control
→ mcp__databricks__execute_sql(
    "UPDATE etl.status_control SET Status_Flag=0, Final_Status='Completed'
     WHERE Stream_Name='SOBacklog' AND Status_Flag=-1"
  )
  NOTE: Only on Dev. For Prod, ask user to reset manually or via stored proc.

Resolution: Data is fine — ADF timeout was too short. Increase PL_Master_SOBacklog
timeout from 7200s to 10800s in Dev, test, then promote.
```

---

## §Auth & Troubleshooting

### Authentication Methods by Server

| Server | Primary Auth | Fallback | Token Command |
|--------|-------------|----------|---------------|
| Databricks | PAT token | AAD token | `az account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d` |
| ADF | DefaultAzureCredential | — | `az login` |
| ADLS (Azure MCP) | DefaultAzureCredential | — | `az login` |
| ADLS (community) | Account key | — | `az storage account keys list --account-name ...` |
| Azure DevOps | PAT | — | Generate at `dev.azure.com/{org}/_usersSettings/tokens` |
| Power BI | Local (PBI Desktop) | XMLA + AAD | `az account get-access-token --resource https://analysis.windows.net/powerbi/api` |
| Fabric Core | Entra ID | — | `az account get-access-token --resource https://api.fabric.microsoft.com` |

### Common Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `401 Unauthorized` | Token expired | Re-run `az login` or regenerate PAT |
| `403 Forbidden` | Insufficient RBAC | Check role assignments on the resource |
| `Connection refused` on Databricks | Workspace URL wrong or cluster down | Verify URL in env config, check cluster state |
| `XMLA endpoint not available` | Not Premium/PPU workspace | Use local PBI Desktop mode instead |
| `MCP server not found` | Config not in `.mcp.json` | Verify `~/.claude/.mcp.json` has the server entry |
| `dotnet not found` | .NET SDK not installed | Install .NET 8.0 SDK |
| `npx` timeout | Corporate proxy blocking npm | Use `npm install -g` then reference global binary |
| `schannel: server closed abruptly` | TLS issue through corporate proxy | Use `az` CLI commands instead of raw `curl` |

### Token Refresh Quick Reference

```bash
# Azure ARM (for ADF, ADLS, general Azure)
az login --tenant 0f634ac3-b39f-41a6-83ba-8f107876c692 --use-device-code
az account set --subscription 52a1d076-bbbf-422a-9bf7-95d61247be4b

# Databricks AAD token
TOKEN=$(az account get-access-token --resource 2ff814a6-3304-4ab8-85cb-cd0e6f879c1d --query accessToken -o tsv)

# Power BI token
PBI_TOKEN=$(az account get-access-token --resource https://analysis.windows.net/powerbi/api --query accessToken -o tsv)

# Fabric token
FABRIC_TOKEN=$(az account get-access-token --resource https://api.fabric.microsoft.com --query accessToken -o tsv)

# Graph API (for AAD user lookups)
GRAPH_TOKEN=$(az account get-access-token --resource https://graph.microsoft.com --query accessToken -o tsv)
```

---

## Installation Status

### Installed & Configured in `.mcp.json` (ready to use)

| Server | Config Key | Runtime | How Installed |
|--------|-----------|---------|---------------|
| Azure MCP Server | `azure` | Node.js (npx) | `npm install -g @azure/mcp` |
| Azure DevOps MCP | `azure-devops` | Node.js (npx) | `npm install -g @azure-devops/mcp` |
| DataFactory.MCP | `adf` | .NET 10.0 | Built from source at `C:\Tools\DataFactory.MCP\` |

### Cloud-Hosted (no local install needed)

| Server | Access | Notes |
|--------|--------|-------|
| Databricks MCP | Managed via AI Gateway | `pip install databricks-mcp` provides client library; server is cloud-hosted at workspace URL |
| Fabric Core MCP | `https://api.fabric.microsoft.com/v1/mcp/core` | Streamable HTTP, Entra ID auth |

### Not Yet Available

| Server | Status | Notes |
|--------|--------|-------|
| Power BI Modeling MCP | Public Preview (docs only) | Repo at `C:\Tools\powerbi-modeling-mcp\` — no source code yet, only documentation |
| ADLS community server | Not on PyPI | `erikhoward/adls-mcp-server` not pip-installable; use the `azure` MCP server for ADLS operations instead |
| Fabric Pro-Dev | Not yet published | Check GitHub for future releases |

### Reference Documentation

Per-server setup scripts, READMEs, and skill files at:
`<USER_HOME>/OneDrive - <ORG>\AI\UBI AI Intergration\MCP_Servers\`
Subfolders: `ADF/`, `Databricks/`, `ADLS_Gen2/`, `Fabric/`, `Azure_DevOps/`, `Power_BI/`
