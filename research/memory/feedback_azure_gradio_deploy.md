---
name: feedback-azure-gradio-deploy
description: "Azure App Service deployment gotchas for Gradio apps — build timeouts, startup probes, lazy-init pattern"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 44d5fe90-7fa0-4075-b543-76e38e1574b4
---

Never deploy pre-built zips (>50MB) via `az webapp deploy` — the SCM endpoint 504s. Use source-only zip + `SCM_DO_BUILD_DURING_DEPLOYMENT=true`.

**Why:** Azure SCM upload endpoint has a ~60s internal timeout. The 67MB pre-built zip exceeds this. Source-only zip is 19KB and uploads instantly; Oryx builds server-side using pip cache.

**How to apply:**
- Always use `--async true` since the CLI also times out waiting for the Oryx build (~7-10 min for Gradio). Poll ARM API for `status=4`.
- Never create Azure AI/OpenAI clients at module import time — use lazy-init. The `DefaultAzureCredential` chain blocks for 30-60s probing IMDS/CLI/env, which can exceed the 230s warmup probe.
- Set `WEBSITES_CONTAINER_START_TIME_LIMIT=600` for Gradio apps (they're slow to load).
- Set `alwaysOn=true` to avoid cold starts for end users.
- If the app writes to Blob Storage (e.g. audit logs), the Managed Identity needs **Storage Blob Data Contributor** on the target container — assign via REST API (see [[feedback-rbac-rest-api]]).
- Make tunables (concurrency limits, tool rounds) env vars, not hardcoded — change via App Settings without redeploy.
