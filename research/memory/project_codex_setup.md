---
name: project-codex-setup
description: "OpenAI Codex Desktop setup on Azure AI Foundry — config, known bugs, workarounds"
metadata: 
  node_type: memory
  type: project
  originSessionId: ffc03abc-31f3-40f0-879c-68155eaa6ff8
---

# Codex Desktop on Azure AI Foundry

**Project folder**: `<USER_HOME>/OneDrive - <ORG>\Codex\`
**Config file**: `<USER_HOME>/.codex\config.toml`
**Skills copied**: 33 skills in `Codex\skills\` (4 superpowers, 5 UBI, 18 AI, 6 beautification) with per-category READMEs

## Working Config (2026-05-17)

```toml
model = "gpt-5.5"
model_provider = "azure"
model_reasoning_effort = "medium"

[model_providers.azure]
name = "Azure OpenAI"
base_url = "https://flk-team-ai-enablement-ai.services.ai.azure.com/api/projects/claude-code-enablement/openai/v1"
env_key = "AZURE_OPENAI_API_KEY"
wire_api = "responses"

[windows]
sandbox = "unelevated"
```

## Key Setup Facts

- **Active model**: `gpt-5.5` (switched from `gpt-5.3-codex-node-0` — same bug on both, kept 5.5)
- **Deployment name**: must match Azure exactly (case-sensitive)
- **API key**: stored as user environment variable `AZURE_OPENAI_API_KEY` (never in config.toml)
- **Set env var**: `[System.Environment]::SetEnvironmentVariable("AZURE_OPENAI_API_KEY", "<key>", "User")` in PowerShell as <USER> (not <ADMIN_USER>)
- **base_url**: must end with `/openai/v1` — strip `/responses` from the Azure Target URI
- **Section name**: `[model_providers.azure]` NOT `[providers.azure]` (wrong name = "provider not found" error)
- **wire_api**: must be `"responses"` — `"chat"` is deprecated and rejected
- **Session directories**: Codex expects `~/.codex/sessions/YYYY/MM/DD/` to exist (create with `New-Item -ItemType Directory -Force`)
- **Plugins**: Documents/Spreadsheets/Presentations plugins inject tool schemas that cause `invalid_payload` — removed from config. Codex may re-add marketplace entries on restart (harmless as long as plugins stay off)
- **Restart required**: fully quit and reopen Codex Desktop after any config or env var change
- **Final clean state**: config has no plugin or marketplace entries; Codex re-adds `openai-bundled` marketplace on restart (expected, harmless)

## Known Bug — Azure Tool Sessions (GitHub #16916)

**Status**: OPEN as of 2026-05-17
**Symptom**: Basic text prompts work. File/tool tasks fail with `invalid_payload: The provided data does not match the expected schema`
**Root cause**: Codex sends Azure-incompatible continuation payloads in `/responses` API after the first tool call
**Workarounds attempted**: (1) query_params with api-version — rejected (not allowed with /v1 path), (2) switched gpt-5.3-codex to gpt-5.5 — same error (model-independent), (3) disabled plugins — helped with first error but tool sessions still broken
**Only known fix**: Local payload-patching proxy (no public config shared)
**Current usage**: Text/chat only — works fine on gpt-5.5
**Tracking**: https://github.com/openai/codex/issues/16916 (also #15584, #14695)

**Why:** Azure's Responses API is stricter about payload schemas than OpenAI's direct API. Codex generates tool round-trip payloads that OpenAI accepts but Azure rejects.

**How to apply:** Use Codex for text-only prompts through Azure. For file/tool-heavy tasks, use [[project-ai-enablement]] Claude Code instead. Check #16916 periodically for a fix.

## Errors Encountered & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `Model provider 'azure' not found` | `[providers.azure]` instead of `[model_providers.azure]` | Rename section |
| `wire_api = "chat" is no longer supported` | Deprecated wire API | Use `wire_api = "responses"` |
| `failed to resolve rollout path` (os error 3) | Missing session date directory | `New-Item -ItemType Directory -Path "~\.codex\sessions\YYYY\MM\DD" -Force` |
| `invalid_payload` on file tasks | Known Azure bug #16916 | No fix yet — text-only works |
| Plugins cause `invalid_payload` | Tool schemas injected by plugins | Remove plugin entries from config (Codex re-adds marketplace on restart, that's OK) |
| `api-version query parameter is not allowed` | query_params conflicts with /v1 path | Do not add query_params — /v1 handles versioning |

## Deliverables in Project Folder

- `config.toml` — reference copy of working config
- `credentials.txt` — endpoint URI, API key, deployment name
- `Codex_Azure_AI_Foundry_Setup_Manual.docx` — step-by-step team guide
- `skills/` — 33 skills in 4 categories with dependency READMEs
