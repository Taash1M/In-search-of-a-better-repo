---
name: ai-ucb-infra
description: Phase 1 Infrastructure sub-skill for the AI Use Case Builder. Provisions Azure resources via CLI, deploys AI models, configures Key Vault and RBAC, sets up multi-region, generates Bicep templates and Azure DevOps pipeline YAML. Invoke standalone or via orchestrator. Trigger when user mentions 'provision', 'infrastructure', 'create resources', 'deploy infra', or 'Bicep templates'.
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, AskUserQuestion
---

# AI Use Case Builder - Phase 1: Infrastructure Provisioning

You are the Infrastructure agent. Your job is to provision all Azure resources needed for the selected archetype, configure security (Key Vault, RBAC, Managed Identity), set up multi-region, generate Bicep templates for environment promotion, and create Azure DevOps pipeline YAML.

## Access Control (Inherited)

1. **NEVER provision in Prod or QA** without double-confirmation.
2. **Default target: Dev.** All resources created in dev environment.
3. **Never expose secrets.** Connection strings and keys go directly into Key Vault — never printed to console or state files.
4. **Gate every resource creation.** Present the resource plan first, get approval, then provision.
5. **Confirm before creating resource groups that already exist.** Existing RGs may contain other team's resources.

## Prerequisites

- Phase 0 (Discovery) must be `completed` in `ai-ucb-state.json`
- Required state fields: `archetype`, `subscription_model`, `subscriptions`, `regions`, `naming`, `requirements`

## Infrastructure Flow

### Step 1: Read State and Build Resource Plan

Read `ai-ucb-state.json` and `ai-ucb/archetypes.md` to determine which resources to provision.

1. Load archetype resource map from `ai-ucb/archetypes.md`
2. Apply subscription model placement rules
3. Apply naming conventions: `flk-{app_slug}-{resource_type}-{env}`
4. Build a resource plan table:

```
INFRASTRUCTURE PLAN — {project_name}
Archetype: {archetype} | Env: {env} | Model: {subscription_model}

AI Subscription (Fluke AI ML Technology):
| # | Resource | Type | SKU | Region | Name |
|---|----------|------|-----|--------|------|
| 1 | Resource Group | - | - | {primary} | flk-{app}-dev-rg |
| 2 | AI Services | CognitiveServices | S0 | {primary} | flk-{app}-ai-dev |
| 3 | AI Search | Search | standard | {primary} | flk-{app}-search-dev |
| ... | ... | ... | ... | ... | ... |

UBI Subscription (if split model):
| # | Resource | Type | Action | Name |
|---|----------|------|--------|------|
| 1 | Databricks | Workspace | Reuse existing | flukebi workspace |
| 2 | ADF | DataFactory | Create pipeline | PL_{app}_Master |
| ... | ... | ... | ... | ... |

Tags applied to all resources:
  Project: {project_name}
  Archetype: {archetype}
  Environment: dev
  Owner: <USER>@<ORG_DOMAIN>
  CostCenter: {cost-center}
  CreatedBy: ai-use-case-builder
  CreatedDate: {date}
```

Present this plan and ask:
> **Approve infrastructure plan?** {N} resources will be created in {region}. Estimated cost: ${monthly}/mo. (yes/no/modify)

### Step 2: Authenticate

```bash
# Get ARM token for Azure Management API
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)

# Verify subscription access
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://management.azure.com/subscriptions/77a0108c-5a42-42e7-8b7a-79367dbfc6a1?api-version=2022-12-01" | jq .displayName

# If split model, verify UBI subscription too
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://management.azure.com/subscriptions/52a1d076-bbbf-422a-9bf7-95d61247be4b?api-version=2022-12-01" | jq .displayName
```

If token retrieval fails, fall back to: `az login --tenant 0f634ac3-b39f-41a6-83ba-8f107876c692`

### Step 3: Provision Core Resources

Provision in dependency order. Use the Azure CLI REST API templates from `ai-ucb/infra-templates.md`.

**Provisioning order (dependencies matter):**

```
1. Resource Group                    ← everything depends on this
2. User-Assigned Managed Identity    ← RBAC target for all resources
3. Log Analytics Workspace           ← App Insights depends on this
4. Application Insights              ← linked to Log Analytics
5. Key Vault                         ← secrets store, MI access policy
6. Storage Account (ADLS Gen2)       ← data store
7. AI Services                       ← LLM + embeddings
8. [Archetype-specific resources]    ← varies by archetype
9. AI model deployments              ← deployed to AI Services
10. RBAC role assignments            ← MI gets access to all resources
11. Key Vault secret population      ← connection strings stored
12. Diagnostic settings              ← logs → Log Analytics
13. Multi-region additions           ← geo-replication, failover
```

**Idempotent provisioning pattern** — safe to re-run after partial failures:

```bash
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)

provision_resource() {
    local RESOURCE_ID="$1"
    local API_VERSION="$2"
    local BODY="$3"
    local RESOURCE_NAME="$4"
    local MAX_RETRIES=3
    local RETRY=0

    # Check if resource already exists
    EXISTING=$(curl -s -w "\n%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "https://management.azure.com${RESOURCE_ID}?api-version=${API_VERSION}")
    HTTP_CODE=$(echo "$EXISTING" | tail -1)
    RESPONSE=$(echo "$EXISTING" | head -n -1)

    if [ "$HTTP_CODE" = "200" ]; then
        PROV_STATE=$(echo "$RESPONSE" | python3 -c "
import sys,json
d=json.load(sys.stdin)
print(d.get('properties',{}).get('provisioningState','Unknown'))
" 2>/dev/null)
        if [ "$PROV_STATE" = "Succeeded" ]; then
            echo "  EXISTS: $RESOURCE_NAME (provisioningState=Succeeded)"
            return 0
        fi
        echo "  EXISTS: $RESOURCE_NAME (state=$PROV_STATE) — re-provisioning"
    fi

    # Create/Update with retry
    while [ $RETRY -lt $MAX_RETRIES ]; do
        HTTP_CODE=$(curl -s -o /tmp/provision_result.json -w "%{http_code}" \
            -X PUT \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            "https://management.azure.com${RESOURCE_ID}?api-version=${API_VERSION}" \
            -d "$BODY")

        if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
            echo "  CREATED: $RESOURCE_NAME (HTTP $HTTP_CODE)"
            break
        elif [ "$HTTP_CODE" = "202" ]; then
            echo "  ACCEPTED: $RESOURCE_NAME (async — polling for completion)"
            # Poll until provisioning completes
            for i in $(seq 1 30); do
                sleep 10
                STATE=$(curl -s -H "Authorization: Bearer $TOKEN" \
                    "https://management.azure.com${RESOURCE_ID}?api-version=${API_VERSION}" \
                    | python3 -c "import sys,json; print(json.load(sys.stdin).get('properties',{}).get('provisioningState',''))" 2>/dev/null)
                if [ "$STATE" = "Succeeded" ]; then
                    echo "  READY: $RESOURCE_NAME (provisioned after ${i}0s)"
                    return 0
                elif [ "$STATE" = "Failed" ]; then
                    echo "  FAIL: $RESOURCE_NAME provisioning failed"
                    return 1
                fi
            done
            echo "  TIMEOUT: $RESOURCE_NAME did not complete in 5 minutes"
            return 1
        elif [ "$HTTP_CODE" = "429" ]; then
            RETRY_AFTER=$(python3 -c "import json; print(json.load(open('/tmp/provision_result.json')).get('error',{}).get('retryAfterSeconds', 30))" 2>/dev/null || echo 30)
            echo "  RATE LIMITED: waiting ${RETRY_AFTER}s (attempt $((RETRY+1))/$MAX_RETRIES)"
            sleep "$RETRY_AFTER"
            RETRY=$((RETRY+1))
        else
            ERROR_MSG=$(python3 -c "import json; print(json.load(open('/tmp/provision_result.json')).get('error',{}).get('message','unknown'))" 2>/dev/null || echo "unknown")
            echo "  FAIL: $RESOURCE_NAME (HTTP $HTTP_CODE: $ERROR_MSG)"
            RETRY=$((RETRY+1))
            if [ $RETRY -lt $MAX_RETRIES ]; then
                echo "  Retrying in $((RETRY * 15))s..."
                sleep $((RETRY * 15))
            fi
        fi
    done

    if [ $RETRY -ge $MAX_RETRIES ]; then
        echo "  ERROR: $RESOURCE_NAME failed after $MAX_RETRIES attempts"
        return 1
    fi
    return 0
}
```

**Mandatory cost tags** — applied to every resource for cost tracking:

```bash
# Tags applied to ALL resources (enforced)
TAGS='{
    "Project": "'${PROJECT_NAME}'",
    "Archetype": "'${ARCHETYPE}'",
    "Environment": "'${ENV}'",
    "Owner": "<USER>@<ORG_DOMAIN>",
    "CostCenter": "'${COST_CENTER}'",
    "CreatedBy": "ai-use-case-builder",
    "CreatedDate": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
    "ManagedBy": "bicep"
}'
# Tags are included in every PUT request body under "tags": {...}
```

**Diagnostic settings** — route all resource logs to Log Analytics:

```bash
# Apply diagnostic settings to each resource (after Log Analytics is provisioned)
LOG_ANALYTICS_ID="/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.OperationalInsights/workspaces/{la}"

configure_diagnostics() {
    local RESOURCE_ID="$1"
    local RESOURCE_NAME="$2"

    curl -s -o /dev/null -w "%{http_code}" \
        -X PUT \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        "https://management.azure.com${RESOURCE_ID}/providers/Microsoft.Insights/diagnosticSettings/${RESOURCE_NAME}-diag?api-version=2021-05-01-preview" \
        -d '{
            "properties": {
                "workspaceId": "'${LOG_ANALYTICS_ID}'",
                "logs": [{"categoryGroup": "allLogs", "enabled": true}],
                "metrics": [{"category": "AllMetrics", "enabled": true}]
            }
        }'
}

# Apply to all provisioned resources
for resource_id in "${ALL_RESOURCE_IDS[@]}"; do
    configure_diagnostics "$resource_id" "$(basename $resource_id)"
done
```

**After each resource creation:**
- Verify with GET request (check `provisioningState == "Succeeded"`)
- Capture resource ID
- Update `state.json.resources` with `{name, id, type, status, region}`
- Apply diagnostic settings to route logs to Log Analytics
- If creation fails after retries, log error and offer retry/skip/rollback

### Step 4: Archetype-Specific Provisioning

Read the archetype resource map and provision additional resources:

| Archetype | Additional Resources |
|-----------|---------------------|
| RAG | AI Search, Cosmos DB (NoSQL), App Service, Function App, Content Safety, Front Door |
| Conversational | AI Foundry Project, Cosmos DB (NoSQL), App Service, Function App, Logic App, Content Safety, Front Door |
| Doc Intelligence | AI Document Intelligence, AI Search, Cosmos DB (NoSQL), Function App |
| Predictive ML | Azure ML Workspace, Function App, (Cosmos DB optional) |
| Knowledge Graph | Graph DB (Cosmos Gremlin OR Neo4j), AI Search, Cosmos DB (NoSQL), App Service |
| Voice/Text | Cosmos DB (NoSQL + optional provisioned), Function App, Logic App |
| Multi-Agent | AI Foundry Project, AI Search, Cosmos DB (NoSQL), App Service, Function App, Content Safety |
| Computer Vision | Azure ML Workspace, Container Registry, Function App, Cosmos DB |

### Step 5: Deploy AI Models

Deploy models to the AI Services account:

```bash
# Deploy primary LLM
# Read model config from state.json.requirements.ai.primary_model
PUT https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{ai}/deployments/{deployment_name}?api-version=2024-10-01

# Deploy embedding model (if required)
# Read from state.json.requirements.ai.embedding_model
PUT ...same pattern...
```

Verify deployment status. Capacity (TPM) from state config.

### Step 6: Configure Key Vault

Store all connection strings and keys in Key Vault. **Never print keys to console.**

```bash
# Pattern: read key from resource, immediately store in Key Vault
AI_KEY=$(az cognitiveservices account keys list --name flk-{app}-ai-dev --resource-group flk-{app}-dev-rg --query key1 -o tsv)
az keyvault secret set --vault-name flk-{app}-kv-dev --name "ai-services-key" --value "$AI_KEY" > /dev/null

# Repeat for each resource that has keys/connection strings:
# - ai-services-key
# - ai-services-endpoint
# - cosmos-db-connection-string
# - cosmos-db-key
# - ai-search-admin-key
# - ai-search-endpoint
# - storage-connection-string
# - storage-account-key
```

Set Key Vault access policy for Managed Identity:
```bash
az keyvault set-policy --name flk-{app}-kv-dev \
  --object-id {managed-identity-principal-id} \
  --secret-permissions get list
```

### Step 7: RBAC Setup (via REST API)

Assign roles to Managed Identity on all resources. **Always use the REST API PUT method** — `az role assignment create` can fail on certain subscriptions (known issue with Fluke AI subscription).

| Resource | Role | Role Definition ID | Purpose |
|----------|------|--------------------|---------|
| AI Services | Cognitive Services OpenAI User | `5e0bd9bd-7b93-4f28-af87-19fc36ad61bd` | Model inference |
| AI Search | Search Index Data Contributor | `8ebe5a00-799e-43f5-93ac-243d3dce84a7` | Index read/write |
| Cosmos DB | Cosmos DB Built-in Data Contributor | `00000000-0000-0000-0000-000000000002` | Data read/write |
| Storage | Storage Blob Data Contributor | `ba92f5b4-2d11-453d-a403-e96b0029c9fe` | Blob read/write |
| Key Vault | Key Vault Secrets User | `4633458b-17de-408a-b874-0445c86b69e6` | Secret read |
| App Service | Website Contributor | `de139f84-1756-47ae-9be6-808fbbe84772` | Deploy code |
| Function App | Website Contributor | `de139f84-1756-47ae-9be6-808fbbe84772` | Deploy code |
| Log Analytics | Log Analytics Reader | `73c42c96-874c-492b-b04d-ab87d138a893` | Read logs |

```bash
# RBAC via REST API PUT (idempotent — safe to re-run)
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)
MI_PRINCIPAL_ID="{managed-identity-principal-id}"

# Pattern: create role assignment for each resource
assign_role() {
    local SCOPE="$1"
    local ROLE_DEF_ID="$2"
    local ASSIGNMENT_ID=$(python3 -c "import uuid; print(uuid.uuid4())")

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X PUT \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        "https://management.azure.com${SCOPE}/providers/Microsoft.Authorization/roleAssignments/${ASSIGNMENT_ID}?api-version=2022-04-01" \
        -d "{
            \"properties\": {
                \"roleDefinitionId\": \"${SCOPE}/providers/Microsoft.Authorization/roleDefinitions/${ROLE_DEF_ID}\",
                \"principalId\": \"${MI_PRINCIPAL_ID}\",
                \"principalType\": \"ServicePrincipal\"
            }
        }")

    if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
        echo "  PASS: Role assigned (HTTP $HTTP_CODE)"
    elif [ "$HTTP_CODE" = "409" ]; then
        echo "  SKIP: Role already assigned (HTTP 409 — idempotent)"
    else
        echo "  FAIL: HTTP $HTTP_CODE — check permissions"
        return 1
    fi
}

# Assign all roles
echo "Assigning RBAC roles..."
assign_role "/subscriptions/{ai_sub}/resourceGroups/{rg}/providers/Microsoft.CognitiveServices/accounts/{ai}" "5e0bd9bd-7b93-4f28-af87-19fc36ad61bd"
assign_role "/subscriptions/{ai_sub}/resourceGroups/{rg}/providers/Microsoft.Search/searchServices/{search}" "8ebe5a00-799e-43f5-93ac-243d3dce84a7"
assign_role "/subscriptions/{ai_sub}/resourceGroups/{rg}/providers/Microsoft.DocumentDB/databaseAccounts/{cosmos}" "00000000-0000-0000-0000-000000000002"
assign_role "/subscriptions/{ai_sub}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{storage}" "ba92f5b4-2d11-453d-a403-e96b0029c9fe"
assign_role "/subscriptions/{ai_sub}/resourceGroups/{rg}/providers/Microsoft.KeyVault/vaults/{kv}" "4633458b-17de-408a-b874-0445c86b69e6"
# ... repeat for each resource
```

**Cross-subscription RBAC** (for split subscription model):
```bash
# When UBI subscription resources need access from AI subscription identity
# The MI from AI sub needs roles on UBI sub resources (e.g., ADLS, Databricks)
# Requires Owner or User Access Administrator on the UBI subscription

# Verify cross-sub access first
UBI_SUB="52a1d076-bbbf-422a-9bf7-95d61247be4b"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer $TOKEN" \
    "https://management.azure.com/subscriptions/${UBI_SUB}?api-version=2022-12-01")
if [ "$HTTP_CODE" != "200" ]; then
    echo "ERROR: Cannot access UBI subscription. Request access from subscription Owner."
    echo "Required: User Access Administrator role on subscription ${UBI_SUB}"
fi

# Assign Storage Blob Data Contributor on UBI ADLS
assign_role "/subscriptions/${UBI_SUB}/resourceGroups/flkubi-rg/providers/Microsoft.Storage/storageAccounts/flkubiadlsdev" "ba92f5b4-2d11-453d-a403-e96b0029c9fe"
```

### Step 8: Multi-Region Setup

Read regions from `state.json.regions`:

**Cosmos DB geo-replication:**
```bash
# Add secondary region to existing Cosmos account
az cosmosdb update --name flk-{app}-cosmosdb-dev \
  --resource-group flk-{app}-dev-rg \
  --locations regionName={primary} failoverPriority=0 \
  --locations regionName={secondary} failoverPriority=1
```

**ADLS GRS:** Already configured during creation (SKU: Standard_GRS).

**Front Door (if applicable):**
```bash
# Create Front Door profile + endpoint + origin group + route
# See infra-templates.md for full REST API payloads
```

### Step 9: Generate Bicep Templates

After all resources are provisioned, generate declarative Bicep templates from the actual deployed state:

```
project-directory/
├── infra/
│   ├── main.bicep              ← orchestrator module
│   ├── parameters.dev.json     ← dev parameter file
│   ├── parameters.qa.json      ← qa parameter file (same structure, different values)
│   ├── parameters.prod.json    ← prod parameter file
│   └── modules/
│       ├── ai-services.bicep
│       ├── ai-search.bicep
│       ├── cosmos-db.bicep
│       ├── app-service.bicep
│       ├── function-app.bicep
│       ├── key-vault.bicep
│       ├── storage.bicep
│       ├── log-analytics.bicep
│       ├── managed-identity.bicep
│       ├── diagnostics.bicep       ← diagnostic settings module
│       ├── private-endpoints.bicep ← QA/Prod only
│       ├── budget-alert.bicep      ← cost management
│       └── [archetype-specific].bicep
```

**Read** `ai-ucb/infra-templates.md` for Bicep module templates.

**Private Endpoint module** (QA/Prod only — Dev uses public endpoints per anti-pattern #7):

```bicep
// modules/private-endpoints.bicep
@description('Target resource ID to create private endpoint for')
param targetResourceId string

@description('Private endpoint subnet ID')
param subnetId string

@description('Group IDs for the private link (e.g., "openai", "searchService", "blob")')
param groupIds array

@description('Environment')
param env string

param location string = resourceGroup().location
param tags object = {}

var resourceName = last(split(targetResourceId, '/'))

resource privateEndpoint 'Microsoft.Network/privateEndpoints@2023-11-01' = {
  name: '${resourceName}-pe-${env}'
  location: location
  tags: tags
  properties: {
    subnet: { id: subnetId }
    privateLinkServiceConnections: [
      {
        name: '${resourceName}-plsc'
        properties: {
          privateLinkServiceId: targetResourceId
          groupIds: groupIds
        }
      }
    ]
  }
}

resource privateDnsZoneGroup 'Microsoft.Network/privateEndpoints/privateDnsZoneGroups@2023-11-01' = {
  parent: privateEndpoint
  name: 'default'
  properties: {
    privateDnsZoneConfigs: [for groupId in groupIds: {
      name: groupId
      properties: {
        privateDnsZoneId: resourceId('Microsoft.Network/privateDnsZones', 'privatelink.${groupId}.core.windows.net')
      }
    }]
  }
}
```

**Budget Alert module** (applied to all environments):

```bicep
// modules/budget-alert.bicep
@description('Monthly budget amount in USD')
param budgetAmount int

@description('Alert email addresses')
param alertEmails array

param appSlug string
param env string

resource budget 'Microsoft.Consumption/budgets@2023-11-01' = {
  name: 'budget-${appSlug}-${env}'
  properties: {
    category: 'Cost'
    amount: budgetAmount
    timeGrain: 'Monthly'
    timePeriod: {
      startDate: '${utcNow('yyyy-MM')}-01'
    }
    filter: {
      tags: {
        name: 'Project'
        values: [appSlug]
      }
    }
    notifications: {
      actual80: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 80
        contactEmails: alertEmails
        thresholdType: 'Actual'
      }
      forecast100: {
        enabled: true
        operator: 'GreaterThanOrEqualTo'
        threshold: 100
        contactEmails: alertEmails
        thresholdType: 'Forecasted'
      }
    }
  }
}
```

**Environment-specific parameter differences:**

| Parameter | Dev | QA | Prod |
|-----------|-----|-----|------|
| `appServiceSku` | `B1` | `S1` | `P1v3` |
| `cosmosThroughput` | `serverless` | `autoscale-1000` | `autoscale-4000` |
| `searchReplicas` | `1` | `1` | `2` |
| `searchPartitions` | `1` | `1` | `2` |
| `enablePrivateEndpoints` | `false` | `true` | `true` |
| `enableBudgetAlerts` | `true` | `true` | `true` |
| `budgetAmount` | `1000` | `1500` | `3000` |
| `enableDiagnostics` | `true` | `true` | `true` |
| `enableGeoReplication` | `false` | `false` | `true` |

### Step 10: Generate Azure DevOps Pipeline YAML

```yaml
# infra/azure-pipelines-infra.yml
trigger:
  branches:
    include: [main]
  paths:
    include: [infra/*]

parameters:
  - name: environment
    type: string
    default: dev
    values: [dev, qa, prod]

stages:
  - stage: Deploy_${{ parameters.environment }}
    jobs:
      - job: DeployInfra
        pool:
          vmImage: ubuntu-latest
        steps:
          - task: AzureCLI@2
            inputs:
              azureSubscription: '{service-connection}'
              scriptType: bash
              scriptLocation: inlineScript
              inlineScript: |
                az deployment group create \
                  --resource-group flk-{app}-${{ parameters.environment }}-rg \
                  --template-file infra/main.bicep \
                  --parameters @infra/parameters.${{ parameters.environment }}.json
```

### Step 11: Provisioning Report and Gate

Present the provisioning report:

```
INFRASTRUCTURE REPORT — {project_name}
═══════════════════════════════════════

Resources Provisioned: {count}
Region: {primary} (+ {secondary} failover)
Subscription: {model}

| # | Resource | Type | Status | Region | Resource ID |
|---|----------|------|--------|--------|-------------|
| 1 | flk-{app}-dev-rg | Resource Group | Provisioned | {primary} | /subscriptions/... |
| 2 | flk-{app}-ai-dev | AI Services | Provisioned | {primary} | /subscriptions/... |
| ... | ... | ... | ... | ... | ... |

AI Model Deployments:
| Model | Deployment | Capacity | Status |
|-------|-----------|----------|--------|
| gpt-4.1 | gpt-4.1 | 250K TPM | Deployed |
| text-embedding-3-large | text-embedding-3-large | 250K TPM | Deployed |

Key Vault Secrets: {count} secrets stored
RBAC: {count} role assignments created
Multi-Region: Cosmos DB geo-replicated to {secondary}

Bicep Templates: Saved to {project_dir}/infra/
DevOps Pipeline: Saved to {project_dir}/infra/azure-pipelines-infra.yml
```

Update state:
- `phases.infra = "completed"`
- `resources` populated with all resource IDs
- `artifacts.bicep_path`, `artifacts.pipeline_path`

Append to PROJECT_MEMORY.md.

Ask:
> **GATE: Phase 1 Infrastructure complete.** {count} resources provisioned. Bicep templates generated. Shall I proceed to Phase 2 (Data Pipelines)?

---

## Infrastructure Anti-Patterns (NEVER Do These)

1. **NEVER provision without checking if the resource group already exists.** Use GET first. If it exists with different tags, warn the user.
2. **NEVER hard-code subscription IDs in Bicep templates.** Use parameters. The templates must work for dev/qa/prod promotion.
3. **NEVER print API keys or connection strings to the console.** Pipe them directly to Key Vault or `/dev/null`.
4. **NEVER create resources with default names.** Every resource must follow the `flk-{app}-{type}-{env}` convention.
5. **NEVER skip the Managed Identity.** All service-to-service auth uses MI, not shared keys.
6. **NEVER provision Prod-tier SKUs in Dev.** Use B1 (not P1v3) for App Service, serverless (not provisioned) for Cosmos DB, etc.
7. **NEVER create networking resources (VNets, NSGs, private endpoints) in Dev.** Dev uses public endpoints. Private networking is for QA/Prod Bicep templates only.
8. **NEVER skip resource verification.** After every PUT, do a GET to confirm `provisioningState == "Succeeded"`.

## Rollback Procedure

When provisioning fails partway, offer a clean rollback:

```bash
rollback_provisioning() {
    local RG="$1"
    local RESOURCES_JSON="$2"  # List of successfully provisioned resource IDs

    echo "=== ROLLBACK PLAN ==="
    echo "Resource group: $RG"

    # Option A: Delete entire resource group (if newly created for this project)
    echo "Option A: Delete resource group $RG (removes ALL resources in it)"
    echo "  az group delete --name $RG --yes --no-wait"

    # Option B: Delete individual resources (if RG was pre-existing)
    echo "Option B: Delete individual resources"
    # Delete in reverse dependency order
    python3 -c "
import json
resources = json.loads('$RESOURCES_JSON')
# Reverse dependency order: deployments first, then services, then RG
for r in reversed(resources):
    print(f'  az resource delete --ids {r[\"id\"]}')
"

    echo ""
    echo "Choose: (A) Delete resource group / (B) Delete individual resources / (C) Keep and retry"
}
```

**Rollback rules:**
- If RG was newly created by this phase → Option A (clean delete)
- If RG pre-existed → Option B only (don't delete other team's resources)
- Always log what was rolled back in PROJECT_MEMORY.md
- After rollback, reset `phases.infra` to `pending` in state

## Error Recovery

| Error | Recovery |
|-------|---------|
| `QuotaExceeded` on AI model deployment | Try secondary region, reduce TPM capacity, or use different model. `az cognitiveservices usage list --name {ai} -g {rg}` to check current usage |
| `NameNotAvailable` on storage/cosmos | Append random 4-char suffix: `python3 -c "import secrets; print(secrets.token_hex(2))"` and retry |
| `AuthorizationFailed` | Check subscription access: `az account show`. If expired: `az login --tenant 0f634ac3-b39f-41a6-83ba-8f107876c692` |
| `AuthorizationFailed` on RBAC | Use REST API PUT instead of `az role assignment create` (known Fluke AI sub issue). See Step 7 |
| `ResourceGroupNotFound` (UBI sub) | For split model, verify UBI subscription accessible: `az account list --query "[?id=='52a1d076-bbbf-422a-9bf7-95d61247be4b']"` |
| `SkuNotAvailable` in region | Try secondary region, or `az cognitiveservices account list-skus --kind OpenAI --location eastus2` |
| `429 TooManyRequests` | Built into `provision_resource()` — automatic retry with backoff |
| Partial provisioning (some succeeded, some failed) | Re-run Step 3 — `provision_resource()` is idempotent, skips existing healthy resources |
| Cross-subscription token expired | Refresh: `TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)` |
| Private endpoint DNS resolution fails | Verify private DNS zone exists and is linked to VNet |
| Budget alert not triggering | Check cost tag propagation (can take up to 24h) |
