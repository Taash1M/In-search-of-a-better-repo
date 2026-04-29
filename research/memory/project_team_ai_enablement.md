---
name: Team AI Enablement (Claude Code for Team)
description: Claude Code deployment for 34+ Fluke users across 5 nodes on Azure AI Foundry. SG-based onboarding, 5 LLM Gateways (hardened), AAD auth migration live (4 users flowing), ETL v3 with diagnostic logs, sync_aad_users.py pre-ETL step, 7-step runbook.
type: project
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---
## Deployment Directory
`C:\Users\tmanyang\OneDrive - Fortive\AI\Claude code deployment\`

## Azure AI Foundry
- **Resource**: `flk-team-ai-enablement-ai` (East US 2)
- **Subscription**: Fluke AI ML Technology (`77a0108c-5a42-42e7-8b7a-79367dbfc6a1`)
- **Resource group**: `flk-team-ai-enablement-rg`
- **Base URL**: `https://flk-team-ai-enablement-ai.services.ai.azure.com/anthropic`
- **Auth**: API key via `ANTHROPIC_FOUNDRY_API_KEY` + `CLAUDE_CODE_USE_FOUNDRY=1`
- **API key header**: `x-api-key` (not `api-key`)
- **Key discovery**: Foundry project required before Anthropic deployments; api-version=2025-12-01 required

## Models (15 deployments total)
- `claude-opus-4-6` (750 TPM, **Opus 4.7** since Apr 27), `claude-sonnet-4-6` (1,625 TPM), `claude-haiku-4-5` (100 TPM)
- 9 node-specific deployments for nodes 1-3 (3 per model family, 250cap each)
- 3 node-0 deployments (added 2026-04-23): `claude-opus-node-0` (Opus **4.7**), `claude-sonnet-node-0`, `claude-haiku-node-0` (250cap each)

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

## Users (29+ total, 25+ with Azure AI User RBAC on flk-team-ai-enablement-ai)
- node1 (5): Kevin Davison, Eshwari Mulpuru, Urvin Thakkar, Mihai Constantin-Pau, Rachel King
- node2 (10): Jd Giles, Richard Feng, Alex Chillman, Julian Knabe, Matt Markl, Jim Moeller, Peter Bergstrom, John Erickson, Sanjay Kalra (2026-04-22), Michael Johnston (2026-04-24)
- node3 (7): Vineet Thuvara, Steven Moore, Taashi Manyanga, Daniel Pouley, Azra Jabeen, Sean Sparks, Treg Vanden Berg (2026-04-28)
- **Eshwari batch (Apr 22/23)**: Kranthi Kothapally, Arpan Saha, Deep Katyal (added to existing nodes)
- node4 (12, L1 Excel): Parker Burke, Jay Hack, Claire Hu Weber, Kathya Kalinine, Katie Marquardt, Neal Nowick, Sue-Ann Prentice, Kathryn Sweers + Alex Chillman, Azra Jabeen, Steven Moore, Vineet Thuvara

### RBAC Audit (2026-04-22)
24 users hold Azure AI User role on `flk-team-ai-enablement-ai`. Added in 4 cohorts:
- **Mar 4** (10): Taashi, Kevin, Eshwari, Urvin, Mihai, JD, Richard, Alex C, Vineet, Steven
- **Mar 5** (+2): Daniel Pouley, Azra Jabeen
- **Mar 11** (+3 Finance): Julian Knabe, Rachel King, Matt Markl
- **Mar 23** (+1 IT): Sean Sparks
- **Apr 2** (+8 Executives): Parker Burke, Jay Hack, Kathryn Sweers, Sue-Ann Prentice, Katie Marquardt, Neal Nowick, Kathya Kalinine, Claire Hu Weber
- Jim Moeller, Peter Bergstrom, John Erickson (added Apr 7) — RBAC status needs verification
- **Apr 22** (+1): Sanjay Kalra (OID: fcfde7a6-41a7-404b-84c3-839abd5e437b, node2)

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

## Node-0 Test Gateway (2026-04-23)
- **Web App**: `flk-team-ai-llm-gateway-node-0`
- **URL**: `https://flk-team-ai-llm-gateway-node-0.azurewebsites.net`
- **Image**: `flkdockerregistry.azurecr.io/litellm-gateway-node0:v5`
- **Routes to**: node-0 model deployments (claude-opus-node-0, claude-sonnet-node-0, claude-haiku-node-0)
- **Purpose**: Dry-run testing gateway for security hardening before production rollout
- **Config**: `LLM Gateway/litellm-node0/config.yaml` + `Dockerfile`

## LLM Gateway Usage Tracking
See [project_llm_usage_tracking.md](project_llm_usage_tracking.md). DuckDB on VM (`llm-usage-duckdb-vm`, Standard_B2ms, ~$5.27/mo), 12h cron schedule. All 5 gateway nodes in `flkdockerregistry` ACR. 11 Delta tables including `gold/audit/user_activity` (deployed+validated 2026-04-23, 8 user groups, 37 cols). **Infrastructure health check added 2026-04-13** — 6 check categories, results to Delta, non-blocking step in ETL runbook.

## Infrastructure Health Check (2026-04-13, fixed 2026-04-22)
- Runs as Step 3/6 of `Invoke-LLMUsageETL` runbook (same 12h schedule)
- Checks: RG, AI Services, 12 model deployments, 25 RBAC users, 4 gateway web apps, Anthropic endpoint
- Delta table: `delta/metadata/health_checks/` (28 columns)
- Verdict: HEALTHY / DEGRADED / UNHEALTHY
- Current state: 12 deployments (4 Opus + 4 Sonnet + 3 Haiku nodes + 1 shared Sonnet), 25 Azure AI User assignments, all gateways Running
- **MI Permissions Bug (fixed 2026-04-22)**: Automation MI `flk-llm-etl-automation` lacked Reader on RG → 403s on all ARM checks → false UNHEALTHY verdicts. Fixed by assigning Reader on `flk-team-ai-enablement-rg`. Validated with manual runbook trigger → HEALTHY 6/6.

## Usage Metrics Snapshot (30-day, 2026-04-22)
- **Total**: ~24.4M tokens, ~19,729 requests across 12 deployments
- **By model**: Opus 61% (15M tokens), Sonnet 27% (6.5M), Haiku 12% (2.9M)
- **Heaviest node**: node3 (7.5M tokens, 6,278 requests) — 5 users including Taashi
- **Zero/near-zero usage**: sonnet-node2 (0), haiku-node2 (~2 requests) — candidates for cleanup
- **Shared deployments underused**: opus shared only 222K tokens; most traffic goes through dedicated nodes
- **PBI Report**: 5-page DirectLake report (v2). Page 4 "Infrastructure Health" (18 visuals, 6 HC measures). Page 5 "Usage & Health Insights" (15 visuals, 5 cross-table TREATAS measures — combo chart requests vs latency, bar chart by verdict, KPI cards, verdict explanation notes). README lists all 5 pages. Full_date slicers rebuilt (MMM-dd-yyyy, underlying=519). 21 total modelExtensions measures.
- **Correlation tracking**: `date_key` (YYYYMMDD) + `etl_run_id` (UUID) added to health_checks; `correlation_id` to job_runs. Backfill script deployed and run.

## Node 5 (UBI Subscription — 2026-04-17)
- **Subscription**: Fluke Unified BI (`52a1d076-bbbf-422a-9bf7-95d61247be4b`) — intentionally separate from nodes 1-4
- **Resource group**: `flkubi-prd-rg-001`
- **Resource**: `flkubi-claude-enablemen-resource`
- **Base URL**: `https://flkubi-claude-enablemen-resource.services.ai.azure.com/anthropic`
- **Models**: `claude-opus-node-5`, `claude-sonnet-node-5`, `claude-haiku-node-5` (+ 3 shared deployments)
- **Access**: Security group `flkazu-ubi-FlkBIprojects-iam-group@fluke.com` (group-based RBAC, not individual)
- **Settings**: `user-config/Flkubi/settings.json`
- **Docs**: `user-config/Flkubi/Node5_Claude_Enablement_Setup.docx` (7 sections)
- **SG config**: `user-config/SG config.txt` updated with node-5 entry

## Outlook Email Export (Claude Access Requests)
- **Dir**: `requests/` | **Output**: `requests/exported_pdfs/` + `_manifest.csv`
- **v1** (2026-04-17): `Export-ClaudeRequests.ps1` — PS1, Outlook COM → MHTML → Word COM PDF, searched all 78 subfolders, any "claude" mention
- **v2** (2026-04-19): `export_claude_requests_v2.py` + `run_export.bat` — Python, Outlook COM + Edge headless PDF, Inbox only, 2026 date filter, 17 regex access-request patterns

### v2 Architecture (the working method)
1. **Auth**: Outlook COM via `win32com.client.Dispatch("Outlook.Application")` — requires tmanyang session
2. **Search**: DASL filter on Inbox only: `subject/body LIKE '%claude%' AND datereceived >= 2026-01-01`
3. **Filter**: Secondary Python regex (17 patterns) for explicit access-request language (access, request, setup, enable, license, onboard, deploy, pilot, trial, etc.)
4. **Export**: `mail.HTMLBody` → styled HTML wrapper → Edge headless (`--headless --print-to-pdf`) → PDF
5. **Manifest**: CSV with Date, Sender, Email, Subject, MatchedPhrase, Status

### Cross-session execution trick (adm-tmanyang → tmanyang)
- **Problem**: COM can't cross Windows user sessions. Graph API blocked by Fortive tenant (AADSTS65002/AADSTS50105 for all tested client IDs: Office, Graph CLI, Azure CLI).
- **Solution**: `run_export.bat` wraps Python call with full path (`C:\Users\tmanyang\Python312\python.exe`). Launch via `explorer.exe "path\to\run_export.bat"` from admin session — Explorer runs as desktop user (tmanyang), so the .bat inherits tmanyang's session. Output redirected to `export_log.txt` for polling from admin session.
- **Python path**: tmanyang profile has `C:\Users\tmanyang\Python312\python.exe` (not on PATH for that user — must use full path in .bat)

### Run results (2026-04-19)
- 13,232 Inbox items → 130 DASL matches → 60 exported PDFs, 2 Edge timeouts, 47 filtered out (no access language)
- **False positives identified**: Microsoft PIM notifications (6), Outlook Reaction Digests (2), Teams notification emails (2), setup guide thread replies (~25), EOD status updates (4)
- **Genuine requests**: Bergstrom, Knabe, King (5 licenses), Moeller, Johnston, Erickson, Schultz, plus forwarded business cases from Mulpuru
- **Next run**: tighten filters to exclude system senders (microsoft.com, system-notification@fortive.com) and setup-guide-thread replies

## Deliverables (updated 2026-04-28)
Three documents built from the email export analysis:

### 1. Access Requests Summary (DOCX) — UPDATED DAILY
- **File**: `requests/Claude_Code_Access_Requests_Summary.docx`
- **Current state (2026-04-28)**: 16 requests (8 fulfilled / 17 seats, 8 pending / 17 seats)
- **Fulfilled**: Knabe(1), Bergstrom(1), Erickson(1), Moeller(5), Johnston(1), Kalra(1), Eshwari team(6: Kalra, Kothapally, Davison, Saha, Pouley, Katyal), Treg Vanden Berg(1)
- **Pending**: King(5), Cornely(1), Moore/Hartmann(1), Nebeker(1), Schultz(1), Bridges(6), Tomlinson/Sandeep(1), McNeal(1)
- **Routed to GitHub Copilot**: Andy Nguyen (from original Treg+Andy request)
- **Daily update workflow**: See [reference_access_request_workflow.md](reference_access_request_workflow.md)
- **Eshwari directive (Apr 22)**: All CLI requests must be routed through her for approval/cost justification

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
- **File**: `C:\Users\tmanyang\OneDrive - Fortive\AI\AI Advisory Committee\AI_Charter_Progress_Update_CLevel_April2026.docx`
- **Content**: Executive summary + 4 real use cases (JD Giles channel coverage, Vineet CRS docs, Steven competitive intel, Julian M&A models) + 7 strategic decisions table + governance + risk awareness ("dangerously powerful" CLI)
- **Sources**: Two AI Office Hours transcripts (Apr 10 + Apr 24) + AI Next Steps Plan PPTX
- **Use cases with metrics**: JD (3 days → 1.5 hours), Vineet (3 weeks → 30 min), Steven (18 competitors analyzed), Julian (3-4 hours → 30 min)

## Architecture Diagrams & Miro Board (2026-04-28)

### Miro Board
- **URL**: `https://miro.com/app/board/uXjVHajHEbE=/`
- **Content**: 15 native Miro diagrams + 5 Azure-icon PNGs + 5 D2-rendered SVGs

### Board Layout (native Miro flowcharts)
| Row | y | Content |
|-----|---|---------|
| Architecture (detailed) | -5000 | 5 detailed architecture flowcharts with clusters/boundaries, color-coded by service category |
| Architecture (simple) | 0 | 5 simplified architecture flowcharts |
| Data Flow | 3000 | 5 data flow diagrams |

Phases spaced 5000-5500 units apart on x-axis: Phase 1 CLI (x=0), Phase 2 Gateway (x=5500), Phase 3 ETL (x=11000), Phase 4 Security (x=16500), Infrastructure (x=22000)

### Azure-Icon Architecture PNGs (drag-drop to board)
Generated via `azure_diagrams.py` with real Microsoft Azure SVG icons:
- **Location**: `C:\Users\tmanyang\OneDrive - Fortive\AI\Miro\Claude Code Deployment\architecture\`
- `phase1_azure_arch.png` — 13 nodes: 3 user groups → CLI → Entra/RBAC → AI Foundry → 3 node deployments + shared pool
- `phase2_azure_arch.png` — 14 nodes: users → clients → 5 LiteLLM gateways → AI Foundry, container infra sidebar
- `phase3_azure_arch.png` — 15 nodes: 5 gateways → Blob → VM pipeline → Bronze → Silver → Gold star schema
- `phase4_azure_arch.png` — 12 nodes: 3 defense-in-depth layers (transport+identity, API hardening, key management)
- `infra_azure_landscape.png` — 15 services in grid layout (subscription → RG → all resources with SKUs/costs)
- **Generator**: `diagrams/generate_azure_arch_v2.py` (uses Node/Connection/Boundary/DiagramConfig API, standalone preset)

### D2 Data Flow Diagrams
- **Source**: `C:\Users\tmanyang\OneDrive - Fortive\AI\Miro\Claude Code Deployment\dataflow-d2\`
- **SVGs**: `C:\Users\tmanyang\OneDrive - Fortive\AI\Miro\Claude Code Deployment\dataflow-svg\`
- 5 diagrams: phase1_cli, phase2_gateway, phase3_etl, phase4_security, infra (each .d2 + .svg)
- D2 CLI v0.7.1 at `C:\Users\tmanyang\tools\d2\d2-v0.7.1\bin\d2.exe`
- D2 gotcha: `$` triggers variable substitution — use `52/mo` not `$52/mo`

## Documents
DeploymentPlan, EnterpriseArchitect, EndUserConfigGuide, per-node credential emails, Excel Quick Start Guide v3 (all DOCX). Memory: `CLAUDE.md` in deployment dir.
