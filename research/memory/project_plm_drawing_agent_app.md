---
name: project-plm-drawing-agent-app
description: "PLM Drawing Agent — Build 4 FINAL (20,345 nodes, 820 drawings, filename-based IDs), 17 tools, Gradio UI, GitHub synced (fcdae9b main, docs/ added), live at flk-plm-drawing-agent.azurewebsites.net (2026-06-16)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 44d5fe90-7fa0-4075-b543-76e38e1574b4
---

## PLM Drawing Agent — Gradio Web App

**URL**: https://flk-plm-drawing-agent.azurewebsites.net
**Resource Group**: `flk-taashi-ai-sandbox`
**Runtime**: Python 3.12, Gradio 6.15, GPT-5.5 + Neo4j Graph-RAG
**Source**: `<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack\`
**Git repo**: `PLM-AI-Drawing-tool` (sanitized copy)

### Architecture
- `foundry_agent.py` — Gradio ChatInterface, GPT-5.5 via Azure AI Foundry, agent loop with tool-calling
- `query_graph.py` — 17 Neo4j tools (13 original + 4 BoM: find_components_by_spec, get_assembly_breakdown, find_common_components, get_component_specs)
- `audit_logger.py` — NDJSON audit logs → local file + Azure Blob (`plmsandbox/logs/YYYY/MM/DD/`)
- `startup.sh` — `python foundry_agent.py --serve`
- Neo4j Aura instance: `e23c24ac.databases.neo4j.io` (20,370 nodes, 31,268 rels, 7,348 enriched with parsed specs)

### Deployment Gotchas (2026-06-03)

1. **Oryx build timeout**: Gradio has massive dependencies (~298MB). The default 10-minute Oryx build limit on Azure App Service is not enough. Successful deployments use the pip cache from prior builds. If cache is cold (new instance), the build will time out (status=3).
   **How to apply**: For fresh deployments, do a source-only zip deploy with `SCM_DO_BUILD_DURING_DEPLOYMENT=true` and `--async true`. The CLI may timeout but the build continues server-side — poll via ARM API until `status=4`.

2. **Container startup timeout (230s default)**: `DefaultAzureCredential` + AIProjectClient creation at module import time blocks the Gradio server from binding its port. Azure's warmup probe gives up at 230s.
   **Fix applied**: Lazy-init the AI client (only created on first request). Also set `WEBSITES_CONTAINER_START_TIME_LIMIT=600`.

3. **Neo4j Aura Free tier pauses**: After ~72 hours of inactivity, Aura pauses the instance. The cached Neo4j driver holds dead connections.
   **Fix applied**: `get_driver()` now calls `verify_connectivity()` before returning, and auto-recreates the driver with 3 retries + exponential backoff.

4. **Azure token caching without TTL**: Tokens expire after ~1 hour but were cached forever.
   **Fix applied**: 45-minute TTL (`TOKEN_TTL_SECONDS=2700`), auto-refresh on 401.

5. **No concurrency control**: Multiple simultaneous users exhaust Neo4j connections and GPT-5.5 rate limits.
   **Fix applied**: `MAX_CONCURRENT_CHATS=10`, threading semaphore + Gradio `concurrency_limit`, GPT-5.5 retry with exponential backoff on 429.

6. **`az webapp deploy` 504 on large zips**: The 67MB pre-built zip triggers a 504 GatewayTimeout on the SCM upload endpoint.
   **How to apply**: Don't deploy pre-built packages via `az webapp deploy`. Use source-only zip (19KB) + remote build instead.

7. **Always-On**: Set to `true` to avoid cold starts for users. Without it, first request after idle takes 60-90s.

### App Settings
- `AZURE_AI_ENDPOINT`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PWD`, `NEO4J_DB`
- `WEBSITES_PORT=8000`, `SCM_DO_BUILD_DURING_DEPLOYMENT=true`
- `WEBSITES_CONTAINER_START_TIME_LIMIT=600`, `alwaysOn=true`

### Deploy Runbook (copy-paste ready)

**Pre-req**: `SCM_DO_BUILD_DURING_DEPLOYMENT=true` in App Settings (already set).

```bash
# Step 1 — Build the source-only zip (from Heather stack dir)
cd "<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack"
python -c "
import zipfile, os
files = ['query_graph.py','foundry_agent.py','audit_logger.py','plm_agent.py','startup.sh','requirements.txt']
with zipfile.ZipFile('deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
    for f in files: zf.write(f)
print(f'deploy.zip: {os.path.getsize(\"deploy.zip\"):,} bytes')
"

# Step 2 — Deploy (use --async true — CLI WILL timeout, that's expected)
az webapp deploy --name flk-plm-drawing-agent --resource-group flk-taashi-ai-sandbox \
  --src-path "<USER_HOME>/OneDrive - <ORG>/AI/Technical Validation/Heather stack/deploy.zip" \
  --type zip --async true

# Step 3 — Poll until build completes (~7-10 min, pip cache speeds repeat builds)
# status=1 → building, status=4 → success, status=3 → failed
SUB=$(az account show --query id -o tsv)
az rest --method get \
  --url "https://management.azure.com/subscriptions/$SUB/resourceGroups/flk-taashi-ai-sandbox/providers/Microsoft.Web/sites/flk-plm-drawing-agent/deployments?api-version=2022-03-01" \
  --query "value[0].{status:properties.status, complete:properties.complete}" -o table

# Step 4 — Restart to pick up new code
az webapp restart --name flk-plm-drawing-agent --resource-group flk-taashi-ai-sandbox

# Step 5 — Wait ~90s for cold start, then health check
curl -s -o /dev/null -w "HTTP %{http_code}\n" --max-time 120 \
  "https://flk-plm-drawing-agent.azurewebsites.net"
```

**Key facts**:
- Source-only zip is ~20KB. Do NOT deploy pre-built zips (>50MB) — SCM 504s.
- The `az webapp deploy` CLI will exit with error (timeout) — ignore it, build continues server-side.
- Poll step 3 every 20s until `status=4, complete=True`.
- If `status=3` (failed), check Oryx build log: `az webapp log download --name flk-plm-drawing-agent --resource-group flk-taashi-ai-sandbox --log-file logs.zip`
- Cold start takes ~60-90s after restart. `alwaysOn=true` prevents cold starts on user requests.

### Tunable Settings (env vars — change without redeploy via App Settings)
- `MAX_TOOL_ROUNDS` — max GPT-5.5 tool-calling rounds per query (default 5, was 8)
- `MAX_CONCURRENT_CHATS` — Gradio concurrency limit (default 10)
- `WEBSITES_CONTAINER_START_TIME_LIMIT` — container startup timeout (set to 600)

### Prompt Tuning (2026-06-03)

System prompt includes an EFFICIENCY section that prevents GPT-5.5 from exhaustive tool-calling:
- Pick the most targeted tool first; don't scatter-shot across indexes
- After 2-3 rounds without the data, say so clearly and stop searching
- Summarize what was found when tool budget is nearly exhausted
- **Forced summarization**: when all rounds are used, a final API call **without tools** forces the model to summarize rather than returning a generic fallback message

Before: "What voltage rating does the Fluke 179 have?" → 44.8s, 25 tool calls, generic fallback.
After: same query → 9.2s, 2 tool calls, real cited answer.

### RBAC (2026-06-03)

- Web App Managed Identity `cb4873b4-e7ac-4646-8c74-69b444b149bf` needs **Storage Blob Data Contributor** on `aisandbox02/plmsandbox` container for audit logging to work.
- Assigned via REST API (az role assignment create fails on this sub — see [[feedback-rbac-rest-api]]).
- Cognitive Services User role (cross-RG to `flk-team-ai-enablement-ai`) was already set in Phase 4.

### Performance Benchmarks (2026-06-03, 32 audit records)

| Metric | Value |
|--------|-------|
| P50 latency | 5.9s |
| P90 latency | 11.3s |
| Max latency | 17.1s (after prompt tuning) |
| Avg tool calls/query | 2.1 |
| 5 concurrent users | 14.1s wall time, 0 errors |
| Tool error rate | 0/51 calls (0%) |
| Audit records in blob | 32 (all ok, 0 errors) |

### BoM Enrichment Redeployment (2026-06-10)

Redeployed with 4 new BoM query tools and updated system prompts. Key changes:
- `query_graph.py`: 4 new functions + TOOL_DEFINITIONS + TOOL_DISPATCH (17 tools total)
- `foundry_agent.py`: Updated SYSTEM_PROMPT with BoM tool selection guide + component spec properties
- `plm_agent.py`: Same prompt updates for Claude agent
- `text-embedding-3-small` deployed on `flk-team-ai-enablement-ai` (120 TPM Standard) — was missing
- All endpoints now derived from `AZURE_AI_ENDPOINT` env var (no hardcoded URLs)
- E2E validated: 5/5 questions answered correctly on live Gradio

### Build 4 FINAL + Query Fixes + UI Tweaks (2026-06-12)

Build 4 graph: 20,345 nodes, 24,698 rels, 820 drawings, 100% embeddings, 0 orphans. Four builds total (B1: 9 failures + 89536, B2: crashed on list title, B3: clean 701 drawings, B4: filename-based IDs 820 drawings).

Key fixes applied:
- **Filename-based drawing IDs**: `{cid}_{pdf_stem}` so users see actual filenames. AI-extracted value in `extracted_drawing_number` (fulltext-indexed, returned in search results).
- **FSCM 89536 collision**: `_resolve_drawing_number()` with FSCM_BLACKLIST + barcode prefix detection + D-prefix preference. 21 merged → 0.
- `toLower(toString())` on all 24 Cypher property comparisons across 7 functions
- `WITH DISTINCT p, d` dedup in both `_PRODUCT_DRAWING_QUERY` and fuzzy fallback
- `r.quantity` from CONTAINS_COMPONENT relationship (was `p.quantity` → always null)
- `extracted_drawing_number` + `source_pdf_filename` added to vector_search, fulltext_search, smart_search returns
- `isinstance()` type guards on 6 extraction fields + `str()` wraps on all Neo4j properties
- Embedding circuit breaker (5 consecutive failures → skip)
- **Gradio UI**: height=690, max-width=95%, thin borders (#c0c0c0) on chatbot + input
- E2E: Build 4 133P/2W/0F (9 tests incl FN1 filename traceability). 12/12 live smoke tests PASS.
- GitHub: All branches merged to main at `fcdae9b` (2026-06-16). `docs/` folder with 6 deliverables. README updated for Phase 7+8 (820 drawings, 17 tools). 48 files tracked.

### BoM Quantity (USES Edges) Deployment (2026-06-19) — DEPLOYED & VALIDATED

Added per-FG component **quantities** from the Oracle BoM CSV (`BoM for the 50 items in scope with Qty.csv`, 22,042 rows, cp1252). New edge `Product-[:USES {assembly_id, quantity, ...}]->BOMComponent`, one per (FG, Assembly, Component) row — preserves the 79 multi-qty pairs losslessly.

- **Graph**: 1,142 USES edges, 15/50 FGs covered (match-only load — rest pending Phase 8 extraction), 703 components, 2,097.5 total units. `(:LoadEvent)` provenance node + SHA-256 on every edge. Latest LoadEvent `bom_uses_20260619_150757_ea9e768a`.
- **2 new tools** (#18/#19): `get_component_quantity`, `list_components_with_quantity`. Status enum: product_not_found / no_quantity_data_loaded / component_not_found_in_fg / ok_single_component / ok_multiple_components_aggregated. Fan-out `warning` + `was_truncated` (LIMIT 500). Deterministic `_resolve_product` (exact+prefix, no naked CONTAINS).
- **Agent redeployed** (2 deploys, both status=4): foundry_agent.py + plm_agent.py system prompts gained a CRITICAL QUANTITY RULE — never use get_bom_tree/get_bom_for_drawing/get_product_drawings for "how many" questions (they carry no per-FG quantity). Tool count 17→19.
- **Loader**: `load_uses_edges.py` (match-only, idempotent single-SET, quality gates before LoadEvent). `NEO4J_PWD` now env-only (hardcoded fallback removed — DLP).
- **Test bed**: `test_15_fgs_uses.py` (deterministic, 4 traversals: Top-Down/Bottom-Up/Middle-Out/CSV-Recon — **15/15 PASS, 0 qty mismatches vs CSV**) + `live_agent_15_fgs_uses.py` (**live agent 15/15 PASS**) + `compare_15fg_results.py` (**3-way 15/15 AGREE: CSV==graph==live agent**, incl. fractional qty 4.375). 28 unit/integration tests pass.
- **GitHub**: PR #9 merged to main (commit `13bcf48`) on local twin `PLM-AI-Drawing-tool`; dev reconciled to main. 10 files. Azure twin needs no change (cloud-extraction scope only). DLP scan clean. `_sanitize.py` gitignored (holds raw secret map).
- **Folder reorg (2026-06-19)**: Technical Validation root cleaned — new `PLM-Drawing-Tech-Validation/` container (documentation/{reports,plans,reviews}, deliverables, deliverables-scripts, tests). `Heather stack/` cleaned too BUT code stays FLAT (35 scripts `from query_graph import`, glob-matched `jason_extraction_*`, deploy zip + git mirrors all assume flat root). Only inert artifacts moved into `_legacy/`, `data/inert/`, `intermediates/`, `documentation/`. Map file: `Heather stack/FOLDER_MAP.md`. Integrity verified post-move: query_graph imports (19 tools), 28/28 tests, 15/15 FG bed PASS. `PLM Drawing Structured Data.xlsx` left at root (3 scripts hardcode it). Plaintext secret files (`AWS/*.txt`, `Neo4j/*.txt`) left in place — governance, not reorg.
- **3-persona review** (SA/EA/DE, 2 passes, all code P1/P2 fixed). Reports: `uses_review_*.md` + `_pass2.md`.
- **Backup**: `Bkps/20260619_144533_post_uses_load_pre_review.cypher` (33.6 MB, full graph).
- **Deployment report**: `DEPLOYMENT_REPORT_USES_2026-06-19.md` (Heather stack + deliverables).
- **Deferred governance** (non-code): CSV classification, Aura password rotation, backup restore-test.
- Re-run runbook: `python load_uses_edges.py --execute` (idempotent) after Phase 8 adds FGs.

### 15-FG Re-validation on PROD graph + LIVE app (2026-06-22)
Re-ran the full 3-leg USES/structure validation against the OFFICIAL prod Aura graph `e23c24ac`
(20,345 nodes) and the LIVE app `flk-plm-drawing-agent.azurewebsites.net` (HTTP 200). Run order +
results: **Leg 1** `test_15_fgs_uses.py` (deterministic graph vs CSV) = **15/15 PASS** all 4 traversals,
0 qty mismatches; **Leg 2** `live_agent_15_fgs_uses.py` (deployed GPT-5.5 app) = **15/15 PASS**; **Leg 3**
`compare_15fg_results.py` (3-way CSV==graph==live) = **15/15 AGREE** (incl. fractional TL175=4.375).
4 traversals per FG validate ALL THREE node types + directions, not just quantities: TOP_DOWN
(FG→Component→Drawing, counts drawings), BOTTOM_UP (Drawing/Component→FG, reaches target), MIDDLE_OUT
(assembly→up-to-FG + down-to-comps/drawings), CSV_RECON (quantities). Run order matters: Leg 1 writes the
anchors+expected-qty JSON that Legs 2/3 consume. Creds: NEO4J_PWD from `Neo4j/Neo4j-e23c24ac-Created-*.txt`
(env-only, DLP). Artifacts: test_15_fgs_uses_results.json, live_agent_15_fgs_uses_results.json,
uses_15fg_comparison.json + a results DOCX in PLM-Drawing-Tech-Validation/documentation/reports.

### Related
- [[project_plm_drawing_extraction]] — extraction pipeline that populates the Neo4j graph
- [[project_ubi_gold_graph]] — Neo4j knowledge graph context
- [[feedback_claude_code_env_override]] — running on AWS Bedrock this session
