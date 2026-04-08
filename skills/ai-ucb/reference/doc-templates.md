---
name: ai-ucb:doc-templates
description: AI Use Case Builder - Document Templates. Contains templates for all 8 enterprise documents (EA, Solution Design, Data Flow, API Spec, Developer Guide, User Guide, Runbook, STM). Referenced by ai-ucb-docs.md (Phase 6).
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# AI Use Case Builder - Document Templates

All document templates consumed by Phase 6. Each template uses `{placeholder}` syntax populated from `ai-ucb-state.json`.

---

## 1. Enterprise Architecture Document Template

```markdown
# Enterprise Architecture Document: {app_name}

**Version:** 1.0
**Date:** {date}
**Archetype:** {archetype}
**Author:** {owner} + Claude Opus 4.6

---

## 1. Architecture Vision (TOGAF Phase A)

### 1.1 Business Objective
{business_objective_from_memory}

### 1.2 Stakeholders
| Stakeholder | Role | Concern |
|------------|------|---------|
| {stakeholder_1} | {role} | {concern} |

### 1.3 Scope
- **In Scope:** {in_scope}
- **Out of Scope:** {out_of_scope}
- **Archetype:** {archetype} — {archetype_description}

---

## 2. Business Architecture (TOGAF Phase B)

### 2.1 Business Process
{process_description}

### 2.2 Use Case Flow
1. User submits {input_type}
2. System {processing_description}
3. User receives {output_type}

---

## 3. Information Architecture (TOGAF Phase C)

### 3.1 Data Sources
| Source | Type | Extraction | Volume |
|--------|------|-----------|--------|
{source_table_from_state}

### 3.2 Data Model (Medallion Architecture)
| Layer | Database | Tables | Key Transforms |
|-------|----------|--------|----------------|
| Bronze | flukebi_Bronze | {bronze_tables} | {bronze_strategy} |
| Silver | flukebi_Silver | {silver_tables} | {silver_transforms} |
| Gold | flukebi_Gold | {gold_tables} | {gold_output} |
| AI Layer | {ai_store} | {ai_tables} | {ai_processing} |

### 3.3 AI Index Schema
| Field | Type | Searchable | Vector |
|-------|------|-----------|--------|
{index_fields_from_state}

---

## 4. Technology Architecture (TOGAF Phase D)

### 4.1 C4 Context Diagram
{c4_context_ascii}

### 4.2 C4 Container Diagram
{c4_container_ascii}

### 4.3 Resource Inventory
| Resource | Type | SKU | Region | Subscription |
|----------|------|-----|--------|-------------|
{resource_inventory_from_state}

### 4.4 Network Topology
{network_diagram_or_description}

---

## 5. Opportunities & Solutions (TOGAF Phase E)

### 5.1 Cost Optimization
{cost_estimate_from_phase_0}

### 5.2 Scaling Path
| Trigger | Action | Cost Impact |
|---------|--------|------------|
| >1000 daily users | Upgrade App Service to P1v3 | +$74/mo |
| >100GB index | Upgrade AI Search to S2 | +$500/mo |
| >50 RU/s sustained | Switch Cosmos to provisioned | Variable |

---

## 6. Migration Planning (TOGAF Phase F)

### 6.1 Deployment Pipeline
{devops_pipeline_description}

### 6.2 Environment Promotion
Dev → QA → Production (manual gate at each stage)

### 6.3 Rollback Strategy
{rollback_description}
```

---

## 2. Solution Design Document Template

```markdown
# Solution Design: {app_name}

## 1. Overview
- **Use Case:** {use_case_description}
- **Archetype:** {archetype}
- **Primary Model:** {primary_model} ({deployment_name})
- **Target Audience:** {audience}

## 2. Architecture Decisions
{decisions_from_project_memory}

| # | Decision | Options Considered | Choice | Rationale |
|---|----------|-------------------|--------|-----------|
{decision_table}

## 3. Component Design
{resource_inventory_table}

## 4. Data Model
### 4.1 Bronze Schema
{bronze_schema_table}

### 4.2 Silver Schema
{silver_schema_table}

### 4.3 Gold Schema
{gold_schema_table}

### 4.4 AI Layer Schema
{ai_schema_table}

## 5. API Design
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
{api_endpoints_table}

## 6. AI Configuration
- **Primary Model:** {model} on {deployment}
- **Embedding Model:** {embedding_model} ({dimensions}D)
- **Vector Store:** {vector_store_type} ({index_name})
- **Retrieval Strategy:** {retrieval_strategy}
- **Chunking:** {chunk_size} tokens, {overlap} overlap, {method} method

## 7. Security Design
- **Authentication:** {auth_method}
- **Authorization:** {rbac_summary}
- **Content Safety:** {safety_mode} mode
- **PII Protection:** {pii_config}
- **Audit Logging:** {logging_config}

## 8. Cost Estimate
{cost_table_from_phase_0}

## 9. Deployment Plan
{deployment_config}
```

---

## 3. Data Flow Diagram Template

```
{app_name} — Data Flow Diagram
══════════════════════════════

SUBSCRIPTION: {ubi_subscription_name}
─────────────────────────────────────

  {source_1} ──┐
  {source_2} ──┤
  {source_3} ──┘
               │
               ▼
  ┌──── ADF: PL_{app}_Master ────┐
  │  Copy Activities / Databricks │
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──── BRONZE ──────────────────┐
  │ flukebi_Bronze.{table}       │
  │ Strategy: {bronze_strategy}  │
  │ Format: Delta                │
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──── SILVER ──────────────────┐
  │ flukebi_Silver.{table}       │
  │ Transforms: {transforms}     │
  │ Format: Delta                │
  └──────────────┬───────────────┘
                 │
                 ▼
  ┌──── GOLD ────────────────────┐
  │ flukebi_Gold.{views}         │
  │ Output: {gold_output}        │
  │ Format: Delta Views          │
  └──────────────┬───────────────┘

SUBSCRIPTION: {ai_subscription_name}
─────────────────────────────────────

                 │
                 ▼
  ┌──── AI LAYER ────────────────┐
  │ Processing: {ai_processing}  │
  │ Embeddings: {embedding_model}│
  │ Dimensions: {dimensions}     │
  └──────────────┬───────────────┘
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
  ┌─────────┐        ┌─────────┐
  │AI Search│        │Cosmos DB│
  │{index}  │        │{db}     │
  └────┬────┘        └────┬────┘
       │                   │
       └─────────┬─────────┘
                 │
                 ▼
  ┌──── FRONTEND ────────────────┐
  │ Type: {frontend_type}        │
  │ URL: {app_url}               │
  │ Auth: {auth_method}          │
  │ Safety: {safety_mode}        │
  └──────────────────────────────┘
```

---

## 4. Developer Guide Template

```markdown
# Developer Guide: {app_name}

## 1. Prerequisites
- Azure CLI >= 2.60
- Databricks CLI >= 0.18
- Python >= 3.10
- Node.js >= 20 (for React frontend)
- Azure DevOps access to `flukeit/Fluke Data And Analytics`

## 2. Repository Structure
```
{repo_name}/
├── notebooks/
│   ├── Bronze_{app}_{source}.py
│   ├── Silver_{app}.py
│   ├── Gold_{app}.py
│   ├── AILayer_{app}.py
│   └── Publish_AISearch_{app}.py
├── adf/
│   └── PL_{app}_Master.json
├── frontend/
│   ├── app.py (or Next.js project)
│   └── requirements.txt
├── infra/
│   ├── main.bicep
│   └── modules/
├── docs/
│   └── (this documentation)
└── tests/
    └── test_queries.json
```

## 3. Local Development Setup
```bash
# Clone repo
git clone https://dev.azure.com/flukeit/Fluke%20Data%20And%20Analytics/_git/{repo}
cd {repo}
git checkout -b Users/{username}/{feature}

# Install dependencies
pip install -r frontend/requirements.txt

# Set environment variables (from .env.template)
cp frontend/.env.template frontend/.env
# Edit .env with values from Key Vault
```

## 4. Databricks Development
- Workspace: {databricks_host}
- Notebooks: `/Shared/{app}/`
- Secret scope: `{app}` (backed by Key Vault)
- Widget parameters: `StreamName`, `SubStream`, `Database`

## 5. ADF Configuration
- Factory: `flk-{app}-adf-dev`
- Master pipeline: `PL_{app}_Master`
- Trigger: {trigger_type} ({schedule})

## 6. Debugging
| Issue | Debug Step |
|-------|-----------|
| Notebook fails | Check Databricks driver logs, verify widget params |
| ADF activity fails | Check ADF Monitor, verify linked service auth |
| AI Search returns 0 results | Check index doc count, verify embedding dimensions |
| Frontend 502 | Check App Service logs, verify startup command |
| Content Safety blocks safe input | Review filter thresholds in Content Safety Studio |

## 7. Azure DevOps Workflow
1. Create branch: `Users/{username}/{feature}`
2. Make changes, test locally
3. Push and create PR to `main`
4. Peer review + automated checks
5. Merge → triggers deployment pipeline
```

---

## 5. End User Guide Template

```markdown
# {app_name} — User Guide

## Welcome
{app_name} helps you {value_proposition}. Ask questions about your documents and get AI-powered answers with source citations.

## Getting Started
1. Navigate to {app_url}
2. Sign in with your Fluke email (Entra ID)
3. You'll see the {main_interface} interface

## Features

### Chat (if enabled)
Type your question in the chat box. The AI will search your documents and provide an answer with source citations.
- **Tips:** Be specific in your questions for better results
- **Sources:** Click "Sources" to see which documents were used

### Search (if enabled)
Enter keywords to search across all indexed documents. Results are ranked by relevance.

### Upload (if enabled)
Upload new documents to be indexed. Supported formats: PDF, DOCX, HTML.
Note: newly uploaded documents may take a few minutes to be indexed.

## FAQ
**Q: How accurate are the answers?**
A: The AI only answers based on your indexed documents. It will say "I don't have enough information" if the answer isn't in the documents.

**Q: Can I trust the sources shown?**
A: Yes — every source citation links to the actual document and section used.

**Q: What if I get an incorrect answer?**
A: Use the feedback button to report issues. This helps improve the system.

## Troubleshooting
| Issue | Solution |
|-------|---------|
| Can't sign in | Contact IT — verify Entra ID access |
| Slow responses | Check internet connection; peak hours may be slower |
| "No results" for known content | Content may not be indexed yet; contact admin |
| Error message | Refresh the page; if persistent, contact support |
```

---

## 6. Operations Runbook Template

```markdown
# Operations Runbook: {app_name}

## 1. Service Architecture
{c4_container_diagram}

| Component | Resource | Health URL | SLA |
|-----------|----------|-----------|-----|
| Frontend | flk-{app}-app-dev | /health | 99.9% |
| AI Services | flk-{app}-ai-dev | /openai/models | 99.9% |
| AI Search | flk-{app}-srch-dev | /indexes | 99.9% |
| Cosmos DB | flk-{app}-cosmos-dev | N/A (SDK) | 99.99% |
| Key Vault | flk-{app}-kv-dev | N/A (SDK) | 99.99% |
| ADF | flk-{app}-adf-dev | Pipeline Monitor | 99.9% |

## 2. Health Checks

```bash
# Run all health checks
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)

# Frontend
curl -s https://flk-{app}-app-dev.azurewebsites.net/health | jq .

# AI Services
curl -s -H "api-key: {key}" "https://flk-{app}-ai-dev.openai.azure.com/openai/models?api-version=2024-10-01" | jq '.data | length'

# AI Search doc count
curl -s -H "api-key: {key}" "https://flk-{app}-srch-dev.search.windows.net/indexes/{index}/docs/\$count?api-version=2024-07-01"
```

## 3. Monitoring (Log Analytics)

### Token Usage (last 24h)
```kql
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.COGNITIVESERVICES"
| where TimeGenerated > ago(24h)
| summarize TotalTokens=sum(toint(properties_s.total_tokens)) by bin(TimeGenerated, 1h)
| render timechart
```

### Error Rate
```kql
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.COGNITIVESERVICES"
| where resultSignature_d >= 400
| where TimeGenerated > ago(24h)
| summarize ErrorCount=count() by bin(TimeGenerated, 1h), resultSignature_d
| render timechart
```

### Content Safety Blocks
```kql
AzureDiagnostics
| where ResourceProvider == "MICROSOFT.COGNITIVESERVICES"
| where operationName_s contains "ContentSafety"
| where resultSignature_d == 400
| where TimeGenerated > ago(24h)
| summarize BlockCount=count() by bin(TimeGenerated, 1h)
```

## 4. Incident Response Playbook

### Severity Levels
| Severity | Criteria | Response Time | Escalation |
|----------|----------|--------------|------------|
| P1 | Service down, data loss | 15 min | Team lead + manager |
| P2 | Degraded service, safety bypass | 1 hour | Team lead |
| P3 | Non-critical error, slow performance | 4 hours | On-call engineer |
| P4 | Cosmetic issue, feature request | Next sprint | Backlog |

### P1 Runbook: Service Down
1. Check App Service status: `az webapp show --name flk-{app}-app-dev`
2. Check App Service logs: `az webapp log tail --name flk-{app}-app-dev`
3. Restart App Service: `az webapp restart --name flk-{app}-app-dev`
4. If persistent: check AI Services health, Key Vault access
5. Escalate if not resolved in 30 minutes

### P2 Runbook: Content Safety Bypass
1. Check Content Safety resource: verify Prompt Shields enabled
2. Review blocked/unblocked logs in Content Safety Studio
3. If safety is disabled: RE-ENABLE IMMEDIATELY
4. Review recent code deployments for safety configuration changes
5. Document incident and add regression test

## 5. Scaling Guide
| Trigger | Current | Scale To | Cost Impact |
|---------|---------|----------|------------|
| CPU > 80% sustained | B1 | B2 or P1v3 | +$30-74/mo |
| >50 req/sec | S1 Search | S2 Search | +$500/mo |
| >10K documents | 1536D HNSW | Quantized flat | -20% memory |
| >100 concurrent users | 1 instance | 3 instances (auto) | +2x App Service |

## 6. Backup & Recovery
- **Cosmos DB:** Continuous backup (30-day retention). Restore via Portal.
- **ADLS:** GRS replication. Point-in-time restore for blobs.
- **AI Search:** Re-index from Delta tables (AI Layer notebook).
- **Key Vault:** Soft delete enabled (90-day retention).
- **App Service:** Redeploy from Azure DevOps pipeline.
```

---

## 7. STM Template (UBI 45-Column Format)

```
Source-to-Target Mapping: {app_name}
Columns: 45 (7 stages × ~6-7 cols each + metadata)

HEADER ROW:
SourceSystem | SourceSchema | SourceTable | SourceColumn | SourceDataType | SourceDescription |
LandingContainer | LandingPath | LandingColumn | LandingDataType | LandingTransformation | LandingNotes |
BronzeDatabase | BronzeTable | BronzeColumn | BronzeDataType | BronzeTransformation | BronzeNotes |
SilverDatabase | SilverTable | SilverColumn | SilverDataType | SilverTransformation | SilverBusinessRule |
GoldDatabase | GoldTable | GoldColumn | GoldDataType | GoldTransformation | GoldAlias |
ADLSContainer | ADLSPath | ADLSColumn | ADLSDataType | ADLSPartition | ADLSFormat |
PBIDataset | PBITable | PBIColumn | PBIMeasure | PBIDisplayFolder | PBINotes |
StreamName | SubStream | Owner | LastUpdated | Status

EXAMPLE ROW (RAG):
SharePoint | /sites/docs | file.pdf | content | NVARCHAR(MAX) | Document content |
bronze/{app}/sharepoint | *.pdf | content | STRING | Raw PDF binary | Extracted via PyPDF2 |
flukebi_Bronze | {app}_documents | content | STRING | Text extraction | Page-level storage |
flukebi_Silver | {app}_clean_docs | content_clean | STRING | HTML strip, normalize | Business text |
flukebi_Gold | {app}_chunked | chunk_content | STRING | Semantic chunking 512/128 | Chunk text |
{adls_container} | gold/{app}/ | chunk_content | STRING | date partition | Delta |
N/A | N/A | N/A | N/A | N/A | No PBI for RAG |
{app} | Documents | {owner} | {date} | Active
```

---

## 8. Architecture Decision Record (ADR) Template

```markdown
# ADR-{number}: {title}

**Status:** {Proposed | Accepted | Deprecated | Superseded by ADR-XXX}
**Date:** {date}
**Deciders:** {stakeholder_list}

## Context

{What is the issue? What forces are at play? Include technical, business, and organizational constraints.}

## Decision

{What is the change we're making? State in full sentences using active voice.}

## Alternatives Considered

| Option | Pros | Cons | Est. Cost |
|--------|------|------|-----------|
| {option_1} | {pros} | {cons} | {cost} |
| {option_2} | {pros} | {cons} | {cost} |
| **{chosen}** (selected) | {pros} | {cons} | {cost} |

## Consequences

### Positive
- {benefit_1}
- {benefit_2}

### Negative
- {trade_off_1}
- {trade_off_2}

### Risks
- {risk_1} — Mitigation: {mitigation}

## Related
- ADR-{related}: {title}
- {link_to_design_doc}
```

**When to generate:** Create one ADR per major architectural decision made during Phase 0/1 Discovery. Typical decisions: model selection, vector store choice, authentication method, indexing strategy, multi-region vs single-region.

---

## 9. Model Card Template

```markdown
# Model Card: {model_name}

## Model Overview

| Field | Value |
|-------|-------|
| Model Name | {model_name} |
| Version | {version} |
| Type | {classification / regression / generation / embedding} |
| Framework | {MLflow / Azure ML / Databricks} |
| Registration | {Unity Catalog path or Azure ML registry} |
| Alias | {champion / challenger / staging} |
| Last Trained | {date} |
| Training Data | {table_or_dataset_path} |
| Training Duration | {duration} |

## Intended Use

- **Primary use:** {what the model does}
- **Users:** {who uses the model's output}
- **Out of scope:** {what the model should NOT be used for}

## Training Data

| Metric | Value |
|--------|-------|
| Dataset | {flukebi_Gold.{app}_training_data} |
| Rows | {total_rows} |
| Features | {feature_count} |
| Train/Val/Test Split | {70/15/15} |
| Date Range | {start} to {end} |
| Known Gaps | {gaps_or_biases} |

## Performance Metrics

| Metric | Train | Validation | Test | Threshold |
|--------|-------|------------|------|-----------|
| Accuracy | {val} | {val} | {val} | >= {threshold} |
| F1 Score | {val} | {val} | {val} | >= {threshold} |
| AUC-ROC | {val} | {val} | {val} | >= {threshold} |
| RMSE | {val} | {val} | {val} | <= {threshold} |

## Fairness & Bias

- **Sensitive attributes tested:** {list}
- **Disparate impact ratio:** {ratio} (threshold: > 0.8)
- **Known biases:** {description}
- **Mitigation:** {what was done}

## Limitations

- {limitation_1}
- {limitation_2}

## Monitoring

- **Drift detection:** {method — PSI, KS test, etc.}
- **Retrain trigger:** {when to retrain}
- **Dashboard:** {link_to_monitoring}

## Ethical Considerations

- {consideration_1}
- {consideration_2}
```

**When to generate:** Create for every Predictive ML archetype (Phase 2 produces the model, Phase 6 documents it). Also generate for any custom fine-tuned model in other archetypes.

---

## 10. Document Template Anti-Patterns (NEVER Do These)

1. **NEVER leave `{placeholder}` values in generated documents.** Every variable must be resolved. Unresolved placeholders in delivered documents indicate incomplete generation.
2. **NEVER generate an EA document without C4 diagrams.** Text-only architecture docs are hard to review. ASCII C4 diagrams are minimum.
3. **NEVER skip the STM for UBI-connected projects.** The 45-column format is required for UBI governance. "We'll do it later" means it never gets done.
4. **NEVER write the Operations Runbook without actual KQL queries.** Generic "check the logs" instructions are useless in an incident. Include copy-paste ready queries.
5. **NEVER generate the Developer Guide without the actual repo structure.** Read the artifact paths from state and document what actually exists, not what might exist.
6. **NEVER produce DOCX files with broken heading hierarchy.** H1 → H2 → H3, never skip levels. This breaks TOC generation and accessibility.
7. **NEVER include internal architecture details in the End User Guide.** Users don't need to know about Cosmos DB or AI Search. Keep it focused on the application experience.
8. **NEVER skip ADRs for major architectural decisions.** "We chose X because it seemed right" is not documentation. Every model/store/auth/region decision gets an ADR with alternatives considered and trade-offs documented. *What happens:* 6 months later, someone asks "why didn't we use Y?" and nobody remembers.
9. **NEVER deploy a Predictive ML model without a Model Card.** Model Cards document training data, performance metrics, known biases, and limitations. Without them, downstream consumers can't assess whether the model is appropriate for their use case.
10. **NEVER generate documents in isolation.** Cross-reference between documents: EA → Solution Design, Solution Design → Developer Guide, Developer Guide → Runbook. Disconnected documents get stale independently.
