---
name: RBAC via REST API (not az CLI)
description: az role assignment create fails with MissingSubscription on Fluke AI subscription — always use REST API PUT for role assignments.
type: feedback
---

Use the REST API for Azure RBAC assignments on the Fluke AI ML Technology subscription (`77a0108c-...`), not `az role assignment create`.

**Why:** `az role assignment create --scope <resource-id>` returns `MissingSubscription` error even when the subscription is set and the resource exists. This is likely a PIM/tenant interaction bug. The REST API works reliably with the same scope string.

**How to apply:** When onboarding users to Azure AI Foundry:
1. Resolve email → OID: `az ad user show --id "user@fluke.com" --query "id" -o tsv`
2. Get token: `az account get-access-token --resource https://management.azure.com --query accessToken -o tsv`
3. PUT via REST: `https://management.azure.com{scope}/providers/Microsoft.Authorization/roleAssignments/{uuid}?api-version=2022-04-01`
4. Body: `{ "properties": { "roleDefinitionId": "...roleDefinitions/53ca6127-...", "principalId": "{OID}", "principalType": "User" } }`

Full onboarding script is in the deployment CLAUDE.md under "User Onboarding Process".
