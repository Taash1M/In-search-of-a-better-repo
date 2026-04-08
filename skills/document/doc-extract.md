---
name: doc-extract
description: Extract structured data from PDFs, DOCX, and images using ContextGem (declarative LLM extraction), RAG-Anything (multimodal parsing), and agentic-doc (production batch patterns). Use when user needs to pull tables, fields, entities, or knowledge from documents — engineering drawings, contracts, reports, invoices, research papers.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
keywords: extract, parse, PDF, DOCX, document, OCR, table, invoice, contract, drawing, schema, concept, aspect, pipeline, multimodal, vision, batch
when: User says "extract from PDF", "parse document", "pull data from", "engineering drawing", "invoice extraction", "contract fields", "document pipeline", "batch extract", "what's in this PDF", "BOM extraction". Also when user points at a folder of PDFs/DOCX and wants structured output.
---

# Document Extraction Skill

You are a document extraction expert. You pull structured data from unstructured documents — PDFs, DOCX, images, scans — using the right tool for the job. You know three frameworks deeply and pick the one that fits.

## WHAT this skill knows that you don't

- ContextGem's 7 concept types and when each one fails silently
- How to route simple vs. complex extractions to different LLMs via DocumentLLMGroup roles
- RAG-Anything's 4 modal processors and context window tuning for technical documents
- Production batch patterns: PDF splitting, parallel processing, retry with jitter, bounding box grounding
- The difference between extracting FROM a document vs. understanding a document (extraction ≠ RAG)

## WHEN to use this skill

**Use when the user needs to:**
- Extract specific fields from documents (dates, amounts, names, tables, entities)
- Process engineering drawings, specs, or technical PDFs
- Build reusable extraction pipelines for document batches
- Parse documents with mixed content (text + images + tables + equations)
- Get structured JSON/Excel output from unstructured documents

**Do NOT use when:**
- User just wants to chat about a document → use RAG or direct reading
- User wants to build a full RAG pipeline → use `rag-multimodal` skill
- User wants to beautify a document → use `docx-beautify` skill
- Document is a simple text file → just read it

## Before Extracting, Ask Yourself

1. **What specific data needs to come out?** If the user can't name fields, help them define concepts first.
2. **Is this extraction or understanding?** Extraction = specific fields with types. Understanding = open-ended questions.
3. **One document or many?** One → interactive. Many → build a pipeline with ExtractionPipeline.
4. **What's in the document?** Text-only → ContextGem. Mixed content → RAG-Anything. Engineering drawings → vision extraction.
5. **Does the user need source references?** If yes, always set `add_references=True`.

---

## Decision Tree: Which Framework

```
START: What kind of document extraction?
  │
  ├─ Specific fields from text-based documents (contracts, reports, invoices)?
  │   └─► ContextGem — declarative concepts + aspects
  │       ├─ Single doc? → DocumentLLM + extract_all()
  │       └─ Batch? → ExtractionPipeline + loop
  │
  ├─ Documents with images, tables, charts, equations mixed in?
  │   └─► RAG-Anything — multimodal parsing + knowledge graph
  │       ├─ Need to query later? → process_document_complete() + aquery()
  │       └─ Just need parsed content? → parser only, skip KG
  │
  ├─ Engineering drawings, scans, image-heavy PDFs?
  │   └─► ContextGem vision extraction OR RAG-Anything image processor
  │       ├─ Known fields (part numbers, dimensions)? → ContextGem + vision concepts
  │       └─ Unknown structure, explore first? → RAG-Anything
  │
  └─ Large batch (100+ docs), production pipeline?
      └─► ContextGem pipeline + agentic-doc patterns
          (ExtractionPipeline for extraction, ThreadPoolExecutor for parallelism,
           tenacity retry for resilience)
```

---

## Framework 1: ContextGem — Declarative Extraction

**When:** You know what fields to extract. Best for contracts, reports, invoices, specs.

**Install:** `pip install contextgem`

**Repos:**
- Framework: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\contextgem\repo\`
- Taash1M fork (enhanced): `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Taashi_Github\18_ContextGem_Document_Extraction\`

### Core Pattern

```python
from contextgem import (
    Document, DocumentLLM, PdfConverter, DocxConverter,
    StringConcept, NumericalConcept, BooleanConcept,
    DateConcept, RatingConcept, JsonObjectConcept, LabelConcept,
    Aspect, ExtractionPipeline
)

# 1. Convert document
converter = PdfConverter()  # or DocxConverter()
doc = converter.convert("document.pdf")

# 2. Define what to extract
doc.add_concepts([
    StringConcept(name="Vendor Name", description="Company providing goods/services",
                  add_references=True, reference_depth="sentences", singular_occurrence=True),
    NumericalConcept(name="Total Amount", description="Total monetary value",
                     numeric_type="float", singular_occurrence=True),
    DateConcept(name="Due Date", description="Payment due date", singular_occurrence=True),
])

# 3. Extract
llm = DocumentLLM(model="anthropic/claude-sonnet-4-20250514", api_key=os.environ["ANTHROPIC_API_KEY"])
doc = llm.extract_all(doc, use_concurrency=True)

# 4. Access results
for concept in doc.concepts:
    for item in concept.extracted_items:
        print(f"{concept.name}: {item.value}")
```

### The 7 Concept Types — When to Use Each

| Type | Use When | Key Params | Gotcha |
|------|----------|------------|--------|
| `StringConcept` | Free-form text (names, descriptions, clauses) | `examples=[]` for complex extractions | Without examples, vague descriptions produce vague results |
| `BooleanConcept` | Yes/No questions | `singular_occurrence=True` always | Ambiguous text → wrong answer silently. Add "Unknown" via LabelConcept instead |
| `NumericalConcept` | Numbers (amounts, counts, durations) | `numeric_type="float"` or `"int"` | `numeric_type` is a hint, not enforced. Validate post-extraction |
| `DateConcept` | Dates | `singular_occurrence=True` for single dates | Ambiguous dates (02/03/2025) may be mis-parsed. Add context in description |
| `RatingConcept` | Subjective scores on a scale | `rating_scale=(1, 5)` (tuple, not RatingScale) | Always use `singular_occurrence=True` |
| `JsonObjectConcept` | Structured records (line items, addresses) | `structure={"field": type}` | Keep structures flat. Nested classes need `JsonObjectClassStruct` base |
| `LabelConcept` | Classification from fixed labels | `labels=[...]`, `classification_type="multi_class"` | multi_class always returns 1 label. Include "Other" or "N/A" as catch-all |

### Aspects vs. Concepts

- **Concepts** = specific data points (a date, a name, a number)
- **Aspects** = document sections/topics that contain concepts

Use aspects when you need to scope extraction to specific parts of a document:

```python
payment_aspect = Aspect(
    name="Payment Terms",
    description="Sections discussing payment schedules and amounts",
    concepts=[
        StringConcept(name="Payment Schedule", description="When payments are due"),
        NumericalConcept(name="Late Fee Percentage", description="Penalty rate", numeric_type="float"),
    ]
)
doc.add_aspects([payment_aspect])
```

**Constraint:** Aspect-level concepts can only use `extractor_text` or `reasoner_text` roles. No vision extraction inside aspects.

### Multi-Model Routing (DocumentLLMGroup)

Route simple extractions to fast/cheap models, complex reasoning to powerful models:

```python
from contextgem import DocumentLLMGroup

fast = DocumentLLM(model="openai/gpt-4o-mini", api_key=key, role="extractor_text")
powerful = DocumentLLM(model="anthropic/claude-sonnet-4-20250514", api_key=key, role="reasoner_text")

group = DocumentLLMGroup(llms=[fast, powerful])

# Simple fields → fast model
simple_concept = StringConcept(name="Title", description="Document title", llm_role="extractor_text")
# Complex reasoning → powerful model
complex_concept = RatingConcept(name="Risk Score", description="Overall risk assessment",
                                rating_scale=(1, 10), llm_role="reasoner_text")
```

**Rules:**
- Each role must be unique across LLMs in the group
- Minimum 2 LLMs in a group
- Fallback LLM must match the primary's role

### Reusable Pipelines (Batch Processing)

```python
pipeline = ExtractionPipeline(
    aspects=[payment_aspect, obligation_aspect],
    concepts=[vendor_concept, date_concept, amount_concept],
)

for file in pdf_files:
    doc = converter.convert(file)
    doc.add_pipeline(pipeline)  # Deep-copies — no shared state
    doc = llm.extract_all(doc, use_concurrency=True)
    results.append(doc)
```

### Vision Extraction (Images in Documents)

```python
from contextgem import create_image

# From PDF with images
doc = PdfConverter().convert("drawing.pdf", include_images=True)

# Or manually attach images
img = create_image("schematic.png")
doc = Document(raw_text="", images=[img])

# Vision concept — must use vision role
doc.add_concepts([
    StringConcept(name="Part Numbers", description="All part numbers visible in the drawing",
                  llm_role="extractor_vision"),
    JsonObjectConcept(name="BOM", description="Bill of materials",
                      structure={"part_number": str, "description": str, "quantity": int},
                      llm_role="extractor_vision"),
])

# Requires vision-capable model
llm = DocumentLLM(model="openai/gpt-4o", api_key=key)
doc = llm.extract_all(doc)
```

**Constraint:** Vision concepts are document-level only. Cannot be inside aspects. Cannot have references.

---

## Framework 2: RAG-Anything — Multimodal Parsing

**When:** Documents have mixed content (text + images + tables + equations). Need knowledge graph or multimodal querying.

**Install:** `pip install raganything`

**Repo:** `C:\Users\tmanyang\OneDrive - Fortive\Claude code\RAG\rag-anything\`

### Core Pattern

```python
from raganything import RAGAnything, RAGAnythingConfig

config = RAGAnythingConfig(
    parser="mineru",              # or "docling"
    parse_method="auto",          # "auto", "ocr", "txt"
    enable_image_processing=True,
    enable_table_processing=True,
    enable_equation_processing=True,
    context_window=1,             # pages around current item for context
    context_mode="page",          # "page" or "chunk"
    max_context_tokens=2000,
)

rag = RAGAnything(
    llm_model_func=your_llm_func,
    vision_model_func=your_vision_func,  # Optional, enables VLM queries
    embedding_func=your_embedding_func,
    config=config,
)

# Process document (parse + build knowledge graph)
await rag.process_document_complete("technical_spec.pdf", output_dir="./output")

# Query
result = await rag.aquery("What components are in the chassis assembly?", mode="hybrid")
```

### 4 Modal Processors

| Processor | Handles | Key Behavior |
|-----------|---------|--------------|
| `ImageModalProcessor` | Photos, diagrams, screenshots | Calls vision model with base64 image + surrounding context |
| `TableModalProcessor` | Markdown tables extracted from docs | LLM interprets tabular data with context |
| `EquationModalProcessor` | LaTeX formulas | LLM explains mathematical content |
| `GenericModalProcessor` | Fallback for unknown types | Handles any content type not matched above |

### Context Window Tuning

For technical documents (engineering drawings, specs), increase context:

```python
config = RAGAnythingConfig(
    context_window=2,          # 2 pages before + after (more context for technical docs)
    max_context_tokens=4000,   # Allow more context per item
    context_mode="page",       # Page-based for structured PDFs
)
```

### Query Modes

| Mode | Use When |
|------|----------|
| `"local"` | Specific factual questions about a section |
| `"global"` | Broad questions requiring cross-document understanding |
| `"hybrid"` | **Default choice** — combines local + global |
| `"naive"` | Simple keyword-based retrieval |
| `"mix"` | All modes combined |

---

## Framework 3: Production Patterns (from agentic-doc)

**When:** Processing large batches, need resilience, retries, parallel processing, bounding boxes.

**Repo:** `C:\Users\tmanyang\OneDrive - Fortive\Claude code\contextgem\agentic-doc\`

These patterns apply TO any framework above. Cherry-pick as needed.

### Pattern: Retry with Exponential Backoff + Jitter

```python
import tenacity

@tenacity.retry(
    wait=tenacity.wait_exponential_jitter(exp_base=1.5, initial=1, max=60, jitter=10),
    stop=tenacity.stop_after_attempt(3),
    retry=tenacity.retry_if_exception_type((ConnectionError, TimeoutError)),
)
def extract_with_retry(doc, llm):
    return llm.extract_all(doc, use_concurrency=True)
```

### Pattern: PDF Splitting for Large Documents

```python
from pypdf import PdfReader, PdfWriter
from pathlib import Path

def split_pdf(pdf_path, split_size=10):
    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    parts = []
    for start in range(0, total, split_size):
        writer = PdfWriter()
        end = min(start + split_size, total)
        for i in range(start, end):
            writer.add_page(reader.pages[i])
        part_path = Path(pdf_path).parent / f"part_{start}_{end}.pdf"
        writer.write(str(part_path))
        parts.append({"path": part_path, "start": start, "end": end})
    return parts
```

### Pattern: Parallel Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def process_batch(files, pipeline, llm, max_workers=4):
    def process_one(f):
        doc = PdfConverter().convert(str(f))
        doc.add_pipeline(pipeline)
        return llm.extract_all(doc, use_concurrency=True)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(executor.map(process_one, files), total=len(files)))
    return results
```

### Pattern: Connector Abstraction

```python
# Local files
from pathlib import Path
files = list(Path("./documents").glob("*.pdf"))

# SharePoint (via OneDrive sync)
files = list(Path(r"C:\Users\tmanyang\OneDrive - Fortive\...").glob("*.pdf"))

# S3 (download first, then process)
import boto3
s3 = boto3.client("s3")
for obj in s3.list_objects_v2(Bucket="bucket", Prefix="docs/")["Contents"]:
    s3.download_file("bucket", obj["Key"], f"./temp/{Path(obj['Key']).name}")
```

---

## 10 NEVER Rules

1. **NEVER treat a PDF as flat text.** Always use a converter (PdfConverter, MinerU, PyMuPDF) that preserves structure. *What happens:* Tables become garbled text, reading order breaks, images are lost entirely.
2. **NEVER skip `singular_occurrence=True`** for fields that should have exactly one value (dates, totals, titles). *What happens:* LLM extracts every number it sees as "Total Amount" — you get 15 results instead of 1.
3. **NEVER put vision concepts inside aspects.** Aspects are text-only. Vision concepts must be document-level. *What happens:* `ValueError: Vision concepts do not support aspects`.
4. **NEVER use BooleanConcept for ambiguous questions.** Use LabelConcept with ["Yes", "No", "Unclear"] instead. *What happens:* BooleanConcept silently returns False when the answer is actually "maybe" or "not stated".
5. **NEVER build complex nested JsonObjectConcept structures.** Keep flat. Split into multiple simpler concepts if needed. *What happens:* Prompt overloading — LLM returns partial/malformed JSON, extraction silently drops fields.
6. **NEVER process 100+ page PDFs in one shot.** Split into 10-page chunks, process in parallel, merge results. *What happens:* Context window overflow, timeout, or truncated extraction that misses later pages entirely.
7. **NEVER assume OCR output is correct.** Always validate key fields, especially numbers and dates from scanned documents. *What happens:* "1,250,000" becomes "1,250,0OO" — the O/0 confusion costs real money downstream.
8. **NEVER forget to set `add_references=True`** when the user needs to trace extracted values back to source text. *What happens:* User asks "where did this number come from?" and you can't answer.
9. **NEVER use `use_concurrency=True` without checking rate limits.** Concurrent extraction fires many parallel API calls. *What happens:* 429 rate limit errors cascade, retries compound, cost spikes.
10. **NEVER extract without defining concepts first.** If the user says "extract everything", help them name specific fields. *What happens:* Vague extraction = vague results. The LLM doesn't know what "everything" means.

---

## Default Choices (When in Doubt)

- **Framework:** ContextGem (most document extraction is field-based)
- **Model:** `openai/gpt-4o` for vision, `anthropic/claude-sonnet-4-20250514` for text
- **Concurrency:** Off for development, on for production batches
- **References:** Always on (`add_references=True`) unless user explicitly doesn't need them
- **Singular occurrence:** On for any field that should have exactly one value

## When the User Says "Extract Everything"

Don't blindly extract. Instead:

1. **Read the first page** of the document to understand its type
2. **Propose a concept list** based on the document type:
   - Invoice → vendor, date, amounts, line items, PO number
   - Contract → parties, dates, value, type, key clauses
   - Engineering drawing → drawing number, title, revision, BOM, materials
   - Report → title, author, date, key findings, recommendations
   - Datasheet → product name, specs, ratings, dimensions
3. **Ask the user to confirm or adjust** before extracting
4. Build the pipeline, extract, present results

This takes 30 seconds of clarification but saves 10 minutes of useless extraction.

---

## Common Workflows

### Workflow: Engineering Drawing Extraction

```python
# Engineering drawings are image-heavy PDFs — use vision extraction
from contextgem import PdfConverter, Document, DocumentLLM, StringConcept, JsonObjectConcept

converter = PdfConverter()
doc = converter.convert("chassis_assembly.pdf", include_images=True, page_range=(1, 5))

doc.add_concepts([
    StringConcept(name="Drawing Number", description="Engineering drawing/document number",
                  llm_role="extractor_vision", singular_occurrence=True),
    StringConcept(name="Revision", description="Drawing revision level",
                  llm_role="extractor_vision", singular_occurrence=True),
    StringConcept(name="Title", description="Drawing title from title block",
                  llm_role="extractor_vision", singular_occurrence=True),
    JsonObjectConcept(name="BOM Items", description="Bill of materials line items",
                      structure={"item_no": int, "part_number": str,
                                 "description": str, "quantity": int},
                      llm_role="extractor_vision"),
    StringConcept(name="Materials", description="Materials called out in the drawing",
                  llm_role="extractor_vision"),
    StringConcept(name="Key Dimensions", description="Critical dimensions with tolerances",
                  llm_role="extractor_vision"),
])

llm = DocumentLLM(model="openai/gpt-4o", api_key=os.environ["OPENAI_API_KEY"])
doc = llm.extract_all(doc)
```

### Workflow: Contract Field Extraction (Batch)

```python
pipeline = ExtractionPipeline(
    concepts=[
        StringConcept(name="Parties", description="All contracting parties",
                      add_references=True, reference_depth="sentences"),
        DateConcept(name="Effective Date", description="Agreement start date",
                    singular_occurrence=True),
        DateConcept(name="Expiration Date", description="Agreement end date",
                    singular_occurrence=True),
        NumericalConcept(name="Contract Value", description="Total contract value",
                         numeric_type="float", singular_occurrence=True),
        LabelConcept(name="Contract Type", description="Type of agreement",
                     labels=["NDA", "MSA", "SOW", "Amendment", "Other"],
                     singular_occurrence=True),
        RatingConcept(name="Risk Level", description="Overall contractual risk",
                      rating_scale=(1, 5), llm_role="reasoner_text",
                      add_justifications=True, justification_depth="balanced",
                      singular_occurrence=True),
    ],
    aspects=[
        Aspect(name="Payment Terms", description="Payment schedules, amounts, penalties",
               concepts=[
                   StringConcept(name="Payment Schedule", description="When payments are due"),
                   NumericalConcept(name="Late Fee", description="Late payment penalty percentage",
                                    numeric_type="float"),
               ]),
    ],
)

converter = DocxConverter()
for file in Path("./contracts").glob("*.docx"):
    doc = converter.convert(str(file))
    doc.add_pipeline(pipeline)
    doc = llm.extract_all(doc, use_concurrency=True)
    save_results(doc, file.stem)
```

### Workflow: Multimodal Technical Document

```python
# For documents with diagrams, tables, and text interleaved
from raganything import RAGAnything, RAGAnythingConfig

rag = RAGAnything(
    llm_model_func=claude_func,
    vision_model_func=gpt4o_vision_func,
    embedding_func=embedding_func,
    config=RAGAnythingConfig(
        parser="mineru",
        context_window=2,
        max_context_tokens=4000,
        enable_image_processing=True,
        enable_table_processing=True,
    ),
)

await rag.process_document_complete("technical_spec.pdf", output_dir="./output")

# Query the processed document
result = await rag.aquery("What are the key specifications?", mode="hybrid")
```

---

## Output Patterns

### Save Extraction Results to JSON

```python
import json

def extraction_to_dict(doc):
    results = {}
    for concept in doc.concepts:
        items = []
        for item in concept.extracted_items:
            entry = {"value": item.value}
            if hasattr(item, "justification") and item.justification:
                entry["justification"] = item.justification
            if hasattr(item, "reference_paragraphs") and item.reference_paragraphs:
                entry["references"] = [p.raw_text[:200] for p in item.reference_paragraphs]
            items.append(entry)
        results[concept.name] = items[0]["value"] if len(items) == 1 else items
    return results

with open("results.json", "w") as f:
    json.dump(extraction_to_dict(doc), f, indent=2, default=str)
```

### Save to Excel (Batch Results)

```python
import pandas as pd

rows = []
for doc, filename in zip(processed_docs, filenames):
    row = {"filename": filename}
    for concept in doc.concepts:
        if concept.extracted_items:
            row[concept.name] = concept.extracted_items[0].value
    rows.append(row)

df = pd.DataFrame(rows)
df.to_excel("extraction_results.xlsx", index=False)
```

---

## LLM Provider Configuration

```python
# Azure AI Foundry (Fortive)
llm = DocumentLLM(
    model="anthropic/claude-sonnet-4-20250514",
    api_key=os.environ["ANTHROPIC_FOUNDRY_API_KEY"],
    api_base="https://flk-team-ai-enablement-ai.services.ai.azure.com",
)

# OpenAI direct
llm = DocumentLLM(model="openai/gpt-4o", api_key=os.environ["OPENAI_API_KEY"])

# Ollama (local, free)
llm = DocumentLLM(model="ollama/llama3.2", api_base="http://localhost:11434")
```

### Cost Tracking

```python
llm = DocumentLLM(model="openai/gpt-4o", api_key=key, auto_pricing=True)
doc = llm.extract_all(doc)
print(f"Cost: ${llm.total_cost:.4f} | Input: {llm.total_usage.get('input_tokens', 0)} | Output: {llm.total_usage.get('output_tokens', 0)}")
llm.reset_usage()  # Reset for next document
```

---

## Reference File

For schemas, prompt templates, converter options, and advanced patterns, read:
`~/.claude/commands/doc-extract-reference.md`

**MANDATORY:** Read the reference file when:
- Building a JsonObjectConcept with nested structure
- Configuring RAG-Anything modal processors
- Setting up production batch processing with retries
- Working with engineering drawings or image-heavy documents
