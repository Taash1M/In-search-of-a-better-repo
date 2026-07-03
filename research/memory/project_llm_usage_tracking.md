---
name: LLM Gateway Usage Tracking
description: Usage tracking ETL — Sprint #23-#29 EXECUTION PLAN review-clean v5 (2026-06-26, 5 adversarial rounds via data-dev-planning). All 7 sprint defects confirmed UNFIXED in live _scripts/llm_usage_etl_v2.py (2294 lines, the script run_etl.sh:69 actually deploys). Plan guarantees zero PBI regression (G-PBI structural + G-PBI-VALUE per-user). NOT built/deployed yet — awaiting user go-ahead.
type: project
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---

## ETL Correctness Sprint #23–#29 — Execution Plan (2026-06-26, review-clean v5)

Built a full execution plan via `/data-dev-planning` (5 adversarial 3-persona rounds → clean). Plan:
`AI\Claude code deployment\docs\plans\ETL_CORRECTNESS_SPRINT_EXECUTION_PLAN.md`; reviews:
`docs\reviews\round1..5_consolidated.md`. **Status: FINAL v5, execution-ready, NOTHING built/deployed.**

### Live-code facts verified this session (correct earlier ambiguity)
- **THE running ETL is `_scripts/llm_usage_etl_v2.py`** — 2,294 lines, 110,367 bytes, modified 2026-06-16.
  `run_etl.sh:69` deploys it as `llm_usage_etl.py` and runs THAT. `deploy/llm_usage_etl.py` (939 lines)
  and `_scripts/llm_usage_etl_v3.py` (Apr 27) are **STALE red herrings — not run.** (Earlier audit read v3 by mistake.)
- Local git repo `claude-code-poc-etl/` is on branch **`feature/phase-a-diagnostic-only-fix`** (`a3516f0`),
  2,294 lines, **NOT merged to main** — likely == live blob (Phase 0 must md5-confirm). Phase A ≠ this sprint.
- All 7 sprint defects CONFIRMED UNFIXED at exact lines: #24 `:319-330` (merge fallback catches all → overwrite),
  #23 `:2026` (fuzzy dedups fact side only), #26 `:1550,1553` (failed-parse blob still watermarked),
  #27 `:1952,1960,2026` (timestamp-only tie-break), #29a `:2247` (watermark save after Gold), #29b `:168-184`
  (hardcoded DIM_USERS PII), #25 `:1097` (content Bronze still `overwrite`).
- **diagnostic_only rows carry non-zero hardcoded est cost (`:2111-2114`) + synthesized `'diag-'||correlation_id`
  keys (`:2085`)** — yet `validate_etl_run.py` check 12 FAILs if diag_only cost≠0 (3-way plan/code/harness conflict).
- **Bronze `_delta_log` `_last_checkpoint` = v99, commits 0-98 DELETED** — confirms the checkpoint-blind local
  readers (16 scripts parse only `_delta_log/*.json`) silently read partial tables. (Out of scope here.)
- `dim_aad_users` schema = {object_id, user_name, user_email, first_seen, last_updated} — **NO user_key/node_key**
  (so it can't be joined to dim_users; #29b must self-source from prior dim_users Delta instead).
- `DIM_USERS` literal has **3 consumers**: dim_users Delta write, `NODE_DEFAULT_USER`→Gold Fact user_key FK (`:1703`),
  and `user_activity` name/email enrichment (`:1851-1892`, a PBI model table).

### Plan design (key decisions)
- **Scope = sprint #23–#29 only** (user choice). Phase 0 repo reconciliation; local validation (DuckDB fixtures +
  new harness importing shared `PER_USER_USAGE_SQL` + `validate_etl_run.py` 13 checks); deploy = double-confirm Prod gate.
- **Zero PBI regression (user requirement) = two gates:** G-PBI (15-table schema-diff ∅ + dim_users.user_key
  unchanged + parse_failures not in model) AND **G-PBI-VALUE** (per-user cost over **pre∪post full-outer join**,
  every delta ≈0 or in a logged match-type-transition list — catches users appearing/disappearing, #23's main effect).
- **#23 = deterministic 2-stage greedy** (rn_fact PARTITION BY request_id THEN rn_corr PARTITION BY correlation_id,
  losers→unmatched never dropped, single materialized `time_diff`, MEC partition gate).
- **#24 = structural `is_deltatable()` detection** (not error-string matching) + pin deltalake to a corruption-FIXED
  version (NOT 1.5.0 which has bugs #2174/#2180/#3392).
- **#29b = self-source dim_users from its own prior Delta** (byte-identical) — kills the unbuildable dim_aad_users
  join AND the new-PII-flow concern; all 3 consumers re-sourced; config carries emails-free skeleton only.
- **Smoke isolation:** ALL THREE watermarks prefix-keyed (`*_${DELTA_PREFIX}.json`), `DELTA_PREFIX=delta_smoke`,
  paused cron+Automation (guaranteed re-enable trap), direct non-wrapper invocation, hard-coded `delta_smoke/` cleanup.
- QA-gate posture = **ENFORCED** (agent + SubagentStop hook both present).

### DEPLOYED TO PROD 2026-06-27 (run 2855eaeb, status=success)
- **Deployed code**: `_scripts/llm_usage_etl_v2.py` md5 `8bb67505fada4d1a3ae1f6c503042896` (build_stamp `etl-sprint-23-29-a3516f0`). Replaced prior `2d23dd4c`.
- **G-DEPLOY gate** (the prior wrong/stale-code incident guard): 3-way md5 verification — blob re-read ✓, on-VM `llm_usage_etl.py` after wrapper auto-deploy ✓, ETL logs its own `__file__` md5 + BUILD_STAMP into `job_runs` ✓. **All 3 must match before a run is trusted.**
- **6 fixes live** (#29b descoped — emails/names ARE required PBI join keys, DIM_USERS literal retained): #24 `_delta_merge_or_create` structural is_deltatable create-only no-overwrite-fallback; #23 2-stage greedy fuzzy losers→unmatched; #25 content Bronze overwrite→MERGE; #26 durable `delta/metadata/parse_failures`; #27 fuzzy total-order tiebreak; #29a watermark unchanged.
- **Live impact**: 819 Gold Fact dupes removed (deterministic tiebreak, old corruption residue); per_user_usage 133,191 rows; **content-analysis 401 FIXED** (VM `AZURE_AI_API_KEY` was stale post-rotation → refreshed from live AI Services account key1, tested HTTP 200). diagnostic_only cost estimate RETAINED (per-model coef) for cost tracking — no schema change. **No trusted-number regression** (Gold/per-user $ unchanged; verified via June 2026 before deploy).
- **Restore point**: `archive/etl-sprint-restore-20260626T205305Z/` + rollback blob `_backups/llm_usage_etl_v2.PRE-SPRINT-20260627T035951Z.py` (md5 2d23dd4c). Rollback = re-upload that blob to `_scripts/`.
- **Git — FULLY UNIFIED (2026-06-27)**: PR #1 MERGED to `feature/phase-a-diagnostic-only-fix` (merge `ca07d37`, head branch deleted), then **feature MERGED to `main`** (merge `f7e5d36`). All three — prod `_scripts/`, feature, main — now byte-identical at ETL md5 `8bb67505`. The feature→main merge had a content conflict in `llm_usage_etl_v2.py` (main's `419a1bd` vs feature line); **resolved in favor of the feature/deployed version** (authoritative running code), md5-verified == prod, main's unique files (system_prompt_injector.py, usage_logger.py, upgrade_opus_models.py, configs/) all retained, 29/29 tests pass post-merge. **Lesson: never blind-merge feature→main here** — dry-run first, resolve ETL conflict to the deployed version, confirm main's extra files survive.
- **Plan + 5-round reviews**: `AI\Claude code deployment\docs\{plans,reviews}\`. Built via [[data-dev-planning]] + [[data-engineering]].

### Open follow-ups (NOT done)
- Content backlog: 20,741 content blobs, 500/run cap → ~40 scheduled runs to clear (by design, self-catching-up).
- DS artifact `phase2_baselines/diag_cost_estimator_v2.json`: duration-stratified estimate (~$33K vs deployed ~$14.6K coef) on the shelf if more accurate AAD cost visibility wanted later.
- Backlog (out of sprint scope): checkpoint-aware local readers, periodic Gold dedup job, MI auth for ETL, Azure Monitor token-metric per-user path.

LLM Gateway usage tracking system captures request logs from 5 LiteLLM gateway nodes (was 4 — node-0 added 2026-04-23) and transforms them into Delta tables for cost allocation and usage analytics.

**Why:** Enterprise requirement for tracking AI token usage and costs across 45+ Claude Code team members on Azure AI Foundry Marketplace billing. Current gateway-level tracking identifies nodes but not individual users.

**How to apply:** When working on the LLM Gateway, AI Enablement, or usage dashboards, reference the plan at `<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\LLM Gateway\LLM_Gateway_Usage_Tracking_Plan.md` and the project memory at `<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\CLAUDE.md`.

## Budget Enforcement — MONITOR ONLY (2026-06-10 decision)
- Per-user registry has `max_budget_monthly_usd: 200.0` — this value is **not enforced** at the gateway
- LiteLLM requires a PostgreSQL/SQLite database backend to track cumulative spend; our gateways have no `database_url` configured
- `user_key_auth.py` passes `max_budget` to `UserAPIKeyAuth` but LiteLLM ignores it without a DB
- TPM/RPM limits (`tpm_limit: 100000`, `rpm_limit: 50`) are in-memory only — reset on container restart
- **Decision**: Continue observe-only. Usage data flows gateway→blob→ETL→Delta→PBI for reporting/alerting. Users are NOT blocked at any threshold.
- **If enforcement is ever needed**: (1) Add PostgreSQL Flexible Server (~$13/mo) + `database_url` to config.yaml, or (2) Custom query in `user_key_auth.py` against Delta tables at auth time

## Per-User Tracking via Azure Diagnostic Logs (2026-04-27, was Phase 0 only on 2026-04-24)

The gateway-level ETL (LiteLLM logs → DuckDB → Delta) continues as-is for cost/token tracking. Diagnostic log processing is now **integrated into the ETL** (v3) for per-user identity resolution:

- **Data source**: `RequestResponse` diagnostic category → NDJSON blobs in `flkaienablement` storage (`insights-logs-requestresponse` container)
- **Record types**: Type A (callerIpAddress, objectId) + Type B (modelDeploymentName, modelName), joined by `correlationId`
- **Key insight**: `objectId` is blank with API key auth, populated with AAD auth → AAD migration enables per-user tracking
- **Resolution**: `objectId` → `dim_aad_users` cache (primary) → Graph API fallback (if token available)
- **Plan**: `Usage Tracking/Per_User_Usage_Tracking_Plan.md` (741 lines, 6 phases)
- **Implementation guide**: `Usage Tracking/Per_User_Usage_Tracking_Implementation_Guide.docx` (206 paragraphs, 14 tables, 6 D2 diagrams)
- **Coexistence**: Both API key and AAD auth work simultaneously (`disableLocalAuth=false`) — no disruption to existing users

### ETL v3 (deployed 2026-04-27, updated 2026-05-11)
- **Script**: `llm_usage_etl.py` (2,069 lines, Sonnet safety analysis, 15/15 table validation)
- **VM path**: `<VM_HOME>/llm_usage_etl.py` (auto-deployed by wrapper from blob)
- **Canonical blob path**: `_scripts/llm_usage_etl_v2.py` (wrapper deploys from `_scripts/` prefix — this is THE deployed version)
- **Backup blob path**: `scripts/llm_usage_etl_v3_sonnet.py` (synced copy, not used by wrapper)
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
- **Known gap**: Script only reads `principalType == "User"` from RBAC — does NOT expand security group memberships. Users assigned exclusively via SGs (no direct RBAC) are missed. Needs update to enumerate group members.
- **Backfill (2026-05-08)**: Manual backfill via interactive Graph token resolved 50/53 rows with names. 6 missing SG-only users inserted (Erickson, Galli, Hartmann, Katyal, Kothapally, Moeller). 40 previously empty names populated. 3 rows remain unresolvable (likely service principals/deleted).
- **Current state**: 53 rows total, 50 with names/emails
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
- **VM Managed Identity**: SystemAssigned MI enabled (2026-05-05), principal `3dde942e-1f7a-4d87-8040-cb15d246eb4c`, Storage Blob Data Contributor on `flkaienablement` storage account. Enables `az login --identity` and `az storage blob upload --auth-mode login` from VM without API keys.
- **Gateway master keys are per-node**: Each LiteLLM gateway has its own unique `LITELLM_MASTER_KEY`. Wrong key → misleading `"No connected db."` 400 error. Always query the correct node's key before testing: `az webapp config appsettings list --name <app> --resource-group flk-team-ai-enablement-rg --query "[?name=='LITELLM_MASTER_KEY'].value" -o tsv`. See [[feedback-litellm-no-connected-db]].

### VM Operational Reference (CRITICAL — avoid repeat troubleshooting)
- **Python venv**: `<VM_HOME>/etl_env/` — NOT system Python. System pip locked by PEP 668.
- **Activation**: `. etl_env/bin/activate` (POSIX dot-source). Do NOT use `source` — VM `az vm run-command` uses `sh`, not `bash`.
- **Installed packages** (in venv): `duckdb 1.2.2`, `pandas 3.0.1`, `deltalake 1.5.0`, `azure-storage-blob 12.28.0`, `azure-core 1.39.0`
- **NOT installed**: `azure-storage-file-datalake` — use `azure-storage-blob` or account key for ADLS access
- **`etl_env.sh`**: On VM at `<VM_HOME>/etl_env.sh` — exports `AZURE_STORAGE_CONNECTION_STRING` and `AZURE_BLOB_CONTAINER_NAME`. Sourced by `run_etl.sh` if conn string not already in env.
- **Querying Delta tables from VM**: Use `deltalake` Python library with `abfss://` scheme + account_key. Do NOT use DuckDB `delta_scan` — it can't authenticate to ADLS (returns `Identity not found`).
- **Gold Fact column names**: `model_deployment` (not `model_deployment_name`), `total_tokens`, `request_id`, `date_key`
- **Job metadata column names**: `run_start_time`, `run_duration_seconds`, `new_blobs_processed`, `bronze_rows_written`, `total_tokens_processed`, `correlation_id`

### Wrapper Script: `run_etl.sh` (hardened 2026-05-07)
- **VM path**: `<VM_HOME>/run_etl.sh`
- **Local path**: `LLM Gateway/run_etl.sh`
- **Purpose**: Single entry point — auto-deploys latest scripts from blob, handles HOME, venv, etl_env.sh, runs health + sync + ETL + query
- **Auto-deploy**: On every run, pulls `_scripts/llm_usage_etl_v2.py` → `llm_usage_etl.py`, `_scripts/sync_aad_users.py`, `_scripts/query_usage.py`, `_scripts/infra_health_check.py` from blob storage before executing
- **Canonical ETL script**: Always `llm_usage_etl.py` (the `ETL_SCRIPT` variable). Development file is `llm_usage_etl_v2.py` — deployed AS the canonical name.
- **Flags**: `--health`, `--sync`, `--etl`, `--query DATE_KEY`, `--all` (no args = --all)
- **Steps**: [0] Health Check → [1] AAD Sync → [2] ETL → [3] Usage Query
- **Companion**: `<VM_HOME>/query_usage.py` — reports usage by node, diagnostic users, dimensions, last ETL run
- **Script deployment**: Upload to blob `_scripts/` → wrapper auto-downloads on every run (no manual VM deployment needed)
- **Blob backup**: `scripts/` prefix has versioned copies (e.g., `llm_usage_etl_v3_sonnet.py`, `*_latest.py`). VM MI can also upload directly via `az storage blob upload --auth-mode login`.

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
  "export HOME=/home/azureuser ARM_ACCESS_TOKEN='$ARM_TOKEN' GRAPH_ACCESS_TOKEN='$GRAPH_TOKEN' && <VM_HOME>/run_etl.sh --all" \
  --query "value[0].message" -o tsv

# 5. Deallocate VM
az vm deallocate --resource-group flk-team-ai-enablement-rg --name llm-usage-duckdb-vm --no-wait
```

#### ETL-only (no tokens needed — used for quick fix validation):
```bash
az vm start --resource-group flk-team-ai-enablement-rg --name llm-usage-duckdb-vm
az vm run-command invoke --resource-group flk-team-ai-enablement-rg --name llm-usage-duckdb-vm \
  --command-id RunShellScript --scripts \
  "export ETL_CORRELATION_ID='adhoc-$(date +%Y%m%dT%H%M%S)-description' && /bin/bash <VM_HOME>/run_etl.sh --etl"
az vm deallocate --resource-group flk-team-ai-enablement-rg --name llm-usage-duckdb-vm --no-wait
```
- Wrapper auto-deploys from blob `_scripts/` → sources `etl_env.sh` → runs venv Python
- Upload script to blob first: `az storage blob upload --account-name flkaienablement --container-name litellm-logs --file <local> --name "_scripts/llm_usage_etl_v2.py" --overwrite --connection-string "$(az storage account show-connection-string --name flkaienablement --resource-group flk-team-ai-enablement-rg --query connectionString -o tsv)"`

#### Query-only (no tokens needed, reads from etl_env.sh):
```bash
az vm run-command invoke --resource-group flk-team-ai-enablement-rg --name llm-usage-duckdb-vm \
  --command-id RunShellScript --scripts \
  "export HOME=/home/azureuser && . <VM_HOME>/etl_env.sh && <VM_HOME>/run_etl.sh --query 20260428" \
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

### Fixes Deployed (2026-05-17, adhoc-20260517T210146-infra-content-fix)
1. **Infra classification**: Exact-join rows where `user_name` is blank are now `match_type='infra'` instead of `'exact'`. These are ApiKey-authenticated infrastructure requests (gateway self-calls, Haiku safety calls) with no user identity. Result: exact=0, fuzzy=3778, infra=41, unmatched=12030.
2. **Content user enrichment**: `_process_content_logs()` now enriches silver rows with `user_name`/`user_email` from `per_user_usage` table (joined by `request_id`) before writing to Delta and before alert generation. Fixed the bug where `aad_lookup` was loaded but never used (lines 1067-1075 dead code).
3. **Backfill**: One-time script enriched 197/6324 content_silver rows and 2/17 content_alerts rows with user identity. Remaining blanks are requests not matched to any user in per_user_usage (unmatched/infra).

### Fixes Deployed (2026-05-18, adhoc-dedup-fix-20260518T)
1. **Per-user dedup**: Added `fact_clean` and `diag_clean` CTEs to per_user_usage SQL query (lines ~1867-1882). Both use `ROW_NUMBER() ... EXCLUDE (_rn)` to deduplicate Gold Fact by `request_id` and diagnostic_user_activity by `correlation_id` before joining. Also switched all references from `fact_pu`/`diag_pu` to `fact_clean`/`diag_clean`.
2. **Root cause**: Gold Fact had 4,146 duplicate request_ids (16,188 total, 12,042 unique) — accumulated from May 6 corruption rebuild. `_delta_merge_or_create` merge only updates/inserts, never removes existing duplicates.
3. **Result**: 15,880 → **12,042 rows** (3,838 dupes eliminated). Duplicate request_ids: **0** (confirmed by validation). Match breakdown: exact=0, fuzzy=3,851, infra=45, unmatched=8,146.
4. **Dedup logging**: Added pre-query duplicate detection log line showing fact/diag dedup counts.
5. **Top 10 Users attribution**: 9 named users, 164 rows (1.4% coverage). Diagnostic_user_activity is richer (13 users, 20K rows). Plan: add second PBI page for diagnostic-based top users.

### Deployed (2026-05-18, caller_ip_hash for API Key User Segmentation)
1. **Feature**: Added `caller_ip_hash` (MD5 of `caller_ip` from diagnostic logs) to `per_user_usage` table — enables IP-level segmentation of API key traffic.
2. **ETL edits**: 4 CTE changes in `llm_usage_etl_v2.py` (~lines 1914, 1948, 1974, 2003): `exact_matches` + `fuzzy_ranked` get `md5(COALESCE(d.caller_ip, ''))`, `fuzzy_matches` adds `caller_ip_hash` to column list, `unmatched` gets `'' AS caller_ip_hash`.
3. **PBI changes**: TMDL column added to `llmUsage per_user_usage.tmdl` (after `auth_type`), visual `b55933bce3b9409cb700` updated with "IP Hash" as first column.
4. **SIT results** (all PASS): 12,080 rows, 24 columns, 0 dupes, fuzzy=3,856 (19 distinct hashes), infra=45 (1 hash), unmatched=8,179 (empty), 13/13 Delta tables healthy.
5. **Key insight**: 1 dominant hash (`57e1bb8...`) covers 3,445/3,856 fuzzy rows — likely the primary API key automation client. 15+ distinct hashes in total provide meaningful segmentation.
6. **GitHub**: Committed to `Taashi-Manyanga_fortive/Claude-Code-POC-ETL` (commit d1e42ce).
7. **Archive**: Pre-change backup at `LLM Gateway/archive/2026-05-18_pre_caller_ip/` (12 files).

#### Claude CLI POC Report (`Claude CLI POC Usage Tracking.pbip`) — 2026-05-13, updated 2026-05-18
- **DirectQuery** to Fabric Warehouse (same SQL endpoint as New_base_template)
- **5 pages**: Read Me, Usage Tracking, Content Alerts, Content Analysis, Top 10 Users
- **Top 10 Users page** (`d4e5f6a7b8c9d0e1f2a3`, 16 visuals): Two side-by-side tables at bottom + matching bar charts above
  - **Left: "Top 10 AAD Users"** (`b55aad10e3b9409cb700`, x=10, y=590, w=935, h=490, z=10200) — `diagnostic_user_activity`. filterConfig: auth_type='AAD' + user_name NOT IN ('', null). Columns: User, Email, Node, Requests (CountNonNull correlation_id), Avg_duration_ms. Sort: Requests desc.
  - **Right: "Per-User Usage: Total Tokens & Est. Cost"** (`a44922bce3b9409cb699`, x=990, y=590, w=930, h=490, z=10100) — `per_user_usage`. Columns: Email, Requests, Total_tokens, Prompt_tokens, Completion_tokens, Total_cost_usd. Sort: total_tokens desc.
  - **Bar charts (updated 2026-05-18 — each mirrors its table below, matching New_base_template):**
    - Left: "Requests by AAD User" (`aa35533ee5db418581a4`) — `diagnostic_user_activity.user_name` × CountNonNull(correlation_id), filterConfig: auth_type='AAD' + non-blank user_name, data labels on
    - Right: "Total Tokens by API Key User" (`cf278591af604aa7841c`) — `per_user_usage.caller_ip_hash` × Sum(total_tokens), filterConfig: match_type IN ('unmatched', 'fuzzy', 'infra'), data labels on
  - **TMDL**: `caller_ip_hash` column added to CLI POC semantic model (2026-05-18, same lineageTag as New_base_template)
- **Content Alerts page** (`c3d4e5f6a7b8c9d00102`, 1280x720, 13 visuals): 3 slicers (full_date range + year_month month + node dropdown), 5 KPI cards, combo chart, bar chart, alert detail table
  - Month slicer (`cl03bmonthslicer`) added 2026-05-18 — `dim_date.year_month` dropdown, positioned between shrunk date slicer and shifted node slicer
- **All 4 data pages have `year_month` month slicers** (Usage Tracking, Content Alerts, Content Analysis, Top 10 Users)

### Current State (2026-05-17, fully deployed — content logging + Sonnet safety analysis + per-user usage live)
- All M queries are simple `Source{[Schema="llmUsage",Item="table_name"]}[Data]` — no computed columns
- **Fabric shortcuts LIVE** for `diagnostic_user_activity` + `dim_aad_users` + `content_analytics` + `safety_analytics` + `content_alerts` + `per_user_usage`
  - **2026-05-11 fix**: `diagnostic_user_activity`, `content_analytics`, `daily_llm_usage` Table shortcuts were broken (OneLake double-hop). Deleted and recreated as direct ADLS Gen2 shortcuts pointing to Delta table paths. 14 total Table shortcuts confirmed healthy.
- **20 Delta table paths** (19 active + 1 archive): see Canonical Delta Table Paths section for authoritative list

#### DirectLake Report (`LLM_Gateway_Usage_Tracking_DirectLake.pbip`)
- **22 relationships** in semantic model (was 14): +8 for content_analytics→dim_date/nodes/models, safety_analytics→dim_date/nodes, content_alerts→dim_date/nodes/models
- **10 PBI pages** (was 7): README, Dashboard, Data Table, User Tracking, Infra Health, Usage & Health, Page 1, README - Safety, Content Analysis & Insights, Content Alerts
- **14 tables in semantic model**: llm_usage, daily_llm_usage, user_activity, diagnostic_user_activity, dim_date, dim_nodes, dim_models, dim_users, dim_aad_users, job_runs, health_checks, content_analytics, safety_analytics, content_alerts

#### New Base Template Report (`New_base_template.pbip`) — 2026-05-13
- **DirectQuery** to Fabric Warehouse (not DirectLake)
- **22 relationships** (19 original + 3 per_user_usage→dim_date/nodes/models)
- **5 pages**: Read Me, Usage Tracking, Content Analysis, Top 10 Users, Content Alerts
- **15 tables**: llm_usage, daily_llm_usage, user_activity, diagnostic_user_activity, dim_date, dim_nodes, dim_models, dim_users, dim_aad_users, job_runs, health_checks, content_analytics, safety_analytics, content_alerts, per_user_usage
- **Read Me page**: Flag Taxonomy (CRITICAL/HIGH/MEDIUM/LOW with color codes) + Alert Escalation triggers + status flow added to right textbox
- **Content Alerts page** (`c3d4e5f6a7b8c9d00102`): 12 visuals — header, title, date/node slicers, 5 KPI cards (Safety Score, Safe %, Total Alerts, Critical Alerts, Frustrated %), combo chart (analyzed vs score over time), bar chart (topic breakdown by node), alert detail table (10 columns)
- **Navigation**: "Content Alerts" button (`ca13navbutton`) on Read Me page
- **Content Analysis & Insights page** (16 visuals, was 12): header, title, 3 slicers, 4 cards, line chart, bar chart, detail table (shrunk to 170px), +2 section labels + 2 data tables (added 2026-05-03)
  - **Sentiment Breakdown table** (ca14): full_date, node_display_name, Positive %, Negative %, Frustrated % — from safety_analytics (Avg aggregation)
  - **Topic Breakdown table** (ca16): full_date, node_display_name, Code %, Data %, Docs %, Other % — from safety_analytics (Avg aggregation)
  - Font size 8pt, positioned side-by-side below detail table (y=580, left x=10, right x=650, each 620px wide × 130px tall)
- **Top 10 Users page** (`d4e5f6a7b8c9d0e1f2a3`, overhauled 2026-05-13, updated 2026-05-18): Two side-by-side tables
  - **Left: "Top 10 AAD Users"** (`a44922bce3b9409cb699`, x=10, y=570) — `diagnostic_user_activity` with filterConfig: auth_type='AAD' + user_name NOT IN ('', null). Columns: User, Email, Node, Requests, Avg_duration_ms
  - **Right: "Top 10 API Key Users"** (`b55933bce3b9409cb700`, x=965, y=570) — `per_user_usage` with filterConfig: match_type IN ('unmatched', 'fuzzy', 'infra'). Columns: Caller_ip_hash, Node, Match Type, Requests, Total_tokens, Prompt_tokens, Completion_tokens, Total_cost_usd
  - 4 cards: Unique Users, Total Requests, Total Tokens, Est. Total Cost — all from per_user_usage
  - 2 bar charts (updated 2026-05-18 — each mirrors its table below):
    - Left: "Requests by AAD User" (`aa35533ee5db418581a4`) — `diagnostic_user_activity.user_name` × CountNonNull(correlation_id), filterConfig: auth_type='AAD' + non-blank user_name, data labels on
    - Right: "Total Tokens by API Key User" (`cf278591af604aa7841c`) — `per_user_usage.caller_ip_hash` × Sum(total_tokens), filterConfig: match_type IN ('unmatched', 'fuzzy', 'infra'), data labels on
  - 2 slicers (dim_date.year_month, dim_nodes.node_display_name)
- **Content Alerts page** (`c3d4e5f6a7b8c9d00102`, updated 2026-05-18): Added `year_month` month slicer (`cl03bmonthslicer`, x=160, w=130) between existing date slicer (shrunk to w=145) and node slicer (shifted to x=295, w=150). Now has 3 slicers + 5 KPI cards in slicer row.
- **filterConfig pattern**: Visual-level filters use `filterConfig.filters[]` at root (NOT bare `filters[]`). Discovered 2026-05-18, applies to schema 2.8.0.
- **Column displayName convention**: Aggregated columns use underscore names (Total_tokens, Prompt_tokens, etc.) with both `nativeQueryRef` and `displayName` properties.
- Month slicers use `year_month` on all 4 data pages (Usage Tracking, Content Analysis, Content Alerts, Top 10 Users)
- **DIM_MODELS: 5 entries** (was 3) — added "Claude Code (Sonnet)" for `claude-code` deployment + "Unknown" catch-all
- **DIM_NODES: 7 entries** (was 5) — added "Shared" + "Unassigned" catch-all entries
- `claude-code` is the Claude Code CLI deployment name (~95% of traffic), mapped to Sonnet rates
- Silver processing validates node_key against VALID_NODE_KEYS set
- user_activity email enrichment from DIM_USERS for node-level groups

## Content Logging & Safety Analysis (Phase 5, deployed 2026-04-30)

### Overview
Full request/response content capture from all 5 LiteLLM gateways via async callback → Azure Blob Storage → DuckDB ETL → Sonnet safety analysis → Delta Lake → PBI.

### Content Logger Callback (`content_logger.py`)
- **Location**: `LLM Gateway/content_logger.py`, deployed as `/app/content_logger.py` in all 5 Docker images
- **Config**: `callbacks: [content_logger.logger_instance, usage_logger.logger_instance]` (list format, both custom callbacks)
- **Feature flag**: `CONTENT_LOGGING_ENABLED=true` env var on each App Service (kill switch: set false, restart)
- **Blob container**: `litellm-content-logs` on `flkaienablement` storage account
- **Blob path**: `{node}/{YYYY}/{MM}/{DD}/{HH}/{request_id}_{epoch_ms}.json`
- **Performance**: Fully async (post-response), zero impact on API latency. Blob upload via `run_in_executor` (thread pool). 500KB per-field truncation.

### Usage Logger Callback (`usage_logger.py`) — NEW 2026-05-05
- **Location**: `LLM Gateway/litellm-node0/usage_logger.py`, deployed as `/app/usage_logger.py`
- **Config**: Listed alongside content_logger in `callbacks` list
- **Blob container**: `litellm-logs` on `flkaienablement` storage account (same container ETL reads from)
- **Blob path**: `{node}/{YYYY}/{MM}/{DD}/{HH}/{request_id}_{epoch_ms}.json`
- **Payload**: request_id, model, model_id, model_group, api_base, status, start_time, end_time, usage (prompt_tokens, completion_tokens, total_tokens, cache tokens), response_cost, user_api_key_hash, metadata, node
- **Why custom**: LiteLLM's built-in `azure_storage` callback is enterprise-only (`LITELLM_LICENSE` required). The `_premium_user_check()` raises ValueError on every log event without a license, silently caught. Our custom logger uses the same `azure-storage-blob` SDK as content_logger — no license needed.
- **ETL compatibility**: Output schema matches what `llm_usage_etl_v2.py` Silver layer expects (17/17 fields validated). Node detection works from blob path prefix.
- **SIT validated**: 4 test blobs → Bronze(4) → Silver(4) → Gold Fact(4) → Gold Agg(108) — full E2E 2026-05-05

### Docker Images (all deployed 2026-05-05)
- **node-0**: v10 (usage_logger + content_logger + codex model, `main-latest`) — upgraded 2026-05-08
- **node1**: v7 (usage_logger + content_logger, `main-latest`)
- **node2**: v7 (usage_logger + content_logger, `main-latest`)
- **node3**: v7 (usage_logger + content_logger, `main-latest`)
- **poc**: v7 (usage_logger + content_logger, `main-latest`)

### LiteLLM azure_storage Callback — Enterprise Gate (2026-05-05 finding)
- **Callback string**: `"azure_storage"` (NOT `"azure_blob"` — that string doesn't exist in LiteLLM codebase)
- **Config key**: Must use `callbacks` list (NOT `success_callback` — that goes to a sync dispatch path the async proxy never reads)
- **Premium gate**: `_premium_user_check()` in `async_log_success_event` + `async_log_failure_event` checks `litellm.proxy.proxy_server.premium_user` — False without `LITELLM_LICENSE`
- **Behavior**: Initializes fine, invoked on every call, raises ValueError, caught silently, payload never queued, no blobs written
- **Decision**: Custom `usage_logger.py` instead of purchasing enterprise license

### ETL Content Processing
- **Function**: `_process_content_logs()` in `llm_usage_etl_v2.py`
- **Pipeline**: Blob → Bronze (content_logs_raw) → Silver (content_logs) → Sonnet Analysis → Gold (content_analytics + safety_analytics) → Alerts (content_alerts)
- **Watermark**: Separate `watermark_content.json` tracking processed hour labels
- **Non-blocking**: Content log failure doesn't prevent existing ETL from completing

### Content Safety Analysis (upgraded 2026-05-02)
- **Endpoint**: `https://flk-team-ai-enablement-ai.services.ai.azure.com/anthropic/v1/messages` (Node 0 direct, not through gateway)
- **Model**: `claude-sonnet-node-0` (upgraded from `claude-haiku-node-0` on 2026-05-02)
- **Auth**: `AZURE_AI_API_KEY` env var on VM (same key as gateways)
- **Rate limiting**: 1 request every 3 seconds (20 req/min), conservative for Sonnet TPM budget
- **Analysis categories**: work_appropriateness_score (0-100), safety_category (safe/caution/unsafe), sentiment (positive/neutral/negative/frustrated), topic_category (10 categories), content_flags (12-flag taxonomy), escalation_required
- **Cost**: ~$0.006/request, ~$45/month at 250 req/day (was ~$5.70 with Haiku)
- **Post-processing pipeline** (4 fixes, defense-in-depth):
  1. **Flag normalization**: Strips any flag not in the 12-flag canonical taxonomy (CANONICAL_FLAGS frozenset)
  2. **Sentiment derivation**: score >= 90 + no flags → "positive"; score < 50 or CRITICAL/HIGH flag → "negative"
  3. **Keyword topic override**: Pre-classifier with 9 keyword categories, overrides LLM when confidence >= 0.7 and LLM picked generic bucket
  4. **Confidence calibration**: Filtered text < 50 chars → "low"; < 200 chars → "medium"
- **System prompt**: ~2500 chars, explicit 12-flag taxonomy with severity levels, Claude Code session context, sentiment/topic/scoring rules
- **User template**: 3 structured sections — user_messages (PRIMARY, 2500 chars), system_prompt context (500 chars), assistant response summary (1000 chars)
- **XML metadata filter**: Generic regex strips all XML blocks, tool_use_id lines, separator lines before analysis

### Haiku→Sonnet Upgrade Results (2026-05-02, validated)
| Metric | Haiku (before) | Sonnet (after) |
|--------|---------------|----------------|
| Sentiment | 93% neutral, 7% frustrated, 0% positive | 84% positive, 9% neutral, 6% frustrated, 1% negative |
| Topics | 60% data_analysis, 5% code | 43% data, 18% code, 17% docs, 7% security, 4% automation |
| Flags invented | 236 instances, 120 types | **0 instances, 0 types** |
| Flags canonical | 9 (off_topic only) | 38 (off_topic only) |
| Confidence | 95% high | 44% medium, 44% high, 12% low |
| Alerts | 30 (invented flags) | 3 (clean off_topic) |
| Gold positive% | 0% everywhere | 33-100% across nodes |

### Content Flag Taxonomy
- **CRITICAL**: illegal_activity, destructive_intent, weapons_explosives
- **HIGH**: hate_speech, harassment, discrimination, sexual_content
- **MEDIUM**: pii_exposure, competitor_intel, policy_circumvention
- **LOW**: profanity, off_topic

### Alert Escalation
- **Triggers**: Any CRITICAL/HIGH flag, score < 50, safety_category = unsafe
- **Table**: `gold/audit/content_alerts` (merge on alert_id)
- **Status workflow**: new → reviewed → dismissed/escalated

### Data Lifecycle
- **Hot (Blob)**: 0-7 days hot tier, 7-30 days cool tier, deleted after 30 days (lifecycle policy)
- **Warm (Delta Silver)**: 90 days retention in content_logs
- **Cold (Delta Archive)**: 365 days in archive/content_logs
- **Gold aggregates**: Kept indefinitely (small, no raw content)

### Bugs Fixed During Deployment
1. **Early return bug**: `run_etl()` returned at line 1152 when no new metadata blobs, skipping content/diagnostic processing. Fixed by removing early return.
2. **Haiku JSON extraction**: Claude Haiku wraps JSON in markdown code fences. Added fence stripping + `{...}` substring extraction.
3. **Empty DataFrame guards**: Added `if bronze_rows:`/`if silver_rows:`/`if fact_rows:` guards around delta write operations.
4. **Cron pointing to v1**: Both `run_etl.sh` and crontab referenced `llm_usage_etl.py` instead of `llm_usage_etl_v2.py`. Fixed via sed.
5. **Cross-node watermark bug** (2026-05-01): Content watermark stored `poc/2026/05/01/03` as single global hour label. Since `node0/`-`node3/` sort alphabetically before `poc/`, all non-POC blobs were skipped (194 of 208 missed). Fixed by switching to per-node watermarks (`last_processed_hours` dict). After fix: 177 new blobs processed, 339 total Silver rows.
6. **Cron not using wrapper** (2026-05-01): Cron ran `python3 llm_usage_etl_v2.py` directly, bypassing `run_etl.sh` wrapper (AAD sync + query skipped). Fixed: `0 */6 * * * /bin/bash <VM_HOME>/run_etl.sh --all >> <VM_HOME>/etl.log 2>&1`

### QA Validation (2026-04-30 → 2026-05-02)
- 15/15 test requests across all 5 nodes, 15/15 content blobs verified (Apr 30)
- Watermark bug fix (May 1): 177 blobs processed in single ETL run after fix
- Sonnet upgrade + Fixes 1-3 (May 2): Full re-analysis of all content blobs
- **Current counts (2026-05-11)**: 3,415 Silver rows, 3 alerts (all MEDIUM, test probes from May 1 validation), 71 content_analytics rows (66 aggregation groups), 40 safety_analytics rows
- **Sentiment**: 84% positive, 9% neutral, 6% frustrated, 1% negative
- **Topics**: 43% data_analysis, 18% code, 17% docs, 7% security, 7% general, 4% automation, 4% other, 1% debugging
- **Flags**: 38 rows flagged (all canonical off_topic), zero invented flags
- **Scores**: 94% at 90-100, 1% at 75-89, 4.5% at 50-74, 0.4% at 0-49
- **AAD users**: 53 total, 50 resolved (backfilled 2026-05-08 — 6 SG-only users added, 40 empty names populated)

### Local Delta Table Querying Pattern (2026-05-31)
- **Use case**: Ad-hoc analytics from local Windows machine without starting the VM or using DuckDB
- **Pattern**: `read_delta_table(table_path)` — parses `_delta_log/*.json` to find active parquet files (tracking add/remove actions), downloads each via `azure-storage-blob`, reads with `pyarrow.parquet`
- **Auth**: Storage account key via `az storage account keys list --account-name flkaienablement`
- **Example**: `read_delta_table("delta/gold/audit/diagnostic_user_activity")` → pandas DataFrame (93K+ rows for May 2026)
- **Scripts using this**: `requests/build_overlap.py`, `requests/add_recommendation_tab.py`
- **Gotcha**: `date_key` is int (YYYYMMDD), not string — filter with `>= 20260501` not `>= '20260501'`
- **May 2026 per-user snapshot** (from diagnostic_user_activity + per_user_usage):
  - 14 unique AAD users in diagnostic logs, 11 matched in per_user_usage
  - Top: Ryan Bryson 14.1M tokens, Joe Seefried 8.7M, Adelaide Hartmann 1.4M
  - 20 of 42 node users still on API key auth (no individual tracking)

### Enterprise System Prompt Cost Validation (2026-05-27)
- **Analysis**: 7-day balanced comparison (May 14-20 pre vs May 21-27 post), 18,236 Silver rows, 3,025 requests analyzed
- **Results**: Cost/request -41.4% ($1.44→$0.85), avg completion -8.5% (604→552), O/I ratio +22.2%, monthly savings $8,120
- **Control**: POC gateway (no injector) O/I declined -16.8% — confirms causality
- **Scripts**: `scripts/analyze_system_prompt_impact.py` (console), `scripts/generate_cost_comparison_deliverables.py` (DOCX+Excel)
- **Deliverables**: `Usage Tracking/System_Prompt_Cost_Impact_Analysis_20260527.docx` + `Usage Tracking/System_Prompt_Cost_Comparison_20260527.xlsx` (4 sheets: Summary, Daily Breakdown, By Node, By Model)
- **Shareable pack (2026-06-17)**: Generic version of analysis script + injector + design doc + HowTo + Infographic in `LLM Gateway/Prompt injector pack/`. See [[project-prompt-injector-pack]]

### Remaining Pending
1. **PBI report NOT published**: Two `.pbip` reports exist locally — `LLM_Gateway_Usage_Tracking_DirectLake` (DirectLake, 10 pages) and `New_base_template` (DirectQuery, 5 pages + Content Alerts). Neither has been published to the Fabric workspace (`599f352a-...`). Must open in PBI Desktop (as <USER>) and Publish.
2. **Fabric Lakehouse shortcuts VERIFIED (2026-05-05)**: 28 shortcuts confirmed via Fabric REST API — 14 ADLS Gen2 in `/Files` + 14 OneLake in `/Tables/llmUsage`. All ADLS shortcuts use connection `27a34b25-...` (Key auth to `flkaienablement.dfs.core.windows.net`, key never rotated). **OneLake DFS PathNotFound** when drilling into shortcut directories — may be a Fabric DFS API limitation with ADLS shortcuts. Verify data flows by previewing tables in Fabric portal; refresh SQL endpoint schema if tables show empty.
3. **Fabric Lakehouse schema refresh for year_month/date_key**: New Delta columns (`year_month` on dim_date, `date_key` on user_activity) exist in Delta but Fabric may not have synced. Refresh table schemas in Fabric portal.
4. **After Fabric syncs**: Re-add `year_month` to dim_date TMDL, `date_key` to user_activity TMDL, add `user_activity→dim_date` relationship, switch month slicers from `month_name` to `year_month` for chronological "2026-04" format.
5. **`neutral_sentiment_pct` NOT in ETL or TMDL**: ETL `safety_analytics` computes positive/negative/frustrated percentages but NOT neutral (the 4 sentiments don't sum to 100%). This is by design — not a missing column.

### Documentation Audit (2026-05-05, COMPLETE)
Full audit of all 179 files under `AI\Claude code deployment\`. 14 .md files updated to reflect v7/v9 Docker images, usage_logger.py, 6h cron, enterprise-gate note. Key files:
- `CLAUDE.md` — 7 edits (status line, user count, Docker versions, callbacks, cron, enterprise gate)
- `docs/DeploymentPlan_TeamAIEnablement.md` — note block updated
- `Usage Tracking/Per_User_Usage_Tracking_Plan.md` — 3 v6→v7/v9 references
- `LLM Gateway/flk-litellm-skill.md` — 5 gateway image versions
- `LLM Gateway/LLM_Gateway_Usage_Tracking_Plan.md` — Docker images + header
- Plus 6 other plan docs with note/status updates
- **Acceptable stale**: `content-logging-plan-option-A.md:66-67` (historical v6 build commands)
- **Not auditable**: 67 .docx + 11 .pptx (binary, manual review needed)

### Code Pipeline Audit (2026-05-05, CONDITIONAL PASS)
Three-way validation: local files ↔ blob storage ↔ VM — ALL MATCH (5 critical scripts).
- All 5 config.yaml: correct `callbacks: [content_logger.logger_instance, usage_logger.logger_instance]`
- All 5 Dockerfiles: both loggers COPY'd
- `run_etl.sh`: auto-deploy, chown fix, correct sequence (sync→ETL→query)
- Crontab: `0 */6 * * *` (correct 6h schedule)
- Watermarks: azureuser-owned (no PermissionError)
- `etl_env.sh`: VM-local env file (635 bytes, connection string + container name)
- **Fix applied**: `infra_health_check.py` line 434 log message "6h"→"24h" (uploaded to blob + VM)
- **Fix applied**: chown on all root-owned scripts → azureuser

### ETL Validation Run (2026-05-05 06:33 UTC, SUCCESS)
Triggered as azureuser via `/bin/bash <VM_HOME>/run_etl.sh --all` (identical to cron):
- Script auto-deploy: 3 scripts pulled correctly from blob
- AAD sync: skipped (no ARM/Graph tokens — expected in cron context)
- Bronze: **4 rows** (usage_logger blobs flowing!)
- Silver: 4, Gold Fact: 4, Gold Agg: 112, Gold Audit: 10
- Diagnostic: 3 blobs → 811 records → 407 joined (381 AAD, 26 ApiKey), 39 users resolved
- Content: 4 blobs → 4 analyzed, 0 alerts (content is safe)
- Duration: 36.2s
- **25,898 total diagnostic records** — platform well-used (top: Johnston 2,757, Davison 1,810, Pouley 1,383)
- VM deallocated after validation

## Architecture Diagrams
- **Miro board**: `https://miro.com/app/board/uXjVHajHEbE=/` — 7-column x 3-row presentation grid (16 diagrams, reorganized 2026-04-30)
- **Board layout**: Phase 1→2→3→4→Infra→Phase 5→PBI Mockups (left to right), Architecture→Flow→Detail (top to bottom)
- **Row coordinates**: Row 1 y=-13844 (Architecture), Row 2 y=-11279 (Flow), Row 3 y=-8713 (Drill-down)
- **Column x-coords**: Phase 1 x=-5000, Phase 2 x=500, Phase 3 x=6000, Phase 4 x=11500, Infra x=17000, Phase 5 x=22500, PBI x=28000
- **PBI mockup images extracted**: `Usage Tracking/pbi_mockups/` (3 PNGs: Content Analysis, Content Alerts, README Safety)
- **Azure-icon PNG**: `AI\Miro\Claude Code Deployment\architecture\phase3_azure_arch.png` (15 nodes: gateways → blob → VM → Bronze/Silver/Gold star schema)
- **D2 data flow**: `AI\Miro\Claude Code Deployment\dataflow-d2\phase3_etl_dataflow.d2` + `.svg`
- **Generator**: `diagrams/generate_azure_arch_v2.py` (uses azure_diagrams.py skill)

## Architecture
- **NOT Databricks** — DuckDB on Azure VM (`llm-usage-duckdb-vm`, Standard_B2ms, Ubuntu 24.04)
- **Schedule**: Every 12 hours via Azure Automation (`Every12Hours` schedule, 07:00 + 19:00 UTC) + backup cron (`0 */6 * * *`) on VM
- **Automation**: `Invoke-LLMUsageETL` runbook (7 steps: Start VM → Wait → Health Check → AAD Sync → ETL → Deallocate → Summary)
- **Storage**: `flkaienablement` storage account, `litellm-logs` container (**HNS enabled 2026-03-30** — ADLS Gen2)
- **Output**: Delta Lake tables at `litellm-logs/delta/{bronze,silver,gold,metadata}/`
- **VM cost**: ~$5.27/month (vs ~$30-50/month for Databricks)

## Canonical Delta Table Paths (AUTHORITATIVE — 2026-05-11)

**CRITICAL: Use these paths, NOT the stale paths listed in the warning below.**

All paths are relative to `abfss://litellm-logs@flkaienablement.dfs.core.windows.net/`

| # | Layer | Table | Delta Path | ETL Variable |
|---|-------|-------|------------|--------------|
| 1 | Bronze | Usage logs (raw) | `delta/bronze/llm_usage_raw` | `DELTA_BRONZE` |
| 2 | Bronze | Content logs (raw) | `delta/bronze/content_logs_raw` | `DELTA_CONTENT_BRONZE` |
| 3 | Silver | Usage logs | `delta/silver/llm_usage` | `DELTA_SILVER` |
| 4 | Silver | Content logs | `delta/silver/content_logs` | `DELTA_CONTENT_SILVER` |
| 5 | Gold Fact | Usage fact | `delta/gold/fact/llm_usage` | `DELTA_GOLD_FACT` |
| 6 | Gold Agg | Daily usage | `delta/gold/agg/daily_llm_usage` | `DELTA_GOLD_AGG` |
| 7 | Gold Agg | Content analytics | `delta/gold/agg/content_analytics` | `DELTA_CONTENT_GOLD` |
| 8 | Gold Agg | Safety analytics | `delta/gold/agg/safety_analytics` | `DELTA_SAFETY_ANALYTICS` |
| 9 | Gold Audit | User activity | `delta/gold/audit/user_activity` | `DELTA_GOLD_AUDIT` |
| 10 | Gold Audit | Diagnostic user activity | `delta/gold/audit/diagnostic_user_activity` | `DELTA_DIAG_ACTIVITY` |
| 11 | Gold Audit | Content alerts | `delta/gold/audit/content_alerts` | `DELTA_CONTENT_ALERTS` |
| 12 | Dimensions | dim_nodes | `delta/gold/dimensions/dim_nodes` | `DELTA_DIM_NODES` |
| 13 | Dimensions | dim_users | `delta/gold/dimensions/dim_users` | `DELTA_DIM_USERS` |
| 14 | Dimensions | dim_models | `delta/gold/dimensions/dim_models` | `DELTA_DIM_MODELS` |
| 15 | Dimensions | dim_date | `delta/gold/dimensions/dim_date` | `DELTA_DIM_DATE` |
| 16 | Dimensions | dim_aad_users | `delta/gold/dimensions/dim_aad_users` | `DELTA_DIM_AAD_USERS` |
| 17 | Metadata | Job runs | `delta/metadata/job_runs` | `DELTA_METADATA` |
| 18 | Metadata | Health checks | `delta/metadata/health_checks` | (in health check script) |
| 19 | Gold Fact | Per-user usage | `delta/gold/fact/per_user_usage` | `DELTA_PER_USER_USAGE` |
| 20 | Archive | Content logs | `delta/archive/content_logs` | `DELTA_CONTENT_ARCHIVE` |

**Row counts (2026-05-11):** Bronze raw 13,423 | Silver 13,423 | Silver content 3,753 | Gold Fact 13,423 | Gold Agg 150 | Content Analytics 74 | Safety Analytics 43 | Diagnostic 18,869 | User Activity 13 | Content Alerts 13 | dim_aad_users 53 | dim_date 121 | dim_nodes 7 | dim_models 5 | dim_users 16 | Job Runs 17 | Health Checks 14 | Content Bronze 64 | Archive 0 (no records >90 days yet)

### STALE PATHS — DO NOT USE
These paths exist from earlier ETL versions and are NOT used by the current ETL (`_scripts/llm_usage_etl_v2.py`). Some have corrupted delta logs ("No files in log segment" from deltalake-rs 1.5.0 bugs). Do NOT reference, audit, or try to rebuild these.

| Stale Path | Replaced By | Status |
|------------|-------------|--------|
| `delta/bronze/llm_usage` | `delta/bronze/llm_usage_raw` | Had corrupted delta log; cleaned 2026-05-11 |
| `delta/content/content_logs_raw` | `delta/bronze/content_logs_raw` | Stale; cleaned 2026-05-11 |
| `delta/content/content_logs` | `delta/silver/content_logs` | Stale; cleaned 2026-05-11 |
| `delta/gold/fact/llmusage` | `delta/gold/fact/llm_usage` | Stale duplicate (no underscore) |

### 2026-05-11 Path Audit Lesson
An earlier audit (same session) reported 4 "corrupted" tables, but the audit checked stale paths — not the canonical paths the ETL actually writes to. All 18 active Delta tables were healthy the entire time. The "corruption" was on abandoned paths from a previous ETL version. Always reference the `DELTA_*` variables in `llm_usage_etl_v2.py` (lines 65-85) as the source of truth for paths.

## Gold Layer Corruption Incident & Recovery (2026-05-06)

### Incident
All 14 Gold/Metadata Delta tables were corrupted — parquet data files physically deleted, v0 metadata logs deleted, only the latest 2 delta_log JSON entries survived per table. Bronze and Silver were FULLY INTACT. Fabric Lakehouse shortcuts returned "underlying location does not exist" errors.

### Root Cause: deltalake-rs 1.5.0 known bugs (NOT our code)
Full code audit confirmed zero vacuum/cleanup/delete operations in ETL, health check, verify, or wrapper scripts. The corruption matches three known deltalake-rs 1.5.0 bugs:
- **Issue #2174**: `cleanup_metadata` deletes recent checkpoints, leaving only latest 2 versions (exact match to our pattern)
- **Issue #2180**: `cleanup_metadata` ignores custom retention settings
- **Issue #3392**: Change Data Feed + file retention mismatch deletes referenced parquets (CDF was active on llm_usage — `_change_data` directory confirmed)

Only Gold tables (using `mode="overwrite"`) were affected. Bronze/Silver (MERGE) were untouched.

### Recovery Steps
1. **Forensic capture**: Downloaded surviving delta log entries (v75-v76 for llm_usage, v124-v125 for job_runs, etc.) for evidence
2. **Cleanup**: Deleted all corrupted remnants from 14 Gold/Metadata table paths (45 files total)
3. **ETL run**: Triggered ETL which recreated tables from Bronze/Silver, but only with new batch (321 rows)
4. **Full rebuild**: Created `rebuild_gold.py` script — reads full Silver table (11,723 rows), transforms to Gold Fact schema (adds date_key, hour_of_day, day_of_week, user_key), rebuilds Gold Agg (119 rows) and Gold Audit (10 rows)
5. **Health check**: Manually ran `infra_health_check.py` to recreate health_checks table (not included in `run_etl.sh`)
6. **Verification**: All 10 Fabric Lakehouse tables queryable via SQL endpoint, 12/12 tables passed health validation

### Post-Incident Monitoring (added to ETL, updated 2026-05-11)
- **`_validate_delta_tables()` function** added to `llm_usage_etl_v2.py` — runs after every ETL
- Checks **15 critical tables** (was 14): added per_user_usage to `CRITICAL_TABLES` dict (2026-05-12)
- Logs `[OK]`, `[WARN]` (below minimum rows/files), or `[ERROR]` (cannot open table)
- Reports: `Validation: X/15 healthy, Y warnings, Z errors`
- If errors > 0: `CRITICAL: Delta table corruption detected!`
- **Canonical blob path**: `_scripts/llm_usage_etl_v2.py` (2,069 lines, deployed 2026-05-12)
- **Variable rename (2026-05-11)**: `HAIKU_API_KEY` → `CONTENT_ANALYSIS_API_KEY` across 3 occurrences (lines 57, 1162, 1164)

### E2E Validation (2026-05-11)
- **Job ID**: `e2e-validation-20260511T002033`
- **Result**: 14/14 tables healthy, 0 warnings, 0 errors
- **All 18 Delta tables updated** with incremented versions
- **Content pipeline**: 5 new blobs → 71 content_analytics rows, 40 safety_analytics rows, 3 content_alerts rows (all MEDIUM, test probes)
- **Duration**: 2m35s
- **65+ consecutive successful scheduled runs** (perfect streak)

### E2E Validation — Per-User Token Identity (2026-06-04)
- **Job IDs**: `e2e-node0-soak-validation-20260604T060500`, `e2e-user-email-fix-20260604T064700`, `e2e-per-user-coalesce-fix-20260604T065900`
- **Result**: 13/13 tables healthy, 0 warnings, 0 errors
- **ETL fixes validated**: Silver user_email extraction + per_user_usage COALESCE
- **Confirmed**: `<USER>@<ORG_DOMAIN>` in per_user_usage Gold (match_type=unmatched, 745 tokens)
- **Pipeline**: per-user token → gateway auth → usage blob (`metadata.user_api_key_user_email`) → Bronze → Silver (`user_email` column) → Gold Fact → per_user_usage (COALESCE'd)
- **Counts**: 22,070 Bronze, 22,070 Silver, 22,070 Gold Fact, 17,748 per_user_usage (291 with email), 57 AAD users
- **ETL script size**: 100,599 bytes (was 100,213 — +386 bytes for 2 fixes)

### Pending Mitigations
- Consider upgrading deltalake beyond 1.5.0 when fixes for #2174/#2180/#3392 are confirmed

### Runbook Unified to Wrapper (2026-05-07)
- **Problem**: Old runbook ran Python scripts directly, bypassing `run_etl.sh` — caused: no auto-deploy from blob, no AAD sync, no usage query, split HOME/watermark
- **Fix**: Updated `Invoke-LLMUsageETL` to deploy `run_etl.sh` from blob then execute `run_etl.sh --all` (single VM command)
- **Health check moved**: From separate runbook step to wrapper Step 0 (via `--health` flag in `--all`)
- **Validated**: Ad-hoc job `adhoc-validation-20260507T062447Z` — Health=success, Sync=success, ETL=success (42 blobs, 12/12 healthy), Query=success (181 reqs, 11.3M tokens)

## Status (2026-05-06)
- **Phases 1-9 ALL COMPLETE** — system is live and scheduled
- **Gold layer corruption RECOVERED** (2026-05-06) — all 14 tables rebuilt from Silver, Fabric Lakehouse verified, health monitoring added
- **Phase 5 Content Logging: DEPLOYED & VALIDATED** (2026-04-30) — full request/response capture + Sonnet safety analysis (upgraded from Haiku 2026-05-02)
- **Phase 9: User Audit Table DEPLOYED & VALIDATED** (2026-04-23)
- **Phase 2 (Agentic AI Layer): PLAN COMPLETE** (2026-04-13) — see [project_phase2_agentic.md](project_phase2_agentic.md) and `Usage Tracking/Phase 2/` folder
- **Phase 8: Infrastructure Health Check COMPLETE** (2026-04-13)
  - Automated health check runs as Step 3 of existing `Invoke-LLMUsageETL` runbook (same 12h schedule)
  - Script: `infra_health_check.py` on VM, accepts ARM token from runbook's Managed Identity
  - 7 check categories: RG status, AI Services, 15 model deployments (was 12), RBAC (25 users), 5 gateway web apps (was 4), Anthropic endpoint, content logging (blob freshness)
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
- **Fabric Lakehouse (Option B POC)**: `llm_usage_poc` in workspace `599f352a-0626-441a-b320-d4d60cf360d9`, Lakehouse ID `e5ce55d1-ce93-402b-a9ac-1b36fb05ad67`, SQL Endpoint ID `15e35cf6-b12c-45f1-a45c-2bc6b45fb211`
  - SQL endpoint: server `ynfggd47woteda52r4ihq5wgsi-fi2z6wjgaynejmza2tlaz43a3e.datawarehouse.fabric.microsoft.com`, database `llm_usage_poc`
  - ADLS connection ID for shortcuts: `27a34b25-5e9d-4043-afaf-d60e58485b65`
  - Schemas enabled (changes API surface — `GET .../tables` fails, use shortcuts API instead)
- **Power Query scripts**: v4 (`Power_Query_M_Scripts_v4.txt`) — direct ADLS Gen2 via `DeltaLake.Table()`, no local Parquet needed, cloud refresh without gateway
  - Uses `fnGetDeltaTable` helper function + `StorageAccountUrl`/`ContainerPath` parameters
  - Fallback for MetadataJobRuns (corrupt Delta log) reads from `pbi-snapshot/` Parquet

## Phase 4 Results (historical — initial deployment, row counts now much larger)
- 9 Delta tables created in `abfss://litellm-logs@flkaienablement.dfs.core.windows.net/delta/`
- Bronze `llm_usage_raw` (5 rows), Silver `llm_usage` (5 rows), Gold Fact `llm_usage` (5 rows), Gold Agg `daily_llm_usage` (4 rows)
- dim_nodes (4), dim_users (16), dim_models (3), dim_date (121), job_runs (2)
- ETL runs in 1.4s for 5 blobs
- **Key discovery**: deltalake 1.5.0 requires `abfss://` scheme (not `az://`) with `account_name`/`account_key` storage options

## Phase 5 Resources
- **Automation Account**: `flk-llm-etl-automation` (Basic, East US 2, System Assigned MI)
- **Managed Identity**: `851f094f-9646-4518-8eb2-eac560b4a453`
- **RBAC**: VM Contributor + Run Command Admin on `llm-usage-duckdb-vm`
- **Runbook**: `Invoke-LLMUsageETL` (PowerShell, 5 steps — updated 2026-05-07 to use wrapper)
  - Steps: 1. Start VM → 2. Wait for running → 3. Deploy & run `run_etl.sh --all` (health+sync+ETL+query) → 4. Deallocate → 5. Summary
  - Deploys `run_etl.sh` from blob before execution; passes ARM+Graph tokens as env vars; sets HOME=/home/azureuser
  - Ad-hoc validation: 2026-05-07 06:25-06:28 UTC, all 4 pipeline steps success, 12/12 tables healthy, WRAPPER_EXIT_CODE=0
- **Schedule**: `Every12Hours` (07:00 + 19:00 UTC) via Azure Automation runbook; backup cron `0 */6 * * *` on VM
- **E2E Validation (2026-05-05)**: 63 consecutive jobs passed (30-day perfect streak), all 18 active Delta tables fresh, 5/5 gateways running, 15/15 model deployments healthy. Deliverables: `Usage_Tracking_E2E_Validation_20260505.docx` + `.pptx` in Usage Tracking folder.
- **E2E Validation (2026-05-11)**: Job `e2e-validation-20260511T002033` — 14/14 tables healthy (was 12/12), 0 warnings, 0 errors, all 18 Delta tables updated, content pipeline processed 5 blobs → 71 content_analytics + 40 safety_analytics rows. 65+ consecutive successful runs.

## Phase 8 Resources (Health Check)
- **Script**: `infra_health_check.py` (on VM at `<VM_HOME>/`, local at `LLM Gateway/`)
- **Delta table**: `delta/metadata/health_checks/` (28 columns, merge on `check_run_id`)
- **ARM token flow**: Runbook MI → `Get-AzAccessToken` → env var `ARM_ACCESS_TOKEN` → Python `requests`
- **Runbook step**: [3/7] non-blocking, wrapped in try/catch
- **20 Delta table paths** (19 active + 1 archive): see Canonical Delta Table Paths section for authoritative list. Content tables added 2026-04-30. Per-user usage table added 2026-05-12. PBI integration (New_base_template) completed 2026-05-13.

## Key Findings
- LiteLLM built-in `AzureBlobStorageLogger`: DFS-only writer, enterprise-gated — replaced by custom `usage_logger.py` (2026-05-05)
- LiteLLM callback naming: `"azure_storage"` is the correct string (NOT `"azure_blob"`); must be in `callbacks` list (NOT `success_callback`)
- Node derived from `model` field suffix (e.g., `claude-haiku-4-5-2-node1`)
- `status` is string "success"/"failure", not HTTP int
- Azure Marketplace output pricing is 74% higher than Anthropic direct ($130.33/M vs $75/M for Opus)
- deltalake 1.5.0: `az://` scheme → `TableNotFoundError`, must use `abfss://` with explicit account_name/account_key
- HNS migration: soft-delete artifacts (snapshots, deleted blobs) block validation even if soft-delete policy is disabled — must purge them manually
- `flkaienablement` has 4 containers: `litellm-logs` (active), `claude-{opus,sonnet,haiku}-logs` (unused)
- **Stale path trap (2026-05-11)**: ETL Bronze table is `delta/bronze/llm_usage_raw` — an old `delta/bronze/llm_usage` path existed with corrupted delta logs. Content Bronze is `delta/bronze/content_logs_raw` not `delta/content/content_logs_raw`. Content Silver is `delta/silver/content_logs` not `delta/content/content_logs`. Always check ETL code lines 65-85 for canonical paths.

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
- 19 Delta table paths total (18 active + 1 archive): see Canonical Delta Table Paths section

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
- `delta/gold/fact/llmusage/` is a stale duplicate of `delta/gold/fact/llm_usage/` — canonical path uses underscore (see also stale paths table in Canonical Delta Table Paths section)
