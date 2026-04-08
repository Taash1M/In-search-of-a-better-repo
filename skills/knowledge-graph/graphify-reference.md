# Graphify Reference — Pipeline Details & Schemas

> Loaded on demand by the graphify skill. Do not read unless instructed.

## Extraction Schema

```json
{
  "nodes": [{"id": "filestem_entityname", "label": "Human Readable Name", "file_type": "code|document|paper|image", "source_file": "relative/path", "source_location": "L42", "source_url": null, "author": null, "contributor": null}],
  "edges": [{"source": "node_id", "target": "node_id", "relation": "calls|implements|references|cites|conceptually_related_to|semantically_similar_to|rationale_for", "confidence": "EXTRACTED|INFERRED|AMBIGUOUS", "confidence_score": 1.0, "source_file": "relative/path", "source_location": null, "weight": 1.0}],
  "hyperedges": [{"id": "snake_case_id", "label": "Human Readable Label", "nodes": ["id1", "id2", "id3"], "relation": "participate_in|implement|form", "confidence": "EXTRACTED|INFERRED", "confidence_score": 0.75, "source_file": "relative/path"}],
  "input_tokens": 0, "output_tokens": 0
}
```

## Confidence Tags
- **EXTRACTED**: explicit in source (import, call, citation, "see §3.2") — `confidence_score = 1.0`
- **INFERRED**: reasonable deduction (shared data, implied dependency) — `0.4–0.9`
- **AMBIGUOUS**: uncertain, flagged for review — `0.1–0.3`

## Subagent Prompt Template

Use this exact prompt for each semantic extraction subagent (substitute FILE_LIST, CHUNK_NUM, TOTAL_CHUNKS, DEEP_MODE):

```
You are a graphify extraction subagent. Read the files listed and extract a knowledge graph fragment.
Output ONLY valid JSON matching the schema below - no explanation, no markdown fences, no preamble.

Files (chunk CHUNK_NUM of TOTAL_CHUNKS):
FILE_LIST

Rules:
- EXTRACTED: relationship explicit in source (import, call, citation, "see §3.2")
- INFERRED: reasonable inference (shared data structure, implied dependency)
- AMBIGUOUS: uncertain - flag for review, do not omit

Code files: focus on semantic edges AST cannot find (call relationships, shared data, arch patterns).
  Do not re-extract imports - AST already has those.
Doc/paper files: extract named concepts, entities, citations. Also extract rationale — sections
  explaining WHY a decision was made. These become nodes with `rationale_for` edges.
Image files: use vision to understand what the image IS - not just OCR.
  UI screenshot: layout patterns, design decisions, key elements, purpose.
  Chart: metric, trend/insight, data source.
  Tweet/post: claim as node, author, concepts mentioned.
  Diagram: components and connections.
  Research figure: what it demonstrates, method, result.
  Handwritten/whiteboard: ideas and arrows, mark uncertain readings AMBIGUOUS.

DEEP_MODE (if --mode deep): be aggressive with INFERRED edges. Mark uncertain ones AMBIGUOUS.

Semantic similarity: if two concepts solve the same problem without structural link, add
  `semantically_similar_to` edge marked INFERRED with confidence_score 0.6-0.95.
  Only when genuinely non-obvious and cross-cutting.

Hyperedges: if 3+ nodes participate in a shared concept/flow/pattern, add hyperedge. Max 3 per chunk.

If a file has YAML frontmatter (--- ... ---), copy source_url, captured_at, author,
  contributor onto every node from that file.

confidence_score is REQUIRED on every edge:
- EXTRACTED: 1.0 always
- INFERRED: 0.4-0.9 (reason individually, most should be 0.6-0.9)
- AMBIGUOUS: 0.1-0.3

Output exactly this JSON:
{"nodes":[{"id":"filestem_entityname","label":"Human Readable Name","file_type":"code|document|paper|image","source_file":"relative/path","source_location":null}],"edges":[{"source":"node_id","target":"node_id","relation":"...", "confidence":"EXTRACTED|INFERRED|AMBIGUOUS","confidence_score":1.0,"source_file":"relative/path","weight":1.0}],"hyperedges":[{"id":"snake_case_id","label":"Human Readable Label","nodes":["id1","id2","id3"],"relation":"participate_in|implement|form","confidence":"EXTRACTED|INFERRED","confidence_score":0.75,"source_file":"relative/path"}],"input_tokens":0,"output_tokens":0}
```

## Pipeline Modules

| Module | Purpose | Lines |
|---|---|---|
| `detect.py` | File discovery, classification (CODE/DOCUMENT/PAPER/IMAGE), corpus health | 275 |
| `extract.py` | AST extraction via tree-sitter (LanguageConfig pattern), 13 languages | 1,588 |
| `build.py` | Merge extractions into NetworkX graph, dedup, edge direction | 71 |
| `cluster.py` | Leiden (graspologic) or Louvain community detection, splits oversized communities | 118 |
| `analyze.py` | God nodes, surprising connections (cross-file edges), suggested questions | 250+ |
| `report.py` | GRAPH_REPORT.md generation (9 sections) | 200+ |
| `export.py` | HTML (vis.js)/JSON/SVG/GraphML/Neo4j Cypher/Obsidian vault | 600+ |
| `cache.py` | Per-file SHA256 caching, semantic cache check | 125 |
| `validate.py` | Schema enforcement on extraction output | 72 |
| `security.py` | URL scheme validation, path traversal guards, label sanitization (XSS) | 167 |
| `ingest.py` | URL fetching — tweets (oEmbed), arXiv (PDF), webpages (html2text) | 200+ |
| `watch.py` | File watcher + AST-only rebuild, 3s debounce | 140+ |
| `serve.py` | MCP stdio server (query, path, explain, stats, neighbors) | 200+ |
| `wiki.py` | Wikipedia-style article generation per community + god node | 250+ |
| `hooks.py` | Git post-commit/post-checkout hook management | 150+ |
| `benchmark.py` | Token reduction measurement (BFS from sample questions) | 127 |

## Dependencies

**Core** (always required): `networkx`, `tree-sitter` + 13 language grammars (python, javascript, typescript, go, rust, java, c, cpp, ruby, c-sharp, kotlin, scala, php)

**Optional** (`pip install graphifyy[all]`):
- `graspologic` — Leiden clustering (falls back to Louvain if missing)
- `watchdog` — file watcher for `--watch`
- `mcp` — MCP stdio server for `--mcp`
- `neo4j` — Neo4j driver for `--neo4j-push`
- `pypdf`, `html2text` — PDF + HTML-to-markdown ingestion

## Supported Languages (13)
Python, TypeScript, JavaScript, Go, Rust, Java, C, C++, Ruby, C#, Kotlin, Scala, PHP

## Optional Export Code Blocks

**SVG** (`--svg`):
```bash
$(cat .graphify_python) -c "
import json
from graphify.build import build_from_json
from graphify.export import to_svg
from pathlib import Path
extraction = json.loads(Path('.graphify_extract.json').read_text())
analysis = json.loads(Path('.graphify_analysis.json').read_text())
labels_raw = json.loads(Path('.graphify_labels.json').read_text()) if Path('.graphify_labels.json').exists() else {}
G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
labels = {int(k): v for k, v in labels_raw.items()}
to_svg(G, communities, 'graphify-out/graph.svg', community_labels=labels or None)
print('graph.svg written')
"
```

**GraphML** (`--graphml`):
```bash
$(cat .graphify_python) -c "
import json
from graphify.build import build_from_json
from graphify.export import to_graphml
from pathlib import Path
extraction = json.loads(Path('.graphify_extract.json').read_text())
analysis = json.loads(Path('.graphify_analysis.json').read_text())
G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
to_graphml(G, communities, 'graphify-out/graph.graphml')
print('graph.graphml written')
"
```

**Neo4j Cypher** (`--neo4j`):
```bash
$(cat .graphify_python) -c "
import json
from graphify.build import build_from_json
from graphify.export import to_cypher
from pathlib import Path
G = build_from_json(json.loads(Path('.graphify_extract.json').read_text()))
to_cypher(G, 'graphify-out/cypher.txt')
print('cypher.txt written - import with: cypher-shell < graphify-out/cypher.txt')
"
```

**Neo4j Push** (`--neo4j-push <uri>`):
```bash
$(cat .graphify_python) -c "
import json
from graphify.build import build_from_json
from graphify.export import push_to_neo4j
from pathlib import Path
extraction = json.loads(Path('.graphify_extract.json').read_text())
analysis = json.loads(Path('.graphify_analysis.json').read_text())
G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
result = push_to_neo4j(G, uri='NEO4J_URI', user='NEO4J_USER', password='NEO4J_PASSWORD', communities=communities)
print(f'Pushed to Neo4j: {result[\"nodes\"]} nodes, {result[\"edges\"]} edges')
"
```

**Obsidian Vault** (`--obsidian`):
```bash
$(cat .graphify_python) -c "
import json
from graphify.build import build_from_json
from graphify.export import to_obsidian, to_canvas
from pathlib import Path
extraction = json.loads(Path('.graphify_extract.json').read_text())
analysis = json.loads(Path('.graphify_analysis.json').read_text())
labels_raw = json.loads(Path('.graphify_labels.json').read_text()) if Path('.graphify_labels.json').exists() else {}
G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
cohesion = {int(k): v for k, v in analysis['cohesion'].items()}
labels = {int(k): v for k, v in labels_raw.items()}
n = to_obsidian(G, communities, 'graphify-out/obsidian', community_labels=labels or None, cohesion=cohesion)
to_canvas(G, communities, 'graphify-out/obsidian/graph.canvas', community_labels=labels or None)
print(f'Obsidian vault: {n} notes in graphify-out/obsidian/')
"
```

**MCP Server** (`--mcp`):
```bash
python -m graphify.serve graphify-out/graph.json
```
Exposes tools: `query_graph`, `get_node`, `get_neighbors`, `get_community`, `god_nodes`, `graph_stats`, `shortest_path`.

## --update (Incremental) Pipeline

```bash
$(cat .graphify_python) -c "
import json
from graphify.detect import detect_incremental
from pathlib import Path
result = detect_incremental(Path('INPUT_PATH'))
Path('.graphify_incremental.json').write_text(json.dumps(result))
if result.get('new_total', 0) == 0:
    print('No files changed since last run.')
    raise SystemExit(0)
print(f'{result[\"new_total\"]} new/changed file(s) to re-extract.')
"
```

Check if code-only changes:
```bash
$(cat .graphify_python) -c "
import json
from pathlib import Path
result = json.loads(Path('.graphify_incremental.json').read_text())
code_exts = {'.py','.ts','.js','.go','.rs','.java','.cpp','.c','.rb','.swift','.kt','.cs','.scala','.php','.cc','.cxx','.hpp','.h','.kts'}
new_files = result.get('new_files', {})
all_changed = [f for files in new_files.values() for f in files]
code_only = all(Path(f).suffix.lower() in code_exts for f in all_changed)
print('code_only:', code_only)
"
```

If `code_only=True`: AST-only extraction (no LLM, no subagents). Otherwise full pipeline.

Merge into existing graph:
```bash
cp graphify-out/graph.json .graphify_old.json
$(cat .graphify_python) -c "
import json
from graphify.build import build_from_json
from graphify.export import to_json
from networkx.readwrite import json_graph
import networkx as nx
from pathlib import Path
existing_data = json.loads(Path('graphify-out/graph.json').read_text())
G_existing = json_graph.node_link_graph(existing_data, edges='links')
new_extraction = json.loads(Path('.graphify_extract.json').read_text())
G_new = build_from_json(new_extraction)
G_existing.update(G_new)
print(f'Merged: {G_existing.number_of_nodes()} nodes, {G_existing.number_of_edges()} edges')
"
```

Then re-run Steps 4-8. Show graph diff afterward. Clean up `.graphify_old.json`.

## --cluster-only Pipeline

Skip Steps 1-3. Load existing graph and re-cluster:
```bash
$(cat .graphify_python) -c "
import json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections
from graphify.report import generate
from graphify.export import to_json
from networkx.readwrite import json_graph
import networkx as nx
from pathlib import Path
data = json.loads(Path('graphify-out/graph.json').read_text())
G = json_graph.node_link_graph(data, edges='links')
communities = cluster(G)
cohesion = score_all(G, communities)
gods = god_nodes(G)
surprises = surprising_connections(G, communities)
labels = {cid: 'Community ' + str(cid) for cid in communities}
detection = {'total_files': 0, 'total_words': 99999, 'needs_graph': True, 'warning': None, 'files': {'code': [], 'document': [], 'paper': []}}
tokens = {'input': 0, 'output': 0}
report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, '.')
Path('graphify-out/GRAPH_REPORT.md').write_text(report)
to_json(G, communities, 'graphify-out/graph.json')
analysis = {'communities': {str(k): v for k, v in communities.items()}, 'cohesion': {str(k): v for k, v in cohesion.items()}, 'gods': gods, 'surprises': surprises}
Path('.graphify_analysis.json').write_text(json.dumps(analysis, indent=2))
print(f'Re-clustered: {len(communities)} communities')
"
```

Then run Steps 5-8 as normal.
