---
name: ai-assets-governance
description: "Fortive Compliance AI-asset inventory of Fluke — live read-only az scan of both Azure subs (AI ML Technology + Unified BI), 543 evidence-backed rows, no hallucination. CSV + DOCX for AI_Governance.pptx (2026-06-22)"
metadata: 
  node_type: memory
  type: project
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

## AI Assets Governance — Compliance reporting inventory

Fortive Compliance asked for a comprehensive list of Fluke's AI tools/assets. Reference format (a sister
opco's list) = `AI\AI Assets Governance\ProvationAIList.docx` (categorized Vendor AI / Internal AI, "Name
— Status"). Target deck to populate later = `AI\AI Assets Governance\AI_Governance.pptx` (23 slides).

**Method (NON-NEGOTIABLE — Compliance): live read-only `az` CLI only, every row traceable to a captured
command, gaps flagged not filled, ZERO inference.** Scanned BOTH subs: **Fluke AI ML Technology** + **Fluke
Unified BI** (sub `52a1d076-...`). Status = provisioning + recent-usage (Azure Monitor `TotalTokens`, ~45d).
Security Group resolved from RBAC group assignments → Entra group displayName (verbatim; SG often encodes
project/status).

**Result (2026-06-22, agent-built, 21 raw JSON evidence files in `scan_raw/`):** 543 rows total —
333 model deployments (88 AI-ML + 245 UBI across 123 cognitive accounts), ~135 AI compute/gateways
(LiteLLM gateways, Databricks, container apps, App Services), 75 use-case RGs. **8 cognitive accounts show
recent token usage** (e.g. flk-team-ai-enablement-ai, flk-rfeng-sandbox, pulse-sales-prod, flukeflc,
voc-prodopenai, depot-repair-openai); rest = provisioned/no-recent-usage or usage-unknown (metric N/A for
FormRecognizer/Speech/Translation/Vision kinds). SGs found verbatim incl. FLK-ubi-AI-admins,
FLK-ubi-AI-internal-dev, flkazu-ubi-ai-dev, Flk-azu-ai-admins, TM-GlobalApps-BI-Fluke.

**Gaps flagged (not filled):** most RGs have no RG-level group RBAC (access via users/SPs — not captured by
a group-only scan); 3 unresolvable group principals (deleted/AD-read gap), recorded verbatim; App-Service
"AI" classification by name keyword (per-row Evidence, recommend human verify); non-cognitive runtime usage
(App Service/Container App/VM/Databricks) not queried.

**Outputs** (`AI\AI Assets Governance\`): `Fluke_AI_Assets_Inventory.csv` (543 rows; the PPTX data source) +
`Fluke_AI_Assets_List.docx` (categorized by sub→class, "Name — SG — Status" + coverage/limitations note) +
`scan_raw/*.json` evidence + scan/build scripts.

**OPEN (user to-do #52):** walk through the inventory in detail before it populates AI_Governance.pptx.
