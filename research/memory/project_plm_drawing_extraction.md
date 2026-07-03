---
name: plm-drawing-extraction-validation
description: "PLM drawing extraction — Phase 8: Build 4 FINAL (20,345 nodes, 820 drawings, filename-based IDs), 133P/2W/0F E2E, GitHub synced (fcdae9b main, docs/ added, README Phase 7+8), agent live. AWS BDA: 3 blueprints LIVE, 4 inference profiles tagged, Resource Group created, Bedrock settings active, comparison DOCX delivered (2026-06-19)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 5890f7d5-69bd-4e9b-95cb-12d890817d1c
---

## Overview

Technical validation of AI models for extracting structured metadata from PLM engineering drawings (Fluke).

**Why:** Validate whether AI vision/OCR extraction can replace manual metadata entry for PLM documents and determine which model best fits production needs.

**How to apply:** Use these findings when selecting models for PLM integration pipelines or document extraction at scale.

## Phase 1 — Claude Sonnet 4.6 Only (April 2026)

- **7 fields only** (drawing #, title, revision, type, scale, size, date)
- 18/19 PDFs processed in 3.6 minutes (21 MB file skipped)
- Title block: 89-100% accuracy, BOM: 80% accuracy
- Cost: ~$0.028/drawing

## Phase 2 — Comprehensive 3-Way Comparison (May 26, 2026)

Re-ran all three models with **25+ fields across 8 categories** (title block, personnel, revision history, BOM, materials/finishes, tolerances/dimensions, notes/compliance, electrical specs).

### Models Tested

| Model | API Pattern | Auth |
|-------|------------|------|
| Claude Sonnet 4.6 | Anthropic Messages API (vision — pymupdf→PNG→base64) | Azure AD (cognitiveservices audience) |
| Mistral Document AI 2505 | OCR API (`/providers/mistral/azure/ocr`) — native PDF base64 | Azure AD (cognitiveservices audience) |
| Mistral Document AI 2512 | OCR API (`/providers/mistral/azure/ocr`) — native PDF base64 | Azure AD (cognitiveservices audience) |

### Key Results

| Metric | Claude Sonnet 4.6 | Mistral 2505 | Mistral 2512 |
|--------|-------------------|--------------|--------------|
| Files processed | 18/19 | 18/19 | 17/19 |
| Total time | 1048s (17.5 min) | 192s (3.2 min) | 187s (3.1 min) |
| BOM items | 139 | 113 | 107 |
| Notes | 380 | 122 | 115 |
| Dimensions | 249 | 118 | 98 |
| Referenced docs | 135 | 8 | 7 |
| Compliance markings | 33 | 16 | 12 |
| Standards | 27 | 12 | 11 |
| Wins (depth) | 15/19 files | — | — |
| Speed advantage | — | 5.5x faster | 5.6x faster |

### Critical Learnings

1. **Mistral uses OCR API, NOT chat/completions** — `chatCompletion: false` capability flag; endpoint is `/providers/mistral/azure/ocr`
2. **Mistral request format**: `document` object with `type: "document_url"` + base64 data URL; structured extraction via `document_annotation_format` with `json_schema` (must include `name` field)
3. **Mistral supports native PDF base64** — no need for pymupdf→PNG conversion
4. **Mistral 30-page hard limit** — D2132850 (36 pages) fails with HTTP 400 on both Mistral models
5. **Mistral 2512 connection instability** — first file hit `RemoteDisconnected`, subsequent files OK
6. **Claude extracts 2-4x more information** per field category but takes 5.5x longer
7. **GlobalStandard SKU doesn't expose inference** — Mistral models need DataZoneStandard deployment

### Recommendation

- **Accuracy-critical workflows**: Claude Sonnet 4.6 (deeper extraction, 15/19 wins)
- **Speed/cost-sensitive batch**: Mistral 2505 (best balance of speed + completeness)
- **Production hybrid**: Mistral for first-pass OCR + Claude for validation on flagged items

## Output Location

`<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Document extraction - PLM Drawings\Image Model approach\`

### Deliverables

| File | Description |
|------|-------------|
| `extract_comprehensive_claude.py` | Claude extraction (25+ fields, Anthropic Messages API) |
| `extract_drawings_mistral.py` | Mistral extraction (25+ fields, OCR API, supports both 2505/2512) |
| `build_comprehensive_comparison.py` | 6-sheet Excel comparison builder |
| `gen_summary_docx.py` | Executive summary DOCX generator |
| `build_presentation.py` | 17-slide PPTX comparison builder (Fluke template, validated safe zones) |
| `build_infographic.py` | 3-page A4 landscape infographic builder (GPT Image 2 panels) |
| `build_results_excel.py` | 9-tab consultant-grade Excel results workbook |
| `claude_comprehensive_20260526_140351.json` | Claude raw results |
| `mistral_comprehensive_20260526_141538.json` | Mistral 2505 raw results |
| `mistral_comprehensive_20260526_143743.json` | Mistral 2512 raw results |
| `comprehensive_comparison_20260526_*.xlsx` | 6-sheet comparison workbook |
| `Mistral_vs_Claude_Comprehensive_Evaluation.docx` | Executive summary document |
| `PLM_Drawing_Extraction_Comparison.pptx` | 17-slide presentation (Fluke template) |
| `PLM_Drawing_Extraction_Infographic.docx` | 3-page A4 landscape infographic (GPT Image 2 panels + narrative) |
| `PLM_Extraction_Results_Detailed.xlsx` | 9-tab detailed results (Cover, Title Block, 3x BOM, Notes, Tech Detail, Analysis, Summary) |
| `panel_1_overview.png` / `panel_2_results.png` / `panel_3_recommendation.png` | GPT Image 2 infographic panels |

## Phase 3 — Heather Stack: Graph-RAG Agent (May 27, 2026)

Full extraction + Neo4j knowledge graph + Graph-RAG agent for 20 drawings from SCTASK1370482.

### Pipeline

1. **Extraction**: `extract_heather_claude.py` — Claude Sonnet 4.6 vision, 40+ fields, 3-way metadata enrichment
2. **Excel**: `build_heather_results_excel.py` — 11-tab workbook (443 BOM rows, 648 notes, 924 graph edges)
3. **Infographic**: `build_heather_infographic.py` — 3-page A4 landscape DOCX
4. **Neo4j Load**: `load_neo4j_graph.py` — 12-step loader, 1,007 nodes, 1,113 relationships, 10 node types
5. **Embeddings**: `generate_embeddings.py` — text-embedding-3-small (1536d), cosine vector index
6. **Query Engine**: `query_graph.py` — 12 tools (vector/fulltext/Cypher/BOM/BOM-tree/class-search/component-details/standards/materials/products/drawing-details/stats)
7. **Agent**: `foundry_agent.py` — GPT-5.5 function-calling agent on Azure Web App; `plm_agent.py` — Claude Sonnet 4.6 alternative with Gradio UI

### Neo4j Instance

- URI: `neo4j+s://e23c24ac.databases.neo4j.io`
- Database: `e23c24ac`
- 10 node types: Drawing(449), Part(267), Document(90), Dimension(68), Standard(35), Person(28), Item(24), Product(24), Revision(19), Material(3)
- 16 indexes: 9 uniqueness, 6 full-text, 1 vector (drawing_embeddings), 2 composite, 1 LOOKUP

### Key Issue: FSCM 89536 vs _doc_number

Claude extracted FSCM code `89536` (Fluke manufacturer code from title blocks) as `drawing_number` for 13/19 drawings. Fixed by using Oracle `_doc_number` (D-prefix folder name) as primary key everywhere. Critical `replace_all` applied in `load_neo4j_graph.py`.

### Documentation Deliverables (Updated 2026-05-30 with Phase 5 stats)

| File | Description |
|------|-------------|
| `PLM_GraphRAG_Architecture.docx` | Architecture & approach with 4 D2 diagrams, Phase 5 stats (20,360 nodes, 31,268 rels, 479 drawings, 12 tools) |
| `PLM_GraphRAG_Deployment_Guide.docx` | 14-section deployment guide with Phase 5 stats (11 node types, 22 rel types, 13-step loader) |
| `PLM_GraphRAG_Walkthrough.pptx` | 10-slide walkthrough with 12 tool cards, updated graph schema, Phase 5 stats |
| `Heather_Extraction_Infographic.docx` | 3-page A4 landscape infographic for 20-drawing Heather set |
| `Heather_Extraction_Results_Detailed.xlsx` | 11-tab results workbook for Heather extraction (443 BOM, 648 notes) |
| `Jason_BOM_Extraction_Infographic.docx` | 3-page A4 landscape infographic for 458-drawing Jason BOM dump |
| `Jason_BOM_Extraction_Results_Detailed.xlsx` | 11-tab results workbook for Jason BOM dump (1,294 BOM, 13,146 notes, 11,219 tech, 5,513 edges) |

### Working Directory

`<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack\`

## Phase 4 — GPT-5.5 Agent + Azure Web App (May 28, 2026)

Deployed the PLM agent as a publicly accessible Azure Web App using GPT-5.5 via the OpenAI Chat Completions API with function-calling tools.

### Architecture

- **Reasoning engine**: GPT-5.5 (`gpt-5.5` GlobalStandard, 5000 capacity on `flk-team-ai-enablement-ai`)
- **API pattern**: OpenAI Chat Completions with tool calling (Assistants API not available on this resource)
- **System prompt**: Optimized ~350 tokens (vs Claude's ~680) — includes graph schema, tool selection guide, 5 rules
- **Script**: `foundry_agent.py` — uses `azure-ai-projects` SDK v2.1.0, `AIProjectClient.get_openai_client()` with `DefaultAzureCredential`
- **Web UI**: Gradio `ChatInterface` with 5 sample questions, served on `0.0.0.0:$PORT`
- **Tool dispatch**: Reuses `query_graph.py` as-is — `TOOL_DEFINITIONS` converted from Anthropic to OpenAI format at startup

### Azure Resources (sandbox RG: `flk-taashi-ai-sandbox`)

| Resource | Name | Details |
|----------|------|---------|
| App Service Plan | `plm-agent-plan` | B1 Linux, East US 2 |
| Web App | `flk-plm-drawing-agent` | Python 3.12, Managed Identity enabled |
| MI Role | Cognitive Services User | Cross-RG to `flk-team-ai-enablement-ai` |
| Storage | `aisandbox02` / `plmsandbox` | Medallion data lake (bronze/silver/gold) |

### Medallion Storage (`aisandbox02/plmsandbox/`)

- `bronze/pdfs/` — 20 raw PLM drawing PDFs (D-prefix naming)
- `bronze/extractions/` — Raw Claude extraction JSON + XLSX
- `gold/graph_ready/` — Graph-ready extraction JSON

### Live URL

`https://flk-plm-drawing-agent.azurewebsites.net`

### Key Learnings

1. **Assistants API (beta) not available** on Azure AI Foundry `services.ai.azure.com` endpoint — returned 404. Switched to Chat Completions with tool calling.
2. **GPT-5.5 requires `max_completion_tokens`** (not `max_tokens`) — parameter was deprecated.
3. **`azure-ai-projects` v2.1.0**: `AIProjectClient.get_openai_client()` returns standard `openai.OpenAI` client with `base_url={endpoint}/openai/v1/` and AAD bearer token.
4. **Gradio theme parameter** moved to `launch()` in v6 — warning only, still works.
5. **RBAC propagation delay**: Storage Blob Data Contributor assignment took several minutes to propagate; used `az storage` CLI with account key for initial uploads.

### Documentation Deliverables (Updated 2026-05-28)

All three documentation build scripts updated to include Phase 4 (GPT-5.5, Azure Web App, medallion storage, MI auth):

| File | Build Script | Key Updates |
|------|-------------|-------------|
| `PLM_GraphRAG_Architecture.docx` (1,401 KB) | `build_architecture_docx.py` | New Section 10 (Frontend Deployment), 5-tier architecture diagram, GPT-5.5 in all agent references, medallion storage, MI auth flow |
| `PLM_GraphRAG_Deployment_Guide.docx` (45 KB) | `build_deployment_docx.py` | New sections 3 (Azure Web App) + 4 (Medallion Storage), GPT-5.5 model/endpoint, app settings table, MI config, 14 sections (was 12) |
| `PLM_GraphRAG_Walkthrough.pptx` (374 KB) | `build_walkthrough_pptx.py` | Live URL as primary "How to Use", GPT-5.5 in architecture diagram + tool explanation, updated Next Steps (removed completed items) |

### Phase 4.1 — Performance Fixes (May 29, 2026)

Two UX issues fixed and redeployed:

**Fix 1: Conversation chaining** — Gradio history was accepted but discarded (`chat_fn` ignored `history` param). Wired 10-turn text-only history (no tool replay) into `agent_loop()` for both `foundry_agent.py` (OpenAI format) and `plm_agent.py` (Anthropic format). Users can now ask follow-ups like "what about its BOM?" and the agent resolves references.

**Fix 2: Consolidated Cypher** — `get_drawing_details()` ran 8 sequential Neo4j queries (one per relationship type). Replaced with single query using `CALL (d) {}` subqueries. Result: **64ms avg** (down from ~800-1600ms estimated). Also fixed Neo4j deprecation warning (`CALL { WITH d ...}` → `CALL (d) {...}`).

Pre-fix code archived in `Heather stack/archive/*.pre-fix1-fix2`.

## Phase 5 — Jason BOM Data Ingest (May 29-30, 2026) — COMPLETE

Ingesting Jason's 29-May full BOM hierarchy extract: 50 parent Fluke products, 31,708 BOM rows (13 levels), 8,084 unique components, 458 DiagramsDrawings to extract via Claude.

### Data Profile

| Metric | Value |
|--------|-------|
| Parent products (Level 0) | 50 |
| Total BOM rows | 31,708 |
| BOM depth | Up to 13 levels |
| Unique components | 8,084 |
| DiagramsDrawings components | 458 (1,782 PDFs) |
| BOM edges (unique parent→child) | 14,706 |

### Pipeline Scripts

| Step | Script | Status |
|------|--------|--------|
| 1. BOM metadata | `load_bom_metadata.py` | COMPLETE — 8.7 MB JSON, 100% product metadata coverage |
| 2. Claude extraction | `extract_jason_drawings.py` | COMPLETE — 458/458 (100%), 3 retry passes, max_tokens bumped 16K→64K |
| 3. Neo4j load | `load_jason_graph.py` | COMPLETE — 20,360 nodes, 31,268 relationships, all 458 drawings + embeddings loaded |
| 4. Query tools + agent | `query_graph.py`, `foundry_agent.py`, `plm_agent.py` | LIVE — agent at flk-plm-drawing-agent.azurewebsites.net, E2E validated |
| 5. GitHub repo (local) | `PLM-AI-Drawing-tool` | LIVE — 19 files, sanitized (23 rules), PR #1/#2/#3 merged |
| 6. GitHub repo (cloud) | `PLM-AI-Drawing-tool-Azure` | LIVE — 18 files (3,010 lines), sanitized (24 rules), PR #1/#2 merged to main |

### Graph Model Changes

New node types:
- `BOMComponent` (8,084) — Oracle BOM components, uniqueness on `item_number`
- Product nodes enriched with `item_number` (Product Item No) — primary user search key

New relationships:
- `Product -[HAS_DRAWING]-> Drawing` — direct link for fast Product Item No lookup
- `Product -[HAS_BOM_ROOT]-> BOMComponent` — product to its level-0 BOM root
- `BOMComponent -[BOM_CONTAINS]-> BOMComponent` — 14,706 parent→child BOM hierarchy edges
- `BOMComponent -[HAS_DRAWING]-> Drawing` — component to its engineering drawing

New indexes:
- `bom_component_text` — full-text on item_number, description, class
- `product_text` — full-text on item_number, model, division, family, market_model
- `bom_class_idx`, `bom_root_parent_idx`, `product_item_idx` — composite/range

### Key Design Decisions

1. **Product MERGE on model (not item_number)**: 24/24 existing Product nodes overlap with new 50. MERGE on model preserves existing nodes + relationships, then adds item_number.
2. **Product Item No not in drawing content**: Oracle system IDs only linked through BOM hierarchy, not extracted from drawings.
3. **Vector embeddings enriched**: Product model, item number, and division added to embedding text for semantic search.
4. **Existing 20 Heather drawings backfilled**: product_item_numbers, product_models, Product→Drawing edges, re-embedded with product context.

### GitHub Repos

**Local twin** — `Taashi-Manyanga_fortive/PLM-AI-Drawing-tool` (private)
- For small jobs (<50 extractions), runs on laptop
- 23 files, 13 commits on main (PR #1-#6 + E2E audit fixes + build script sync)
- 770-line README with 5 Mermaid diagrams, E2E validated stats (20,360 nodes / 31,268 rels)
- max_tokens: 65536 in all 3 extraction scripts (extract_jason_drawings, extract_heather_claude, retry_d2139828)
- 7 build scripts (5 Heather + 2 Jason) synced from Heather stack with sanitization

**Cloud twin** — `Taashi-Manyanga_fortive/PLM-AI-Drawing-tool-Azure` (private)
- For bulk jobs (100+ drawings), runs unattended on Azure VM
- 18 files, 6 commits on main (initial + PRs + max_tokens + credential fix)
- max_tokens: 65536 in extract_drawings_cloud.py
- Blob storage I/O, MI auth, auto-deploy from `_scripts/` prefix, checkpoint/resume
- `check_progress.py` monitors from laptop (no SSH needed)
- Infra scripts: `setup_vm.sh` (VM+MI+RBAC), `setup_storage.sh` (deploy scripts), `teardown_vm.sh` (deallocate)
- VM cost: ~$0.50/run (B2s), Claude API is dominant cost (~$69/run)
- 357-line README with 4 Mermaid diagrams (architecture, data flow, graph schema, orchestration sequence)

**Documentation build scripts** (source of truth in Heather stack; sanitized copies in PLM-AI-Drawing-tool repo):
- `build_architecture_docx.py` — Architecture & approach DOCX with 4 D2 diagrams (updated Phase 5 stats)
- `build_deployment_docx.py` — 14-section deployment guide DOCX (updated Phase 5 stats)
- `build_walkthrough_pptx.py` — 10-slide walkthrough PPTX, 12 tool cards, updated graph schema (updated Phase 5 stats)
- `build_heather_infographic.py` — 3-page A4 landscape DOCX for 20-drawing Heather extraction
- `build_heather_results_excel.py` — 11-tab results workbook for Heather extraction
- `build_jason_infographic.py` — 3-page A4 landscape DOCX for 458-drawing Jason BOM dump
- `build_jason_results_excel.py` — 11-tab results workbook for Jason BOM dump (1,294 BOM + 13,146 notes + 11,219 technical + 5,513 edges)
- All 7 scripts updated/created 2026-05-30 with Phase 5 final stats

**Shared conventions**:
- Branch strategy: main ← dev ← feature/* (PR workflow)
- Sanitization: 23-24 regex rules via `sanitize_for_repo.py`, matching `repo-sync.py` standard
- Secret scanner hook blocks credentials; all env vars use `os.environ.get("...", "")  # placeholder`

### Extraction Results (FINAL — 2026-05-30)

- **458/458 completed** (100%) in ~10.5 hrs total, ~$69 Claude API cost
- 827 pages processed, 1,294 BOM items, 5,042 notes, 4,973 dimensions, 4,756 cross-references
- Avg 79s/drawing, 1.8 pages/drawing, 2.8 BOM items/drawing, 11.0 notes/drawing
- Drawing types: Part Drawing (241), Assembly Drawing (114), Fabrication Drawing (57), Exploded View (23), PCB Layout (14), Specification (4), Datasheet (3), Wiring Diagram (1), Schematic (1)
- 22 initial failures → retried → 5 persistent JSON truncation at 16K max_tokens → bumped to 64K → 3 recovered → last 2 were transient network errors → retried → all passed
- max_tokens gotcha saved as feedback memory [[claude-max-tokens-truncation]]

### E2E Validation (2026-05-30) — ALL PASS

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Jason drawings in graph | 458 | 458 | PASS |
| Products | 50 | 50 | PASS |
| BOMComponents | 8,084 | 8,084 | PASS |
| BOM_CONTAINS edges | 14,706 | 14,706 | PASS |
| Drawings with embeddings | 458 | 458 | PASS |
| Orphan drawings (no HAS_DRAWING) | 0 | 0 | PASS |
| Heather drawings (regression) | 2,824 | 2,824 | PASS |
| 5 retry drawings verified | 5 | 5 | PASS |
| Agent health | 200 | 200 | PASS |
| Missing PDFs | 0 | 0 | PASS |
| Queue IDs not in results | 0 | 0 | PASS |

### Current Graph State (FINAL — 2026-05-30)

- **20,360 nodes, 31,268 relationships** (was 10,667/17,819 — nearly doubled)
- BOMComponent (8,084), Dimension (5,014), Drawing (3,282), Document (1,260), Revision (828), Part (756), Standard (443), Person (402), Material (217), Product (50), Item (24)
- 23 indexes (9 uniqueness, 6 full-text, 1 vector, 2 composite, 2 LOOKUP, 3 range)
- Agent live at `flk-plm-drawing-agent.azurewebsites.net`

### E2E Validation Reference (paths, connections, field names)

**Working directory**: `<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack\`

**Bronze layer files**:
- `bom_metadata.json` — top-level keys: `generated_at`, `source_file`, `summary`, `product_metadata`, `parents`, `components`, `bom_edges`, `extraction_queue`
- Extraction queue item keys: `component_id`, `description`, `revision`, `pdf_paths`, `pdf_count`, `parent_products`
- PDFs at: `<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Jason data dump\29may_oracle_attachments\oracle_attachments\{component_id}\{revision}\*.pdf`

**Silver layer files**:
- Progress file: `extraction_progress.json` — top-level keys: `completed` (dict of component_id→metadata), `failed` (dict), `started_at`
- Results files: `jason_extraction_*.json` — top-level keys: `generated_at`, `source`, `summary`, `results`, `errors`
- **Extraction result field names** (NOT what you might guess):
  - `bom_items` (not `bill_of_materials`)
  - `general_notes` (not `notes`)
  - `title_block_info` (not `title_block`)
  - `key_dimensions` (not `dimensions`)
  - `cross_references` (dict with keys: `child_components`, `parent_assemblies`, `related_drawings`, `related_specifications`, `related_standards`)
  - `_component_id`, `_pages_sent`, `_pdf_count`, `_extraction_time_s`, `_revision`, `_description`, `_total_pages`
  - `drawing_number`, `drawing_title`, `drawing_type`, `extraction_confidence` (dict with text values like "high", not floats)

**Gold layer (Neo4j)**:
- URI: `neo4j+s://e23c24ac.databases.neo4j.io`, DB: `e23c24ac`
- Credentials in `load_jason_graph.py` as `os.environ.get()` with defaults
- **Source property**: Jason drawings use `d.source = 'jason_bom_29may'` (not `jason_bom`)
- Heather drawings have `d.source IS NULL`
- Drawing properties include: `drawing_number`, `title`, `drawing_type`, `source`, `embedding`, `bom_count`, `notes_count`, `dimensions_count`, `product_item_numbers`, `product_models`

**Agent endpoint**: `https://flk-plm-drawing-agent.azurewebsites.net/` (Gradio, returns 200 on GET)

### E2E Code/Doc Audit Fixes (2026-05-30)

| Fix | Severity | Files Changed |
|-----|----------|---------------|
| `query_graph.py`: `s.standard_id`→`s.identifier`, `m.material_id`→`m.name` | HIGH | Both repos |
| `sanitize_for_repo.py`: hardcoded Neo4j password → env var `NEO4J_PWD` | CRITICAL | Both repos |
| All docs: uniqueness constraints 8/11→9, full-text indexes 4→6 | MEDIUM | 3 build scripts |
| Architecture DOCX: "Claude's function-calling"→"GPT-5.5's function-calling" | LOW | build_architecture_docx.py |
| Deployment DOCX: max_tokens "16,384"→"65,536" | MEDIUM | build_deployment_docx.py |
| Walkthrough PPTX: constraint count 11→9, full-text 4→6 | MEDIUM | build_walkthrough_pptx.py |

Canonical graph stats: **9** uniqueness constraints (Dimension and Revision nodes lack them), **6** full-text indexes (drawing_text, part_text, document_text, standard_text, bom_component_text, product_text), **1** vector index, **12** retrieval tools.

### E2E Audit Session 3 Fixes (2026-05-31)

| Fix | Severity | Files Changed |
|-----|----------|---------------|
| Deployment DOCX: index table 11→9 constraints + 2 missing FT indexes added | MEDIUM | build_deployment_docx.py |
| Walkthrough PPTX: "4"→"6" search indexes in stats card + fulltext tool card | MEDIUM | build_walkthrough_pptx.py |
| All 7 build scripts synced from Heather stack to repo (copy+sanitize) | MEDIUM | 7 build scripts |
| 2 Jason build scripts added to repo (were missing) | LOW | build_jason_infographic.py, build_jason_results_excel.py |
| max_tokens 16K→64K in extract_heather_claude.py and retry_d2139828.py | MEDIUM | 2 Heather stack scripts |
| Memory: build scripts ARE in repo (was "not in repos"), tool count 9→12, agent GPT-5.5 | LOW | project memory |
| Deployment DOCX: plm_agent.py "Claude-powered"→"Claude alternative" | LOW | build_deployment_docx.py |
| Agent redeployed with fixed query_graph.py | HIGH | deploy.zip → Azure Web App |

### Round 2 UAT Results (2026-05-31)

39-question comprehensive UAT against live agent at `flk-plm-drawing-agent.azurewebsites.net`:

| Category | Questions | PASS | PARTIAL | FAIL | Avg Rating |
|----------|-----------|------|---------|------|------------|
| Round 1 Re-runs | 9 | 8 | 0 | 1 | 7.9 |
| Structured Queries | 16 | 14 | 2 | 0 | 8.1 |
| Edge Case / Vague | 14 | 9 | 4 | 1 | 6.6 |
| **Total** | **39** | **31 (79%)** | **6 (15%)** | **2 (5%)** | **7.5** |

**Improvements over Round 1** (avg was ~5.0):
- `find_drawings_by_standard` fixed: IPC returns 37, MIL returns 7 (was 0 in Round 1)
- `find_drawings_by_material` fixed: material name search now works
- Screw size accuracy improved (M2.2 correct, was M2)
- Round 1 re-run avg: 7.9/10 (up from ~5.0)

**3 remaining gaps**:
1. **Conversation chaining broken** — agent ignores passed chat history (FAIL, rating 2)
2. **No fuzzy matching** — "87V" doesn't resolve to "FLUKE-87-5" (FAIL, rating 3)
3. **Weak semantic ranking** — "thermal" returns label drawings, not thermal imager products (PARTIAL, rating 5)

Results in Excel: `ADHOC test results from round 1.xlsx` → "Round 2 (Post-Fix UAT)" tab.

### Round 3 Gap Fixes + Re-test (2026-05-31)

3 code fixes deployed to close Round 2 gaps:

| Fix | Files Changed | Approach |
|-----|---------------|----------|
| Conversation chaining | `foundry_agent.py` | `_normalize_history()` handles tuple+dict formats; 2 system prompt rules for anaphoric resolution |
| Fuzzy product matching | `query_graph.py` | `_normalize_product_query()` with Roman numeral mapping (87V→FLUKE-87-5); 3-step fallback cascade (CONTAINS→variants→Lucene fuzzy) |
| Semantic ranking | `query_graph.py` | `smart_search()` — hybrid vector+fulltext with Reciprocal Rank Fusion (k=60); registered as tool #13 |

SIT: 5 tests pass (3 unit + 2 integration). UAT re-test of 8 failed/partial questions + 3 bonus:

| Q# | Category | Was | Now | Notes |
|----|----------|-----|-----|-------|
| Q3 | Conversation chain | FAIL (2) | PASS | History passes correctly; GPT-5.5 acknowledges prior context |
| Q27 | Fuzzy "87V" | FAIL (3) | PASS | "87V maps to FLUKE-87-5", returns 15 drawings |
| Q-87V | Fuzzy voltage | timeout | PASS | Returns CAT III 1000V from D1102614 |
| Q21 | Thermal search | PARTIAL (5) | PASS | HEAT SINK ASSEMBLY ranked by smart_search |
| Q24 | Surface finish | PARTIAL (6) | PASS | 145 drawings with finish specs found |
| Q29 | Compare random | PARTIAL (6) | PASS | Comparison table generated |
| Q31 | "What's wrong" | PARTIAL (5) | PASS | Identifies FSCM 89536 mismatch |
| Q23 | PCB+connector | PARTIAL (7) | PARTIAL | Max tool rounds (complex multi-criteria) |
| Q34 | CSV export | PARTIAL (6) | PARTIAL | Response length limit hit |
| Q37 | Convo chain | — | PASS* | History passes but GPT-5.5 still asks for clarification |
| Q38 | Convo chain | — | PASS* | Same — model capability limitation |

*Q37/Q38 pass keyword checks but GPT-5.5 doesn't fully resolve "those drawings" from history — model limitation, not code bug.

**Result**: 9/11 PASS (81%). Both FAILs resolved. 4/6 PARTIALs improved to PASS.

**Deployment**: `deploy.zip` rebuilt and deployed to Azure Web App. Gradio 6.x does NOT support `type="messages"` on ChatInterface — removed (was causing startup crash). `_normalize_history` handles format conversion regardless.

**GitHub**: PR #7 merged → dev → main (commit `e919cf3`). Now 13 retrieval tools (was 12).

### Embedding Validation (2026-05-31)

Full validation of Neo4j vector embedding layer:

| Check | Expected | Actual | Status |
|-------|----------|--------|--------|
| Drawings with embedding | 3,282 | 3,282 | PASS |
| Drawings without embedding | 0 | 0 | PASS |
| Embedding dimension | 1,536 | 1,536 | PASS |
| Vector index status | ONLINE | ONLINE | PASS |
| Fulltext indexes (6) | ONLINE | All ONLINE | PASS |
| Semantic relevance gap | >0.1 | 0.229 | PASS |

Semantic quality tests:
- "thermal management" → HEAT SINK ASSEMBLY (score 0.677) — correct
- "voltage rating multimeter" → TRUE RMS MULTIMETER (score 0.734) — correct
- "insulation resistance tester" → INSULATION TESTER (RRF rank #1) — correct
- Irrelevant vs relevant score gap: 0.229 (0.615 vs 0.845) — good discrimination

Graph totals confirmed: 20,360 nodes / 31,268 rels across 11 node types / 22 relationship types.

### What Remains

- Cloud twin: provision VM, upload data, test extraction on VM
- Production graph migration (Aura → self-hosted)
- AAD EasyAuth for testers
- Neo4j password rotation (exposed in early git history)
- Read-only Neo4j user for agent connection (defense-in-depth)
- ~~Token TTL/refresh in query_graph.py embedding calls~~ → DONE (2026-06-03): 45-min TTL, auto-refresh on 401
- ~~Audit logging~~ → DONE (2026-06-03): NDJSON to `plmsandbox/logs/YYYY/MM/DD/`, MI RBAC set
- ~~Concurrency handling for 20 testers~~ → DONE (2026-06-03): 10-slot semaphore, Neo4j pool 15, GPT-5.5 retry
- ~~Prompt tuning for efficiency~~ → DONE (2026-06-03): MAX_TOOL_ROUNDS=5 (env var), EFFICIENCY prompt, forced summarization

### Round 3 Testing Email (drafted 2026-06-02, updated 2026-06-03)

HTML email to broader PLM team (20 testers) requesting another round of testing. Updated 2026-06-03 with correct stats and new improvements. 7 improvements highlighted: conversation memory, extraction accuracy, fuzzy product matching, smarter search, expanded dataset (3,282 drawings), reliability/concurrency, faster responses. Scope table: 50 FG products, 3,282 drawings, 8,084 BOM components, 20,360 nodes/31,268 rels, 13 tools. Deadline: Tuesday, June 10.

**File**: `<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack\plm_testing_email.html`

### Next Steps (Future)

1. **Round 3 UAT** — Email updated and ready to send (20 testers, deadline June 10). 7 improvements, 3,282 drawings scope.
2. **Production graph** — Evaluate migration from Aura SaaS to self-hosted Neo4j on Azure.
3. **AAD authentication** — Enable App Service EasyAuth for testers.
4. **Remaining perf fixes** — Streaming responses, embedding cache, MI for embedding auth.
5. **Security hardening** — Rotate Neo4j password, create read-only user, add token TTL.

## Phase 6 — System Infographics (June 7-8, 2026)

Created comprehensive 6-page landscape A4 infographic DOCX documenting the complete Graph-RAG architecture, data pipeline, and query flow.

### Deliverables

| File | Description |
|------|-------------|
| `PLM_GraphRAG_Infographic.docx` (941KB) | v1: matplotlib diagrams with Azure SVG icons (cairosvg), 3 diagram + 3 explainer pages |
| `PLM_GraphRAG_Infographic_v2.docx` (1.6MB) | v2: GPT Image 2 illustrated panels (3 images ~170s each), 3 diagram + 3 explainer pages |
| `generate_infographic.py` | v1 generator (matplotlib + cairosvg + real Azure SVG icons) |
| `generate_infographic_v2.py` | v2 generator (GPT Image 2 API via Azure AI Foundry) |
| `infographic_v2_architecture.png` | GPT Image 2 panel: system architecture |
| `infographic_v2_process_flow.png` | GPT Image 2 panel: 5-stage data pipeline |
| `infographic_v2_query_flow.png` | GPT Image 2 panel: query flow + 12 tools + reasoning loop |

### Page Structure (both versions)

1. **Architecture Diagram** — Oracle PLM → Azure Blob → VM → AI Foundry → Neo4j → Gradio
2. **Architecture Explainer** — 3-column table: Source & Storage | Compute & AI | Graph & Interface
3. **Process Flow Diagram** — 5 numbered stages: Ingest → Extract → Load → Embed → Serve
4. **Pipeline Walkthrough** — 3-column table: Ingest/Extract | Load/Embed | Serve details
5. **Query Flow Diagram** — Engineer → Agent → 12 Tools → Neo4j → multi-round reasoning loop
6. **User Guide** — Agent comparison (Claude vs GPT-5.5) + tips + example questions

### GPT Image 2 Config (v2)

- Endpoint: `https://codevsclaude46-resource.services.ai.azure.com`
- Model: `gpt-image-2`
- Size: 1536x1024 (landscape, high quality)
- ~170s per image generation
- Prompt length gotcha: long prompts cause 500 errors — keep under ~600 chars

## Phase 7 — BoM CSV Enrichment Pipeline (June 9, 2026)

E2E pipeline to ingest the official BoM CSV (22,054 rows, 50 products) and enrich the existing graph with parsed component specifications.

### New Scripts (in PLM-AI-Drawing-tool repo + Heather stack)

| Script | Lines | Purpose |
|--------|-------|---------|
| `profile_bom_csv.py` | 502 | CSV profiling, Neo4j reconciliation (≥90% gate), 36-query regression baseline, pre-enrichment snapshot |
| `parse_bom_descriptions.py` | 493 | Two-tier parser: regex (53%) + Claude Sonnet batch (47%), checkpoint/resume |
| `enrich_graph_bom.py` | 484 | Graph enrichment with BATCH_SIZE=200 UNWIND/MERGE, dry-run default, --sample smoke test |
| `test_bom_enrichment.py` | 400 | 31 TDD tests: CSV loading, regex parsing, entity profiling, assembly classification, tool registration, enrichment prep, JSON safety |

### New Query Tools (4, total now 17)

| Tool | Purpose |
|------|---------|
| `find_components_by_spec` | Search by component type + spec value (e.g., "0603 resistors in the 87V") |
| `get_assembly_breakdown` | Assembly-level product structure with child counts |
| `find_common_components` | Cross-product component reuse (collect+intersect, not Cartesian) |
| `get_component_specs` | Parsed electrical/mechanical specs with confidence level |

### Graph Schema Changes

- New BOMComponent properties: `component_type`, `spec_value`, `tolerance`, `power_rating`, `voltage_rating`, `current_rating`, `package_size`, `material`, `full_description`, `bom_csv_detail`, `bom_csv_parse_method`, `bom_csv_parse_confidence`, `bom_csv_enriched_at`, `bom_csv_source`, `description_variants`, `bom_path_count`
- Rebuilt fulltext index: `bom_component_text` now includes `full_description`, `component_type`, `spec_value`, `bom_csv_detail`
- New indexes: `bom_component_type_idx`, `bom_package_size_idx`
- `text-embedding-3-small` deployed on `flk-team-ai-enablement-ai` (120 TPM Standard) — was missing, caused vector_search/smart_search 404s

### Execution Results (2026-06-09/10)

| Phase | Result |
|-------|--------|
| Phase 1: Profile | 22,054 rows, 7,348 unique items, 99.9% match rate (PASS ≥90%), 36 baseline queries 0 errors |
| Phase 2: Parse | 7,348/7,348 (100%), 0 failures, regex 3,896 (53%) + Claude 3,452 (47%), 69 Claude batches |
| Phase 3: Enrich | 7,338 enriched + 10 new + 4,651 path counts + 3 indexes, 8.3s |
| Code Review | 3-persona review: 13 issues found + 2 SIT failures + 1 Cypher syntax + 1 embedding deploy = 17 fixes total |
| TDD Tests | 31/31 PASS |
| Regression | 36/36 queries PASS (0 regressions from enrichment) |
| E2E Agent Eval | 20/20 PASS (Claude), then 15/15 across all 3 agents |
| Deployment | Heather stack updated, deploy.zip rebuilt, Azure Web App redeployed |

### 3-Agent Validation (2026-06-10)

| Agent | Score | Notes |
|-------|-------|-------|
| Claude Sonnet (Local) | 5/5 | All 4 new tools used correctly, avg 22s/query |
| GPT-5.5 (Local) | 5/5 | All 4 new tools used correctly, avg 9s/query |
| GPT-5.5 (Live Gradio) | 5/5 | All 4 new tools used correctly, avg 18s/query |

### Design Decisions

1. **Enrichment overlay, not new data source**: BoM CSV overlaps heavily with existing BOMComponents. Value is in parsed description specs, not hierarchy.
2. **No quantity inference**: Flattened CSV doesn't reliably indicate quantity. `bom_path_count` used as reuse indicator instead.
3. **Data lineage**: All enriched properties tagged with `bom_csv_source`, `bom_csv_enriched_at`, `bom_csv_parse_method`, `bom_csv_parse_confidence`.
4. **Three-tier review**: Solution architect → enterprise architect → principal data engineer. 17 total fixes applied.
5. **Collect+intersect for common components**: Avoids Cartesian explosion of bidirectional `*1..13` traversals. Traversal depth capped at `*1..6`.
6. **Env var derivation for endpoints**: All scripts derive `EMBED_ENDPOINT` and `CLAUDE_ENDPOINT` from `AZURE_AI_ENDPOINT` env var — no hardcoded URLs in repo.

### GitHub

PR #8 merged to main (commit `ca67f8d`), 2,506 lines across 8 files. Post-merge fix `d265159` (agent endpoint derivation).

### GitHub Sync (2026-06-16)

All branches consolidated — `feature/multi-pdf-fix` → `dev` → `main` at commit `fcdae9b`:
- README.md: Updated for Phase 7+8 (820 drawings, 17 tools, 20,345 nodes, 24,698 rels). 8-section file inventory. Agent tool table expanded to 17 entries.
- `foundry_agent.py`: Gradio CSS fix (height=690, max-width=95%, borders)
- `.gitignore`: Added `!docs/**` exception
- `docs/` folder: 6 deliverable files (4.7 MB) — architecture DOCX, deployment guide, walkthrough PPTX, extraction tracker XLSX, 2 results workbooks
- 48 files tracked, all pushed to remote
- Azure twin (`PLM-AI-Drawing-tool-Azure`): commit `1f35e89` — timeout fixes, flushed output, `diagnose_vm.py` (150 lines), 20 files tracked

## Phase 8 — Bulk Supplemental Extraction (June 10, 2026) — IN PROGRESS

Extracting ALL remaining BOM component documents (not just DiagramsDrawings class).

### Scope

- **4,587 items** queued (was 4,599 — 12 skipped >20MB), 6,008 PDFs, 3.7 GB
- All BOM classes: Resistor(489), Capacitor(349), PlasticComponent(308), MetalFabricated(294), ElectricalConnector(222), Fastener(184), IC_*(500+), etc.
- Partitioned into 4 slices for parallel VM extraction

### Hybrid Extraction Approach

Replaced pure-vision with hybrid text+vision routing:
- PyMuPDF `page.get_text()` for text-heavy pages (>100 chars) — datasheets, specs
- Claude vision only for diagram pages (<100 chars text) — engineering drawings
- **Validated**: 72-page capacitor spec: hybrid 420 KB / 166s vs vision 9.1 MB / CRASHED
- **Data quality**: hybrid extracted MORE than native PDF (102 notes vs 77, 28 tolerances vs 14)
- Applied to both `extract_drawings_cloud.py` (cloud) and `extract_jason_drawings.py` (local)
- Cloud repo commit `ccf8933`

### Infrastructure

- **VM**: `plm-extract-vm-0` in `flk-taashi-ai-sandbox` (subscription `77a0108c-...`)
- **Resized**: B2s (4GB burstable) → **D2s_v5** (8GB dedicated CPU) — B2s throttled after burst credits
- **Storage**: `aisandbox02/plmsandbox` — metadata + PDFs + progress + results
- **RBAC**: MI has Storage Blob Data Contributor + Cognitive Services User (cross-RG to `flk-team-ai-enablement-ai`)

### Orchestration Wrapper

Two-tier architecture modeled on LLM Usage ETL pipeline:
- `orchestrate.sh` — laptop-side (8 steps: start VM → deploy → extract → retry → load → embed → validate → deallocate)
- `run_extraction.sh` — VM-side (auto-deploys from blob, flag parsing, sequential steps, status summary)
- Per-step status tracking, 10% failure gate, SIGINT trap, `--skip-deallocate` for debugging

### Status (2026-06-11)

- **752/4,587 extracted** (16.4%), **16/50 parent items DONE** (32%), 2 failed (bad source data)
- **Multi-PDF extraction COMPLETE for 15 DONE parents**: 843 results total (830 GOOD 98.5%, 12 LOW 1.4%, 0 EMPTY)
- **All file types handled**: PDF (hybrid text+vision), PPTX, DOCX, DOC, TXT, FRM/FM/FM5 (FrameMaker screenshot+vision), DWG (ODA+ezdxf), TIF (PIL+vision), ZIP (extract inner PDFs)
- **D2179860 ZIP**: 3 inner PDFs + 1 ZIP container metadata → 4 Drawing nodes, all linked to D2179860 component
- **4271987 FM5**: Was last EMPTY — re-extracted from FrameMaker screenshots (4 pages), now has drawing_number 37X-4R01T-K
- **FrameMaker ExtendScript**: `screenshot_4271987.jsx` — page navigation via `FirstBodyPageInDoc`/`PageNext` + `.pyw` silent screenshot capture (File > Script > Run Script)
- **Archive taken**: `neo4j_archive_v1_20260611_131834.json` (37.7 MB, 72,156 nodes, 100,529 rels)
- **Fresh graph Build 4 FINAL (2026-06-12)**: 20,345 nodes, 24,698 rels, 820 drawings (100% embeddings), 15 products, 827 components, 0 orphans
- **Filename-based drawing IDs**: drawing_number now uses `{cid}_{pdf_stem}` so users see actual filenames. AI-extracted value stored in `extracted_drawing_number` (fulltext-indexed). Both searchable.
- **Build 4 E2E**: 133P/2W/0F across 9 tests × 15 parents (added FN1 filename traceability test). 12/12 live smoke tests PASS.
- **1560856 = 4 drawings** confirmed across all rounds (tester-reported issue resolved)
- **4 builds total**: B1 (9 failures + 89536), B2 (crashed on list title), B3 (clean, 701 drawings), B4 (filename IDs, 820 drawings)
- **FSCM 89536 collision**: `_resolve_drawing_number()` with FSCM_BLACKLIST + barcode prefix detection + title_block_info fallback + D-prefix preference. 21 merged → 0.
- **Key code fixes (33+)**: isinstance() type guards, str() wraps, toLower(toString()) on 24 Cypher calls, WITH DISTINCT dedup, r.quantity, document_text removed, embedding circuit breaker, FSCM blacklist, filename-based drawing IDs, extracted_drawing_number in search results, startsWith check
- **test_all_15_parents.py**: Automated 9-test suite (TD1-4, BU1-2, MO1, VAL1, FN1) for all 15 parents. ~3 min. Results in `test_results/R2_*.json`
- **Gradio UI**: height=690, max-width=95%, thin borders on chatbot + input
- Agent live at `flk-plm-drawing-agent.azurewebsites.net`
- GitHub: All branches merged to main at `fcdae9b` (2026-06-16). README updated. `docs/` folder added with 6 deliverables.
- PLM Graph skill created (`plm-graph.md`) — 10 operations, decision tree, architecture reference
- Cost: ~$130 spent (extraction $112 + multi-PDF fix ~$18), ~$550 remaining

### Pipeline (automated)

1. Extract: `python extract_supplemental_local.py --parent X --concurrent`
2. Auto-load: Results pushed to Neo4j immediately after extraction (embedded in script)
3. Multi-PDF fix: `python fix_multi_pdf.py --extract --parent X --concurrent` then `--load`
4. Track: `python extraction_tracker.py --update` → Excel + CSV with parent_items column
5. Validate: E2E test per parent item (6 dimensions: drawings, BOM, assemblies, leaf+drawing, specs, search)

### Multi-PDF Fix Design

- **Problem**: 19% of components (866 items, 2,287 PDFs) have multiple Oracle attachments. Original pipeline merged all PDFs into 1 Drawing node — testers expected 1 node per document.
- **Fix**: Two-phase script (`fix_multi_pdf.py`):
  - Phase 1 `--extract`: Extract each PDF individually, save permanently to `multi_pdf_results/{component_id}_{filename}.json`
  - Phase 2 `--load`: Load all saved results into Neo4j (separate step, can retry independently)
- **Key design**: Results are NEVER deleted. Extraction and loading are decoupled. Failures in loading don't lose extraction work.
- **Scope**: 15 DONE parents first (~500 docs), then remaining parents as they complete
- **Cost**: ~$0.15 per individual PDF extraction

### Remaining

1. **Redeploy agent** with all query_graph.py fixes (deploy.zip → Azure Web App) — toLower, dedup, FSCM fixes
2. Fix `extract_supplemental_local.py` to not merge multi-PDF items going forward
3. Continue parent-item extraction (34 products remaining)
4. VM approach ready for future use (flush fixes committed to Azure repo `1f35e89`)
5. ~~Merge feature/multi-pdf-fix → main~~ DONE (2026-06-16, `fcdae9b`)
6. ~~Update README for Phase 7+8~~ DONE (2026-06-16)
7. ~~Add deliverable docs to repo~~ DONE (2026-06-16, `docs/` folder)

## BOM Quantity Gap (2026-06-16)

**Problem:** `BOM_CONTAINS` relationships have no `quantity` property. The Oracle BOM Excel file (`flkt28may2026_BOM_to_file.xlsx`) was loaded by `load_bom_metadata.py` reading columns 0-9 (level, parent, path, component, description, revision, class, docs) but the **quantity column was not extracted**. The CSV at `BoM\BoM for the 50 items in scope.csv` also lacks this field.

**Why:** Users asking "what components are in the Fluke 87V with quantities?" get the hierarchy but no per-parent quantity. The `CONTAINS_COMPONENT` relationship (Drawing→Part) does carry `quantity`, but only for parts listed on a drawing's BOM table — not the full Oracle BOM hierarchy.

**How to apply:** User will obtain an updated Oracle BOM file that includes the quantity column. When received:
1. Identify the quantity column index in the new file
2. Add column extraction in `load_bom_metadata.py` (around line 91-138)
3. Include `quantity` in the `bom_edges` dictionaries in `bom_metadata.json`
4. Set `r.quantity = row.quantity` on `BOM_CONTAINS` edges in `load_jason_graph.py` (around line 277-284) and `load_graph_cloud.py` (around line 241-248)
5. Rebuild graph and validate natural language queries return quantities

**Status:** RESOLVED (2026-06-19). Jason delivered `BoM for the 50 items in scope with Qty.csv` (with `Sum of Extended Quantity` column). Rather than retrofit `BOM_CONTAINS`, quantity was modeled as a new `Product-[:USES {assembly_id, quantity}]->BOMComponent` edge (per-FG, lossless on 79 multi-qty pairs). 1,142 edges loaded (15/50 FGs, match-only), 2 new agent tools, agent redeployed, 15/15 test bed PASS (0 qty mismatch vs CSV). See [[project-plm-drawing-agent-app]] "BoM Quantity (USES Edges) Deployment". Loader: `load_uses_edges.py`. Re-run after Phase 8 adds the remaining 35 FGs.

## MarkItDown Evaluation (2026-06-16)

Evaluated `microsoft/markitdown` (8.7/10, APPROVED) as potential alternative to current Claude Vision extraction pipeline. See [[project_skill_evaluation]] for full evaluation.

**Current method:** PDF → pymupdf render @ 150 DPI → PNG base64 → Claude Sonnet Vision API → JSON ($0.028/doc, 79s/doc)
**MarkItDown local:** PDF → pdfminer + pdfplumber → Markdown text/tables → Claude Text API → JSON (~$0.002/doc, ~10s/doc)
**MarkItDown + Azure CU:** PDF → Azure Content Understanding → structured Markdown + YAML fields → Claude Text API → JSON (~$0.015/doc, ~20s/doc)

Benchmarking skill created: `/markitdown-bench`.

### Benchmark Results — Product 5594650 (FLUKE-II905) — 2026-06-16

**Sample:** 18 documents (17 PDF + 1 DOCX) across 11 components. Output at `<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\MarkItDown\`.

| Metric | Claude Vision (Current) | MarkItDown Local |
|--------|------------------------|------------------|
| Total time (18 docs) | 771s (12.9 min) | 33s (0.5 min) — **24x faster** |
| Avg cost/doc | $0.048 | $0.009 — **5.5x cheaper** |
| Projected 820-doc cost | ~$39 | ~$7.80 — **80% savings** |

**Quality by document type:**
- 5 EXCELLENT (specs, datasheets, DOCX) — full text + tables preserved
- 3 GOOD (text-heavy PDFs) — meaningful text extracted
- 7 WEAK (engineering drawings) — only title block text, no visual content
- 3 FAIL (decals, press-ready PDF) — 0-421 chars, image-only content

**Key finding:** MarkItDown fails on image-only PDFs (returns 0 chars for press-ready QRG at 32 MB). Works excellently on text-based specs/datasheets.

**Recommended hybrid routing:**
- >= 2,000 chars → MarkItDown text only ($0.002)
- 500-2,000 chars → MarkItDown + selective vision ($0.010)
- < 500 chars → Full vision pipeline ($0.028)
- Projected cost with hybrid: $0.170 for this sample vs $0.861 all-vision (80% reduction)

**Artifacts:** `benchmark_results.json`, `benchmark_report.md`, `markitdown_samples/` (17 .md files)

**Next:** Field-by-field accuracy comparison (send MarkItDown output through same Claude prompt), test Azure CU on 3 FAIL docs, expand sample to 50+ docs.

## Related

- [[project_doc_extract]] — Unified doc-extract skill (ContextGem+RAG-Anything)
- [[project_graphify]] — Knowledge graph skill used in early drawing extraction experiments
- [[project_ubi_gold_graph]] — Neo4j knowledge graph from UBI Gold tables
- [[project_skill_evaluation]] — MarkItDown repo evaluation (8.7/10, APPROVED)
