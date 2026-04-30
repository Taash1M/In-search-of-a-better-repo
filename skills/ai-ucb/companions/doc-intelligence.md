---
name: doc-intelligence
description: Parse, extract, and understand documents with layout-aware processing, OCR, image restoration, and LLM-powered structured extraction. Supports PDF, DOCX, images. Use when user needs to extract structured data from documents, parse complex PDFs with tables/charts/images, process scanned documents, or build document understanding pipelines. Works standalone or as AI UCB Phase 2 enhancement.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# Document Intelligence Skill

You are a document processing expert. You build pipelines that parse, extract, and understand documents — converting unstructured PDFs, DOCX files, and images into structured, queryable data. You combine layout detection, OCR, image restoration, and LLM-powered extraction into production-grade workflows.

**Cherry-picked from:** Doctra (parsing engine), ContextGem (extraction framework), Azure AI Document Intelligence (enterprise).

## When This Skill Activates

- User needs to extract structured data from PDFs, DOCX, or images
- User has scanned/damaged documents needing OCR or restoration
- User wants to parse tables, charts, or figures from documents
- User needs declarative extraction (entities, aspects, concepts) from text
- AI UCB Phase 2 dispatches `doc-intelligence` archetype or requests enhanced parsing for RAG pipeline
- User mentions: "parse PDF", "extract tables", "OCR", "document intelligence", "contract extraction", "invoice processing"

## Core Principles

1. **Layout-first parsing.** Never treat PDFs as flat text. Always detect layout regions (text, table, chart, figure) before extraction.
2. **Right tool for the job.** Use Azure AI Document Intelligence for enterprise/forms. Use Doctra patterns for complex multi-element PDFs. Use ContextGem patterns for declarative extraction from parsed text.
3. **Preserve structure.** Tables must remain tabular. Charts must be converted to structured data. Reading order must be maintained.
4. **Trace everything.** Every extracted item must reference its source location (page, paragraph, bounding box).
5. **Cost-aware.** Track LLM/VLM API calls and costs. Use OCR before VLM when possible.

---

## Architecture: Three Processing Tiers

### Tier 1: Layout-Aware Parsing (Doctra patterns)

Converts documents into structured content lists with element types.

```
INPUT: PDF / DOCX / Image
    ↓
[1] RASTERIZE — PDF → PIL images at 200 DPI (pdf2image / PyMuPDF)
    ↓
[2] LAYOUT DETECTION — PaddleOCR PP-DocLayout_plus-L
    Output: LayoutBox[] per page (text, table, chart, figure + bounding boxes + confidence)
    ↓
[3] READING ORDER — Sort boxes top-to-bottom, left-to-right
    ↓
[4] PER-ELEMENT EXTRACTION
    ├─ Text regions → OCR (PyTesseract or PaddleOCR)
    ├─ Tables → Crop image + VLM structured extraction → {headers, rows}
    ├─ Charts → Crop image + VLM chart-to-table → {title, headers, rows}
    ├─ Figures → Crop image + save + optional VLM description
    └─ Split tables → Detect cross-page splits, merge images, re-extract
    ↓
[5] OUTPUT — Markdown + HTML + Excel + cropped images
```

**Configuration:**

```python
# Parser config
PARSER_CONFIG = {
    "dpi": 200,                          # Rendering quality (150-300)
    "layout_model": "PP-DocLayout_plus-L", # PaddleOCR layout model
    "min_confidence": 0.3,               # Layout detection threshold
    "ocr_engine": "pytesseract",         # "pytesseract" or "paddleocr"
    "ocr_lang": "eng",                   # Tesseract language codes
    "merge_split_tables": True,          # Cross-page table merging
    "column_alignment_tolerance": 10.0,  # Split table alignment threshold
}
```

**OCR Engine Selection:**

| Engine | When to Use | Strengths | Weaknesses |
|--------|-------------|-----------|------------|
| PyTesseract | Default, most documents | Fast, lightweight, 100+ languages | Struggles with complex layouts |
| PaddleOCR (PP-OCRv5) | Complex/multilingual docs | Higher accuracy, GPU accel, document unwarping | Heavier dependencies |
| Azure AI Doc Intelligence | Enterprise forms/invoices | Pre-built models, key-value extraction, training | Cost per page, Azure dependency |

**Image Restoration (DocRes):**

For scanned or damaged documents, apply restoration before OCR:

```python
# DocRes restoration tasks
RESTORATION_TASKS = {
    "appearance":    "General image enhancement (default)",
    "dewarping":     "Perspective/curvature correction",
    "deshadowing":   "Shadow removal from scans",
    "deblurring":    "Motion/focus blur reduction",
    "binarization":  "Convert to clean B&W",
    "end2end":       "Full pipeline (all tasks)",
}
```

**Dependencies:**
```
pip install paddleocr paddlepaddle pdf2image pymupdf pytesseract pillow opencv-python openpyxl
# For DocRes: pip install torch torchvision scikit-image huggingface_hub
# For PaddleOCRVL: pip install paddleocrVL (end-to-end vision-language)
```

**VLM Providers for Chart/Table Extraction:**

| Provider | Model | Config |
|----------|-------|--------|
| Azure OpenAI | gpt-4o | `api_key` from Key Vault, `base_url` from AI Services endpoint |
| Google Gemini | gemini-2.0-flash | `GOOGLE_API_KEY` env var |
| Anthropic | claude-3.5-sonnet | `ANTHROPIC_API_KEY` env var |
| Ollama (local) | llava, bakllava | `http://localhost:11434` |

**VLM Extraction Schema (Pydantic):**

```python
from pydantic import BaseModel
from typing import List, Optional

class StructuredTable(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    headers: List[str]
    rows: List[List[str]]

class StructuredChart(BaseModel):
    title: Optional[str] = None
    chart_type: Optional[str] = None  # bar, line, pie, scatter
    description: Optional[str] = None
    headers: List[str]
    rows: List[List[str]]
```

**Output Formats:**

| Format | Function | Content |
|--------|----------|---------|
| Markdown | `write_markdown(lines, out_dir)` | Full document with inline image refs |
| HTML | `write_html(lines, out_dir)` | Styled document with responsive images |
| Excel | `write_structured_excel(items, path)` | One sheet per table/chart, TOC with hyperlinks, styled headers |
| Images | `save_box_image(page_img, box, out_dir)` | Cropped figures/charts/tables as PNG |
| JSON | `to_structured_dict(items)` | Structured items for downstream pipelines |

---

### Tier 2: Declarative Structured Extraction (ContextGem patterns)

After Tier 1 produces parsed text, apply declarative extraction to pull structured data.

```
INPUT: Parsed text (from Tier 1 or raw text)
    ↓
[1] DOCUMENT SETUP — Create Document with text, paragraphs, optional images
    ↓
[2] DEFINE EXTRACTION — Declare Concepts (what to extract) + Aspects (text segments)
    ↓
[3] LLM PROCESSING — Auto-generated prompts, schema validation, retries
    ↓
[4] OUTPUT — Typed extracted items with justifications + source references
```

**8 Concept Types:**

| Type | Extracts | Example |
|------|----------|---------|
| `StringConcept` | Free-form text | Contract parties, clause descriptions |
| `BooleanConcept` | True/False | "Has non-compete clause?", "Is signed?" |
| `NumericalConcept` | Numbers (int/float) | Total amount, page count, duration days |
| `DateConcept` | Dates | Effective date, expiration date |
| `RatingConcept` | Integer rating (bounded) | Risk score (1-5), compliance grade (1-10) |
| `JsonObjectConcept` | Structured JSON | Line items, address blocks, party details |
| `LabelConcept` | Classification labels | Document type, risk level, department |
| `Aspect` | Text segments | Key clauses, anomalies, obligations |

**Extraction Pattern:**

```python
from contextgem import Document, DocumentLLM, StringConcept, BooleanConcept, DateConcept, Aspect

# 1. Create document from parsed text
doc = Document(raw_text=parsed_text)

# 2. Define what to extract
doc.concepts = [
    StringConcept(
        name="Contracting Parties",
        description="Names of all parties to the agreement",
        add_references="paragraphs",      # Trace back to source
        add_justification="brief",         # Include reasoning
    ),
    DateConcept(
        name="Effective Date",
        description="When the agreement takes effect",
    ),
    BooleanConcept(
        name="Contains Non-Compete",
        description="Whether the document contains a non-compete clause",
        add_justification="detailed",
    ),
]

doc.aspects = [
    Aspect(
        name="Key Obligations",
        description="Material obligations of each party",
        add_references="sentences",
    ),
]

# 3. Process with LLM
llm = DocumentLLM(
    model="azure/gpt-4o",              # LiteLLM provider format
    api_key=api_key,
    api_base=endpoint,
)
doc = llm.extract_all(doc)

# 4. Access results
for item in doc.extracted_items:
    print(f"{item.concept_name}: {item.value}")
    print(f"  Justification: {item.justification}")
    print(f"  References: {[p.text[:50] for p in item.reference_paragraphs]}")
```

**LLM Provider Configuration (via LiteLLM):**

```python
# Azure OpenAI
llm = DocumentLLM(model="azure/gpt-4o", api_key="...", api_base="https://...", api_version="2024-12-01-preview")

# OpenAI direct
llm = DocumentLLM(model="openai/gpt-4o-mini", api_key="sk-...")

# Anthropic
llm = DocumentLLM(model="anthropic/claude-sonnet-4-20250514", api_key="...")

# Ollama (local)
llm = DocumentLLM(model="ollama/llama3", api_base="http://localhost:11434")
```

**LLM Roles (for DocumentLLMGroup):**

| Role | Use Case |
|------|----------|
| `extractor_text` | Standard text extraction (default) |
| `reasoner_text` | Chain-of-thought reasoning (o1, o4 models) |
| `extractor_vision` | Vision-only extraction (images) |
| `reasoner_vision` | CoT reasoning on images |
| `extractor_multimodal` | Combined text + vision |
| `reasoner_multimodal` | CoT reasoning multimodal |

**Extraction Pipeline (Reusable):**

```python
from contextgem import ExtractionPipeline

# Define once, apply to many documents
pipeline = ExtractionPipeline(
    aspects=[...],
    concepts=[...],
)

# Apply to each document
for doc in documents:
    doc.assign_pipeline(pipeline)
    doc = llm.extract_all(doc)
```

**Cost Tracking:**

```python
# After extraction
print(f"Total cost: ${llm.total_cost:.4f}")
print(f"Input tokens: {llm.total_input_tokens}")
print(f"Output tokens: {llm.total_output_tokens}")
```

**Dependencies:**
```
pip install contextgem  # Includes: litellm, pydantic, wtpsplit-lite, jinja2, pillow
```

---

### Tier 3: Azure AI Document Intelligence (Enterprise)

For enterprise forms, invoices, receipts — use Azure's purpose-built service.

```
INPUT: PDF / Image / TIFF
    ↓
[1] Upload to Azure AI Document Intelligence endpoint
    ↓
[2] Select model: prebuilt-invoice, prebuilt-receipt, prebuilt-layout, custom
    ↓
[3] Extract: key-value pairs, tables, entities, signatures, barcodes
    ↓
[4] Post-process with LLM for complex reasoning
    ↓
[5] Store to Cosmos DB / AI Search / Delta table
```

**API Pattern:**

```bash
# Analyze document
curl -X POST "https://{endpoint}/documentintelligence/documentModels/{model}:analyze?api-version=2024-11-30" \
  -H "Ocp-Apim-Subscription-Key: {key}" \
  -H "Content-Type: application/pdf" \
  --data-binary @document.pdf

# Get results
curl "https://{endpoint}/documentintelligence/documentModels/{model}/analyzeResults/{resultId}?api-version=2024-11-30" \
  -H "Ocp-Apim-Subscription-Key: {key}"
```

**Prebuilt Models:**

| Model | Use Case |
|-------|----------|
| `prebuilt-invoice` | Invoices (vendor, amounts, line items, tax) |
| `prebuilt-receipt` | Receipts (merchant, total, items) |
| `prebuilt-layout` | General layout (text, tables, figures, checkmarks) |
| `prebuilt-read` | Text extraction (OCR only) |
| `prebuilt-idDocument` | IDs, passports, driver's licenses |
| `prebuilt-businessCard` | Business cards |
| Custom | Train on your own document types |

---

## Tier Selection Guide

| Scenario | Tier | Why |
|----------|------|-----|
| Complex multi-element PDF (tables + charts + text + figures) | **Tier 1** | Layout detection preserves structure |
| Scanned/damaged PDF | **Tier 1** + DocRes | Image restoration before OCR |
| Extract specific fields from parsed text (contracts, reports) | **Tier 2** | Declarative concepts with reference tracing |
| Standard invoices, receipts, forms | **Tier 3** | Azure prebuilt models are purpose-built |
| Custom form with unique layout | **Tier 3** (custom model) | Train on your documents |
| Multi-step: parse PDF then extract fields | **Tier 1 → Tier 2** | Pipeline: parse first, extract second |
| RAG ingestion with rich documents | **Tier 1 → feed to rag-multimodal** | Layout-aware parsing produces better chunks |
| Engineering drawings (title blocks, BOMs, callouts) | **Vision Extraction** | Image-first — text extraction alone misses visual layout |
| Technical PDFs with mixed vector/raster content | **Vision Extraction → Tier 2** | Render pages as images, then declarative extraction on JSON output |

---

## Vision Extraction (Engineering Drawings & Image-Heavy PDFs)

For documents where the visual layout IS the data — engineering drawings, schematics, datasheets, assembly diagrams — use direct vision extraction. Text-based parsing cannot capture title blocks, callout annotations, or graphical BOMs.

**Proven in:** PLM Drawing Extraction technical validation (18/19 PDFs, 94% title block accuracy, 80% BOM accuracy, $0.03/drawing).

```
INPUT: PDF (engineering drawing, schematic, technical datasheet)
    |
[1] RASTERIZE — PyMuPDF renders pages as PNG at 150 DPI (max 5 pages)
    |
[2] ENCODE — base64 encode each page image
    |
[3] TEXT SUPPLEMENT — PyMuPDF getText() extracts embedded text as context
    |
[4] PROMPT BUILD — Assemble multimodal message:
    |   [image_url (base64 PNG), ..., text context, JSON schema prompt]
    |
[5] VISION LLM — litellm routes to Claude Sonnet / GPT-4o via Azure AI Foundry
    |   model: anthropic/claude-sonnet-4-6 (or openai/gpt-4o)
    |   max_tokens: 4096, temperature: 0
    |
[6] PARSE — Strip markdown fences, parse JSON, validate fields
    |
[7] OUTPUT — JSON + Excel (openpyxl with formatted headers)
```

**Configuration:**

```python
VISION_CONFIG = {
    "dpi": 150,                          # 150 DPI balances quality vs token cost
    "max_pages": 5,                      # Limit pages per extraction call
    "max_file_size_mb": 15,              # Skip files exceeding this
    "temperature": 0,                    # Deterministic extraction
    "max_tokens": 4096,                  # Response token budget
    "model": "anthropic/claude-sonnet-4-6",  # Vision-capable model
}
```

**Engineering Drawing Concept Set:**

```python
# Standard fields for engineering drawing extraction
DRAWING_CONCEPTS = {
    "drawing_number":  {"type": "string", "singular": True, "description": "Primary drawing/document number from title block"},
    "drawing_title":   {"type": "string", "singular": True, "description": "Drawing title from title block"},
    "revision_level":  {"type": "string", "singular": True, "description": "Current revision letter or number"},
    "drawing_type":    {"type": "label",  "singular": True, "labels": ["Assembly", "Part Drawing", "Schematic", "Wiring Diagram", "Datasheet", "Specification", "Other"]},
    "bom_items":       {"type": "json_array", "structure": {"item_no": "int", "part_number": "str", "description": "str", "quantity": "int", "material": "str"}},
    "materials":       {"type": "string", "description": "Materials called out in the drawing (alloys, plastics, coatings)"},
    "notes":           {"type": "string", "description": "Manufacturing notes, tolerances, compliance callouts (RoHS, REACH, PFAS)"},
}
```

**Two-Pass BOM Extraction (for assembly drawings):**

Assembly drawings often have BOMs on the last sheet (beyond the 5-page limit) or as graphical callouts rather than tables. Use a two-pass approach:

```
PASS 1: Azure AI Document Intelligence (prebuilt-layout)
    → Detect table regions and bounding boxes
    → Identify which pages contain BOM tables
    → Extract table structure (headers, rows, cell boundaries)

PASS 2: Vision LLM (Claude Sonnet / GPT-4o)
    → Send only the BOM region (cropped or specific pages)
    → Use focused prompt: "Extract the Bill of Materials table..."
    → Higher accuracy on the specific table vs. whole-page extraction
```

**LiteLLM Routing Pattern:**

```python
import litellm
import os, base64

os.environ["ANTHROPIC_API_KEY"] = api_key          # From Key Vault
os.environ["ANTHROPIC_API_BASE"] = api_base         # Azure AI Foundry endpoint

def extract_drawing(page_images_b64, embedded_text, concepts):
    """Vision extraction via litellm → Azure AI Foundry."""
    content = []
    for img_b64 in page_images_b64:
        content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}})
    if embedded_text:
        content.append({"type": "text", "text": f"Embedded text from PDF:\n{embedded_text}"})
    content.append({"type": "text", "text": build_extraction_prompt(concepts)})

    response = litellm.completion(
        model="anthropic/claude-sonnet-4-6",
        messages=[{"role": "user", "content": content}],
        max_tokens=4096, temperature=0,
    )
    return parse_json_response(response.choices[0].message.content)
```

**Accuracy Benchmarks (PLM Validation — 18 drawings):**

| Field | Accuracy | Notes |
|-------|----------|-------|
| Drawing Title | 100% | Robust across all title block formats |
| Drawing Type | 100% | 7-class classification, zero misclassification |
| Drawing Number | 94% | Ambiguity with supplier part numbers vs. controlling numbers |
| Notes | 94% | Rich extraction of compliance, tolerances, mfg specs |
| Revision Level | 89% | Null for non-revisioned docs (correct behavior) |
| Materials | 83% | Null for schematics with no material callouts (correct) |
| BOM Items | 80% | Tabular BOMs excellent; callout-style BOMs incomplete |

---

## Gotchas & Troubleshooting (Field-Tested)

Critical issues discovered during production validation:

| Issue | Symptom | Root Cause | Fix |
|-------|---------|------------|-----|
| **ContextGem vision silently skipped** | All vision concepts return empty; warning: "missing LLM roles {'extractor_vision'}" | `DocumentLLM` defaults to `extractor_text`. Concepts with `llm_role="extractor_vision"` are silently skipped. | Set `role="extractor_vision"` explicitly on `DocumentLLM` constructor |
| **ContextGem + Azure AI Foundry 404** | `NotFoundError: AnthropicException - {"error":{"code":"404"}}` | ContextGem's internal litellm routing cannot resolve Azure AI Foundry's `/anthropic/v1/messages` endpoint | Bypass ContextGem's LLM layer entirely. Use `litellm.completion()` directly with `ANTHROPIC_API_KEY` and `ANTHROPIC_API_BASE` env vars |
| **ContextGem PdfConverter missing** | `ImportError: cannot import name 'PdfConverter'` | ContextGem v0.22.0 only has `DocxConverter`, not `PdfConverter` | Use PyMuPDF to render pages as images, feed via `create_image()` for ContextGem or base64 for direct litellm |
| **API key env var stale** | `401 Unauthorized: invalid subscription key` | `ANTHROPIC_FOUNDRY_API_KEY` env var contains a rotated key. `os.environ.get()` returns the stale value, never falling through to default. | Always verify the key VALUE, not just presence. Read from Key Vault in production, not env vars. |
| **Drawing number ambiguity** | Model returns supplier PN instead of controlling number | Drawings have multiple numbers (FPN, controlling #, supplier #) and the model picks the most prominent one | Add prompt guidance: "Prefer the Fluke/controlling drawing number over supplier or vendor part numbers" |
| **BOM on last sheet** | BOM extraction returns empty or incomplete | Assembly drawing BOMs are often on sheet 5+ (beyond MAX_PAGES=5 limit) | Two-pass approach: first detect BOM pages, then extract from those specific pages |

---

## AI UCB Integration

### When Activated by AI UCB

This skill is invoked in two scenarios within the AI Use Case Builder:

**Scenario A: `doc-intelligence` archetype (Phase 2)**

When `ai-ucb-state.json` has `archetype: "doc-intelligence"`, Phase 2 (`/ai-ucb-pipeline`) dispatches to this skill for the pipeline templates.

**Validation checkpoint:** The orchestrator sets `state.requirements.pipeline.doc_intelligence_tier` to one of:
- `"tier1"` — Doctra-pattern layout parsing (complex PDFs)
- `"tier2"` — ContextGem-pattern declarative extraction
- `"tier3"` — Azure AI Document Intelligence (forms/invoices)
- `"tier1+tier2"` — Parse then extract (most common)
- `"tier3+tier2"` — Azure parse then LLM extraction

**State contract fields (set by Phase 0 Discovery):**

```json
{
  "requirements": {
    "pipeline": {
      "doc_intelligence_tier": "tier1+tier2",
      "document_types": ["pdf", "docx"],
      "extraction_concepts": [
        {"name": "Invoice Total", "type": "numerical"},
        {"name": "Vendor Name", "type": "string"},
        {"name": "Line Items", "type": "json_object"}
      ],
      "ocr_engine": "paddleocr",
      "enable_image_restoration": false,
      "vlm_provider": "azure",
      "output_formats": ["json", "excel", "delta"]
    }
  }
}
```

**Phase 2 generates these notebooks:**

| Notebook | Layer | Purpose |
|----------|-------|---------|
| `Bronze_{app}_DocIngest` | Bronze | Raw document storage + metadata catalog |
| `Silver_{app}_DocParse` | Silver | Tier 1 layout-aware parsing (or Tier 3 Azure API) |
| `Silver_{app}_DocExtract` | Silver | Tier 2 declarative extraction |
| `Gold_{app}_ExtractedData` | Gold | Business-ready structured output |
| `AILayer_{app}_Embeddings` | AI Layer | Embed extracted text for search (if RAG combo) |

**Scenario B: RAG archetype enhancement (Phase 2)**

When `archetype: "rag"` AND `requirements.pipeline.enhanced_parsing: true`, this skill enhances the standard RAG Bronze notebook with layout-aware parsing instead of basic PyPDF2.

**Validation checkpoint:** The orchestrator sets `state.requirements.pipeline.enhanced_parsing` to `true` when:
- Source documents contain tables, charts, or images
- User explicitly requests better document understanding
- Discovery phase identifies complex document types

**What changes in the RAG pipeline:**

| Standard RAG Bronze | Enhanced RAG Bronze (with doc-intelligence) |
|---|---|
| PyPDF2 text extraction | Tier 1 layout-aware extraction |
| Loses all tables/images | Preserves tables as markdown, saves images |
| Flat text chunking | Structure-aware chunking (table = chunk, text = chunked) |
| No image handling | Images described by VLM, descriptions embedded in chunks |

---

## DOCX Parsing

For Word documents, use specialized DOCX parsing (no OCR needed):

**Elements Extracted:**
- Paragraphs (with heading levels, formatting)
- Tables (preserving structure, spanning cells)
- Embedded images (with VLM analysis if enabled)
- Lists (with nesting levels)
- Footnotes, comments, headers/footers
- Hyperlinks (with URLs)

**Implementation:**

```python
# ContextGem DOCX converter (production-grade, lxml-based)
from contextgem.public.converters.docx import DocxConverter

converter = DocxConverter()
doc = converter.convert("contract.docx", output_format="markdown")

# Or Doctra DOCX parser (with VLM image analysis)
from doctra import StructuredDOCXParser
parser = StructuredDOCXParser(extract_images=True, vlm=vlm_instance)
parser.parse("contract.docx")  # → document.md, tables.xlsx, images/
```

---

## Split Table Detection

Tables spanning multiple PDF pages require special handling:

```python
# Detection: Line Segment Detector (LSD) checks column alignment
# across consecutive pages. If columns align within tolerance → merge.

SPLIT_TABLE_CONFIG = {
    "column_alignment_tolerance": 10.0,  # pixels
    "min_columns": 2,                    # minimum to consider
    "max_page_gap": 1,                   # consecutive pages only
}

# After detection, merge vertically:
# 1. Crop both table regions from their respective pages
# 2. Stack images vertically
# 3. Re-run OCR or VLM on merged image
# 4. Output as single table in results
```

---

## Output Integration Points

| Downstream Consumer | Output Format | Notes |
|---|---|---|
| RAG pipeline (`rag-multimodal`) | Content list (JSON) | Text + multimodal items with metadata |
| AI Search index | JSON documents | chunk_id, content, source_file_path, content_vector |
| Cosmos DB | JSON documents | Extracted fields + metadata |
| Delta table (Gold layer) | Structured DataFrame | Via Databricks notebook |
| Excel report | .xlsx | For human review of extracted data |
| Power BI | Delta/Parquet via ADLS | Published from Gold layer |

---

## Error Handling

| Error | Recovery |
|-------|----------|
| OCR returns empty text | Retry with different PSM mode, then fall back to VLM |
| Layout detection misses element | Lower `min_confidence` threshold, retry |
| VLM extraction fails schema validation | Retry with simplified prompt, fall back to OCR-only |
| DocRes restoration fails (OOM) | Fall back to CPU mode, reduce DPI |
| Split table merge misaligns | Skip merge, extract tables separately |
| LLM extraction timeout | Retry with shorter context window, batch smaller |
| Azure Doc Intelligence quota exceeded | Queue with backoff, warn user |

---

## Quality Validation

After extraction, validate:

```python
def validate_extraction(results, expected_fields):
    issues = []
    
    # 1. Completeness — all expected fields present?
    for field in expected_fields:
        if field not in results:
            issues.append(f"WARN: Missing field: {field}")
    
    # 2. Confidence — low-confidence extractions flagged
    for item in results:
        if item.get("confidence", 1.0) < 0.7:
            issues.append(f"WARN: Low confidence ({item['confidence']:.0%}): {item['name']}")
    
    # 3. Consistency — cross-field validation
    # e.g., line item totals should sum to invoice total
    
    # 4. Source tracing — every extraction has a reference
    for item in results:
        if not item.get("source_page") and not item.get("source_paragraph"):
            issues.append(f"INFO: No source reference: {item['name']}")
    
    return issues
```

---

## References

| Resource | Location |
|----------|----------|
| Doctra repo | `<USER_HOME>/OneDrive - <ORG>\Claude code\RAG\doctra\` |
| ContextGem repo | `<USER_HOME>/OneDrive - <ORG>\Claude code\RAG\contextgem\` |
| Azure AI Document Intelligence | `https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/` |
| AI UCB archetypes | `~/.claude/commands/ai-ucb/archetypes.md` (Archetype 3) |
| AI UCB pipeline templates | `~/.claude/commands/ai-ucb/pipeline-templates.md` |
