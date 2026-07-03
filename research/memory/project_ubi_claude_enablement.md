---
name: project-ubi-claude-enablement
description: "UBI subscription Claude/AI enablement — flkubi-claude-enablemen-resource in flkubi-prd-rg-001, 9 model deployments, RBAC via security group + direct assignments (last updated 2026-07-02)"
metadata: 
  node_type: memory
  type: project
  originSessionId: edc72005-8a71-4afe-9aaa-3040c235e4a7
---

## UBI Claude Enablement Resource

**Why:** Claude and GPT models provisioned in the UBI subscription (`52a1d076`) for the BI/data engineering team, separate from the Fluke AI ML Technology subscription's Team AI Enablement resource.

**How to apply:** When anyone on the UBI team needs Claude/AI model access, check this resource's RBAC first.

### Resource Details
- **Resource**: `flkubi-claude-enablemen-resource` (AIServices, S0)
- **Location**: East US 2
- **Resource Group**: `flkubi-prd-rg-001`
- **Subscription**: Fluke Unified BI (`52a1d076-bbbf-422a-9bf7-95d61247be4b`)
- **Endpoint**: `https://flkubi-claude-enablemen-resource.services.ai.azure.com/anthropic/v1/messages`
- **Cognitive Services endpoint**: `https://flkubi-claude-enablemen-resource.cognitiveservices.azure.com/`
- **AI Foundry Project**: `flkubi-claude-enablement`
- **disableLocalAuth**: False (both API key and AAD auth work)

### Model Deployments (9 total)
| Deployment | Model | Capacity | Status |
|-----------|-------|----------|--------|
| claude-opus-4-7 | claude-opus-4-7 | 1000 | Succeeded |
| claude-sonnet-4-6 | claude-sonnet-4-6 | 937 | Succeeded |
| claude-haiku-4-5 | claude-haiku-4-5 | 1000 | Succeeded |
| claude-opus-node-5 | claude-opus-4-7 | 425 | Succeeded |
| claude-sonnet-node-5 | claude-sonnet-4-6 | 425 | Succeeded |
| claude-haiku-node-5 | claude-haiku-4-5 | 450 | Succeeded |
| claude-opus-node-6 | claude-opus-4-7 | 250 | Succeeded |
| claude-sonnet-node-6 | claude-sonnet-4-6 | 251 | Succeeded |
| gpt-5.4-mini | gpt-5.4-mini | 5000 | Succeeded |

### RBAC — Azure AI User Role
Access controlled via:
1. **Security group**: `flkazu-ubi-FlkBIprojects-iam-group` (`e2e98118-edc0-4671-8dd7-042bfcfe660c`) — Azure AI User role directly on the resource. Group owner: Rama Kompella.
2. **Direct assignments**: Added 2026-06-04 for users not yet in the group.

**Group members (9):** Taashi Manyanga, Shwetabh Shekhar, Mohd Zaid, Rishabh Chouhan, Rekha Kiranmai Muttinti, Veera Narayana Poondla, Anas Khan, Sriya Sushrutha Reddy Kandi, Suresh Sundaram

**Direct Foundry User assignments:**
- Harsha Nadig Subbarao (`41183d4f`) — added 2026-06-04; was blocked on AAD, API key worked
- Aravind Sivaji (`562c4e30`) — added 2026-06-04; was blocked on AAD, API key worked
- Kranthi Kothapally (`cc3d8cc0`) — added 2026-07-02; AAD auth, Node 5 models; assignment `14b76987-e741-4551-9f59-bc52adea27ee`; settings.json at `user-config/Flkubi/Kranthi/settings.json`

**Pending**: Add Harsha + Aravind to the security group (week of 2026-06-09), then remove direct assignments.

### Diagnostic Logging
| Setting | Value |
|---------|-------|
| Name | `claude-usage-logs` |
| Destination | `flkubiadlsprd` (Prod ADLS) |
| RequestResponse | Enabled (captures API request/response metadata, per-user identity via AAD objectId) |
| Audit | Enabled |
| AzureOpenAIRequestUsage | Disabled (N/A for Anthropic) |
| Trace | Disabled |
| AllMetrics | Enabled |

### API Call Pattern
```bash
# AAD auth
AI_TOKEN=$(az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken -o tsv)
curl -X POST "https://flkubi-claude-enablemen-resource.services.ai.azure.com/anthropic/v1/messages?api-version=2025-12-01" \
  -H "Authorization: Bearer $AI_TOKEN" \
  -H "Content-Type: application/json" \
  -H "anthropic-version: 2023-06-01" \
  -d '{"model": "claude-opus-4-7", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hello"}]}'
```

Related: [[project-team-ai-enablement]] (different subscription, same team enablement pattern)
