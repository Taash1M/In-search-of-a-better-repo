---
name: plm-graph
description: >
  PLM Knowledge Graph operations — extract engineering drawings via Claude hybrid text+vision,
  load into Neo4j, validate per parent item, track progress, redeploy the Gradio agent, and
  improve extraction/loading code. Trigger on: 'PLM', 'drawing extraction', 'Neo4j graph',
  'parent item', 'BOM component', 'supplemental extraction', 'PLM agent', 'Heather stack',
  'graph-RAG', 'drawing agent', 'extraction tracker', 'PLM deploy', 'plm-graph'.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Task
---

# PLM Graph Operations Skill

You are an expert operator of the <ORG> PLM Knowledge Graph pipeline. This skill provides the
commands, conventions, validation protocols, and code improvement patterns needed to extract
engineering drawings, load them into Neo4j, validate the graph, and maintain the agent app.

## Access Control Rules (MANDATORY)

1. **NEVER write to Neo4j in production without user confirmation.** All write operations (load, enrich, delete) require explicit approval.
2. **NEVER commit credentials.** Neo4j password, Azure tokens, and API keys stay in env vars or are obtained via `az account get-access-token`.
3. **NEVER push to GitHub without running the secret scanner hook.** The repo-sync hook auto-sanitizes, but verify before any manual push.
4. **Extraction costs real money.** Always confirm before running large extraction batches (~$0.15/item, ~$650 for all remaining items).

## Task Decision Tree

```
What do you need?
├─ Extract drawings for a parent item     → S1: Extract New Parent Item
├─ Check extraction progress              → S2: Check Status
├─ Retry failed extractions               → S3: Retry Failures
├─ Manually load results to graph         → S4: Load to Graph
├─ Update tracker Excel/CSV               → S5: Update Tracker
├─ Validate a parent item E2E             → S6: Validate Parent Item
├─ Redeploy the Gradio agent app          → S7: Redeploy Agent
├─ Improve extraction/loading code        → S8: Code Improvements
├─ Query the graph (ad hoc)               → S9: Ad Hoc Queries
├─ Rebuild the parent queue               → S10: Rebuild Parent Queue
├─ Check graph statistics                 → S9: Ad Hoc Queries (use graph_statistics)
└─ Understand the architecture            → Architecture Reference (bottom of file)
```

## Working Directory

All commands run from:

```
<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack\
```

Always `cd` to this directory before running any pipeline script.

## Environment

| Resource | Value |
|----------|-------|
| **Neo4j URI** | `neo4j+s://e23c24ac.databases.neo4j.io` |
| **Neo4j DB** | `e23c24ac` |
| **Neo4j User** | `e23c24ac` |
| **Agent URL** | `https://flk-plm-drawing-agent.azurewebsites.net` |
| **Azure Subscription** | `77a0108c-...` |
| **Resource Group** | `flk-taashi-ai-sandbox` |
| **AI Endpoint** | `flk-team-ai-enablement-ai.services.ai.azure.com` |
| **Claude Model** | `claude-sonnet-4-6` |
| **Embedding Model** | `text-embedding-3-small` (1536d) |
| **BOM Excel** | `Jason data dump\29may_oracle_attachments\oracle_attachments\flkt28may2026_BOM_to_file.xlsx` |
| **PDF Base** | `Jason data dump\29may_oracle_attachments\oracle_attachments\{component_id}\{revision}\*.pdf` |
| **GitHub (local)** | `Taashi-Manyanga_fortive/PLM-AI-Drawing-tool` |
| **GitHub (cloud)** | `Taashi-Manyanga_fortive/PLM-AI-Drawing-tool-Azure` |

## Key Files

| File | Purpose |
|------|---------|
| `extract_supplemental_local.py` | Main extraction script (hybrid text+vision, concurrent, parent-item-driven, auto-load) |
| `load_single_drawing.py` | Neo4j graph loader (Drawing + BOM + Parts + Dims + Standards + Materials + Personnel + Embedding) |
| `query_graph.py` | 17 query tools for the agent (vector/fulltext/smart/Cypher/BOM-tree/specs/assembly/common) |
| `extraction_tracker.py` | Progress tracking and reconciliation (Excel + CSV export) |
| `build_parent_queue.py` | Parent-item queue builder (sorted smallest to largest) |
| `foundry_agent.py` | GPT-5.5 Gradio agent (deployed to Azure Web App) |
| `plm_agent.py` | Claude Sonnet agent (local alternative) |
| `bom_metadata_by_parent.json` | Parent-item queue (50 parents, components grouped) |
| `supplemental_extraction_progress.json` | Checkpoint/resume progress file |
| `supplemental_results/` | Extraction result JSON files |

---

## S1: Extract New Parent Item

**When:** User wants to process drawings for a specific <ORG> product (parent item number).

### Steps

1. **List available parents** to find the item number:
   ```bash
   cd "<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack"
   python extract_supplemental_local.py --list-parents
   ```
   Output shows all 50 parent items sorted smallest to largest, with completion status (DONE/PARTIAL/PENDING).

2. **Pick the next PENDING parent** (work top-down = smallest first for quick wins and tester handoff).

3. **Run extraction** with concurrent mode:
   ```bash
   python extract_supplemental_local.py --parent <ITEM_NUMBER> --concurrent
   ```
   This will:
   - Filter queue to only components under that parent
   - Extract using hybrid text+vision (text for >100 chars pages, vision for diagrams)
   - Use 8 parallel workers (~105s/item effective throughput)
   - Auto-load each result into Neo4j immediately after extraction
   - Print per-parent summary at the end

4. **Verify auto-load succeeded** (check the summary output for "Auto-load complete: X OK, Y FAIL").

5. **If any auto-loads failed**, manually load them (see S4).

### CLI Flags

| Flag | Effect |
|------|--------|
| `--parent <ITEM>` | Extract only components under this parent item |
| `--concurrent` | Enable 8 parallel workers (default is sequential) |
| `--workers 4` | Custom worker count (default 8) |
| `--max-items 10` | Smoke test — process only first 10 items |
| `--retry` | Retry previously failed items only |
| `--status` | Show progress without extracting |
| `--list-parents` | Show all parent items with counts |

### Cost and Time Estimates

- ~$0.15 per item (Claude API)
- ~105s effective per item in concurrent mode (8 workers)
- Smallest parents: 5-20 components (~$3, ~5 min)
- Largest parents: 200-400 components (~$60, ~1 hour)

### Processing Order (50 Parents, Smallest to Largest)

Always process top-down from `--list-parents` output. Smallest items finish fastest and give testers something to validate while larger items run.

---

## S2: Check Status

**When:** User wants to see extraction progress.

### Quick status
```bash
cd "<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack"
python extract_supplemental_local.py --status
```
Shows: completed/failed/remaining counts, cost, ETA, per-parent breakdown.

### Per-parent status
```bash
python extract_supplemental_local.py --list-parents
```
Shows each parent item with DONE/PARTIAL/PENDING status and component counts.

### Detailed tracker (with graph reconciliation)
```bash
python extraction_tracker.py --summary
```
Shows status breakdown (loaded/extracted/failed/pending/no_pdf/oversized), extraction metrics, and top classes by completion.

---

## S3: Retry Failures

**When:** Some items failed during extraction (network errors, timeouts, token expiry).

### Retry all failures globally
```bash
cd "<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack"
python extract_supplemental_local.py --retry --concurrent
```

### Retry failures for a specific parent
```bash
python extract_supplemental_local.py --parent <ITEM_NUMBER> --retry --concurrent
```

### Common failure causes and fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ReadTimeout` | Claude API slow on large PDFs | Retry (auto-backoff handles this) |
| `401 Unauthorized` | Azure AD token expired | Script auto-refreshes; if persistent, run `az login` |
| `429 Too Many Requests` | Rate limit hit with concurrent workers | Reduce `--workers 4` or wait |
| `SSLError` | Corporate proxy interference | Retry; if persistent, check VPN |
| `JSON parse failed` | Claude returned malformed JSON | Regex fallback in script; raw saved to debug file |
| `stop_reason=max_tokens` | Response truncated at 64K | Rare with current settings; split large multi-PDF items |

---

## S4: Load to Graph

**When:** Results exist in `supplemental_results/` but were not auto-loaded (e.g., auto-load was added after extraction).

### Load a single result file
```bash
cd "<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack"
python load_single_drawing.py <result_json_path> <component_id>
```

### Load all unloaded results (batch, error-isolated)
```python
import json, os, subprocess, sys, glob, time
sys.stdout.reconfigure(encoding="utf-8")
from query_graph import get_driver, NEO4J_DB

driver = get_driver()
already = set()
with driver.session(database=NEO4J_DB) as s:
    for row in s.run("MATCH (c:BOMComponent)-[:HAS_DRAWING]->(d:Drawing) RETURN c.item_number AS item"):
        already.add(row["item"])
driver.close()

to_load = []
for f_path in sorted(glob.glob("supplemental_results/*.json")):
    with open(f_path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    for r in data.get("results", []):
        if r["_component_id"] not in already:
            to_load.append(r)

print(f"Loading {len(to_load)} items...")
script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else os.getcwd()
ok = fail = 0
for i, r in enumerate(to_load):
    cid = r["_component_id"]
    tmp = f"_tmp_load_{cid}.json"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(r, f, indent=2, ensure_ascii=False)
        result = subprocess.run(
            [sys.executable, "load_single_drawing.py", tmp, cid],
            capture_output=True, text=True, timeout=180, encoding="utf-8", cwd=script_dir,
        )
        if result.returncode == 0: ok += 1
        else: fail += 1
    except subprocess.TimeoutExpired:
        fail += 1; print(f"  TIMEOUT: {cid}", flush=True)
    except Exception as e:
        fail += 1; print(f"  ERROR: {cid}: {e}", flush=True)
    finally:
        if os.path.exists(tmp): os.remove(tmp)
    if (i+1) % 25 == 0 or i == len(to_load)-1:
        print(f"  [{i+1}/{len(to_load)}] {ok} OK, {fail} FAIL", flush=True)
print(f"Done. {ok} loaded, {fail} failed.")
```

**IMPORTANT:** Always use `try/except subprocess.TimeoutExpired` to isolate timeout failures — a single slow item must NOT crash the entire batch.

### What `load_single_drawing.py` does (13-step pipeline)

1. MERGE Drawing node (with source tracking: `supplemental_extraction`)
2. Link BOMComponent -> Drawing (if component exists in graph)
3. Link Products -> Drawing (traverses BOM hierarchy up to 13 levels)
4. CREATE/MERGE Part nodes from BOM items (with quantity on relationship)
5. MERGE Dimension nodes
6. MERGE Standard nodes and COMPLIES_WITH relationships
7. MERGE Material nodes and USES_MATERIAL relationships
8. MERGE Person nodes with role-typed relationships (whitelisted: DRAWN_BY, CHECKED_BY, APPROVED_BY, ENGINEERED_BY, AUTHORED)
9. Generate text-embedding-3-small embedding (enriched with BOM, materials, standards)
10. Store embedding on Drawing node
11. All within a single transaction (rollback on failure)
12. Verification query prints loaded counts
13. Close driver

---

## S5: Update Tracker

**When:** After extraction/loading batches, to reconcile progress against BOM Excel.

```bash
cd "<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack"
python extraction_tracker.py --update
```

This:
1. Loads extraction progress from `supplemental_extraction_progress.json`
2. Scans result JSON files in `supplemental_results/`
3. Queries Neo4j for components with HAS_DRAWING relationships
4. Reconciles against BOM Excel
5. Exports `PLM_Extraction_Tracker.csv` and `PLM_Extraction_Tracker.xlsx` (beautified with conditional coloring)
6. Prints reconciliation summary (status breakdown, metrics, top classes)

### Tracker columns

| Column | Description |
|--------|-------------|
| `component_id` | Oracle BOM component item number |
| `description` | Component description |
| `class` | BOM class (Resistor, Capacitor, PlasticComponent, etc.) |
| `parent_items` | Finished goods parent products |
| `status` | loaded / extracted / failed / pending / no_pdf / oversized |
| `graph_loaded` | Y/N — whether component has HAS_DRAWING in Neo4j |
| `drawing_number` | Extracted drawing number (may differ from component_id) |
| `est_cost_usd` | ~$0.15 per extracted item |

### Other tracker commands

| Command | Purpose |
|---------|---------|
| `--init` | Full rebuild from BOM Excel + queue + progress + graph |
| `--update` | Incremental update (faster) |
| `--export` | Export CSV/Excel only (no graph check) |
| `--summary` | Print summary only |

---

## S6: Validate Parent Item

**When:** After extracting and loading a parent item, run E2E validation across 6 test dimensions.

### Validation Protocol (6 dimensions)

Run these Cypher queries via `python -c` or interactively. Replace `<ITEM>` with the parent item number.

#### 1. Top-Down: Product -> Drawings

```python
from query_graph import get_driver, NEO4J_DB
driver = get_driver()
with driver.session(database=NEO4J_DB) as s:
    # Count drawings reachable from this product via BOM
    r = s.run("""
        MATCH (p:Product {item_number: $item})
        MATCH (p)-[:HAS_BOM_ROOT]->(:BOMComponent)-[:BOM_CONTAINS*0..13]->(c:BOMComponent)-[:HAS_DRAWING]->(d:Drawing)
        RETURN count(DISTINCT d) AS drawings, count(DISTINCT c) AS components_with_drawings
    """, item="<ITEM>")
    print(dict(r.single()))
driver.close()
```
**PASS criteria:** drawings > 0, components_with_drawings matches expected count from `--list-parents`.

#### 2. Bottom-Up: Component -> Products

```python
from query_graph import get_component_details
# Pick a leaf component from the parent's BOM
details = get_component_details("<LEAF_ITEM_NUMBER>")
print(f"Products: {details.get('products', [])}")
print(f"Parents: {details.get('parents', [])}")
print(f"Drawings: {details.get('drawings', [])}")
```
**PASS criteria:** `products` list includes the parent item's model.

#### 3. Middle-Out: Smart Search

```python
from query_graph import smart_search
results = smart_search("<PRODUCT_NAME>")
for r in results:
    print(f"  {r['drawing_number']}: {r.get('title', '')} (RRF={r['rrf_score']:.4f})")
```
**PASS criteria:** Results include drawings from the parent item's BOM.

#### 4. BOM Tree

```python
from query_graph import get_bom_tree
tree = get_bom_tree("<ITEM>", max_depth=3)
print(f"Root: {tree['root_item']} — {tree['root_description']}")
print(f"Children: {tree['total_children']}")
for c in tree['children'][:10]:
    print(f"  L{c['level']}: {c['item_number']} {c['description'][:50]} draw={c['has_drawing']}")
```
**PASS criteria:** tree has children, some have `has_drawing=True`.

#### 5. Assembly Breakdown

```python
from query_graph import get_assembly_breakdown
result = get_assembly_breakdown("<PRODUCT_MODEL>")
print(f"Assemblies: {result.get('total_assemblies', 0)}")
for a in result.get('assemblies', [])[:10]:
    print(f"  L{a['bom_level']}: {a['assembly_item_number']} ({a['child_count']} children)")
```
**PASS criteria:** assemblies found with child counts > 0.

#### 6. Component Specs (if enriched)

```python
from query_graph import find_components_by_spec
results = find_components_by_spec("Resistor", "0603", product_query="<PRODUCT_MODEL>")
print(f"Found: {len(results)} matching components")
```
**PASS criteria:** returns enriched components if BoM CSV enrichment has been applied.

### Validation Summary Template

```
Parent Item: <ITEM> (<DESCRIPTION>)
─────────────────────────────────────
1. Top-Down (Drawings)          : PASS — X drawings, Y components
2. Bottom-Up (Component→Product): PASS — links to <MODEL>
3. Middle-Out (Smart Search)    : PASS — X results with RRF scores
4. BOM Tree                     : PASS — X children across Y levels
5. Assembly Breakdown           : PASS — X assemblies found
6. Component Specs              : PASS — X enriched specs found
─────────────────────────────────────
Overall: 6/6 PASS
```

---

## S7: Redeploy Agent

**When:** After code changes to `query_graph.py`, `foundry_agent.py`, or system prompts.

### Steps

1. **Build deploy.zip** from the Heather stack working directory:
   ```bash
   cd "<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack"

   # Create deploy.zip with the required files
   python -c "
   import zipfile, os
   files = [
       'foundry_agent.py',
       'query_graph.py',
       'audit_logger.py',
       'plm_agent.py',
       'startup.sh',
       'requirements.txt',
   ]
   with zipfile.ZipFile('deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zf:
       for f in files:
           if os.path.exists(f):
               zf.write(f)
           else:
               print(f'WARNING: {f} not found')
   print('deploy.zip created')
   "
   ```

2. **Deploy to Azure Web App:**
   ```bash
   az webapp deploy --resource-group flk-taashi-ai-sandbox --name flk-plm-drawing-agent --src-path deploy.zip --type zip
   ```

3. **Verify the agent is live:**
   ```bash
   curl -s -o /dev/null -w "%{http_code}" https://flk-plm-drawing-agent.azurewebsites.net/
   ```
   **PASS:** HTTP 200.

4. **Smoke test** the agent by opening `https://flk-plm-drawing-agent.azurewebsites.net` and asking:
   - "How many drawings are in the graph?" (should use `graph_statistics`)
   - "Show me drawings for the <ORG>-179" (should use `get_product_drawings`)

### Common Deploy Issues

| Issue | Fix |
|-------|-----|
| Startup crash | Check `az webapp log tail --name flk-plm-drawing-agent --resource-group flk-taashi-ai-sandbox` |
| Gradio version conflict | Gradio 6.x does NOT support `type="messages"` on ChatInterface — remove if present |
| `ModuleNotFoundError` | Check `requirements.txt` includes all deps: `gradio`, `neo4j`, `requests`, `azure-identity`, `openai` |
| 502 Bad Gateway | App still starting — wait 60s (600s startup timeout, `alwaysOn=true`) |
| Tool not found | Ensure `TOOL_DISPATCH` in `query_graph.py` has entry for every tool in `TOOL_DEFINITIONS` |

---

## S8: Code Improvements

**When:** User wants to fix bugs, add features, or refactor extraction/loading code.

### 3-Persona Code Review Pattern

Before merging any significant change, run a 3-persona review:

1. **Solution Architect** — Correctness, edge cases, error handling, security
2. **Enterprise Architect** — Scalability, maintainability, patterns, separation of concerns
3. **Principal Data Engineer** — Data quality, graph schema integrity, query performance, idempotency

### Review Checklist

| Category | Check |
|----------|-------|
| **Correctness** | JSON parse has try/except with regex fallback? |
| **Correctness** | Token refresh on 401 with cache invalidation? |
| **Correctness** | Retry with exponential backoff on transient errors? |
| **Correctness** | `flush=True` on all print statements (critical for VM stdout buffering)? |
| **Correctness** | Atomic file writes via tmp + `os.replace`? |
| **Security** | No hardcoded credentials? All via env vars or `az account get-access-token`? |
| **Security** | Cypher write operations blocked (whitelist check in `cypher_query`)? |
| **Security** | Personnel relationship types whitelisted (ALLOWED_RELS)? |
| **Graph** | MERGE (not CREATE) for Dimension/Standard/Material/Person nodes? |
| **Graph** | BOMComponent existence check before HAS_DRAWING link? |
| **Graph** | Transaction wrapper with rollback on failure? |
| **Graph** | Embedding enriched with BOM, materials, standards context? |
| **Performance** | Thread-safe progress updates with lock? |
| **Performance** | Concurrent mode with configurable worker count? |
| **Performance** | Neo4j connection pool (15) with retry on ServiceUnavailable? |
| **Data Quality** | Deduplication on merged list fields? |
| **Data Quality** | Null-safe notes handling (`[str(n) for n in notes if n]`)? |
| **Data Quality** | `drawing_number_source` tracked (extracted vs. component_id_fallback)? |

### Test Protocol

After any code change:

1. **Unit test** — Run the script's self-test:
   ```bash
   python query_graph.py   # Runs 4-check self-test (vector, fulltext, details, stats)
   ```

2. **Smoke test** — Extract 1 item:
   ```bash
   python extract_supplemental_local.py --parent <SMALL_PARENT> --max-items 1
   ```

3. **Regression** — Run 36-query baseline (from Phase 7):
   ```python
   from query_graph import *
   checks = [
       ("vector_search", lambda: vector_search("multimeter", 3)),
       ("fulltext_search", lambda: fulltext_search("CAT III", "drawing_text", 3)),
       ("smart_search", lambda: smart_search("thermal management", 3)),
       ("get_drawing_details", lambda: get_drawing_details("D2042647")),
       ("get_bom_tree", lambda: get_bom_tree("1564549", 2)),
       ("graph_statistics", lambda: graph_statistics()),
       ("find_components_by_spec", lambda: find_components_by_spec("Resistor", "0603")),
       ("get_assembly_breakdown", lambda: get_assembly_breakdown("<ORG>-179")),
   ]
   for name, fn in checks:
       try:
           result = fn()
           err = result.get("error") if isinstance(result, dict) else None
           print(f"  {'PASS' if not err else 'FAIL'}: {name} — {err or 'OK'}")
       except Exception as e:
           print(f"  FAIL: {name} — {e}")
   ```

4. **Agent validation** — If query_graph.py changed, redeploy and test (see S7).

### GitHub Workflow

- **Branch strategy:** `main` <-- `dev` <-- `feature/*`
- **PR workflow:** Create feature branch, make changes, PR to dev, merge to main
- **Sanitization:** 23-24 regex rules via `sanitize_for_repo.py` — replaces local paths, usernames, emails, Neo4j passwords
- **Both repos:** Changes must be synced to both `PLM-AI-Drawing-tool` (local) and `PLM-AI-Drawing-tool-Azure` (cloud)

---

## S9: Ad Hoc Queries

**When:** User wants to query the graph directly.

### Python one-liner pattern

```bash
cd "<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack"
python -c "
from query_graph import *
import json

# Graph stats
stats = graph_statistics()
print(json.dumps(stats, indent=2))
"
```

### Common queries

**Total graph size:**
```python
stats = graph_statistics()
# Expected: ~20K+ nodes, ~31K+ relationships (grows with each extraction batch)
```

**Drawings per source:**
```python
results = cypher_query("""
    MATCH (d:Drawing)
    RETURN d.source AS source, count(d) AS count
    ORDER BY count DESC
""")
```

**Products with most drawings:**
```python
results = cypher_query("""
    MATCH (p:Product)-[:HAS_DRAWING]->(d:Drawing)
    RETURN p.model AS product, p.item_number AS item, count(d) AS drawings
    ORDER BY drawings DESC LIMIT 10
""")
```

**Components without drawings (orphans):**
```python
results = cypher_query("""
    MATCH (c:BOMComponent)
    WHERE NOT (c)-[:HAS_DRAWING]->(:Drawing)
    AND c.doc_count > 0
    RETURN c.item_number AS item, c.description AS desc, c.class AS class
    LIMIT 20
""")
```

**17 Available Query Tools:**

| Tool | Purpose |
|------|---------|
| `vector_search` | Semantic similarity search via embeddings |
| `fulltext_search` | Keyword/phrase search across 6 indexes |
| `smart_search` | Hybrid vector+fulltext with Reciprocal Rank Fusion |
| `get_drawing_details` | Full drawing with all relationships |
| `get_bom_for_drawing` | BOM parts list for a drawing |
| `find_drawings_by_standard` | Drawings by compliance standard (IEC, UL, MIL) |
| `find_drawings_by_material` | Drawings by material (ABS, copper, etc.) |
| `get_product_drawings` | Drawings linked to a product (with fuzzy matching) |
| `get_bom_tree` | BOM hierarchy tree (up to 6 levels) |
| `find_components_by_class` | Components by BOM class (Resistor, Capacitor, etc.) |
| `get_component_details` | Full component with parents, children, drawings, products |
| `graph_statistics` | Summary counts by node/relationship type |
| `cypher_query` | Read-only Cypher (no writes allowed) |
| `find_components_by_spec` | Components by electrical/mechanical spec |
| `get_assembly_breakdown` | Assembly-level product structure |
| `find_common_components` | Cross-product component reuse |
| `get_component_specs` | Parsed specs with confidence level |

---

## S10: Rebuild Parent Queue

**When:** After new data arrives, or to refresh the queue after graph changes.

```bash
cd "<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Heather stack"
python build_parent_queue.py
```

This:
1. Reads BOM Excel (`flkt28may2026_BOM_to_file.xlsx`)
2. Groups components by parent item (finished goods product)
3. Checks Neo4j for already-loaded components (skips them)
4. Scans disk for available PDFs
5. Filters out oversized items (>20 MB)
6. Outputs `bom_metadata_by_parent.json` sorted smallest to largest
7. Prints all 50 parent items with pending/done counts

---

## Architecture Reference

### Pipeline Flow

```
BOM Excel (Oracle PLM export)
    |
    v
build_parent_queue.py  -->  bom_metadata_by_parent.json (50 parents, sorted)
    |
    v
extract_supplemental_local.py --parent X --concurrent
    |  (hybrid text+vision: PyMuPDF text for >100 chars pages, Claude vision for diagrams)
    |  (8 parallel workers, checkpoint/resume, auto-retry with backoff)
    |
    v
supplemental_results/*.json  +  supplemental_extraction_progress.json
    |
    v  (auto-load embedded in extraction script)
load_single_drawing.py  -->  Neo4j (Drawing + Parts + Dims + Standards + Materials + Personnel + Embedding)
    |
    v
extraction_tracker.py --update  -->  PLM_Extraction_Tracker.xlsx/csv
    |
    v
foundry_agent.py (GPT-5.5) / plm_agent.py (Claude)  -->  Gradio Web App
    |                                                       (17 query tools)
    v
https://flk-plm-drawing-agent.azurewebsites.net
```

### Graph Schema

**11 Node Types:**
- `Drawing` (3,282+) — Engineering drawings with embeddings
- `BOMComponent` (8,084) — Oracle BOM components with parsed specs
- `Product` (50) — Finished goods (<ORG>-179, <ORG>-1587 FC, etc.)
- `Part` (756+) — Parts from BOM tables on drawings
- `Dimension` (5,014+) — Dimensional callouts
- `Document` (1,260) — Referenced documents
- `Standard` (443) — Compliance standards (IEC, UL, MIL)
- `Person` (402) — Engineers, drafters, approvers
- `Revision` (828) — Revision history entries
- `Material` (217) — Materials and finishes
- `Item` (24) — Legacy item nodes (Heather data)

**22 Relationship Types:**
- `HAS_DRAWING` (Product/BOMComponent -> Drawing)
- `HAS_BOM_ROOT` (Product -> BOMComponent)
- `BOM_CONTAINS` (BOMComponent -> BOMComponent, 14,706 edges, up to 13 levels)
- `CONTAINS_COMPONENT` (Drawing -> Part)
- `HAS_DIMENSION` (Drawing -> Dimension)
- `COMPLIES_WITH` (Drawing -> Standard)
- `USES_MATERIAL` (Drawing -> Material)
- `DRAWN_BY/CHECKED_BY/APPROVED_BY/ENGINEERED_BY/AUTHORED` (Person -> Drawing)
- `HAS_REVISION` (Drawing -> Revision)
- `REFERENCES` (Drawing -> Document)
- `IS_PRODUCT` (Product -> Item, legacy)
- `DOCUMENTS` (Drawing -> Item, legacy)

**Indexes (23):**
- 9 uniqueness constraints
- 6 full-text indexes (drawing_text, part_text, document_text, standard_text, bom_component_text, product_text)
- 1 vector index (drawing_embeddings, 1536d, cosine)
- 2 composite indexes
- 2 LOOKUP indexes
- 3 range indexes

### Hybrid Extraction Design

The extraction uses a hybrid text+vision approach that reduces API payload by ~99%:

- **Text pages** (>100 chars from PyMuPDF `page.get_text()`): Sent as plain text blocks
- **Vision pages** (<100 chars text): Rendered as PNG via PyMuPDF and sent as base64 images
- **DPI scaling**: 150 DPI for <15 vision pages, 100 DPI for >15
- **Max pages**: 30 per document (hard limit)
- **Max file size**: 20 MB (files larger are skipped)

**Why hybrid matters:** A 72-page capacitor spec sends 420 KB via hybrid vs. 9.1 MB via pure vision (which crashes). Hybrid also extracts MORE data (102 notes vs. 77 from native PDF processing).

### Key Learnings

1. **flush=True on all prints** — Critical for VM stdout buffering. Without it, no output appears until the process exits.
2. **Atomic progress writes** — Use `tmp + os.replace()` pattern to prevent corruption from concurrent workers.
3. **Parent-item batching** — Completing one parent item = all its components are ready for tester handoff.
4. **Auto-load after extraction** — Added in Phase 8 so results go straight into the graph without a separate step.
5. **drawing_number fallback** — Some documents lack a drawing number; script uses `component_id` as fallback and tracks the source.
6. **max_tokens=65536** — Prevents JSON truncation on large multi-page documents (was 16K, caused 5 failures in Phase 5).
7. **Token TTL=2700s** — Refresh 45 min before the 1-hour Azure AD token expiry, with cache invalidation on 401.
8. **Neo4j Aura pausing** — Free-tier instances auto-pause after inactivity. The driver has 3-attempt reconnection with exponential backoff.
9. **Gradio 6.x** — Does NOT support `type="messages"` on ChatInterface. Use `_normalize_history()` for format conversion.
10. **Collect+intersect for common components** — Avoids Cartesian explosion of bidirectional `*1..13` BOM traversals. Depth capped at `*1..6`.

### Extraction Field Names (Common Gotchas)

The Claude extraction JSON uses these field names (NOT what you might guess):
- `bom_items` (not `bill_of_materials`)
- `general_notes` (not `notes`)
- `title_block_info` (not `title_block`)
- `key_dimensions` (not `dimensions`)
- `cross_references.related_standards` (not `standards`)
- `materials_finishes.primary_material` (not `material`)
- `extraction_confidence` — dict with text values like "high" (not floats)
- `_component_id`, `_pages_sent`, `_pdf_count`, `_extraction_time_s`, `_revision`, `_description`, `_total_pages` — underscore-prefixed metadata fields

### Drawing Sources in Neo4j

| `d.source` | Origin |
|------------|--------|
| `NULL` | Original 20 Heather drawings (Phase 3) |
| `jason_bom_29may` | 458 Jason BOM drawings (Phase 5) |
| `supplemental_extraction` | Phase 8 supplemental extraction (current) |
