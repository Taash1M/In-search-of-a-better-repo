---
name: azure-ai-foundry-config
description: "Team Azure AI Foundry config — flk-team-ai-enablement-ai (East US 2), model TPM allotments, AAD+legacy auth, AWS Bedrock alt provider, diagnostic logging, usage-ETL VM scripts + MI, billing"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

# Azure AI Foundry Configuration (Team — switched 2026-03-26)

- **Resource**: `flk-team-ai-enablement-ai` (East US 2)
- **Settings file**: `<USER_HOME>/.claude\settings.json` (env section)
- **Models**: opus (750 TPM), sonnet (1,625 TPM), haiku (100 TPM), **fable-5** (1,000 TPM shared + 250 Node0 + 250 Node1), **opus-4-8** (1,000 TPM), codex (5,008 TPM via node-0 gateway), gpt-5.5 (5,000 TPM), text-embedding-3-small (120 TPM Standard)
- **Auth (legacy)**: `ANTHROPIC_FOUNDRY_API_KEY` + `CLAUDE_CODE_USE_FOUNDRY=1` — Taashi's CLI on Key2 (`9mhth2AX...`), Key1 regenerated 2026-06-08
- **Auth (live for 4+ users)**: AAD via `az login` (no API key) — populates objectId in diagnostic logs
- **Alt provider (2026-06-19)**: AWS Bedrock us-east-2, settings at `settings.bedrock.json`, swap with `cp ~/.claude/settings.bedrock.json ~/.claude/settings.json`
- **Diagnostic logging**: `RequestResponse` category enabled on AI Services (2026-04-24), NDJSON → `flkaienablement` storage
- **ETL**: ~2,100 lines (Sonnet safety + per-user join + token identity), processes LiteLLM + diagnostic + content logs, `dim_aad_users` 57 rows. Detail + Delta paths in `project_llm_usage_tracking.md` (Bronze=`llm_usage_raw`)
- **VM scripts**: `<VM_HOME>/{llm_usage_etl.py, sync_aad_users.py, infra_health_check.py, query_usage.py}` (auto-deployed by wrapper from `_scripts/` blob prefix)
- **Canonical blob script**: `_scripts/llm_usage_etl_v2.py` (wrapper deploys from here); backup: `scripts/llm_usage_etl_v3_sonnet.py`
- **VM Managed Identity**: SystemAssigned MI (`3dde942e-1f7a-4d87-8040-cb15d246eb4c`), Storage Blob Data Contributor on `flkaienablement` (2026-05-05)
- **VM Azure CLI**: v2.85.0 installed (2026-04-27)
- Billing: Fluke AI ML Technology subscription (Azure Marketplace)

Related: [[llm-gateway-usage-tracking]] · [[team-ai-enablement]] · [[claude-code-env-override]]
