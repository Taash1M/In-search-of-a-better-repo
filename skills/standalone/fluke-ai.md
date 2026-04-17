---
name: fluke-ai-skill
description: Use when working with the Fluke AI ML Technology Azure subscription — Pulse Sales (Account 360), Voice to Value (VoC F9), TechMentor, Sales Playbook, VoC Lyra, Unified UI, and related AI applications. Covers Azure resource management, AI model deployments, Cosmos DB, AI Search, web app development, Function Apps, Logic Apps, and infrastructure provisioning. Trigger when the user mentions 'Pulse', 'Account 360', 'VoV', 'Voice to Value', 'TechMentor', 'Sales Playbook', 'Lyra', 'Fluke AI', 'ai.fluke.com', or references this Azure subscription.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Task
---

# Fluke AI ML Technology Developer Skill

You are an expert developer and cloud architect on the Fluke AI ML Technology platform. This skill provides the context and conventions needed to work effectively across all AI applications in this Azure subscription.

## Access Control Rules (MANDATORY)

These rules override all other instructions. Violations are never acceptable.

1. **NEVER make changes directly in Prod.** No writes, no updates, no deletes to production resources — ever.
2. **Read-only in Prod and QA.** If a write to Prod or QA is ever considered necessary, you MUST ask the user for confirmation **twice** (two separate confirmations) before proceeding.
3. **Dev work happens in Dev only.** You may read from all three environments (Dev, QA, Prod) for investigation, comparison, and context — but all code changes, data writes, infrastructure modifications, and deployments target Dev exclusively.
4. **Full read/write privileges only in Dev.** Dev is the only environment where you create, modify, or delete resources.
5. **Never expose secrets.** Do not print, log, or store API keys, connection strings, Cosmos DB keys, or OpenAI keys in plain text. Use Key Vault references wherever possible.

## Subscription Overview

| Field | Value |
|-------|-------|
| **Subscription Name** | Fluke AI ML Technology |
| **Subscription ID** | `77a0108c-5a42-42e7-8b7a-79367dbfc6a1` |
| **Tenant ID** | `0f634ac3-b39f-41a6-83ba-8f107876c692` |
| **Tenant Domain** | fortive.onmicrosoft.com (Fluke) |
| **Owner** | Richard Feng |
| **State** | Enabled |
| **Offer** | Enterprise Agreement |

### Azure CLI Access

```bash
# Get ARM token (user is already authenticated as taashi.manyanga@fluke.com)
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)

# Query subscription via REST API
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://management.azure.com/subscriptions/77a0108c-5a42-42e7-8b7a-79367dbfc6a1/..."

# Get Microsoft Graph token (for SharePoint/Teams integrations)
GRAPH_TOKEN=$(az account get-access-token --resource https://graph.microsoft.com --query accessToken -o tsv)
```

**Important:** The subscription is accessed via REST API using `az account get-access-token`. The `az account set` command may not work for this subscription depending on the login context — always use the token-based REST approach as a fallback.

## Knowledge Base Reference

The full subscription knowledge base with every resource group, resource, AI model deployment, and architecture detail is maintained at:

```
C:\Users\tmanyang\OneDrive - Fortive\AI\Commercial Americas\fluke-ai-ml-subscription-knowledge.md
```

**Always read this file at the start of any development session** to ensure you have current context on the subscription's resources.

## Project Artifacts Directory

All project-related artifacts, documentation, and working files for Commercial Americas initiatives are stored at:

```
C:\Users\tmanyang\OneDrive - Fortive\AI\Commercial Americas\
```

---

## Applications

### 1. Pulse Sales / Account 360

The flagship AI agent providing account intelligence to sales teams.

| Environment | Resource Group | Web App | URL |
|-------------|---------------|---------|-----|
| **Dev** | `dev-flk-ai-foundry-hub-rg` | `flk-pulse-sales-agent` | `*.eastus2-01.azurewebsites.net` |
| **QA** | `flk-pulsesales-qa-rg` | `flk-pulse-webapp-test` | `pulse-test.fluke.com` |
| **Prod** | `flk-pulsesales-prod-rg` | `flk-pulse-webapp-production` | `pulse-sales.fluke.com` |

**Key Resources (Dev):**
- AI Services: `pulse-sales-dev-ai-resource` (gpt-4o, text-embedding-3-large)
- AI Foundry Hub: `FLK-AI-Foundry-Hub-Dev`
- AI Foundry Project: `pulse-sales-dev`
- Cosmos DB: `dev-flk-cosmosdb` (East US)
- AI Search: `dev-flk-search-service-free` (Free tier)
- Key Vault: `dev-flk-kv-ai-foundry`
- Container Registry: `flkdockerregistry` (`flkdockerregistry.azurecr.io`)
- Function App: `flk-pulsesales-funcappfc-dev` (Flex consumption)
- Logic App: `flk-pulsesales-logicapp-dev`
- Storage: `devflkaifoundryhubadls`, `devflkaigeneralstorage`

**Key Resources (Prod):**
- AI Services: `pulse-sales-prod-ai-resource` (gpt-4o-prod, text-embedding-3-large)
- Cosmos DB: `flk-pulsesales-prod-cosmosdb` (Central US)
- Bing Grounding: `pulse-sales-prod-groundingwithbingsearch`

**AI Models:**
| Env | Deployment | Model | Capacity |
|-----|-----------|-------|----------|
| Dev | gpt-4o | gpt-4o 2024-11-20 | 250K TPM |
| Dev | text-embedding-3-large | text-embedding-3-large v1 | 250K TPM |
| QA | gpt-4o | gpt-4o 2024-11-20 | 250K TPM |
| QA | text-embedding-3-large | text-embedding-3-large v1 | 527K TPM |
| Prod | gpt-4o-prod | gpt-4o 2024-11-20 | 250K TPM |
| Prod | text-embedding-3-large | text-embedding-3-large v1 | 250K TPM |

**Related IT Projects (2026):**
1. Expand customer data to 5 years history in CRM (Q1, Dev in progress, Jatin Kochhar)
2. Account 360 feedback loop app (Q1, Dev in progress, Jatin Kochhar)
3. CRM/Oracle Account Match and Linkage (Q1, POC, Richard Feng)
4. Account Comparison Tool — Base (Q2, To Do, Richard Feng)
5. Account Comparison Tool — 360 PBI Dashboard (Q2, To Do, Richard Feng)
6. Account Comparison Tool — Heat Map (Q2, To Do, Richard Feng)
7. Additional Account 360 questions (Q4, To Do, Richard Feng)
8. **Sales Playbook** — AI-powered vertical market playbooks (Q2, Define Requirements, Richard Feng)
9. **Build vertical markets knowledge repository** (Q2, Define Requirements, Richard Feng)
10. **Geo 360 questions** (Q3, To Do, Richard Feng)

---

### 2. Voice to Value / Sales VoC F9

Customer voice analytics from sales calls — extracts signals, sentiment, product mentions.

| Environment | Resource Group | Web App |
|-------------|---------------|---------|
| **Dev** | `flk-salesvoc-f9-dev-rg` | `flk-salesvoc-f9-dev` |
| **Prod** | `flk-salesvoc-f9-prod-rg` | `flk-salesvoc-f9-prod` |

**Key Resources (Prod):**
- OpenAI: `flk-salesvoc-f9-openai-prod` (gpt-4.1, text-embedding-3-large)
- Cosmos DB: `flk-salesvoc-f9-cosmos-prod` (Central US)
- Cosmos DB (provisioned): `flk-salesvoc-f9-prov-cosmos-prod` (Central US + East US 2 geo-replicated)
- Function App: `flk-salesvoc-f9-funcappfc-prod` (Flex consumption)
- Logic App: `flk-salesvoc-f9-logicapp-prod`
- Storage: `flksalesvocf9storageprod`

**AI Models:**
| Env | Deployment | Model | Capacity |
|-----|-----------|-------|----------|
| Dev | gpt-5.1 | gpt-5.1 2025-11-13 | 101K TPM |
| Dev | gpt-4.1 | gpt-4.1 2025-04-14 | 769K TPM |
| Dev | gpt-4.1-small | gpt-4.1 2025-04-14 | 75K TPM |
| Dev | gpt-4o | gpt-4o 2024-11-20 | 81K TPM |
| Prod | gpt-4.1 | gpt-4.1 2025-04-14 | 774K TPM |
| Prod | gpt-4.1-small | gpt-4.1 2025-04-14 | 77K TPM |

**Related IT Projects (2026):**
1. VoV feedback loop app (Q1, Dev in progress, Jatin Kochhar)
2. Improve Product Identification (Q1/Q2, POC, Jatin Kochhar) — **needs Sr. AI engineer**
3. Improve VoV Quality (Q1, Dev in progress, Jatin Kochhar) — **needs Sr. AI engineer**
4. Newsletter and reports (Q2, To Do, Richard Feng)

---

### 3. TechMentor

AI technical assistant for internal use.

| Environment | Resource Group | Web App |
|-------------|---------------|---------|
| **Dev** | `flk-techmentor-dev-rg` | `flk-techmentor-dev` |
| **UAT** | `flk-techmentor-uat-rg` | (empty) |
| **Prod** | `flk-techmentor-prod-rg` | `flk-techmentor-prod` |

**AI Models (Prod):**
| Deployment | Model | Capacity |
|-----------|-------|----------|
| gpt-5 | gpt-5 2025-08-07 | 250K TPM |
| gpt-5-nano | gpt-5-nano 2025-08-07 | 250K TPM |
| o3-mini | o3-mini 2025-01-31 | 250K TPM |
| text-embedding-3-large | text-embedding-3-large v1 | 250K TPM |

---

### 4. Pulse Unified UI

The portal that consolidates all Pulse AI tools under one interface.

| Environment | Resource Group | Web App | URL |
|-------------|---------------|---------|-----|
| **Dev** | `flk-pulse-unifiedui-dev` | `pulse-unified-ui-dev` | `*.azurewebsites.net` |
| **Test** | `flk-pulse-unifiedui-dev` | `pulse-unified-ui-test` | `*.azurewebsites.net` |
| **Prod** | `flk-unified-ui-prod-rg` | `pulse-unified-ui-prd` | `ai.fluke.com` |

---

### 5. VoC Lyra (Development/Experimental)

Comprehensive VoC analytics platform — currently **stopped** in dev.

| Resource Group | Key Resources |
|---------------|---------------|
| `flk-voc-lyra-dev-rg` | AI Services (`voc-lyra-dev-ai`), Cosmos DB, AI Search (Standard), App Gateway, VNet, Function App |

**AI Models (voc-lyra-dev-ai) — MOST EXTENSIVE deployment in subscription:**
gpt-5 (x2), gpt-4.1, gpt-4.1-mini, gpt-4o, o4-mini, o3-mini, o1, text-embedding-3-large — all at 250K TPM.

---

### 6. VoC 360 Customer Search

Customer search and recruitment intelligence tool.

| Environment | Resource Group | Web App |
|-------------|---------------|---------|
| **Dev** | `flk-voc360-recruitment-dev` | `voc-recruitment-accountsearch` |
| **Prod** | `flk-voc360-recruitment-prod` | `voc360-customersearch-prod` |

---

### 7. Team AI Enablement (Claude Code)

Shared Claude Code infrastructure enabling 10 team members to use Claude Opus 4.6 via Azure AI Foundry.

| Environment | Resource Group | AI Services | Location |
|-------------|---------------|-------------|----------|
| **Shared** | `flk-team-ai-enablement-rg` | `flk-team-ai-enablement-ai` | East US 2 |

**Key Resources:**
- AI Services: `flk-team-ai-enablement-ai` (S0, AIServices, SystemAssigned identity)
- Foundry Project: `claude-code-enablement`
- Endpoint: `https://flk-team-ai-enablement-ai.services.ai.azure.com/anthropic/v1/messages`

**AI Models (Anthropic via Azure AI Foundry):**
| Deployment | Model | SKU | Capacity | RPM | TPM |
|-----------|-------|-----|----------|-----|-----|
| claude-code-node1 | claude-opus-4-6 | GlobalStandard | 250 | 250 | 250K |
| claude-code-node2 | claude-opus-4-6 | GlobalStandard | 250 | 250 | 250K |
| claude-code-node3 | claude-opus-4-6 | GlobalStandard | 250 | 250 | 250K |
| claude-opus-4-6 | claude-opus-4-6 | GlobalStandard | 750 | 750 | 750K |

**Node Assignments (3-5 users per node):**
| Node | Users |
|------|-------|
| node1 | Kevin Davison, Eshwari Mulpuru, Urvin Thakkar, Mihai Constantin-Pau |
| node2 | Jd Giles, Richard Feng, Alex Chillman |
| node3 | Vineet Thuvara, Steven Moore, Taashi Manyanga, Daniel Pouley, Azra Jabeen |

**End-User Configuration:**
```bash
export CLAUDE_CODE_USE_FOUNDRY=1
export ANTHROPIC_FOUNDRY_RESOURCE="flk-team-ai-enablement-ai"
export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-code-nodeX"  # node1/node2/node3
export ANTHROPIC_FOUNDRY_API_KEY="<api-key>"
```

**RBAC:** Azure AI User (53ca6127-db72-4b80-b1b0-d745d6d5456d) assigned to all 12 users on the AI Services resource.

**Deployment Notes:**
- Anthropic models require `api-version=2025-12-01` for REST API
- Portal-based deployments (ai.azure.com) recommended over REST API for initial Anthropic model provisioning
- Marketplace agreement: `anthropic-claude-opus-4-6-offer` (signed 2026-03-02)
- Foundry project + SystemAssigned managed identity required before deploying

---

### 8. Other Applications

| Application | Resource Group | Purpose |
|-------------|---------------|---------|
| Oracle Code-to-BI | `flk-oracle-code-to-business-insight-dev` | Oracle ERP insight tool with Whisper container registry |
| HR Flukie AI | `flk-hr-flukie-ai-prod-rg` | HR AI search (Standard search service, no webapp) |
| GraphRAG POC | `flk-dev-ms-rag-poc-lyra` | MS Chandrasekar's GraphRAG POC for Lyra use cases |

---

## Architecture Patterns

### Standard Application Architecture

Every application in this subscription follows this pattern:

```
Azure OpenAI / AI Services
        |
        v
Web App (Linux, App Service)  <-->  Cosmos DB (GlobalDocumentDB)
        |                               |
        v                               v
Function App (Flex Consumption)    AI Search (Standard/Free)
        |
        v
Logic App  -->  API Connections (SharePoint, Blob Storage)
        |
        v
Storage Account (StorageV2)
```

### Environment Promotion Path

```
Dev (East US) --> QA/UAT (East US 2) --> Prod (Central US / East US 2)
```

### Resource Naming Convention

```
flk-{app-name}-{env}-{resource-type}
```

| Segment | Values |
|---------|--------|
| `flk` | Fluke prefix (always) |
| `{app-name}` | `pulsesales`, `salesvoc-f9`, `techmentor`, `voc-lyra`, `voc360`, `pulse-unifiedui`, `team-ai-enablement` |
| `{env}` | `dev`, `qa`, `uat`, `prod` |
| `{resource-type}` | `rg`, `cosmosdb`, `openai`, `funcapp`, `logicapp`, etc. |

### Custom Domains

| Domain | Application |
|--------|-------------|
| `ai.fluke.com` | Pulse Unified UI (portal) |
| `pulse-sales.fluke.com` | Pulse Sales / Account 360 |
| `pulse-test.fluke.com` | Pulse Sales QA |

---

## AI Model Inventory

### Models Available Across Subscription

| Model Family | Models | Primary Use |
|-------------|--------|-------------|
| **GPT-5.x** | gpt-5.1, gpt-5, gpt-5-nano | Latest generation — VoC F9 dev, TechMentor prod |
| **GPT-4.1** | gpt-4.1, gpt-4.1-mini, gpt-4.1-small | Primary workhorse — VoC F9, TechMentor, Lyra |
| **GPT-4o** | gpt-4o | Previous gen — Pulse Sales dev/prod/qa |
| **o-series** | o1, o3-mini, o4-mini | Reasoning models — TechMentor, Lyra |
| **Embeddings** | text-embedding-3-large | Standard across all environments |
| **Claude (Anthropic)** | claude-opus-4-6 | Team AI Enablement — via Azure AI Foundry (East US 2) |

### When selecting models for new development:
- **Chat/agent tasks:** Use `gpt-4.1` (proven workhorse) or `gpt-5` (latest, in TechMentor prod)
- **Cost-sensitive:** Use `gpt-4.1-mini` or `gpt-5-nano`
- **Complex reasoning:** Use `o3-mini` or `o4-mini`
- **Embeddings:** Always use `text-embedding-3-large`
- **Pulse Sales specifically** still uses `gpt-4o` — check with team before upgrading

---

## Integration Points

### SharePoint Online
Logic Apps in Dev, VoC F9 Prod, and TechMentor Prod all have SharePoint API connections for document ingestion and workflow triggers.

**SharePoint Site (Pulse AI):**
- Site ID: `fortive.sharepoint.com,40341b96-c6ae-4345-87fe-9820b1956776,ef391053-7bee-40f4-b0e0-66d51dd2100f`
- Drive ID: `b!lhs0QK7GRUOH_pggsZVndlMQOe_ue_RAsOBm1R3SEA-BMkeuj3psRK7ZujIA_o0w`

### Logic Apps

3 Logic Apps in this subscription (all Recurrence-triggered, HTTP→Parse→ForEach pattern). For full Logic App management patterns, templates, and API connection setup, use the **`/azure-logic-apps`** skill.

| Logic App | Resource Group | Purpose |
|-----------|---------------|---------|
| `flk-pulsesales-logicapp-dev` | `dev-flk-ai-foundry-hub-rg` | Pulse Sales data sync |
| `flk-salesvoc-f9-logicapp-prod` | `flk-salesvoc-f9-prod-rg` | VoC F9 data sync |
| `flk-techmentor-logicapp-prod` | `flk-techmentor-prod-rg` | TechMentor data sync |

### Bing Search Grounding
Pulse Sales (Prod + QA) uses Bing Search for grounding AI responses with web data.

### Container Registries
| Registry | URL | Purpose |
|----------|-----|---------|
| `flkdockerregistry` | `flkdockerregistry.azurecr.io` | Main Docker registry (Pulse Sales) |
| `flukewhisperregistry` | `flukewhisperregistry.azurecr.io` | Whisper ASR containers (Oracle Code-to-BI) |

---

## Key Personnel

| Person | Role | Responsible For |
|--------|------|----------------|
| **Richard Feng** | Subscription Owner / AI Architect | Sales Playbook, Account Comparison tools, Industry knowledge repo, Geo 360, VoV newsletters, sandbox environments |
| **Jatin Kochhar** | AI Development Lead | TechMentor (creator), Account 360 5yr history, feedback loops, VoV quality/product ID, Unified UI prod |
| **Kranthi Kothapally** | Data/BI Lead | IIR to UBI integration, CRM to BigQuery |
| **Sandeep Roy** | CRM Developer | IIR to CRM Lead |
| **Vijeta** | AI Researcher | Research workspace in AI Foundry Dev |
| **Anushka** | AI Researcher | Research workspace in AI Foundry Dev |
| **MS Chandrasekar** | Consultant | GraphRAG POC for Lyra |
| **Prashanth** | Developer | Personal dev AI Foundry environment |

---

## Development Workflow

### Creating a New AI Application

1. **Create resource group** following naming convention: `flk-{app-name}-dev-rg`
2. **Provision core resources:**
   - Azure OpenAI or AI Services account (S0)
   - Cosmos DB (GlobalDocumentDB, Standard)
   - App Service Plan + Web App (Linux)
   - Storage Account (StorageV2)
3. **Deploy AI models** (text-embedding-3-large + primary chat model)
4. **Configure Key Vault** for secrets
5. **Set up API connections** (SharePoint, Blob) if needed
6. **Create Function App** (Flex consumption) for background processing
7. **Add Logic App** for workflow automation

### Working with Azure OpenAI Deployments

```bash
# List deployments for an account
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)
RG="dev-flk-ai-foundry-hub-rg"
ACCOUNT="pulse-sales-dev-ai-resource"

curl -s -H "Authorization: Bearer $TOKEN" \
  "https://management.azure.com/subscriptions/77a0108c-5a42-42e7-8b7a-79367dbfc6a1/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/$ACCOUNT/deployments?api-version=2024-10-01"
```

### Working with Cosmos DB

```bash
# Get Cosmos DB account info
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://management.azure.com/subscriptions/77a0108c-5a42-42e7-8b7a-79367dbfc6a1/resourceGroups/$RG/providers/Microsoft.DocumentDB/databaseAccounts/{ACCOUNT_NAME}?api-version=2024-05-15"
```

### Working with Web Apps

```bash
# Get web app details
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://management.azure.com/subscriptions/77a0108c-5a42-42e7-8b7a-79367dbfc6a1/resourceGroups/$RG/providers/Microsoft.Web/sites/{SITE_NAME}?api-version=2023-12-01"

# Get web app configuration (app settings, connection strings)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://management.azure.com/subscriptions/77a0108c-5a42-42e7-8b7a-79367dbfc6a1/resourceGroups/$RG/providers/Microsoft.Web/sites/{SITE_NAME}/config/appsettings/list?api-version=2023-12-01" \
  -X POST
```

---

## Commercial Americas Context

This subscription supports the **Commercial Americas** initiative — building a Vertical Market Sales Playbook powered by Pulse AI. Key context files are at:

```
C:\Users\tmanyang\OneDrive - Fortive\AI\Commercial Americas\
  fluke-ai-ml-subscription-knowledge.md   -- Full subscription inventory
  source_docs\                             -- SharePoint documents (project plans, exec summaries)
  Miro Board Screenshots\                  -- Playbook wireframes, process flows, operating model
```

### IT Commercial Projects 2026 (21 total)
- **17 PD projects** under "PD: HGV DC/DER/DEF (IP1)" — AI, BI, CRM, UBI
- **3 Strategy Initiative projects** — PTK/AZ Migration, USM Phase 4, Catalog Sites
- **1 unclassified** — Fortive CRM to BigQuery

### Sales Playbook Architecture (from Miro Board)
The Sales Playbook (Project 8) has a 7-layer architecture:
1. Commercial Layer ("The Why Us") — Universal Fluke value prop
2. Vertical Market Layer ("Where We Play") — 12 verticals
3. ICP Layer ("Our Ideal Customer") — Customer profiles per vertical
4. Persona Layer ("Who We Sell To") — Buyer personas
5. Account Scenario Layer ("When to Use Which Play") — Situational playbooks
6. Sales Execution Layer ("Own the Win") — 12-stage selling process
7. Enablement & Feedback Layer ("Keep it Alive") — Training, coaching

### 10-Step Pulse-AI Guided Prospecting Process
1. Define Vertical → 2. Research → 3. Pre-Call Planning → 4. Persona → 5. Customer Engagement → 6. Value Proposition → 7. Account Planning → 8. Execution → 9. Reflection → 10. Cross-Sell

### Systems Integration
- **Dynamics** (CRM) — Primary CRM system
- **PowerBI** — Analytics and dashboards
- **Eloqua** — Marketing automation
- **Pulse AI** — AI guidance platform (this subscription)
- **SharePoint** — Content management

---

## Capacity Constraints (Important for Planning)

These projects have flagged resource needs — factor into any development planning:

| Project | Constraint |
|---------|-----------|
| Sales Playbook | Sr. AI engineer + 2+ AI devs needed post-requirements |
| Industry Knowledge Repo | Sr. AI engineer + 2+ AI devs needed post-requirements |
| Improve Product ID | Sr. AI engineer + 1+ AI devs needed |
| Improve VoV Quality | Sr. AI engineer + 1+ AI devs needed |
