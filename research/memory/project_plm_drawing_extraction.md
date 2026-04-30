---
name: PLM Drawing Extraction Validation
description: Technical validation of doc-extract skill on 20 PLM engineering drawings. 94% title block accuracy, 80% BOM accuracy. Key learnings on ContextGem vision routing and API key rotation.
type: project
---

## Overview

First real-world test of the `doc-extract` skill on 20 Fluke engineering drawings from SharePoint PLM.

**Why:** Validate whether AI vision extraction can replace manual metadata entry for PLM documents.

**How to apply:** Use these learnings when running future doc-extract jobs or building PLM integration pipelines.

## Key Results

- **18/19 PDFs** processed in 3.6 minutes (1 skipped at 21MB)
- **94 BOM items** extracted across 8 drawings
- Title block metadata: **89-100% accuracy** (drawing #, title, revision, type)
- BOM extraction: **80% accuracy** (tabular BOMs excellent, callout-style BOMs incomplete)
- Cost: ~$0.028/drawing

## Critical Learnings

1. **ContextGem v0.22.0 has no PdfConverter** — use pymupdf to render pages as images, feed via `create_image()`
2. **ContextGem DocumentLLM defaults to `extractor_text`** — must set `role="extractor_vision"` explicitly for vision concepts, otherwise they are silently skipped
3. **ContextGem + Azure AI Foundry routing broken** — litellm direct calls work, ContextGem's internal routing gets 404s
4. **ANTHROPIC_FOUNDRY_API_KEY env var was rotated** — the env var (`fn76FGjIhF...`) differs from settings.json key (`5RjMeVsH...`). Always verify key value, not just presence.
5. **BOM extraction needs two-pass approach** for assembly drawings where BOM is on separate sheet or as callouts

## Output Location

`<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\Document extraction - PLM Drawings\`

## Recommendation

Phase 1 (title block metadata): Ready for pilot deployment
Phase 2 (BOM extraction): Needs two-pass enhancement before production
Phase 3 (production pipeline): SharePoint integration, parallel processing, PLM validation
