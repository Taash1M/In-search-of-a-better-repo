---
name: ai-ucb-docs
description: Phase 6 Documentation sub-skill for the AI Use Case Builder. Generates 10 enterprise documents (EA Document, Solution Design, Data Flow, API Spec, Developer Guide, User Guide, Operations Runbook, STM, Model Card, Architecture Decision Records) in Markdown, DOCX, YAML, and XLSX formats. Reads full state from ai-ucb-state.json and PROJECT_MEMORY.md. Invoke standalone or via orchestrator. Trigger when user mentions 'documentation', 'docs', 'generate docs', 'EA document', 'solution design', 'runbook', 'STM', 'developer guide', 'user guide', 'API spec', 'model card', or 'ADR'.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# AI Use Case Builder - Phase 6: Documentation

You are the Technical Writing agent. Your job is to generate 10 enterprise documents populated from the project state, then output in Markdown, DOCX, YAML, and XLSX formats using template-driven generation.

**Key principle:** Documents are generated from state, not written from scratch. Every diagram, table, and specification is populated from `ai-ucb-state.json` and `PROJECT_MEMORY.md`. This ensures accuracy and eliminates manual transcription errors.

**Template engine:** All documents use Jinja2 templates with state variables injected at render time. This separates document structure from content, making updates reliable and auditable.

## Access Control (Inherited)

1. **NEVER include API keys, connection strings, or secrets in documentation.** Use placeholder patterns like `{from-key-vault}`.
2. **NEVER generate documents before testing is complete.** Documents must reflect the tested, validated state.
3. **NEVER skip the STM for UBI-connected projects.** The 45-column STM is required for UBI governance.
4. **NEVER leave Jinja2 template variables unresolved.** Every `{{ variable }}` must resolve to a value. If missing, raise an explicit error naming the missing field.
5. **NEVER generate Model Cards without bias/limitations section.** Responsible AI requires transparent documentation of model constraints.

## Prerequisites

- Phase 5 (Testing) must be `completed` in `ai-ucb-state.json`
- Required state: all sections populated, `artifacts.test_report` exists
- Required packages: `pip install python-docx openpyxl jinja2 pyyaml`

## Documentation Flow

### Step 1: Read State and Gather Content

```python
import json, os
from pathlib import Path
from datetime import datetime

# Load state contract
state_path = Path("ai-ucb-state.json")
assert state_path.exists(), "ai-ucb-state.json not found in working directory"
state = json.loads(state_path.read_text())

# Validate prerequisites
assert state["phases"].get("test") == "completed", \
    f"Phase 5 (Test) must be completed. Current: {state['phases'].get('test')}"
assert state.get("artifacts", {}).get("test_report"), \
    "Test report artifact missing — run Phase 5 first"

# Load all state sections
memory = Path("PROJECT_MEMORY.md").read_text() if Path("PROJECT_MEMORY.md").exists() else ""
archetype = state["archetype"]
resources = state.get("resources", {})
artifacts = state.get("artifacts", {})
requirements = state.get("requirements", {})
naming = state.get("naming", {})
app_name = state.get("project_name", "unnamed-project")
app_slug = naming.get("app_slug", app_name)
env = naming.get("env", "dev")
timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
test_report = artifacts.get("test_report", {})

# Build template context (shared across all documents)
ctx = {
    "app_name": app_name,
    "app_slug": app_slug,
    "env": env,
    "archetype": archetype,
    "timestamp": timestamp,
    "subscription_model": state.get("subscription_model", "split"),
    "regions": state.get("regions", {}),
    "resources": resources,
    "requirements": requirements,
    "artifacts": artifacts,
    "test_report": test_report,
    "naming": naming,
    "cost_estimate": state.get("cost_estimate", {}),
    "memory": memory,
}
```

### Step 1b: Jinja2 Template Engine Setup

```python
from jinja2 import Environment, BaseLoader, StrictUndefined

# StrictUndefined ensures NO unresolved variables slip through
jinja_env = Environment(
    loader=BaseLoader(),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)

def render_template(template_str: str, context: dict) -> str:
    """Render a Jinja2 template with strict variable checking."""
    try:
        tmpl = jinja_env.from_string(template_str)
        return tmpl.render(**context)
    except Exception as e:
        raise ValueError(f"Template rendering failed: {e}. "
                         f"Check ai-ucb-state.json for missing fields.")

def validate_rendered(content: str, doc_name: str) -> list:
    """Post-render validation: check for unresolved placeholders and empty sections."""
    import re
    issues = []
    # Check for Jinja2 remnants
    jinja_remnants = re.findall(r'\{\{.*?\}\}|\{%.*?%\}', content)
    if jinja_remnants:
        issues.append(f"{doc_name}: {len(jinja_remnants)} unresolved template variables: {jinja_remnants[:3]}")
    # Check for empty sections (heading followed immediately by another heading)
    empty_sections = re.findall(r'^(#{1,4} .+)\n(?=#{1,4} )', content, re.MULTILINE)
    if empty_sections:
        issues.append(f"{doc_name}: {len(empty_sections)} empty sections: {[s[:40] for s in empty_sections[:3]]}")
    # Check for placeholder patterns that should have been resolved
    placeholders = re.findall(r'\{[a-z_]+\}', content)
    if placeholders:
        issues.append(f"{doc_name}: {len(placeholders)} unresolved placeholders: {placeholders[:5]}")
    return issues
```

### Step 2: Generate All 10 Documents

**Read** `ai-ucb/doc-templates.md` for all document templates.

Generate in this order (dependencies flow top-down):

| # | Document | Populates From | Format |
|---|----------|---------------|--------|
| 1 | Enterprise Architecture | archetype, resources, data flow | MD + DOCX |
| 2 | Solution Design | requirements, resources, PROJECT_MEMORY.md decisions | MD + DOCX |
| 3 | Data Flow Diagram | pipeline config, resource topology | MD + DOCX |
| 4 | API Specification | frontend config, Function App routes | OpenAPI 3.1 YAML + MD |
| 5 | Developer Guide | all artifacts, repo structure | MD + DOCX |
| 6 | End User Guide | frontend type, features | MD + DOCX |
| 7 | Operations Runbook | resources, monitoring config, test results | MD + DOCX |
| 8 | Source-to-Target Mapping | pipeline schemas, medallion tables | MD + XLSX |
| 9 | Model Card | AI config, test results, limitations | MD + DOCX |
| 10 | Architecture Decision Records | PROJECT_MEMORY.md decisions | MD + DOCX |

#### Doc 1: Enterprise Architecture Document

Populate from state using TOGAF ADM structure:

- **Phase A (Vision):** Use case name, archetype, business objectives from `PROJECT_MEMORY.md`
- **Phase B (Business):** Stakeholder map, business process from discovery requirements
- **Phase C (Information):** Data model from pipeline schemas, AI index schemas
- **Phase D (Technology):** Azure resource inventory from `resources`, C4 diagrams
- **Phase E (Opportunities):** Cost optimization from pricing estimates
- **Phase F (Migration):** Deployment plan from Sprint 9 artifacts

**Architecture diagrams** — use the `/azure-diagrams` sub-skill for publication-quality diagrams with actual Azure icons:

```python
# Try to import azure_diagrams from the Document Beautification project
# The module location is resolved dynamically — never hardcode user paths
import importlib, sys
from pathlib import Path

def _load_azure_diagrams():
    """Dynamically locate and load the azure_diagrams module."""
    # Search order: (1) already importable, (2) Document Beautification project
    if importlib.util.find_spec("azure_diagrams"):
        return importlib.import_module("azure_diagrams")
    # Search common locations relative to user profile
    candidates = [
        Path.home() / "OneDrive - <ORG>" / "Claude code" / "Document Beautification",
        Path.home() / "Claude code" / "Document Beautification",
        Path.cwd() / "lib",
    ]
    for candidate in candidates:
        if (candidate / "azure_diagrams.py").exists():
            sys.path.insert(0, str(candidate))
            return importlib.import_module("azure_diagrams")
    return None  # Fallback to ASCII diagrams

azure_diag = _load_azure_diagrams()

if azure_diag:
    # Build service list from state resources
    services = [{"name": r["name"], "type": r["type"]} for r in resources.values() if isinstance(r, dict)]
    img_path = azure_diag.quick_architecture(
        services=services,
        connections=[...],  # Built from archetype resource map
        output_path=str(docs_dir / "arch_diagram.png"),
        title=f"{app_name} Architecture",
        output_preset="docx_portrait",
    )
    doc.add_picture(img_path, width=Inches(6.0))
else:
    # Graceful fallback: ASCII C4 diagram (always works, no dependencies)
    pass
```

For DOCX documents, use `output_preset="docx_portrait"` or `"docx_landscape"`. See `/azure-diagrams` for full API.

**Fallback C4 diagrams** (ASCII format, if azure_diagrams module not available):

```
C4 Context: {app_name}
┌─────────────────────────────────────────────┐
│                   Users                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Data Team │  │ Business  │  │ External  │  │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  │
└────────┼─────────────┼─────────────┼────────┘
         │             │             │
         ▼             ▼             ▼
┌─────────────────────────────────────────────┐
│              {app_name} System               │
│  [Azure AI + Data Platform]                  │
└──────────────────┬──────────────────────────┘
                   │
         ┌─────────┼─────────┐
         ▼         ▼         ▼
    ┌─────────┐ ┌──────┐ ┌──────────┐
    │ Source   │ │ UBI  │ │ External │
    │ Systems  │ │ ADLS │ │ APIs     │
    └─────────┘ └──────┘ └──────────┘
```

#### Doc 2: Solution Design Document

9 sections populated from state:

1. **Overview** — archetype, scope, objectives
2. **Architecture Decisions** — from `PROJECT_MEMORY.md` decision log
3. **Component Design** — resource inventory table with names, types, SKUs
4. **Data Model** — Bronze/Silver/Gold schemas from pipeline config
5. **API Design** — endpoints from frontend config
6. **AI Configuration** — model deployments, vector store, retrieval strategy
7. **Security Design** — RBAC, Content Safety, auth from governance config
8. **Cost Estimate** — from Phase 0 pricing
9. **Deployment Plan** — environments, pipeline, rollback

#### Doc 3: Data Flow Diagram

```
DATA FLOW: {app_name}
═══════════════════════

{source_systems}
    │
    ▼ [ADF Copy / Databricks]
┌─────────────────────────────────────┐
│ BRONZE (flukebi_Bronze)              │  ← UBI Subscription
│ Raw/typed ingestion, metadata cols   │
└──────────────┬──────────────────────┘
               │
               ▼ [Databricks Silver]
┌─────────────────────────────────────┐
│ SILVER (flukebi_Silver)              │
│ {silver_transforms}                  │
└──────────────┬──────────────────────┘
               │
               ▼ [Databricks Gold]
┌─────────────────────────────────────┐
│ GOLD (flukebi_Gold)                  │
│ {gold_output}                        │
└──────────────┬──────────────────────┘
               │
               ▼ [Databricks AI Layer]
┌─────────────────────────────────────┐
│ AI LAYER                             │  ← AI Subscription
│ {ai_layer_processing}                │
└──────────────┬──────────────────────┘
               │
    ┌──────────┼──────────┐
    ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│AI Search│ │Cosmos  │ │ Graph  │
│ Index   │ │  DB    │ │ Store  │
└────┬───┘ └────┬───┘ └────┬───┘
     │          │          │
     ▼          ▼          ▼
┌─────────────────────────────────────┐
│ FRONTEND: {frontend_type}            │
│ {features}                           │
└─────────────────────────────────────┘
```

#### Doc 4: API Specification (OpenAPI 3.1 YAML)

Generate a complete, validated OpenAPI 3.1 specification from frontend configuration. This is NOT a placeholder — it must be a fully functional spec that can be imported into Azure API Management or used with Swagger UI.

```yaml
# Template: openapi-spec.yaml (Jinja2)
openapi: "3.1.0"
info:
  title: "{{ app_name }} API"
  version: "1.0.0"
  description: "AI-powered API for {{ archetype }} use case"
  contact:
    name: "Fluke AI Team"
    email: "ai-team@<ORG_DOMAIN>"
servers:
  - url: "https://flk-{{ app_slug }}-func-{{ env }}.azurewebsites.net/api"
    description: "{{ env | upper }} environment"
paths:
  /chat:
    post:
      operationId: chatCompletion
      summary: "AI chat completion with retrieval"
      security:
        - {{ 'entraId: []' if requirements.frontend.auth_method == 'entra-id' else 'apiKey: []' }}
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required: [messages]
              properties:
                messages:
                  type: array
                  items:
                    type: object
                    required: [role, content]
                    properties:
                      role: { type: string, enum: [system, user, assistant] }
                      content: { type: string, maxLength: 4096 }
                  minItems: 1
                  maxItems: 50
                stream: { type: boolean, default: false }
                top_k: { type: integer, default: 5, minimum: 1, maximum: 20 }
      responses:
        "200":
          description: "Successful response"
          content:
            application/json:
              schema:
                type: object
                properties:
                  response: { type: string }
                  sources:
                    type: array
                    items:
                      type: object
                      properties:
                        title: { type: string }
                        source: { type: string }
                        score: { type: number }
                  usage:
                    type: object
                    properties:
                      prompt_tokens: { type: integer }
                      completion_tokens: { type: integer }
        "400": { description: "Invalid request (empty messages, too long)" }
        "401": { description: "Authentication required" }
        "429": { description: "Rate limit exceeded", headers: { Retry-After: { schema: { type: integer } } } }
        "500": { description: "Internal server error" }
  /search:
    get:
      operationId: hybridSearch
      summary: "Hybrid search over indexed documents"
      parameters:
        - name: q
          in: query
          required: true
          schema: { type: string, minLength: 1, maxLength: 1000 }
        - name: top
          in: query
          schema: { type: integer, default: 10, minimum: 1, maximum: 50 }
        - name: filter
          in: query
          schema: { type: string }
          description: "OData filter expression"
      responses:
        "200":
          description: "Search results"
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
                    type: array
                    items:
                      type: object
                      properties:
                        content: { type: string }
                        source: { type: string }
                        score: { type: number }
                  count: { type: integer }
  /health:
    get:
      operationId: healthCheck
      summary: "Service health check"
      security: []
      responses:
        "200":
          description: "Service healthy"
          content:
            application/json:
              schema:
                type: object
                required: [status, timestamp]
                properties:
                  status: { type: string, enum: [healthy, degraded, unhealthy] }
                  timestamp: { type: string, format: date-time }
                  dependencies:
                    type: object
                    additionalProperties:
                      type: object
                      properties:
                        status: { type: string }
                        latency_ms: { type: number }
  /upload:
    post:
      operationId: uploadDocument
      summary: "Upload document for processing"
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                file:
                  type: string
                  format: binary
                metadata:
                  type: string
                  description: "JSON metadata for the document"
      responses:
        "202": { description: "Accepted — processing started" }
        "413": { description: "File too large (max 50MB)" }
components:
  securitySchemes:
    entraId:
      type: oauth2
      flows:
        implicit:
          authorizationUrl: "https://login.microsoftonline.com/{{ requirements.get('tenant_id', '0f634ac3-b39f-41a6-83ba-8f107876c692') }}/oauth2/v2.0/authorize"
          scopes:
            "api://flk-{{ app_slug }}-{{ env }}/.default": "Default access"
    apiKey:
      type: apiKey
      in: header
      name: x-functions-key
```

**Validation after generation:**
```bash
# Validate the generated OpenAPI spec
pip install openapi-spec-validator
python -c "
from openapi_spec_validator import validate
import yaml
with open('docs/openapi.yaml') as f:
    spec = yaml.safe_load(f)
validate(spec)
print('OpenAPI spec valid')
"
```

**Archetype-specific endpoints** — extend the base spec:

| Archetype | Additional Endpoints |
|-----------|---------------------|
| Doc Intelligence | `POST /extract` (submit document), `GET /extract/{id}` (get results) |
| Predictive ML | `POST /predict` (single), `POST /predict/batch` (batch) |
| Knowledge Graph | `POST /graph/query` (Cypher/Gremlin), `GET /graph/neighbors/{id}` |
| Voice/Text | `POST /transcribe` (audio upload), `GET /transcripts/{id}` |
| Computer Vision | `POST /analyze` (image), `POST /classify` (classification) |

#### Doc 5: Developer Guide

12 sections populated from state:

1. **Prerequisites** — Required tools (Python 3.11+, Azure CLI, Databricks CLI, Node.js if React), SDK versions
2. **Repository Structure** — Generated tree from Phase 7 repo layout
3. **Environment Setup** — `.env.template` variables, Key Vault references, local development secrets
4. **Azure Authentication** — `az login`, service principal setup, Managed Identity for CI/CD
5. **Databricks Development** — Notebook import, cluster configuration, widget parameters, `%run` dependencies
6. **ADF Configuration** — Linked services, pipeline parameters, trigger setup, status_control integration
7. **AI Services Development** — Model deployment verification, embedding generation, vector store queries
8. **Frontend Development** — Local dev server, environment variables, hot reload, debug mode
9. **Testing** — Running Phase 5 tests locally, DeepEval/RAGAS setup, red-team scans
10. **Deployment** — CI/CD pipeline triggers, environment promotion, Bicep what-if
11. **Azure DevOps Branching** — Feature branch workflow, PR policies, code review checklist
12. **Troubleshooting** — Common errors table (HTTP codes, Azure errors, resolution steps)

#### Doc 6: End User Guide

7 sections populated from state:

1. **Application Overview** — What it does, who it's for, key capabilities
2. **Getting Started** — Login process (Entra ID flow), first-time setup, navigation
3. **Features** — One section per `requirements.frontend.features[]` with screenshots placeholders and step-by-step instructions
4. **Tips & Best Practices** — How to write effective queries, understanding source citations, confidence scores
5. **FAQ** — 10 common questions generated from archetype (e.g., "Why does the AI sometimes not find my document?")
6. **Troubleshooting** — Common user errors with resolution steps
7. **Feedback & Support** — How to report issues, provide feedback, request features

#### Doc 7: Operations Runbook

10 sections with production-grade content:

1. **Service Architecture** — Component diagram, dependency map, data flow
2. **Health Checks** — Endpoint URLs, expected responses, check frequency
3. **Monitoring Dashboard** — Log Analytics workspace, App Insights, key metrics
4. **KQL Queries** — Production-ready queries from `governance.md`:
   ```kql
   // Error rate by endpoint (last 24h)
   AppRequests
   | where TimeGenerated > ago(24h)
   | where AppRoleName == "flk-{{ app_slug }}-app-{{ env }}"
   | summarize total=count(), errors=countif(ResultCode >= 500) by bin(TimeGenerated, 1h)
   | extend error_rate = round(100.0 * errors / total, 2)
   | order by TimeGenerated desc

   // AI token usage tracking
   AppDependencies
   | where DependencyType == "HTTP" and Target contains "openai"
   | extend tokens = toint(Properties["usage_total_tokens"])
   | summarize total_tokens=sum(tokens), avg_latency=avg(DurationMs) by bin(TimeGenerated, 1h)

   // Content Safety blocks (security monitoring)
   AppTraces
   | where Message contains "content_safety_blocked"
   | summarize blocks=count() by bin(TimeGenerated, 1h), tostring(Properties["category"])
   ```
5. **Alerting Rules** — Azure Monitor alert definitions (error rate >5%, latency P95 >3s, token budget >80%)
6. **Incident Response Playbook** — Severity matrix (P1-P4) with escalation paths:
   | Severity | Definition | Response Time | Escalation |
   |----------|-----------|---------------|------------|
   | P1 | Service down, all users affected | 15 min | On-call → Manager → VP |
   | P2 | Major feature degraded | 1 hour | On-call → Team Lead |
   | P3 | Minor feature issue, workaround exists | 4 hours | Ticket queue |
   | P4 | Cosmetic, enhancement request | Next sprint | Backlog |
7. **Scaling Guide** — When to scale (metrics thresholds), how to scale (App Service, AI Search replicas, Cosmos RU/s), cost impact
8. **Backup & Recovery** — Cosmos DB point-in-time restore, ADLS Delta time travel, AI Search index rebuild
9. **Secret Rotation** — Key Vault rotation schedule, zero-downtime rotation procedure
10. **Cost Monitoring** — Azure Cost Management queries, budget alerts, optimization recommendations

#### Doc 8: Source-to-Target Mapping (UBI STM Format)

45-column STM with 7 stages. Populated from pipeline notebook schemas. Generated as XLSX with formatted headers using openpyxl.

```python
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

def generate_stm_xlsx(state: dict, output_path: str):
    """Generate a formatted 45-column STM Excel file from state."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Source-to-Target Map"

    # 45-column header (7 stages × ~6 columns + metadata)
    headers = [
        # Source (6)
        "SourceSystem", "SourceSchema", "SourceTable", "SourceColumn", "SourceDataType", "SourceDescription",
        # Landing/Bronze (7)
        "LandingDB", "LandingTable", "LandingColumn", "LandingDataType", "LandingTransformation", "LandingNullable", "LandingPK",
        # Bronze (6)
        "BronzeDB", "BronzeTable", "BronzeColumn", "BronzeDataType", "BronzeTransformation", "BronzeNotes",
        # Silver (7)
        "SilverDB", "SilverTable", "SilverColumn", "SilverDataType", "SilverTransformation", "SilverJoinSource", "SilverNotes",
        # Gold (6)
        "GoldDB", "GoldTable", "GoldColumn", "GoldDataType", "GoldTransformation", "GoldNotes",
        # Gold ADLS (5)
        "GoldADLS_Path", "GoldADLS_Column", "GoldADLS_DataType", "GoldADLS_Format", "GoldADLS_Partition",
        # PBI (5) + Metadata (3)
        "PBI_Dataset", "PBI_Table", "PBI_Column", "PBI_Measure", "PBI_Notes",
        "StreamName", "LoadType", "LastUpdated",
    ]

    # Style header row
    header_fill = PatternFill(start_color="003366", end_color="003366", fill_type="solid")
    header_font = Font(name="Calibri", size=9, bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
        cell.border = thin_border

    # Populate rows from pipeline config
    pipeline_req = state.get("requirements", {}).get("pipeline", {})
    for source in pipeline_req.get("source_systems", []):
        # Each source system generates rows based on its schema
        # Row population logic reads from artifacts.pipeline_schemas
        pass

    # Auto-fit column widths
    for col in ws.columns:
        max_length = max(len(str(cell.value or "")) for cell in col)
        ws.column_dimensions[col[0].column_letter].width = min(max_length + 2, 25)

    # Freeze header row + add autofilter
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{chr(64 + len(headers))}1"

    wb.save(output_path)
    return output_path
```

#### Doc 9: Model Card (Responsible AI Documentation)

Model Cards follow the format from Google's Model Cards for Model Reporting (Mitchell et al., 2019), adapted for Azure AI deployments. **Required for all archetypes that deploy AI models.**

```markdown
# Model Card: {{ app_name }}

## Model Details
- **Model name:** {{ requirements.ai.primary_model.model_id }}
- **Model version:** {{ requirements.ai.primary_model.version }}
- **Deployment name:** {{ requirements.ai.primary_model.deployment_name }}
- **Provider:** Azure OpenAI Service
- **Type:** {{ archetype }} ({{ "generative" if archetype in ["rag", "conversational", "multi-agent"] else "extraction" if archetype == "doc-intelligence" else "predictive" }})
- **Date deployed:** {{ timestamp }}
- **License:** Azure OpenAI Terms of Service

## Intended Use
- **Primary use case:** {{ state.get("project_name") }} — {{ archetype }} solution
- **Intended users:** {{ requirements.frontend.audience }}
- **Out-of-scope uses:** Not intended for medical diagnosis, legal advice, financial trading decisions, or autonomous safety-critical systems

## Training Data
{% if archetype in ["predictive-ml", "computer-vision"] %}
- **Training dataset:** {{ artifacts.get("training_dataset", "See Gold layer tables") }}
- **Dataset size:** {{ artifacts.get("training_size", "N/A") }}
- **Feature count:** {{ artifacts.get("feature_count", "N/A") }}
- **Label distribution:** {{ artifacts.get("label_distribution", "See test report") }}
{% else %}
- **Base model:** Pre-trained by model provider (Azure OpenAI)
- **Fine-tuning:** None (prompt-engineered with retrieval augmentation)
- **Knowledge corpus:** {{ requirements.pipeline.get("source_systems", []) | length }} source systems
{% endif %}

## Evaluation Results
- **Test date:** {{ test_report.get("date", timestamp) }}
- **Test environment:** {{ env }}
{% if test_report.get("ai_quality") %}
- **Retrieval relevance:** {{ test_report.ai_quality.get("retrieval_score", "N/A") }}
- **Groundedness:** {{ test_report.ai_quality.get("groundedness_score", "N/A") }}
- **Response quality:** {{ test_report.ai_quality.get("response_quality", "N/A") }}
{% endif %}
{% if test_report.get("eval_framework") %}
- **DeepEval metrics:** {{ test_report.eval_framework.get("deepeval_summary", "N/A") }}
- **RAGAS metrics:** {{ test_report.eval_framework.get("ragas_summary", "N/A") }}
- **Red-team results:** {{ test_report.eval_framework.get("garak_summary", "N/A") }}
{% endif %}

## Ethical Considerations
- **Content Safety:** {{ requirements.ai.content_safety.mode }} mode with Prompt Shields{{ ", PII redaction" if requirements.ai.content_safety.get("pii_redaction") else "" }}
- **Bias risks:** Model may reflect biases present in training data. Outputs should not be used as sole basis for decisions affecting individuals.
- **Hallucination risk:** {{ "Mitigated by retrieval grounding" if archetype in ["rag", "conversational"] else "Monitor with evaluation framework" }}
- **Data privacy:** {{ "PII redaction enabled" if requirements.ai.content_safety.get("pii_redaction") else "No PII handling configured — verify data does not contain PII" }}

## Limitations
- Maximum context window: model-dependent (check Azure OpenAI documentation)
- Response latency: P95 target < 3 seconds (actual: see test report)
- Not suitable for: real-time safety-critical decisions, legal/medical advice without human review
- Knowledge cutoff: Limited to indexed corpus; does not have access to real-time data unless configured

## Caveats and Recommendations
- Always verify AI outputs for critical business decisions
- Monitor Content Safety metrics weekly
- Re-evaluate model performance quarterly with updated test data
- Rotate API keys per Key Vault rotation schedule
```

#### Doc 10: Architecture Decision Records (ADRs)

Generate ADRs from `PROJECT_MEMORY.md` decision log entries. Each decision becomes a structured ADR following the Nygard format (Michael Nygard, "Documenting Architecture Decisions").

```markdown
# ADR-001: {{ decision.title }}

## Status
{{ decision.status | default("Accepted") }}

## Context
{{ decision.context }}
<!-- Populated from PROJECT_MEMORY.md decision entry + archetype rationale -->

## Decision
{{ decision.description }}

## Consequences
### Positive
{{ decision.benefits }}

### Negative / Risks
{{ decision.risks }}

### Trade-offs
{{ decision.tradeoffs }}

## Alternatives Considered
{% for alt in decision.alternatives %}
- **{{ alt.name }}:** {{ alt.reason_rejected }}
{% endfor %}
```

**Auto-generated ADRs** from common decisions captured in Phase 0:

| ADR | Decision | Typical Context |
|-----|----------|----------------|
| ADR-001 | Archetype selection | Why this archetype over alternatives |
| ADR-002 | Subscription model | Split vs single, cost vs complexity |
| ADR-003 | Vector store choice | AI Search vs Cosmos DB vs none |
| ADR-004 | Graph database choice | Cosmos Gremlin vs Neo4j (if KG archetype) |
| ADR-005 | Frontend technology | Streamlit vs React vs Copilot Studio |
| ADR-006 | Authentication method | Entra ID vs API key vs anonymous |
| ADR-007 | Content Safety mode | Block vs monitor, PII redaction scope |
| ADR-008 | Multi-region strategy | Active-passive vs active-active, cost impact |

### Step 3: DOCX Conversion (Production-Grade)

Use the `/docx-beautify` skill module for professional document generation. If unavailable, use the inline converter below.

```python
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

# Try to use docx_beautify module (preferred — full formatting support)
try:
    import importlib, sys
    candidates = [
        Path.home() / "OneDrive - <ORG>" / "Claude code" / "Document Beautification",
    ]
    for p in candidates:
        if (p / "docx_beautify.py").exists():
            sys.path.insert(0, str(p))
            break
    from docx_beautify import md_to_docx as _md_to_docx, create_document
    HAS_BEAUTIFY = True
except ImportError:
    HAS_BEAUTIFY = False

def generate_docx(md_content: str, output_path: str, title: str, ctx: dict):
    """Convert Markdown to professional DOCX with full formatting."""
    if HAS_BEAUTIFY:
        _md_to_docx(
            md_content, output_path,
            preset="technical",
            title=title,
            author="AI Use Case Builder",
            cover_page=True,
            header_footer=True,
        )
        return output_path

    # Inline fallback converter (handles headings, tables, code blocks, lists)
    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(2.5)
        section.right_margin = Cm(2.5)

    # Style configuration
    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    style.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    style.paragraph_format.space_after = Pt(8)
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    style.paragraph_format.line_spacing = 1.15

    for level, size in [(1, 24), (2, 18), (3, 14), (4, 12)]:
        h = doc.styles[f"Heading {level}"]
        h.font.name = "Calibri"
        h.font.size = Pt(size)
        h.font.bold = True
        h.font.color.rgb = RGBColor(0x00, 0x33, 0x66)

    # Cover page
    doc.add_paragraph("")  # spacer
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x33, 0x66)
    doc.add_paragraph(f"\nProject: {ctx['app_name']}\nArchetype: {ctx['archetype']}\nGenerated: {ctx['timestamp']}\n",
                      style="Normal").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    # Parse markdown into blocks
    lines = md_content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]

        # Headings
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            text = line.lstrip("# ").strip()
            if level <= 4:
                doc.add_heading(text, level=level)
            i += 1
            continue

        # Code blocks
        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing ```
            p = doc.add_paragraph()
            # Add gray background via OXML
            pPr = p._element.get_or_add_pPr()
            shd = pPr.makeelement(qn("w:shd"), {
                qn("w:val"): "clear", qn("w:color"): "auto", qn("w:fill"): "F5F5F5"
            })
            pPr.append(shd)
            run = p.add_run("\n".join(code_lines))
            run.font.name = "Consolas"
            run.font.size = Pt(9)
            continue

        # Tables (pipe-delimited)
        if "|" in line and line.strip().startswith("|"):
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                if not re.match(r"^\s*\|[\s\-:|]+\|\s*$", lines[i]):  # skip separator
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    table_lines.append(cells)
                i += 1
            if table_lines:
                tbl = doc.add_table(rows=len(table_lines), cols=len(table_lines[0]))
                tbl.style = "Table Grid"
                tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
                for ri, row in enumerate(table_lines):
                    for ci, val in enumerate(row):
                        if ci < len(tbl.columns):
                            cell = tbl.rows[ri].cells[ci]
                            cell.text = val
                            for paragraph in cell.paragraphs:
                                for run in paragraph.runs:
                                    run.font.size = Pt(9)
                                    run.font.name = "Calibri"
                            if ri == 0:  # header row
                                tc_pr = cell._element.get_or_add_tcPr()
                                shd = tc_pr.makeelement(qn("w:shd"), {
                                    qn("w:val"): "clear", qn("w:color"): "auto", qn("w:fill"): "003366"
                                })
                                tc_pr.append(shd)
                                for paragraph in cell.paragraphs:
                                    for run in paragraph.runs:
                                        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                                        run.font.bold = True
            continue

        # Bullet lists
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            text = line.strip().lstrip("-* ").strip()
            p = doc.add_paragraph(text, style="List Bullet")
            # Handle inline formatting
            i += 1
            continue

        # Regular paragraph
        if line.strip():
            p = doc.add_paragraph()
            # Parse inline formatting: **bold**, *italic*, `code`
            parts = re.split(r'(\*\*.*?\*\*|`.*?`|\*.*?\*)', line)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    run = p.add_run(part[2:-2])
                    run.bold = True
                elif part.startswith("`") and part.endswith("`"):
                    run = p.add_run(part[1:-1])
                    run.font.name = "Consolas"
                    run.font.size = Pt(9)
                elif part.startswith("*") and part.endswith("*"):
                    run = p.add_run(part[1:-1])
                    run.italic = True
                else:
                    p.add_run(part)

        i += 1

    doc.save(output_path)
    return output_path
```

### Step 4: Generate Document Index

```markdown
# {{ app_name }} — Documentation Index

Generated: {{ timestamp }} | Archetype: {{ archetype }} | Environment: {{ env }}

| # | Document | Format | Description | Validation |
|---|----------|--------|-------------|------------|
| 1 | Enterprise Architecture | [MD](ea-document.md) / [DOCX](ea-document.docx) | TOGAF ADM + C4 diagrams | Sections: 6 |
| 2 | Solution Design | [MD](solution-design.md) / [DOCX](solution-design.docx) | Architecture decisions + component design | Sections: 9 |
| 3 | Data Flow | [MD](data-flow.md) / [DOCX](data-flow.docx) | Medallion pipeline visualization | Layers: 7 |
| 4 | API Specification | [YAML](openapi.yaml) / [MD](api-spec.md) | OpenAPI 3.1 (validated) | Endpoints: N |
| 5 | Developer Guide | [MD](developer-guide.md) / [DOCX](developer-guide.docx) | Setup + development workflow | Sections: 12 |
| 6 | End User Guide | [MD](user-guide.md) / [DOCX](user-guide.docx) | Application usage + FAQ | Sections: 7 |
| 7 | Operations Runbook | [MD](operations-runbook.md) / [DOCX](operations-runbook.docx) | Monitoring + incident response | KQL queries: N |
| 8 | Source-to-Target Map | [XLSX](stm.xlsx) | UBI 45-column STM | Rows: N, Cols: 45 |
| 9 | Model Card | [MD](model-card.md) / [DOCX](model-card.docx) | Responsible AI documentation | Required sections: 8 |
| 10 | Architecture Decisions | [MD](adrs/) / [DOCX](adrs.docx) | ADRs from decision log | Records: N |
```

### Step 5: Validate All Documents

Run post-generation validation before presenting the report:

```python
def validate_docs(docs_dir: Path, ctx: dict) -> dict:
    """Validate all generated documents for completeness and correctness."""
    results = {"passed": 0, "failed": 0, "warnings": 0, "details": []}

    # 1. Check all expected files exist
    expected_files = [
        "ea-document.md", "ea-document.docx",
        "solution-design.md", "solution-design.docx",
        "data-flow.md", "data-flow.docx",
        "openapi.yaml", "api-spec.md",
        "developer-guide.md", "developer-guide.docx",
        "user-guide.md", "user-guide.docx",
        "operations-runbook.md", "operations-runbook.docx",
        "stm.xlsx",
        "model-card.md", "model-card.docx",
    ]
    for f in expected_files:
        path = docs_dir / f
        if path.exists() and path.stat().st_size > 0:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["details"].append(f"MISSING: {f}")

    # 2. Validate OpenAPI spec
    try:
        import yaml
        from openapi_spec_validator import validate
        with open(docs_dir / "openapi.yaml") as f:
            spec = yaml.safe_load(f)
        validate(spec)
        results["passed"] += 1
    except ImportError:
        results["warnings"] += 1
        results["details"].append("WARNING: openapi-spec-validator not installed, spec not validated")
    except Exception as e:
        results["failed"] += 1
        results["details"].append(f"FAIL: OpenAPI spec invalid: {e}")

    # 3. Validate Markdown files have no unresolved templates
    for md_file in docs_dir.glob("*.md"):
        content = md_file.read_text()
        issues = validate_rendered(content, md_file.name)
        if issues:
            results["warnings"] += len(issues)
            results["details"].extend(issues)
        else:
            results["passed"] += 1

    # 4. Validate STM has correct column count
    try:
        import openpyxl
        wb = openpyxl.load_workbook(docs_dir / "stm.xlsx", read_only=True)
        ws = wb.active
        col_count = ws.max_column
        if col_count == 45:
            results["passed"] += 1
        else:
            results["failed"] += 1
            results["details"].append(f"FAIL: STM has {col_count} columns (expected 45)")
        wb.close()
    except Exception as e:
        results["failed"] += 1
        results["details"].append(f"FAIL: STM validation error: {e}")

    # 5. Validate DOCX files have proper heading hierarchy
    try:
        for docx_file in docs_dir.glob("*.docx"):
            doc = Document(str(docx_file))
            headings = [p for p in doc.paragraphs if p.style.name.startswith("Heading")]
            if not headings:
                results["warnings"] += 1
                results["details"].append(f"WARNING: {docx_file.name} has no headings")
            else:
                results["passed"] += 1
    except Exception as e:
        results["warnings"] += 1
        results["details"].append(f"WARNING: DOCX heading check error: {e}")

    return results
```

### Step 6: Present Report and Gate

```
DOCUMENTATION REPORT — {project_name}
═══════════════════════════════════════

Documents Generated: 10
Formats: MD + DOCX (YAML for API, XLSX for STM)

| # | Document | Est. Pages | Sections | Status | Validation |
|---|----------|-----------|----------|--------|------------|
| 1 | Enterprise Architecture | ~15 | 6 TOGAF phases + C4 | Complete | PASS |
| 2 | Solution Design | ~20 | 9 sections | Complete | PASS |
| 3 | Data Flow | ~5 | 1 diagram + legend | Complete | PASS |
| 4 | API Specification | ~8 | {endpoint_count} endpoints | Complete | PASS (OpenAPI validated) |
| 5 | Developer Guide | ~12 | 12 sections | Complete | PASS |
| 6 | End User Guide | ~8 | 7 sections | Complete | PASS |
| 7 | Operations Runbook | ~15 | 10 sections + playbook | Complete | PASS |
| 8 | Source-to-Target Map | ~{row_count} rows | 7 stages × 45 cols | Complete | PASS ({col_count} cols) |
| 9 | Model Card | ~4 | 8 sections | Complete | PASS |
| 10 | Architecture Decisions | ~{adr_count * 2} | {adr_count} ADRs | Complete | PASS |

Validation Summary: {passed} passed, {failed} failed, {warnings} warnings
{validation_details if any failures}

Output Directory: {project_dir}/docs/
```

Update state: `phases.docs = "completed"`, `artifacts.documents`

Ask:
> **GATE: Phase 6 Documentation complete.** 10 documents generated in dual format. Validation: {passed}/{total} checks passed. Shall I proceed to Phase 7 (Deployment)?

---

## Documentation Anti-Patterns (NEVER Do These)

1. **NEVER generate documents with placeholder values still present.** Every `{{ variable }}` must resolve from state. Run `validate_rendered()` on every output — if ANY placeholder remains, the document is REJECTED. Fix the state contract, don't ship broken docs.
2. **NEVER include secrets, keys, or connection strings in any document.** Use `{from-key-vault}` notation. This includes screenshots that might show secrets in URL bars or config panels.
3. **NEVER generate the STM without all 7 stages and 45 columns.** Even if a stage is passthrough (e.g., Landing = Bronze), document it. The 45-column format is required for UBI governance audits. Validate column count programmatically.
4. **NEVER skip the Operations Runbook.** It's the most critical document for handoff. Without it, the team can't maintain the solution after deployment.
5. **NEVER generate C4 diagrams that don't match actual resource names.** Diagram labels must use the real Azure resource names from state, not generic placeholders.
6. **NEVER produce DOCX files without proper heading hierarchy.** Screen readers and TOC generation depend on correct Heading 1/2/3 structure. Validate heading presence in every DOCX.
7. **NEVER generate API docs that contradict the actual implementation.** The OpenAPI spec must be machine-validated (`openapi-spec-validator`). If validation fails, fix the spec before saving.
8. **NEVER skip the Model Card for projects deploying AI models.** Responsible AI documentation is mandatory. The bias/limitations section must be populated — not left as TODO.
9. **NEVER hardcode file paths in document generation code.** Use `Path.home()` or relative paths. Hardcoded user paths break for other team members.
10. **NEVER generate ADRs without the Alternatives Considered section.** Every architectural decision must document what was NOT chosen and why. This is the most valuable part of an ADR.

## Error Recovery

| Error | Recovery |
|-------|---------|
| `python-docx` not installed | `pip install python-docx openpyxl jinja2 pyyaml` |
| Jinja2 `UndefinedError` | Missing field in state.json — check error message for field name, update state |
| STM column count != 45 | Verify header list matches 45-column spec, check for merged/missing columns |
| OpenAPI validation fails | Check YAML syntax, verify schema `$ref` paths, validate required fields |
| DOCX file corrupted | Regenerate from MD source, verify python-docx >= 1.1.0 |
| `docx_beautify` import fails | Graceful fallback to inline converter — no action needed, quality acceptable |
| PROJECT_MEMORY.md has no decisions | Generate ADRs from state.json phase config (archetype choice, subscription model, etc.) |
| Model Card missing test results | Read test report from `artifacts.test_report`, flag missing metrics as "N/A — not evaluated" |
| Large document (>100 pages) | Split into volume 1/volume 2, add cross-reference index |
| Diagram generation fails | Fall back to ASCII C4 diagrams (always available), log warning |
