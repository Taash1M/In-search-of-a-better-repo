---
name: ubi-neo4j-skill
description: Use when building, maintaining, querying, or optimizing Neo4j knowledge graphs from the UBI Gold Layer data (431 tables in Fabric Lakehouse). Covers structured data import, unstructured data ingestion (GraphRAG), Cypher queries, graph modeling, data mesh patterns, graph optimization, and prototyping with free tools.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Task, Agent, WebFetch, WebSearch
---

# UBI Neo4j Developer Skill

You are an expert Neo4j graph database developer working with the Fluke UBI (Unified Business Intelligence) data estate. This skill covers building enterprise knowledge graphs from 431 Gold layer tables, implementing GraphRAG patterns, and maintaining graph infrastructure.

## Access Control Rules (MANDATORY)

1. **Read-only access to production data.** Never write, update, or delete data in the Fabric Gold Lakehouse, Databricks prod, or ADLS prod.
2. **Graph writes only to local/dev Neo4j instances.** All graph creation, modification, and deletion targets local prototyping environments or dev instances.
3. **No secrets in code or artifacts.** Connection strings, API keys, and passwords go in `.env` files or environment variables — never hardcoded.
4. **All artifacts** saved to `C:\Users\tmanyang\OneDrive - Fortive\AI\Neo4j\UBI Gold Graph\`

## Gold Layer Data Source

### Fabric Lakehouse Connection

| Detail | Value |
|---|---|
| Lakehouse | `FLK_UBI_LH_GOLDS` |
| Lakehouse ID | `0a252e47-a44f-4002-8d96-4cbdb8dc1951` |
| Workspace ID | `4037a9f7-9627-4b77-a7bb-ae42bbdaf1bc` |
| SQL Endpoint | `ynfggd47woteda52r4ihq5wgsi-66utoqbhsz3uxj53vzblxwxrxq.datawarehouse.fabric.microsoft.com` |
| Database | `FLK_UBI_LH_GOLDS` |
| Tables | 431 (all Delta format) |
| Access | Fabric REST API via Azure AD token |

### Table Inventory by Domain

| Domain | ~Count | Key Tables |
|---|---|---|
| CRM | 80 | DimCRMAccount, DimCRMContact, FactCRMOpportunity, FactCRMLead, FactCRMIncident |
| Orders/Sales | 40 | FactOrders, FactOrderDetails, FactBacklog, FactSOBacklog_SOB, FactShipment |
| Inventory | 30 | DimInvItem, DimInvOrgs, FactOnHandDetails_*, FactInvReservations_* |
| Procurement | 20 | DimProcSupplier, FactProcPPV, FactProcSpend, FactProcurement |
| AR | 10 | DimAccountReceivables*, FactARInstallments_Snapshots |
| Service/Repair | 20 | DimServiceCenter, FactRepairOrder, WorkRepairNotes |
| VOC | 30 | factvoclines, voc* views |
| Finance/GL | 10 | DimGLAccount, DimGeneralLedger_WC |
| Warranty | 5 | FactWarrantyCost |
| POS | 5 | FactPointofSales |
| Calendar | 15 | DimCalendar, DimCalendar_* |
| Product | 15 | DimProduct, DimInvProductHierarchy |
| Geography | 10 | DimCountry, DimGeo, DimOneFlukeRegion |
| Organization | 10 | DimOrg, DimOrgStructure |
| Currency | 5 | DimCurrency, CurrencyExchangeRate* |
| WIP/Mfg | 10 | FactWIPJobs, DimBOM* |
| AI views | 15 | *_AI suffix (CRM, Orders analytics) |

### Gold View Source Code

SQL/Python definitions at `C:\Users\tmanyang\AzureDataBricks\FlukeCoreGrowth\Mart\Refresh\Refresh_*_Gold.{sql,py}`. These reveal JOIN patterns, column sources, and inter-table relationships — essential for graph modeling.

---

## Graph Data Modeling

### Core Principles

1. **Entities = Nouns** → Node labels (Customer, Product, Order, Invoice, etc.)
2. **Relationships = Verbs** → Edge types (PLACED_ORDER, SOLD_TO, MANUFACTURED_BY, etc.)
3. **Properties = Attributes** → Key-value pairs on nodes and edges
4. **Start with the question** → Model your graph to answer the business questions you care about
5. **Whiteboard-friendly** → If you can draw it on a whiteboard, it's a valid graph model

### UBI Domain Model Strategy

The Gold layer follows a star/snowflake schema (Dim + Fact tables). Converting to a graph model:

```
STAR SCHEMA → GRAPH MODEL MAPPING
─────────────────────────────────
Dimension table    → Node label (e.g., DimCRMAccount → :Customer)
Fact table         → Relationship OR intermediate node
Foreign key        → Relationship
Measure columns    → Properties on relationship or node
Bridge table       → Relationship with properties
Calendar dimension → :Date node or property on relationship
Hierarchy          → Chain of relationships (Country → Region → Territory)
```

### Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Node labels | PascalCase, singular | `:Customer`, `:Product`, `:Order` |
| Relationship types | UPPER_SNAKE_CASE, active verb | `:PLACED_ORDER`, `:SOLD_TO` |
| Properties | camelCase | `customerName`, `orderDate`, `totalAmount` |
| Unique identifiers | Use source system IDs | `crmAccountId`, `ebsCustomerId` |

### Graph Model Patterns for Enterprise Data

**Pattern 1: Dimension-to-Dimension Relationships**
```cypher
// Instead of joining through a fact table:
(:Customer)-[:LOCATED_IN]->(:Country)-[:IN_REGION]->(:Region)
(:Customer)-[:HAS_INDUSTRY]->(:Industry)
(:Product)-[:IN_CATEGORY]->(:ProductCategory)-[:IN_HIERARCHY]->(:ProductHierarchy)
```

**Pattern 2: Fact as Relationship**
```cypher
// Simple facts become relationships with properties
(:Customer)-[:PLACED_ORDER {orderDate: date('2026-01-15'), amount: 1500.00}]->(:Product)
```

**Pattern 3: Fact as Intermediate Node (for complex facts)**
```cypher
// Complex facts with many dimensions become nodes
(:Customer)-[:PLACED]->(:Order {orderId: 'SO123', orderDate: date('2026-01-15')})
(:Order)-[:CONTAINS]->(:OrderLine {quantity: 5, unitPrice: 300.00})
(:OrderLine)-[:FOR_PRODUCT]->(:Product)
(:Order)-[:SHIPPED_TO]->(:Address)
(:Order)-[:IN_CURRENCY]->(:Currency)
```

**Pattern 4: Temporal Patterns**
```cypher
// Snapshot data as versioned relationships
(:Customer)-[:HAD_BALANCE {asOfDate: date('2026-01-31'), amount: 50000}]->(:Account)
// Or as temporal nodes
(:Customer)-[:HAS_SNAPSHOT]->(:CustomerSnapshot {snapshotDate: date('2026-01-31'), balance: 50000})
```

**Pattern 5: Cross-Domain Connections (the graph's superpower)**
```cypher
// Connections that are invisible in star schemas:
(:Customer)-[:PLACED]->(:Order)-[:CONTAINS]->(:OrderLine)-[:FOR_PRODUCT]->(:Product)
(:Product)-[:MANUFACTURED_AT]->(:Plant)-[:IN_COUNTRY]->(:Country)
(:Customer)-[:FILED_COMPLAINT]->(:VOCCase)-[:ABOUT_PRODUCT]->(:Product)
(:Customer)-[:HAS_WARRANTY]->(:WarrantyClaim)-[:FOR_PRODUCT]->(:Product)
// Now you can traverse: Customer → Order → Product → VOC → Warranty in one query
```

---

## Cypher Query Language Reference

### Basics

```cypher
// Create nodes
CREATE (c:Customer {name: 'Fluke Corp', id: 'CRM001'})

// Create relationships
MATCH (c:Customer {id: 'CRM001'}), (p:Product {id: 'PROD001'})
CREATE (c)-[:PURCHASED {date: date('2026-01-15'), qty: 10}]->(p)

// Read patterns
MATCH (c:Customer)-[:PURCHASED]->(p:Product)
WHERE c.name CONTAINS 'Fluke'
RETURN c.name, p.name, count(*) AS purchases
ORDER BY purchases DESC

// Update
MATCH (c:Customer {id: 'CRM001'})
SET c.lastUpdated = datetime()

// Delete (careful!)
MATCH (c:Customer {id: 'CRM001'})-[r]-()
DELETE r, c
```

### Advanced Patterns

```cypher
// Variable-length paths (1 to 5 hops)
MATCH path = (c:Customer)-[*1..5]->(p:Product)
RETURN path

// Shortest path
MATCH path = shortestPath((a:Customer)-[*]-(b:Customer))
WHERE a.id = 'CRM001' AND b.id = 'CRM002'
RETURN path

// Aggregation with COLLECT
MATCH (c:Customer)-[:PLACED]->(:Order)-[:CONTAINS]->(ol:OrderLine)-[:FOR_PRODUCT]->(p:Product)
RETURN c.name, collect(DISTINCT p.name) AS products, sum(ol.amount) AS totalSpend

// UNWIND for batch operations
UNWIND $rows AS row
MERGE (c:Customer {id: row.id})
SET c.name = row.name, c.country = row.country

// APOC for batch loading (if available)
CALL apoc.periodic.iterate(
  'MATCH (c:Customer) WHERE c.needsUpdate = true RETURN c',
  'SET c.processed = true',
  {batchSize: 10000}
)
```

### Indexing for Performance

```cypher
// Unique constraint (also creates index)
CREATE CONSTRAINT customer_id IF NOT EXISTS
FOR (c:Customer) REQUIRE c.id IS UNIQUE

// Composite index
CREATE INDEX customer_country_idx IF NOT EXISTS
FOR (c:Customer) ON (c.country, c.region)

// Full-text index
CREATE FULLTEXT INDEX customer_name_ft IF NOT EXISTS
FOR (c:Customer) ON EACH [c.name, c.alternateName]

// Vector index (for GraphRAG)
CREATE VECTOR INDEX chunk_embedding IF NOT EXISTS
FOR (c:Chunk) ON c.embedding
OPTIONS {indexConfig: {
  `vector.dimensions`: 1536,
  `vector.similarity_function`: 'cosine'
}}
```

---

## Structured Data Import

### From CSV/Parquet (Batch Load)

```python
from neo4j import GraphDatabase
import pandas as pd

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def load_nodes(tx, rows, label, id_prop):
    """Batch load nodes using UNWIND."""
    query = f"""
    UNWIND $rows AS row
    MERGE (n:{label} {{{id_prop}: row.{id_prop}}})
    SET n += row
    """
    tx.run(query, rows=rows)

def load_relationships(tx, rows, src_label, src_id, rel_type, tgt_label, tgt_id):
    """Batch load relationships using UNWIND."""
    query = f"""
    UNWIND $rows AS row
    MATCH (a:{src_label} {{{src_id}: row.src_id}})
    MATCH (b:{tgt_label} {{{tgt_id}: row.tgt_id}})
    MERGE (a)-[r:{rel_type}]->(b)
    SET r += row.props
    """
    tx.run(query, rows=rows)

# Load in batches of 5000
BATCH_SIZE = 5000
df = pd.read_parquet('customers.parquet')
rows = df.to_dict('records')

with driver.session() as session:
    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i+BATCH_SIZE]
        session.execute_write(load_nodes, batch, 'Customer', 'customerId')
```

### From Fabric Lakehouse (via REST API + Delta)

```python
import json, urllib.request, subprocess

def get_fabric_token():
    """Get Azure AD token for Fabric API."""
    return subprocess.check_output(
        ["az", "account", "get-access-token",
         "--resource", "https://analysis.windows.net/powerbi/api",
         "--query", "accessToken", "-o", "tsv"],
        text=True
    ).strip()

def list_lakehouse_tables(workspace_id, lakehouse_id):
    """Enumerate all tables in the Fabric Lakehouse."""
    token = get_fabric_token()
    tables = []
    url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/lakehouses/{lakehouse_id}/tables"
    while url:
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
        tables.extend(data.get("data", []))
        url = data.get("continuationUri")
    return tables

# Usage
WORKSPACE = "4037a9f7-9627-4b77-a7bb-ae42bbdaf1bc"
LAKEHOUSE = "0a252e47-a44f-4002-8d96-4cbdb8dc1951"
tables = list_lakehouse_tables(WORKSPACE, LAKEHOUSE)
```

### Data Importer (Neo4j Aura UI)

For quick prototyping, use Neo4j's Data Importer:
1. Export Gold tables as CSVs
2. Navigate to Import > Data Importer in Neo4j Aura console
3. Map columns to node labels and properties
4. Define relationships by dragging between nodes
5. Set unique ID (key) property for each node type
6. Click Run Import

**CRITICAL**: Property names must match exactly (case-sensitive) between structured and unstructured imports.

---

## Unstructured Data Ingestion (GraphRAG)

### Knowledge Graph from Documents

```python
from neo4j import GraphDatabase
from neo4j_graphrag.experimental.pipeline.kg_builder import SimpleKGPipeline
from neo4j_graphrag.llm import OpenAILLM  # or AzureOpenAILLM
from neo4j_graphrag.embeddings import OpenAIEmbeddings
import asyncio

# Connect
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Initialize LLM and embedder
llm = OpenAILLM(model_name="gpt-4o", api_key=OPENAI_API_KEY)
embedder = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

# Define schema — ENTITIES = NOUNS, RELATIONS = VERBS
entities = [
    {"label": "Customer", "properties": [{"name": "name", "type": "STRING"}]},
    {"label": "Product", "properties": [{"name": "name", "type": "STRING"}]},
    {"label": "Issue", "properties": [{"name": "description", "type": "STRING"}]},
]
relations = [
    {"label": "REPORTED", "source": "Customer", "target": "Issue"},
    {"label": "AFFECTS", "source": "Issue", "target": "Product"},
]

# Build pipeline
pipeline = SimpleKGPipeline(
    driver=driver, llm=llm, embedder=embedder,
    entities=entities, relations=relations,
    enforce_schema=True  # IMPORTANT: prevents schema drift
)

# Process documents
async def ingest(file_path):
    await pipeline.run_async(pdf_path=file_path)

asyncio.run(ingest("customer_feedback.pdf"))
```

### Vector Index for Semantic Search

```python
from neo4j_graphrag.indexes import create_vector_index

create_vector_index(
    driver, name="chunkEmbeddings", label="Chunk",
    embedding_property="embedding", dimensions=1536,
    similarity_fn="cosine"
)
```

### GraphRAG Retrieval Patterns

**Pattern 1: Basic Vector Search** — semantic similarity on chunk embeddings
```python
from neo4j_graphrag.retrievers import VectorRetriever
from neo4j_graphrag.generation import GraphRAG

retriever = VectorRetriever(driver, index_name="chunkEmbeddings",
                            embedder=embedder, return_properties=["text"])
rag = GraphRAG(llm=llm, retriever=retriever)
result = rag.search(query_text="What are the top product quality issues?")
```

**Pattern 2: Graph-Enhanced Vector Search (VectorCypherRetriever)** — the power pattern
```python
from neo4j_graphrag.retrievers import VectorCypherRetriever

# Traverse from chunk → document → customer → products
traversal_query = """
WITH node
MATCH (node)-[:FROM_DOCUMENT]-(doc:Document)-[:ABOUT]-(c:Customer)-[:PURCHASED]->(p:Product)
RETURN c.name AS customer, collect(DISTINCT p.name) AS products, node.text AS context
"""

retriever = VectorCypherRetriever(
    driver=driver, index_name="chunkEmbeddings",
    embedder=embedder, retrieval_query=traversal_query
)
```

**Pattern 3: Text2Cypher** — natural language to Cypher (great for exploration, not for production)
```python
from neo4j_graphrag.retrievers import Text2CypherRetriever
from neo4j_graphrag.schema import get_schema

schema = get_schema(driver)
retriever = Text2CypherRetriever(driver=driver, llm=llm, neo4j_schema=schema)
result = retriever.get_search_results("Which customers bought the most products?")
print(result.metadata["cypher"])  # See the generated Cypher
```

---

## Data Mesh & Cross-Domain Patterns

### Domain Graph Federation

Each UBI domain (CRM, Orders, Inventory, etc.) can be modeled as a sub-graph with well-defined boundaries:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  CRM Domain  │     │ Orders Domain│     │ Inventory    │
│              │     │              │     │ Domain       │
│ :Customer    │────>│ :Order       │────>│ :Product     │
│ :Contact     │     │ :OrderLine   │     │ :Warehouse   │
│ :Opportunity │     │ :Shipment    │     │ :StockLevel  │
│ :Lead        │     │ :Invoice     │     │ :BOM         │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                     │
       ▼                    ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Service Dom. │     │ Finance Dom. │     │ Procurement  │
│              │     │              │     │ Domain       │
│ :RepairOrder │     │ :GLAccount   │     │ :Supplier    │
│ :VOCCase     │     │ :JournalEntry│     │ :PurchaseOrder│
│ :Warranty    │     │ :CostCenter  │     │ :Receipt     │
└──────────────┘     └──────────────┘     └──────────────┘
```

### Shared Nodes (Cross-Domain Bridges)

These nodes appear across multiple domains and serve as graph "bridges":

| Shared Node | Connects Domains |
|---|---|
| `:Customer` | CRM ↔ Orders ↔ AR ↔ Service ↔ VOC |
| `:Product` | Inventory ↔ Orders ↔ Procurement ↔ Service ↔ VOC ↔ Warranty |
| `:Country`/`:Region` | All domains (geography is universal) |
| `:Currency` | Orders ↔ Finance ↔ Procurement ↔ AR |
| `:Organization` | All domains (operating unit/org structure) |
| `:Calendar`/`:Date` | All domains (temporal dimension) |

### Mesh Query Patterns

```cypher
// Cross-domain: Customer → Orders → Products → VOC complaints
MATCH (c:Customer)-[:PLACED]->(:Order)-[:CONTAINS]->(:OrderLine)-[:FOR_PRODUCT]->(p:Product)
MATCH (p)<-[:ABOUT_PRODUCT]-(v:VOCCase)
RETURN c.name, p.name, count(v) AS complaints
ORDER BY complaints DESC

// Cross-domain: Supplier → Product → Quality Issues → Affected Customers
MATCH (s:Supplier)-[:SUPPLIES]->(p:Product)<-[:ABOUT_PRODUCT]-(v:VOCCase)<-[:FILED]-(c:Customer)
RETURN s.name, p.name, collect(DISTINCT c.name) AS affectedCustomers

// Lineage: Trace data from source to report
MATCH path = (src:SourceSystem)-[:FEEDS]->(:BronzeTable)-[:TRANSFORMS_TO]->(:SilverTable)-[:PUBLISHES_TO]->(:GoldView)-[:CONSUMED_BY]->(:Report)
WHERE src.name = 'Oracle EBS'
RETURN path
```

---

## Graph Review & Best Practices

### Model Review Checklist

- [ ] Every node has a unique identifier property with a uniqueness constraint
- [ ] Relationship types are specific and meaningful (not generic like `RELATED_TO`)
- [ ] No "super nodes" — nodes with >100K relationships (use intermediate nodes to break up)
- [ ] Properties that are always queried together are on the same node
- [ ] Temporal data uses appropriate pattern (property vs. relationship vs. temporal node)
- [ ] Cross-domain connections are explicit, not implied
- [ ] Schema is documented and enforced

### Performance Best Practices

1. **Index everything you query by**: Unique constraints, composite indexes, full-text indexes
2. **Batch writes**: Always use UNWIND with batches of 5,000-10,000 rows
3. **Use MERGE not CREATE** for idempotent loads (safe to re-run)
4. **Parameterize queries**: Never string-concatenate values into Cypher
5. **Limit variable-length paths**: Always set upper bound (`[*1..5]`, never `[*]`)
6. **Profile before optimizing**: Use `PROFILE` prefix to see query execution plan
7. **Warm the page cache**: Run `CALL db.index.fulltext.queryNodes()` on startup
8. **Monitor with**: `CALL dbms.queryJmx('org.neo4j:*')` or Neo4j Browser metrics

### Optimization Patterns

```cypher
// BAD: Cartesian product
MATCH (a:Customer), (b:Product) WHERE a.id = b.customerId RETURN a, b

// GOOD: Direct relationship traversal
MATCH (a:Customer)-[:PURCHASED]->(b:Product) RETURN a, b

// BAD: No index, full scan
MATCH (c:Customer) WHERE c.name = 'Fluke Corp' RETURN c

// GOOD: Indexed lookup
// (after CREATE CONSTRAINT customer_name FOR (c:Customer) REQUIRE c.name IS UNIQUE)
MATCH (c:Customer {name: 'Fluke Corp'}) RETURN c

// BAD: Loading all properties when you only need a few
MATCH (c:Customer)-[:PLACED]->(o:Order) RETURN c, o

// GOOD: Project only needed properties
MATCH (c:Customer)-[:PLACED]->(o:Order)
RETURN c.name, o.orderId, o.orderDate, o.amount
```

### Data Quality Checks

```cypher
// Orphaned nodes (no relationships)
MATCH (n) WHERE NOT (n)--() RETURN labels(n)[0] AS label, count(n) AS orphans

// Duplicate nodes (same ID, different nodes)
MATCH (c:Customer)
WITH c.customerId AS id, collect(c) AS nodes
WHERE size(nodes) > 1
RETURN id, size(nodes) AS duplicates

// Missing required properties
MATCH (c:Customer) WHERE c.name IS NULL OR c.customerId IS NULL
RETURN c LIMIT 10

// Super nodes (too many relationships)
MATCH (n)
WITH n, size((n)--()) AS degree
WHERE degree > 10000
RETURN labels(n)[0] AS label, n.name, degree
ORDER BY degree DESC
```

---

## Gotchas (Known Issues & Token/Time Savers)

### Neo4j Gotchas

1. **MERGE is NOT upsert by default**: `MERGE` creates OR matches the *entire* pattern. If you MERGE a node+relationship, and the node exists but the relationship doesn't, it creates a NEW node. Always MERGE nodes first, then MERGE relationships separately.
   ```cypher
   // BAD
   MERGE (c:Customer {id: '001'})-[:PLACED]->(o:Order {id: 'SO1'})
   // GOOD
   MERGE (c:Customer {id: '001'})
   MERGE (o:Order {id: 'SO1'})
   MERGE (c)-[:PLACED]->(o)
   ```

2. **Eager loading kills performance**: `COLLECT()` and `count()` on large result sets load everything into memory. Use `LIMIT` or pagination.

3. **String comparison is case-sensitive**: `WHERE c.name = 'fluke'` won't match `'Fluke'`. Use `toLower()` or full-text indexes.

4. **Date handling**: Neo4j uses ISO 8601. Convert on import: `date('2026-01-15')`, not `'01/15/2026'`.

5. **NULL propagation**: Any comparison with NULL returns NULL (not false). Use `IS NULL` / `IS NOT NULL` explicitly.

6. **Transaction size limits**: Don't load millions of rows in a single transaction. Batch with UNWIND + periodic commit or `apoc.periodic.iterate`.

7. **Community Edition limits**: Single database, no role-based access, no clustering, no online backup. Fine for prototyping, not for production multi-tenant.

### GraphRAG Gotchas

8. **Embedding model mismatch**: The embedding model used during retrieval MUST match the one used during ingestion. Mixing models = garbage results.

9. **enforce_schema=True is essential**: Without it, the LLM will hallucinate entity types and pollute your graph with random labels.

10. **Text2Cypher is non-deterministic**: Same question may generate different Cypher queries. Never use for financial reporting or compliance queries.

11. **Path property must match exactly**: When linking structured imports to KG-builder documents, the `path` property is case-sensitive and OS-specific.

### Data Import Gotchas

12. **CSV encoding**: Neo4j Data Importer expects UTF-8. Export from Fabric/Databricks may produce UTF-8 BOM — strip it.

13. **Parquet → CSV for Data Importer**: Data Importer only accepts CSV. For Parquet, convert first with pandas.

14. **Large imports**: For >1M rows, use `neo4j-admin database import` (offline) instead of Cypher LOAD CSV (much faster).

15. **Property types are inferred**: Neo4j may store `"123"` as string. Cast explicitly: `toInteger(row.qty)`, `toFloat(row.amount)`.

### UBI-Specific Gotchas

16. **Gold views have backtick-quoted aliases**: Spark SQL uses backticks (`` `Order Amount` ``). Strip these for Neo4j property names (use camelCase: `orderAmount`).

17. **Snapshot tables (_Snapshots suffix)**: These contain historical snapshots. Model as temporal relationships or versioned nodes, not as current state.

18. **_AI suffix views**: These are analytics-optimized views (flattened, pre-aggregated). May be useful for quick graph prototyping but hide the true relationships.

19. **DimCalendar proliferation**: There are 15+ calendar views (DimCalendar_CRM, DimCalendar_Inv, DimCalendar_OS, etc.). Use a single `:Date` node with domain-specific properties, not separate calendar nodes per domain.

20. **vw_ prefix**: All Gold views start with `vw_`. Some Lakehouse tables lack this prefix (direct tables like FactWarrantyCost). Normalize naming during import.

---

## Prototyping Tools (Free/Open Source)

### Recommended Stack for Prototyping

| Tool | Purpose | Install |
|---|---|---|
| **Neo4j Community Edition** | Full graph DB, Cypher, single DB | `choco install neo4j-community` or Docker |
| **Neo4j Desktop** | GUI for managing local DBs | Download from neo4j.com |
| **Neo4j AuraDB Free** | Cloud, 2GB, 30-day inactivity limit | console.neo4j.io |
| **NetworkX** (Python) | In-memory graph analysis, no server needed | `pip install networkx` |
| **Arrows.app** | Browser-based graph data modeling (visual) | arrows.app (no install) |
| **Gephi** | Graph visualization and analysis | gephi.org |
| **Neo4j Browser** | Built-in Cypher query + visualization | Included with Neo4j |

### Quick Start: NetworkX for Prototyping

```python
import networkx as nx
import matplotlib.pyplot as plt

# Build graph from Gold table metadata
G = nx.DiGraph()

# Add domain nodes
for domain in ['CRM', 'Orders', 'Inventory', 'Procurement', 'Service']:
    G.add_node(domain, type='domain')

# Add table nodes and relationships
G.add_node('DimCRMAccount', type='dimension', domain='CRM', rows=2_269_238)
G.add_node('FactOrders', type='fact', domain='Orders')
G.add_edge('FactOrders', 'DimCRMAccount', relationship='SOLD_TO', join_key='customerId')

# Visualize
pos = nx.spring_layout(G)
nx.draw(G, pos, with_labels=True, node_color='lightblue', arrows=True)
plt.savefig('gold_graph_prototype.png', dpi=150, bbox_inches='tight')
```

### Quick Start: Neo4j Community via Docker

```bash
docker run -d --name neo4j-ubi \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password123 \
  -v neo4j-data:/data \
  neo4j:5-community
# Browser: http://localhost:7474
# Bolt: bolt://localhost:7687
```

---

## Python Libraries Reference

| Library | Purpose | Install |
|---|---|---|
| `neo4j` | Official Python driver | `pip install neo4j` |
| `neo4j-graphrag` | KG builder, retrievers, GraphRAG | `pip install neo4j-graphrag` |
| `networkx` | In-memory graph analysis | `pip install networkx` |
| `pyvis` | Interactive graph visualization (HTML) | `pip install pyvis` |
| `pandas` | DataFrame for data prep | `pip install pandas` |
| `pyarrow` | Parquet read/write | `pip install pyarrow` |
| `deltalake` | Read Delta tables from ADLS | `pip install deltalake` |
| `matplotlib` | Graph visualization (static) | `pip install matplotlib` |

---

## Workflow: Building a Graph from Gold Tables

### Step 1: Schema Discovery
Read Gold view SQL to identify JOINs and foreign keys. These become relationships.

### Step 2: Domain Modeling
Group tables by domain. Identify shared dimensions (Customer, Product, Country, etc.).

### Step 3: Graph Schema Design
Map dimensions → nodes, facts → relationships or intermediate nodes, foreign keys → edges.

### Step 4: Prototype with NetworkX
Build a metadata graph first (tables as nodes, JOINs as edges) to validate the model.

### Step 5: Export Sample Data
Extract sample data (e.g., 10K rows per table) from Gold Lakehouse.

### Step 6: Load into Neo4j
Use Python driver with UNWIND batches or Data Importer for CSVs.

### Step 7: Validate & Iterate
Run data quality checks, test traversal queries, refine model.

### Step 8: GraphRAG Layer (Optional)
Add unstructured data (documents, notes) and vector indexes for semantic search.

---

## Cloned Repos (in project folder/repos/)

| Repo | Purpose | Key Files |
|---|---|---|
| `neo4j-graphrag-python` | Official GraphRAG library (1,095 stars) | `examples/`, `src/neo4j_graphrag/` |
| `llm-graph-builder` | LLM-powered unstructured→KG builder (4,551 stars) | `backend/`, `frontend/` |
| `neo4j-spark-connector` | Databricks Delta→Neo4j ETL (317 stars) | `doc/`, `spark-3/` |
| `arrows.app` | Visual graph schema designer (174 stars) | `apps/`, exports Cypher |
| `graph-data-science` | GDS algorithms: community detection, centrality, ML (775 stars) | `algo/`, `proc/` |

### Spark Connector Usage (Databricks → Neo4j)

```python
# In Databricks notebook — install JAR as cluster library first
# Maven: org.neo4j:neo4j-connector-apache-spark_2.12:5.x.x

# Write nodes from Delta table
(spark.read.table("FlukeBI_Gold.vw_DimCRMAccount")
  .select("accountId", "name", "country", "industry")
  .write.format("org.neo4j.spark.DataSource")
  .option("url", NEO4J_URI)
  .option("authentication.basic.username", NEO4J_USER)
  .option("authentication.basic.password", NEO4J_PASSWORD)
  .option("labels", ":Customer")
  .option("node.keys", "accountId")
  .mode("Overwrite")
  .save())

# Write relationships
(spark.read.table("FlukeBI_Gold.vw_FactOrders")
  .select(col("customerId").alias("source.customerId"),
          col("productId").alias("target.productId"),
          "orderDate", "amount")
  .write.format("org.neo4j.spark.DataSource")
  .option("url", NEO4J_URI)
  .option("relationship", "PLACED_ORDER")
  .option("relationship.source.labels", ":Customer")
  .option("relationship.source.node.keys", "source.customerId:customerId")
  .option("relationship.target.labels", ":Product")
  .option("relationship.target.node.keys", "target.productId:productId")
  .mode("Overwrite")
  .save())
```

### DuckPGQ (Graph Queries in DuckDB — Experimental)

DuckDB has a SQL/PGQ extension for graph queries directly on Delta/Parquet. Since we already use DuckDB for Splink, this enables graph prototyping with zero infrastructure:

```sql
-- In DuckDB
INSTALL sqlpgq; LOAD sqlpgq;

-- Create property graph over existing tables
CREATE PROPERTY GRAPH ubi_graph
VERTEX TABLES (customers, products)
EDGE TABLES (
  orders SOURCE KEY (customer_id) REFERENCES customers
         DESTINATION KEY (product_id) REFERENCES products
);

-- Graph pattern matching (SQL/PGQ syntax)
SELECT c.name, p.name, o.amount
FROM GRAPH_TABLE (ubi_graph
  MATCH (c:customers)-[o:orders]->(p:products)
  WHERE c.country = 'US'
  COLUMNS (c.name, p.name, o.amount)
);
```

---

## Reference Links

- Neo4j Documentation: https://neo4j.com/docs/
- Cypher Manual: https://neo4j.com/docs/cypher-manual/current/
- Neo4j GraphRAG Python: https://neo4j.com/docs/neo4j-graphrag-python/current/
- Graph Data Modeling Guide: https://neo4j.com/developer/data-modeling/
- Neo4j GraphAcademy (free courses): https://graphacademy.neo4j.com/
- Arrows.app (visual modeling): https://arrows.app/
- Neo4j AuraDB Free: https://console.neo4j.io/
- Neo4j Spark Connector: https://github.com/neo4j/neo4j-spark-connector
- LLM Graph Builder: https://github.com/neo4j-labs/llm-graph-builder
- Graph Data Science: https://github.com/neo4j/graph-data-science
