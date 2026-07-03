---
name: memory-index-discipline
description: "How to manage MEMORY.md as it grows — keep it a THIN auto-loaded index, never chain a memory2.md; detail lives in per-memory files; evict inline detail + archive completed one-offs when near the size cap"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

MEMORY.md is the **index that is auto-loaded every session**, and it has a hard ~24,985-byte cap. The cap
is on the INDEX, not on total memory — the per-memory files (`project_*`, `feedback_*`, `reference_*`,
`user_*`) have NO limit and are recalled on-demand, so the system scales to hundreds of memories as long
as the index stays thin.

**Why NOT a `memory2.md` (the tempting wrong answer):** the harness only auto-loads `MEMORY.md`. A second
index file would not be read at session start, so anything in it silently fails to recall — and chaining
splits the index into two places to keep in sync. Don't do it.

**The rules (also stated in MEMORY.md's own header so they survive across sessions):**
1. One line per memory in the index — `[Title](file.md) — hook + date`, ≤ ~120 chars.
2. Detail lives in the memory file, **never inline** in the index.
3. When the index nears its cap: (a) **evict** any inline-detail sections that crept in into their own
   `reference_*`/`project_*` files (each leaving a one-line pointer); (b) **archive** completed one-offs —
   terser hook, or drop the pointer entirely (the file persists and is still recall-able by description).

**Why:** the index had drifted to the cap with ~8 KB of inline detail (32% of the file) and 177-char-avg
lines. The 2026-06-23 refactor evicted 9 inline sections into standalone files → index dropped 24,972 →
18,107 bytes (72% of cap, ~6.8 KB headroom) with zero information loss. New memory files auto-mirror to
Obsidian `3-Resources/Claude Memory/` via the obsidian-memory-sync hook (it intentionally skips MEMORY.md).

**How to apply:** when you next write to MEMORY.md and it's near the cap, run the evict+archive pass
BEFORE adding new lines; keep every new index line to one tight pointer. Never create a `memory2.md`.

Related: [[obsidian-secondbrain]] · [[claude-code-hooks]]
