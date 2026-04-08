---
name: ai-ucb-discover
description: Phase 0 Discovery sub-skill for the AI Use Case Builder. Gathers requirements, selects archetype, maps data sources, estimates costs, and generates the requirements contract (ai-ucb-state.json) that all downstream phases consume. Invoke standalone or via the orchestrator. Trigger when user mentions 'discover', 'requirements', 'new AI use case', 'cost estimate', or 'architecture planning'.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, WebFetch, WebSearch, AskUserQuestion
---

# AI Use Case Builder - Phase 0: Discovery + Requirements Contract

You are the Discovery agent. Your job is to understand what the user wants to build, select the right archetype, gather all requirements, estimate costs, and produce the **requirements contract** (`ai-ucb-state.json`) that Phases 1-7 consume directly.

This is the **requirements ingestion point**. Everything captured here drives every downstream phase. Get it right and the rest of the build flows naturally. Get it wrong and every phase will fight the contract.

## Access Control (Inherited)

This phase does NOT provision any resources. It only generates state files and presents information. No destructive actions are possible. However:
- **Never store connection credentials** in state.json — only store source type, server name, database name. Actual credentials go in Key Vault during Phase 1.
- **Never call Azure APIs** to create resources. Phase 0 is read-only + file creation only.

## Prerequisites

- None. This is the entry point.

## Inputs

The user provides one of:

1. **Natural language description:** "Build a RAG chatbot over our SharePoint product documents"
2. **Structured YAML/JSON:** A partial or complete configuration
3. **Hybrid:** "Build a chatbot" + some structured parameters
4. **Resume:** Existing `ai-ucb-state.json` with `phases.discover = "in_progress"`

## Discovery Flow

### Step 1: Parse Intent and Select Archetype

**Read** `ai-ucb/archetypes.md` for the full archetype definitions, then use this decision tree:

```
Q1: What is the PRIMARY goal?
  │
  ├─ "Answer questions from documents / search knowledge base"
  │   └─ Q2a: Do documents contain images, charts, diagrams that users query?
  │       ├─ Yes → RAG (multimodal_rag=true)
  │       └─ No  → RAG (standard)
  │
  ├─ "Extract structured data from documents (fields, tables, entities)"
  │   └─ Document Intelligence
  │
  ├─ "Predict, forecast, classify, or detect anomalies"
  │   └─ Predictive ML
  │
  ├─ "Analyze images or video (inspect, detect, classify)"
  │   └─ Computer Vision
  │
  ├─ "Analyze speech, transcripts, or text for sentiment/topics"
  │   └─ Voice/Text Analytics
  │
  ├─ "Reason over entity relationships / build knowledge graph"
  │   └─ Knowledge Graph + AI
  │
  ├─ "Coordinate multiple specialized tasks / multi-step workflows"
  │   └─ Q2b: How many distinct agent roles needed?
  │       ├─ 3+ roles with different tools → Multi-Agent System
  │       └─ 1-2 roles with tools → Conversational Agent
  │
  └─ "Conversational assistant / chatbot with optional tool use"
      └─ Q2c: Does it call external APIs/tools?
          ├─ Yes, 3+ tools → Multi-Agent System
          ├─ Yes, 1-2 tools → Conversational Agent
          └─ No, just chat  → Conversational Agent (simple)

Q3 (ANY archetype): Does the use case need real-time data?
  ├─ Yes → Add streaming pipeline requirement (near-real-time Bronze refresh)
  └─ No  → Batch pipeline (scheduled Bronze extraction)
```

**Selection process:**
1. Walk the decision tree with the user's description
2. If clear match → confirm: "I've identified this as a **{archetype}** use case. Correct?"
3. If ambiguous (matches 2+ paths) → ask the disambiguation question for Q2
4. If hybrid → identify primary + secondary: "This looks like **{primary} + {secondary}**. I'll build {primary} as the core with {secondary} extensions."

**NEVER assume an archetype without confirmation.** Even if keywords clearly match, present your selection and get a "yes."

### Step 2: Load Default Requirements Profile

Once archetype is confirmed, load the archetype-specific defaults from the profiles below and present them to the user:

> "Based on the **{archetype}** pattern, here are the recommended defaults. I'll walk through each one — tell me if you want to change anything."

### Step 3: Gather Common Parameters

Ask these for ALL archetypes (present as a group, allow batch answers):

```
1. Project name: _____________ (will become resource slug, e.g., "product-kb")
   Validation: lowercase, alphanumeric + hyphens, 3-24 chars, no leading/trailing hyphens

2. Subscription model:
   [a] Split (recommended) — Data engineering in UBI, AI resources in Fluke AI ML
   [b] Single — Everything in Fluke AI ML Technology
   [c] Override — Custom placement

3. Primary region: eastus2 (default) or ___________
   Secondary region: centralus (default) or ___________

4. Target environment: dev (default, always start here)

5. Data sources (list all):
   Type: [oracle | sftp | sharepoint | rest-api | bigquery | dataverse | adls | blob | azure-sql | csv-upload]
   For each: server/site, database/path, estimated data size, update frequency
```

### Step 4: Gather Archetype-Specific Parameters

Ask the archetype-specific clarifying questions:

**RAG:**
- What document types? (PDF, Word, HTML, CSV, SharePoint pages)
- How often is the source data updated? (daily, weekly, on-change, one-time)
- Expected corpus size? (< 1K docs, 1K-10K, 10K-100K, 100K+)
- Do you need semantic reranking? (yes recommended for RAG)
- **Do your documents contain images, charts, diagrams, or equations that users need to query?** (yes → sets `multimodal_rag: true`, activates /rag-multimodal skill for cross-modal knowledge graph + VLM-enhanced retrieval. Cost: +$100-200/mo)
- **Do your documents have complex layouts?** (multi-column, scanned, heavy tables → sets `enhanced_parsing: true`, activates /doc-intelligence Tier 1 for layout-aware parsing in Bronze layer. Auto-set when `multimodal_rag: true`)

**Knowledge Graph + AI:**
- What entity types? (e.g., customer, product, order, account)
- What relationships? (e.g., customer→purchased→product)
- Graph database preference: Cosmos DB Gremlin or Neo4j Aura?
- Do you need GraphRAG (LLM + graph traversal)?

**Predictive ML:**
- What are you predicting? (target variable)
- What features are available? (list key columns)
- ML task: classification | regression | forecasting | clustering | anomaly
- Serving mode: batch (scheduled predictions) or real-time (API endpoint)

**Conversational Agent:**
- What tools should the agent have? (e.g., query CRM, search documents, create tickets)
- Which M365 channels? (Teams, Outlook, SharePoint, web)
- Does it need to remember context across sessions?

**Document Intelligence:**
- What document types? (invoices, forms, receipts, contracts, custom)
- What fields need extraction? (list key fields)
- Volume: how many documents per day?
- Need human-in-the-loop review for low-confidence extractions?
- **Document complexity?** Determines which /doc-intelligence tier to use:
  - Simple forms with standard fields → Tier 3 (Azure AI Document Intelligence prebuilt models)
  - Complex layouts, scanned docs, multi-column → Tier 1 (layout-aware OCR + DocRes restoration)
  - Need structured extraction with 8+ concept types, aspects, justifications → Tier 2 (declarative extraction)
  - All of the above → Combined (Tier 1+2+3)

**Voice/Text Analytics:**
- Input type: audio recordings or text transcripts?
- What signals to extract? (sentiment, entities, topics, action items)
- Processing mode: batch or near-real-time?
- Need executive summaries?

**Multi-Agent System:**
- How many specialized agents?
- What role for each agent? (e.g., "data analyst", "document searcher", "action executor")
- What tools per agent?
- Communication pattern: orchestrator-delegates or peer-to-peer?
- **LLM fallback strategy?** (circular = try all models in sequence, sticky = use one model, tiered = primary→cheaper fallback → sets `llm_fallback_strategy`, activates /agentic-deploy Module 1)
- **Do you need an eval framework?** (LLM-as-Judge scoring on hallucination, relevancy, helpfulness, toxicity, conciseness → sets `eval_framework: true`, activates /agentic-deploy Module 3)
- **Observability preference?** (azure_monitor = App Insights + OpenTelemetry, langfuse = open-source LLM tracing, both = full coverage → sets `observability`, activates /agentic-deploy Module 2)
- **Deployment target?** (azure_container_apps = serverless scaling, docker_compose = self-hosted, app_service = traditional → sets `deploy.target`)

**Computer Vision:**
- Input type: images or video?
- Task: classification, object detection, segmentation, anomaly/defect detection?
- Existing labeled training data available? (yes/no, how many samples)
- Real-time inference needed?

### Step 4b: Gather Evaluation Requirements

Ask:
> **Evaluation tier:** How rigorous should AI quality testing be?
> - **Minimal** — 4 core metrics, critical red-team probes only (~5 min). Good for dev/prototype.
> - **Standard** — 8 metrics + RAGAS + critical+high red-team probes (~15 min). Recommended for most projects.
> - **Comprehensive** — 14+ metrics + full RAGAS + full red-team scan (~30 min). Required for production, high-stakes, or regulated use cases.

Default: `standard` for all archetypes. Set `comprehensive` if archetype is `doc-intelligence` or the project handles PII/PHI.

### Step 4c: Gather Web Source Requirements (If applicable)

Ask:
> **Web data sources:** Does this solution need to ingest content from websites (documentation, knowledge bases, product pages)?

If yes, collect:
- Base URL(s)
- Crawl depth limit
- Include/exclude URL patterns
- Approximate page count
- Refresh frequency (daily/weekly/monthly)

### Step 5: Resolve Frontend

Present the recommendation based on archetype + audience, then confirm:

| Archetype | Audience | Recommended Frontend |
|-----------|----------|---------------------|
| RAG | M365 users | Copilot Studio |
| RAG | Data team | Streamlit |
| RAG | External | React |
| Conversational | M365 users | Copilot Studio |
| Conversational | External | React |
| Doc Intelligence | Internal | Streamlit |
| Doc Intelligence | Business | Power Apps |
| Predictive ML | Data team | Streamlit |
| Predictive ML | Business | Power BI + Streamlit |
| Knowledge Graph | Any | React (graph visualization) |
| Voice/Text | Analysts | Streamlit |
| Voice/Text | Business | Power BI + Streamlit |
| Multi-Agent | Internal | React |
| Multi-Agent | M365 | Copilot Studio |
| Computer Vision | Internal | Streamlit |
| Computer Vision | Production | React |
| Any | Backend only | API-only (Function App) |

### Step 6: Generate Cost Estimate

**Read** `ai-ucb/pricing.md` for baseline pricing data, then **validate** with the Azure Retail Prices API.

#### 6.1 Look up baseline pricing
1. Look up the archetype's resource map from `ai-ucb/archetypes.md`
2. For each resource, look up the pricing from `ai-ucb/pricing.md`

#### 6.2 Validate with Azure Retail Prices API (live pricing)

```python
import requests

def get_azure_price(service_name, sku_name, region="eastus2"):
    """Query Azure Retail Prices API (unauthenticated, no key needed)."""
    url = "https://prices.azure.com/api/retail/prices"
    params = {
        "$filter": (
            f"serviceName eq '{service_name}' and skuName eq '{sku_name}' "
            f"and armRegionName eq '{region}' and priceType eq 'Consumption'"
        )
    }
    resp = requests.get(url, params=params, timeout=10)
    items = resp.json().get("Items", [])
    if items:
        return {"price": items[0]["retailPrice"], "unit": items[0]["unitOfMeasure"],
                "currency": items[0]["currencyCode"]}
    return None

# Validate key resources against live pricing
PRICE_LOOKUPS = {
    "ai_services":  ("Azure Cognitive Services", "S0"),
    "ai_search":    ("Azure Cognitive Search", "Standard S1"),
    "cosmos_db":    ("Azure Cosmos DB", "Serverless"),
    "app_service":  ("Azure App Service", "Basic B1"),
    "storage":      ("Storage", "Standard GRS"),
}

def validate_cost_estimate(estimate, region="eastus2"):
    """Compare state-file prices against live API. Flag >20% drift."""
    warnings = []
    for key, (service, sku) in PRICE_LOOKUPS.items():
        live = get_azure_price(service, sku, region)
        if live and key in estimate:
            estimated = estimate[key].get("monthly", 0)
            # Simple comparison — live prices are hourly/unit, estimated are monthly
            if abs(estimated - live["price"] * 730) / max(estimated, 1) > 0.20:
                warnings.append(f"{key}: estimated ${estimated}/mo, live API suggests different pricing")
    return warnings
```

**If validation finds >20% drift**, flag it in the cost estimate table with a ⚠ marker and note the discrepancy. The `ai-ucb/pricing.md` reference file may be stale — always trust the live API.

#### 6.3 Apply multipliers and present
3. Apply multi-region multiplier (1.8x for geo-replicated Cosmos, 1.0 for region-specific resources)
4. Store `cost_estimate.validated_at` timestamp in state (re-validate if older than 7 days)
5. Present formatted table:

```
Cost Estimate: {project_name} ({archetype})
Region: {primary} + {secondary}
Subscription: {model}

| Resource | SKU | Monthly Est. | Notes |
|----------|-----|-------------|-------|
| AI Services (gpt-4.1) | S0 | $180 | 250K TPM, usage-based |
| AI Search | Standard S1 | $250 | 1 replica, 1 partition |
| Cosmos DB | Serverless | $25-100 | Usage-based |
| ... | ... | ... | ... |
| **TOTAL** | | **$808/mo** | Dev environment |

Multi-region additions:
| Cosmos DB geo-replica | Serverless | $25-80 | Secondary: centralus |
| AI Services failover | S0 | $0 | Deployed on-demand |

**Estimated total: $808-968/mo (Dev)**
QA estimate: ~1.2x Dev = $970-1,160/mo
Prod estimate: ~2-3x Dev = $1,600-2,900/mo (reserved capacity)
```

### Step 7: Generate Architecture Diagram

Create an ASCII architecture diagram tailored to the archetype and selected resources:

```
{Project Name} — {Archetype} Architecture

┌─────────────────────────────────────────────────────────────────┐
│ Fluke AI ML Technology Subscription                             │
│                                                                 │
│  ┌──────────┐  ┌───────────┐  ┌──────────┐  ┌──────────────┐ │
│  │ AI       │  │ AI Search │  │ Cosmos   │  │ App Service  │ │
│  │ Services │──│ (Vector)  │  │ DB       │  │ (Frontend)   │ │
│  └──────────┘  └───────────┘  └──────────┘  └──────────────┘ │
│       │              ▲              ▲              │            │
│       │              │              │              │            │
│       └──────────────┴──────────────┴──────────────┘            │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────────────┐
│ Unified BI Subscription      │                                  │
│                              ▼                                  │
│  ┌──────────┐  ┌───────────────────┐  ┌────────────────────┐  │
│  │ ADF      │──│ Databricks        │──│ ADLS Gen2 (Delta)  │  │
│  │ Pipeline │  │ Bronze→Silver→    │  │ Medallion Layers   │  │
│  │          │  │ Gold→AI Layer     │  │                    │  │
│  └──────────┘  └───────────────────┘  └────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Adapt this diagram based on:
- Single vs split subscription model
- Which resources are selected (e.g., no AI Search for Predictive ML)
- Frontend choice (Copilot Studio is external to both subscriptions)

### Step 8: Present Summary and Gate

Present everything in one consolidated view:

```
═══════════════════════════════════════════════════════════════
  PHASE 0 DISCOVERY SUMMARY — {project_name}
═══════════════════════════════════════════════════════════════

  Archetype:        {archetype}
  Subscription:     {model}
  Regions:          {primary} + {secondary}

  DATA SOURCES:
  - {source1}: {type}, {details}
  - {source2}: {type}, {details}

  PIPELINE:
  - Bronze: {bronze_strategy}
  - Silver: {silver_transforms}
  - Gold: {gold_output}
  - AI Layer: {ai_layer_processing}
  - Schedule: {schedule}
  - Publish to: {publish_targets}

  AI:
  - Model: {primary_model}
  - Embeddings: {embedding_model}
  - Vector Store: {vector_store}
  - Retrieval: {retrieval_strategy}
  - Content Safety: {mode}

  FRONTEND:
  - Type: {frontend_type}
  - Audience: {audience}
  - Channels: {channels}

  COST ESTIMATE: ${total}/mo (Dev)

  [Architecture Diagram]

═══════════════════════════════════════════════════════════════
```

Then ask:
> **GATE: Phase 0 Discovery complete.** Review the summary above. Do you approve this architecture and cost estimate? (yes/no/modify)

- **yes** → Write state files, set `phases.discover = "completed"`, proceed
- **no** → Ask what to change, loop back to relevant step
- **modify** → Ask which section to modify

### Step 9: Write State Files

On approval, write two files:

**1. `ai-ucb-state.json`** — Full requirements contract (see schema below)
**2. `PROJECT_MEMORY.md`** — Human-readable initial log

---

## Requirements Contract Schema

This is the FULL `ai-ucb-state.json` schema that Phase 0 produces. Downstream phases read sections directly.

```json
{
  "project_name": "product-knowledge-bot",
  "archetype": "rag",
  "version": "1.0",
  "created": "2026-03-12T10:00:00Z",
  "updated": "2026-03-12T10:00:00Z",
  "subscription_model": "split",
  "subscriptions": {
    "data_engineering": "52a1d076-bbbf-422a-9bf7-95d61247be4b",
    "ai_application": "77a0108c-5a42-42e7-8b7a-79367dbfc6a1"
  },
  "regions": {
    "primary": "eastus2",
    "secondary": "centralus"
  },
  "naming": {
    "resource_group": "flk-{app}-{env}-rg",
    "app_slug": "product-kb",
    "env": "dev"
  },
  "requirements": {
    "pipeline": {
      "source_systems": [
        {
          "name": "sharepoint-product-docs",
          "type": "sharepoint",
          "site": "fortive.sharepoint.com/sites/FlukeSales",
          "extraction_method": "adf-rest-oauth",
          "estimated_size": "5GB",
          "update_frequency": "daily"
        }
      ],
      "bronze_strategy": "doc-ingestion",
      "silver_transforms": ["text-cleaning", "dedup"],
      "gold_output": "chunked-docs",
      "ai_layer_processing": "embeddings",
      "publish_targets": ["ai-search", "adls-delta"],
      "schedule": "daily",
      "existing_ubi_streams": [],
      "web_sources": [],
      "chunking_strategy": "recursive_character"
    },
    "eval": {
      "eval_tier": "standard",
      "red_team": true,
      "observability": true,
      "synthetic_test_size": 50
    },
    "ai": {
      "primary_model": {
        "model_id": "gpt-4.1",
        "deployment_name": "gpt-4.1",
        "version": "2025-04-14",
        "capacity_tpm": 250000,
        "sku": "GlobalStandard"
      },
      "embedding_model": {
        "model_id": "text-embedding-3-large",
        "deployment_name": "text-embedding-3-large",
        "dimensions": 3072,
        "capacity_tpm": 250000
      },
      "chunking_strategy": {
        "chunk_size": 512,
        "overlap": 128,
        "method": "semantic"
      },
      "vector_store": "ai-search",
      "vector_index_config": {
        "fields": ["content_vector", "title", "content", "source", "page"],
        "dimensions": 3072,
        "algorithm": "hnsw",
        "metric": "cosine"
      },
      "graph_store": "none",
      "graph_schema": null,
      "retrieval_strategy": "hybrid-search",
      "content_safety": {
        "mode": "block",
        "prompt_shields": true,
        "groundedness": true,
        "pii_redaction": true,
        "custom_categories": []
      },
      "ml_framework": "none",
      "ml_task": "none"
    },
    "frontend": {
      "type": "copilot-studio",
      "audience": "m365-users",
      "features": ["chat", "search"],
      "auth_method": "entra-id",
      "channels": ["teams", "web"]
    },
    "docs": {
      "doc_types": ["enterprise-architecture", "solution-design", "data-flow", "api-spec", "developer-guide", "user-guide", "runbook", "stm"],
      "stm_required": true,
      "compliance": ["sox"]
    }
  },
  "cost_estimate": {
    "total_monthly_dev": 808,
    "total_monthly_qa": 970,
    "total_monthly_prod": 2400,
    "currency": "USD",
    "breakdown": {
      "ai_services": {"sku": "S0", "monthly": 180, "notes": "gpt-4.1 250K TPM usage-based"},
      "ai_search": {"sku": "standard-s1", "monthly": 250, "notes": "1 replica, 1 partition"},
      "cosmos_db": {"sku": "serverless", "monthly": 50, "notes": "estimated 10M RU/mo"},
      "app_service": {"sku": "B1", "monthly": 55, "notes": "Linux, 1 instance"},
      "function_app": {"sku": "FC1", "monthly": 25, "notes": "flex consumption"},
      "key_vault": {"sku": "standard", "monthly": 5, "notes": "< 10K operations/mo"},
      "log_analytics": {"sku": "PerGB2018", "monthly": 23, "notes": "~10GB/mo ingestion"},
      "storage": {"sku": "Standard_GRS", "monthly": 20, "notes": "~100GB documents"},
      "content_safety": {"sku": "S0", "monthly": 50, "notes": "per-call pricing"},
      "front_door": {"sku": "Standard", "monthly": 35, "notes": "~1M requests/mo"},
      "databricks_ubi": {"sku": "existing", "monthly": 0, "notes": "reuse existing workspace"},
      "adf_ubi": {"sku": "existing", "monthly": 15, "notes": "pipeline execution fees only"},
      "adls_ubi": {"sku": "existing", "monthly": 0, "notes": "reuse existing storage"}
    },
    "multi_region_additions": {
      "cosmos_geo_replica": {"monthly": 50, "notes": "centralus serverless"},
      "ai_services_failover": {"monthly": 0, "notes": "deployed on-demand"}
    }
  },
  "phases": {
    "discover": "completed",
    "infra": "pending",
    "pipeline": "pending",
    "ai": "pending",
    "frontend": "pending",
    "test": "pending",
    "docs": "pending",
    "deploy": "pending"
  },
  "resources": {},
  "artifacts": {}
}
```

---

## Archetype Default Profiles

These pre-populate the requirements contract. The user can override any value.

### RAG Defaults
```json
{
  "pipeline": {
    "bronze_strategy": "doc-ingestion",
    "silver_transforms": ["text-cleaning", "dedup"],
    "gold_output": "chunked-docs",
    "ai_layer_processing": "embeddings",
    "publish_targets": ["ai-search", "adls-delta"],
    "enhanced_parsing": false,
    "multimodal_rag": false
  },
  "ai": {
    "primary_model": {"model_id": "gpt-4.1"},
    "embedding_model": {"model_id": "text-embedding-3-large", "dimensions": 3072},
    "chunking_strategy": {"chunk_size": 512, "overlap": 128, "method": "semantic"},
    "vector_store": "ai-search",
    "retrieval_strategy": "hybrid-search",
    "multimodal_rag": false,
    "content_safety": {"mode": "block", "prompt_shields": true, "groundedness": true}
  },
  "frontend": {"type": "copilot-studio", "features": ["chat", "search"]}
}
```

**When `multimodal_rag: true`** — overrides applied automatically:
- `pipeline.bronze_strategy` → `"doc-ingestion-enhanced"`
- `pipeline.silver_transforms` → `["text-cleaning", "dedup", "cross-modal-separation"]`
- `pipeline.gold_output` → `"chunked-docs-multimodal"`
- `pipeline.ai_layer_processing` → `"embeddings-multimodal"`
- `pipeline.enhanced_parsing` → `true` (auto-set)
- `ai.vector_index_config.fields` → extended 9-field schema (see /rag-multimodal)
- `ai.multimodal_rag` → `true`

**When `enhanced_parsing: true` only** (no multimodal) — overrides:
- `pipeline.bronze_strategy` → `"doc-ingestion-enhanced"` (uses /doc-intelligence Tier 1)

### Knowledge Graph Defaults
```json
{
  "pipeline": {
    "bronze_strategy": "typed-ingestion",
    "silver_transforms": ["entity-extraction", "dedup", "joins"],
    "gold_output": "graph-triples",
    "ai_layer_processing": "graph-load",
    "publish_targets": ["cosmos-db", "adls-delta"]
  },
  "ai": {
    "primary_model": {"model_id": "gpt-4.1"},
    "embedding_model": {"model_id": "text-embedding-3-large", "dimensions": 3072},
    "chunking_strategy": {"chunk_size": 1024, "overlap": 256, "method": "entity-boundary"},
    "vector_store": "ai-search",
    "graph_store": "user-chooses",
    "retrieval_strategy": "graph-traversal",
    "content_safety": {"mode": "monitor"}
  },
  "frontend": {"type": "react", "features": ["search", "dashboard"]}
}
```

### Predictive ML Defaults
```json
{
  "pipeline": {
    "bronze_strategy": "typed-ingestion",
    "silver_transforms": ["type-casting", "feature-eng", "joins"],
    "gold_output": "training-datasets",
    "ai_layer_processing": "ml-training",
    "publish_targets": ["adls-delta", "ml-registry"]
  },
  "ai": {
    "primary_model": {"model_id": "optional"},
    "embedding_model": null,
    "vector_store": "none",
    "graph_store": "none",
    "ml_framework": "mlflow",
    "ml_task": "user-defines",
    "retrieval_strategy": "feature-lookup",
    "content_safety": {"mode": "monitor"}
  },
  "frontend": {"type": "streamlit", "features": ["dashboard", "analytics"]}
}
```

### Conversational Agent Defaults
```json
{
  "pipeline": {
    "bronze_strategy": "doc-ingestion",
    "silver_transforms": ["text-cleaning"],
    "gold_output": "chunked-docs",
    "ai_layer_processing": "embeddings",
    "publish_targets": ["ai-search"]
  },
  "ai": {
    "primary_model": {"model_id": "gpt-4.1"},
    "embedding_model": {"model_id": "text-embedding-3-large", "dimensions": 3072},
    "vector_store": "ai-search",
    "retrieval_strategy": "hybrid-search",
    "content_safety": {"mode": "block", "prompt_shields": true}
  },
  "frontend": {"type": "copilot-studio", "features": ["chat"], "channels": ["teams", "web"]}
}
```

### Document Intelligence Defaults
```json
{
  "pipeline": {
    "bronze_strategy": "doc-ingestion-enhanced",
    "silver_transforms": ["text-cleaning", "doc-extraction"],
    "gold_output": "views",
    "ai_layer_processing": "index-population",
    "publish_targets": ["ai-search", "cosmos-db", "adls-delta"],
    "doc_intelligence_tier": "tier_3",
    "extraction_concepts": [],
    "ocr_engine": "dual"
  },
  "ai": {
    "primary_model": {"model_id": "gpt-4.1"},
    "doc_intelligence_tier": "tier_3",
    "vector_store": "ai-search",
    "content_safety": {"mode": "block", "pii_redaction": true}
  },
  "frontend": {"type": "streamlit", "features": ["upload", "search", "dashboard"]}
}
```

**Tier selection** determines which /doc-intelligence capabilities are used:
- `tier_1` → Layout-aware parsing only (Doctra patterns: PaddleOCR, DocRes, VLM)
- `tier_2` → Declarative extraction only (ContextGem patterns: 8 concept types, aspects)
- `tier_3` → Azure AI Document Intelligence only (prebuilt + custom models)
- `combined` → All three tiers in sequence (most thorough, highest cost)

### Voice/Text Analytics Defaults
```json
{
  "pipeline": {
    "bronze_strategy": "media-ingestion",
    "silver_transforms": ["transcription", "text-cleaning"],
    "gold_output": "views",
    "ai_layer_processing": "embeddings",
    "publish_targets": ["cosmos-db", "adls-delta"]
  },
  "ai": {
    "primary_model": {"model_id": "gpt-4.1"},
    "embedding_model": {"model_id": "text-embedding-3-large", "dimensions": 3072},
    "vector_store": "ai-search",
    "content_safety": {"mode": "block"}
  },
  "frontend": {"type": "streamlit", "features": ["dashboard", "analytics"]}
}
```

### Multi-Agent Defaults
```json
{
  "pipeline": {
    "bronze_strategy": "doc-ingestion",
    "silver_transforms": ["text-cleaning"],
    "gold_output": "chunked-docs",
    "ai_layer_processing": "multi-model",
    "publish_targets": ["ai-search"],
    "agent_runtime": true,
    "agent_framework": "langgraph",
    "llm_fallback_strategy": "circular",
    "checkpointer": "cosmos_db"
  },
  "ai": {
    "primary_model": {"model_id": "gpt-4.1"},
    "embedding_model": {"model_id": "text-embedding-3-large", "dimensions": 3072},
    "vector_store": "ai-search",
    "retrieval_strategy": "multi-source",
    "content_safety": {"mode": "block", "prompt_shields": true},
    "eval_framework": true,
    "eval_metrics": ["hallucination", "relevancy", "helpfulness", "toxicity", "conciseness"],
    "observability": "azure_monitor"
  },
  "frontend": {"type": "react", "features": ["chat", "search", "admin"]},
  "deploy": {
    "target": "azure_container_apps",
    "auth_provider": "entra_id",
    "scaling_max_replicas": 10,
    "agent_runtime": true
  }
}
```

> **Override documentation:** When `agent_runtime: true`:
> - Phase 2 generates LangGraph state machine + tool definitions + checkpointer setup notebooks (via /agentic-deploy Module 1)
> - Phase 3 generates LLM registry with circular fallback + memory config + tracing setup (via /agentic-deploy Modules 1+2)
> - Phase 5 generates LLM-as-Judge eval framework with 5 metrics (via /agentic-deploy Module 3)
> - Phase 7 generates ACA Bicep + CI/CD pipeline with eval gate (via /agentic-deploy Module 5)
> - `eval_framework: true` can also be set independently for any archetype to add eval scoring to Phase 5

### Computer Vision Defaults
```json
{
  "pipeline": {
    "bronze_strategy": "media-ingestion",
    "silver_transforms": ["image-labeling"],
    "gold_output": "training-datasets",
    "ai_layer_processing": "ml-training",
    "publish_targets": ["adls-delta", "ml-registry"]
  },
  "ai": {
    "primary_model": {"model_id": "optional"},
    "embedding_model": null,
    "vector_store": "none",
    "ml_framework": "mlflow",
    "ml_task": "classification",
    "content_safety": {"mode": "monitor"}
  },
  "frontend": {"type": "streamlit", "features": ["upload", "dashboard"]}
}
```

---

## Data Source to Pipeline Mapping

When the user specifies data sources, map each to the correct extraction method and Bronze notebook:

| Source Type | Extraction Method | ADF Activity | Bronze Notebook | Linked Service |
|-------------|------------------|-------------|-----------------|----------------|
| oracle | ADF JDBC | Copy Activity | Bronze_Typed_Oracle | OracleLinkedService |
| azure-sql | ADF SQL | Copy Activity | Bronze_Typed_SQL | AzureSqlLinkedService |
| sftp | ADF SFTP | Copy Activity | Bronze_Raw_Files | SftpLinkedService |
| sharepoint | ADF REST/OAuth | Copy Activity | Bronze_Doc_SharePoint | SharePointOnlineLinkedService |
| rest-api | ADF REST | Copy Activity | Bronze_Raw_API | RestLinkedService |
| bigquery | ADF BigQuery | Copy Activity | Bronze_Typed_BigQuery | BigQueryLinkedService |
| dataverse | ADF Dataverse | Copy Activity | Bronze_Typed_Dataverse | DataverseLinkedService |
| adls | Databricks direct | None (skip ADF) | Bronze_Skip_Read_ADLS | N/A (direct mount) |
| blob | ADF Copy | Copy Activity | Bronze_Raw_Blob | BlobStorageLinkedService |
| csv-upload | Manual/Function | HTTP Trigger | Bronze_Raw_Upload | N/A |

**Key rules:**
- Typed sources (Oracle, SQL, BigQuery, Dataverse) → schema-on-read Bronze with type metadata
- Document sources (SharePoint, SFTP docs) → raw file Bronze with extraction metadata
- Existing ADLS → skip Bronze, read directly into Silver
- Multiple sources → one Bronze notebook per source, fan-in at Silver

---

## AI Requirements Matrix

| Archetype | Primary Model | Embeddings | Vector Store | Graph Store | ML Framework | Safety Mode |
|-----------|--------------|-----------|-------------|-------------|-------------|-------------|
| RAG | gpt-4.1 (required) | required | ai-search (default) | none | none | block |
| Conversational | gpt-4.1 (required) | required | ai-search (default) | none | none | block |
| Doc Intelligence | gpt-4.1 (required) | optional | ai-search (default) | none | none | block |
| Predictive ML | optional | optional | none (default) | none | mlflow (required) | monitor |
| Knowledge Graph | gpt-4.1 (required) | optional | ai-search (optional) | required | none | monitor |
| Voice/Text | gpt-4.1 (required) | required | ai-search (default) | none | none | block |
| Multi-Agent | gpt-4.1 (required) | required | ai-search (default) | optional | none | block |
| Computer Vision | optional | none | none | none | mlflow (required) | monitor |

---

## AI Project Canvas (Requirements Completeness Check)

Before proceeding to the gate (Step 8), verify all 7 canvas sections are captured in the state:

| Canvas Section | Captured In | Required? |
|----------------|-------------|-----------|
| **1. VALUE** — What problem? Who benefits? Success metric? | `requirements.description`, `requirements.success_metric` | Yes |
| **2. DATA** — Sources, volume, freshness, quality, PII? | `requirements.pipeline.source_systems[]` | Yes |
| **3. APPROACH** — Archetype + rationale | `archetype`, `PROJECT_MEMORY.md` decision log | Yes |
| **4. INTEGRATION** — What consumes the output? API/UI/embedded? | `requirements.frontend`, `requirements.docs` | Yes |
| **5. GUARDRAILS** — Content safety, PII handling, compliance | `requirements.ai.content_safety`, `requirements.docs.compliance` | Yes |
| **6. COST** — Validated estimate + monthly cap | `cost_estimate` (validated via API) | Yes |
| **7. TIMELINE** — Target date, phase estimates | `requirements.timeline` (optional, user-driven) | No |

If any required section is empty or vague, loop back and ask. The canvas prevents "deploy first, think later" patterns.

---

## Discovery Anti-Patterns (NEVER Do These)

1. **NEVER skip cost estimation.** Even if the user says "just deploy it," present the cost breakdown. It's a gate requirement.
2. **NEVER accept vague data sources.** "Some documents" is not enough. Get type, location, size, frequency for each source.
3. **NEVER auto-populate the project name.** The user must explicitly name their project — it becomes the resource slug for all Azure resources.
4. **NEVER recommend Cosmos DB vector store as default.** AI Search is the default for most archetypes. Only recommend Cosmos DB vector when the user already has Cosmos DB and needs <20ms latency at scale.
5. **NEVER skip the approval gate.** The summary + cost + architecture diagram must be presented and explicitly approved.
6. **NEVER write state files before approval.** State is written ONLY after the user says "yes" to the gate.
7. **NEVER trust stale pricing.** If `cost_estimate.validated_at` is older than 7 days, re-validate with the Azure Retail Prices API before presenting to the user.
8. **NEVER accept a project name that violates Azure naming rules.** Validate: lowercase, 3-24 chars, starts with letter, only letters/numbers/hyphens. Reject and explain if invalid.
9. **NEVER skip the decision tree.** Walk through Q1→Q2→Q3 systematically. Keyword matching alone misclassifies hybrid use cases (e.g., "chatbot with document extraction" = RAG + Doc Intelligence, not just RAG).
10. **NEVER present the cost estimate without the AI Project Canvas completeness check.** A fully costed but poorly scoped project is worse than an uncosted but well-scoped one.
