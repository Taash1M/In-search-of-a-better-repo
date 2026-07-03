---
name: claude-max-tokens-truncation
description: Claude extraction max_tokens must be 64K+ for large drawings — 16K causes JSON truncation on complex multi-page PDFs
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e13fff43-ea99-4b04-9edb-0ab4118fbc30
---

Always set Claude `max_tokens` to at least 65,536 (not 16,384) for document extraction tasks that produce structured JSON output.

**Why:** During PLM drawing extraction (Phase 5, 2026-05-30), 5/458 drawings consistently failed with "Unterminated string" JSON parse errors. Claude's output was truncating at ~36-47K chars because `max_tokens` was set to 16,384. These were complex multi-page drawings with large BOMs, many notes, and full page text content. The JSON output simply exceeded the token budget and got cut off mid-string. Bumping to 65,536 resolved all 5.

**How to apply:** Whenever building extraction pipelines that call Claude with structured JSON output:
1. Default `max_tokens` to 65,536 (Claude Sonnet 4.6 supports up to 64K output)
2. For the cloud twin (`extract_drawings_cloud.py`), update the same setting
3. Watch for "Unterminated string" or "Expecting delimiter" JSON parse errors — these almost always mean output truncation, not malformed generation
4. If 64K still truncates (unlikely), split into per-page extraction passes and merge results
