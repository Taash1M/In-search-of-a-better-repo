# Document Extraction Reference — Advanced Patterns & Schemas

> Loaded on demand by the doc-extract skill. Do not read unless instructed.

## ContextGem API Reference

### Document Converters — Full Options

**PdfConverter:**
```python
from contextgem import PdfConverter

converter = PdfConverter()
doc = converter.convert(
    "report.pdf",               # str, Path, or BinaryIO
    apply_markdown=True,        # Heading detection via font size/bold heuristics
    include_tables=True,        # Extract tables via pymupdf detection
    include_images=True,        # Extract embedded images (JPEG, PNG, WebP)
    page_range=(1, 10),         # 1-based inclusive range. None = all pages
    strict_mode=False,          # False = skip errors; True = raise on any failure
)

# Text-only extraction (no Document object)
text = converter.convert_to_text_format(
    "report.pdf", output_format="markdown", page_range=(1, 5)
)
```

**DocxConverter:**
```python
from contextgem import DocxConverter

converter = DocxConverter()
doc = converter.convert(
    "contract.docx",            # str, Path, or BinaryIO
    apply_markdown=True,        # Preserve heading/bold/italic as markdown
    include_tables=True,
    include_comments=True,
    include_footnotes=True,
    include_headers=True,
    include_footers=True,
    include_textboxes=True,
    include_images=True,
    include_links=True,
    include_inline_formatting=True,
    strict_mode=False,
)
```

**Limitations:**
- PdfConverter: No OCR for scanned PDFs. Preprocess with OCR tool first.
- DocxConverter: Only `.docx` (not `.doc`). No charts, SmartArt, complex embedded objects.
- Neither: No password-protected files.

### JsonObjectConcept — Structure Patterns

```python
# Simple flat structure
structure = {"vendor_name": str, "amount": float, "currency": str}

# Optional fields
structure = {"name": str, "email": str | None}

# Nested dict (no class needed)
structure = {"address": {"street": str, "city": str, "zip": str}}

# List of primitives
structure = {"tags": [str], "amounts": [float]}

# List of objects
structure = {"line_items": [{"description": str, "qty": int, "unit_price": float}]}

# Literal values (enum-like)
structure = {"status": Literal["active", "inactive", "pending"]}
```

**NOT supported:**
- `dict[str, SomeClass]` — use `[{"key": str, "value": SomeClass}]` instead
- Deeply nested class hierarchies without `JsonObjectClassStruct` base

### DocumentLLM — Full Parameters

```python
llm = DocumentLLM(
    model="anthropic/claude-sonnet-4-20250514",  # provider/model (LiteLLM format)
    api_key="...",
    api_base=None,                  # Custom endpoint (Azure, Ollama)
    api_version=None,               # Azure API version
    deployment_id=None,             # Azure deployment name
    role="extractor_text",          # LLM role for DocumentLLMGroup routing
    temperature=0.3,                # 0.0-1.0
    top_p=0.3,                      # Nucleus sampling
    max_tokens=4096,                # Standard models
    max_completion_tokens=16000,    # Reasoning models (o1, o4)
    reasoning_effort="high",        # "minimal", "low", "medium", "high", "xhigh"
    timeout=120,                    # Seconds
    auto_pricing=True,              # Track costs
    fallback_llm=None,              # Fallback DocumentLLM (must match role)
    seed=None,                      # For reproducibility
    system_message=None,            # Custom system prompt
)
```

### extract_all() — Full Parameters

```python
doc = llm.extract_all(
    document=doc,
    overwrite_existing=False,                   # Reprocess already-extracted concepts
    max_items_per_call=0,                       # 0=all in one call; >0=batch by N
    use_concurrency=False,                      # Parallel API calls
    max_paragraphs_to_analyze_per_call=0,       # 0=all paragraphs
    max_images_to_analyze_per_call=0,           # Document-level images only
    raise_exception_on_extraction_error=True,   # False=warn instead of raise
)
```

**Concurrency gotcha:** When `use_concurrency=True` and `max_items_per_call=0`, it's auto-set to 1 (each concept gets its own call).

### Concept Common Parameters

All 7 concept types share these:
```python
name: str                           # Required. Must be unique within document/aspect
description: str                    # Required. Must be unique. Drives LLM understanding
llm_role: str = "extractor_text"    # Role for LLMGroup routing
add_justifications: bool = False    # Include LLM reasoning
justification_depth: str = "brief"  # "brief", "balanced", "comprehensive"
justification_max_sents: int = 2    # Max justification sentences
add_references: bool = False        # Link to source text
reference_depth: str = "paragraphs" # "paragraphs" or "sentences"
singular_occurrence: bool = False   # Expect exactly 1 extracted item
examples: list = []                 # Few-shot examples (StringExample or JsonObjectExample)
```

### Accessing Extracted Results

```python
# After llm.extract_all(doc):

# Document-level concepts
for concept in doc.concepts:
    print(f"\n{concept.name}:")
    for item in concept.extracted_items:
        print(f"  Value: {item.value}")
        if item.justification:
            print(f"  Justification: {item.justification}")
        if item.reference_paragraphs:
            for p in item.reference_paragraphs:
                print(f"  Reference: {p.raw_text[:100]}...")
        if item.reference_sentences:
            for s in item.reference_sentences:
                print(f"  Sentence: {s.raw_text[:100]}...")

# Aspect-level concepts
for aspect in doc.aspects:
    print(f"\nAspect: {aspect.name}")
    for para in aspect.reference_paragraphs:
        print(f"  Paragraph: {para.raw_text[:100]}...")
    for concept in aspect.concepts:
        for item in concept.extracted_items:
            print(f"  {concept.name}: {item.value}")
```

### Serialization (Save/Load Results)

```python
# Save full document with extractions
json_str = doc.to_json()
with open("results.json", "w") as f:
    f.write(json_str)

# Load without re-extracting
from contextgem import Document
with open("results.json") as f:
    loaded = Document.from_json(f.read())

# Access results from loaded document
for concept in loaded.concepts:
    print(concept.name, [i.value for i in concept.extracted_items])
```

---

## RAG-Anything Reference

### RAGAnythingConfig — Full Parameters

```python
RAGAnythingConfig(
    # Parser
    parser: str = "mineru",                     # "mineru" or "docling"
    parse_method: str = "auto",                 # "auto", "ocr", "txt"

    # Multimodal toggles
    enable_image_processing: bool = True,
    enable_table_processing: bool = True,
    enable_equation_processing: bool = True,

    # Context extraction
    context_window: int = 1,                    # Pages/chunks around current item
    context_mode: str = "page",                 # "page" or "chunk"
    max_context_tokens: int = 2000,             # Hard limit
    include_headers: bool = True,
    include_captions: bool = True,
    context_filter_content_types: list = ["text"],

    # File handling
    use_full_path: bool = False,                # Basenames vs full paths in KG
    supported_file_extensions: list = [".pdf", ".jpg", ".jpeg", ".png", ...],

    # Batch
    max_concurrent_files: int = 1,
    recursive_folder_processing: bool = True,

    # Storage
    working_dir: str = "./rag_storage",
)
```

### Supported File Types

PDF, JPG, JPEG, PNG, BMP, TIFF, TIF, GIF, WebP, DOC, DOCX, PPT, PPTX, XLS, XLSX, TXT, MD

Office docs require LibreOffice installed for conversion.

### Query Functions

```python
# Standard text query
result = await rag.aquery(query="...", mode="hybrid")

# VLM-enhanced (auto if vision_model_func provided)
result = await rag.aquery(query="...", mode="hybrid", vlm_enhanced=True)

# Multimodal query (with attached content)
result = await rag.aquery_with_multimodal(
    query="Explain this table",
    multimodal_content=[{"type": "table", "table_body": "| A | B |\n|---|---|\n| 1 | 2 |"}],
    mode="hybrid",
)
```

### Content List Format (Pre-Parsed Input)

```python
content_list = [
    {"type": "text", "text": "Section content...", "page_idx": 0},
    {"type": "image", "img_path": "/abs/path/to/img.jpg", "image_caption": ["..."], "page_idx": 1},
    {"type": "table", "table_body": "| H1 | H2 |\n|---|---|\n| v1 | v2 |", "table_caption": ["..."], "page_idx": 2},
    {"type": "equation", "latex": "E = mc^2", "text": "Energy-mass equivalence", "page_idx": 3},
]

await rag.insert_content_list(content_list, file_path="document.pdf")
```

---

## Production Batch Patterns (from agentic-doc)

### Full Batch Processing Pipeline

```python
import os
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import tenacity
from contextgem import PdfConverter, DocumentLLM, ExtractionPipeline

# Config
INPUT_DIR = Path("./documents")
OUTPUT_DIR = Path("./results")
OUTPUT_DIR.mkdir(exist_ok=True)
BATCH_SIZE = 4
MAX_WORKERS = 5
SPLIT_SIZE = 10

# Setup
converter = PdfConverter()
llm = DocumentLLM(model="openai/gpt-4o", api_key=os.environ["OPENAI_API_KEY"], auto_pricing=True)
pipeline = ExtractionPipeline(concepts=[...], aspects=[...])

@tenacity.retry(
    wait=tenacity.wait_exponential_jitter(exp_base=1.5, initial=1, max=60, jitter=10),
    stop=tenacity.stop_after_attempt(3),
    retry=tenacity.retry_if_exception_type((ConnectionError, TimeoutError, Exception)),
)
def process_one(file_path):
    doc = converter.convert(str(file_path), include_images=True)
    doc.add_pipeline(pipeline)
    doc = llm.extract_all(doc, use_concurrency=True)
    # Save results
    result_path = OUTPUT_DIR / f"{file_path.stem}.json"
    result_path.write_text(doc.to_json())
    return {"file": file_path.name, "status": "success"}

# Batch execute
files = list(INPUT_DIR.glob("*.pdf"))
with ThreadPoolExecutor(max_workers=BATCH_SIZE) as executor:
    results = list(tqdm(executor.map(process_one, files), total=len(files), desc="Extracting"))

# Summary
success = sum(1 for r in results if r["status"] == "success")
print(f"Processed: {success}/{len(files)} | Cost: ${llm.total_cost:.4f}")
```

### Grounding / Bounding Box Pattern

For documents where you need to know WHERE on the page an extraction came from:

```python
# ContextGem references give paragraph/sentence-level grounding
# For pixel-level bounding boxes, use agentic-doc patterns:

import pymupdf
import numpy as np

def page_to_image(pdf_path, page_num, dpi=96):
    doc = pymupdf.open(pdf_path)
    page = doc[page_num]
    pix = page.get_pixmap(dpi=dpi)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    return img

def crop_region(img, box, page_width, page_height):
    """box = normalized [left, top, right, bottom] in 0-1 range"""
    h, w = img.shape[:2]
    x1 = max(0, int(box[0] * w))
    y1 = max(0, int(box[1] * h))
    x2 = min(w, int(box[2] * w))
    y2 = min(h, int(box[3] * h))
    return img[y1:y2, x1:x2]
```

### Error Tracking Pattern

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ExtractionResult:
    file: str
    status: str  # "success", "partial", "failed"
    concepts_extracted: int = 0
    concepts_total: int = 0
    error: Optional[str] = None
    cost: float = 0.0

results: list[ExtractionResult] = []

def process_with_tracking(file_path, pipeline, llm):
    result = ExtractionResult(file=file_path.name, status="failed",
                              concepts_total=len(pipeline.concepts))
    try:
        doc = converter.convert(str(file_path))
        doc.add_pipeline(pipeline)
        doc = llm.extract_all(doc, use_concurrency=True,
                              raise_exception_on_extraction_error=False)
        extracted = sum(1 for c in doc.concepts if c.extracted_items)
        result.concepts_extracted = extracted
        result.status = "success" if extracted == result.concepts_total else "partial"
        result.cost = llm.total_cost
    except Exception as e:
        result.error = str(e)
    results.append(result)
    return result
```

---

## Engineering Drawing Extraction — Detailed Schema

For Fluke/Fortive engineering drawings (the Test Drawings folder), use this extraction pipeline:

```python
from contextgem import (
    PdfConverter, DocumentLLM, ExtractionPipeline,
    StringConcept, NumericalConcept, JsonObjectConcept, LabelConcept
)

drawing_pipeline = ExtractionPipeline(
    concepts=[
        # Title block fields
        StringConcept(name="Drawing Number", description="Engineering drawing or document control number from the title block",
                      llm_role="extractor_vision", singular_occurrence=True),
        StringConcept(name="Drawing Title", description="Title of the engineering drawing from the title block",
                      llm_role="extractor_vision", singular_occurrence=True),
        StringConcept(name="Revision Level", description="Current revision (e.g., R, R004, Rev A)",
                      llm_role="extractor_vision", singular_occurrence=True),
        LabelConcept(name="Drawing Type", description="Type of engineering document",
                     labels=["Assembly Drawing", "Part Drawing", "Schematic", "Wiring Diagram",
                             "Datasheet", "Specification", "Other"],
                     llm_role="extractor_vision", singular_occurrence=True),

        # Content extraction
        JsonObjectConcept(name="BOM Items", description="Bill of materials / parts list",
                          structure={"item_no": str, "part_number": str,
                                     "description": str, "quantity": str, "material": str | None},
                          llm_role="extractor_vision"),
        StringConcept(name="Materials", description="Materials and finishes specified",
                      llm_role="extractor_vision"),
        StringConcept(name="Key Dimensions", description="Critical dimensions with tolerances",
                      llm_role="extractor_vision"),
        StringConcept(name="Notes", description="General notes, specifications, and callouts",
                      llm_role="extractor_vision"),
        StringConcept(name="Standards Referenced", description="Industry standards cited (ANSI, ISO, MIL, etc.)",
                      llm_role="extractor_vision"),
    ],
)
```

---

## Dependencies Summary

| Framework | Install | Key Dependencies |
|-----------|---------|------------------|
| ContextGem | `pip install contextgem` | litellm, pydantic, pymupdf, lxml, wtpsplit-lite, pillow |
| RAG-Anything | `pip install raganything` | lightrag-hku, mineru (or docling), huggingface_hub |
| Production patterns | manual | tenacity, pypdf, tqdm, concurrent.futures (stdlib) |

**Python:** 3.10 - 3.13

---

## Azure AI Foundry LLM Config (Fortive)

```python
# For ContextGem
llm = DocumentLLM(
    model="anthropic/claude-sonnet-4-20250514",
    api_key=os.environ.get("ANTHROPIC_FOUNDRY_API_KEY"),
    api_base="https://flk-team-ai-enablement-ai.services.ai.azure.com",
)

# For RAG-Anything (function-based)
async def llm_model_func(prompt, system_prompt=None, **kwargs):
    import litellm
    response = await litellm.acompletion(
        model="anthropic/claude-sonnet-4-20250514",
        messages=[
            {"role": "system", "content": system_prompt or ""},
            {"role": "user", "content": prompt},
        ],
        api_key=os.environ.get("ANTHROPIC_FOUNDRY_API_KEY"),
        api_base="https://flk-team-ai-enablement-ai.services.ai.azure.com",
    )
    return response.choices[0].message.content
```
