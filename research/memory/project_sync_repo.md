---
name: Master Sync Repo
description: Private GitHub repo (Taash1M/In-search-of-a-better-repo) for syncing Claude Code skills, hooks, configs, memory, MCPs across devices. Auto-sync hook wired in settings.json. 3 scripts (sync, push, hook).
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
## Overview

Master sync repo for all Claude Code assets. Enables identical setups across multiple devices and accounts.

**Why:** Claude Code config is scattered across `~/.claude/commands/`, `~/.claude/hooks/`, `~/.claude/projects/.../memory/`, and env vars. This repo is the single source of truth.

**How to apply:** When creating or improving skills, hooks, or memory — the `repo-sync.py` hook auto-copies changes to the OneDrive clone. Run `push_to_github.py` to commit and push. On other devices, `git pull` and run the Quick Start from the root README.

## Key Facts

- **GitHub**: `https://github.com/Taash1M/In-search-of-a-better-repo` (private)
- **OneDrive clone**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\In search of a more perfect repo\`
- **Local clone**: `C:\Users\tmanyang\In-search-of-a-better-repo` (use for push — avoids OneDrive SSL issues)
- **PROJECT_MEMORY**: In repo root (not in `~/.claude/projects/` — lives with the project)
- **Created**: 2026-04-08
- **Content**: 52 skills, 4 hooks, 30 memory files, 3 Python modules, 1 MCP server (PBI Semantic), sanitized settings.json, .mcp.json (2 servers: context7 + obsidian)

## Three Scripts

### 1. `repo-sync.py` (auto — PostToolUse hook)
- **Wired in**: `~/.claude/settings.json` → PostToolUse for Edit, Write, MultiEdit
- **What it does**: Copies modified files from live Claude Code locations to OneDrive clone
- **Watches**: skills (`~/.claude/commands/`), hooks, memory, settings.json, MCP source dirs
- **Settings.json**: Auto-redacts secrets (API keys → `<REDACTED>`) before copying
- **Skill routing**: 23 named overrides (ai-ucb, document, knowledge-graph), default → standalone/
- **Skill subdirs**: Handles `commands/frontend-slides/`, `commands/notebooklm/` etc. recursively
- **MCP routing**: More-specific paths ordered first (data/ before general src/)
- **Does NOT** commit or push — just copies files

### 2. `sync_to_repo.py` (manual — comprehensive batch sync)
- **Usage**: `python sync_to_repo.py [--dry-run] [--category skills|hooks|memory|modules|mcp|settings|all] [--auto-discover]`
- **Categories**: skills (flat + subdirs), hooks, memory, modules, settings (sanitized), mcp
- **Auto-discover**: `--auto-discover` finds NEW files not in explicit map and syncs them
- **MCP sync**: Structured paths for PBI Semantic (source, tools, metadata, data, tests, root files)
- **Idempotent**: Only copies if source is newer or dest missing (mtime + size check)

### 3. `push_to_github.py` (manual — handles OneDrive push workaround)
- **Usage**: `python push_to_github.py [--no-commit] [--message "msg"] [--dry-run]`
- **Workflow**: Commit in OneDrive clone → bundle → pull into local clone → push with schannel SSL → cleanup
- **Why needed**: OneDrive + OpenSSL `git push` fails on large payloads through corporate proxy. The `schannel` SSL backend works.
- **Verifies**: Checks remote HEAD matches local HEAD after push

## Full Sync Workflow (for Claude)

When user says "sync to GitHub" or "push to repo":
1. If files were just edited, `repo-sync.py` hook already copied them to OneDrive clone
2. For a comprehensive sync: `python sync_to_repo.py --auto-discover`
3. To push: `python push_to_github.py -m "description of changes"`

Or if doing it manually via bash:
```bash
# 1. Commit in OneDrive clone
cd "C:/Users/tmanyang/OneDrive - Fortive/Claude code/In search of a more perfect repo"
git add -A && git commit -m "Sync update"

# 2. Bundle → local clone → push
git bundle create /c/Users/tmanyang/repo-sync-bundle.bundle main
cd "C:/Users/tmanyang/In-search-of-a-better-repo"
git pull /c/Users/tmanyang/repo-sync-bundle.bundle main
git config http.sslBackend schannel
git push origin main
rm /c/Users/tmanyang/repo-sync-bundle.bundle
```

## Important Notes

- Settings in repo have redacted keys — real keys stay in local `~/.claude/settings.json`
- Binary docs (DOCX, PDF, PNG) NOT in git — referenced by OneDrive path in `docs/README.md`
- Secret scanner skips this repo for local commits (authorized private repo exception)
- **SSL fix required**: Both clones need `git config http.sslBackend schannel` for push to work through corporate proxy
- MCP servers synced under `modules/mcp-servers/<name>/` — repo-sync.py watches MCP source dirs
- `sync_to_repo.py` SYNC_MAP must be kept in sync with `repo-sync.py` SKILL_OVERRIDES — both route files to the same destinations
