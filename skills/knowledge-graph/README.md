# Knowledge Graph Skills

2 skills for building queryable knowledge graphs from code, documents, papers, and images. Based on the safishamsi/graphify open-source project (v0.3.0, MIT license).

---

## Overview

The knowledge graph skill group transforms unstructured codebases and document collections into navigable, queryable graphs. The approach is novel: no embeddings, no vector similarity — topology-based clustering via the Leiden algorithm. This keeps graphs interpretable and dramatically reduces token usage (71.5x reduction versus naive LLM processing).

Two files cover different access patterns:
- **graphify.md** — the main operational skill, invoked directly
- **graphify-reference.md** — deep technical reference, loaded on-demand when pipeline details or schema specifics are needed

---

## Architecture

Two-pass extraction pipeline:

```
Input Folder (code / docs / images)
        │
        ▼
  Pass 1: Tree-sitter AST Parsing
        │
        ├── Tokenize source files (13 languages)
        ├── Extract: functions, classes, imports, calls, definitions
        ├── Build initial dependency graph (nodes + edges)
        └── Prune to structural skeleton (71.5x token reduction)
        │
        ▼
  Pass 2: Parallel Claude Semantic Analysis
        │
        ├── Leiden clustering on topology (no embeddings)
        ├── Cluster labeling and summary generation
        ├── Relationship inference across clusters
        └── Entity enrichment (purpose, patterns, anomalies)
        │
        ▼
  Knowledge Graph
        │
        ├── HTML  — interactive visualization, browsable in browser
        ├── JSON  — machine-readable, queryable programmatically
        ├── Neo4j — Cypher-queryable, integrates with UBI Neo4j instance
        └── Obsidian — markdown vault with backlinks, local graph view
```

---

## Capabilities

| Capability | Detail |
|-----------|--------|
| Supported languages | Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin (13 total) |
| Input types | Source code files, DOCX, PDF, plain text, images |
| Clustering method | Leiden algorithm on call graph topology — no embeddings required |
| Token reduction | 71.5x versus processing raw source with LLM |
| Export formats | HTML (interactive), JSON, Neo4j (Cypher), Obsidian (markdown vault) |
| Parallelism | Parallel Claude API calls for semantic enrichment per cluster |
| Source repo | safishamsi/graphify v0.3.0 (MIT license) |
| Source size | 5,723 lines source code, 3,256 lines tests |

---

## File Inventory

| File | Purpose | Lines | Grade History |
|------|---------|------:|---------------|
| `graphify.md` | Main operational skill — invoked directly to build graphs | 369 | D (79/120) → B (102/120) |
| `graphify-reference.md` | On-demand reference — pipeline internals, schemas, edge types, export formats | 279 | Reference |

### Grade Improvement History (graphify.md)
Initial Skill Judge score was D (79/120). Issues identified and resolved:
- Added proper YAML frontmatter with trigger conditions
- Cut redundant pipeline description sections (reduced overlap with reference file)
- Removed expert anti-patterns (over-specifying internal API details in the main skill)
- Tightened invocation examples and output expectations

Final score: B (102/120).

---

## Skill Details

### graphify.md — Main Skill
Invoked when the user wants to build a knowledge graph from a folder. Handles:
- Input validation and language detection
- Invoking tree-sitter AST parsing (Pass 1)
- Orchestrating parallel Claude semantic enrichment (Pass 2)
- Leiden clustering and cluster labeling
- Export to the requested format(s)
- Summary report: node count, edge count, cluster count, top clusters by size

### graphify-reference.md — Technical Reference
Loaded by `graphify.md` on-demand when deeper detail is needed. Contains:
- Full edge type taxonomy (calls, imports, inherits, uses, defines, etc.)
- Neo4j schema with node labels and relationship types
- Obsidian vault structure and frontmatter conventions
- JSON export schema
- Batch processing patterns for large repos
- Known limitations and workarounds

---

## Usage Examples

```bash
# Build a knowledge graph from the UBI Databricks repo
/graphify path="C:/Users/tmanyang/AzureDataBricks" export=["neo4j", "html"]

# Graph a Python library for architecture review
/graphify path="C:/Users/tmanyang/OneDrive - Fortive/Claude code/graphify" export=["json", "html"]

# Build an Obsidian vault from a research document collection
/graphify path="./research-papers" input_type="docs" export=["obsidian"]

# Query the resulting Neo4j graph (via /ubi-neo4j)
/ubi-neo4j query="MATCH (c:Cluster)-[:CONTAINS]->(f:Function) WHERE c.label = 'data_pipeline' RETURN f.name"
```

---

## Integration with UBI Neo4j

The `neo4j` export format produces Cypher `CREATE` statements compatible with the UBI Neo4j instance (431 Gold tables). Use `/ubi-neo4j` to load and query the exported graph:

```
/graphify  →  Neo4j export  →  /ubi-neo4j load  →  Cypher queries
```

This enables cross-referencing code structure (graphify graph) with data lineage (UBI Gold graph) in a single Neo4j instance.

---

## Local Repo

The graphify source repo is cloned at:

```
C:\Users\tmanyang\OneDrive - Fortive\Claude code\graphify\
```

Use `/repo-eval` against this path to re-evaluate or extract updated patterns if the upstream repo is updated.

---

## Sync Workflow

Both skills are promoted to `~/.claude/commands/` for global availability.

```bash
# Sync after edits
cp "skills/knowledge-graph/graphify.md" "$HOME/.claude/commands/graphify.md"
cp "skills/knowledge-graph/graphify-reference.md" "$HOME/.claude/commands/graphify-reference.md"
```

To re-score with Skill Judge after changes:
- Target grade: B (102/120) or above for `graphify.md`
- Reference files are not scored — they are evaluated on completeness and precision only
- Run `/session-review` after any significant skill revision to capture lessons learned
