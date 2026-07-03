---
name: claude-code-env-override
description: "Windows User/Machine env vars override Claude Code settings.json — when swapping providers, also clean Windows env or /status keeps showing the old provider"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d0518511-12b3-40f2-a588-f406002e059b
---

When swapping Claude Code between providers (Azure Foundry ⇄ AWS Bedrock), editing `settings.json` is **not enough** if the old provider's keys are also set as Windows User-level or Machine-level environment variables. The process inherits them and overrides settings.json silently — `/status` keeps showing the old provider.

**Why:** Hit on 2026-06-19 when swapping to Bedrock. settings.json was correct (`CLAUDE_CODE_USE_BEDROCK=1`), but `ANTHROPIC_FOUNDRY_API_KEY` was set at Windows User level and Claude Code kept routing to Foundry. Diagnosed via `Get-ChildItem env: | Where-Object { $_.Name -like "*ANTHROPIC*" }`.

**How to apply:** Whenever swapping or removing a Claude Code provider:
1. Edit settings.json under the **right user** (Claude Code in admin shell reads `<ADMIN_HOME>/.claude\settings.json`, not <USER>'s)
2. Check Windows persistent env vars: `Get-ChildItem env: | Where-Object { $_.Name -like "*ANTHROPIC*" -or $_.Name -like "*CLAUDE*" -or $_.Name -like "*FOUNDRY*" -or $_.Name -like "*BEDROCK*" }`
3. Remove leftovers at User AND Machine scope:
   ```powershell
   [System.Environment]::SetEnvironmentVariable("ANTHROPIC_FOUNDRY_API_KEY", $null, "User")
   [System.Environment]::SetEnvironmentVariable("ANTHROPIC_FOUNDRY_API_KEY", $null, "Machine")
   ```
4. **Restart Claude Code** (close + reopen terminal) so the new process picks up the cleaned env
5. Verify with `/status`

Related:
- [[reference_aws_bda]] — AWS Bedrock active config
- [[credentials-swap-azure-to-bedrock]] — full swap procedure (file: `<USER_HOME>/.claude\Swap\credentials_swap_azure_to_bedrock.md`)
- [[user_workstation]] — dual-user Windows session
