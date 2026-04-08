---
name: Graphify Knowledge Graph Skill
description: Knowledge graph builder from safishamsi/graphify — AST + semantic extraction, Leiden clustering, 13 languages, multiple export formats
type: project
---

## Overview
Graphify turns any folder (code, docs, papers, images) into a queryable knowledge graph with community detection and an honest audit trail. Based on safishamsi/graphify v0.3.0 (MIT).

**Why:** Persistent cross-session graph, EXTRACTED/INFERRED/AMBIGUOUS confidence tags, cross-document surprise discovery via Leiden clustering. 71.5x token reduction on mixed corpora.

**How to apply:** Use `/graphify` skill for codebase analysis, reading list mapping, research corpus navigation. Integrates with UBI Gold Graph (Neo4j) and MCP server for agent access.

## Project Location
- **Repo clone**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\graphify\`
- **Skill file**: `C:\Users\adm-tmanyang\.claude\commands\graphify.md`
- **Source**: https://github.com/safishamsi/graphify (MIT license)
- **PyPI package**: `graphifyy` (temporary name, v0.3.0)

## Architecture
```
detect() → extract() → build_graph() → cluster() → analyze() → report() → export()
```

- **Two-pass extraction**: deterministic AST (tree-sitter, 13 langs) + parallel Claude semantic
- **No embeddings**: topology-based Leiden clustering via edge density
- **SHA256 caching**: re-runs only process changed files
- **13 languages**: Python, TS, JS, Go, Rust, Java, C, C++, Ruby, C#, Kotlin, Scala, PHP

## Key Modules (5,723 lines source, 3,256 lines tests)
| Module | Purpose |
|---|---|
| `detect.py` | File discovery, classification, corpus health |
| `extract.py` | AST extraction via tree-sitter (LanguageConfig pattern) |
| `build.py` | NetworkX graph assembly, dedup |
| `cluster.py` | Leiden/Louvain community detection |
| `analyze.py` | God nodes, surprising connections, suggested questions |
| `report.py` | GRAPH_REPORT.md generation |
| `export.py` | HTML/JSON/SVG/GraphML/Neo4j/Obsidian vault |
| `cache.py` | Per-file SHA256 caching |
| `serve.py` | MCP stdio server |
| `watch.py` | File watcher + AST-only rebuild |
| `ingest.py` | URL fetching (tweets, arXiv, PDFs, webpages) |
| `hooks.py` | Git hook management |

## Dependencies
- Core: networkx, tree-sitter + 13 grammar packages
- Optional: graspologic (Leiden), watchdog, mcp, neo4j, pypdf, html2text

## Status (2026-04-06)
- Repo cloned and analyzed
- Skill file created at `~/.claude/commands/graphify.md`
- Not yet run on any Fortive codebase
