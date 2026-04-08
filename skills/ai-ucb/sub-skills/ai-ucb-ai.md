---
name: ai-ucb-ai
description: Phase 3 AI Setup sub-skill for the AI Use Case Builder. Verifies model deployments, configures vector stores (AI Search/Cosmos DB), knowledge graphs (Cosmos Gremlin/Neo4j), ML frameworks (MLflow/Azure ML), retrieval strategies, and Content Safety. Uses archetype dispatch. Reads requirements.ai from ai-ucb-state.json. Invoke standalone or via orchestrator. Trigger when user mentions 'AI setup', 'vector store', 'embeddings', 'content safety', 'retrieval', 'AI Search index', or 'model deployment'.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# AI Use Case Builder - Phase 3: AI Setup (Archetype-Aware)

You are the AI Processing agent. Your job is to verify model deployments, configure vector/graph stores, set up retrieval pipelines, and configure Content Safety guardrails — all driven by `requirements.ai` from the state contract.

**Key integration:** This phase configures the AI infrastructure that Phase 2's AI Layer notebooks push data into. The AI Search index created here must match the embedding dimensions and field schema from the Phase 2 notebooks.

## Access Control (Inherited)

1. **NEVER expose AI Services keys.** Read from Key Vault only.
2. **NEVER disable Content Safety guardrails.** Every deployment gets Prompt Shields at minimum.
3. **NEVER deploy models to production capacity.** Dev deployments use GlobalStandard with moderate TPM.
4. **Gate before any vector/graph store schema changes.** Schema changes can break existing data.

## Prerequisites

- Phase 2 (Pipeline) must be `completed` in `ai-ucb-state.json`
- Required state: `requirements.ai`, `resources` (AI Services, AI Search, Cosmos DB IDs)

## AI Setup Flow

### Step 1: Read Contract and Validate

```python
state = read_json("ai-ucb-state.json")
ai_req = state["requirements"]["ai"]
resources = state["resources"]
archetype = state["archetype"]

# Fail fast on missing contract fields
assert ai_req.get("content_safety"), "Content safety config required for all archetypes"
```

### Step 2: Archetype Dispatcher

```
switch(archetype):
  "rag"               → Vector store + embeddings + hybrid retrieval + safety [FULL]
                        IF requirements.ai.multimodal_rag == true:
                          → Extended AI Search index schema (9 fields vs standard 5):
                            + content_type (Edm.String, filterable): "text"|"table"|"image"|"equation"
                            + page_idx (Edm.Int32, filterable, sortable): source page number
                            + image_path (Edm.String): ADLS path to extracted image
                            + is_multimodal (Edm.Boolean, filterable): flags multimodal chunks
                          → VLM model deployment for query-time image analysis
                          → Cross-modal graph edges (belongs_to, references) in vector store metadata
                          → Three query modes: text-only, VLM-enhanced, multimodal input
                          Read /rag-multimodal for full index schema and retrieval patterns
  "conversational"    → Vector store + embeddings + tool config + safety [FULL — RAG variant]
                        Inherits multimodal_rag conditional from RAG
  "doc-intelligence"  → Document parsing + structured extraction + safety [FULL — via /doc-intelligence]
                        Tier-based setup from requirements.ai.doc_intelligence_tier:
                          tier_1: Layout-aware parsing config (PaddleOCR models, DocRes restoration)
                          tier_2: Declarative extraction config (concept definitions, aspect hierarchy)
                          tier_3: Azure AI Document Intelligence (prebuilt model selection, custom training)
                        → Vector store for extracted data indexing (optional, based on publish_targets)
                        → Content Safety: block mode, PII redaction enabled
                        Read /doc-intelligence for tier-specific setup details
  "predictive-ml"     → ML model deployment + serving endpoint [FULL]
  "knowledge-graph"   → Graph store + GraphRAG retrieval + safety [FULL]
  "voice-text"        → Speech services + embeddings + signal extraction + safety [FULL]
                        → Model: Azure Speech-to-Text (standard or custom speech model)
                          - Verify Speech Service resource deployed (az cognitiveservices show)
                          - If requirements.pipeline.custom_speech_model: verify custom model endpoint
                          - Store Speech key in Key Vault (speech-api-key)
                        → Vector store: AI Search index for transcript chunks
                          - Standard 5-field schema + speaker_id (Edm.String, filterable)
                          - start_time/end_time (Edm.Double, sortable) for temporal search
                          - Semantic config on transcript content field
                        → Retrieval: hybrid search with speaker + time-range filters
                          - OData filter: speaker_id eq '{speaker}' and start_time ge {t1}
                          - Supports "What did {person} say about {topic}?" queries
                        → Content Safety: block mode, PII redaction enabled (call recordings)
                        → Signal extraction config (optional):
                          - Sentiment analysis on transcript chunks (Azure AI Language)
                          - Key phrase extraction for topic summarization
                          - Action item detection via LLM post-processing
  "multi-agent"       → Multi-model deployment + multi-retrieval [FULL]
                        If requirements.pipeline.agent_runtime == true:
                          Generate LLM registry with circular fallback (Azure AI Foundry models)
                          Generate long-term memory config (AI Search vector index with user_id scoping)
                          Generate observability setup (App Insights + Langfuse tracing callbacks)
                        If requirements.ai.eval_framework == true:
                          Generate LLM-as-Judge evaluator with 5 metrics (any archetype)
                        Read /agentic-deploy for fallback patterns, memory config, and eval framework
  "computer-vision"   → Vision model deployment + optional training pipeline + safety [FULL]
                        → Model: Azure AI Vision 4.0 (Image Analysis API)
                          - Verify AI Vision resource deployed (az cognitiveservices show)
                          - Multimodal embeddings endpoint (vectorizeImage, vectorizeText)
                          - Store Vision key in Key Vault (vision-api-key)
                        IF requirements.pipeline.vision_mode == "document":
                          → Vision extraction via /doc-intelligence
                            - Model: Claude Sonnet 4.6 or GPT-4o via Azure AI Foundry
                            - Verify Foundry endpoint + API key in Key Vault
                            - No vector store needed (structured extraction output)
                        IF requirements.pipeline.vision_mode == "classification":
                          → Vector store: AI Search index for image embeddings
                            - content_vector (1024 dims for Florence-2, 1536 for multimodal embeddings)
                            - image_path (Edm.String), labels (Collection(Edm.String), filterable)
                            - bounding_boxes (Edm.String, JSON-serialized)
                          → Retrieval: image similarity search (vectorizeImage → cosine)
                        IF requirements.pipeline.custom_vision_model:
                          → Azure ML workspace + compute cluster for Florence-2 fine-tuning
                          → Model registered in Azure ML registry
                          → Online endpoint for inference (Standard_NC6s_v3 GPU)
                        → Content Safety: monitor mode (no text generation to guard)
                          - Image content moderation via Azure AI Content Safety (hate, violence, sexual, self-harm)
                          - Severity threshold: medium (configurable)
```

### Step 3: Model Deployment Verification

For ALL archetypes that specify a primary model:

```bash
# Check if model deployment exists and is healthy
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{ai}/deployments/{deployment}?api-version=2024-10-01"

# Verify: status.provisioningState == "Succeeded"
# Verify: capacity matches requirements.ai.primary_model.capacity_tpm
```

If deployment is missing or unhealthy, deploy it using the template from `ai-ucb/infra-templates.md`.

Check embedding model similarly if `requirements.ai.embedding_model` is specified.

### Step 4: Vector Store Setup

**Dispatched by `requirements.ai.vector_store`:**

#### AI Search (default for RAG, Conversational, Doc Intelligence) [FULL]

```bash
# Read index config from contract
fields = ai_req["vector_index_config"]["fields"]
dimensions = ai_req["vector_index_config"]["dimensions"]
algorithm = ai_req["vector_index_config"]["algorithm"]
is_multimodal = ai_req.get("multimodal_rag", False)

# Create/update search index via REST API
SEARCH_KEY=$(az keyvault secret show --vault-name flk-{app}-kv-dev --name ai-search-admin-key --query value -o tsv)

# Standard fields (all archetypes)
standard_fields = [
    {"name": "chunk_id", "type": "Edm.String", "key": true, "filterable": true},
    {"name": "content", "type": "Edm.String", "searchable": true, "analyzerName": "en.microsoft"},
    {"name": "source_file_path", "type": "Edm.String", "filterable": true, "facetable": true},
    {"name": "chunk_index", "type": "Edm.Int32", "filterable": true, "sortable": true},
    {"name": "content_vector", "type": "Collection(Edm.Single)",
     "searchable": true, "vectorSearchDimensions": dimensions,
     "vectorSearchProfileName": "vector-profile"}
]

# Multimodal extension fields (when multimodal_rag == true)
# Read /rag-multimodal for full schema documentation
multimodal_fields = [
    {"name": "content_type", "type": "Edm.String", "filterable": true, "facetable": true},  # text|table|image|equation
    {"name": "page_idx", "type": "Edm.Int32", "filterable": true, "sortable": true},
    {"name": "image_path", "type": "Edm.String", "filterable": false},  # ADLS path to extracted image
    {"name": "is_multimodal", "type": "Edm.Boolean", "filterable": true}
]

all_fields = standard_fields + (multimodal_fields if is_multimodal else [])

PUT https://{search-service}.search.windows.net/indexes/{index-name}?api-version=2024-07-01
Headers: api-key: {SEARCH_KEY}
Body: {
  "name": "{index-name}",
  "fields": all_fields,
  "vectorSearch": {
    "algorithms": [{"name": "hnsw-algo", "kind": "hnsw",
      "hnswParameters": {"m": 4, "efConstruction": 400, "metric": "cosine"}}],
    "profiles": [{"name": "vector-profile", "algorithmConfigurationName": "hnsw-algo"}]
  },
  "semantic": {
    "configurations": [{
      "name": "semantic-config",
      "prioritizedFields": {"contentFields": [{"fieldName": "content"}]}
    }]
  }
}
```

#### Cosmos DB Vector [FULL]

```bash
# Create container with vector search policy
PUT https://{cosmos-account}.documents.azure.com/dbs/{db}/colls/{container}
Body: {
  "id": "{container}",
  "partitionKey": {"paths": ["/source_file_path"], "kind": "Hash"},
  "indexingPolicy": {
    "vectorIndexes": [{"path": "/content_vector", "type": "diskANN"}]
  },
  "vectorEmbeddingPolicy": {
    "vectorEmbeddings": [{
      "path": "/content_vector",
      "dataType": "float32",
      "distanceFunction": "cosine",
      "dimensions": {dimensions}
    }]
  }
}
```

#### None (Predictive ML, Computer Vision document-mode)

Skip vector store setup when archetype is `predictive-ml` or `computer-vision` with `vision_mode: "document"` (structured extraction doesn't need vector search). For `computer-vision` with `vision_mode: "classification"`, use AI Search with image embedding fields (see dispatcher).

### Step 5: Knowledge Graph Setup

**Dispatched by `requirements.ai.graph_store`:**

#### Cosmos DB Gremlin [FULL]

```bash
# Create Cosmos DB Gremlin API account, database, and graph container
COSMOS_ACCOUNT="flk-${app}-cosmos-${env}"
COSMOS_DB="${app}-graphdb"
COSMOS_GRAPH="knowledge"

# Create Gremlin database
az cosmosdb gremlin database create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group flk-${app}-${env}-rg \
  --name $COSMOS_DB

# Create graph container with partition key and indexing
az cosmosdb gremlin graph create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group flk-${app}-${env}-rg \
  --database-name $COSMOS_DB \
  --name $COSMOS_GRAPH \
  --partition-key-path "/pk" \
  --throughput 1000 \
  --idx @- <<'EOF'
{
  "indexingMode": "consistent",
  "automatic": true,
  "includedPaths": [{"path": "/*"}],
  "excludedPaths": [{"path": "/\"_etag\"/?"}],
  "compositeIndexes": [[
    {"path": "/vertex_type", "order": "ascending"},
    {"path": "/label", "order": "ascending"}
  ]]
}
EOF

# Store connection in Key Vault
COSMOS_KEY=$(az cosmosdb keys list --name $COSMOS_ACCOUNT \
  --resource-group flk-${app}-${env}-rg --query primaryMasterKey -o tsv)
COSMOS_ENDPOINT=$(az cosmosdb show --name $COSMOS_ACCOUNT \
  --resource-group flk-${app}-${env}-rg --query documentEndpoint -o tsv)
az keyvault secret set --vault-name kv-${app}-${env} \
  --name cosmos-gremlin-endpoint --value "$COSMOS_ENDPOINT"
az keyvault secret set --vault-name kv-${app}-${env} \
  --name cosmos-gremlin-key --value "$COSMOS_KEY"
```

Graph schema setup (from `requirements.ai.graph_schema`):

```python
# Run in Databricks after Cosmos DB is provisioned
# Creates vertex labels, edge labels, and property constraints
from gremlin_python.driver import client as gremlin_client

cosmos_endpoint = dbutils.secrets.get(f"kv-{app}", "cosmos-gremlin-endpoint")
cosmos_key = dbutils.secrets.get(f"kv-{app}", "cosmos-gremlin-key")

gc = gremlin_client.Client(
    f"wss://{cosmos_endpoint}:443/",
    "g",
    username=f"/dbs/{app}-graphdb/colls/knowledge",
    password=cosmos_key
)

# Vertex labels from graph_schema (example: entity types)
vertex_labels = graph_schema.get("vertex_labels", ["Document", "Entity", "Concept", "Person", "Organization"])
for label in vertex_labels:
    gc.submit(f"g.addV('{label}').property('id', 'schema_{label}').property('pk', '{label}').property('_is_schema', true)")

# Sample traversal queries (stored as artifacts for Phase 4)
sample_queries = {
    "neighbors": "g.V().has('id', '{entity_id}').both().limit(20)",
    "2hop": "g.V().has('id', '{entity_id}').repeat(both().simplePath()).times(2).dedup().limit(50)",
    "shared_connections": "g.V().has('id', '{e1}').both().where(both().has('id', '{e2}')).dedup()",
    "subgraph": "g.V().has('vertex_type', '{type}').outE().inV().path().limit(100)",
}
gc.close()
```

#### Neo4j Aura [FULL]

```bash
# Neo4j Aura deployment via Azure Marketplace (guided + automated config)
# Step 1: Guide user to deploy Neo4j Aura Professional from Marketplace
echo ">>> Deploy Neo4j Aura from Azure Marketplace:"
echo "    1. Go to portal.azure.com → Marketplace → search 'Neo4j Aura'"
echo "    2. Select Neo4j Aura Professional (or Enterprise)"
echo "    3. Resource group: flk-${app}-${env}-rg"
echo "    4. Region: ${region}"
echo "    5. After deployment, copy Bolt URI, username, password"

# Step 2: Store credentials in Key Vault
read -p "Neo4j Bolt URI: " NEO4J_URI
read -p "Neo4j Username: " NEO4J_USER
read -sp "Neo4j Password: " NEO4J_PASS
az keyvault secret set --vault-name kv-${app}-${env} --name neo4j-uri --value "$NEO4J_URI"
az keyvault secret set --vault-name kv-${app}-${env} --name neo4j-user --value "$NEO4J_USER"
az keyvault secret set --vault-name kv-${app}-${env} --name neo4j-password --value "$NEO4J_PASS"
```

Schema setup (run in Databricks after deployment):

```python
from neo4j import GraphDatabase

neo4j_uri = dbutils.secrets.get(f"kv-{app}", "neo4j-uri")
neo4j_user = dbutils.secrets.get(f"kv-{app}", "neo4j-user")
neo4j_pass = dbutils.secrets.get(f"kv-{app}", "neo4j-password")
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))

with driver.session() as session:
    # Uniqueness constraints on entity IDs
    vertex_labels = graph_schema.get("vertex_labels", ["Document", "Entity", "Concept"])
    for label in vertex_labels:
        session.run(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{label}) REQUIRE n.id IS UNIQUE")

    # Full-text index for text search across labels
    session.run("""
        CREATE FULLTEXT INDEX entitySearch IF NOT EXISTS
        FOR (n:Entity|Concept|Person|Organization)
        ON EACH [n.label, n.description]
    """)

    # Vector index for embedding-based retrieval (Neo4j 5.11+)
    session.run("""
        CREATE VECTOR INDEX entityEmbedding IF NOT EXISTS
        FOR (n:Entity) ON (n.embedding)
        OPTIONS {indexConfig: {
            `vector.dimensions`: 1536,
            `vector.similarity_function`: 'cosine'
        }}
    """)

    # Sample Cypher queries (stored as artifacts for Phase 4)
    sample_queries = {
        "neighbors": "MATCH (n {id: $entityId})-[r]-(m) RETURN n, r, m LIMIT 20",
        "2hop": "MATCH path = (n {id: $entityId})-[*1..2]-(m) RETURN path LIMIT 50",
        "shortest_path": "MATCH path = shortestPath((a {id: $e1})-[*..5]-(b {id: $e2})) RETURN path",
        "community": "MATCH (n {id: $entityId})-[r]-(m)-[r2]-(o) WHERE n <> o RETURN DISTINCT o LIMIT 30",
    }

driver.close()
```

### Step 6: ML Framework Setup

**Dispatched by `requirements.ai.ml_framework`:**

#### MLflow [FULL]

```python
# MLflow configuration in Databricks workspace
import mlflow
from mlflow.tracking import MlflowClient

# Create experiment with artifact location on ADLS
experiment_name = f"/Shared/{app}/ml-experiment"
artifact_uri = f"dbfs:/mnt/{app}/mlflow-artifacts"
mlflow.set_experiment(experiment_name)

client = MlflowClient()
experiment = client.get_experiment_by_name(experiment_name)

# Configure model registry aliases (staging → production promotion)
# After training (see pipeline-templates.md AI Layer: ML Training):
#   mlflow.xgboost.log_model(model, "model", registered_model_name=f"{stream}_model")
# Then promote:
#   client.set_registered_model_alias(f"{stream}_model", "staging", version)
#   client.set_registered_model_alias(f"{stream}_model", "production", version)

# Model serving endpoint (Databricks Model Serving)
# Creates REST endpoint for real-time inference
serving_config = {
    "name": f"{app}-serving",
    "config": {
        "served_models": [{
            "model_name": f"{app}_model",
            "model_version": "latest",
            "workload_size": "Small",
            "scale_to_zero_enabled": True
        }],
        "traffic_config": {
            "routes": [{"served_model_name": f"{app}_model", "traffic_percentage": 100}]
        }
    }
}

# Deploy via Databricks REST API
import requests
databricks_host = spark.conf.get("spark.databricks.workspaceUrl")
token = dbutils.secrets.get(f"kv-{app}", "databricks-token")
resp = requests.post(
    f"https://{databricks_host}/api/2.0/serving-endpoints",
    headers={"Authorization": f"Bearer {token}"},
    json=serving_config, timeout=60
)
print(f"Serving endpoint: {resp.status_code} - {resp.json().get('name', 'error')}")
```

#### Azure ML [FULL]

```bash
# Azure ML workspace, online endpoint, and monitoring setup
ML_WORKSPACE="flk-${app}-ml-${env}"
ML_RG="flk-${app}-${env}-rg"

# Verify workspace
az ml workspace show --name $ML_WORKSPACE --resource-group $ML_RG

# Create managed online endpoint
az ml online-endpoint create \
  --name ${app}-endpoint \
  --workspace-name $ML_WORKSPACE \
  --resource-group $ML_RG \
  --auth-mode key

# Create deployment with autoscaling
az ml online-deployment create \
  --name ${app}-deploy-v1 \
  --endpoint-name ${app}-endpoint \
  --workspace-name $ML_WORKSPACE \
  --resource-group $ML_RG \
  --model azureml:${app}_model@latest \
  --instance-type Standard_DS3_v2 \
  --instance-count 1 \
  --request-timeout-ms 30000

# Configure autoscaling (scale 1-5 instances based on CPU)
az monitor autoscale create \
  --resource-group $ML_RG \
  --name ${app}-autoscale \
  --min-count 1 --max-count 5 --count 1 \
  --resource $(az ml online-deployment show --name ${app}-deploy-v1 \
    --endpoint-name ${app}-endpoint --workspace-name $ML_WORKSPACE \
    --resource-group $ML_RG --query id -o tsv)

az monitor autoscale rule create \
  --resource-group $ML_RG \
  --autoscale-name ${app}-autoscale \
  --condition "CpuUtilizationPercentage > 70 avg 5m" \
  --scale out 1

az monitor autoscale rule create \
  --resource-group $ML_RG \
  --autoscale-name ${app}-autoscale \
  --condition "CpuUtilizationPercentage < 25 avg 10m" \
  --scale in 1

# Set up model monitoring (data drift detection)
az ml schedule create \
  --workspace-name $ML_WORKSPACE \
  --resource-group $ML_RG \
  --file @- <<'EOF'
$schema: https://azuremlschemas.azureedge.net/latest/schedule.schema.json
name: ${app}-drift-monitor
trigger:
  type: recurrence
  frequency: day
  interval: 1
create_monitor:
  compute:
    instance_type: standard_e4s_v3
  monitoring_target:
    ml_task: classification
    endpoint_deployment_id: azureml:${app}-endpoint:${app}-deploy-v1
  monitoring_signals:
    data_drift:
      type: data_drift
      production_data:
        input_data:
          type: uri_folder
          path: azureml:${app}-inference-logs:1
      reference_data:
        input_data:
          type: mltable
          path: azureml:${app}_training:1
      features: all_features
      metric_thresholds:
        - applicable_feature_type: numerical
          threshold: 0.3
  alert_notification:
    emails: [${alert_email}]
EOF

# Store endpoint key in Key Vault
ENDPOINT_KEY=$(az ml online-endpoint get-credentials \
  --name ${app}-endpoint --workspace-name $ML_WORKSPACE \
  --resource-group $ML_RG --query primaryKey -o tsv)
az keyvault secret set --vault-name kv-${app}-${env} \
  --name ml-endpoint-key --value "$ENDPOINT_KEY"
```

### Step 7: Retrieval Configuration

**Dispatched by `requirements.ai.retrieval_strategy`:**

#### Hybrid Search (RAG, Conversational) [FULL]

Configure the retrieval pipeline that the frontend will call:

```python
# Retrieval function template (saved as artifact for Phase 4)
def retrieve_context(query: str, top_k: int = 5, content_type_filter: str = None) -> list:
    """Hybrid search: vector + full-text + semantic reranker."""
    # 1. Generate query embedding
    embedding = embed(query)  # via AI Services

    # 2. Build filter (multimodal index supports content_type filtering)
    odata_filter = f"content_type eq '{content_type_filter}'" if content_type_filter else None

    # 3. Hybrid search (vector + keyword)
    results = search_client.search(
        search_text=query,
        vector_queries=[VectorizedQuery(vector=embedding, k_nearest_neighbors=top_k, fields="content_vector")],
        query_type="semantic",
        semantic_configuration_name="semantic-config",
        filter=odata_filter,
        top=top_k
    )

    # 4. Return ranked results with source attribution
    return [{"content": r["content"], "source": r["source_file_path"],
             "score": r["@search.score"],
             "content_type": r.get("content_type", "text"),
             "image_path": r.get("image_path")} for r in results]
```

#### VLM-Enhanced Retrieval (RAG with multimodal_rag == true) [FULL]

When `requirements.ai.multimodal_rag == true`, add VLM-enhanced retrieval alongside hybrid search.
Read `/rag-multimodal` for full implementation details.

```python
def retrieve_context_multimodal(query: str, top_k: int = 5) -> list:
    """Multimodal retrieval: text search + VLM image analysis + cross-modal graph."""
    # 1. Standard hybrid search across all content types
    text_results = retrieve_context(query, top_k=top_k)

    # 2. Find related images via cross-modal graph edges
    image_results = retrieve_context(query, top_k=3, content_type_filter="image")

    # 3. VLM-enhanced: analyze retrieved images with query context
    vlm_enhanced = []
    for img_result in image_results:
        if img_result.get("image_path"):
            # Call VLM (gpt-4.1 with vision) to analyze image in query context
            vlm_response = vlm_analyze(
                image_path=img_result["image_path"],
                query=query,
                surrounding_text=img_result["content"]
            )
            vlm_enhanced.append({
                "content": f"[Image Analysis] {vlm_response}",
                "source": img_result["source"],
                "score": img_result["score"] * 1.1,  # Boost VLM-enhanced results
                "content_type": "image_analysis",
                "image_path": img_result["image_path"]
            })

    # 4. Merge and deduplicate
    all_results = text_results + vlm_enhanced
    return sorted(all_results, key=lambda x: -x["score"])[:top_k * 2]
```

#### Graph Traversal (Knowledge Graph) [FULL]

GraphRAG: combine graph traversal context with vector retrieval for grounded answers.

```python
def retrieve_context_graphrag(query: str, top_k: int = 5) -> list:
    """GraphRAG: entity extraction → graph traversal → vector search → merge."""
    from azure.ai.textanalytics import TextAnalyticsClient
    from neo4j import GraphDatabase

    # 1. Extract entities from query using Azure AI Language
    ta_client = TextAnalyticsClient(endpoint=ai_endpoint, credential=credential)
    entities = ta_client.recognize_entities([query])[0].entities
    entity_names = [e.text for e in entities if e.confidence_score > 0.7]

    # 2. Graph traversal: find 2-hop neighborhood of matched entities
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_pass))
    graph_context = []
    with driver.session() as session:
        for entity_name in entity_names:
            result = session.run("""
                MATCH (n)-[r]-(m)
                WHERE n.label CONTAINS $name
                WITH n, r, m LIMIT 10
                OPTIONAL MATCH (m)-[r2]-(o)
                WHERE o <> n
                RETURN n.label AS source, type(r) AS rel, m.label AS target,
                       collect(DISTINCT o.label)[..5] AS extended
                LIMIT 20
            """, name=entity_name)
            for record in result:
                graph_context.append({
                    "source": record["source"],
                    "relationship": record["rel"],
                    "target": record["target"],
                    "extended": record["extended"]
                })
    driver.close()

    # 3. Vector search for document chunks (same as hybrid search)
    embedding = embed(query)
    vector_results = search_client.search(
        search_text=query,
        vector_queries=[VectorizedQuery(vector=embedding, k_nearest_neighbors=top_k, fields="content_vector")],
        top=top_k
    )

    # 4. Merge: graph context prepended to vector results
    graph_summary = "\n".join(
        f"- {g['source']} --[{g['relationship']}]--> {g['target']}"
        for g in graph_context[:15]
    )
    results = [{"content": f"[Graph Context]\n{graph_summary}", "source": "knowledge-graph", "score": 1.0}]
    results += [{"content": r["content"], "source": r["source_file_path"], "score": r["@search.score"]}
                for r in vector_results]
    return results
```

#### Feature Lookup (Predictive ML) [FULL]

Serves features from Delta tables for real-time and batch inference.

```python
def retrieve_features(entity_id: str, feature_table: str) -> dict:
    """Look up pre-computed features from Gold Delta table for inference."""
    # Batch mode: read from Delta table directly
    features = spark.table(f"flukebi_Gold.{feature_table}") \
        .filter(f"entity_id = '{entity_id}'") \
        .first()

    if features is None:
        raise ValueError(f"No features found for entity {entity_id}")

    return features.asDict()

def predict_online(entity_id: str, feature_table: str, endpoint_name: str) -> dict:
    """Real-time prediction: fetch features → call serving endpoint."""
    import requests

    # 1. Get features
    features = retrieve_features(entity_id, feature_table)
    feature_cols = [k for k in features.keys() if k != "entity_id"]
    input_data = {k: features[k] for k in feature_cols}

    # 2. Call model serving endpoint (Databricks or Azure ML)
    scoring_uri = dbutils.secrets.get(f"kv-{app}", "ml-endpoint-url")
    endpoint_key = dbutils.secrets.get(f"kv-{app}", "ml-endpoint-key")
    resp = requests.post(
        scoring_uri,
        headers={"Authorization": f"Bearer {endpoint_key}", "Content-Type": "application/json"},
        json={"instances": [input_data]}, timeout=30
    )
    resp.raise_for_status()
    return {"entity_id": entity_id, "prediction": resp.json()["predictions"][0]}
```

#### Multi-Source (Multi-Agent) [FULL]

Routes queries to the appropriate retrieval strategy based on agent role.

```python
def retrieve_context_multi(query: str, agent_role: str, top_k: int = 5) -> list:
    """Router: selects retrieval strategy based on the active agent's role."""
    strategy_map = {
        "research":    ["vector_search", "graph_traversal"],
        "analyst":     ["feature_lookup", "vector_search"],
        "support":     ["vector_search"],
        "coordinator": ["vector_search", "graph_traversal", "api_lookup"],
    }

    strategies = strategy_map.get(agent_role, ["vector_search"])
    all_results = []

    for strategy in strategies:
        if strategy == "vector_search":
            results = retrieve_context(query, top_k=top_k)
            all_results.extend(results)
        elif strategy == "graph_traversal":
            results = retrieve_context_graphrag(query, top_k=top_k)
            all_results.extend(results)
        elif strategy == "feature_lookup":
            # Extract entity ID from query context
            entity_id = extract_entity_id(query)
            if entity_id:
                features = retrieve_features(entity_id, f"{app}_features")
                all_results.append({
                    "content": f"[Features] {json.dumps(features, default=str)}",
                    "source": "feature-store",
                    "score": 1.0
                })
        elif strategy == "api_lookup":
            # Call external APIs registered for this agent
            api_results = call_registered_apis(agent_role, query)
            all_results.extend(api_results)

    # Deduplicate and rank by score
    seen = set()
    unique = []
    for r in sorted(all_results, key=lambda x: -x.get("score", 0)):
        key = r["content"][:100]
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique[:top_k * 2]
```

### Step 8: Content Safety Configuration (ALL Archetypes)

**Read** `ai-ucb/governance.md` for configuration templates.

This step runs for EVERY archetype — Content Safety is not optional.

#### 8.1 Content Safety SDK Setup

```python
# pip install azure-ai-contentsafety azure-ai-textanalytics
from azure.ai.contentsafety import ContentSafetyClient
from azure.ai.contentsafety.models import (
    AnalyzeTextOptions, TextCategory,
    ShieldPromptOptions, ShieldPromptResult,
)
from azure.core.credentials import AzureKeyCredential
import os

safety_client = ContentSafetyClient(
    endpoint=os.environ["CONTENT_SAFETY_ENDPOINT"],
    credential=AzureKeyCredential(os.environ["CONTENT_SAFETY_KEY"]),
)
```

#### 8.2 Input Guard — Prompt Shields (ALL Archetypes)

```python
def check_input(user_message: str, documents: list[str] = None) -> dict:
    """Run Prompt Shields on user input. Call BEFORE sending to LLM."""
    # Prompt Shields: detect jailbreak + indirect injection
    shield_result = safety_client.shield_prompt(
        ShieldPromptOptions(
            user_prompt=user_message,
            documents=documents or [],  # Retrieved docs for indirect injection check
        )
    )

    blocked = False
    reasons = []

    if shield_result.user_prompt_analysis and shield_result.user_prompt_analysis.attack_detected:
        blocked = True
        reasons.append("jailbreak_detected")

    if shield_result.documents_analysis:
        for i, doc_analysis in enumerate(shield_result.documents_analysis):
            if doc_analysis.attack_detected:
                blocked = True
                reasons.append(f"indirect_injection_in_doc_{i}")

    # Text moderation: 4 harm categories
    text_result = safety_client.analyze_text(
        AnalyzeTextOptions(
            text=user_message,
            categories=[TextCategory.HATE, TextCategory.VIOLENCE,
                       TextCategory.SEXUAL, TextCategory.SELF_HARM],
        )
    )
    for cat in text_result.categories_analysis:
        if cat.severity >= 4:  # 0-6 scale, 4+ = medium-high
            blocked = True
            reasons.append(f"harmful_content_{cat.category}")

    return {"blocked": blocked, "reasons": reasons}
```

#### 8.3 Output Guard — Groundedness + Protected Material

```python
def check_output(llm_response: str, grounding_sources: list[str], mode: str = "block") -> dict:
    """Run output checks AFTER LLM generates response."""
    result = {"blocked": False, "reasons": [], "warnings": []}

    # Groundedness detection (RAG, Conversational, KG, Multi-Agent)
    if grounding_sources:
        ground_result = safety_client.detect_groundedness(
            domain="Generic",
            task="QnA",
            text=llm_response,
            grounding_sources=grounding_sources,
            reasoning=True,
        )
        if ground_result.ungrounded_detected:
            pct = ground_result.ungrounded_percentage
            if pct > 0.5 and mode == "block":
                result["blocked"] = True
                result["reasons"].append(f"ungrounded_{pct:.0%}")
            elif pct > 0.2:
                result["warnings"].append(f"partially_ungrounded_{pct:.0%}")

    # Text moderation on output (catch harmful generation)
    text_result = safety_client.analyze_text(
        AnalyzeTextOptions(text=llm_response[:10000])  # API limit
    )
    for cat in text_result.categories_analysis:
        if cat.severity >= 4:
            result["blocked"] = True
            result["reasons"].append(f"harmful_output_{cat.category}")

    return result
```

#### 8.4 PII Redaction (When Enabled)

```python
from azure.ai.textanalytics import TextAnalyticsClient

def redact_pii(text: str, categories: list = None) -> str:
    """Redact PII from text before storage or display."""
    ta_client = TextAnalyticsClient(
        endpoint=os.environ["LANGUAGE_ENDPOINT"],
        credential=AzureKeyCredential(os.environ["LANGUAGE_KEY"]),
    )
    result = ta_client.recognize_pii_entities(
        [text],
        categories_filter=categories,  # e.g., ["Email", "PhoneNumber", "SSN"]
    )
    doc = result[0]
    if not doc.is_error:
        return doc.redacted_text
    return text  # Return original if PII detection fails
```

#### 8.5 Custom Blocklists (Domain-Specific)

```bash
# Create custom blocklist for domain-specific blocked terms
BLOCK_LIST_NAME="flk-${APP_SLUG}-blocklist"

curl -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "${CS_ENDPOINT}/contentsafety/text/blocklists/${BLOCK_LIST_NAME}?api-version=2024-09-01" \
  -d '{"description": "Domain-specific blocked terms for '${APP_SLUG}'"}'

# Add blocked items
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "${CS_ENDPOINT}/contentsafety/text/blocklists/${BLOCK_LIST_NAME}:addOrUpdateBlocklistItems?api-version=2024-09-01" \
  -d '{"blocklistItems": [
    {"description": "Competitor product", "text": "{competitor_term}"},
    {"description": "Internal codename", "text": "{internal_codename}"}
  ]}'
```

#### 8.6 Integration Pattern — Request Pipeline

Wire input/output guards into the application request pipeline:

```python
def handle_chat_request(user_message: str, history: list) -> dict:
    """Full request pipeline with Content Safety guards."""
    # STEP 1: Input guard (before ANY LLM call)
    input_check = check_input(user_message)
    if input_check["blocked"]:
        return {"response": "I can't process that request.", "blocked": True,
                "reasons": input_check["reasons"]}

    # STEP 2: Retrieve context
    context, sources = build_context(user_message)

    # STEP 3: Check retrieved docs for indirect injection
    doc_check = check_input(user_message, documents=[s["content"] for s in sources])
    if doc_check["blocked"]:
        return {"response": "A retrieved document triggered safety filters.",
                "blocked": True, "reasons": doc_check["reasons"]}

    # STEP 4: Generate LLM response
    response = call_llm(user_message, context, history)

    # STEP 5: Output guard (before returning to user)
    output_check = check_output(response, grounding_sources=[context])
    if output_check["blocked"]:
        return {"response": "The generated response did not meet safety standards.",
                "blocked": True, "reasons": output_check["reasons"]}

    # STEP 6: PII redaction (if enabled)
    if ai_req["content_safety"].get("pii_redaction"):
        response = redact_pii(response)

    return {"response": response, "sources": sources, "warnings": output_check.get("warnings", [])}
```

**Safety mode per archetype:**

| Archetype | Default Mode | Prompt Shields | Groundedness | PII Redaction | Custom Blocklist |
|-----------|-------------|----------------|-------------|---------------|-----------------|
| RAG | block | yes | yes | yes | optional |
| Conversational | block | yes | yes | yes | optional |
| Doc Intelligence | block | yes | no | yes | no |
| Predictive ML | monitor | yes | no | no | no |
| Knowledge Graph | monitor | yes | yes (GraphRAG) | depends | no |
| Voice/Text | block | yes | no | yes | optional |
| Multi-Agent | block | yes | yes | yes | optional |
| Computer Vision | monitor | yes (text inputs) | no | no | no |

**Key rule:** Prompt Shields runs for ALL archetypes, even monitor-mode ones. The difference is whether harmful content blocks the response (`block`) or just logs it (`monitor`).

### Step 9: Prompt Optimization (Optional — P1 Enhancement)

**If systematic prompt engineering is needed**, use DSPy or Azure AI Promptflow.

#### DSPy — Algorithmic Prompt Optimization

```python
# pip install dspy-ai
import dspy

# Configure Azure OpenAI as the LM
lm = dspy.AzureOpenAI(
    api_base=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    deployment_id="gpt-4.1",
    api_version="2024-10-01",
)
dspy.settings.configure(lm=lm)

# Define a RAG module with learnable prompts
class RAGAnswer(dspy.Module):
    def __init__(self):
        self.retrieve = dspy.Retrieve(k=5)
        self.generate = dspy.ChainOfThought("context, question -> answer")

    def forward(self, question):
        context = self.retrieve(question).passages
        return self.generate(context=context, question=question)

# Compile (optimize) prompts from examples
from dspy.teleprompt import BootstrapFewShot

trainset = [
    dspy.Example(question="What is the accuracy of the Fluke 87V?",
                 answer="The Fluke 87V has DC accuracy of ±0.05% + 1 digit."),
    # ... 10-20 examples from domain experts
]

optimizer = BootstrapFewShot(metric=dspy.evaluate.answer_exact_match)
compiled_rag = optimizer.compile(RAGAnswer(), trainset=trainset)

# Save optimized prompts
compiled_rag.save("optimized_rag_prompts.json")
```

#### Azure Promptflow — Visual Prompt Workflow

```bash
# pip install promptflow promptflow-azure
# Promptflow integrates with Azure AI Foundry for:
# - Visual DAG-based prompt flow design
# - Built-in evaluation nodes
# - Versioned prompt management
# - One-click deployment to Azure App Service

pf flow init --flow rag-flow --type chat
pf flow test --flow rag-flow --inputs question="What is Fluke?"
pf run create --flow rag-flow --data test_data.jsonl --name eval_run_1
```

**When to use:**
- DSPy: When you have 10+ examples and want automated prompt optimization
- Promptflow: When you need visual flow design and Azure-native deployment
- Neither: For most projects, well-crafted manual prompts are sufficient

### Step 10: Retrieval Quality Testing

**For RAG/Conversational (FULL):**

```python
# Run 5 sample queries against the vector store
test_queries = [
    "What is {relevant_topic}?",
    "How does {process} work?",
    "Tell me about {entity}",
    "What are the requirements for {task}?",
    "Compare {A} and {B}"
]

for query in test_queries:
    results = retrieve_context(query, top_k=3)
    print(f"Query: {query}")
    print(f"  Top result: {results[0]['content'][:100]}...")
    print(f"  Score: {results[0]['score']}")
    print(f"  Source: {results[0]['source']}")
```

**For all archetypes:** Verify configuration exists (model deployed, index created, container exists) and run archetype-appropriate smoke tests.

### Step 11: Present Report and Gate

```
AI SETUP REPORT — {project_name}
═══════════════════════════════════

Archetype: {archetype}
Template Status: FULL (all archetypes production-ready)

Model Deployments:
| Model | Deployment | Capacity | Status |
|-------|-----------|----------|--------|
| {primary_model} | {deployment} | {tpm} TPM | Healthy |
| {embedding_model} | {deployment} | {tpm} TPM | Healthy |

Vector Store: {type}
  Index: {index_name}
  Dimensions: {dimensions}
  Algorithm: {algorithm}
  Fields: {field_count}

Knowledge Graph: {type or "none"}
ML Framework: {type or "none"}

Retrieval Strategy: {strategy}
  Sample Results: {pass/fail summary}

Content Safety:
  Mode: {mode}
  Prompt Shields: Enabled
  Groundedness: {enabled/disabled}
  PII Redaction: {enabled/disabled}
  Test Results: {pass/fail}

```

Update state: `phases.ai = "completed"`, `artifacts.ai_config`

Ask:
> **GATE: Phase 3 AI Setup complete.** Models verified, {vector/graph} store configured, Content Safety enabled. Shall I proceed to Phase 4 (Frontend)?

---

## AI Setup Anti-Patterns (NEVER Do These)

1. **NEVER skip Content Safety configuration.** Every archetype gets Prompt Shields. No exceptions.
2. **NEVER use cosine similarity with unnormalized embeddings.** text-embedding-3-large outputs normalized vectors — cosine is correct. If using a different model, verify normalization.
3. **NEVER create AI Search indexes without semantic search enabled.** Standard tier includes it — always configure `semantic.configurations`.
4. **NEVER hard-code embedding dimensions.** Read from `requirements.ai.vector_index_config.dimensions`. Models may change.
5. **NEVER skip the integration check between Phase 2 AI Layer notebooks and Phase 3 index schema.** The embedding dimensions and field names MUST match.
6. **NEVER deploy graph databases without partition key planning.** Cosmos Gremlin requires `/pk` partition. Neo4j requires index design. Bad partitioning = poor performance.
7. **NEVER configure retrieval without testing.** Even a basic 3-query smoke test catches schema mismatches before the frontend phase.
8. **NEVER check only input OR only output.** Content Safety requires BOTH input guards (Prompt Shields + text moderation) AND output guards (groundedness + text moderation). Checking only input misses harmful generation; checking only output misses jailbreaks.
9. **NEVER fail open when Content Safety is down.** If the Content Safety API returns 503, block the request (fail closed). A user-facing AI system without safety is worse than one that's temporarily unavailable.
10. **NEVER skip indirect injection checks on retrieved documents.** Adversarial content embedded in indexed documents can hijack the system prompt. Always pass retrieved docs through Prompt Shields.

## Error Recovery

| Error | Recovery |
|-------|---------|
| AI Search index creation fails (400) | Check field names for reserved words, verify dimensions match model |
| Cosmos DB vector policy rejected | Verify API version supports vector search (2024-05-15+) |
| Model deployment capacity unavailable | Try secondary region, reduce TPM, or use alternative model |
| Content Safety API 403 | Verify Content Safety resource provisioned, MI needs `Cognitive Services User` role |
| Content Safety API 503 | Fail closed (block requests), check service health, retry after 60s |
| Embedding dimension mismatch | Update index to match model output, re-embed if needed |
| Neo4j Aura connection timeout | Check firewall rules, verify bolt URI format |
| Groundedness false positives | Lower ungrounded_percentage threshold, add more context to grounding sources |
| PII redaction over-aggressive | Narrow `categories_filter` to only the PII types relevant to your domain |
| Blocklist not propagating | Custom blocklists take up to 5 minutes to propagate. Wait and retry. |
