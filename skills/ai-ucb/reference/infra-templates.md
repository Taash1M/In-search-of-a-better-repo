# AI Use Case Builder - Infrastructure Templates

Azure CLI REST API commands and Bicep module templates for resource provisioning. Used by the Infrastructure sub-skill (`ai-ucb-infra.md`) during Phase 1.

**Usage:** Read the relevant section for each resource type. Replace `{app}`, `{env}`, `{region}`, `{sub}`, `{rg}` with values from `ai-ucb-state.json`.

---

## Common Variables

```bash
SUB_AI="77a0108c-5a42-42e7-8b7a-79367dbfc6a1"
SUB_UBI="52a1d076-bbbf-422a-9bf7-95d61247be4b"
TOKEN=$(az account get-access-token --resource https://management.azure.com --query accessToken -o tsv)
API="https://management.azure.com"
APP="{app-slug}"
ENV="dev"
RG="flk-${APP}-${ENV}-rg"
REGION="eastus2"
REGION2="centralus"
TAGS='{"Project":"{project}","Archetype":"{archetype}","Environment":"dev","Owner":"taashi.manyanga@fluke.com","CostCenter":"{cc}","CreatedBy":"ai-use-case-builder"}'
```

---

## Resource Group

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG?api-version=2024-03-01" \
  -d "{\"location\":\"$REGION\",\"tags\":$TAGS}"
```

**Bicep:**
```bicep
targetScope = 'subscription'

param location string
param appName string
param env string
param tags object

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: 'flk-${appName}-${env}-rg'
  location: location
  tags: tags
}
```

---

## User-Assigned Managed Identity

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/flk-${APP}-mi-${ENV}?api-version=2023-01-31" \
  -d "{\"location\":\"$REGION\",\"tags\":$TAGS}"
```

**Bicep:**
```bicep
param location string
param appName string
param env string
param tags object

resource mi 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'flk-${appName}-mi-${env}'
  location: location
  tags: tags
}

output principalId string = mi.properties.principalId
output clientId string = mi.properties.clientId
output resourceId string = mi.id
```

---

## Log Analytics Workspace

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/flk-${APP}-logs-${ENV}?api-version=2023-09-01" \
  -d "{\"location\":\"$REGION\",\"properties\":{\"sku\":{\"name\":\"PerGB2018\"},\"retentionInDays\":30},\"tags\":$TAGS}"
```

**Bicep:**
```bicep
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: 'flk-${appName}-logs-${env}'
  location: location
  tags: tags
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 30
  }
}

output workspaceId string = logAnalytics.id
```

---

## Application Insights

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.Insights/components/flk-${APP}-insights-${ENV}?api-version=2020-02-02" \
  -d "{\"location\":\"$REGION\",\"kind\":\"web\",\"properties\":{\"Application_Type\":\"web\",\"WorkspaceResourceId\":\"/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.OperationalInsights/workspaces/flk-${APP}-logs-${ENV}\"},\"tags\":$TAGS}"
```

**Bicep:**
```bicep
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'flk-${appName}-insights-${env}'
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

output instrumentationKey string = appInsights.properties.InstrumentationKey
output connectionString string = appInsights.properties.ConnectionString
```

---

## Key Vault

**CLI:**
```bash
TENANT="0f634ac3-b39f-41a6-83ba-8f107876c692"
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.KeyVault/vaults/flk-${APP}-kv-${ENV}?api-version=2023-07-01" \
  -d "{\"location\":\"$REGION\",\"properties\":{\"tenantId\":\"$TENANT\",\"sku\":{\"family\":\"A\",\"name\":\"standard\"},\"enableRbacAuthorization\":true,\"enableSoftDelete\":true,\"softDeleteRetentionInDays\":90},\"tags\":$TAGS}"
```

**Bicep:**
```bicep
param tenantId string = '0f634ac3-b39f-41a6-83ba-8f107876c692'

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'flk-${appName}-kv-${env}'
  location: location
  tags: tags
  properties: {
    tenantId: tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
  }
}
```

---

## Storage Account (ADLS Gen2)

**Naming:** Storage accounts must be 3-24 lowercase alphanumeric only (no hyphens).
Convention: `flk{app}storage{env}` (remove hyphens from app slug).

**CLI:**
```bash
STORAGE_NAME="flk${APP//[-]/}storage${ENV}"
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/${STORAGE_NAME}?api-version=2023-05-01" \
  -d "{\"location\":\"$REGION\",\"sku\":{\"name\":\"Standard_GRS\"},\"kind\":\"StorageV2\",\"properties\":{\"isHnsEnabled\":true,\"minimumTlsVersion\":\"TLS1_2\",\"allowBlobPublicAccess\":false},\"tags\":$TAGS}"
```

**Bicep:**
```bicep
var storageName = replace('flk${appName}storage${env}', '-', '')

resource storage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: storageName
  location: location
  tags: tags
  sku: { name: 'Standard_GRS' }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
  }
}
```

---

## Azure AI Services (Cognitive Services)

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/flk-${APP}-ai-${ENV}?api-version=2024-10-01" \
  -d "{\"location\":\"$REGION\",\"sku\":{\"name\":\"S0\"},\"kind\":\"AIServices\",\"properties\":{\"customSubDomainName\":\"flk-${APP}-ai-${ENV}\",\"publicNetworkAccess\":\"Enabled\"},\"tags\":$TAGS}"
```

**Bicep:**
```bicep
resource aiServices 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: 'flk-${appName}-ai-${env}'
  location: location
  tags: tags
  sku: { name: 'S0' }
  kind: 'AIServices'
  properties: {
    customSubDomainName: 'flk-${appName}-ai-${env}'
    publicNetworkAccess: 'Enabled'
  }
}
```

---

## AI Model Deployment

**CLI (deploy to existing AI Services account):**
```bash
# LLM deployment
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/flk-${APP}-ai-${ENV}/deployments/{deployment_name}?api-version=2024-10-01" \
  -d "{\"sku\":{\"name\":\"GlobalStandard\",\"capacity\":{tpm}},\"properties\":{\"model\":{\"format\":\"OpenAI\",\"name\":\"{model_id}\",\"version\":\"{version}\"}}}"

# Embedding deployment
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/flk-${APP}-ai-${ENV}/deployments/text-embedding-3-large?api-version=2024-10-01" \
  -d "{\"sku\":{\"name\":\"GlobalStandard\",\"capacity\":250},\"properties\":{\"model\":{\"format\":\"OpenAI\",\"name\":\"text-embedding-3-large\",\"version\":\"1\"}}}"
```

---

## Azure AI Search

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.Search/searchServices/flk-${APP}-search-${ENV}?api-version=2024-06-01-preview" \
  -d "{\"location\":\"$REGION\",\"sku\":{\"name\":\"standard\"},\"properties\":{\"replicaCount\":1,\"partitionCount\":1,\"hostingMode\":\"default\",\"semanticSearch\":\"standard\"},\"tags\":$TAGS}"
```

**Bicep:**
```bicep
resource aiSearch 'Microsoft.Search/searchServices@2024-06-01-preview' = {
  name: 'flk-${appName}-search-${env}'
  location: location
  tags: tags
  sku: { name: 'standard' }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
    semanticSearch: 'standard'
  }
}
```

---

## Cosmos DB (NoSQL — Serverless)

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.DocumentDB/databaseAccounts/flk-${APP}-cosmosdb-${ENV}?api-version=2024-05-15" \
  -d "{\"location\":\"$REGION\",\"properties\":{\"locations\":[{\"locationName\":\"$REGION\",\"failoverPriority\":0}],\"databaseAccountOfferType\":\"Standard\",\"capabilities\":[{\"name\":\"EnableServerless\"}],\"consistencyPolicy\":{\"defaultConsistencyLevel\":\"Session\"}},\"tags\":$TAGS}"
```

**Bicep:**
```bicep
resource cosmosDb 'Microsoft.DocumentDB/databaseAccounts@2024-05-15' = {
  name: 'flk-${appName}-cosmosdb-${env}'
  location: location
  tags: tags
  properties: {
    locations: [{ locationName: location, failoverPriority: 0 }]
    databaseAccountOfferType: 'Standard'
    capabilities: [{ name: 'EnableServerless' }]
    consistencyPolicy: { defaultConsistencyLevel: 'Session' }
  }
}
```

**Add geo-replication (multi-region):**
```bash
# Update to add secondary region
curl -s -X PUT ... \
  -d "{...\"locations\":[{\"locationName\":\"$REGION\",\"failoverPriority\":0},{\"locationName\":\"$REGION2\",\"failoverPriority\":1}]...}"
```

---

## Cosmos DB (Gremlin API — Knowledge Graph)

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.DocumentDB/databaseAccounts/flk-${APP}-graphdb-${ENV}?api-version=2024-05-15" \
  -d "{\"location\":\"$REGION\",\"properties\":{\"locations\":[{\"locationName\":\"$REGION\",\"failoverPriority\":0}],\"databaseAccountOfferType\":\"Standard\",\"capabilities\":[{\"name\":\"EnableGremlin\"}],\"consistencyPolicy\":{\"defaultConsistencyLevel\":\"Session\"}},\"tags\":$TAGS}"
```

---

## App Service (Linux)

**CLI (Plan + Web App):**
```bash
# App Service Plan
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.Web/serverfarms/flk-${APP}-plan-${ENV}?api-version=2023-12-01" \
  -d "{\"location\":\"$REGION\",\"sku\":{\"name\":\"B1\",\"tier\":\"Basic\"},\"kind\":\"linux\",\"properties\":{\"reserved\":true},\"tags\":$TAGS}"

# Web App
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.Web/sites/flk-${APP}-webapp-${ENV}?api-version=2023-12-01" \
  -d "{\"location\":\"$REGION\",\"properties\":{\"serverFarmId\":\"/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.Web/serverfarms/flk-${APP}-plan-${ENV}\",\"siteConfig\":{\"linuxFxVersion\":\"PYTHON|3.12\",\"appSettings\":[{\"name\":\"KEY_VAULT_URL\",\"value\":\"https://flk-${APP}-kv-${ENV}.vault.azure.net/\"}]}},\"identity\":{\"type\":\"UserAssigned\",\"userAssignedIdentities\":{\"/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.ManagedIdentity/userAssignedIdentities/flk-${APP}-mi-${ENV}\":{}}},\"tags\":$TAGS}"
```

**Bicep:**
```bicep
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: 'flk-${appName}-plan-${env}'
  location: location
  tags: tags
  sku: { name: env == 'prod' ? 'P1v3' : 'B1' }
  kind: 'linux'
  properties: { reserved: true }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: 'flk-${appName}-webapp-${env}'
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${mi.id}': {} }
  }
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      appSettings: [
        { name: 'KEY_VAULT_URL', value: keyVault.properties.vaultUri }
      ]
    }
  }
}
```

---

## Function App (Flex Consumption)

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.Web/sites/flk-${APP}-funcapp-${ENV}?api-version=2023-12-01" \
  -d "{\"location\":\"$REGION\",\"kind\":\"functionapp,linux\",\"properties\":{\"siteConfig\":{\"linuxFxVersion\":\"PYTHON|3.12\"},\"functionAppConfig\":{\"runtime\":{\"name\":\"python\",\"version\":\"3.12\"},\"scaleAndConcurrency\":{\"maximumInstanceCount\":100,\"instanceMemoryMB\":2048},\"deployment\":{\"storage\":{\"type\":\"blobContainer\",\"value\":\"/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.Storage/storageAccounts/flk${APP//[-]/}storage${ENV}/blobServices/default/containers/function-releases\",\"authentication\":{\"type\":\"SystemAssignedIdentity\"}}}}},\"tags\":$TAGS}"
```

---

## Content Safety

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.CognitiveServices/accounts/flk-${APP}-safety-${ENV}?api-version=2024-10-01" \
  -d "{\"location\":\"$REGION\",\"sku\":{\"name\":\"S0\"},\"kind\":\"ContentSafety\",\"properties\":{\"customSubDomainName\":\"flk-${APP}-safety-${ENV}\"},\"tags\":$TAGS}"
```

---

## Azure Front Door (Standard)

**CLI:**
```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/subscriptions/$SUB_AI/resourceGroups/$RG/providers/Microsoft.Cdn/profiles/flk-${APP}-fd-${ENV}?api-version=2024-02-01" \
  -d "{\"location\":\"global\",\"sku\":{\"name\":\"Standard_AzureFrontDoor\"},\"tags\":$TAGS}"
```

---

## RBAC Role Assignment

**CLI:**
```bash
# Pattern: assign role to managed identity on a specific resource
ROLE_ID="{role-definition-id}"
PRINCIPAL_ID="{managed-identity-principal-id}"
SCOPE="{resource-id}"
ASSIGNMENT_ID=$(uuidgen)

curl -s -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  "$API/${SCOPE}/providers/Microsoft.Authorization/roleAssignments/${ASSIGNMENT_ID}?api-version=2022-04-01" \
  -d "{\"properties\":{\"roleDefinitionId\":\"/subscriptions/$SUB_AI/providers/Microsoft.Authorization/roleDefinitions/${ROLE_ID}\",\"principalId\":\"${PRINCIPAL_ID}\",\"principalType\":\"ServicePrincipal\"}}"
```

**Common Role Definition IDs:**

| Role | ID |
|------|----|
| Cognitive Services OpenAI User | `5e0bd9bd-7b93-4f28-af87-19fc36ad61bd` |
| Search Index Data Contributor | `8ebe5a00-799e-43f5-93ac-243d3dce84a7` |
| Cosmos DB Built-in Data Contributor | `00000000-0000-0000-0000-000000000002` |
| Storage Blob Data Contributor | `ba92f5b4-2d11-453d-a403-e96b0029c9fe` |
| Key Vault Secrets User | `4633458b-17de-408a-b874-0445c86b69e6` |
| Website Contributor | `de139f84-1756-47ae-9be6-808fbbe84772` |

---

## Naming Convention Rules

| Resource Type | Pattern | Max Length | Restrictions |
|---------------|---------|-----------|-------------|
| Resource Group | `flk-{app}-{env}-rg` | 90 | Alphanumeric, hyphens, underscores, periods |
| AI Services | `flk-{app}-ai-{env}` | 64 | Alphanumeric, hyphens |
| AI Search | `flk-{app}-search-{env}` | 60 | Lowercase, alphanumeric, hyphens |
| Cosmos DB | `flk-{app}-cosmosdb-{env}` | 44 | Lowercase, alphanumeric, hyphens |
| Storage Account | `flk{app}storage{env}` | 24 | Lowercase alphanumeric only (no hyphens!) |
| Key Vault | `flk-{app}-kv-{env}` | 24 | Alphanumeric, hyphens |
| App Service Plan | `flk-{app}-plan-{env}` | 40 | Alphanumeric, hyphens |
| Web App | `flk-{app}-webapp-{env}` | 60 | Alphanumeric, hyphens |
| Function App | `flk-{app}-funcapp-{env}` | 60 | Alphanumeric, hyphens |
| Log Analytics | `flk-{app}-logs-{env}` | 63 | Alphanumeric, hyphens |
| Managed Identity | `flk-{app}-mi-{env}` | 128 | Alphanumeric, hyphens, underscores |
| Front Door | `flk-{app}-fd-{env}` | 64 | Alphanumeric, hyphens |
| Content Safety | `flk-{app}-safety-{env}` | 64 | Alphanumeric, hyphens |

**NEVER exceed max length.** If `{app}` slug is long, truncate it (keep the first 10 chars + hash suffix).

---

## Tag Standards

All resources MUST have these tags:

| Tag | Value | Example |
|-----|-------|---------|
| Project | Project name from state.json | product-knowledge-bot |
| Archetype | Archetype from state.json | rag |
| Environment | dev / qa / prod | dev |
| Owner | User email | taashi.manyanga@fluke.com |
| CostCenter | Business cost center | TBD-at-discovery |
| CreatedBy | Always this value | ai-use-case-builder |
| CreatedDate | ISO 8601 date | 2026-03-12 |

---

## Infrastructure Template Anti-Patterns (NEVER Do These)

1. **NEVER use `az resource create` instead of the typed REST API.** The generic command doesn't support all properties. Always use the resource-specific PUT endpoint with the correct API version.
2. **NEVER hard-code the tenant ID in CLI commands.** Use the variable `$TENANT` — it must be parameterizable for multi-tenant scenarios.
3. **NEVER use `dependsOn` in Bicep when implicit dependencies exist.** If module B references module A's output, Bicep auto-infers the dependency. Explicit `dependsOn` hides the real dependency graph.
4. **NEVER put secrets in Bicep parameter files.** Use Key Vault references (`@Microsoft.KeyVault(SecretUri=...)`) or `@secure()` parameters.
5. **NEVER deploy storage accounts with `allowBlobPublicAccess: true`.** Always `false`. Public blob access is a security violation.
6. **NEVER skip `enableSoftDelete` on Key Vault.** Accidental deletion without soft delete means permanent secret loss. Always enable with 90-day retention.
7. **NEVER create AI Services without `customSubDomainName`.** Without it, you can't use Entra ID auth — only key-based auth. Always set it to match the resource name.

---

## main.bicep Template

```bicep
targetScope = 'resourceGroup'

@description('Application name slug')
param appName string

@description('Environment')
@allowed(['dev', 'qa', 'prod'])
param env string

@description('Primary region')
param location string

@description('Secondary region for geo-replication')
param secondaryLocation string = 'centralus'

@description('Tags applied to all resources')
param tags object

// Core modules (all archetypes)
module mi 'modules/managed-identity.bicep' = { name: 'mi', params: { appName: appName, env: env, location: location, tags: tags } }
module logs 'modules/log-analytics.bicep' = { name: 'logs', params: { appName: appName, env: env, location: location, tags: tags } }
module insights 'modules/app-insights.bicep' = { name: 'insights', params: { appName: appName, env: env, location: location, tags: tags, workspaceId: logs.outputs.workspaceId } }
module kv 'modules/key-vault.bicep' = { name: 'kv', params: { appName: appName, env: env, location: location, tags: tags } }
module storage 'modules/storage.bicep' = { name: 'storage', params: { appName: appName, env: env, location: location, tags: tags } }

// Archetype-specific modules added conditionally based on parameters
// (Discovery sub-skill generates the appropriate main.bicep per archetype)
```
