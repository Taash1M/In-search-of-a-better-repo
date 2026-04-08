# AI Use Case Builder - Archetype Catalog

This reference defines all 8 AI solution archetypes supported by the Use Case Builder. Each archetype specifies the required Azure resources, data flow pattern, recommended models, frontend, data stores, and cost tier.

**Usage:** The orchestrator (`ai-use-case-builder.md`) and discovery sub-skill (`ai-ucb-discover.md`) read this file to match user intent to an archetype and generate the correct resource map.

---

## Archetype Decision Tree

Use this tree to map natural language input to the correct archetype. When ambiguous, ask the clarification question.

```
User describes their use case
    │
    ├─ Mentions: documents, search, Q&A, chatbot, knowledge base, product info, FAQs
    │   ├─ Data is structured documents (PDFs, Word, SharePoint) → RAG
    │   ├─ Data has complex entity relationships → Knowledge Graph + AI
    │   └─ Needs multi-turn conversation with tool calling → Conversational Agent
    │
    ├─ Mentions: extract, parse, classify documents, invoices, forms, receipts
    │   └─ → Document Intelligence
    │
    ├─ Mentions: predict, forecast, classify, regression, anomaly, train model
    │   └─ → Predictive ML
    │
    ├─ Mentions: calls, transcripts, sentiment, voice, NLP, text mining, feedback
    │   └─ → Voice/Text Analytics
    │
    ├─ Mentions: multiple agents, orchestrate, coordinate, workflow, specialized bots
    │   └─ → Multi-Agent System
    │
    ├─ Mentions: images, video, visual inspection, defect detection, OCR on images
    │   └─ → Computer Vision
    │
    └─ Unclear
        └─ Ask: "What is the primary input data type?"
            ├─ Text documents → RAG or Document Intelligence
            ├─ Structured/tabular data → Predictive ML
            ├─ Audio/transcripts → Voice/Text Analytics
            ├─ Images/video → Computer Vision
            ├─ Graph/relationship data → Knowledge Graph + AI
            └─ Multiple types → Multi-Agent System
```

**Keyword-to-archetype mapping (for NL parsing):**

| Keywords | Archetype |
|----------|-----------|
| RAG, retrieval, search, Q&A, chatbot, knowledge base, documents, SharePoint, FAQ, product info | RAG |
| conversation, dialogue, multi-turn, tool use, function calling, assistant, agent | Conversational Agent |
| extract, parse, invoice, form, receipt, OCR, document intelligence, structured extraction | Document Intelligence |
| predict, forecast, classify, regression, anomaly, train, model, ML, machine learning, time series | Predictive ML |
| knowledge graph, relationships, entities, graph database, neo4j, gremlin, GraphRAG, ontology | Knowledge Graph + AI |
| voice, speech, transcript, sentiment, NLP, text analytics, call recording, feedback, VoC | Voice/Text Analytics |
| multi-agent, orchestrate, coordinate, specialized agents, workflow, crew, swarm | Multi-Agent System |
| image, video, vision, visual inspection, defect, classification, segmentation, object detection | Computer Vision |

---

## Archetype Selection Anti-Patterns (NEVER Do These)

1. **NEVER choose Conversational Agent when RAG is sufficient.** If the user just needs Q&A over documents with no tool calling or external actions, RAG is simpler, cheaper, and faster to build. Conversational Agent adds Foundry Agent Service, tool registration, and state management overhead.
2. **NEVER choose Multi-Agent when a single agent with tools works.** Multi-Agent is for genuinely distinct expertise domains that need separate context windows. If one agent with 3-5 tools solves the problem, use Conversational Agent instead.
3. **NEVER default to Knowledge Graph without entity-relationship data.** If the user's data is flat documents, RAG with good chunking outperforms a graph. Knowledge Graph shines when there are explicit entity types and relationships (customer→product→category).
4. **NEVER choose Predictive ML for rule-based classification.** If the business rules are known and finite (e.g., "if revenue > $1M, flag as enterprise"), use SQL logic in the Gold layer. ML is for patterns that can't be hand-coded.
5. **NEVER select Computer Vision when Document Intelligence handles it.** If the user needs to extract text/tables from PDFs or forms, Document Intelligence is purpose-built and cheaper. Computer Vision is for image classification, object detection, and visual inspection.
6. **NEVER assume single archetype when hybrid is needed.** If the user says "chatbot over product docs with related product recommendations," that's RAG + Knowledge Graph. Ask which is primary and build the primary archetype with the secondary as an extension.

## Hybrid Archetype Guidance

Some use cases require combining archetypes. When this happens:

| Combination | Primary | Secondary Extension | Example |
|-------------|---------|---------------------|---------|
| RAG + Knowledge Graph | RAG | Add graph store + GraphRAG retrieval | Product docs with relationship navigation |
| RAG + Conversational Agent | Conversational Agent | Add AI Search retrieval as a tool | Helpdesk bot that searches docs + creates tickets |
| Knowledge Graph + Predictive ML | Knowledge Graph | Add ML scoring to graph entities | Customer graph with churn prediction per node |
| Voice/Text + RAG | Voice/Text Analytics | Add AI Search for context retrieval | Call analytics with knowledge-grounded summaries |

**Build strategy for hybrids:**
1. Build the primary archetype through all 8 phases
2. Extend with the secondary archetype's specific resources in a follow-up pass
3. State.json `archetype` field uses format: `"rag+knowledge-graph"` (primary first)

## Mid-Build Archetype Change

If the user wants to change archetypes after Phase 0:
1. **Before Phase 1 (infra not provisioned):** Safe to change. Update `state.json.archetype` and re-run Phase 0.
2. **After Phase 1 (infra exists):** Warn that resources may need to be deleted and re-provisioned. Offer to keep compatible resources and add/remove the delta.
3. **After Phase 2+ (data pipelines exist):** Strongly discourage. Pipelines are archetype-specific. Recommend starting a new project.

---

## Archetype 1: RAG (Retrieval-Augmented Generation)

**Description:** Answers questions by retrieving relevant chunks from a document corpus and generating responses grounded in source material.

**Fluke Examples:** Pulse Sales (Account 360), TechMentor

### Required Azure Resources

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Resource Group | - | AI | Container for all resources |
| AI Services | Azure AI Services | AI | LLM inference + embeddings |
| AI Search | Azure AI Search (Standard) | AI | Vector + hybrid + semantic search |
| Cosmos DB | Azure Cosmos DB (NoSQL) | AI | Conversation history, app state |
| App Service | Azure App Service (Linux) | AI | Web frontend hosting |
| Function App | Azure Functions (Flex) | AI | Event processing, API endpoints |
| Key Vault | Azure Key Vault | AI | Secrets management |
| Log Analytics | Azure Monitor | AI | Logging and monitoring |
| App Insights | Application Insights | AI | Application telemetry |
| Storage Account | ADLS Gen2 | AI | Document storage, embeddings cache |
| Content Safety | Azure AI Content Safety | AI | Prompt shields, groundedness |
| Front Door | Azure Front Door | AI | Multi-region load balancing, WAF |

**Split-model additions (data engineering in UBI):**

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Databricks | Azure Databricks | UBI | Document processing, chunking, embeddings |
| ADF Pipeline | Azure Data Factory | UBI | Orchestration of ingestion pipeline |
| ADLS Gen2 | Azure Data Lake Storage | UBI | Medallion layers (Bronze/Silver/Gold) |

### Data Flow

```
Source Documents (SharePoint, ADLS, APIs, SFTP)
    │
    ▼
Bronze: Raw document ingestion (PDF, DOCX, HTML, CSV)
    │   [Databricks notebook: schema-on-read, metadata extraction]
    ▼
Silver: Text extraction, cleaning, deduplication
    │   [Databricks notebook: text normalization, entity tagging]
    ▼
Gold: Chunked documents with metadata
    │   [Databricks notebook: semantic chunking, overlap, metadata enrichment]
    ▼
AI Layer: Embeddings → Vector Index
    │   [Databricks notebook: text-embedding-3-large batch processing]
    │   [Output: AI Search index with vector + text + metadata fields]
    ▼
AI Application: LLM + Retrieval + Content Safety → Frontend
```

### Recommended Configuration

| Parameter | Default | Options |
|-----------|---------|---------|
| AI Model | gpt-4.1 | gpt-4.1, gpt-5, claude-opus-4-6 |
| Embedding Model | text-embedding-3-large | text-embedding-3-large, text-embedding-3-small |
| Embedding Dimensions | 3072 | 3072, 1536 (small) |
| Vector Store | AI Search (Standard) | AI Search, Cosmos DB Vector |
| Chunk Size | 512 tokens | 256-2048 |
| Chunk Overlap | 128 tokens | 64-512 |
| Chunking Strategy | Semantic (paragraph-aware) | semantic, fixed, sliding-window |
| Retrieval | Hybrid (vector + full-text + semantic reranker) | hybrid, vector-only, keyword-only |
| Frontend | Copilot Studio | Copilot Studio, Streamlit, React, API-only |
| Content Safety | Block mode (B2C) / Monitor mode (B2B) | block, monitor, custom |
| **Multimodal RAG** | false | true (enables /rag-multimodal: cross-modal graph, VLM retrieval, extended index) |
| **Enhanced Parsing** | false | true (enables /doc-intelligence Tier 1: layout-aware OCR, DocRes, VLM chart extraction) |

**Multimodal RAG option:** When documents contain images, diagrams, charts, or equations alongside text, set `multimodal_rag: true` in Phase 0. This activates the `/rag-multimodal` skill pipeline: layout-aware parsing → cross-modal separation → type-aware chunking → extended AI Search index (9 fields) → VLM-enhanced retrieval at query time. Cost increase: ~$100-200/mo for VLM inference.

**Enhanced Parsing option:** When documents have complex layouts (multi-column, scanned, tables) but no image-based Q&A is needed, set `enhanced_parsing: true`. This activates `/doc-intelligence` Tier 1 for Bronze-layer parsing only — better text extraction without the full multimodal pipeline.

### Cost Tier: Medium ($600-1,200/mo dev), Medium-High with multimodal ($800-1,400/mo dev)

---

## Archetype 2: Conversational Agent

**Description:** Multi-turn dialogue agent with tool calling capabilities. Can access APIs, databases, and external services to complete tasks on behalf of users.

**Fluke Examples:** Pulse Unified UI (multi-tool agent)

### Required Azure Resources

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Resource Group | - | AI | Container |
| AI Services | Azure AI Services | AI | LLM with function calling |
| AI Foundry Project | Microsoft Foundry | AI | Agent Service, tool registration |
| Cosmos DB | Azure Cosmos DB (NoSQL) | AI | Conversation state, tool results cache |
| App Service | Azure App Service | AI | Web frontend |
| Function App | Azure Functions (Flex) | AI | Tool implementations |
| Logic App | Azure Logic App | AI | Workflow triggers (email, SharePoint, Teams) |
| Key Vault | Azure Key Vault | AI | Secrets |
| App Insights | Application Insights | AI | Telemetry |
| Content Safety | Azure AI Content Safety | AI | Guardrails |
| Front Door | Azure Front Door | AI | Multi-region |

### Data Flow

```
User Message → Agent Framework (Foundry Agent Service)
    │
    ├─ Tool Selection (function calling)
    │   ├─ API calls (Function App)
    │   ├─ Database queries (Cosmos DB, SQL)
    │   ├─ Document retrieval (AI Search)
    │   └─ External integrations (Logic App)
    │
    ├─ Context Assembly (conversation history + tool results)
    │
    └─ Response Generation (LLM + Content Safety) → User
```

### Recommended Configuration

| Parameter | Default | Options |
|-----------|---------|---------|
| AI Model | gpt-4.1 | gpt-4.1, gpt-5, claude-opus-4-6 |
| Agent Framework | Foundry Agent Service | Foundry, Semantic Kernel, custom |
| Conversation Store | Cosmos DB (NoSQL) | Cosmos DB, Redis |
| Frontend | Copilot Studio | Copilot Studio, React, Streamlit |
| Tool Auth | Managed Identity | Managed Identity, API Key |
| Session Timeout | 30 minutes | configurable |

### Cost Tier: Medium-High ($800-1,500/mo dev)

---

## Archetype 3: Document Intelligence

**Description:** Extracts structured data from unstructured documents — invoices, forms, receipts, contracts. Uses the `/doc-intelligence` skill with 3-tier architecture: Tier 1 (layout-aware parsing), Tier 2 (declarative extraction), Tier 3 (Azure AI Document Intelligence).

**Fluke Examples:** Invoice processing (potential)

### Required Azure Resources

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Resource Group | - | AI | Container |
| AI Document Intelligence | Azure AI Document Intelligence | AI | OCR + layout + extraction (Tier 3) |
| AI Services | Azure AI Services | AI | LLM for complex reasoning + VLM for charts |
| AI Search | Azure AI Search | AI | Extracted data indexing |
| Cosmos DB | Azure Cosmos DB (NoSQL) | AI | Extracted metadata store |
| Function App | Azure Functions (Flex) | AI | Document processing pipeline |
| Storage Account | ADLS Gen2 | AI | Document intake + results |
| Key Vault | Azure Key Vault | AI | Secrets |
| App Insights | Application Insights | AI | Telemetry |

**Split-model additions:**

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Databricks | Azure Databricks | UBI | Post-processing, validation, analytics |
| ADF Pipeline | Azure Data Factory | UBI | Batch document processing orchestration |
| ADLS Gen2 | ADLS | UBI | Medallion storage for extracted data |

### 3-Tier Architecture (via /doc-intelligence skill)

| Tier | When to Use | Key Capabilities |
|------|-------------|------------------|
| **Tier 1** — Layout-Aware Parsing | Complex layouts, scanned docs, multi-column PDFs | PaddleOCR PP-DocLayout_plus-L layout detection, dual OCR (PyTesseract + PaddleOCR PP-OCRv5), DocRes image restoration (6 tasks), VLM chart-to-table extraction, split table merging |
| **Tier 2** — Declarative Extraction | Structured data extraction from parsed text | 8 concept types (String, Boolean, Numerical, Date, Rating, JsonObject, Label, Aspect), reference tracing to paragraphs/sentences, justifications, ExtractionPipeline reusability |
| **Tier 3** — Azure AI Doc Intelligence | Standard forms/invoices, enterprise compliance | Prebuilt models (invoice, receipt, ID, W-2), custom-trained models, key-value pairs, tables, signatures |

**Tier selection** is set at Phase 0 via `requirements.pipeline.doc_intelligence_tier` (tier_1, tier_2, tier_3, or combined).

### Data Flow

```
Documents (PDF, images, scans)
    │
    ▼
Bronze: Layout-aware document ingestion (Tier 1)
    │   [Databricks: PaddleOCR layout detection, dual OCR, DocRes restoration]
    │   [Output: structured regions (text, tables, images, headers)]
    ▼
Silver: Structured extraction + validation (Tier 2 + Tier 3)
    │   [Tier 2: ContextGem-pattern declarative extraction → concepts + aspects]
    │   [Tier 3: Azure AI Doc Intelligence → key-value pairs, tables, entities]
    │   [Databricks: schema enforcement, business rules, cross-reference]
    ▼
Gold: Business-ready structured data
    │   [Views: aggregations, cross-reference, extraction confidence scores]
    ▼
AI Search Index + Cosmos DB → Application
```

### Recommended Configuration

| Parameter | Default | Options |
|-----------|---------|---------|
| Doc Intelligence Tier | tier_3 (Azure prebuilt) | tier_1, tier_2, tier_3, combined (tier_1+tier_2+tier_3) |
| Document Model | Prebuilt (invoice/receipt) | prebuilt, custom-trained (Tier 3 only) |
| AI Model | gpt-4.1 | For complex extraction reasoning |
| VLM Model | gpt-4.1 (vision) | For chart/diagram extraction (Tier 1) |
| OCR Engine | dual (PyTesseract + PaddleOCR) | pytesseract, paddleocr, dual (Tier 1) |
| Extraction Concepts | user-defined | 8 types: String, Boolean, Numerical, Date, Rating, JsonObject, Label, Aspect (Tier 2) |
| Output Format | JSON + searchable index | JSON, CSV, Cosmos DB |
| Frontend | Streamlit | Streamlit, React, Power Apps |

### Cost Tier: Low-Medium ($400-800/mo dev)

---

## Archetype 4: Predictive ML

**Description:** Traditional machine learning — classification, regression, forecasting, clustering, anomaly detection. Uses Databricks MLflow + Azure ML for training, tracking, and deployment.

**Fluke Examples:** Demand forecasting (potential), predictive maintenance (potential)

### Required Azure Resources

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Resource Group | - | AI or UBI | Container |
| Databricks | Azure Databricks | UBI | Training compute, feature engineering |
| Azure ML | Azure Machine Learning | AI | Model registry, endpoints, monitoring |
| ADLS Gen2 | Azure Data Lake Storage | UBI | Feature store, training data (Delta) |
| ADF Pipeline | Azure Data Factory | UBI | Feature pipeline orchestration |
| Function App | Azure Functions | AI | Inference API (real-time) |
| Key Vault | Azure Key Vault | AI | Secrets |
| App Insights | Application Insights | AI | Model performance monitoring |

**Optional:**

| Resource | Service | When |
|----------|---------|------|
| Fabric Lakehouse | Microsoft Fabric | Power BI Direct Lake reporting |
| Cosmos DB | Azure Cosmos DB | Real-time prediction caching |
| Streamlit App | App Service | Interactive model exploration |

### Data Flow

```
Source Systems (Oracle, APIs, SFTP, databases)
    │
    ▼
Bronze: Raw feature data ingestion
    │   [Databricks: schema-on-read, type preservation]
    ▼
Silver: Feature engineering, joins, aggregations
    │   [Databricks: window functions, lag features, normalization]
    ▼
Gold: Training datasets, feature store (Delta tables)
    │   [Databricks SQL: versioned feature sets]
    ▼
AI Layer: Model training (MLflow) → Model Registry (Azure ML)
    │   [Databricks: experiment tracking, hyperparameter tuning]
    ▼
Inference Endpoint (Azure ML / Function App) → Application
```

### Recommended Configuration

| Parameter | Default | Options |
|-----------|---------|---------|
| ML Framework | MLflow on Databricks | MLflow, Azure ML AutoML |
| Task | User-defined | classification, regression, forecasting, clustering, anomaly |
| Feature Store | Delta Lake tables | Delta Lake, Azure ML Feature Store |
| Serving | Azure ML Online Endpoint | Azure ML, Function App, Databricks Serving |
| Frontend | Streamlit | Streamlit, Power BI, React, API-only |
| Monitoring | Azure ML Model Monitor | drift detection, performance tracking |

### Cost Tier: Medium ($500-1,000/mo dev, depends on compute)

---

## Archetype 5: Knowledge Graph + AI

**Description:** Builds entity-relationship graphs for multi-hop reasoning, entity resolution, and GraphRAG. Combines graph databases with LLM-powered question answering.

**Fluke Examples:** Product knowledge graph (potential), Customer MDM graph

### Required Azure Resources

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Resource Group | - | AI | Container |
| AI Services | Azure AI Services | AI | LLM + embeddings |
| Graph DB (option A) | Cosmos DB (Gremlin API) | AI | Knowledge graph storage |
| Graph DB (option B) | Neo4j Aura | Marketplace | Knowledge graph storage |
| AI Search | Azure AI Search | AI | Hybrid retrieval (vector + graph) |
| Cosmos DB | Azure Cosmos DB (NoSQL) | AI | App state, conversation history |
| App Service | Azure App Service | AI | Frontend |
| Key Vault | Azure Key Vault | AI | Secrets |
| App Insights | Application Insights | AI | Telemetry |

**Split-model additions:**

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Databricks | Azure Databricks | UBI | Entity extraction, graph construction |
| ADF Pipeline | Azure Data Factory | UBI | Ingestion orchestration |
| ADLS Gen2 | ADLS | UBI | Medallion storage |

### Data Flow

```
Source Data (databases, documents, APIs)
    │
    ▼
Bronze: Raw entity data ingestion
    │   [Databricks: schema-on-read]
    ▼
Silver: Entity extraction, relationship mapping
    │   [Databricks: NER, co-reference resolution, LLM-assisted extraction]
    ▼
Gold: Graph triples (subject, predicate, object)
    │   [Databricks SQL: standardized entity/edge format]
    ▼
AI Layer: Graph load + Embeddings
    │   ├─ Cosmos Gremlin / Neo4j: vertices + edges
    │   └─ AI Search: entity embeddings for hybrid retrieval
    ▼
GraphRAG: Graph traversal + vector retrieval + LLM → Application
```

### Recommended Configuration

| Parameter | Default | Options |
|-----------|---------|---------|
| AI Model | gpt-4.1 | gpt-4.1, gpt-5 |
| Graph DB | User choice at Phase 0 | Cosmos DB Gremlin, Neo4j Aura |
| Graph Query | Gremlin or Cypher | depends on DB choice |
| Embedding Model | text-embedding-3-large | text-embedding-3-large |
| Retrieval | Multi-source (graph + vector) | graph-only, hybrid |
| Chunk Size | 1024 tokens | larger chunks for entity context |
| Frontend | React | React, Streamlit, Copilot Studio |

### Cost Tier: Medium-High ($700-1,400/mo dev)

---

## Archetype 6: Voice/Text Analytics

**Description:** Extracts signals, sentiment, entities, and themes from voice recordings, call transcripts, survey responses, and text feedback.

**Fluke Examples:** Voice to Value (VoC F9)

### Required Azure Resources

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Resource Group | - | AI | Container |
| AI Services | Azure AI Services | AI | LLM + Speech-to-Text + Language |
| Cosmos DB | Azure Cosmos DB (NoSQL) | AI | Processed signals, analytics data |
| Cosmos DB (provisioned) | Azure Cosmos DB | AI | High-throughput real-time analytics (optional) |
| Function App | Azure Functions (Flex) | AI | Audio/text processing pipeline |
| Logic App | Azure Logic App | AI | Trigger on new recordings, notifications |
| Storage Account | ADLS Gen2 | AI | Audio file storage |
| Key Vault | Azure Key Vault | AI | Secrets |
| App Insights | Application Insights | AI | Telemetry |

**Split-model additions:**

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Databricks | Azure Databricks | UBI | Batch NLP, aggregation, trend analysis |
| ADF Pipeline | Azure Data Factory | UBI | Scheduled processing orchestration |
| ADLS Gen2 | ADLS | UBI | Medallion layers for signal data |

### Data Flow

```
Audio/Text Sources (call recordings, surveys, emails, chat logs)
    │
    ▼
Bronze: Raw ingestion (audio files, text dumps)
    │   [Databricks/Function App: format normalization]
    ▼
Silver: Transcription (Speech-to-Text) + NLP pipeline
    │   [AI Services: transcription, language detection]
    │   [Databricks: entity extraction, sentiment, topic modeling]
    ▼
Gold: Structured signals (sentiment scores, entities, themes, trends)
    │   [Databricks SQL: aggregations, time-series views]
    ▼
AI Layer: Embeddings + LLM summarization
    │   [Signal clustering, theme extraction, executive summaries]
    ▼
Dashboard / API → Application
```

### Recommended Configuration

| Parameter | Default | Options |
|-----------|---------|---------|
| AI Model | gpt-4.1 | gpt-4.1, gpt-5 |
| Speech Model | Azure Speech-to-Text (Whisper) | Whisper, custom |
| NLP | Azure AI Language | sentiment, entities, key phrases, PII |
| Frontend | Streamlit (dashboard) | Streamlit, React, Power BI, Power Apps |
| Processing | Batch (scheduled) | batch, near-real-time, real-time |

### Cost Tier: Medium ($500-1,100/mo dev)

---

## Archetype 7: Multi-Agent System

**Description:** Multiple specialized AI agents coordinated by an orchestrator agent. Each sub-agent has its own tools, data access, and expertise domain. Built on LangGraph state machines with circular LLM fallback, LLM-as-Judge evaluation, and Azure-native observability. See `/agentic-deploy` skill for full runtime patterns.

**Fluke Examples:** Sales Playbook (potential)

### Required Azure Resources

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Resource Group | - | AI | Container |
| AI Services | Azure AI Services | AI | LLM for each agent (circular fallback pool) |
| AI Foundry Project | Microsoft Foundry | AI | Agent Service, MCP, tool registration |
| AI Search | Azure AI Search | AI | Shared knowledge retrieval + long-term user memory |
| Cosmos DB | Azure Cosmos DB (NoSQL) | AI | Agent state, conversation checkpointing, results |
| Container Apps | Azure Container Apps | AI | Agent runtime (auto-scaling, health probes) |
| Container Registry | Azure Container Registry | AI | Agent Docker images |
| Function App | Azure Functions (Flex) | AI | Agent tool implementations |
| Key Vault | Azure Key Vault | AI | Secrets (LLM keys, DB connections) |
| App Insights | Application Insights | AI | Per-agent telemetry + OpenTelemetry traces |
| Content Safety | Azure AI Content Safety | AI | Per-agent guardrails |

### Runtime Architecture (via /agentic-deploy)

```
User Request → FastAPI + Entra ID Auth + Rate Limiting
    │
    ├─ LangGraph State Machine (Orchestrator)
    │   ├─ chat node: LLM inference (circular fallback: Opus → Sonnet → Haiku → GPT-4o)
    │   ├─ tool_call node: Execute tools, route back to chat
    │   └─ Checkpointer: Cosmos DB (conversation state persistence)
    │
    ├─ Route to Specialist Agent(s) (sub-graphs)
    │   ├─ Agent A: Domain expertise + tools + own LLM config
    │   ├─ Agent B: Data analysis + tools + own LLM config
    │   └─ Agent C: Action execution + tools + own LLM config
    │
    ├─ Long-Term Memory (AI Search + pgvector)
    │   ├─ User-scoped vector memory (personalization across sessions)
    │   └─ Fact extraction → background task with error handling
    │
    ├─ Observability Stack
    │   ├─ Structured logging (structlog JSON → App Insights)
    │   ├─ LLM tracing (Langfuse callbacks per agent)
    │   └─ Metrics (latency histograms, token counters, request counts)
    │
    ├─ LLM-as-Judge Eval Framework (5 metrics)
    │   ├─ Hallucination, Relevancy, Helpfulness, Toxicity, Conciseness
    │   ├─ Batch evaluator fetches unscored traces → pushes scores to Langfuse
    │   └─ CI/CD gate: eval must pass before deploy
    │
    └─ Orchestrator assembles response → User
```

### Recommended Configuration

| Parameter | Default | Options |
|-----------|---------|---------|
| Orchestrator Model | claude-sonnet-4-6 | claude-opus-4-6, claude-sonnet-4-6, gpt-4.1 |
| Agent Models | claude-haiku-4-5 per agent | claude-haiku-4-5, claude-sonnet-4-6, gpt-4.1-mini, mixed |
| LLM Fallback | Circular (all models) | circular, sticky, tiered |
| Agent Framework | LangGraph | LangGraph, Foundry Agent Service, Semantic Kernel |
| Checkpointer | Cosmos DB | cosmos_db, postgres, memory (dev only) |
| Communication | Shared Cosmos DB state | Cosmos DB, message queue |
| Long-Term Memory | AI Search (user-scoped) | ai-search, pgvector, none |
| Auth | Entra ID | entra_id, jwt_custom |
| Observability | Azure Monitor + Langfuse | azure_monitor, langfuse, both |
| Eval Framework | LLM-as-Judge (5 metrics) | true, false |
| Deployment | Azure Container Apps | azure_container_apps, docker_compose, app_service |
| Frontend | React | React, Copilot Studio |

| Flag | Effect |
|------|--------|
| `agent_runtime: true` | Activates /agentic-deploy Modules 1+4+5 — LangGraph scaffolding, FastAPI, ACA deployment |
| `eval_framework: true` | Activates /agentic-deploy Module 3 — LLM-as-Judge with 5 quality metrics |
| `observability: "both"` | Activates /agentic-deploy Module 2 — App Insights + Langfuse dual tracing |

### Cost Tier: High ($1,000-2,500/mo dev, scales with agent count + ~$100/mo for eval LLM calls)

---

## Archetype 8: Computer Vision

**Description:** Image and video analysis — classification, object detection, defect inspection, OCR on visual content.

**Fluke Examples:** Quality inspection (potential)

### Required Azure Resources

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Resource Group | - | AI | Container |
| AI Services | Azure AI Services (Vision) | AI | Image analysis, custom vision |
| Azure ML | Azure Machine Learning | AI | Custom model training, endpoints |
| Container Registry | Azure Container Registry | AI | Custom model containers |
| Storage Account | ADLS Gen2 | AI | Image/video storage |
| Function App | Azure Functions | AI | Image processing pipeline |
| Cosmos DB | Azure Cosmos DB | AI | Results, metadata |
| Key Vault | Azure Key Vault | AI | Secrets |
| App Insights | Application Insights | AI | Telemetry |

**Split-model additions:**

| Resource | Service | Subscription | Purpose |
|----------|---------|-------------|---------|
| Databricks | Azure Databricks | UBI | Batch image processing, feature extraction |
| ADLS Gen2 | ADLS | UBI | Labeled dataset storage |

### Data Flow

```
Image/Video Sources (cameras, uploads, storage)
    │
    ▼
Bronze: Raw media ingestion
    │   [ADLS: original files, metadata sidecar]
    ▼
Silver: Preprocessing + AI Vision analysis
    │   [AI Services: classification, detection, OCR]
    │   [Databricks: batch processing, augmentation]
    ▼
Gold: Labeled datasets, analysis results
    │   [Structured metadata, confidence scores, bounding boxes]
    ▼
AI Layer: Custom model training (Azure ML) → Endpoint
    │   [MLflow tracking, model versioning]
    ▼
Inference API / Dashboard → Application
```

### Recommended Configuration

| Parameter | Default | Options |
|-----------|---------|---------|
| Vision Model | Azure AI Vision 4.0 | AI Vision, Custom Vision, Florence |
| Custom Training | Azure ML | Azure ML, Databricks |
| Frontend | React | React, Streamlit, Power Apps |
| Processing | Batch | batch, real-time (streaming) |

### Cost Tier: Medium-High ($600-1,500/mo dev, depends on volume)

### Sub-Variant: Document Vision (computer-vision + vision_mode: "document")

**Description:** Specialized variant for extracting structured data from engineering drawings, schematics, datasheets, and other technical PDFs using LLM vision capabilities rather than traditional OCR. Distinct from Doc Intelligence (which handles forms and contracts) — Document Vision targets visual-heavy documents where layout understanding and icon/symbol recognition are critical.

**Fluke Examples:** PLM engineering drawing extraction (validated: 94% title block accuracy, 80% BOM accuracy across 18 drawings), product datasheets, assembly schematics, test equipment calibration certificates.

**When to use Document Vision vs Doc Intelligence:**

| Signal | Document Vision | Doc Intelligence |
|--------|----------------|-----------------|
| Content type | Engineering drawings, schematics, diagrams | Contracts, forms, invoices, reports |
| Key data | Title blocks, BOM tables, callout annotations, dimensions | Named fields, clauses, tables, entities |
| Visual complexity | High (symbols, lines, overlapping text) | Low-Medium (structured text layout) |
| Extraction method | PyMuPDF→base64→LLM vision (Claude Sonnet/GPT-4o) | ContextGem concepts / Azure AI Doc Intelligence |
| BOM extraction | Two-pass: detect table region → extract with vision | Single-pass ContextGem JsonObjectConcept |

**Additional Resources (beyond base Computer Vision):**

| Resource | Service | Purpose |
|----------|---------|---------|
| Azure AI Foundry | Anthropic Claude Sonnet 4.6 or GPT-4o | Vision LLM for structured extraction |
| SharePoint connector | Graph API or OneDrive sync | Source PLM drawing files |

**Data Flow:**

```
PLM / SharePoint (engineering drawings, PDF/TIFF/DWG)
    │
    ▼
Bronze: Raw media ingestion (ADLS, metadata sidecar)
    │   [PDF/image files, size < 15MB per file]
    ▼
Silver: Vision extraction via litellm → Azure AI Foundry
    │   [PyMuPDF renders PDF→PNG at 150 DPI, max 5 pages]
    │   [base64 encode → Claude Sonnet structured JSON extraction]
    │   [Two-pass BOM: page scan → table region → detail extraction]
    │   Output: drawing_number, title, revision, type, BOM, materials, notes
    ▼
Gold: Structured metadata tables (Delta)
    │   [Extraction results + confidence scores per field]
    │   [BOM detail table (item_no, part_number, description, qty)]
    ▼
AI Layer: Index population (AI Search) or Graph load (Neo4j)
    │   [Optional: PLM validation against master data]
    ▼
Frontend: Document viewer + search (Streamlit or React)
```

**Recommended Configuration:**

| Parameter | Default | Options |
|-----------|---------|---------|
| Vision LLM | Claude Sonnet 4.6 via Azure AI Foundry | Claude Sonnet, GPT-4o |
| Rendering | PyMuPDF 150 DPI | PyMuPDF, pdf2image |
| Max pages/doc | 5 | 1-20 (cost scales linearly) |
| Max file size | 15 MB | Up to 50 MB with PDF splitting |
| BOM extraction | Two-pass | Single-pass (simple BOMs), Two-pass (assembly drawings) |
| Output format | JSON + Excel | JSON, Excel, Cosmos DB, Neo4j |
| Cost/drawing | ~$0.028 | Varies by page count and model |

**Key Learnings (from PLM validation):**

1. ContextGem v0.22.0 vision routing is broken with Azure AI Foundry — use litellm direct calls
2. Set `role="extractor_vision"` explicitly (ContextGem defaults to `extractor_text`, silently skips vision)
3. Drawing number ambiguity: some drawings have supplier PN + controlling PN — validate against PLM master
4. BOM extraction accuracy varies: tabular BOMs (100%) vs callout-style BOMs (60%) — use two-pass for assemblies
5. Always verify API key value, not just presence (`os.environ.get()` may return stale rotated key)

**Cost Tier:** Low ($50-200/mo dev, ~$0.03/drawing)

---

## Resource Map Summary

### Core Resources (All Archetypes)

Every archetype provisions these resources as a minimum:

| Resource | Service | Subscription |
|----------|---------|-------------|
| Resource Group | - | AI (always) |
| Key Vault | Azure Key Vault | AI |
| Log Analytics | Azure Monitor | AI |
| App Insights | Application Insights | AI |
| Storage Account | ADLS Gen2 | AI |

### Archetype-Specific Resources

| Resource | RAG | Conv | DocInt | ML | KG | Voice | Multi | Vision |
|----------|-----|------|--------|----|----|-------|-------|--------|
| AI Services | Y | Y | Y | - | Y | Y | Y | Y |
| AI Search | Y | - | Y | - | Y | - | Y | - |
| Cosmos DB (NoSQL) | Y | Y | Y | opt | Y | Y | Y | Y |
| Cosmos DB (Gremlin) | - | - | - | - | opt | - | - | - |
| Neo4j Aura | - | - | - | - | opt | - | - | - |
| Azure ML | - | - | - | Y | - | - | - | Y |
| AI Doc Intelligence | - | - | Y | - | - | - | - | - |
| App Service | Y | Y | - | opt | Y | opt | Y | opt |
| Function App | Y | Y | Y | Y | - | Y | Y | Y |
| Logic App | - | Y | - | - | - | Y | - | - |
| AI Foundry Project | - | Y | - | - | - | - | Y | - |
| Container Registry | - | - | - | - | - | - | - | Y |
| Content Safety | Y | Y | - | - | - | - | Y | - |
| Front Door | Y | Y | - | - | opt | - | Y | - |
| Databricks (UBI) | Y* | - | Y* | Y | Y* | Y* | - | Y* |
| ADF (UBI) | Y* | - | Y* | Y | Y* | Y* | - | - |
| ADLS (UBI) | Y* | - | Y* | Y | Y* | Y* | - | Y* |
| Fabric (UBI) | opt | - | opt | opt | - | - | - | - |

`Y` = always, `opt` = optional, `Y*` = when using split-subscription model, `-` = not needed

### Subscription Placement Rules

1. **AI subscription (Fluke AI ML Technology):** AI Services, AI Search, Cosmos DB, App Service, Function App, Logic App, Key Vault, App Insights, Front Door, Content Safety, AI Foundry, Azure ML, Container Registry
2. **UBI subscription (Unified BI):** Databricks, ADF, ADLS Gen2, Fabric, Azure SQL (status control metadata)
3. **Single-subscription model:** Everything goes to AI subscription; Databricks/ADF created there instead
4. **Override:** User specifies custom placement per resource

### Cost Tier Reference

| Tier | Monthly Range (Dev) | Typical Archetypes |
|------|--------------------|--------------------|
| Low | $200-500 | Document Intelligence (simple), Predictive ML (small) |
| Medium | $500-1,200 | RAG, Voice/Text, Predictive ML, Computer Vision |
| High | $1,000-2,500 | Multi-Agent, Knowledge Graph + AI, Conversational Agent |

These are Dev environment estimates. QA/Prod will be higher due to production SKUs, multi-region, and reserved capacity.

---

## JSON Resource Map Template

When Discovery (Phase 0) selects an archetype, populate `state.json.resources` using this template. Replace `{app}` with the project slug and `{env}` with `dev`.

**RAG archetype example (split-subscription model):**

```json
{
  "resource_map": {
    "ai_subscription": {
      "resource_group": "flk-{app}-{env}-rg",
      "resources": [
        {"name": "flk-{app}-ai-{env}", "type": "Microsoft.CognitiveServices/accounts", "sku": "S0", "purpose": "AI Services"},
        {"name": "flk-{app}-search-{env}", "type": "Microsoft.Search/searchServices", "sku": "standard", "purpose": "AI Search"},
        {"name": "flk-{app}-cosmosdb-{env}", "type": "Microsoft.DocumentDB/databaseAccounts", "sku": "serverless", "purpose": "Cosmos DB NoSQL"},
        {"name": "flk-{app}-webapp-{env}", "type": "Microsoft.Web/sites", "sku": "B1", "purpose": "App Service"},
        {"name": "flk-{app}-funcapp-{env}", "type": "Microsoft.Web/sites", "sku": "FC1", "purpose": "Function App"},
        {"name": "flk-{app}-kv-{env}", "type": "Microsoft.KeyVault/vaults", "sku": "standard", "purpose": "Key Vault"},
        {"name": "flk-{app}-logs-{env}", "type": "Microsoft.OperationalInsights/workspaces", "sku": "PerGB2018", "purpose": "Log Analytics"},
        {"name": "flk-{app}-insights-{env}", "type": "Microsoft.Insights/components", "purpose": "App Insights"},
        {"name": "flk{app}storage{env}", "type": "Microsoft.Storage/storageAccounts", "sku": "Standard_GRS", "purpose": "ADLS Gen2"},
        {"name": "flk-{app}-safety-{env}", "type": "Microsoft.CognitiveServices/accounts", "sku": "S0", "purpose": "Content Safety"},
        {"name": "flk-{app}-fd-{env}", "type": "Microsoft.Cdn/profiles", "sku": "Standard_AzureFrontDoor", "purpose": "Front Door"}
      ]
    },
    "ubi_subscription": {
      "resources": [
        {"name": "existing", "type": "Microsoft.Databricks/workspaces", "purpose": "Databricks (reuse existing)"},
        {"name": "PL_{app}_Master", "type": "Microsoft.DataFactory/factories/pipelines", "purpose": "ADF Master Pipeline"},
        {"name": "flukebi_{app}", "type": "adls_container", "purpose": "ADLS medallion storage"}
      ]
    }
  }
}
```

**Subscription placement key:** Use `ai_subscription` for all AI/app resources, `ubi_subscription` for data engineering. In single-subscription model, merge all into `ai_subscription`.
