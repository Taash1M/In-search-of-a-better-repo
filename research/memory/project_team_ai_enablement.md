---
name: Team AI Enablement (Claude Code for Team)
description: Claude Code deployment for 44 active Fluke users across 6 nodes on Azure AI Foundry. Per-user token auth LIVE on nodes 0-3. Phase 6 EXECUTED + Foundry Key1 rotated 2026-06-08: old shared keys DEAD, gateway master keys rotated (sk-admin-*), gateways migrated Key1->Key2, Key1 regenerated (20 direct API key users cut off), all validation PASS. Enterprise prompt injector $8K/mo savings.
type: project
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---
## Deployment Directory
`<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\`

## Azure AI Foundry
- **Resource**: `flk-team-ai-enablement-ai` (East US 2)
- **Subscription**: Fluke AI ML Technology (`77a0108c-5a42-42e7-8b7a-79367dbfc6a1`)
- **Resource group**: `flk-team-ai-enablement-rg`
- **Base URL**: `https://flk-team-ai-enablement-ai.services.ai.azure.com/anthropic`
- **Auth**: API key via `ANTHROPIC_FOUNDRY_API_KEY` + `CLAUDE_CODE_USE_FOUNDRY=1`
- **API key header**: `x-api-key` (not `api-key`)
- **Key discovery**: Foundry project required before Anthropic deployments; api-version=2025-12-01 required

## Models (22 deployments total, updated 2026-06-10)
- `claude-opus-4-6` (750 TPM, **Opus 4.7** since Apr 27), `claude-sonnet-4-6` (1,625 TPM), `claude-haiku-4-5` (100 TPM)
- 9 node-specific deployments for nodes 1-3 (3 per model family, 250cap each)
- 3 node-0 deployments (added 2026-04-23): `claude-opus-node-0` (Opus **4.7**), `claude-sonnet-node-0`, `claude-haiku-node-0` (250cap each)
- `claude-opus-4-8` (1,000 TPM, GlobalStandard) — added 2026-06-10
- `claude-fable-5` (1,000 TPM shared, GlobalStandard) + `claude-fable-5-Node0` (250) + `claude-fable-5-Node1` (250) — added 2026-06-10
- `text-embedding-3-small` (120 TPM, Standard)
- `gpt-5.3-codex-node-0` (5,008 TPM, GlobalStandard) — added 2026-05-08 for Codex desktop app
- `gpt-5.5` (5,000 TPM, GlobalStandard)

### Opus 4.7 Upgrade (2026-04-27)
- **In-place upgrade via PUT** — no delete+recreate needed. Azure supports changing model name/version on existing deployment.
- `claude-opus-node-0`: Opus 4.7 (reference, already upgraded)
- `claude-code-node1`: **Opus 4.7** (upgraded Apr 27)
- `claude-code-node2`: **Opus 4.7** (upgraded Apr 27)
- `claude-code-node3`: **Opus 4.6** (intentionally held — upgrade when ready)
- `claude-opus-4-6` (shared): **Opus 4.7** (upgraded Apr 27, deployment name unchanged)
- **Upgrade script**: `LLM Gateway/upgrade_opus_models.py` (~600 lines, rolling upgrade, --dry-run, --node flags, JSON backup, interactive confirmation)
- **Validation**: All 15 deployments healthy post-upgrade, live inference confirmed Opus 4.7, usage data flowing on all nodes
- **Manual upgrade**: Azure Portal (AI Services → Model deployments → Edit → change version) or REST API PUT with `properties.model.name: "claude-opus-4-7"`

## Users (45 active across nodes 1-4, verified 2026-06-10)
- node1 (9): Kevin Davison (flukenetworks.com), Eshwari Mulpuru, Urvin Thakkar, Mihai Constantin-Pau, Rachel King, Richard Feng, Taashi Manyanga, Rohit Lokwani (fortive.com, Mac), **Josh Ciaramitaro** (Sr. InfoSec Compliance Lead, NEW 2026-06-10, AAD OID `a13b90e6-7b40-47d0-989d-d252f89c5415`, in SG `47a23ea8`)
- node2 (14): Jd Giles, Richard Feng, Alex Chillman, Julian Knabe, Matt Markl, Jim Moeller, Peter Bergstrom, John Erickson, Sanjay Kalra, Taashi Manyanga, Kranthi Kothapally, Arpan Saha, Deep Katyal, **Elizaveta Petrenko** (NEW 2026-06-05, Excel add-in user, validation candidate)
- node3 (16): Vineet Thuvara, Steven Moore, Taashi Manyanga, Daniel Pouley, Azra Jabeen, Sean Sparks, Treg Vanden Berg, Ryan Bryson (flukecal.com), Adelaide Hartmann, Lloyd Hung, Kendra Zimdars, Joe Seefried, Mark Galli, Gavin Smith, Evan Nebeker, **Kathleen Wang** (NEW 2026-05-21)
- **PAUSED**: Michael Johnston (michael.johnston@flukecal.com) — removed from FLK-ai-enablement-node-3 SG on 2026-06-05. Re-add to restore access.
- node4 (13, L1 Excel): Parker Burke, Jay Hack, Claire Hu Weber, Kathya Kalinine, Katie Marquardt, Neal Nowick, Sue-Ann Prentice, Kathryn Sweers, Taashi Manyanga + cross-assigned: Alex Chillman (node2), Azra Jabeen (node3), Steven Moore (node3), Vineet Thuvara (node3)
- **Taashi Manyanga** is a member of all 4 SGs (admin/testing access)
- **Richard Feng** is in both node1 and node2 SGs

### RBAC Audit (2026-05-21, verified via Azure REST API)
42 unique users across 4 SGs (+ 37 direct RBAC user assignments), each SG has Azure AI User role on `flk-team-ai-enablement-ai`. Historical cohorts:
- **Mar 4** (10): Taashi, Kevin, Eshwari, Urvin, Mihai, JD, Richard, Alex C, Vineet, Steven
- **Mar 5** (+2): Daniel Pouley, Azra Jabeen
- **Mar 11** (+3 Finance): Julian Knabe, Rachel King, Matt Markl
- **Mar 23** (+1 IT): Sean Sparks
- **Apr 2** (+8 Executives): Parker Burke, Jay Hack, Kathryn Sweers, Sue-Ann Prentice, Katie Marquardt, Neal Nowick, Kathya Kalinine, Claire Hu Weber
- **Apr 7** (+3): Jim Moeller, Peter Bergstrom, John Erickson
- **Apr 22** (+1): Sanjay Kalra (node2)
- **Apr 22/23** (+3, Eshwari batch): Kranthi Kothapally, Arpan Saha, Deep Katyal (node2)
- **Apr 24** (+1): Michael Johnston (node3, flukecal.com)
- **Apr 28** (+1): Treg Vanden Berg (node3)
- **Apr 30** (+1): Evan Nebeker (node3)
- **Date unknown**: Joe Seefried (node3), Gavin Smith (node3) — found in SG during 2026-04-30 audit, no prior record
- **Jun 2** (+1): Rohit Lokwani (node1, fortive.com, Mac user, AAD auth, OID `0ca934f3-b091-4269-98af-c07fad83e282`)

### New Users Added 2026-04-07
| User | Email | Node | Settings File |
|------|-------|------|---------------|
| Jim Moeller | jim.moeller@fluke.com | node2 | `user-config/settings_jim_moeller_node2.json` |
| Peter Bergstrom | peter.bergstrom@fluke.com | node2 | `user-config/settings_peter_bergstrom_node2.json` |
| John Erickson | john.erickson@fluke.com | node2 | `user-config/settings_john_erickson_node2.json` |

Settings JSONs generated. Onboarding email DOCX created (2026-04-07): `user-comms/Email_ClaudeCode_node2_onboarding_jim_peter_john.docx` (CLI setup + Excel gateway credentials, references attached Quick Start Guide). RBAC role assignment status unknown — verify before sending credentials. User list file updated at `user-comms/list of users to be granted access.txt` (19 users total).

### Sanjay Kalra Added 2026-04-22
| User | Email | Node | Settings File |
|------|-------|------|---------------|
| Sanjay Kalra | sanjay.kalra@fluke.com | node2 | `user-config/settings_sanjay_kalra_node2.json` |

RBAC confirmed (Azure AI User, HTTP 201). Onboarding DOCX: `user-comms/Email_ClaudeCode_node2_onboarding_sanjay_kalra.docx` (settings.json approach with env table, 5-step CLI setup, Azure Portal key retrieval, Excel gateway creds). API key intentionally empty in settings JSON — user must retrieve from Azure Portal.

## Node 4 (POC gateway renamed for Excel add-in users)
- **Gateway URL**: `https://flk-team-ai-llm-gateway.azurewebsites.net`
- **Token**: `flk-team-da6d8bfe-de40-49fc-8e69-6987f7b6a462`
- **Routes to**: shared model deployments (not node-specific)
- **Training doc**: `docs/Training/Claude_for_Excel_Quick_Start_Guide_v3.docx`

## LLM Gateway Master Keys (per-node — CRITICAL, ROTATED 2026-06-08)
Each gateway has its OWN unique `LITELLM_MASTER_KEY`. Using the wrong key returns a **misleading** `"No connected db."` 400 error (see [[feedback-litellm-no-connected-db]]).

| App Service | Node | Key Prefix | Status |
|-------------|------|------------|--------|
| `flk-team-ai-llm-gateway` | POC/Node4 | `flk-team-da6d8bfe...f7b6a462` | **Unchanged** |
| `flk-team-ai-llm-gateway-node-0` | node0 | `sk-admin-node0-7aa77...a79a0af4` | **ROTATED** (was sk-node1...bc189ba2) |
| `flk-team-ai-llm-gateway-node1` | node1 | `sk-admin-node1-52a23...82a85d0a` | **ROTATED** (was sk-node1...bc189ba2) |
| `flk-team-ai-llm-gateway-node2` | node2 | `sk-admin-node2-84be5...d0b7d27d` | **ROTATED** (was sk-node2...b07724fb) |
| `flk-team-ai-llm-gateway-node3` | node3 | `sk-admin-node3-3498b...5601c633` | **ROTATED** (was sk-node3...44be8f00) |
| `flk-team-ai-llm-gateway-ubi` | UBI (node5+6) | `sk-ubi-...c93df21f69cf` | **Unchanged** (gateway stopped) |

**Rollback reference**: `Per-User Token Migration/master_key_rotation_20260608_173216.json`

**Query a node's key**: `az webapp config appsettings list --name <app> --resource-group flk-team-ai-enablement-rg --query "[?name=='LITELLM_MASTER_KEY'].value" -o tsv`

## User Onboarding — Security Group Model (2026-04-22)
### 3-Step Process
1. **Add user to the node's Security Group** (Entra ID)
2. **Email them** the generic onboarding DOCX + settings.json for that node
3. **Validate** their access is working

### Security Groups (Azure AI User on `flk-team-ai-enablement-ai`)
| SG Name | OID | Assigned |
|---------|-----|----------|
| FLK-ai-enablement-node-1 | `47a23ea8-a6c7-457c-bdb9-490e386641da` | 2026-04-22 |
| FLK-ai-enablement-node-2 | `78e46cdb-b147-444f-bfaf-ce5aeb043483` | 2026-04-22 |
| FLK-ai-enablement-node-3 | `64967da1-9cd6-4e29-9d9a-2ba03421ed59` | 2026-04-22 |
| FLK-ai-enablement-node-4 | `53bd21f1-b7e2-4c06-8e8b-8a81e31e5f45` | 2026-04-22 |

Node 5 (UBI subscription) uses separate SG: `flkazu-ubi-FlkBIprojects-iam-group@fluke.com`

### Generic Onboarding Materials
- **Settings files**: `user-config/settings_generic_node{1-4}.json` (API key blank)
- **Email DOCXs**: `user-comms/Email_ClaudeCode_node{1-4}_generic_onboarding.docx`
  - Part 1A: macOS CLI setup (Homebrew + Node.js + Claude Code + settings.json + API key from Portal)
  - Part 1B: Windows CLI setup (Node.js installer + PowerShell + settings.json + API key)
  - Part 2: Excel add-in setup (6 steps, credentials table, capabilities, FAQ, troubleshooting)
  - Note: PowerPoint and Word follow identical installation pattern
  - Credentials summary, Important Notes, FAQ (7 items), Support links
- **Generator**: `user-comms/generate_generic_onboarding_emails.py`

### Node-Specific Model Deployments
| Node | Opus | Sonnet | Haiku |
|------|------|--------|-------|
| 0 (test) | claude-opus-node-0 (**Opus 4.7**) | claude-sonnet-node-0 | claude-haiku-node-0 |
| 1 | claude-code-node1 | claude-sonnet-4-6-node1 | claude-haiku-4-5-2-node1 |
| 2 | claude-code-node2 | claude-sonnet-4-6-node2 | claude-haiku-4-5-2-node2 |
| 3 | claude-code-node3 | claude-sonnet-4-6-node3 | claude-haiku-4-5-2-node3 |
| 4 | claude-opus-4-6 (shared) | claude-sonnet-4-6 (shared) | claude-haiku-4-5 (shared) |

### Legacy Individual RBAC
- **Role**: Azure AI User (`53ca6127-db72-4b80-b1b0-d745d6d5456d`) on AI Services resource
- **Bug**: `az role assignment create --scope` returns `MissingSubscription` error on this subscription
- **Workaround**: Use REST API (`PUT .../Microsoft.Authorization/roleAssignments/{uuid}?api-version=2022-04-01`)
- 27 individual user assignments still active (can be cleaned up after SG membership is complete)
- **RBAC total**: 31 assignments (27 individual + 4 SGs)

## LLM Gateway Security Hardening (2026-04-23)

### Audit Findings (6 findings, F1-F6)
- **F1 (HIGH)**: Swagger UI exposed without auth at `GET /` (78-page API docs)
- **F2 (MEDIUM)**: HTTPS not enforced (`httpsOnly: false`)
- **F3 (HIGH)**: No network access restrictions (IP Allow All)
- **F4 (HIGH)**: No App Service Authentication (Easy Auth disabled)
- **F5 (LOW)**: Health endpoint leaks version info
- **F6 (CRITICAL)**: `/v1/model/info` leaks Azure AI Services API key in `extra_headers.x-api-key`

### Fixes Applied (2026-04-23) — ALL 5 GATEWAYS
| Fix | Status | Detail |
|-----|--------|--------|
| Fix 1: HTTPS Only | **DONE** | `httpsOnly: true` on all 5 gateways. HTTP → 301 redirect. Zero downtime. |
| Fix 2: Disable Swagger | **DONE** | `NO_DOCS=true` env var on all 5 gateways. Root returns `"LiteLLM: RUNNING"`. |
| Fix 3: API key redaction | OPEN | Requires Docker image config change to hide key in `/v1/model/info` |
| Fix 4: IP restrictions | BLOCKED | Waiting on Fortive corporate egress IPs from IT Network team |

### Key Finding
- `NO_DOCS=true` works on LiteLLM 1.82.6 — `DOCS_URL=""` does **NOT** work (Swagger still renders)
- Hardening plan document: `LLM Gateway/LLM_Gateway_Security_Hardening_Plan.md`

### Validation (all 5 gateways passed)
- Health endpoint returns 200
- `GET /` returns `"LiteLLM: RUNNING"` (not Swagger)
- `http://` redirects to `https://`
- All data endpoints return 401 without Bearer token

### App Service Plan Upgrade (2026-04-23)
- **B2 → B3** (7GB RAM, 4 vCPU, ~$52/mo) to accommodate 5 LiteLLM containers (~1.2GB each)
- B2 (3.5GB) was insufficient for 5 containers — node-0 caused 503 timeouts until upgrade

## Enterprise System Prompt Injector (2026-05-21)
- **Purpose**: Inject ~1,100-token enterprise system prompt (6 XML sections) into all LLM requests for cost optimization, quality standards, and guardrails
- **File**: `system_prompt_injector.py` v1.1 — `CustomLogger` subclass with `async_pre_call_hook`
- **Config dir**: `<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\node config\`
- **Key bugs fixed**: (1) `call_type` must accept both `"completion"` AND `"acompletion"` (LiteLLM proxy uses async); (2) use in-place `messages.insert()` not list reassignment; (3) YAML callbacks must use inline `[a, b, c]` format, NOT multi-line dash format
- **Kill switch**: `ENTERPRISE_PROMPT_ENABLED=false` env var → instant disable
- **Idempotency**: Detects existing `<enterprise_context>` tag to prevent double-injection
- **Projected savings**: $3,300-5,800/month (15-25% output token reduction + improved caching)
- **Design doc**: `Enterprise_System_Prompt_v1.md` in config dir

### Deployment Status (2026-05-21)
| Node | Image | Status |
|------|-------|--------|
| node0 | `litellm-gateway-node0:v12` (ca1p) | **LIVE, VALIDATED** |
| node1 | `litellm-gateway-node1:v9` (ca1q) | **LIVE, VALIDATED** |
| node2 | `litellm-gateway-node2:v9` (ca1r) | **LIVE, VALIDATED** |
| node3 | `litellm-gateway-node3:v9` (ca1s) | **LIVE, VALIDATED** |
| POC  | `litellm-poc:latest` | PLANNED (after hours — Claude Code's own gateway) |
| UBI  | `litellm-gateway-ubi:v1` (ca1t) | CONFIGURED + STOPPED (start off-peak) |

### Shareable Prompt Injector Pack (2026-06-17)
- **Location**: `LLM Gateway/Prompt injector pack/` — 5 generic artifacts + 2 generator scripts
- **Contents**: `system_prompt_injector.py` (v1.1, generic), `Enterprise_System_Prompt_v1.md`, `analyze_system_prompt_impact.py`, HowTo DOCX (5 pages), Infographic DOCX (6 pages, 3 GPT Image 2 panels)
- **3-role review**: Solution Architect, Enterprise Architect, Elite Data Engineer — 8 gaps identified and fixed
- **Key fixes**: LiteLLM v1.30+ compat note, `--deploy-date` required, `PROMPT_VERSION` constant, rate-independence note, removed phantom file refs, `--storage-key` CLI arg, skipped blob reporting, non-Claude model note
- **Purpose**: Enable other teams to replicate the $8,120/mo savings. All Fluke-specific references generalized.
- See [[project-prompt-injector-pack]] for full details

### Usage Impact — 7-Day Validated Analysis (May 27, pre=May 14-20 vs post=May 21-27)
- **Avg completion/req**: 604 → 552 tokens (**-8.5%**)
- **Cost per request**: $1.44 → $0.85 (**-41.4%**)
- **O/I ratio**: 0.0062 → 0.0076 (+22.2%)
- **Total cost**: $2,809 pre (7d) → $915 post (7d)
- **By node**: node3 +47.5% O/I (strongest), node1 +14.4%, node2 -8.9%, node0 +789.5% (tiny sample 9 reqs), POC -16.8% (control group — confirms causality)
- **By model**: claude-code (Sonnet, 95% traffic) +27.9% O/I, claude-opus +8.3%
- **Cache hit rate**: 0% in both periods — caching benefit not yet materialized
- **Avg duration**: 8.0s → 8.3s (+3.5%) — within expected overhead for ~1,100-token prompt
- **Monthly projection**: $401/day pre → $131/day post = **$8,120/month savings** (exceeds original $3,300-5,800 projection)
- **Sample**: 1,080 post (7 days) vs 1,945 pre (7 days) — statistically reliable balanced comparison
- **Analysis script**: `scripts/analyze_system_prompt_impact.py` (reusable, `--deploy-date` and `--pre-days` args)
- **Deliverables generator**: `scripts/generate_cost_comparison_deliverables.py` → DOCX + 4-sheet Excel
- **Deliverables (2026-05-27)**: `Usage Tracking/System_Prompt_Cost_Impact_Analysis_20260527.docx` + `Usage Tracking/System_Prompt_Cost_Comparison_20260527.xlsx`

## Node-0 Test Gateway (2026-04-23, updated 2026-05-21)
- **Web App**: `flk-team-ai-llm-gateway-node-0`
- **URL**: `https://flk-team-ai-llm-gateway-node-0.azurewebsites.net`
- **Image**: `flkdockerregistry.azurecr.io/litellm-gateway-node0:v12` (enterprise prompt injector v1.1, validated 2026-05-21)
- **Routes to**: node-0 model deployments (claude-opus-node-0, claude-sonnet-node-0, claude-haiku-node-0, **codex** → gpt-5.3-codex-node-0)
- **Purpose**: Dry-run testing gateway + Codex desktop app proxy
- **Config**: `node config/config_node0.yaml` + `Dockerfile`
- **Codex model** (added 2026-05-08): `model_name: codex`, routes to `azure/gpt-5.3-codex-node-0` via `https://flk-team-ai-enablement-ai.openai.azure.com/`, `api_version: 2025-04-01-preview`
- **Codex desktop app config**: `OPENAI_API_KEY=<node-0 master key>`, `OPENAI_BASE_URL=https://flk-team-ai-llm-gateway-node-0.azurewebsites.net/v1`, `OPENAI_MODEL=codex`

## LLM Gateway Usage Tracking
See [project_llm_usage_tracking.md](project_llm_usage_tracking.md). DuckDB on VM (`llm-usage-duckdb-vm`, Standard_B2ms, ~$5.27/mo, MI enabled 2026-05-05), 12h Azure Automation schedule. All 5 gateway nodes in `flkdockerregistry` ACR with custom `usage_logger.py` + `content_logger.py` callbacks. Docker images: all 5 nodes updated to `litellm-{node}:latest` (2026-05-12) with `azure_correlation_id` field. 20 Delta table paths (19 active + 1 archive — see canonical path table in project_llm_usage_tracking.md). ETL: 2,124 lines with Sonnet safety analysis + per-user 3-tier join, 15/15 table validation. Canonical script: `_scripts/llm_usage_etl_v2.py` (wrapper deploys from `_scripts/`). 65+ consecutive jobs passed (as of 2026-05-11). E2E validated 2026-05-11: all 18 active tables healthy, content pipeline live (3,753 Silver content rows, 74 content_analytics, 43 safety_analytics, 13 alerts). Content freshness window widened from 6h to 24h (2026-05-04). **Per-user usage**: `per_user_usage` Gold table with exact/fuzzy/unmatched join, PBI integration complete (3 relationships, Content Alerts page, Flag Taxonomy on Read Me). **Path warning**: Bronze is at `delta/bronze/llm_usage_raw` (NOT `delta/bronze/llm_usage` — that's a stale old path).

### azure_correlation_id Rollout (2026-05-12)
All 5 gateways now capture Azure's `apim-request-id` response header as `azure_correlation_id` in both usage and content logs. Enables 1:1 join with Azure diagnostic `correlationId`. All validated with test requests. See [project_per_user_usage_table.md](project_per_user_usage_table.md) for details.

## Infrastructure Health Check (2026-04-13, fixed 2026-04-22, validated 2026-05-05)
- Runs as Step 3/7 of `Invoke-LLMUsageETL` runbook (Every12Hours schedule)
- Checks: RG, AI Services, 15 model deployments, 26 RBAC users, 5 gateway web apps, Anthropic endpoint, content logging (blob freshness)
- Delta table: `delta/metadata/health_checks/` (28 columns)
- Verdict: HEALTHY / DEGRADED / UNHEALTHY
- Current state (2026-05-05): 15 deployments (5 Opus + 5 Sonnet + 5 Haiku), 26 Azure AI User assignments, 5 gateways Running, content freshness 24h window
- **VM Managed Identity** (2026-05-05): SystemAssigned MI enabled on `llm-usage-duckdb-vm`, principal `3dde942e-1f7a-4d87-8040-cb15d246eb4c`, Storage Blob Data Contributor on `flkaienablement` — enables script sync from VM to blob
- **MI Permissions Bug (fixed 2026-04-22)**: Automation MI `flk-llm-etl-automation` lacked Reader on RG → 403s on all ARM checks → false UNHEALTHY verdicts. Fixed by assigning Reader on `flk-team-ai-enablement-rg`. Validated with manual runbook trigger → HEALTHY 6/6.

## Usage Metrics Snapshot (30-day, 2026-04-22)
- **Total**: ~24.4M tokens, ~19,729 requests across 12 deployments
- **By model**: Opus 61% (15M tokens), Sonnet 27% (6.5M), Haiku 12% (2.9M)
- **Heaviest node**: node3 (7.5M tokens, 6,278 requests) — 5 users including Taashi
- **Zero/near-zero usage**: sonnet-node2 (0), haiku-node2 (~2 requests) — candidates for cleanup
- **Shared deployments underused**: opus shared only 222K tokens; most traffic goes through dedicated nodes
- **PBI Report**: 5-page DirectLake report (v2). Page 4 "Infrastructure Health" (18 visuals, 6 HC measures). Page 5 "Usage & Health Insights" (15 visuals, 5 cross-table TREATAS measures — combo chart requests vs latency, bar chart by verdict, KPI cards, verdict explanation notes). README lists all 5 pages. Full_date slicers rebuilt (MMM-dd-yyyy, underlying=519). 21 total modelExtensions measures.
- **Correlation tracking**: `date_key` (YYYYMMDD) + `etl_run_id` (UUID) added to health_checks; `correlation_id` to job_runs. Backfill script deployed and run.

## Node 5+6 (UBI Subscription — 2026-04-17, gateway 2026-05-21)
- **Subscription**: Fluke Unified BI (`52a1d076-bbbf-422a-9bf7-95d61247be4b`) — intentionally separate from nodes 1-4
- **Resource group**: `flkubi-prd-rg-001`
- **Resource**: `flkubi-claude-enablemen-resource`
- **Base URL**: `https://flkubi-claude-enablemen-resource.services.ai.azure.com/anthropic`
- **Models**: `claude-opus-node-5` (425 TPM), `claude-sonnet-node-5` (425 TPM), `claude-haiku-node-5` (450 TPM), `claude-opus-node-6` (250 TPM), `claude-sonnet-node-6` (251 TPM) + 3 shared deployments
- **Access**: Security group `flkazu-ubi-FlkBIprojects-iam-group@fluke.com` (group-based RBAC, not individual)
- **Settings**: `user-config/Flkubi/settings.json` (currently direct-to-Foundry — pending switch to gateway)
- **Docs**: `user-config/Flkubi/Node5_Claude_Enablement_Setup.docx` (7 sections)
- **SG config**: `user-config/SG config.txt` updated with node-5 entry

### UBI LiteLLM Gateway (2026-05-21)
- **Discovery**: `flkubi-claude` App Service is a "Claude Chat" web UI, NOT a LiteLLM gateway. No LiteLLM infrastructure exists in UBI subscription.
- **Solution**: New gateway in AI/ML subscription routing cross-subscription to UBI's AI Foundry
- **App Service**: `flk-team-ai-llm-gateway-ubi` on `flk-team-ai-llm-gateway-plan` (B3)
- **Image**: `flkdockerregistry.azurecr.io/litellm-gateway-ubi:v1` (ACR run ca1t)
- **Master key**: `sk-ubi-c682af50-0922-47b4-98bd-c93df21f69cf`
- **AZURE_AI_API_KEY**: UBI subscription key (not AI/ML)
- **GATEWAY_NODE**: `ubi`
- **Config**: `node config/config_ubi.yaml` — 5 models (3 node5 + 2 node6)
- **State**: **STOPPED** — fully configured (17 settings, HTTPS-only, ACR creds), awaiting off-peak start + validation
- **B3 capacity**: CPU 4.5%, Memory 67.9% (5 running) → projected ~82% with UBI. Upgrade trigger: >85% → P1v2

## Outlook Email Export (Claude Access Requests)
- **Dir**: `requests/` | **Output**: `requests/exported_pdfs/` + `_manifest.csv`
- **v1** (2026-04-17): `Export-ClaudeRequests.ps1` — PS1, Outlook COM → MHTML → Word COM PDF, searched all 78 subfolders, any "claude" mention
- **v2** (2026-04-19): `export_claude_requests_v2.py` + `run_export.bat` — Python, Outlook COM + Edge headless PDF, Inbox only, 2026 date filter, 17 regex access-request patterns

### v2 Architecture (the working method)
1. **Auth**: Outlook COM via `win32com.client.Dispatch("Outlook.Application")` — requires <USER> session
2. **Search**: DASL filter on Inbox only: `subject/body LIKE '%claude%' AND datereceived >= 2026-01-01`
3. **Filter**: Secondary Python regex (17 patterns) for explicit access-request language (access, request, setup, enable, license, onboard, deploy, pilot, trial, etc.)
4. **Export**: `mail.HTMLBody` → styled HTML wrapper → Edge headless (`--headless --print-to-pdf`) → PDF
5. **Manifest**: CSV with Date, Sender, Email, Subject, MatchedPhrase, Status

### Cross-session execution trick (<ADMIN_USER> → <USER>)
- **Problem**: COM can't cross Windows user sessions. Graph API blocked by Fortive tenant (AADSTS65002/AADSTS50105 for all tested client IDs: Office, Graph CLI, Azure CLI).
- **Solution**: `run_export.bat` wraps Python call with full path (`<USER_HOME>/Python312\python.exe`). Launch via `explorer.exe "path\to\run_export.bat"` from admin session — Explorer runs as desktop user (<USER>), so the .bat inherits <USER>'s session. Output redirected to `export_log.txt` for polling from admin session.
- **Python path**: <USER> profile has `<USER_HOME>/Python312\python.exe` (not on PATH for that user — must use full path in .bat)

### Run results (2026-04-19)
- 13,232 Inbox items → 130 DASL matches → 60 exported PDFs, 2 Edge timeouts, 47 filtered out (no access language)
- **False positives identified**: Microsoft PIM notifications (6), Outlook Reaction Digests (2), Teams notification emails (2), setup guide thread replies (~25), EOD status updates (4)
- **Genuine requests**: Bergstrom, Knabe, King (5 licenses), Moeller, Johnston, Erickson, Schultz, plus forwarded business cases from Mulpuru
- **Next run**: tighten filters to exclude system senders (microsoft.com, system-notification@fortive.com) and setup-guide-thread replies

## Deliverables (updated 2026-04-28)
Three documents built from the email export analysis:

### 1. Access Requests Summary (DOCX) — UPDATED 2026-05-28
- **Files**: `requests/Claude_Code_Access_Requests_Summary_May2026.docx` + `requests/Claude_Code_Access_Requests.xlsx`
- **Current state (2026-05-28)**: 26 requests (12 fulfilled / ~21 seats, 12 pending / ~23 seats, 2 routed to GitHub Copilot)
- **Fulfilled**: Knabe(1), Bergstrom(1), Erickson(1), Moeller(5), Johnston(1), Kalra(1), Eshwari team(6), Treg(1), Nebeker(1), Hartmann(1), Kathleen Wang(1), Rachel King(5)
- **Pending**: Cornely(1), Schultz(2), Bridges(6), McNeal(1), Straka(1), Poondla(1), Schuster(1), Johnson(1), Pilla(1), Jack Henry(1), Venkata Mahesh Nandam(1), Marco Rossi(1)
- **Routed to GitHub Copilot**: Andy Nguyen, Todd Tomlinson (+Sandeep)
- **New since May 21**: Rachel King moved Pending→Fulfilled; Venkata Mahesh Nandam and Marco Rossi added as pending
- **Undocumented SG additions**: Joe Seefried, Gavin Smith, Kathleen Wang (all node-3, no request on file)
- **Current users Excel**: `requests/Claude_Code_Current_Users.xlsx` (42 unique users, 50 memberships across 4 SGs)
- **Daily update workflow**: See [reference_access_request_workflow.md](reference_access_request_workflow.md)
- **Eshwari directive (Apr 22)**: All CLI requests must be routed through her for approval/cost justification

### 1b. Enterprise License Allocation — NEW 2026-05-28
- **File**: `requests/Enterprise Licenses/Claude Users Access - Fluke.xlsx`
- **Tabs**: Eligible (11 org columns), Blocked (11 users), Wave 1 Users (70 users)
- **Orgs**: Finance (Azra Jabeen), Operations (Neal Nowick), eMaint (Jay Hack), Commercial Americas (Steven Moore), Engineering (Alex Chillman), HR (Katie Marquardt), Marketing (Sue-Ann Prentice), Product (Vineet Thuvara), Legal (Kathryn Sweers), CEO (Parker Burke), IT (Eshwari Mulpuru)
- **Wave 1 Users**: 70 users, all "Standard" allocation, populated from Eligible tab + Access Requests + Current Users
- **Blocked**: Claire Weber, Valeria Menes, Przemek Abramowicz, Sandra Baijens, Andrea Gratton, Geeta Miriyala, Chunyan Liu, Jai Gandhi, Jerry Paton, Sue-Ann Prentice, Olivia Kline (EMEA/legal restrictions)
- **Scripts**: `update_enterprise.py` (adds users to both tabs), `fix_notice.py` (beautifies enablement notice)
- **Enterprise rollout**: Wave 1 (Fluke, FHS, Fortive corporate) live May 26, Wave 2 (Gordian, ISC, ServiceChannel, Censis) May 27, Accruent+Provation May 28

### 1c. Enablement Notice — UPDATED 2026-06-01
- **v1 (DOCX)**: `requests/Enterprise Licenses/Claude Code enablement notice.docx` (May 2026, original)
- **v2 (DOCX)**: `requests/Enterprise Licenses/Claude Code enablement notice v2.docx` (June 2026)
- **v2 (HTML)**: `requests/Enterprise Licenses/Claude Code enablement notice v2.html` — email-paste-friendly version (open in browser → Ctrl+A → Ctrl+C → paste into Outlook). HTML preserves formatting; DOCX copy-paste loses it.
- **Generator**: `requests/Enterprise Licenses/build_notice_v2.py`
- **Audience**: C-Suite, Directors, and existing POC users
- **Format**: Consultant-grade with icons, navy palette (#1A3A5C), 8pt body / 11pt headers
- **Sections**: Title → What Is Claude → How to Get Started (4 steps) → Desktop App (still being enabled, use claude.ai) → **POC/O365 Add-in Migration** (NEW in v2) → Support & Escalation → Responsible AI Training → Key Reminders → Getting the Most from Claude (4 tips) → FAQ (4 Q&As) → Closing
- **v2 changes from v1**:
  - Date updated to June 2026
  - New section "For Existing Claude POC & O365 Add-in Users" — thanks POC participants, POC ending, API key rotating end of week, 4-step logout/SSO re-auth instructions
  - Clarifies: personal subscriptions on @fluke.com/@fortive.com email MUST re-auth to SSO; fully personal (non-Fortive email) NOT affected but should not be used on corporate devices
  - Desktop App messaging updated: still being enabled, some features not fully functional, use claude.ai, Fortive will confirm Software Center availability
- **Email list**: `requests/wave1_email_list.txt` — 62 semicolon-separated emails (Wave 1 minus 9 excluded users)
- **FAQ topics**: Usage tracking reports, token limit adjustments, monthly billing, cross-charge timeline
- **Names retained** (user override of no-PII policy): Bill Karazsia, Taashi Manyanga, Eshwari Mulpuru

### 1d. Enterprise License Overlap Analysis — NEW 2026-05-31
- **Objective**: Identify users who should be REMOVED from Enterprise licenses because they already have working node access
- **Scripts**: `requests/build_overlap.py` (4-sheet overlap Excel), `requests/add_recommendation_tab.py` (License Recommendation tab)
- **Output**: `requests/Claude_Code_Day1_Current_Overlap.xlsx` (5 sheets: License Recommendation, By Org, Eligible, Need Node Access, Usage Summary)
- **Overlap stats**: 63 Wave 1 enterprise users vs 42 current node users = **30 overlap** (on both lists), 33 need node access, 12 node-only
- **May 2026 usage data**: Queried `diagnostic_user_activity` (AAD requests) + `per_user_usage` (tokens) Delta tables from local Windows machine using storage account key + azure-storage-blob + pyarrow
- **Tracking gap**: Only 10 of 30 overlap users have individual-level tracking (AAD auth); 20 still on shared API key auth (untrackable)
- **Recommendations** (ranked by May total tokens):
  - **REMOVE (4)**: Mid-tier node users safe to drop from enterprise — Pete Bergstrom (179K tokens), Julian Knabe (129K), Lloyd Hung (123K), Michael Johnston (81K)
  - **Keep — power users (5)**: Ryan Bryson (14.1M), Joe Seefried (8.7M), Adelaide Hartmann (1.4M), Gavin Smith (616K), Evan Nebeker (312K)
  - **Keep — low usage (1)**: Bottom-ranked tracked user (needs enablement or more time)
  - **Keep — untracked (20)**: API key auth, no individual usage data — can't recommend removal without evidence
- **Color coding**: Green=remove, Blue=keep power, Orange=keep low, Yellow=untracked
- **Local Delta query pattern**: `read_delta_table()` function — parses `_delta_log/*.json` for active parquet files, downloads via blob SDK, reads with pyarrow. Mimics ETL connection pattern without needing VM/DuckDB.

### 2. Business Case Presentation (PPTX)
- **File**: `requests/Claude_Code_Enablement_Business_Case.pptx` (51KB, 9 slides)
- Generator: `requests/build_deliverables.py`
- Slides: Title → "What We've Built" (KPI cards + node breakdown) → "Business Demand Signal" (request table + chart + callout) → "Scale Plan to 45 Users" (3-phase roadmap + governance pillars) → Closing ("The Ask")
- Styled to match Leadership Forum reference (`Fluke_leadership_forum_draft ii.pptx`): Arial/Arial Black fonts, #003366 navy palette, category stamps, shadow cards

### PPTX Bug Fix (2026-04-19)
Initial PPTX errored on open. Three root causes:
1. **Invalid `a:bodyPr anchor='tl'`** — OOXML only accepts `t`, `ctr`, `b`. Fixed with `_anchor_str()` helper.
2. **Positive bullet indent** — OOXML `a:pPr indent` for hanging bullets must be negative. Changed to `-177800`.
3. **`str(PRGBColor)` in XML** — Fragile; replaced with `f'{fill[0]:02X}{fill[1]:02X}{fill[2]:02X}'` for clean 6-char hex.

### 3. Executive DOCX (completed)
- **File**: `requests/Claude_Code_Enablement_Executive_Briefing.docx` (395KB)
- Generator: `requests/build_exec_docx.py`
- 3 sections: What's Delivered (KPI strip + initiative progress chart + architecture diagram), Business Demand & Feedback (request table + demand chart + use cases), Next Steps & Scale Plan (3-phase roadmap)
- 5 matplotlib charts embedded, navy banners, blue accent lines, callout boxes, alternating-row tables
- Sources: Leadership Forum PPTX content + office hours email feedback + email export analysis

## Per-User Usage Tracking via AAD Auth (2026-04-24)

### Problem
Current API-key auth produces blank `objectId` in Azure Diagnostic Logs — usage can only be tracked at node level, not per user.

### Solution: AAD Authentication Migration
- When `ANTHROPIC_FOUNDRY_API_KEY` is unset, Claude Code uses `DefaultAzureCredential` → `az login` token
- AAD auth populates `objectId` (Entra OID) in diagnostic logs → resolved via `dim_aad_users` cache (35 users pre-seeded from RBAC) or Graph API fallback
- `disableLocalAuth` stays `false` on `flk-team-ai-enablement-ai` (coexistence: both API key and AAD work simultaneously)
- Users already have Azure AI User RBAC via 4 security groups — no new permissions needed

### Rollout Status (2026-04-27)
- **Phase 0**: Diagnostic logging enabled — **DONE** (Apr 24)
- **Phase 1**: Pilot AAD auth — **DONE** (Apr 27, 4 users confirmed flowing: Julian, Danny, Kevin, Taashi)
- **Phase 4**: ETL v3 integration — **DONE** (Apr 27, 939 lines, diagnostic log processing + user resolution)
- **AAD User Sync**: `sync_aad_users.py` — **DONE** (Apr 27, 35 users seeded in `dim_aad_users` from RBAC roster)
- **Runbook**: 7-step orchestration — **DONE** (Apr 27, new Step 4: RBAC → Graph → Delta)
- **Phase 2**: Self-service `migrate_to_aad.bat` — PENDING
- **Phase 3**: AAD-only for new users — PENDING
- **Phase 5**: PBI per-user usage dashboards — PENDING
- **Blocker**: MI `flk-llm-etl-automation` needs `User.Read.All` (Graph app permission) from tenant admin for automated new-user resolution. Pre-seeded cache covers all 34 current RBAC users.

### AAD User Config (no API key)
```bash
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE="flk-team-ai-enablement-ai"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-code-nodeX"
# No ANTHROPIC_FOUNDRY_API_KEY — uses az login token
```

### Key Documents
- Plan: `Usage Tracking/Per_User_Usage_Tracking_Plan.md` (741 lines)
- Implementation Guide: `Usage Tracking/Per_User_Usage_Tracking_Implementation_Guide.docx` (206 paragraphs, 14 tables, 6 D2 diagrams)
- D2 diagrams: `Usage Tracking/diagrams/` (6 .d2/.svg/.png files)
- AAD analysis: `Usage Tracking/AAD_User_Report_Apr24-27.md`

## AI Advisory Committee C-Suite Email (2026-04-24)
- **File**: `<USER_HOME>/OneDrive - <ORG>\AI\AI Advisory Committee\AI_Charter_Progress_Update_CLevel_April2026.docx`
- **Content**: Executive summary + 4 real use cases (JD Giles channel coverage, Vineet CRS docs, Steven competitive intel, Julian M&A models) + 7 strategic decisions table + governance + risk awareness ("dangerously powerful" CLI)
- **Sources**: Two AI Office Hours transcripts (Apr 10 + Apr 24) + AI Next Steps Plan PPTX
- **Use cases with metrics**: JD (3 days → 1.5 hours), Vineet (3 weeks → 30 min), Steven (18 competitors analyzed), Julian (3-4 hours → 30 min)

## Architecture Diagrams & Miro Board (2026-04-30)

### Miro Board
- **URL**: `https://miro.com/app/board/uXjVHajHEbE=/`
- **Content**: 16 native Miro flowchart diagrams in presentation-ready 7x3 grid + 5 Azure-icon PNGs + 5 D2-rendered SVGs (legacy)

### Board Layout — Presentation Grid (reorganized 2026-04-30)
| | Phase 1 (x=-5000) | Phase 2 (x=500) | Phase 3 (x=6000) | Phase 4 (x=11500) | Infra (x=17000) | Phase 5 (x=22500) | PBI (x=28000) |
|---|---|---|---|---|---|---|---|
| **Row 1** Architecture (y=-13844) | CLI Arch | Gateway Arch | ETL Arch | Security Arch | Resource Landscape | Content Logging Arch | Content Analysis |
| **Row 2** Flow (y=-11279) | CLI Flow | Gateway Flow | ETL Flow | Security Flow | Provisioning Flow | Content Process Flow | Content Alerts |
| **Row 3** Detail (y=-8713) | — | — | — | — | — | Content Data Flow | README Safety |

All v2 content (31 users, 19 tables, 6h ETL, PBI LIVE 10 pages, content logging, Haiku safety). PBI column has wireframe diagrams; actual mockup PNGs at `Usage Tracking/pbi_mockups/`.

### Azure-Icon Architecture PNGs (drag-drop to board)
Generated via `azure_diagrams.py` with real Microsoft Azure SVG icons:
- **Location**: `<USER_HOME>/OneDrive - <ORG>\AI\Miro\Claude Code Deployment\architecture\`
- `phase1_azure_arch.png` — 13 nodes: 3 user groups → CLI → Entra/RBAC → AI Foundry → 3 node deployments + shared pool
- `phase2_azure_arch.png` — 14 nodes: users → clients → 5 LiteLLM gateways → AI Foundry, container infra sidebar
- `phase3_azure_arch.png` — 15 nodes: 5 gateways → Blob → VM pipeline → Bronze → Silver → Gold star schema
- `phase4_azure_arch.png` — 12 nodes: 3 defense-in-depth layers (transport+identity, API hardening, key management)
- `infra_azure_landscape.png` — 15 services in grid layout (subscription → RG → all resources with SKUs/costs)
- **Generator**: `diagrams/generate_azure_arch_v2.py` (uses Node/Connection/Boundary/DiagramConfig API, standalone preset)

### D2 Data Flow Diagrams
- **Source**: `<USER_HOME>/OneDrive - <ORG>\AI\Miro\Claude Code Deployment\dataflow-d2\`
- **SVGs**: `<USER_HOME>/OneDrive - <ORG>\AI\Miro\Claude Code Deployment\dataflow-svg\`
- 5 diagrams: phase1_cli, phase2_gateway, phase3_etl, phase4_security, infra (each .d2 + .svg)
- D2 CLI v0.7.1 at `<USER_HOME>/tools\d2\d2-v0.7.1\bin\d2.exe`
- D2 gotcha: `$` triggers variable substitution — use `52/mo` not `$52/mo`

### 4. Use-Case Mapping Infographic (DOCX) — 2026-05-21
5 versions created from 24 access requests, mapping requestors to use cases and anticipated benefits:

| Version | File | Method | Key Feature |
|---------|------|--------|-------------|
| v1 | `Claude_Code_UseCase_Map_v1.docx` | python-docx nested tables | 3×2 grid, category cards, status indicators |
| v1.5 | `Claude_Code_UseCase_Map_v1.5_D2.docx` | D2 `sql_table` + grid layout | Rendered diagram embedded in DOCX |
| v2 | `Claude_Code_UseCase_Map_v2.docx` | python-docx polished | Gold stat highlights, ●/○ status, ROI stats bar |
| v3 | `Claude_Code_UseCase_Map_v3_MindMap.docx` | D2 multi-page (3 pages) | Dashed cross-connections between related use cases |
| Infographic | `Claude_Code_UseCase_Infographic.docx` | GPT Image 2 (7 panels) | Flat 2D illustrations, 3-column insights panel |

**6 categories**: Software & Firmware Dev (4), Financial Analysis (4), Data & Vulnerability Analysis (3), Commercial Strategy & Sales (3), Documentation & Productivity (4), Engineering & Product (4)

**Cross-cutting themes identified**: Documentation Generation (4 users), Automation (3 users), Strategic Intelligence (3 users), Time Compression (3 users with >90% reduction)

**GPT Image 2 infographic**: 7 panels (1 hero + 6 category), 537s total generation time, cached in `%TEMP%/usecase_infographic/` for iteration. 3-page DOCX with alternating illustration/text panels + insights panel (themes, quantified impact, unique cases).

All outputs in: `requests/`

## Per-User Token Migration (2026-06-02)

### Plan
- **v3 Final**: `LLM Gateway/Per-User Token Migration/v3_final_migration_plan.md`
- **Architecture DOCX**: `LLM Gateway/Per-User Token Migration/Per_User_Token_Migration_Architecture.docx`
- **Approach**: Custom auth (no PostgreSQL, $0 cost) — per-user bearer tokens in JSON registry on Azure Blob
- **Superseded plans**: v1 (PostgreSQL), v2 (custom auth draft), v2_architect_review, v3 draft — all in same folder
- **Key design decisions**: No database, blob-hosted registry with 5-min reload, baked-in fallback, atomic ref swap, kill switch env var, AAD JWT deferred to future

### Build Context Reconciliation (2026-06-02)
- **Problem found**: All 5 Dockerfiles on disk were stale (dated May 4-5, pre-injector). Missing `COPY system_prompt_injector.py`. Building from them would have regressed the $8K/mo savings.
- **Archive**: `LLM Gateway/archive/pre-per-user-token-migration-20260602/` — 31 files (5 node contexts + node-config-deployed snapshot)
- **Fix applied**: All 5 build contexts updated with latest configs from `node config/`, system_prompt_injector.py copied in, Dockerfiles updated with COPY line
- **Validated**: All 5 nodes pass (Dockerfile has injector COPY, config has injector callback, .py file present)
- **Node 0 ready for POC**: Build context is clean and correct for v13 image build

### Node-0 POC (LIVE — 2026-06-03)
- **Image**: `litellm-gateway-node0:v13` (ACR run ca1u)
- **Auth module**: `user_key_auth.py` v1.0 — async function, blob registry, master key fallback, rate limiting, kill switch
- **Registry**: 43 users + 1 deprecated shared key, uploaded to blob `config/user_registry_node0.json` (17.7KB)
- **Test results**: 5/5 PASS (invalid→401, master→200, per-user→200 with user_id, deprecated→200, disabled→401)
- **Usage logger verified**: `user_api_key_user_id: <USER>@<ORG_DOMAIN>` flows into usage log blobs automatically
- **Token DOCX**: `Per-User Token Migration/Per_User_Token_Distribution_Node0.docx` (43 users, grouped by home node)
- **Soak started**: 2026-06-03 ~07:40 UTC
- **Post-soak validation**: 17 blobs, 5 successes with user identity confirmed (Sonnet 742p/15c, Opus 1134p/60c, Haiku 739p/8c as <USER>@<ORG_DOMAIN> + 2 admin requests). Haiku had one upstream Azure AI Foundry auth error (our auth passed, model rejected — transient).
- **Gotcha found**: Regenerating 43-user registry replaced the original test token — old token `sk-node0-5808...` stopped working. Taashi's live token is `sk-node0-d44e...` from `token_list_node0.json`. Always reference the token list, not hardcoded values.
- **Next**: Nodes 2+3 deployed (2026-06-05), POC image built (v2), Elizaveta Petrenko validation pending

### Node-0 Soak Validation (2026-06-04, PASSED)
- **Soak period**: June 3 07:40 → June 4 06:02 UTC (22.5h)
- **Real API successes**: 5/5 with user identity (`<USER>@<ORG_DOMAIN>` + `admin`)
- **Production failures**: 0 (11 "failures" = auth rejections by design + 1 transient upstream)
- **Live test**: 4/4 PASS (per-user→200, master→200, invalid→401, deprecated→200)
- **Health probes**: Log as `call_type="/health"` with `status="failure"` — noise, not real failures

### Node-1 Production Deploy (2026-06-04, LIVE)
- **Image**: `litellm-gateway-node1:v10` (ACR run ca1v)
- **Test results**: 5/5 PASS (Taashi per-user→200, master→200, invalid→401, deprecated→200, Rohit per-user→200)
- **Usage blobs verified**: `user_api_key_user_id: <USER>@<ORG_DOMAIN>` + `rohit.lokwani@fortive.com` confirmed in blob metadata
- **Registry**: 43 users + 1 deprecated shared key, uploaded to blob `config/user_registry_node1.json`
- **Token list**: `Per-User Token Migration/token_list_node1.json`

### ETL Fixes for Per-User Identity (2026-06-04, deployed)
1. **Silver layer (line 1597)**: Added `metadata.user_api_key_user_email` and `metadata.user_api_key_user_id` to user_email extraction chain. Old code only checked `metadata.user_email` which per-user tokens don't set.
2. **per_user_usage Gold (3 CTEs)**: Changed `exact_matches`, `fuzzy_matches`, `unmatched` to use `COALESCE(NULLIF(diagnostic_email, ''), NULLIF(fact_user_email, ''), '')`. Previously, user_email came only from diagnostic log join — per-user token identity was lost.
3. **E2E validated**: `<USER>@<ORG_DOMAIN>` confirmed in per_user_usage Gold table (match_type=unmatched, 745 tokens, $0.0112)

### Node-3 Production Deploy (2026-06-05, LIVE)
- **Image**: `litellm-gateway-node3:v10` (ACR run ca1x)
- **Test results**: 5/5 PASS (invalid→401, master→200, Taashi→200, Vineet→200, Steven→200)
- **Usage blobs verified**: `<USER>@<ORG_DOMAIN>` + `vineet.thuvara@fluke.com` + `steven.moore@fluke.com` confirmed
- **Registry**: 45 users, uploaded to blob `config/user_registry_node3.json`

### Current Docker Image Tags (deployed)
| Node | Image | Version | Date |
|------|-------|---------|------|
| node0 | litellm-gateway-node0 | **v13** (custom auth) | **2026-06-03** |
| node1 | litellm-gateway-node1 | **v11** (custom auth, +Josh Ciaramitaro) | **2026-06-10** |
| node2 | litellm-gateway-node2 | **v10** (custom auth) | **2026-06-05** |
| node3 | litellm-gateway-node3 | **v10** (custom auth) | **2026-06-05** |
| POC | litellm-poc | **v2 built** (custom auth) | Ready to deploy |
| UBI | litellm-gateway-ubi | v1 | 2026-05-21 |

### Node-2 Production Deploy (2026-06-05, LIVE)
- **Image**: `litellm-gateway-node2:v10` (ACR run ca1w)
- **Test results**: 5/5 PASS (invalid→401, master→200, Taashi→200, Julian→200, old shared→200)
- **Usage blobs verified**: `<USER>@<ORG_DOMAIN>` + `julian.knabe@fluke.com` confirmed in blob metadata
- **Registry**: 43 users, uploaded to blob `config/user_registry_node2.json`
- **Token list**: `Per-User Token Migration/token_list_node2.json`

### Per-Node Registries (pre-Phase 6 — superseded by post-Phase 6 table below)
| Node | Blob Path | Users | Deprecated Keys |
|------|-----------|-------|-----------------|
| node0 | `config/user_registry_node0.json` | 45 | ~~1~~ → 0 |
| node1 | `config/user_registry_node1.json` | 45 | ~~1~~ → 0 |
| node2 | `config/user_registry_node2.json` | 45 | ~~1~~ → 0 |
| node3 | `config/user_registry_node3.json` | 45 | ~~1~~ → 0 |
| poc | `config/user_registry_poc.json` | 45 | 0 (untouched) |

### GitHub Repos (both up to date as of 2026-05-31)
- **PLM-AI-Drawing-tool**: 7 PRs merged, main branch current
- **PLM-AI-Drawing-tool-Azure**: 2 PRs merged, main branch current

### Per-User Budget Tracking — MONITOR ONLY (2026-06-10 decision)
- Each user registry entry has `max_budget_monthly_usd: 200.0`, `tpm_limit: 100000`, `rpm_limit: 50`
- `user_key_auth.py` passes `max_budget` to LiteLLM's `UserAPIKeyAuth` — but **LiteLLM has no database backend** to track cumulative spend
- `config.yaml` has no `database_url` — budget/TPM/RPM limits are accepted but **never enforced**
- **Architecture is observe-only**: usage_logger.py → blob → ETL → Delta tables → PBI reports. Users are NOT blocked at $200.
- **Decision**: Continue monitor-only approach. If enforcement is ever needed, two options: (1) PostgreSQL backend for native LiteLLM enforcement, (2) custom enforcement in `user_key_auth.py` querying Delta tables at auth time
- TPM/RPM: LiteLLM does in-memory rate limiting (resets on container restart), but without a DB this is best-effort

### Docker Access (2026-06-10)
- `<USER>` account now has Docker Desktop access — can do local builds instead of ACR cloud builds (`az acr build`)
- ACR cloud build still works as fallback (used for Josh's v11 deployment)

### Per-User Token Migration Emails (2026-06-05)
- **Generator**: `user-comms/generate_per_user_token_emails.py`
- **Output**: `user-comms/Per-User Token Emails/` — 36 subfolders (one per user), each containing `.docx` + `.html`
- **Scope**: Nodes 1-3 home users, Michael Johnston excluded (paused)
- **Content**: Short migration notice — personal token, gateway URL, CLI settings.json update, Excel/PPT/Word add-in update, security reminder
- **Folder naming**: `{email_prefix}_{node}` (email-based to avoid name collisions — e.g. Mihai has two email variants)
- **Validation**: 36/36 PASS — correct token, gateway, email, model verified against source token_list JSONs, no cross-node gateway leaks
- **Node counts**: node1=9, node2=12, node3=15

### Credential Rotation Broadcast Email (2026-06-08)
- **Purpose**: Notify all 43 POC users that API keys and shared gateway credentials are being rotated today due to Enterprise SSO migration
- **v1 (verbose)**: `user-comms/Email_Credential_Rotation_June2026.html` — full sections: Path A (Enterprise license → CLI export + SSO), Path B (no license → contact Taashi), What's Not Changing, Timeline, Support
- **v2 (concise)**: `user-comms/Email_Credential_Rotation_June2026_v2.html` — one-pager, two-column layout (Enterprise left / No License right), no-scroll design
- **Recipient list**: `user-comms/claude_cli_all_node_users.txt` — 43 unique emails across nodes 1-4 (semicolon-separated for Outlook paste), Michael Johnston excluded (paused)
- **User breakdown**: node1=8, node2=12, node3=15, node4=8 unique (excludes cross-assigned)
- **Two migration paths**:
  - **Enterprise license holders**: Run `claude export` → open Claude Code App → SSO login → import .md. O365 add-in: logout → SSO re-login.
  - **No enterprise license yet**: Contact Taashi directly for updated CLI credentials.

### Phase 6: Credential Rotation EXECUTED (2026-06-08)
- **v3 plan reference**: Phase 6 of `LLM Gateway/Per-User Token Migration/v3_final_migration_plan.md`
- **Script**: `LLM Gateway/rotate_credentials.py` (dry-run + --execute + --validate modes)
- **Step 1 — Disabled deprecated shared keys**: All 4 blob registries patched (`deprecated_shared_keys: []`, `allow_deprecated_shared_keys: false`). Uploaded to blob.
- **Step 2 — Rotated LITELLM_MASTER_KEY on nodes 0-3**: Old shared keys replaced with admin-only keys (`sk-admin-node{N}-{uuid}`)
  - node0: `sk-node1-9a1f3941-...bc189ba2` → `sk-admin-node0-7aa77...a79a0af4`
  - node1: `sk-node1-9a1f3941-...bc189ba2` → `sk-admin-node1-52a23...82a85d0a`
  - node2: `sk-node2-8e15add8-...b07724fb` → `sk-admin-node2-84be5...d0b7d27d`
  - node3: `sk-node3-f0e0a5dc-...44be8f00` → `sk-admin-node3-3498b...5601c633`
- **Step 3 — Validation**: 12/12 PASS (new admin→200, per-user Taashi→200, invalid→401 on all 4 nodes). All 3 old shared keys return 401 on all 4 nodes (12/12 rejection tests).
- **Rollback file**: `Per-User Token Migration/master_key_rotation_20260608_173216.json` (old + new keys for all 4 nodes)
- **POC gateway**: Untouched (user decision) — `flk-team-ai-llm-gateway` keeps old master key `flk-team-da6d8bfe...`
- **UBI gateway**: Already stopped, no action
- **Key finding during investigation**: `caller_ip_hash` in PBI report is the gateway's outbound IP (shared by all users on a node), NOT end-user IP. Cannot resolve to individual users. Per-user token `user_api_key_user_email` is the only reliable identity path. With old shared keys now dead, all traffic will carry per-user identity.
- **IP hash investigation script**: `LLM Gateway/identify_ip_hashes.py` — queries Delta tables to map caller_ip_hash to resolved users

### Per-Node Registries (post-Phase 6, updated 2026-06-10)
| Node | Blob Path | Users | Deprecated Keys | allow_deprecated |
|------|-----------|-------|-----------------|------------------|
| node0 | `config/user_registry_node0.json` | 45 | **0** | **false** |
| node1 | `config/user_registry_node1.json` | **44** (+Josh Ciaramitaro, 2026-06-10) | **0** | **false** |
| node2 | `config/user_registry_node2.json` | 45 | **0** | **false** |
| node3 | `config/user_registry_node3.json` | 45 | **0** | **false** |
| poc | `config/user_registry_poc.json` | 45 | 0 | true (untouched) |

### Azure AI Services Key Rotation (2026-06-08)
- **Resource**: `flk-team-ai-enablement-ai` (has Key1 + Key2, standard Azure two-key pattern)
- **Script**: `LLM Gateway/rotate_foundry_key.py` (--step1 swap, --step2 regenerate, --validate)
- **Investigation**: `LLM Gateway/check_apikey_users.py` found 20 unique IPs using direct API Key auth (bypassing gateway) since Jun 1, 0 identifiable via AAD cross-ref
- **Step 1 — Migrated gateways Key1 -> Key2**: All 5 gateways (`AZURE_AI_API_KEY`) swapped from Key1 (`5RjMeVsH...ACOGFjYY`) to Key2 (`9mhth2AX...ACOGmjbG`). Taashi CLI settings.json updated. 5/5 health OK, 4/4 per-user token OK.
- **Step 2 — Regenerated Key1**: Old Key1 (`5RjMeVsH...`) now dead (returns 401). New Key1 = `ApyfNAGf...ACOGQZA7`. Key2 unchanged. All gateways confirmed still working on Key2.
- **Result**: 20 direct API Key CLI users cut off (will get 401). Must migrate to AAD (`az login`) or gateway + per-user token.
- **Rollback file**: `Per-User Token Migration/foundry_key_rotation_20260608_191042.json`
- **UBI key**: Separate resource (`flkubi-claude-enablemen-resource`), NOT affected by this rotation

### Azure AI Services Keys (post-rotation)
| Key | Value Prefix | Status | Used By |
|-----|-------------|--------|---------|
| Key1 | `ApyfNAGf...ACOGQZA7` | **NEW** (regenerated) | Available but not assigned |
| Key2 | `9mhth2AX...ACOGmjbG` | Active | **All 5 gateways + Taashi CLI** |

### Full Credential Rotation Summary (2026-06-08)
Three layers rotated in one session:
1. **Gateway deprecated shared keys** — disabled in blob registries (`allow_deprecated_shared_keys: false`)
2. **Gateway master keys** — rotated to `sk-admin-node{N}-{uuid}` (old shared user keys dead)
3. **Azure AI Services Key1** — regenerated (20 direct API Key users dead, gateways on Key2)

**Net effect**: Only two auth paths remain:
- Gateway + per-user token (45 users in registries)
- AAD auth via `az login` (12 identified users)
- All shared/anonymous access eliminated

## Access Revocation — Jul 1, 2026 (Exempt=N cleanup)

**Trigger**: Jun 2026 active user audit (`user-config/Claude_Code_Active_User_Audit_Jun2026.xlsx`). All users with Exempt=N removed from all FLK-ai-enablement-node SGs + direct Foundry User RBAC on `flk-team-ai-enablement-ai`.

**What was removed:**
- 34 SG memberships across 31 unique users (nodes 1–4)
- 22 direct `Foundry User` (and 1 `Owner`) assignments on `flk-team-ai-enablement-ai` resource — these existed in parallel to SG access and were also revoked
- QA: all 4 SGs confirmed clean; AI resource confirmed 0 target user assignments remaining

**Unrelated RBAC left intact (confirmed by user):**
- Richard Feng: subscription-level Owner + Foundry User (sub scope) — legitimate subscription owner
- Arpan Saha: Owner on `flk-oracle-code-to-business-insight-dev` — unrelated RG
- Kathleen Wang: Azure AI Developer + Reader on `flk-rfeng-sandbox-westus-rg` — Richard Feng's sandbox

**Post-revocation SG membership (remaining users):**
- node-1: Taashi Manyanga *(admin only — effectively empty for end-users)*
- node-2: Taashi Manyanga, JD Giles, Matt Markl
- node-3: Taashi Manyanga, Steven Moore, Ryan Bryson, Adelaide Hartmann, Kendra Zimdars, Vineet Thuvara, Treg Vanden Berg
- node-4: Taashi Manyanga, Steven Moore, Vineet Thuvara

**Eshwari Mulpuru org — 9 of the 31 removed users report to her (direct or skip-level):**
| User | Level | Chain |
|------|-------|-------|
| Sanjay Kalra | L1 direct | → Eshwari |
| Josh Ciaramitaro | L1 direct | → Eshwari |
| Kranthi Kothapally | L1 direct | → Eshwari |
| Richard Feng | L1 direct | → Eshwari |
| Kevin Davison | L2 skip | → Todd Tomlinson → Eshwari |
| Sean Sparks | L2 skip | → Todd Tomlinson → Eshwari |
| Kathleen Wang | L2 skip | → Richard Feng → Eshwari |
| Arpan Saha | L3 skip | → Schendel → Mutton → Eshwari |
| Deep Katyal | L3 skip | → Schendel → Mutton → Eshwari |

**Deliverable**: `requests/IT users from CLI to Enterprise/Eshwari_Org_Removed_Users.xlsx` — 9-user table, status colour-coded (green=ACTIVE, amber=UNREGISTERED), manager chain column, summary stats block.

**Re-add process**: Submit ServiceNow RITM → Eshwari approves (her org users route through her) → add to relevant SG + restore Foundry User RBAC on AI resource.

## Active User Audit — Jun 15–29, 2026 (run 2026-06-29)

**Script**: `Usage Tracking/validate_active_users.py` (re-runnable: `python validate_active_users.py <storage_key>`)
**Excel output**: `user-config/Claude_Code_Active_User_Audit_Jun2026.xlsx` (39 rows, 10 cols, color-coded by status)
**Sources**: `diagnostic_user_activity` (AAD) + `per_user_usage` (Gateway) — Gold Delta tables on `flkaienablement`

| Status | Count | Notes |
|--------|-------|-------|
| ACTIVE | 13/28 registered | node2+3 dominant; node1 mostly dormant |
| DORMANT | 15/28 registered | All 8 node4 L1 Excel users + 4 of 5 node1 users |
| UNREGISTERED active | 11 | Active in data but not in registry — need RITM reconciliation |

**Active registered users (by node):**
- node1: Kevin Davison (1,627 reqs, 106.8M tok, $227)
- node2: JD Giles (746 reqs, 134.6M tok, **$1,178** — monitor), Jim Moeller, Julian Knabe, Matt Markl, Peter Bergstrom (near-dormant: 3 reqs), Richard Feng, Sanjay Kalra (API-key only, elevated cost/token ratio)
- node3: Daniel Pouley, Sean Sparks, Steven Moore (1,079 reqs — most active), Taashi Manyanga, Vineet Thuvara (near-dormant: 3 reqs)

**Dormant registered:** node1: Eshwari, Mihai, Rachel, Urvin. node2: Alex Chillman, John Erickson. node3: Azra Jabeen. node4 (all): Parker Burke, Jay Hack, Claire Hu Weber, Kathya Kalinine, Katie Marquardt, Neal Nowick, Sue-Ann Prentice, Kathryn Sweers.
- **node4 caveat**: L1 Excel users auth via API key — no email in usage blobs → invisible to audit. May be active.

**11 unregistered active users (in data, not in CLAUDE.md registry):**
evan.nebeker (1,844 reqs), treg.vandenberg (1,157), josh.ciaramitaro (431), elizaveta.petrenko (375), arpan.saha (293), kranthi.kothapally (226), kathleen.wang (192), deep.katyal (143), kendra.zimdars (142), adelaide.hartmann (47), lloyd.hung (23). All match users known to be on node2/3 — they were added in later waves not yet reflected in CLAUDE.md registry. Reconcile against ServiceNow RITM tracker.

**Key action items:**
1. Reconcile 11 unregistered users against RITM license tracker and add to registry.
2. Investigate JD Giles $1,178/14d — confirm intentional (long-context agent work) vs runaway.
3. Reach out to dormant node1 cohort (4 users) — possible setup issue shared across node1.
4. Contact node4 users directly to confirm actual usage status (API key auth gap).

## Documents
DeploymentPlan, EnterpriseArchitect, EndUserConfigGuide, per-node credential emails, per-user token migration emails, credential rotation broadcast (v1+v2 HTML), Excel Quick Start Guide v3 (all DOCX+HTML). Memory: `CLAUDE.md` in deployment dir.
