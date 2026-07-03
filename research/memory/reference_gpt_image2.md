---
name: gpt-image-2-azure
description: "GPT Image 2 on Azure AI Foundry — endpoint, API format, prompt style, timing for generating consultant-grade PPTX illustrations"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 9055eea3-6ef7-4501-b1af-5635c15c4b21
---

GPT Image 2 is available on Azure AI Foundry for generating professional illustrations.

- **Credentials file**: `<USER_HOME>/OneDrive - <ORG>\Claude code\Presentation Beautification\gpt image to text 2 credentials.txt`
- **Endpoint**: `https://codevsclaude46-resource.services.ai.azure.com`
- **Deployment name**: `gpt-image-2`
- **API**: `POST /openai/deployments/gpt-image-2/images/generations?api-version=2025-04-01-preview`
- **Auth header**: `api-key: <key from credentials file>`
- **Recommended settings**: `size=1536x1024`, `quality=high`, `output_format=png`
- **Response**: `data[0].b64_json` (base64-encoded PNG)
- **Timing**: ~170s per image; 3 parallel threads works reliably
- **Style prompt suffix** (proven for PPTX panels): "Clean flat 2D corporate illustration, minimalist style, white background, muted blue and gray color palette with subtle accent colors. Professional consulting presentation quality. Isometric perspective. No text, no words, no labels, no letters in the image."
- **Gotcha**: requests library needs `timeout=300` (default 120s will time out)

- **Use-case infographic** (2026-05-21): 7 panels (1 hero + 6 category illustrations), 537s total across 3 parallel threads, cached in `%TEMP%/usecase_infographic/` for fast DOCX layout iteration. Output: `Claude_Code_UseCase_Infographic.docx`
- **MSIS 550 case competition** (2026-05-26): 6 panels for Anthropic vs. Google deck (envelopment, five forces, segmentation, roadmap, impact, closing). Sequential generation ~170s/image. Embedded via `add_picture_fit()` into Veritas Clean design. Second credentials location: `<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\gpt image to text 2 credentials.txt` (same endpoint/key).
- **Fluke AI Office Hours** (2026-05-27): 17 images across 2 batches (10 base + 7 V3-only). ~200s/image sequential. Largest: title_hero.png (1.6 MB, 207s), smallest: request_chaos.png (212 KB). 3-version PPTX tier: V1 text-only (1.4 MB), V2 illustrated 8 key slides (7.4 MB), V3 fully illustrated all 14 slides (13.2 MB). All generated from `generate_images.py` and `generate_images_v3.py` with `--skip-existing` support. OneDrive sync delay can make files appear absent to `ls` — check background task output file directly.

- **PLM GraphRAG Infographic v2** (2026-06-08): 3 panels (architecture, process flow, query flow) for 6-page landscape A4 infographic. ~166-175s/image sequential. Prompt length gotcha: prompts >600 chars cause HTTP 500 errors — keep infographic prompts concise. Output: `PLM_GraphRAG_Infographic_v2.docx` (1.6 MB) with 3x 1536x1024 panels at 10.9x7.3" in DOCX. Generator: `generate_infographic_v2.py` in Technical Validation folder.

Related: [[ai-navigator-pro]], [[Presentation Beautification Skill Project]], [[Team AI Enablement]], [[MSIS 550 Case Competition]], [[AI Office Hours]], [[plm-drawing-extraction-validation]]
