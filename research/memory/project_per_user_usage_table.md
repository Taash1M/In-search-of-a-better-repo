---
name: Per-User Estimated Usage Table (Option B)
description: 1:1 join between LiteLLM logs and Azure diagnostic logs via apim-request-id header capture — Top 10 Users page: AAD Users table (left) + per_user_usage table (right) on both reports, filterConfig pattern, displayName convention (2026-05-18)
type: project
originSessionId: c75a0674-7e11-4fff-8068-f0ac01bd1e3f
---
## Goal
Attribute per-individual-user token consumption and cost by linking LiteLLM usage logs (has tokens/cost) with Azure diagnostic logs (has AAD user identity).

## Approach: Option B — `apim-request-id` Passthrough (Exact Join)

Azure's diagnostic `correlationId` IS the `apim-request-id` response header. LiteLLM already captures all response headers with `llm_provider-` prefix into `_hidden_params["additional_headers"]`. We extract it in our custom callbacks and log it alongside the request.

**Why not proportional allocation (Option C)?** Reviewed as Sr DE — 7 structural gaps: no exact join key, 7-20x request count mismatch (Azure logs streaming chunks), time window misalignment (diagnostic May 5+ vs user_activity Mar 26+), shared node unallocatable (1,895 requests), model mix bias (Opus 50-100x more tokens than Haiku), no temporal granularity, no conservation check.

## Implementation Status (2026-05-12)

### Step 1: Logger Changes — DONE (all 5 nodes)
- `usage_logger.py`: Added `_extract_azure_correlation_id()` static method + `azure_correlation_id` field in payload
- `content_logger.py`: Same changes for content logs
- Extraction checks: `llm_provider-apim-request-id`, `llm_provider-x-ms-client-request-id`, `apim-request-id`, `x-ms-client-request-id` — from both `slo.hidden_params` and `response_obj._hidden_params`
- Applied to: node0, node1, node2, node3, poc

### Step 2: Deploy to Node0 — DONE (2026-05-12)
- Built via ACR Tasks: `flkdockerregistry.azurecr.io/litellm-node0:latest` (sha256:8f51cdb254...)
- App Service `flk-team-ai-llm-gateway-node-0` updated from `litellm-gateway-node0:v10` to `litellm-node0:latest`
- Stop+Start performed, health check 200 OK

### Step 3: Validate Join — DONE (2026-05-12)
- Test request: `chatcmpl-0368aba3-9cff-4e30-b717-29553cd7b215` (Haiku, 26 tokens)
- `azure_correlation_id` in blob: `706414d5-dbbd-4baa-9d45-54a6644fedc9`
- `correlationId` in diagnostic log: `706414d5-dbbd-4baa-9d45-54a6644fedc9` — **EXACT MATCH**
- **Limitation found:** Gateway requests have `objectId: ""` in diagnostic logs (API key auth, not AAD). Per-user identity only available for direct AAD-authenticated requests.
- Content log also captures `azure_correlation_id` correctly

### Step 4: Roll Out to All Nodes — DONE (2026-05-12)
- **Node1:** `litellm-node1:latest` → `flk-team-ai-llm-gateway-node1` (was v7) — azure_correlation_id=`800f6147-...` PASS
- **Node2:** `litellm-node2:latest` → `flk-team-ai-llm-gateway-node2` (was v7) — azure_correlation_id=`ba2fd065-...` PASS
- **Node3:** `litellm-node3:latest` → `flk-team-ai-llm-gateway-node3` (was v7) — azure_correlation_id=`d8573912-...` PASS
- **POC:** `litellm-poc:latest` → `flk-team-ai-llm-gateway` (was v7) — azure_correlation_id=`05e3d58b-...` PASS
- All 5 nodes: health check 200, test request success, both usage + content logs validated

### Step 5: ETL Changes — DONE (2026-05-12)
- Added `azure_correlation_id` field to Silver schema (extracted from raw blob JSON)
- Gold Fact inherits via `dict(row)` copy
- New Delta table: `delta/gold/fact/per_user_usage` (DELTA_PER_USER_USAGE)
- 3-tier join strategy via DuckDB CTE:
  1. **Exact match**: `fact.azure_correlation_id = diag.correlation_id` (new data with header capture)
  2. **Fuzzy match**: `±5s timestamp + same node_key` (historical data without correlation_id, ROW_NUMBER dedup)
  3. **Unmatched bucket**: `auth_type = 'pre-correlation'` (no correlation_id) or `'unmatched'` (correlation_id present but no diagnostic match)
- Request-level output schema: 23 columns (request_id, date_key, node_key, model_key, tokens, costs, user_name, user_email, auth_type, match_type, etc.)
- Mode: `overwrite` with `schema_mode="overwrite"` (full rebuild each run, same pattern as Gold Agg/Audit)
- Non-blocking: failure doesn't prevent rest of ETL
- Added to `_validate_delta_tables()` (15 tables, was 14)
- Added to `_write_metadata()` stats: per_user_rows_written, per_user_exact_matches, per_user_fuzzy_matches, per_user_unmatched
- Script: 2,069 lines (was 1,885), syntax verified
- Handles missing `azure_correlation_id` column in historical Gold Fact (adds empty column dynamically)

### Step 6: PBI Integration — DONE (2026-05-13)
- User manually added `per_user_usage` table to Fabric Lakehouse shortcut and PBI semantic model (TMDL)
- Added 3 relationships to `relationships.tmdl`: per_user_usage → dim_date (date_key), dim_nodes (node_key), dim_models (model_key)
- Added Flag Taxonomy (CRITICAL/HIGH/MEDIUM/LOW with color-coded severity) and Alert Escalation docs to Read Me page right textbox
- Created Content Alerts page (c3d4e5f6a7b8c9d00102) with 12 visuals: header, title, date slicer, node slicer, 5 KPI cards, combo chart, bar chart, alert detail table
- Added "Content Alerts" navigation button on Read Me page
- Updated Read Me Contents to list 5 pages (was 4)
- Updated summary stats: 15 tables, 22 relationships, 2,069 lines ETL, 15/15 validation

### Step 7: Top 10 Users Page Overhaul — DONE (2026-05-13, updated 2026-05-18)

#### New_base_template Report (2026-05-13, updated 2026-05-18)
- Full page overhaul of "Top 10 Users" (`d4e5f6a7b8c9d0e1f2a3`)
- **Two tables side-by-side:**
  - **Left: "Top 10 AAD Users"** (`a44922bce3b9409cb699`, x=10, y=570) — `diagnostic_user_activity` with filterConfig: auth_type='AAD' + user_name NOT IN ('', null). Columns: User (user_name), Email, Node (node_key), Requests (CountNonNull correlation_id), Avg_duration_ms (Avg duration_ms). Sort: Requests desc.
  - **Right: "Top 10 API Key Users"** (`b55933bce3b9409cb700`, x=965, y=570) — `per_user_usage` with filterConfig: match_type IN ('unmatched', 'fuzzy', 'infra'). Columns: Caller_ip_hash, Node (dim_nodes), Match Type, Requests (CountNonNull request_id), Total_tokens, Prompt_tokens, Completion_tokens, Total_cost_usd. Sort: total_tokens desc.
- **filterConfig pattern**: Visual-level filters use `filterConfig.filters[]` at root (NOT bare `filters[]`). See [[feedback_pbi_underlyingtype]].
- **Column displayName convention**: Aggregated columns use underscore names (Total_tokens, Prompt_tokens, etc.) with both `nativeQueryRef` and `displayName` properties.

#### Claude CLI POC Report (2026-05-18)
- **Two tables side-by-side** on "Top 10 Users" page (`d4e5f6a7b8c9d0e1f2a3`):
  - **Left: "Top 10 AAD Users"** (`b55aad10e3b9409cb700`, x=10, y=590, w=935, h=490) — NEW. Source: `diagnostic_user_activity`. filterConfig: auth_type='AAD' + user_name NOT IN ('', null). Columns: User, Email, Node, Requests (CountNonNull correlation_id), Avg_duration_ms. Sort: Requests desc. Z-order: 10200.
  - **Right: "Per-User Usage: Total Tokens & Est. Cost"** (`a44922bce3b9409cb699`, x=990, y=590, w=930, h=490) — EXISTING, moved right. Source: `per_user_usage`. Columns: Email, Requests (CountNonNull request_id), Total_tokens (Sum), Prompt_tokens (Sum), Completion_tokens (Sum), Total_cost_usd (Sum). Sort: total_tokens desc.
- **Bar charts updated 2026-05-18** (matching New_base_template):
  - Left: "Requests by AAD User" (`aa35533ee5db418581a4`) — `diagnostic_user_activity.user_name` × CountNonNull(correlation_id), filterConfig: auth_type='AAD' + non-blank user_name, data labels on
  - Right: "Total Tokens by API Key User" (`cf278591af604aa7841c`) — `per_user_usage.caller_ip_hash` × Sum(total_tokens), filterConfig: match_type IN ('unmatched', 'fuzzy', 'infra'), data labels on
- **TMDL**: `caller_ip_hash` column added to CLI POC semantic model (2026-05-18)
- **16 visuals**: 4 nav buttons, 1 separator, 1 title textbox, 2 slicers, 4 cards, 2 bar charts, 2 tables

#### Original Overhaul Details (2026-05-13, bar charts updated 2026-05-18)
- **Cards (4):**
  - Unique Users: DistinctCount(per_user_usage.user_name)
  - Total Requests: CountNonNull(per_user_usage.request_id)
  - Total Tokens: Sum(per_user_usage.total_tokens)
  - Est. Total Cost ($): Sum(per_user_usage.total_cost_usd)
- **Bar charts (2, updated 2026-05-18 — each mirrors its table below):**
  - Left: "Requests by AAD User" (`aa35533ee5db418581a4`) — `diagnostic_user_activity.user_name` × CountNonNull(correlation_id), filterConfig: auth_type='AAD' + non-blank user_name, data labels on
  - Right: "Total Tokens by API Key User" (`cf278591af604aa7841c`) — `per_user_usage.caller_ip_hash` × Sum(total_tokens), filterConfig: match_type IN ('unmatched', 'fuzzy', 'infra'), data labels on
- Slicers (dim_date.year_month, dim_nodes.node_display_name) filter via existing per_user_usage relationships

## Key Data Points (validated 2026-05-12)
- llm_usage: 14,070 rows (Mar 26 – May 12), request_id is UUID
- diagnostic_user_activity: 21,090 rows (May 5 – May 12), correlation_id is UUID
- 0% direct match between request_id and correlation_id (different systems)
- Node0 fuzzy match: 144/157 = 91.7% within ±5s, avg diff 1,025ms, 20 collisions
- Per-node diagnostic:LiteLLM ratio: 6-20x (Azure logs streaming chunks separately)
- user_activity is per-API-key (13 rows), not per-individual — emails concatenated per node
