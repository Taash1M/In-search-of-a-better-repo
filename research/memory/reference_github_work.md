---
name: github-work-account
description: "<USER>'s work GitHub account (Taashi-Manyanga_fortive) for work-related repos and internal sharing"
metadata: 
  node_type: memory
  type: reference
  originSessionId: d8a16674-fc1f-40b3-803f-51b3df5414ad
---

Work GitHub account for <USER> (non-admin persona):
- **URL**: https://github.com/Taashi-Manyanga_fortive
- **Type**: Enterprise Managed User (EMU) — **cannot create public repos**, private only
- **Purpose**: Work-related repos, sharing code/plans internally
- **Distinct from**: `taashim-eng` (the account that owns `ai-navigator-pro` source repo)
- **Use for**: Syncing project progress, sharing deliverables, work repo hosting
- **gh CLI auth**: Authenticated via device code flow, token stored in `<ADMIN_HOME>/AppData/Roaming/GitHub CLI/hosts.yml`. When running as `<ADMIN_USER>`, gh finds it automatically. When running from `<USER>` profile, token is at `<USER_HOME>/AppData/Roaming/GitHub CLI/hosts.yml`.
- **gh CLI path**: `C:/Program Files/GitHub CLI/gh.exe` (not on bash PATH by default — use `export PATH="/c/Program Files/GitHub CLI:$PATH"`)

Related repos:
- [[ai-navigator-pro]] source — `taashim-eng/ai-navigator-pro` (public)
- [[ai-navigator-pro]] deploy — `Taashi-Manyanga_fortive/ai-navigator-pro-deploy` (private, 11 docs, 2026-05-17)
