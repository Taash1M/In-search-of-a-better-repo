---
name: ai-ucb-pipeline
description: Phase 2 Data Pipeline sub-skill for the AI Use Case Builder. Generates ADF pipelines and Databricks notebooks following the UBI medallion architecture (Bronze/Silver/Gold/AI Layer). Uses archetype dispatch to select correct templates. Reads requirements.pipeline from ai-ucb-state.json. Invoke standalone or via orchestrator. Trigger when user mentions 'pipeline', 'data pipeline', 'ADF', 'Databricks notebooks', 'medallion', 'ETL', or 'data ingestion'.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# AI Use Case Builder - Phase 2: Data Pipelines (Archetype-Aware)

You are the Data Engineering agent. Your job is to generate ADF pipelines and Databricks notebooks that move data from source systems through the medallion architecture (Bronze → Silver → Gold → AI Layer) to the target data stores.

**Key design principle:** This skill reads `requirements.pipeline` from `ai-ucb-state.json` — the contract populated by Phase 0 Discovery. Every decision (which Bronze notebook, which Silver transforms, which AI Layer processing) is driven by the contract, not by interpretation.

## Access Control (Inherited)

1. **NEVER write to production Databricks databases or ADF pipelines.**
2. **Default target: Dev environment** — `flukebi_Bronze`, `flukebi_Silver`, `flukebi_Gold` in dev Databricks.
3. **Never hard-code credentials in notebooks.** Use Key Vault-backed secret scopes or widget parameters.
4. **Gate before first pipeline execution.** Generate and validate, then get user approval before running.

## Prerequisites

- Phase 1 (Infrastructure) must be `completed` in `ai-ucb-state.json`
- Required state: `requirements.pipeline`, `resources` (Databricks, ADF, ADLS IDs), `naming`

## Pipeline Flow

### Step 1: Read Contract and Validate

```python
# Read these fields from ai-ucb-state.json
state = read_json("ai-ucb-state.json")
pipeline = state["requirements"]["pipeline"]
resources = state["resources"]
archetype = state["archetype"]

# Validate required fields exist
assert pipeline["source_systems"], "No source systems defined"
assert pipeline["bronze_strategy"], "No bronze strategy defined"
assert pipeline["gold_output"], "No gold output defined"
assert pipeline["ai_layer_processing"], "No AI layer processing defined"
```

If any required field is missing, fail with a clear message pointing back to Phase 0.

### Step 2: Archetype Dispatcher

This is the core integration logic. Dispatch to the correct template set based on archetype:

```
switch(archetype):
  "rag"               → RAG pipeline (FULL implementation)
                        IF requirements.pipeline.multimodal_rag == true:
                          → Enhanced Bronze: layout-aware parsing via /doc-intelligence Tier 1
                          → Enhanced Silver: cross-modal separation (text, tables, images, equations)
                          → Enhanced Gold: type-aware chunking with image references
                          → Enhanced AI Layer: multimodal embeddings + cross-modal graph edges
                          Read /rag-multimodal for 11-stage pipeline details
                        IF requirements.pipeline.enhanced_parsing == true (without multimodal_rag):
                          → Enhanced Bronze: layout-aware parsing via /doc-intelligence Tier 1
                          → Standard Silver/Gold/AI Layer (text-only RAG)
  "conversational"    → Conversational pipeline (FULL — mirrors RAG with minor tweaks)
                        Inherits multimodal_rag / enhanced_parsing conditionals from RAG
  "doc-intelligence"  → Doc Intelligence pipeline (FULL — via /doc-intelligence skill)
                        → Bronze: Bronze_DocIngest (layout-aware parsing, OCR, image restoration)
                        → Silver: Silver_DocParse (Tier 1) + Silver_DocExtract (Tier 2 concepts)
                        → Gold: Gold_ExtractedData (structured extraction output)
                        → AI Layer: AILayer_Embeddings (optional, for searchable index)
                        Tier selection from requirements.pipeline.doc_intelligence_tier:
                          tier_1 → Doctra-pattern parsing (PaddleOCR layout, dual OCR, VLM)
                          tier_2 → ContextGem-pattern extraction (8 concept types, aspects)
                          tier_3 → Azure AI Document Intelligence (prebuilt + custom models)
                        Read /doc-intelligence for tier details and notebook templates
  "predictive-ml"     → Predictive ML pipeline [FULL]
                        → Bronze: Bronze_{app}_{source} (standard extraction from source systems)
                        → Silver: Silver_{app} with feature-eng transform
                          - Window functions (lag, lead, rolling averages)
                          - Aggregation features (group-by summaries, percentile bins)
                          - Temporal features (day of week, month, quarter, YoY delta)
                          - Null imputation (median for numeric, mode for categorical)
                        → Gold: Gold_TrainingData
                          - Feature/label split using requirements.pipeline.ml_label_column
                          - Stratified train/val/test split (70/15/15 default)
                          - Delta table versioned by timestamp for reproducibility
                          - Feature statistics logged (mean, std, null%, cardinality)
                        → AI Layer: AILayer_MLTraining
                          - MLflow experiment creation on Databricks
                          - Model training (XGBoost default, scikit-learn, LightGBM)
                          - Hyperparameter logging + metric tracking (accuracy, F1, AUC)
                          - Model registration in Unity Catalog (catalog.schema.model_name)
                          - Alias promotion (champion/challenger)
                        IF requirements.pipeline.feature_store == true:
                          → Feature table creation via databricks-feature-engineering
                          → FeatureLookup integration for training set assembly
                        Read /ai-ucb/pipeline-templates.md for notebook code
  "knowledge-graph"   → Knowledge Graph pipeline [FULL]
                        → Bronze: Bronze_{app}_{source} (standard extraction)
                        → Silver: Silver_{app} with entity-extraction transform
                          - Azure AI Language NER (built-in categories: Person, Org, Location, DateTime)
                          - OR custom NER model (project_name from requirements.pipeline.ner_project)
                          - Batch processing in chunks of 25 docs (Azure SDK limit)
                          - Entity columns added: entity_text, entity_category, confidence, offset
                        → Gold: Gold_GraphTriples
                          - LLM-powered triple extraction (subject-predicate-object)
                          - Entity deduplication via fuzzy matching (Levenshtein + embedding similarity)
                          - Triple confidence scoring (EXTRACTED vs INFERRED)
                          - Delta table: source_id, subject, predicate, object, confidence, source_page
                        → AI Layer: AILayer_GraphLoad
                          - Batch load to Neo4j (UNWIND pattern, 5000 rows/tx) or Cosmos DB Gremlin
                          - Schema creation: uniqueness constraints, full-text indexes, vector indexes
                          - MERGE-based idempotent loading (re-runnable without duplicates)
                          - Graph validation: orphan node check, relationship coverage
                        Graph store selection from requirements.pipeline.graph_store:
                          "neo4j"     → Neo4j Python driver (bolt://), APOC batch loading
                          "cosmos_db" → Gremlin API (wss://), GraphSONv2, RU throttling
                        Read /doc-intelligence for entity extraction patterns
                        Read graphify skill for Neo4j Cypher export and push patterns
  "voice-text"        → Voice/Text pipeline [FULL]
                        → Bronze: Bronze_Media (store audio/video in ADLS, metadata sidecar)
                        → Silver: Silver_{app} with transcription transform
                          - Azure Speech-to-Text Batch API (REST, api-version=2024-11-15)
                          - Batch job submission with contentUrls from ADLS
                          - Speaker diarization (ConversationTranscriber, max 5 speakers)
                          - Word-level timestamps, punctuation, profanity masking
                          - Poll for completion (30s intervals), retrieve results
                          - Output: transcript text, speaker labels, timestamps per phrase
                        → Gold: Gold_ChunkedDocs
                          - Semantic chunking of transcripts with speaker attribution
                          - Metadata: speaker_id, start_time, end_time, confidence
                        → AI Layer: AILayer_Embeddings (standard embedding pipeline)
                        IF requirements.pipeline.custom_speech_model:
                          → Custom Speech model training via REST API
                          → Acoustic/Language model fine-tuning on domain audio
                        Read Azure Speech SDK docs for real-time vs batch patterns
  "multi-agent"       → Multi-Agent pipeline [FULL] (via /agentic-deploy Module 1)
                        If requirements.pipeline.agent_runtime == true:
                          Generate LangGraph state machine notebooks + tool definitions
                          Generate checkpointer setup (cosmos_db | postgres | memory)
                          Generate LLM registry with circular fallback config
                        Read /agentic-deploy for runtime patterns and notebook templates
  "computer-vision"   → Computer Vision pipeline [FULL] (via /doc-intelligence vision extraction)
                        → Bronze: Bronze_Media (store images/PDFs in ADLS, metadata sidecar)
                        → Silver: Silver_{app} with image-labeling transform
                          - Azure AI Vision 4.0 Image Analysis (caption, tags, objects, OCR)
                          - Batch processing via Azure Functions (blob trigger → analyze → results blob)
                          - Multimodal embeddings for zero-shot classification (vectorizeImage + vectorizeText)
                          - Output: caption, object_list, tag_list, ocr_text, bounding_boxes, confidence
                        IF requirements.pipeline.vision_mode == "document":
                          → Silver: Silver_{app} with vision extraction from /doc-intelligence
                            - PyMuPDF renders PDF→PNG at 150 DPI, base64 encode
                            - litellm → Azure AI Foundry → Claude Sonnet/GPT-4o vision
                            - Structured JSON extraction (drawing_number, title, BOM, materials)
                            - Two-pass BOM: Doc Intelligence table detection → vision LLM extraction
                        → Gold: Gold_ExtractedData (structured metadata + labels)
                          OR Gold_TrainingData (if training custom models)
                        → AI Layer: AILayer_IndexPop (push labeled data to AI Search)
                          OR AILayer_MLTraining (if fine-tuning custom vision models via Azure ML)
                        IF requirements.pipeline.custom_vision_model:
                          → Florence-2 deployment via Azure ML (HuggingFace model)
                          → OR Azure AI Vision custom training (deprecated Mar 2025 — prefer Florence-2)
                        Read /doc-intelligence for vision extraction and two-pass BOM patterns
```

**FULL** = complete, production-ready templates with all logic implemented. All archetypes and notebook templates are now FULL as of Sprint 12.

**Skill cross-references:**
- `/doc-intelligence` — 3-tier document parsing and extraction (Tier 1: layout-aware OCR, Tier 2: declarative extraction, Tier 3: Azure AI Doc Intelligence)
- `/rag-multimodal` — Cross-modal knowledge graph, VLM-enhanced retrieval, multimodal index schema
- `/agentic-deploy` — LangGraph state machine, circular LLM fallback, checkpointer setup, tool definitions (Module 1)

**Read** `ai-ucb/pipeline-templates.md` for all template code.

### Step 3: Generate ADF Pipeline

Read `requirements.pipeline.source_systems[]` to determine extraction activities.

**Source type → ADF activity mapping:**

| Source Type | ADF Activity | Linked Service | Notes |
|-------------|-------------|----------------|-------|
| oracle | Copy Activity (JDBC) | OracleLinkedService | Full table or query |
| azure-sql | Copy Activity (SQL) | AzureSqlLinkedService | Full table or query |
| sftp | Copy Activity (SFTP) | SftpLinkedService | File pattern |
| sharepoint | Databricks Activity | DatabricksLinkedService | REST OAuth extraction |
| rest-api | Databricks Activity | DatabricksLinkedService | Custom API extraction |
| bigquery | Copy Activity (BigQuery) | BigQueryLinkedService | Full table or query |
| dataverse | Copy Activity (Dataverse) | DataverseLinkedService | Entity extraction |
| adls | Skip extraction | N/A | Read directly in Silver |
| blob | Copy Activity (Blob) | BlobStorageLinkedService | File copy |
| csv-upload | Skip extraction | N/A | Manual upload path |

**ADF master pipeline structure (follows UBI pattern):**

```
PL_{app}_Master
├── Pre-Logging
│   └── Stored Procedure: usp_StatusControl_PreLog
│       Parameters: StreamName={app}, SubStream='Master', Status='Running'
│
├── For Each: source_systems[]
│   └── IF source.type IN (oracle, azure-sql, sftp, bigquery, dataverse, blob)
│       └── Copy Activity: Extract_{source.name}
│           Source: {linked_service} → {source.query or table}
│           Sink: ADLS → Bronze/{app}/{source.name}/
│   └── ELSE IF source.type IN (sharepoint, rest-api)
│       └── Databricks Activity: Bronze_{app}_{source.name}
│           Notebook: /Shared/{app}/Bronze_{source.name}
│
├── Databricks Activity: Silver_{app}
│   └── Notebook: /Shared/{app}/Silver_{app}
│
├── Databricks Activity: Gold_{app}
│   └── Notebook: /Shared/{app}/Gold_{app}
│
├── Databricks Activity: AILayer_{app}
│   └── Notebook: /Shared/{app}/AILayer_{app}
│
├── Publish Activities (for each publish_target)
│   ├── IF adls-delta → Write Activity (already done by notebooks)
│   ├── IF ai-search → Databricks Activity: Publish_AISearch_{app}
│   ├── IF cosmos-db → Databricks Activity: Publish_CosmosDB_{app}
│   ├── IF neo4j → Databricks Activity: Publish_Neo4j_{app}
│   └── IF fabric-onelake → Shortcut creation (one-time)
│
├── Post-Logging
│   └── Stored Procedure: usp_StatusControl_PostLog
│       Parameters: StreamName={app}, SubStream='Master', Status='Succeeded'
│
└── On Failure
    ├── Post-Logging: Status='Failed'
    └── Logic App: Send failure alert (email + Teams)
```

**Trigger generation** based on `requirements.pipeline.schedule`:

| Schedule | Trigger Type | Configuration |
|----------|-------------|---------------|
| daily | Schedule Trigger | `"recurrence": {"frequency": "Day", "interval": 1, "startTime": "06:00"}` |
| hourly | Schedule Trigger | `"recurrence": {"frequency": "Hour", "interval": 1}` |
| bi-hourly | Schedule Trigger | `"recurrence": {"frequency": "Hour", "interval": 2}` |
| event-driven | Blob Event Trigger | Monitors ADLS container for new files |
| manual | None | No auto-trigger; manual run only |
| real-time | Event Grid Trigger | Near-real-time event processing |

### Step 4: Generate Databricks Notebooks

Generate one notebook per medallion layer. Notebook content is driven by `requirements.pipeline`.

**Notebook naming:** `{Layer}_{AppSlug}_{Purpose}`
**Notebook location:** `/Shared/{app}/` in Databricks workspace

**Bronze notebook** — selected by `requirements.pipeline.bronze_strategy`:

| Strategy | Template | Key Logic |
|----------|----------|-----------|
| `schema-on-read` | Bronze_Typed | Read source as-is, all columns STRING, add metadata cols |
| `typed-ingestion` | Bronze_Typed | Preserve source types, add metadata, partition by date |
| `doc-ingestion` | Bronze_Documents | Parse PDF/DOCX/HTML → text, extract metadata (author, date, pages) |
| `doc-ingestion-enhanced` | Bronze_DocIngest | Layout-aware parsing via /doc-intelligence Tier 1 (PaddleOCR layout detection, dual OCR, DocRes image restoration, VLM chart-to-table). Auto-selected when `enhanced_parsing: true` or `multimodal_rag: true` |
| `media-ingestion` | Bronze_Media | Store files in ADLS, extract metadata sidecar (duration, format, size) |

**Silver notebook** — composable transforms from `requirements.pipeline.silver_transforms[]`:

Each transform is a code block added to the Silver notebook. Multiple transforms compose sequentially:

| Transform | Code Block | Status |
|-----------|-----------|--------|
| `type-casting` | Cast STRING columns to correct types using schema map | FULL |
| `joins` | LEFT JOIN to dimension tables using key mappings | FULL |
| `dedup` | Window function dedup by PK + ORDER BY timestamp DESC | FULL |
| `text-cleaning` | Strip HTML, normalize whitespace, remove special chars | FULL |
| `entity-extraction` | Azure AI Language NER (TextAnalyticsClient, 25 docs/batch, built-in or custom project). Adds entity_text, entity_category, confidence, offset columns. Batch via `begin_analyze_actions()` for multi-action processing | FULL |
| `doc-extraction` | Declarative extraction via /doc-intelligence Tier 2 (ContextGem-pattern: 8 concept types, aspects, reference tracing, justifications). Auto-selected when archetype is `doc-intelligence` | FULL |
| `cross-modal-separation` | Separate text, tables, images, equations into typed content streams. Auto-selected when `multimodal_rag: true` | FULL |
| `feature-eng` | Window functions (lag/lead/rolling avg), temporal features (day_of_week, month, quarter, YoY delta), aggregation features (group-by summaries, percentile bins), null imputation (median numeric, mode categorical). All features logged to MLflow for lineage | FULL |
| `transcription` | Azure Speech-to-Text Batch API (REST api-version=2024-11-15). Submits contentUrls from ADLS, polls 30s, retrieves JSON results. Speaker diarization via ConversationTranscriber (max 5 speakers). Word-level timestamps, punctuation, profanity masking. Optional custom speech model for domain vocabulary | FULL |
| `image-labeling` | Azure AI Vision 4.0 Image Analysis SDK (caption, tags, objects, OCR, bounding boxes). Batch via Azure Functions blob trigger. Multimodal embeddings (vectorizeImage + vectorizeText) for zero-shot classification. OR vision extraction via /doc-intelligence (PyMuPDF→base64→litellm→Claude Sonnet, two-pass BOM for engineering drawings) | FULL |

**Gold notebook** — selected by `requirements.pipeline.gold_output`:

| Output | Template | Key Logic |
|--------|----------|-----------|
| `views` | Gold_Views | CREATE OR REPLACE VIEW with business aliases | FULL |
| `aggregations` | Gold_Aggregations | Group-by aggregations, summary tables | FULL |
| `chunked-docs` | Gold_ChunkedDocs | Semantic chunking with overlap, metadata enrichment | FULL |
| `chunked-docs-multimodal` | Gold_ChunkedMultimodal | Type-aware chunking: text chunks with image/table references, cross-modal metadata. Auto-selected when `multimodal_rag: true`. Read /rag-multimodal for schema | FULL |
| `training-datasets` | Gold_TrainingData | Feature/label split by `ml_label_column`, stratified train/val/test (70/15/15), Delta versioned by timestamp, feature statistics (mean, std, null%, cardinality) logged to MLflow. Optional FeatureLookup integration when `feature_store: true` | FULL |
| `graph-triples` | Gold_GraphTriples | LLM-powered triple extraction (subject-predicate-object), entity dedup via fuzzy matching (Levenshtein + embedding similarity), confidence scoring (EXTRACTED vs INFERRED), Delta table: source_id, subject, predicate, object, confidence, source_page | FULL |

**AI Layer notebook** — selected by `requirements.pipeline.ai_layer_processing`:

| Processing | Template | Key Logic |
|------------|----------|-----------|
| `embeddings` | AILayer_Embeddings | Batch embed via AI Services → push to AI Search/Cosmos | FULL |
| `embeddings-multimodal` | AILayer_MultimodalEmbed | Text embeddings + cross-modal graph edges (belongs_to, references) + VLM image descriptions. Extended AI Search index with content_type, page_idx, image_path, is_multimodal fields. Auto-selected when `multimodal_rag: true`. Read /rag-multimodal for index schema | FULL |
| `graph-load` | AILayer_GraphLoad | Neo4j: UNWIND batch 5000 rows/tx, MERGE-based idempotent load, uniqueness constraints + full-text + vector indexes, APOC periodic.iterate for large graphs, orphan check. Cosmos DB: Gremlin API (wss://), GraphSONv2, RU throttling on 429, partition key per vertex | FULL |
| `ml-training` | AILayer_MLTraining | MLflow experiment creation, model training (XGBoost/scikit-learn/LightGBM), hyperparameter logging + metric tracking (accuracy, F1, AUC, RMSE), model registration in Unity Catalog (catalog.schema.model_name), alias promotion (champion/challenger). Optional feature store via databricks-feature-engineering FeatureLookup | FULL |
| `index-population` | AILayer_IndexPop | Azure AI Search index creation (SearchIndexClient), batch upload via `upload_documents()` (1000 docs/batch), field mapping from Gold schema, vector field configuration (HNSW, 1536 dims), semantic ranker config, incremental sync via `@search.action: mergeOrUpload`, retry with exponential backoff on 429s | FULL |
| `multi-model` | AILayer_MultiModel | Multi-model inference pipeline: model registry lookup from Unity Catalog, A/B routing (champion vs challenger by traffic %), batch scoring via `mlflow.pyfunc.spark_udf()`, result comparison logging, automatic promotion when challenger beats champion on eval metric for N consecutive batches. Supports ensemble (weighted avg) and cascade (fast→slow fallback) patterns | FULL |

### Step 5: Data Quality Gates Between Layers

Every layer transition must pass a quality gate before the next layer starts. Gates are implemented as notebook exit codes — if a gate fails, the ADF pipeline stops.

**Gate implementation pattern:**

```python
# quality_gate.py — reusable quality gate function
def quality_gate(spark, table_name, checks, gate_name=""):
    """Run data quality checks on a Delta table. Raises AssertionError on failure."""
    results = []
    df = spark.table(table_name)

    for check in checks:
        if check["type"] == "row_count_min":
            actual = df.count()
            passed = actual >= check["threshold"]
            results.append({"check": f"row_count >= {check['threshold']}", "actual": actual, "passed": passed})

        elif check["type"] == "null_rate":
            from pyspark.sql.functions import col, count, when, isnan
            total = df.count()
            nulls = df.filter(col(check["column"]).isNull() | isnan(col(check["column"]))).count()
            rate = nulls / max(total, 1)
            passed = rate <= check["threshold"]
            results.append({"check": f"null_rate({check['column']}) <= {check['threshold']}", "actual": round(rate, 4), "passed": passed})

        elif check["type"] == "pk_uniqueness":
            from pyspark.sql.functions import count as _count
            dupes = df.groupBy(check["columns"]).agg(_count("*").alias("cnt")).filter("cnt > 1").count()
            passed = dupes == 0
            results.append({"check": f"pk_unique({check['columns']})", "actual": dupes, "passed": passed})

        elif check["type"] == "row_count_drift":
            # Compare to previous run — detect >X% drop
            prev_count = spark.sql(f"SELECT MAX(row_count) FROM flukebi_Gold.kpi_row_counts WHERE table_name = '{table_name}'").collect()[0][0] or 0
            current = df.count()
            drift = abs(current - prev_count) / max(prev_count, 1)
            passed = drift <= check["threshold"]
            results.append({"check": f"row_drift <= {check['threshold']}", "actual": round(drift, 4), "passed": passed})

    # Log results to audit table
    gate_passed = all(r["passed"] for r in results)
    print(f"\n{'='*60}")
    print(f"QUALITY GATE: {gate_name} — {'PASSED' if gate_passed else 'FAILED'}")
    for r in results:
        icon = "PASS" if r["passed"] else "FAIL"
        print(f"  [{icon}] {r['check']} → actual: {r['actual']}")
    print(f"{'='*60}\n")

    if not gate_passed:
        failed = [r for r in results if not r["passed"]]
        raise AssertionError(f"Quality gate '{gate_name}' FAILED: {failed}")
    return results
```

**Standard gates per layer:**

| Gate | Checks | Failure Action |
|------|--------|----------------|
| Bronze → Silver | `row_count_min(1)`, `null_rate(pk_col) <= 0.0` | Stop pipeline, alert — extraction failed |
| Silver → Gold | `pk_uniqueness`, `null_rate(required_cols) <= 0.01`, `row_count_drift <= 0.20` | Stop pipeline, investigate transform |
| Gold → AI Layer | `row_count_min(1)`, `null_rate(content_col) <= 0.0` | Stop pipeline, Gold data is corrupted |
| AI Layer → Publish | `row_count_drift <= 0.30` | Warning only — AI layer may legitimately change sizes |

**ADF integration:** Each gate is a Databricks activity between layers. On failure, ADF pipeline goes to the On Failure branch, logs the error, and sends an alert.

### Step 6: Pipeline Retry and Rollback

**Retry pattern (in each notebook):**

```python
import tenacity

@tenacity.retry(
    wait=tenacity.wait_exponential_jitter(initial=2, max=120, jitter=15),
    stop=tenacity.stop_after_attempt(3),
    retry=tenacity.retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
    before_sleep=lambda retry_state: print(f"Retry {retry_state.attempt_number} after error: {retry_state.outcome.exception()}"),
)
def execute_with_retry(func, *args, **kwargs):
    return func(*args, **kwargs)
```

**Pipeline rollback (saga compensation):**

When a mid-pipeline failure leaves partial state, the On Failure branch runs compensation:

```python
# Compensation table — ordered by reverse execution
PIPELINE_COMPENSATION = {
    "AILayer_failed": [
        "DELETE FROM flukebi_Gold.kpi_row_counts WHERE pipeline_run_id = '{run_id}'",
        # Gold data is still valid — don't roll it back
    ],
    "Gold_failed": [
        "DROP TABLE IF EXISTS flukebi_Gold.{app}_temp",
        # Silver data is still valid — don't roll it back
    ],
    "Silver_failed": [
        "DROP TABLE IF EXISTS flukebi_Silver.{app}_temp",
        # Bronze data is still valid — keep for re-run
    ],
    "Bronze_failed": [
        # Nothing to compensate — source extraction failed cleanly
    ],
}

def compensate(spark, failed_stage, run_id, app):
    """Run compensation queries for a failed pipeline stage."""
    queries = PIPELINE_COMPENSATION.get(f"{failed_stage}_failed", [])
    for q in queries:
        resolved = q.format(run_id=run_id, app=app)
        print(f"Compensating: {resolved}")
        spark.sql(resolved)
```

**Idempotency verification:** Every notebook starts with a check — if the output already exists for this run, skip execution:

```python
def check_idempotent(spark, target_table, run_id_col, current_run_id):
    """Check if this run has already been processed. Returns True if already done."""
    try:
        existing = spark.sql(
            f"SELECT COUNT(*) as cnt FROM {target_table} WHERE {run_id_col} = '{current_run_id}'"
        ).collect()[0]["cnt"]
        if existing > 0:
            print(f"Idempotent check: {target_table} already has {existing} rows for run {current_run_id}. Skipping.")
            return True
    except Exception:
        pass  # Table doesn't exist yet
    return False
```

### Step 7: Existing UBI Stream Integration

If `requirements.pipeline.existing_ubi_streams[]` is populated:

1. Read the existing stream's ADF pipeline structure
2. Extend (don't replace) the existing master pipeline with new activities
3. Reference existing Bronze/Silver tables where applicable
4. Add new Gold views and AI Layer notebooks alongside existing ones
5. Reuse existing linked services and Databricks connections

If empty: create all pipelines and notebooks from scratch.

### Step 8: Status Control Setup

Create or extend the Azure SQL metadata tables:

```sql
-- Status control table (if not exists)
IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'StatusControl')
CREATE TABLE StatusControl (
    Id INT IDENTITY(1,1) PRIMARY KEY,
    StreamName NVARCHAR(100),
    SubStream NVARCHAR(100),
    Status NVARCHAR(50),
    StartTime DATETIME2,
    EndTime DATETIME2,
    RowCount BIGINT,
    ErrorMessage NVARCHAR(MAX)
)
```

### Step 9: Pipeline Validation

Before presenting to the user:

1. **ADF validation:** Dry-run the pipeline JSON (validate linked services, activities, parameters)
2. **Notebook syntax:** Parse each notebook for Python/SQL syntax errors
3. **Contract coverage:** Verify every field in `requirements.pipeline` has a corresponding pipeline component
4. **Template check:** Verify all generated notebooks match the FULL template for the selected archetype

### Step 10: Present Report and Gate

```
PIPELINE REPORT — {project_name}
═══════════════════════════════════

Archetype: {archetype}
Template Status: FULL (all archetypes production-ready)

ADF Pipeline: PL_{app}_Master
  Activities: {count}
  Sources: {source_list}
  Trigger: {trigger_type} ({schedule})

Databricks Notebooks:
| # | Notebook | Layer | Status | Key Logic |
|---|----------|-------|--------|-----------|
| 1 | Bronze_{app}_{source} | Bronze | FULL | {bronze_strategy} |
| 2 | Silver_{app} | Silver | FULL | {silver_transforms} |
| 3 | Gold_{app} | Gold | FULL | {gold_output} |
| 4 | AILayer_{app} | AI | FULL | {ai_layer_processing} |
| 5 | Publish_AISearch_{app} | Publish | FULL | Vector index push |

Data Flow:
  {source} → Bronze ({strategy}) → Silver ({transforms}) → Gold ({output}) → AI Layer ({processing}) → {targets}
```

Update state: `phases.pipeline = "completed"`, `artifacts.notebooks`, `artifacts.adf_pipeline`

Ask:
> **GATE: Phase 2 Data Pipelines complete.** {count} notebooks + 1 ADF pipeline generated. Shall I proceed to Phase 3 (AI Setup)?

---

## Pipeline Anti-Patterns (NEVER Do These)

1. **NEVER hard-code connection strings in notebooks.** Use `dbutils.secrets.get(scope="{app}", key="{secret}")` or widget parameters.
2. **NEVER use `INSERT INTO` for Silver/Gold tables.** Always use `MERGE` or `CREATE OR REPLACE` to ensure idempotency.
3. **NEVER skip status_control logging.** Every pipeline run must pre-log and post-log for audit trail.
4. **NEVER generate notebooks without widget parameters.** All notebooks must accept `StreamName`, `SubStream`, and `Database` as Databricks widgets for parameterized execution.
5. **NEVER create notebooks outside `/Shared/{app}/`.** All project notebooks live in the project's shared folder.
6. **NEVER modify existing UBI stream notebooks.** When extending existing streams, create NEW notebooks alongside existing ones. Never edit `Refresh_DimProduct.py` or similar.
7. **NEVER generate incomplete templates.** Every notebook template must include full production logic for the selected archetype. No placeholder or TODO markers in generated output.
8. **NEVER skip the archetype dispatcher.** Even if the user says "just build RAG," read the archetype from state.json and dispatch through the switch. This ensures contract integrity.
9. **NEVER skip data quality gates between layers.** Every Bronze→Silver, Silver→Gold, Gold→AI Layer transition must pass a quality gate. Skipping gates lets corrupted data cascade silently through the pipeline.
10. **NEVER use `overwrite` mode for production Gold tables.** Use MERGE or CREATE OR REPLACE. Overwrite drops the table and recreates it — any downstream queries hitting the table during the write window get errors or empty results.
11. **NEVER retry infinitely on API rate limits.** Use `tenacity` with `stop_after_attempt(3)` and `wait_exponential_jitter`. Infinite retries compound rate limit pressure and can trigger account-level throttling.
12. **NEVER assume notebook idempotency without checking.** Every notebook must verify whether the current run has already been processed before executing. Re-running without this check creates duplicate data.

## Error Recovery

| Error | Recovery |
|-------|---------|
| Databricks workspace not accessible | Verify token/credential, check UBI subscription access |
| ADF linked service auth failure | Check Key Vault secret, verify service principal |
| Bronze notebook fails on source data | Check source connectivity, validate extraction query |
| Silver notebook type-casting errors | Review schema map, add SAFE_CAST fallbacks |
| AI Layer embedding API rate limit | Implement batch retry with exponential backoff |
| Status control SQL connection failure | Verify Azure SQL access, check firewall rules |
| Quality gate fails (row_count_drift) | Check source for data loss, compare to previous run counts, investigate upstream |
| Quality gate fails (pk_uniqueness) | Check Silver dedup logic, verify JOIN conditions not producing fan-out |
| Quality gate fails (null_rate) | Check source data, verify type-casting in Silver, add COALESCE fallbacks |
| Pipeline timeout (ADF) | Increase timeout, check for data skew, add repartition before heavy ops |
| Delta MERGE conflict | Check for concurrent writes, add retry with jitter, verify merge predicate |
| Compensation fails during rollback | Manual cleanup required — check audit log for partial state, drop temp tables |
