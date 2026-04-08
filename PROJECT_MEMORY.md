---
name: In Search of a More Perfect Repo
description: Master sync repo for Claude Code skills, hooks, configs, memory across devices/accounts. GitHub private repo Taash1M/In-search-of-a-better-repo.
type: project
---

## Overview

Private GitHub repo serving as the single source of truth for all Claude Code assets. Enables syncing skills, hooks, configurations, and memory files across multiple devices and accounts.

**Why:** Claude Code configuration is scattered across `~/.claude/commands/`, `~/.claude/hooks/`, `~/.claude/projects/.../memory/`, and env vars. Moving between devices or accounts means rebuilding from scratch. This repo eliminates that.

**How to apply:** After any significant skill improvement, hook change, or memory update — copy the changed file into the appropriate repo subfolder, commit, and push. On other devices, `git pull` and copy to the local Claude Code directories.

## Key Facts

- **GitHub**: `https://github.com/Taash1M/In-search-of-a-better-repo` (private)
- **Local clone**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\In search of a more perfect repo\`
- **Created**: 2026-04-08
- **Content**: 41 skills, 3 hooks, 23 memory files, 2 Python modules, 3 settings templates, 10 READMEs
- **gh CLI**: Extracted to `C:\Users\tmanyang\tools\gh\bin\gh.exe` (v2.67.0) — needs `gh auth login` before first push

## Open Items

- [ ] Authenticate gh CLI (`gh auth login --web --git-protocol https`)
- [ ] Install gh CLI properly with admin privileges (current install is user-level zip extract)
- [ ] Initial commit and push to GitHub
- [ ] Set up sync script for automated copy between `~/.claude/` and repo
- [ ] Monthly audit cadence: remove stale memory, verify file paths
