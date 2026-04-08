---
name: Team AI Enablement (Claude Code for Team)
description: Claude Code deployment for 27 Fluke users across 4 nodes on Azure AI Foundry. 12 model deployments, LLM Gateway, Excel add-in onboarding. 3 new node2 users added 2026-04-07.
type: project
---

## Deployment Directory
`C:\Users\tmanyang\OneDrive - Fortive\AI\Claude code deployment\`

## Azure AI Foundry
- **Resource**: `flk-team-ai-enablement-ai` (East US 2)
- **Subscription**: Fluke AI ML Technology (`77a0108c-5a42-42e7-8b7a-79367dbfc6a1`)
- **Resource group**: `flk-team-ai-enablement-rg`
- **Base URL**: `https://flk-team-ai-enablement-ai.services.ai.azure.com/anthropic`
- **Auth**: API key via `ANTHROPIC_FOUNDRY_API_KEY` + `CLAUDE_CODE_USE_FOUNDRY=1`
- **API key header**: `x-api-key` (not `api-key`)
- **Key discovery**: Foundry project required before Anthropic deployments; api-version=2025-12-01 required

## Models
- `claude-opus-4-6` (750 TPM), `claude-sonnet-4-6` (1,625 TPM), `claude-haiku-4-5` (100 TPM)
- Plus 9 node-specific deployments (3 per model family, 250cap each)

## Users (27 total)
- node1 (5): Kevin Davison, Eshwari Mulpuru, Urvin Thakkar, Mihai Constantin-Pau, Rachel King
- node2 (8): Jd Giles, Richard Feng, Alex Chillman, Julian Knabe, Matt Markl, **Jim Moeller** (2026-04-07), **Peter Bergstrom** (2026-04-07), **John Erickson** (2026-04-07)
- node3 (6): Vineet Thuvara, Steven Moore, Taashi Manyanga, Daniel Pouley, Azra Jabeen, Sean Sparks
- node4 (12, L1 Excel): Parker Burke, Jay Hack, Claire Hu Weber, Kathya Kalinine, Katie Marquardt, Neal Nowick, Sue-Ann Prentice, Kathryn Sweers + Alex Chillman, Azra Jabeen, Steven Moore, Vineet Thuvara

### New Users Added 2026-04-07
| User | Email | Node | Settings File |
|------|-------|------|---------------|
| Jim Moeller | jim.moeller@fluke.com | node2 | `user-config/settings_jim_moeller_node2.json` |
| Peter Bergstrom | peter.bergstrom@fluke.com | node2 | `user-config/settings_peter_bergstrom_node2.json` |
| John Erickson | john.erickson@fluke.com | node2 | `user-config/settings_john_erickson_node2.json` |

Settings JSONs generated. Onboarding email DOCX created (2026-04-07): `user-comms/Email_ClaudeCode_node2_onboarding_jim_peter_john.docx` (CLI setup + Excel gateway credentials, references attached Quick Start Guide). RBAC role assignment status unknown — verify before sending credentials. User list file updated at `user-comms/list of users to be granted access.txt` (18 users total).

## Node 4 (POC gateway renamed for Excel add-in users)
- **Gateway URL**: `https://flk-team-ai-llm-gateway.azurewebsites.net`
- **Token**: `flk-team-da6d8bfe-de40-49fc-8e69-6987f7b6a462`
- **Routes to**: shared model deployments (not node-specific)
- **Training doc**: `docs/Training/Claude_for_Excel_Quick_Start_Guide_v3.docx`

## User Onboarding (RBAC)
- **Role**: Azure AI User (`53ca6127-db72-4b80-b1b0-d745d6d5456d`) on AI Services resource
- **Bug**: `az role assignment create --scope` returns `MissingSubscription` error on this subscription
- **Workaround**: Use REST API (`PUT .../Microsoft.Authorization/roleAssignments/{uuid}?api-version=2022-04-01`)
- **Steps**: (1) resolve email to OID via `az ad user show`, (2) get mgmt token, (3) PUT role assignment via REST, (4) provide gateway credentials
- **Full script**: in `CLAUDE.md` under "User Onboarding Process"

## LLM Gateway Usage Tracking
See [project_llm_usage_tracking.md](project_llm_usage_tracking.md). DuckDB on VM (`llm-usage-duckdb-vm`, Standard_B2ms, ~$5.27/mo), 12h cron schedule. All 4 gateway nodes on v5 in `flkdockerregistry` ACR.

## Documents
DeploymentPlan, EnterpriseArchitect, EndUserConfigGuide, per-node credential emails, Excel Quick Start Guide v3 (all DOCX). Memory: `CLAUDE.md` in deployment dir.
