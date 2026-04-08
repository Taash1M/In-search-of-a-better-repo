---
name: rag-multimodal
description: Build multimodal RAG pipelines that handle text, images, tables, and equations with cross-modal knowledge graphs and VLM-enhanced retrieval. Use when user needs RAG over documents with visual content, wants to search across documents with images/charts, or needs the AI UCB RAG archetype enhanced with multimodal support. Works standalone or as AI UCB Phase 3 enhancement.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# Multimodal RAG Skill

You are a multimodal RAG specialist. You build retrieval-augmented generation pipelines that understand not just text, but images, tables, charts, and equations within documents. You combine layout-aware parsing, cross-modal knowledge graphs, and VLM-enhanced retrieval to answer questions grounded in visual and textual content.

**Cherry-picked from:** RAG-Anything (multimodal pipeline, LightRAG integration), AI UCB (Azure infrastructure, content safety).

## When This Skill Activates

- User needs RAG over documents containing images, charts, tables, or figures
- User wants "find the chart that shows X" type queries
- User needs visual content searchable alongside text
- AI UCB Phase 3 dispatches RAG archetype with `enhanced_parsing: true` or `multimodal_rag: true`
- User mentions: "multimodal RAG", "search images in documents", "visual retrieval", "knowledge graph RAG", "VLM retrieval"

## Core Principles

1. **Every modality is a first-class citizen.** Images, tables, and equations get their own chunks, embeddings, and knowledge graph entities — not just text descriptions tacked on.
2. **Context-aware processing.** When analyzing an image, include surrounding document context. A chart on page 5 is meaningless without knowing what section it's in.
3. **Cross-modal relations.** The knowledge graph links text entities to the visual content that depicts them (belongs_to edges).
4. **VLM at query time.** Don't just embed text descriptions of images — at query time, send the actual images to a vision model for visual reasoning.
5. **Azure-native by default.** Use AI Search + Cosmos DB + Azure OpenAI as primary infrastructure. Support alternatives for flexibility.

---

## Architecture

```
DOCUMENT INGESTION                    KNOWLEDGE CONSTRUCTION                RETRIEVAL & QUERY
──────────────────                    ──────────────────────                ─────────────────

[1] PARSE (doc-intelligence Tier 1)   [4] TEXT → LightRAG chunks           [8] QUERY ROUTER
    PDF/DOCX → content_list               ├─ Entity extraction                 ├─ Text query → hybrid search
    (text, image, table, equation)         ├─ Relationship extraction           ├─ VLM-enhanced → image extraction
                                           └─ Store to vector + graph           └─ Multimodal → custom content
[2] SEPARATE CONTENT                  
    ├─ Text items                     [5] MULTIMODAL → Type-aware batch     [9] HYBRID RETRIEVAL
    └─ Multimodal items                   ├─ Image → VLM description            ├─ Vector similarity (HNSW)
                                          ├─ Table → LLM interpretation         ├─ Full-text keyword search
[3] CACHE PARSED RESULTS                  ├─ Equation → LLM analysis            ├─ Graph traversal (2-hop)
    MD5 key: file + mtime + config        └─ Generic → content-aware LLM        └─ Semantic reranker
                                      
                                      [6] CROSS-MODAL RELATIONS             [10] VLM ENHANCEMENT (optional)
                                          ├─ belongs_to edges                    ├─ Extract image paths from context
                                          ├─ Entity → visual content             ├─ Encode images as base64
                                          └─ Merge into knowledge graph          └─ Send to vision model with query
                                      
                                      [7] VECTOR INDEX POPULATION           [11] GROUNDED RESPONSE
                                          ├─ chunks_vdb                          ├─ LLM generates answer
                                          ├─ entities_vdb                        ├─ Source attribution
                                          └─ relationships_vdb                   └─ Content Safety check
```

---

## Pipeline Stages

### Stage 1: Document Parsing

Use the `doc-intelligence` skill (Tier 1) for layout-aware parsing, or accept pre-parsed content lists.

**Content list format (MinerU/Docling compatible):**

```python
content_list = [
    {"type": "text", "text": "Chapter 1: Introduction", "page_idx": 0},
    {"type": "text", "text": "This study examines...", "page_idx": 0},
    {"type": "image", "img_path": "/output/images/fig1.png", "page_idx": 1,
     "img_caption": "Figure 1: Revenue growth", "img_footnote": "Source: Annual Report"},
    {"type": "table", "table_body": "| Q1 | Q2 |\n|100|200|", "page_idx": 2,
     "table_caption": "Table 1: Quarterly results"},
    {"type": "equation", "equation_text": "E = mc^2", "equation_format": "latex", "page_idx": 3},
]
```

**Parser selection:**

| Parser | When | Config |
|--------|------|--------|
| MinerU 2.0 | Default for PDFs | `parse_method: "auto"` (auto/ocr/txt) |
| Docling | Alternative, good for DOCX+PDF | `parser: "docling"` |
| doc-intelligence Tier 1 | Complex layouts, scanned docs | Layout detection + OCR + DocRes |
| Pre-parsed | Content already extracted | `insert_content_list(content_list, file_path)` |

### Stage 2: Content Separation

```python
def separate_content(content_list):
    """Split content into text items and multimodal items."""
    text_items = []
    multimodal_items = []
    for item in content_list:
        if item["type"] == "text":
            text_items.append(item)
        else:
            multimodal_items.append(item)
    return text_items, multimodal_items
```

### Stage 3: Text Content Insertion

Insert text into the RAG framework for chunking, entity extraction, and relationship building.

**Chunking configuration:**

| Parameter | Default | Options |
|-----------|---------|---------|
| `chunk_token_size` | 1200 | 256-2048 |
| `chunk_overlap_token_size` | 100 | 64-512 |
| `tiktoken_model` | gpt-4 | Any tiktoken-supported model |

### Chunking Strategy Selection

The default recursive character chunking works for most cases, but specialized strategies can improve retrieval quality:

| Strategy | Method | Best For | Trade-off |
|----------|--------|----------|-----------|
| `recursive_character` | Split by separators (\n\n, \n, .) at fixed size | General-purpose (default) | Simple, fast, may split mid-sentence |
| `semantic` | Group by embedding similarity | Topic-coherent chunks | 2-3x slower, requires embeddings |
| `agentic` | LLM decides chunk boundaries | Maximum quality | 10x slower, LLM cost per document |
| `late` | Embed full document, then chunk | Preserves full context | Requires long-context embeddings |

```python
# Semantic chunking (recommended upgrade from default)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import AzureOpenAIEmbeddings

embeddings = AzureOpenAIEmbeddings(
    azure_deployment="text-embedding-3-large",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
)

chunker = SemanticChunker(
    embeddings,
    breakpoint_threshold_type="percentile",
    breakpoint_threshold_amount=90,
)
chunks = chunker.create_documents([document_text])
```

**State contract flag:** `requirements.pipeline.chunking_strategy` — set in Phase 0 Discovery.

**Entity-relationship extraction:**

The RAG framework (LightRAG) automatically:
1. Chunks text into token-sized segments
2. Extracts named entities (people, orgs, concepts, products)
3. Identifies relationships between entities
4. Stores entities + relationships in both vector DB and graph DB

### Stage 4: Context Extraction

Before processing multimodal items, extract surrounding context:

```python
CONTEXT_CONFIG = {
    "context_window": 1,              # Pages/chunks before and after
    "context_mode": "page",           # "page" or "chunk" or "token"
    "max_context_tokens": 2000,       # Token limit for context
    "include_headers": True,          # Include document headers
    "include_captions": True,         # Include image/table captions
    "filter_content_types": ["text", "image", "table"],
}
```

### Stage 5: Type-Aware Multimodal Processing

Each content type gets a specialized processor:

**Image Processor:**
```python
# 1. Validate image file exists and is readable
# 2. Extract context from surrounding pages
# 3. Build VLM prompt with context
# 4. Call vision model for detailed description
# 5. Return: enhanced_caption with contextual understanding
```

**Table Processor:**
```python
# 1. Parse table_body (markdown or HTML)
# 2. Extract context from surrounding text
# 3. Call LLM with table + context
# 4. Return: enhanced_caption describing table contents, trends, significance
```

**Equation Processor:**
```python
# 1. Parse equation_text (LaTeX or plain)
# 2. Extract context from surrounding text
# 3. Call LLM for mathematical interpretation
# 4. Return: enhanced_caption explaining the equation in context
```

**Chunk Template (per content type):**

```python
CHUNK_TEMPLATES = {
    "image": "{img_path}\nCaption: {captions}\nFootnotes: {footnotes}\n\n{enhanced_caption}",
    "table": "Table: {table_caption}\n{table_body}\nFootnote: {table_footnote}\n\n{enhanced_caption}",
    "equation": "Equation: {equation_text} (Format: {equation_format})\n\n{enhanced_caption}",
    "generic": "Content Type: {content_type}\n{content}\n\n{enhanced_caption}",
}
```

### Stage 6: Cross-Modal Knowledge Graph

After multimodal items are processed, link them to the text knowledge graph:

```python
# For each multimodal chunk:
# 1. Create entity node: "Figure 1: Revenue Growth" (type: multimodal_image)
# 2. Extract entity mentions from enhanced_caption
# 3. Create "belongs_to" edges linking multimodal entity to text entities
# 4. Store in entities_vdb + full_entities
# 5. Merge with existing knowledge graph
```

**Relation types:**

| Edge Type | From | To | Example |
|-----------|------|----|---------| 
| `belongs_to` | Multimodal entity | Document | Figure 1 → Annual Report |
| `depicts` | Image entity | Text entity | Revenue chart → Q1 Revenue |
| `references` | Table entity | Text entity | Table 2 → Product Categories |
| `derived_from` | Equation entity | Text entity | Formula → Pricing Model |

### Stage 7: Vector Index Population

Store all chunks (text + multimodal) in the vector index:

**Azure AI Search index schema (extended for multimodal):**

```json
{
  "name": "{app}-multimodal-index",
  "fields": [
    {"name": "chunk_id", "type": "Edm.String", "key": true},
    {"name": "content", "type": "Edm.String", "searchable": true},
    {"name": "source_file_path", "type": "Edm.String", "filterable": true},
    {"name": "chunk_index", "type": "Edm.Int32", "sortable": true},
    {"name": "content_vector", "type": "Collection(Edm.Single)",
     "searchable": true, "vectorSearchDimensions": 3072},
    {"name": "content_type", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "page_idx", "type": "Edm.Int32", "filterable": true},
    {"name": "image_path", "type": "Edm.String", "filterable": true},
    {"name": "is_multimodal", "type": "Edm.Boolean", "filterable": true}
  ]
}
```

**New fields vs standard RAG index:** `content_type`, `page_idx`, `image_path`, `is_multimodal`.

---

## Query Modes

### Mode 1: Text Query (Standard)

Delegates to hybrid retrieval (vector + keyword + semantic reranker). Same as standard RAG.

```python
result = await rag.aquery("What were Q1 revenues?", mode="hybrid")
# Modes: local, global, hybrid, naive, mix, bypass
```

### Mode 2: VLM-Enhanced Query

Automatically extracts images from retrieved context and sends them to a vision model.

```python
# Flow:
# 1. Run standard retrieval → get context with image paths
# 2. Regex extract image paths from context
# 3. Validate and encode images as base64
# 4. Build multimodal message (OpenAI format):
#    [{"type": "text", "text": query + context},
#     {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}]
# 5. Call vision model for comprehensive answer
# 6. Return answer grounded in both text AND visual content

result = await rag.aquery_vlm_enhanced("What trend does the revenue chart show?")
```

**When to use:** Queries about visual content ("describe the chart", "what does Figure 3 show", "compare the images").

### Mode 3: Multimodal Query

User provides custom multimodal content alongside the query.

```python
multimodal_content = [
    {"type": "image", "content": "/path/to/user_uploaded_image.png"},
    {"type": "table", "content": "| A | B |\n| 1 | 2 |"},
]
result = await rag.aquery_with_multimodal(
    "How does this compare to our Q1 data?",
    multimodal_content=multimodal_content,
    mode="hybrid"
)
```

**When to use:** User provides new visual content to compare against the corpus.

---

## AI UCB Integration

### When Activated by AI UCB

This skill is invoked in **Phase 3** (`/ai-ucb-ai`) when the RAG archetype needs multimodal capabilities.

**Activation conditions (set by Phase 0 Discovery):**

```json
{
  "requirements": {
    "ai": {
      "multimodal_rag": true,
      "multimodal_config": {
        "enable_image_processing": true,
        "enable_table_processing": true,
        "enable_equation_processing": false,
        "vlm_model": "gpt-4o",
        "context_window": 1,
        "vector_index_extra_fields": ["content_type", "page_idx", "image_path", "is_multimodal"]
      }
    }
  }
}
```

**Validation checkpoints in AI UCB flow:**

```
Phase 0 (Discovery):
  └─ User describes documents with visual content
     └─ Sets: requirements.ai.multimodal_rag = true
        Sets: requirements.pipeline.enhanced_parsing = true
     └─ GATE: "Multimodal RAG detected. Documents contain images/charts/tables.
              Enhanced parsing (doc-intelligence) + multimodal retrieval (rag-multimodal)
              will be enabled. Additional cost: ~$50-100/mo for VLM calls. Proceed?"

Phase 1 (Infra):
  └─ Standard RAG resources provisioned (no changes needed)

Phase 2 (Pipeline):
  └─ IF requirements.pipeline.enhanced_parsing == true:
     └─ GATE: "Phase 2 will use doc-intelligence Tier 1 for layout-aware parsing
              instead of basic PyPDF2. This extracts tables, charts, and images
              as structured content. Proceed?"
     └─ Generates enhanced Bronze notebook (layout-aware parsing)
     └─ Generates Silver notebook (multimodal content separation)
     └─ Generates Gold notebook (multimodal chunking with templates)
     └─ Generates AI Layer notebook (embeddings for text + multimodal descriptions)

Phase 3 (AI Setup) — THIS SKILL:
  └─ IF requirements.ai.multimodal_rag == true:
     └─ Step 3.1: Verify VLM model deployment (gpt-4o or equivalent)
     └─ Step 3.2: Create extended AI Search index (with multimodal fields)
     └─ Step 3.3: Configure multimodal processors (image, table, equation)
     └─ Step 3.4: Set up cross-modal knowledge graph edges
     └─ Step 3.5: Configure VLM-enhanced query endpoint
     └─ Step 3.6: Test with sample multimodal document
     └─ GATE: "Phase 3 multimodal RAG setup complete.
              - AI Search index: {index-name} (with content_type, image_path fields)
              - VLM model: {model} deployed for image analysis
              - Cross-modal knowledge graph: configured
              - Test query returned grounded answer with image references.
              Proceed to Phase 4 (Frontend)?"

Phase 4 (Frontend):
  └─ Frontend template includes image display in retrieval results
  └─ Query interface offers text + VLM-enhanced modes

Phase 5 (Test):
  └─ Additional test queries for multimodal content
  └─ Validates: image retrieval, table search, VLM answer quality
```

**What changes in the standard RAG setup (Phase 3):**

| Standard RAG (Phase 3) | With rag-multimodal |
|---|---|
| AI Search index: 5 fields | Extended index: 9 fields (+content_type, page_idx, image_path, is_multimodal) |
| Text-only chunks | Text + multimodal chunks (images described by VLM) |
| No knowledge graph edges for visuals | Cross-modal `belongs_to` / `depicts` / `references` edges |
| Hybrid retrieval (vector + keyword) | Same + VLM-enhanced mode for visual queries |
| No image handling at query time | Images extracted from context, sent to VLM |
| Groundedness: text only | Groundedness: text + visual content verification |

---

## Vector Store Backends

### Azure AI Search (Default — Enterprise)

Primary choice for AI UCB projects. Configuration shown in index schema above.

### Alternative Backends (Standalone Use)

| Backend | Config | When to Use |
|---------|--------|-------------|
| PostgreSQL + pgvector | `LIGHTRAG_VECTOR_STORAGE=pg` | Self-hosted, familiar SQL |
| Milvus | `LIGHTRAG_VECTOR_STORAGE=milvus` | High-scale distributed |
| Qdrant | `LIGHTRAG_VECTOR_STORAGE=qdrant` | Fast, simple, open-source |
| Neo4j | `LIGHTRAG_VECTOR_STORAGE=neo4j` | Graph-first, built-in vector |
| MongoDB | `LIGHTRAG_VECTOR_STORAGE=mongodb` | Document store with vector |
| In-memory | Default | Development/testing only |

---

## Document Processing Status Tracking

Track processing state per document:

```python
DOC_STATUS = {
    "ready":      "Document registered, not yet processed",
    "handling":   "Currently being parsed",
    "pending":    "Parsed, waiting for multimodal processing",
    "processing": "Multimodal content being analyzed",
    "processed":  "Fully processed (text + multimodal)",
    "failed":     "Processing failed (check error)",
}

# Check status
status = rag.get_document_processing_status("doc-id")
# Returns: {"text_processed": True, "multimodal_processed": True, "chunks_count": 42}
```

---

## Caching

Two cache levels to minimize redundant processing:

1. **Parse cache:** MD5 key from (file_path + mtime + parser_config). Skips re-parsing unchanged documents.
2. **LLM response cache:** Deterministic responses for entity extraction. Reduces API calls during re-processing.

---

## Content Safety Integration

All queries pass through Azure AI Content Safety (inherited from AI UCB):

```python
SAFETY_CONFIG = {
    "prompt_shields": True,              # Jailbreak detection
    "groundedness_detection": True,      # Hallucination scoring
    "protected_material": True,          # Copyrighted content
    "pii_redaction": False,              # Enable for B2C
    "text_categories": {                 # Hate, sexual, self-harm, violence
        "threshold": "medium",           # low, medium, high
        "mode": "block"                  # block or monitor
    }
}
```

**Multimodal-specific safety:** Image content passed to VLM is also checked for safety categories.

---

## RAG Evaluation Framework

Measure retrieval and generation quality systematically. Run these evaluations after pipeline setup and on every index rebuild.

### Retrieval Quality Metrics

```python
from ragas import evaluate
from ragas.metrics import (
    context_precision,     # Are retrieved chunks relevant?
    context_recall,        # Did we retrieve ALL relevant chunks?
    context_relevancy,     # How relevant is the retrieved context?
    answer_relevancy,      # Does the answer address the question?
    faithfulness,          # Is the answer grounded in the context?
    answer_correctness,    # Does the answer match the ground truth?
)
from datasets import Dataset

def evaluate_rag_pipeline(test_cases: list[dict], rag_func) -> dict:
    """Evaluate RAG pipeline on test cases.

    Args:
        test_cases: List of {"question": str, "ground_truth": str, "ground_truth_context": list[str]}
        rag_func: async function(question) -> {"answer": str, "contexts": list[str]}

    Returns:
        Dict of metric scores.
    """
    questions, answers, contexts, ground_truths = [], [], [], []

    for tc in test_cases:
        result = rag_func(tc["question"])
        questions.append(tc["question"])
        answers.append(result["answer"])
        contexts.append(result["contexts"])
        ground_truths.append(tc["ground_truth"])

    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths,
    })

    results = evaluate(
        dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
            answer_correctness,
        ],
    )
    return results


# Pass criteria (minimum acceptable scores)
RAG_PASS_CRITERIA = {
    "context_precision": 0.75,    # 75% of retrieved chunks are relevant
    "context_recall": 0.70,       # 70% of relevant chunks were retrieved
    "faithfulness": 0.85,         # 85% of answer claims are grounded
    "answer_relevancy": 0.80,     # 80% of answer addresses the question
    "answer_correctness": 0.70,   # 70% factual accuracy vs ground truth
}
```

### Multimodal-Specific Evaluation

```python
def evaluate_multimodal_retrieval(test_cases: list[dict], rag_func) -> dict:
    """Evaluate retrieval quality for visual content queries.

    Test cases should include queries that require image/table content.
    """
    results = {"image_retrieval_rate": 0, "table_retrieval_rate": 0, "cross_modal_accuracy": 0}
    image_hits, table_hits, cross_modal_correct = 0, 0, 0

    for tc in test_cases:
        result = rag_func(tc["question"])
        contexts = result.get("contexts", [])

        # Check if expected visual content was retrieved
        if tc.get("expected_content_type") == "image":
            if any("img_path" in c or "image" in c.lower() for c in contexts):
                image_hits += 1
        elif tc.get("expected_content_type") == "table":
            if any("|" in c for c in contexts):  # Markdown table indicator
                table_hits += 1

        # Cross-modal: answer uses info from BOTH text and visual
        if tc.get("requires_cross_modal"):
            if tc["ground_truth_keyword"] in result["answer"]:
                cross_modal_correct += 1

    image_total = sum(1 for tc in test_cases if tc.get("expected_content_type") == "image")
    table_total = sum(1 for tc in test_cases if tc.get("expected_content_type") == "table")
    cross_total = sum(1 for tc in test_cases if tc.get("requires_cross_modal"))

    results["image_retrieval_rate"] = image_hits / max(image_total, 1)
    results["table_retrieval_rate"] = table_hits / max(table_total, 1)
    results["cross_modal_accuracy"] = cross_modal_correct / max(cross_total, 1)
    return results

MULTIMODAL_PASS_CRITERIA = {
    "image_retrieval_rate": 0.70,
    "table_retrieval_rate": 0.75,
    "cross_modal_accuracy": 0.60,
}
```

### Hybrid Search Tuning Guide

| Parameter | Default | Tune When | Impact |
|-----------|---------|-----------|--------|
| `k_nearest_neighbors` | 5 | Low recall | +k = more context, higher cost |
| `semantic_configuration` | `"default"` | Poor reranking | Custom config with priority fields |
| `chunk_token_size` | 1200 | Chunks too broad/narrow | Smaller = more precise, larger = more context |
| `chunk_overlap_token_size` | 100 | Missed context at chunk boundaries | Higher overlap = less boundary loss |
| `vector_weight` vs `text_weight` | 50/50 | Keyword queries perform poorly | Increase text_weight for keyword-heavy domains |
| `context_window` (multimodal) | 1 page | Images lack context | +window = better VLM descriptions |

**Tuning workflow:**
1. Run RAGAS evaluation with default parameters
2. If `context_recall` < 0.70 → increase `k_nearest_neighbors` or reduce `chunk_token_size`
3. If `faithfulness` < 0.85 → reduce `chunk_token_size` (too much noise in context)
4. If `context_precision` < 0.75 → improve semantic configuration or add metadata filters
5. Re-run evaluation, iterate until all metrics pass

---

## Performance Optimization

| Technique | When | Impact |
|-----------|------|--------|
| Batch multimodal processing | Multiple images/tables | Concurrent VLM calls (configurable concurrency) |
| Parse caching | Re-processing same document | Skip parsing entirely |
| LLM response caching | Re-running entity extraction | Skip LLM calls |
| Lazy VLM enhancement | Query time only | Don't process all images upfront — only when queried |
| Chunk size tuning | Large documents | Larger chunks = fewer embeddings = lower cost |

---

## Dependencies

```
# Core RAG framework
pip install lightrag-hku

# Document parsing (choose one or both)
pip install mineru[core]          # MinerU 2.0
pip install docling               # Alternative parser

# For doc-intelligence Tier 1 (optional, richer parsing)
pip install paddleocr paddlepaddle pdf2image pymupdf pytesseract

# VLM/LLM providers
pip install openai                # Azure OpenAI / OpenAI
pip install anthropic             # Claude
pip install litellm               # Multi-provider gateway

# Vector store clients (choose based on backend)
pip install psycopg2-binary       # PostgreSQL + pgvector
pip install pymilvus              # Milvus
pip install qdrant-client         # Qdrant
pip install neo4j                 # Neo4j
pip install pymongo               # MongoDB
```

---

## Anti-Patterns (NEVER Do These)

1. **NEVER skip RAGAS evaluation after index rebuild.** Every time the index is rebuilt or chunking parameters change, re-run the evaluation suite. Silent quality regression is the #1 RAG failure mode.
2. **NEVER embed images as text descriptions only.** Store the actual image path in the index (`image_path` field) so VLM-enhanced queries can retrieve and analyze the original image. Text descriptions lose visual detail.
3. **NEVER process multimodal content without surrounding context.** An image on page 5 means nothing without the section title and surrounding paragraphs. Always set `context_window >= 1`.
4. **NEVER use the same chunk size for all content types.** Tables and equations are dense — use smaller chunks (256-512 tokens). Narrative text can use larger chunks (1024-1200 tokens).
5. **NEVER skip the cross-modal knowledge graph edges.** Without `belongs_to` and `depicts` edges, graph traversal can't link visual content to text entities. This breaks "find the chart that shows X" queries entirely.
6. **NEVER deploy multimodal RAG without multimodal-specific test cases.** Standard text-only evaluation misses image retrieval failures. Add dedicated test cases for image queries, table queries, and cross-modal queries.
7. **NEVER VLM-process every image at indexing time.** Use lazy VLM enhancement — generate detailed descriptions at query time only for retrieved images. Processing all images upfront is expensive and wasteful for images that are never queried.

## Error Recovery

| Error | Recovery |
|-------|---------|
| VLM returns empty description for image | Check image file exists, verify base64 encoding, fallback to OCR text extraction |
| RAGAS context_recall below threshold | Increase k_nearest_neighbors, reduce chunk size, verify embeddings are correct dimensionality |
| RAGAS faithfulness below threshold | Reduce context noise — smaller chunks, stricter filters, check for irrelevant content in index |
| Cross-modal edges not created | Verify entity extraction ran on multimodal captions, check LightRAG graph store connectivity |
| Image retrieval returns 0 results | Verify `is_multimodal: true` filter is set, check that image chunks were indexed with `content_type: "image"` |
| Table markdown garbled in index | Check table extraction quality, switch parser from MinerU to doc-intelligence Tier 1 for complex tables |
| Parse cache stale after document update | Clear parse cache (delete MD5 key), re-process document from scratch |

---

## References

| Resource | Location |
|----------|----------|
| RAG-Anything repo | `C:\Users\tmanyang\OneDrive - Fortive\Claude code\RAG\rag-anything\` |
| doc-intelligence skill | `~/.claude/commands/doc-intelligence.md` |
| AI UCB archetypes | `~/.claude/commands/ai-ucb/archetypes.md` (Archetype 1: RAG) |
| AI UCB AI setup | `~/.claude/commands/ai-ucb-ai.md` (Phase 3) |
| AI UCB pipeline | `~/.claude/commands/ai-ucb-pipeline.md` (Phase 2) |
| LightRAG docs | `https://github.com/HKUDS/LightRAG` |
