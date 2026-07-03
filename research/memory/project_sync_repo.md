---
name: Master Sync Repo
description: Private GitHub repo (Taash1M/In-search-of-a-better-repo) for syncing Claude Code skills, hooks, configs, memory, MCPs across devices. Auto-sync hook wired in settings.json. 3 scripts (sync, push, hook). Full sanitization: personal IDs + <ORG>/<ORG_PARENT> company names. Last synced 2026-07-02 (c1f543b).
type: project
originSessionId: aa210407-a09e-461f-aa2f-83d0e2fa4475
---
## Overview

Master sync repo for all Claude Code assets. Enables identical setups across multiple devices and accounts.

**Why:** Claude Code config is scattered across `~/.claude/commands/`, `~/.claude/hooks/`, `~/.claude/projects/.../memory/`, and env vars. This repo is the single source of truth.

**How to apply:** When creating or improving skills, hooks, or memory — the `repo-sync.py` hook auto-copies changes to the OneDrive clone. Run `push_to_github.py` to commit and push. On other devices, `git pull` and run the Quick Start from the root README.

## Key Facts

- **GitHub**: `https://github.com/Taash1M/In-search-of-a-better-repo` (private)
- **OneDrive clone**: `<USER_HOME>/OneDrive - <ORG>\Claude code\In search of a more perfect repo\`
- **Local clone**: `<USER_HOME>/In-search-of-a-better-repo` (use for push — avoids OneDrive SSL issues)
- **PROJECT_MEMORY**: In repo root (not in `~/.claude/projects/` — lives with the project)
- **Created**: 2026-04-08
- **Last synced**: 2026-07-02, commit `c1f543b` — 114 files, 3 commits
- **Content**: 60+ skills, 10 hooks, 110+ memory files, 3 Python modules, 1 MCP server (PBI Semantic), sanitized settings.json

## Sanitization Rules (as of 2026-07-02)

Two layers — both `sync_to_repo.py` (on copy) and a one-time `sanitize_repo.py` pass:

| Pattern | Replacement |
|---------|-------------|
| `<ADMIN_HOME>/` | `<ADMIN_HOME>/` |
| `<USER_HOME>/` | `<USER_HOME>/` |
| `OneDrive - <ORG>` | `OneDrive - <ORG>` |
| `<ADMIN_USER>` | `<ADMIN_USER>` |
| `<USER>` | `<USER>` |
| personal emails | `<USER>@<ORG_DOMAIN>` etc. |
| `\bFluke\b` | `<ORG>` |
| `\bFortive\b` | `<ORG_PARENT>` |
| `\bFLK\b` | `<ORG_ABBR>` |

**SANITIZE_RULES are env-parameterized** in `sync_to_repo.py` — loaded from `CLAUDE_SYNC_USER` / `CLAUDE_SYNC_ADMIN` env vars so the rules themselves don't get self-sanitized.

`sync_to_repo.py` and `push_to_github.py` use `Path(__file__).resolve().parent` for `REPO_ROOT` / `ONEDRIVE_CLONE` — survives sanitization passes.

## Three Scripts

### 1. `repo-sync.py` (auto — PostToolUse hook)
- **Wired in**: `~/.claude/settings.json` → PostToolUse for Edit, Write, MultiEdit
- **What it does**: Copies modified files from live Claude Code locations to OneDrive clone
- **Watches**: skills (`~/.claude/commands/`), hooks, memory, settings.json, MCP source dirs
- **Settings.json**: Auto-redacts secrets (API keys → `<REDACTED>`) before copying
- **Content sanitization** (added 2026-04-30): ALL text files (.md, .py, .json, .yaml, .yml, .toml) are sanitized before writing. Replaces local paths, usernames, email addresses, and org names with generic placeholders (`<USER_HOME>/`, `<ADMIN_HOME>/`, `<USER>`, `<ADMIN_USER>`, `<ORG>`, `<USER>@<ORG_DOMAIN>`, etc.). Implemented via `SANITIZE_RULES` list of 9 compiled regex patterns and `_sanitize_content()` function.
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
cd "<USER_HOME>/OneDrive - <ORG>/Claude code/In search of a more perfect repo"
git add -A && git commit -m "Sync update"

# 2. Bundle → local clone → push
git bundle create /c/Users/<USER>/repo-sync-bundle.bundle main
cd "<USER_HOME>/In-search-of-a-better-repo"
git pull /c/Users/<USER>/repo-sync-bundle.bundle main
git config http.sslBackend schannel
git push origin main
rm /c/Users/<USER>/repo-sync-bundle.bundle
```

## Important Notes

- Settings in repo have redacted keys — real keys stay in local `~/.claude/settings.json`
- Binary docs (DOCX, PDF, PNG) NOT in git — referenced by OneDrive path in `docs/README.md`
- Secret scanner skips this repo for local commits (authorized private repo exception)
- **SSL fix required**: Both clones need `git config http.sslBackend schannel` for push to work through corporate proxy
- MCP servers synced under `modules/mcp-servers/<name>/` — repo-sync.py watches MCP source dirs
- `sync_to_repo.py` SYNC_MAP must be kept in sync with `repo-sync.py` SKILL_OVERRIDES — both route files to the same destinations

## Security Incident & Remediation (2026-04-30)

**Incident**: GitHub push on 2026-04-29 (commit `91cd35b`) triggered a DLP/security alert for containing "User details or company related projects" — local file paths with usernames, email addresses, and org names in synced content (hooks, memory, skills).

**Root cause**: `repo-sync.py` redacted API keys in settings.json but did NOT sanitize personal identifiers (paths, usernames, emails) in other file types.

**Fix (two-layer)**:
1. **Preventive**: Added `SANITIZE_RULES` (9 regex patterns) and `_sanitize_content()` to `repo-sync.py` — ALL future synced text files are auto-sanitized before writing to the repo clone
2. **Corrective**: One-time sanitization pass on 72 existing tracked files in the repo (committed as `e4d6843`, pushed 2026-04-30)

**Sanitization patterns**:
| Pattern | Replacement |
|---------|-------------|
| `<ADMIN_HOME>/` | `<ADMIN_HOME>/` |
| `<USER_HOME>/` | `<USER_HOME>/` |
| `OneDrive - <ORG>` | `OneDrive - <ORG>` |
| `<VM_HOME>/` | `<VM_HOME>/` |
| `<USER>@<ORG_DOMAIN>` | `<USER>@<ORG_DOMAIN>` |
| `<USER>@<ORG_DOMAIN>` | `<USER>@<ORG_DOMAIN>` |
| `<USER>@<PERSONAL_DOMAIN>` | `<USER>@<PERSONAL_DOMAIN>` |
| `<ADMIN_USER>` | `<ADMIN_USER>` |
| `<USER>` | `<USER>` |

**Verification**: Full scan confirmed zero remaining personal identifiers in all tracked files. Brand names (<ORG>, <ORG_PARENT>) retained in descriptive content — these are public company names, not PII.
