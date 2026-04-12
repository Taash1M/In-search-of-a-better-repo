---
name: In Search of a More Perfect Repo
description: Master sync repo for Claude Code skills, hooks, configs, memory across devices/accounts. GitHub private repo Taash1M/In-search-of-a-better-repo. 88 files, 42K lines, fully operational.
type: project
---

## Overview

Private GitHub repo serving as the single source of truth for all Claude Code assets. Enables syncing skills, hooks, configurations, and memory files across multiple devices and accounts.

**Why:** Claude Code configuration is scattered across `~/.claude/commands/`, `~/.claude/hooks/`, `~/.claude/projects/.../memory/`, and env vars. Moving between devices or accounts means rebuilding from scratch. This repo eliminates that.

**How to apply:** After any significant skill improvement, hook change, or memory update — copy the changed file into the appropriate repo subfolder, commit, and push. On other devices, `git pull` and copy to the local Claude Code directories. The `repo-sync.py` hook handles this automatically for most file changes.

## Key Facts

- **GitHub**: `https://github.com/Taash1M/In-search-of-a-better-repo` (private)
- **Local clone**: `C:\Users\tmanyang\OneDrive - Fortive\Claude code\In search of a more perfect repo\`
- **Created**: 2026-04-08
- **Initial commit**: 88 files, 42,712 lines
- **gh CLI**: Extracted to `C:\Users\tmanyang\tools\gh\bin\gh.exe` (v2.67.0) — authenticated via git credential manager

## Content Inventory

| Category | Count | Location in Repo |
|----------|------:|------------------|
| Skills (AI UCB) | 21 | `skills/ai-ucb/` (orchestrator, sub-skills, companions, reference) |
| Skills (standalone) | 11 | `skills/standalone/` |
| Skills (document) | 7 | `skills/document/` |
| Skills (knowledge graph) | 2 | `skills/knowledge-graph/` |
| Hooks | 4 | `configurations/hooks/` (incl. repo-sync.py) |
| Settings templates | 3 | `configurations/settings-templates/` (keys = placeholders) |
| Memory files | 23 | `research/memory/` |
| Python modules | 2 | `modules/` (docx_beautify, azure_diagrams) |
| READMEs | 12 | Root + every section/subsection |
| Sync script | 1 | `sync_to_repo.py` |
| **Total** | **88** | |

## Sync Infrastructure

### 1. PostToolUse Hook — `repo-sync.py`
- **Installed at**: `~/.claude/hooks/repo-sync.py`
- **Triggers on**: Edit, Write, MultiEdit to any file in `~/.claude/commands/`, `~/.claude/hooks/`, or `~/.claude/projects/.../memory/`
- **Action**: Auto-copies the changed file to the correct repo subfolder
- **Does NOT**: git commit or push — that's manual or via sync script

### 2. Sync Script — `sync_to_repo.py`
- **Location**: Repo root
- **Usage**: `python sync_to_repo.py` (full sync) or `--dry-run` or `--category skills`
- **Capabilities**: Copies all known files, detects NEW files not in the sync map, writes `.last_sync` metadata
- **Fixed**: Windows cp1252 encoding issue (wraps stdout in utf-8)

### 3. Secret Scanner Exclusion
- **File**: `~/.claude/hooks/secret-scanner.py`
- **Change**: Added `AUTHORIZED_PRIVATE_REPOS` list that skips scanning when `git rev-parse --show-toplevel` matches this repo
- **Also added**: `'In search of a more perfect repo/'` to `EXCLUDED_DIRS` (belt and suspenders)

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| API keys stripped from settings templates | GitHub Push Protection blocks pushes with real Azure AI Service keys. Placeholders used instead. Real keys stay in local `~/.claude/settings.json`. |
| Binary docs NOT in git | Training PNGs, DOCXs, PDFs bloat git history. Referenced by OneDrive path in `docs/README.md`. |
| One template per node (not per user) | 3 templates vs 13 individual files. Users customize locally. |
| READMEs at Architecture/Approach depth | Written for future-Taashi picking up any workstream cold. 7-section structure: Overview, Architecture, Inventory, How It Works, How to Extend, Key Decisions, Gotchas. |
| repo-sync.py hook auto-copies but doesn't commit | Avoids noisy auto-commits. User decides when to commit and push. |
| Secret scanner skips this repo | Authorized private repo exception. Prevents false-positive blocks on skill files containing example passwords/keys in documentation. |

## Completed Items

- [x] gh CLI installed (zip extract to `C:\Users\tmanyang\tools\gh\bin\gh.exe`, v2.67.0)
- [x] gh authenticated via git credential manager
- [x] Initial commit and push to GitHub (88 files, 42,712 lines)
- [x] Sync script created and tested (`sync_to_repo.py`)
- [x] PostToolUse hook created and installed (`repo-sync.py`)
- [x] Secret scanner updated with repo exclusion
- [x] All 12 READMEs written (root, skills, ai-ucb, standalone, document, KG, configurations, environment, research, learnings, modules, docs)

## Open Items

- [ ] Install gh CLI properly with admin privileges (current is user-level zip extract)
- [ ] Monthly audit cadence: remove stale memory, verify file paths, update READMEs
- [ ] Set up scheduled task / cron for periodic `sync_to_repo.py` runs (currently manual)
- [ ] Verify repo clone + setup works on a second device end-to-end
- [ ] Consider adding CLAUDE.md templates to the repo for new project bootstrapping
