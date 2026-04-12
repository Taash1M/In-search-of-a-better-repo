---
name: Master Sync Repo
description: Private GitHub repo (Taash1M/In-search-of-a-better-repo) for syncing Claude Code skills, hooks, configs, memory across devices. 88 files, 42K lines. Auto-sync hook installed.
type: project
---

## Overview

Master sync repo for all Claude Code assets. Enables identical setups across multiple devices and accounts.

**Why:** Claude Code config is scattered across `~/.claude/commands/`, `~/.claude/hooks/`, `~/.claude/projects/.../memory/`, and env vars. This repo is the single source of truth.

**How to apply:** When creating or improving skills, hooks, or memory — the `repo-sync.py` hook auto-copies changes to the repo. Commit and push manually. On other devices, `git pull` and run the Quick Start from the root README.

## Key Facts

- **GitHub**: `https://github.com/Taash1M/In-search-of-a-better-repo` (private)
- **Local**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\In search of a more perfect repo\`
- **PROJECT_MEMORY**: In repo root (not in `~/.claude/projects/` — lives with the project)
- **Created**: 2026-04-08
- **Content**: 41 skills, 4 hooks, 23 memory files, 2 Python modules, 3 settings templates, 12 READMEs
- **gh CLI**: `C:\Users\tmanyang\tools\gh\bin\gh.exe` (v2.67.0, zip extract)

## Sync Infrastructure

1. **`repo-sync.py` hook** — PostToolUse, auto-copies skill/hook/memory files to repo on Edit/Write
2. **`sync_to_repo.py`** — Manual full sync script with `--dry-run` and `--category` options
3. **Secret scanner exclusion** — This repo added to `AUTHORIZED_PRIVATE_REPOS` in `secret-scanner.py`
4. **Settings templates** — API keys replaced with `<YOUR_API_KEY_HERE>` placeholders (GitHub Push Protection)

## Important Notes

- Settings templates have placeholder keys — real keys stay in local `~/.claude/settings.json`
- Binary docs (DOCX, PDF, PNG) NOT in git — referenced by OneDrive path in `docs/README.md`
- Secret scanner skips this repo for local commits (authorized private repo exception)
