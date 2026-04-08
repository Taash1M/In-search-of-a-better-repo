---
name: graphify
description: >
  Build queryable knowledge graphs from any folder of code, docs, papers, or images using
  tree-sitter AST + parallel Claude semantic extraction. Use when the user asks to map a
  codebase, analyze a repository, build a knowledge graph, visualize code architecture,
  find cross-file connections, understand a new repo, or reduce token cost for large corpora.
  Supports: 13 languages, Leiden clustering, Neo4j export, Obsidian vault, MCP server, HTML viz.
  Keywords: knowledge graph, codebase map, graph, community detection, architecture, graphify, graphrag.
---

# Graphify — Knowledge Graph Builder

Turn any folder into a persistent, queryable knowledge graph with community detection and an honest audit trail (EXTRACTED/INFERRED/AMBIGUOUS on every edge).

## When to Use Graphify (Decision Tree)

```
Corpus size?
├─ < 10 files, single language → DON'T USE. Read files directly.
├─ 10-50 files, code only → /graphify (AST-only, instant, free)
├─ 50-200 files, mixed types → /graphify --mode deep
├─ > 200 files → Scope to subfolder first, THEN /graphify
│
Already have a Neo4j graph (e.g., UBI Gold Graph)?
├─ Yes → Use --neo4j-push to enrich existing graph
├─ No → Default HTML + JSON output
│
Repeat analysis across sessions?
├─ Yes → Use --watch or git hooks for auto-rebuild
├─ No → One-shot /graphify is fine
```

## NEVER Do (Expert Anti-Patterns)

1. **NEVER run on a monorepo root** (>500 files without scoping) — graph becomes unusable, HTML viz crashes, subagents waste tokens extracting irrelevant code. Always scope to a meaningful subfolder first.
2. **NEVER dispatch >5 semantic subagents at once** — they compete for rate limits on Azure AI Foundry. Chunk so total subagents ≤ 5. If >100 non-code files, ask user to scope down.
3. **NEVER skip the benchmark step on first run** — if token reduction is < 5x, the graph is too sparse to justify its existence. The fix: add more docs/papers to the corpus, or re-run with `--mode deep`.
4. **NEVER trust a graph where >30% of edges are AMBIGUOUS** — the corpus is too heterogeneous. Split into sub-corpora by domain and graphify each separately.
5. **NEVER invent edges** — if unsure, use AMBIGUOUS. Fabricated INFERRED edges poison the entire graph's trust.
6. **NEVER skip corpus check warnings** — if >200 files or >500K words, always ask which subfolder.
7. **NEVER run HTML viz on >5,000 nodes** — vis.js chokes. Use Obsidian vault or Neo4j instead.
8. **If god_nodes returns only file-level hubs** (filenames, not concepts) — AST extraction dominated and semantic pass added nothing. Re-run with `--mode deep` or check that non-code files were included.
9. **If all communities have cohesion < 0.1** — the graph is too sparse for meaningful clustering. Need more files or denser extraction.
10. **NEVER hardcode python3** on Windows — always use `python`. The skill stores the correct interpreter in `.graphify_python`.

## Before Graphifying, Ask Yourself

- **What question am I trying to answer?** "How does auth work?" needs different depth than "show me everything."
- **Is the corpus self-contained?** If critical code lives outside this folder, the graph will have dangling edges (expected, not an error — but note it).
- **Code-only or mixed?** Code-only = instant (AST, no LLM cost). Mixed = parallel subagents (costs tokens).
- **First run or incremental?** First run: full pipeline. Changed files: `--update`. Re-cluster only: `--cluster-only`.

---

## Usage

```
/graphify [<path>] [--mode deep] [--update] [--cluster-only] [--no-viz]
          [--svg] [--graphml] [--neo4j] [--neo4j-push <uri>]
          [--mcp] [--watch] [--obsidian]
/graphify add <url> [--author "Name"] [--contributor "Name"]
/graphify query "<question>" [--dfs] [--budget 1500]
/graphify path "Node1" "Node2"
/graphify explain "NodeName"
```

Default path is `.` (current directory). Do not ask for a path if not given.

---

## Task Tracking

| Phase | TaskCreate | TaskUpdate |
|---|---|---|
| Detect | "Graphify: Detect and classify files" | → completed when summary shown |
| AST Extract | "Graphify: AST extraction (code)" | → completed when .graphify_ast.json written |
| Semantic Extract | "Graphify: Semantic extraction (docs/papers/images)" | → completed when subagents return |
| Build + Cluster | "Graphify: Build graph, cluster, analyze" | → completed when graph.json written |
| Report + Export | "Graphify: Generate report and exports" | → completed when outputs written |

---

## Full Pipeline (Steps 1-8)

### Step 1 — Install + detect Python

```bash
python -c "import graphify" 2>/dev/null || pip install graphifyy -q 2>&1 | tail -3
python -c "import sys; open('.graphify_python', 'w').write(sys.executable)"
```

**In every subsequent block, use `$(cat .graphify_python)` as interpreter.**

### Step 2 — Detect files

```bash
$(cat .graphify_python) -c "
import json
from graphify.detect import detect
from pathlib import Path
result = detect(Path('INPUT_PATH'))
print(json.dumps(result))
" > .graphify_detect.json
```

Present clean summary (not raw JSON):
```
Corpus: X files · ~Y words
  code: N files    docs: N files    papers: N files    images: N files
```

**Decision points:**
- `total_files == 0` → stop
- `skipped_sensitive` non-empty → mention count, not names
- `total_words > 2,000,000` OR `total_files > 200` → show top 5 subdirs, ask which subfolder, wait
- Otherwise → proceed to Step 3

### Step 3 — Extract (two-pass, parallel)

**Run Part A and Part B in the same message (parallel).**

#### Part A — AST extraction (code, deterministic, free)

```bash
$(cat .graphify_python) -c "
import sys, json
from graphify.extract import collect_files, extract
from pathlib import Path
code_files = []
detect = json.loads(Path('.graphify_detect.json').read_text())
for f in detect.get('files', {}).get('code', []):
    code_files.extend(collect_files(Path(f)) if Path(f).is_dir() else [Path(f)])
if code_files:
    result = extract(code_files)
    Path('.graphify_ast.json').write_text(json.dumps(result, indent=2))
    print(f'AST: {len(result[\"nodes\"])} nodes, {len(result[\"edges\"])} edges')
else:
    Path('.graphify_ast.json').write_text(json.dumps({'nodes':[],'edges':[],'input_tokens':0,'output_tokens':0}))
    print('No code files - skipping AST')
"
```

#### Part B — Semantic extraction (parallel subagents)

**Fast path:** Code-only corpus (zero docs/papers/images) → skip Part B entirely.

**MANDATORY: Use the Agent tool for parallel subagent dispatch.** Reading files one-by-one is 5-10x slower.

**MANDATORY: Read `graphify-reference.md` for the subagent prompt template before dispatching.**

1. **B0 — Check cache:**
```bash
$(cat .graphify_python) -c "
import json
from graphify.cache import check_semantic_cache
from pathlib import Path
detect = json.loads(Path('.graphify_detect.json').read_text())
all_files = [f for files in detect['files'].values() for f in files]
cached_nodes, cached_edges, cached_hyperedges, uncached = check_semantic_cache(all_files)
if cached_nodes or cached_edges or cached_hyperedges:
    Path('.graphify_cached.json').write_text(json.dumps({'nodes': cached_nodes, 'edges': cached_edges, 'hyperedges': cached_hyperedges}))
Path('.graphify_uncached.txt').write_text('\n'.join(uncached))
print(f'Cache: {len(all_files)-len(uncached)} hit, {len(uncached)} need extraction')
"
```

2. **B1 — Chunk** uncached files (20-25 per chunk, images get own chunk). Max 5 chunks.
3. **B2 — Dispatch ALL chunks in ONE message** using Agent tool. Use the prompt from `graphify-reference.md`.
4. **B3 — Collect + merge.** Valid JSON → cache + include. Failed → warn + skip. >50% failed → stop.

Merge cached + new → `.graphify_semantic.json`. Clean up temp files.

#### Part C — Merge AST + semantic

```bash
$(cat .graphify_python) -c "
import sys, json
from pathlib import Path
ast = json.loads(Path('.graphify_ast.json').read_text())
sem = json.loads(Path('.graphify_semantic.json').read_text())
seen = {n['id'] for n in ast['nodes']}
merged_nodes = list(ast['nodes'])
for n in sem['nodes']:
    if n['id'] not in seen:
        merged_nodes.append(n)
        seen.add(n['id'])
merged = {'nodes': merged_nodes, 'edges': ast['edges'] + sem['edges'], 'hyperedges': sem.get('hyperedges', []), 'input_tokens': sem.get('input_tokens', 0), 'output_tokens': sem.get('output_tokens', 0)}
Path('.graphify_extract.json').write_text(json.dumps(merged, indent=2))
print(f'Merged: {len(merged_nodes)} nodes, {len(merged[\"edges\"])} edges')
"
```

### Step 4 — Build, cluster, analyze

```bash
mkdir -p graphify-out
$(cat .graphify_python) -c "
import sys, json
from graphify.build import build_from_json
from graphify.cluster import cluster, score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json
from pathlib import Path
extraction = json.loads(Path('.graphify_extract.json').read_text())
detection  = json.loads(Path('.graphify_detect.json').read_text())
G = build_from_json(extraction)
communities = cluster(G)
cohesion = score_all(G, communities)
tokens = {'input': extraction.get('input_tokens', 0), 'output': extraction.get('output_tokens', 0)}
gods = god_nodes(G)
surprises = surprising_connections(G, communities)
labels = {cid: 'Community ' + str(cid) for cid in communities}
questions = suggest_questions(G, communities, labels)
report = generate(G, communities, cohesion, labels, gods, surprises, detection, tokens, 'INPUT_PATH', suggested_questions=questions)
Path('graphify-out/GRAPH_REPORT.md').write_text(report)
to_json(G, communities, 'graphify-out/graph.json')
analysis = {'communities': {str(k): v for k, v in communities.items()}, 'cohesion': {str(k): v for k, v in cohesion.items()}, 'gods': gods, 'surprises': surprises, 'questions': questions}
Path('.graphify_analysis.json').write_text(json.dumps(analysis, indent=2))
if G.number_of_nodes() == 0:
    print('ERROR: Graph is empty.'); raise SystemExit(1)
print(f'Graph: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges, {len(communities)} communities')
"
```

**If empty → stop.** Replace `INPUT_PATH` with actual path.

### Step 5 — Label communities

Read `.graphify_analysis.json`. Name each community in 2-5 words based on its node labels. Regenerate report:

```bash
$(cat .graphify_python) -c "
import sys, json
from graphify.build import build_from_json
from graphify.cluster import score_all
from graphify.analyze import suggest_questions
from graphify.report import generate
from pathlib import Path
extraction = json.loads(Path('.graphify_extract.json').read_text())
detection  = json.loads(Path('.graphify_detect.json').read_text())
analysis   = json.loads(Path('.graphify_analysis.json').read_text())
G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
cohesion = {int(k): v for k, v in analysis['cohesion'].items()}
tokens = {'input': extraction.get('input_tokens', 0), 'output': extraction.get('output_tokens', 0)}
labels = LABELS_DICT
questions = suggest_questions(G, communities, labels)
report = generate(G, communities, cohesion, labels, analysis['gods'], analysis['surprises'], detection, tokens, 'INPUT_PATH', suggested_questions=questions)
Path('graphify-out/GRAPH_REPORT.md').write_text(report)
Path('.graphify_labels.json').write_text(json.dumps({str(k): v for k, v in labels.items()}))
print('Report updated with community labels')
"
```

Replace `LABELS_DICT` and `INPUT_PATH`.

### Step 6 — HTML viz + optional exports

```bash
$(cat .graphify_python) -c "
import sys, json
from graphify.build import build_from_json
from graphify.export import to_html
from pathlib import Path
extraction = json.loads(Path('.graphify_extract.json').read_text())
analysis   = json.loads(Path('.graphify_analysis.json').read_text())
labels_raw = json.loads(Path('.graphify_labels.json').read_text()) if Path('.graphify_labels.json').exists() else {}
G = build_from_json(extraction)
communities = {int(k): v for k, v in analysis['communities'].items()}
labels = {int(k): v for k, v in labels_raw.items()}
if G.number_of_nodes() > 5000:
    print(f'Graph has {G.number_of_nodes()} nodes - too large for HTML. Use --obsidian or --neo4j.')
else:
    to_html(G, communities, 'graphify-out/graph.html', community_labels=labels or None)
    print('graph.html written')
"
```

**For --svg, --graphml, --neo4j, --neo4j-push, --obsidian, --mcp:** Read `graphify-reference.md` for the code blocks.

### Step 7 — Benchmark (if total_words > 5000)

```bash
$(cat .graphify_python) -c "
import json
from graphify.benchmark import run_benchmark, print_benchmark
from pathlib import Path
detection = json.loads(Path('.graphify_detect.json').read_text())
result = run_benchmark('graphify-out/graph.json', corpus_words=detection['total_words'])
print_benchmark(result)
"
```

**Quality check:** If reduction < 5x, warn user the graph is sparse. Suggest adding docs or using `--mode deep`.

### Step 8 — Manifest, cost tracking, cleanup

```bash
$(cat .graphify_python) -c "
import json
from pathlib import Path
from datetime import datetime, timezone
from graphify.detect import save_manifest
detect = json.loads(Path('.graphify_detect.json').read_text())
save_manifest(detect['files'])
extract = json.loads(Path('.graphify_extract.json').read_text())
input_tok = extract.get('input_tokens', 0)
output_tok = extract.get('output_tokens', 0)
cost_path = Path('graphify-out/cost.json')
cost = json.loads(cost_path.read_text()) if cost_path.exists() else {'runs': [], 'total_input_tokens': 0, 'total_output_tokens': 0}
cost['runs'].append({'date': datetime.now(timezone.utc).isoformat(), 'input_tokens': input_tok, 'output_tokens': output_tok, 'files': detect.get('total_files', 0)})
cost['total_input_tokens'] += input_tok
cost['total_output_tokens'] += output_tok
cost_path.write_text(json.dumps(cost, indent=2))
print(f'This run: {input_tok:,} input, {output_tok:,} output tokens')
print(f'All time: {cost[\"total_input_tokens\"]:,} input, {cost[\"total_output_tokens\"]:,} output ({len(cost[\"runs\"])} runs)')
"
rm -f .graphify_detect.json .graphify_extract.json .graphify_ast.json .graphify_semantic.json .graphify_analysis.json .graphify_labels.json .graphify_python
```

**Report to user:**
```
Graph complete. Outputs in <PATH>/graphify-out/
  graph.html       — interactive graph (open in browser)
  GRAPH_REPORT.md  — audit report
  graph.json       — persistent queryable data
```

Paste from GRAPH_REPORT.md: **God Nodes**, **Surprising Connections**, **Suggested Questions**.

Then offer: pick the most interesting question and ask:
> "The most interesting question this graph can answer: **[question]**. Want me to trace it?"

---

## Subcommands (Compact)

### /graphify query
Check `graphify-out/graph.json` exists → find 1-3 matching nodes → BFS (3 hops) or DFS (`--dfs`, 6 hops) → apply `--budget` cap (default 2000 tokens) → answer using ONLY graph contents, cite `source_location` → save Q&A to `graphify-out/memory/`.

### /graphify path
Find best-matching nodes for both terms → `nx.shortest_path(G, src, tgt)` → explain each hop → save to memory.

### /graphify explain
Find best-matching node → show label, source, type, degree, all connections → write 3-5 sentence explanation → save to memory.

### /graphify add
`ingest(url, Path('./raw'))` → auto-run `--update`. Supports: Twitter/X, arXiv, PDF, images, any webpage.

### --update / --cluster-only / --watch / git hooks
**Read `graphify-reference.md`** for the full code blocks for these modes.

---

## Integration Points (Fortive-Specific)

### UBI Platform (AzureDataBricks repo — 646 files)
Run on specific stream folders (e.g., `FlukeCoreGrowth/Mart/Refresh/`) not the repo root. The repo has 386 SQL + 224 Python files — too many for a single graph. Scope by stream.

### Neo4j (UBI Gold Graph)
Use `--neo4j-push` to enrich the existing Fabric Lakehouse Neo4j instance. MERGE semantics — safe to re-run.

### Always-On Mode
```bash
graphify claude install
```
Writes PreToolUse hook: before every Glob/Grep, Claude reads GRAPH_REPORT.md first. Navigates by structure instead of keyword matching. Reduces tool calls 5-10x for architecture questions.
