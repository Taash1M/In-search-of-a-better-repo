---
name: markitdown-bench
description: "Benchmark MarkItDown against current Claude Vision extraction on PLM drawings. Converts sample documents via 3 methods (MarkItDown local, MarkItDown + Azure CU, current vision pipeline), measures speed/cost/quality, and generates a comparison report. Trigger on: markitdown benchmark, extraction benchmark, document conversion comparison, markitdown vs vision, cheaper extraction."
---

# MarkItDown Benchmarking Skill

Compare MarkItDown (local + cloud) against the current Claude Vision pipeline for PLM drawing extraction.

## When to Use

- Benchmarking MarkItDown against current extraction method
- Testing document conversion quality on a sample set
- Estimating cost savings from switching extraction approaches
- Evaluating Azure Content Understanding vs. local extraction

## Prerequisites

```bash
pip install "markitdown[all]"
pip install openai  # for OCR plugin (optional)
```

Verify installation:
```python
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("test.pdf")
print(result.markdown[:200])
```

## Architecture: Three Methods Compared

```
Method A: Current (Claude Vision)
  PDF → pymupdf render @ 150 DPI → PNG base64 → Claude Sonnet Vision API → JSON
  Cost: ~$0.028/doc | Speed: ~79s/doc | Quality: High (vision understands layout)

Method B: MarkItDown Local (FREE)
  PDF → pdfminer + pdfplumber → Markdown text/tables → Claude Text API → JSON
  Cost: ~$0.002/doc (text tokens only) | Speed: ~5-15s/doc | Quality: Variable

Method C: MarkItDown + Azure CU (CLOUD)
  PDF → Azure Content Understanding → structured Markdown + YAML fields → Claude Text API → JSON
  Cost: ~$0.01-0.02/doc (Azure CU + text tokens) | Speed: ~10-30s/doc | Quality: High
```

## Step 1: Select Sample Documents

Choose 10-20 documents that represent the full spectrum:

| Category | Count | Why |
|----------|-------|-----|
| Simple single-sheet PDFs (text-heavy) | 3-4 | Best case for MarkItDown local |
| Multi-page drawings with BOM tables | 3-4 | Tests table extraction quality |
| Scanned/image-heavy PDFs | 2-3 | Worst case for local extraction (needs OCR) |
| DOCX/PPTX files | 2-3 | Tests non-PDF converters |
| Complex assembly drawings | 2-3 | Tests layout understanding |

Use documents from `<USER_HOME>/OneDrive - <ORG>\AI\Technical Validation\PLM-AI-Drawing-tool\` that already have ground-truth extraction results from the current pipeline.

## Step 2: Create Benchmark Script

Create `markitdown_benchmark.py` in the project folder. The script should:

### 2a. Method B — MarkItDown Local Extraction

```python
import time
import json
from pathlib import Path
from markitdown import MarkItDown

def extract_with_markitdown_local(file_path: str) -> dict:
    """Extract document content using MarkItDown local (no cloud APIs)."""
    md = MarkItDown()
    
    start = time.time()
    result = md.convert(file_path)
    elapsed = time.time() - start
    
    markdown_text = result.markdown
    
    return {
        "method": "markitdown_local",
        "file": str(file_path),
        "elapsed_seconds": round(elapsed, 2),
        "markdown_length": len(markdown_text),
        "markdown_preview": markdown_text[:500],
        "markdown_full": markdown_text,
        "has_tables": "|" in markdown_text and "---" in markdown_text,
        "estimated_input_tokens": len(markdown_text) // 4,  # rough estimate
        "estimated_cost_usd": (len(markdown_text) // 4) * 3 / 1_000_000,  # Sonnet input rate
    }
```

### 2b. Method C — MarkItDown + Azure Content Understanding

```python
def extract_with_markitdown_azure_cu(file_path: str, cu_endpoint: str) -> dict:
    """Extract using MarkItDown with Azure Content Understanding."""
    md = MarkItDown(cu_endpoint=cu_endpoint)
    
    start = time.time()
    result = md.convert(file_path)
    elapsed = time.time() - start
    
    markdown_text = result.markdown
    
    return {
        "method": "markitdown_azure_cu",
        "file": str(file_path),
        "elapsed_seconds": round(elapsed, 2),
        "markdown_length": len(markdown_text),
        "markdown_preview": markdown_text[:500],
        "markdown_full": markdown_text,
        "has_tables": "|" in markdown_text and "---" in markdown_text,
        "has_yaml_fields": markdown_text.startswith("---"),
        "estimated_input_tokens": len(markdown_text) // 4,
        "estimated_cost_usd": 0.01 + (len(markdown_text) // 4) * 3 / 1_000_000,  # Azure CU + Sonnet
    }
```

### 2c. Method A — Current Vision Pipeline (baseline)

Reference the existing results from prior extraction runs. Do NOT re-run the full vision pipeline — use the saved extraction results as ground truth for comparison. If no cached results exist, extract metadata from the existing Neo4j graph or JSON outputs.

### 2d. Quality Comparison

After extracting with all methods, send the MarkItDown markdown to Claude with the SAME structured extraction prompt used in the current pipeline. Then compare field-by-field:

```python
COMPARISON_FIELDS = [
    "drawing_number", "drawing_title", "revision_level", "drawing_type",
    "sheet_size", "cage_code", "bom_items_count", "primary_material",
    "general_tolerances", "key_dimensions", "notes_count",
    "compliance_marks", "cross_references"
]

def compare_results(baseline: dict, candidate: dict) -> dict:
    """Compare extraction results field by field."""
    matches = 0
    mismatches = []
    missing = []
    
    for field in COMPARISON_FIELDS:
        baseline_val = baseline.get(field, "")
        candidate_val = candidate.get(field, "")
        
        if not baseline_val and not candidate_val:
            continue  # Both empty, skip
        
        if str(baseline_val).strip().lower() == str(candidate_val).strip().lower():
            matches += 1
        elif not candidate_val:
            missing.append(field)
        else:
            mismatches.append({
                "field": field,
                "baseline": baseline_val,
                "candidate": candidate_val
            })
    
    total = matches + len(mismatches) + len(missing)
    
    return {
        "accuracy": round(matches / total * 100, 1) if total > 0 else 0,
        "matches": matches,
        "mismatches": mismatches,
        "missing_fields": missing,
        "total_fields": total
    }
```

## Step 3: Run the Benchmark

```python
def run_benchmark(sample_dir: str, cu_endpoint: str = None) -> list[dict]:
    """Run full benchmark across all sample documents."""
    results = []
    sample_files = list(Path(sample_dir).glob("*.pdf"))
    # Also include DOCX, PPTX if present
    sample_files += list(Path(sample_dir).glob("*.docx"))
    sample_files += list(Path(sample_dir).glob("*.pptx"))
    
    for f in sample_files:
        print(f"Processing: {f.name}")
        entry = {"filename": f.name, "file_size_kb": f.stat().st_size // 1024}
        
        # Method B: MarkItDown Local
        try:
            entry["local"] = extract_with_markitdown_local(str(f))
        except Exception as e:
            entry["local"] = {"error": str(e)}
        
        # Method C: MarkItDown + Azure CU (if endpoint provided)
        if cu_endpoint:
            try:
                entry["azure_cu"] = extract_with_markitdown_azure_cu(str(f), cu_endpoint)
            except Exception as e:
                entry["azure_cu"] = {"error": str(e)}
        
        results.append(entry)
    
    return results
```

## Step 4: Generate Comparison Report

The report should be a markdown table with:

| Document | Pages | Size | Method A (Vision) | Method B (Local) | Method C (Azure CU) |
|----------|-------|------|-------------------|------------------|---------------------|
| | | | Time / Cost / Accuracy | Time / Cost / Accuracy | Time / Cost / Accuracy |

Plus summary statistics:

| Metric | Method A (Current) | Method B (Local) | Method C (Azure CU) |
|--------|-------------------|------------------|---------------------|
| Avg time/doc | ~79s | ? | ? |
| Avg cost/doc | ~$0.028 | ? | ? |
| Avg accuracy | ~92% | ? | ? |
| Total cost (820 drawings) | ~$23 | ? | ? |
| Total time (820 drawings) | ~18 hours | ? | ? |
| Best for | Image-heavy, scanned | Text-heavy, tables | All formats, highest quality |

## Step 5: Decision Matrix

After running the benchmark, populate this decision matrix:

| Criterion | Weight | Method A | Method B | Method C |
|-----------|--------|----------|----------|----------|
| Extraction accuracy | 40% | | | |
| Per-document cost | 25% | | | |
| Processing speed | 15% | | | |
| Handles scanned PDFs | 10% | | | |
| No cloud dependency | 10% | | | |
| **Weighted Score** | | | | |

## Output Artifacts

1. `markitdown_benchmark.py` — The benchmark script
2. `benchmark_results.json` — Raw results for all documents and methods
3. `benchmark_report.md` — Formatted comparison report with decision matrix
4. Sample markdown outputs in `markitdown_samples/` folder

## Cost Estimation Model

For the full 820-drawing corpus:

```
Method A (current):  820 docs * $0.028 = $22.96  |  820 * 79s / 8 workers = ~2.25 hours
Method B (local):    820 docs * $0.002 = $1.64    |  820 * 10s / 8 workers = ~17 minutes
Method C (Azure CU): 820 docs * $0.015 = $12.30  |  820 * 20s / 8 workers = ~34 minutes
```

These are estimates — the benchmark will produce actual numbers for the sample set that can be extrapolated.

## Hybrid Strategy (likely best outcome)

The benchmark will likely show that Method B (local) works well for text-heavy documents but fails on scanned/image-heavy PDFs. The recommended approach will likely be:

1. **Route by document type:** Use MarkItDown local for text-heavy PDFs (>100 chars extractable text per page)
2. **Escalate to Azure CU:** For scanned PDFs where MarkItDown local extracts <100 chars per page
3. **Fallback to Vision:** For documents where neither method produces acceptable quality

This mirrors the existing hybrid routing logic in `extract_supplemental_local.py` (TEXT_THRESHOLD = 100 chars).
