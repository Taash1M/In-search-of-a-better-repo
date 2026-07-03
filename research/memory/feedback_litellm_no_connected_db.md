---
name: feedback-litellm-no-connected-db
description: "LiteLLM \"No connected db\" error in config-only mode means wrong Bearer token, not a database/config issue. Each gateway has its own unique LITELLM_MASTER_KEY."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 95ada5d9-1811-49ee-8e73-8aace54fac80
---

"No connected db." (HTTP 400) from LiteLLM in config-only mode (no DATABASE_URL) means the Bearer token does not match that node's `LITELLM_MASTER_KEY`. It does NOT mean the config.yaml is missing, Docker is misconfigured, or there's a database problem.

**Why:** On 2026-05-17, all 4 nodes (0-3) returned this error during test traffic generation. We investigated Docker images, ACR tags, startup commands, and config files — all were correct. The root cause was using the POC gateway's master key (`flk-team-da6d8bfe...`) against nodes 0-3, which each have their own unique key. Unnecessarily restarted all 4 App Services chasing the wrong diagnosis.

**How to apply:**
1. When you see "No connected db." from any LiteLLM gateway, first check the Bearer token matches that specific node's `LITELLM_MASTER_KEY`.
2. Query the correct key: `az webapp config appsettings list --name <app> --resource-group flk-team-ai-enablement-rg --query "[?name=='LITELLM_MASTER_KEY'].value" -o tsv`
3. Do NOT restart App Services, rebuild Docker images, or investigate config.yaml — those are red herrings for this error.
4. Per-node key mapping is documented in [[Team AI Enablement (Claude Code for Team)]].
