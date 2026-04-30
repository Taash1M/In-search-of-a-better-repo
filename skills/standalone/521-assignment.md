# MSIS 521 Assignment Workflow

You are executing a structured workflow for completing MSIS 521 (Text Analytics / NLP) assignments. Follow this systematic approach to ensure high-quality, validated deliverables.

## Assignment Directory
$ARGUMENTS (e.g., "<USER_HOME>/OneDrive\Taashi M\UW\Q3\521\Assignment 2")

---

## PHASE 1: Discovery & Context Gathering

### 1.1 List Assignment Contents
```
List all files in the assignment directory to identify:
- Assignment instructions (PDF)
- Lecture/reference materials (PDF)
- Data files (xlsx, csv, json, etc.)
```

### 1.2 Extract & Review Instructions
```
Read the assignment PDF and extract:
- Total number of parts/sections
- Specific questions for each part
- Required outputs (notebooks, reports, visualizations)
- Any specific models, methods, or libraries mandated
```

### 1.3 Review Lecture Materials
```
If lecture PDFs are provided:
- Extract key concepts, code patterns, and preferred approaches
- Note which lecture maps to which assignment part
- Identify the expected libraries (sklearn, transformers, nltk, gensim, etc.)
- Capture any code snippets that should be used as templates
```

### 1.4 Inspect Data Files
```
For each data file:
- Load and display shape, columns, dtypes
- Check for missing values
- Preview first few rows
- Understand the relationship between data and questions
```

---

## PHASE 2: Solution Development

### 2.1 Create Task List
```
Use TaskCreate to create trackable tasks for:
- Each notebook to be created
- Testing and validation
- Final deliverables
```

### 2.2 Notebook Structure Requirements
Each notebook MUST include:

**Header Cell (Markdown):**
- Course name and assignment title
- Part number and description

**For Each Question:**
1. **Question Markdown Cell** - Quote the exact question text using blockquote format:
   ```markdown
   ### Question X
   > *"Exact question text from assignment..."*
   ```

2. **Code Cell(s)** - With extensive comments:
   - Section headers using `# ============` blocks
   - Step-by-step explanations for junior developers
   - Inline comments for non-obvious logic

3. **Answer Markdown Cell** (for interpretation questions) - Provide written analysis

**Summary Section (at end):**
- Consolidate answers to all interpretation questions

### 2.3 Code Standards
```python
# ============================================================
# Step X: Description of what this section does
# ============================================================

# Detailed comment explaining the next operation
result = some_function(params)  # inline comment if needed
```

### 2.4 Colab Compatibility
Include auto-install block at the start of each notebook:
```python
import importlib, subprocess, sys
for pkg, imp in [('package-name', 'import_name'), ...]:
    if importlib.util.find_spec(imp) is None:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-q', pkg])
```

### 2.5 Reproducibility
- Always set `random_state` parameter (prefer 42)
- Suppress benign warnings that clutter output
- Use dynamic labels instead of hardcoded values where possible

---

## PHASE 3: Notebook Generation

### 3.1 Generation Script
Create a Python script (e.g., `create_notebooks.py`) that:
- Uses `json` to build valid .ipynb structure
- Generates unique cell IDs (uuid) for nbformat 5+ compatibility
- Outputs to the assignment directory

### 3.2 Cell ID Requirement
```python
import uuid

def code(source_text):
    return {
        "cell_type": "code",
        "id": str(uuid.uuid4())[:8],  # REQUIRED for modern Jupyter
        "metadata": {},
        "source": source_lines,
        "outputs": [],
        "execution_count": None
    }
```

### 3.3 Archive Generation Scripts
Move generation scripts to an `archive/` subdirectory for reference.

---

## PHASE 4: Testing & Validation

### 4.1 Install Test Dependencies
```
pip install jupyter nbconvert ipykernel
```

### 4.2 Execute Notebooks via nbconvert
```bash
jupyter nbconvert --to notebook --execute --ExecutePreprocessor.timeout=600 --inplace notebook.ipynb
```

### 4.3 Validation Checklist
For each executed notebook, verify:
- [ ] Zero errors in all code cells
- [ ] Zero warnings in stderr (or only benign ones like HF Hub auth notice)
- [ ] All expected outputs present (tables, charts, numeric results)
- [ ] Markdown answers align with code outputs
- [ ] Cell IDs present (no MissingIDFieldWarning)

### 4.4 Audit Script
```python
import json
with open('notebook.ipynb') as f:
    nb = json.load(f)
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        for out in cell.get('outputs', []):
            if out.get('output_type') == 'error':
                print(f"ERROR: {out['ename']}: {out['evalue']}")
```

---

## PHASE 5: Final Deliverables

### 5.1 Solution Folder Structure
Create a clean solution directory (e.g., `orpusolution/`) containing:
```
orpusolution/
├── IA2_Part1.ipynb      # Executed notebook with outputs
├── IA2_Part2.ipynb      # Executed notebook with outputs
├── data_file_1.xlsx     # Required data files
├── data_file_2.csv
└── CheatSheet.docx      # Reference document
```

### 5.2 Final Execution Test
Execute ALL notebooks from the solution folder to confirm:
- Data files are found (relative paths work)
- No dependency on parent directory files
- Complete standalone package for submission

### 5.3 Cheat Sheet Generation
Create a 5-page reference document (DOCX or PDF) including:

**Content Requirements:**
- Conceptual diagrams (use matplotlib to generate)
- Key code snippets from the notebooks
- Reference tables (functions, parameters, when-to-use)
- Common pitfalls and tips

**Structure:**
1. Title + Overview
2. Concept 1: Theory + Pipeline Diagram + Code
3. Concept 1: Interpreting Results + Reference Table
4. Concept 2: Theory + Pipeline Diagram + Code
5. Concept 2: Results + Comparison Table + Tips

---

## PHASE 6: Quality Checklist

Before declaring completion, verify:

### Notebooks
- [ ] All questions quoted in markdown before code cells
- [ ] Extensive code comments for junior developers
- [ ] Dynamic labels (not hardcoded topic/term names)
- [ ] random_state set for reproducibility
- [ ] Auto-install block for Colab compatibility
- [ ] Cell IDs present (no warnings)
- [ ] Executed with outputs embedded
- [ ] Summary/interpretation markdown at end

### Solution Folder
- [ ] All required files present
- [ ] Notebooks execute successfully from this folder
- [ ] Data files included
- [ ] Cheat sheet included

### Archive
- [ ] Generation scripts preserved in archive/ folder

---

## Common Libraries by Topic

| Topic | Libraries |
|-------|-----------|
| Text Preprocessing | nltk, re, html |
| Document-Term Matrix | sklearn.feature_extraction.text.CountVectorizer, TfidfVectorizer |
| Topic Modeling (LDA) | sklearn.decomposition.LatentDirichletAllocation, gensim |
| Clustering | sklearn.cluster.KMeans, AgglomerativeClustering |
| Sentiment (Traditional) | nltk.sentiment.vader.SentimentIntensityAnalyzer |
| Sentiment (BERT) | transformers.pipeline with sentiment-analysis task |
| Visualization | matplotlib, seaborn |
| Document Generation | python-docx |

---

## Example Invocation

```
/521-assignment "C:\Users\...\Assignment 2"
```

This will:
1. Discover and analyze all assignment materials
2. Create solution notebooks following all standards
3. Test and validate execution
4. Generate final deliverables in solution folder
5. Create reference cheat sheet
