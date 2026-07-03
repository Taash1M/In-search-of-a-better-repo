---
name: Repo content sanitization
description: All content synced to GitHub repo must be sanitized — no local paths, usernames, emails, or org-specific identifiers. repo-sync.py handles this automatically; verify before every push.
type: feedback
originSessionId: ae50e3e1-9553-4e26-a884-435a65a1bea9
---
All content pushed to the GitHub sync repo (Taash1M/In-search-of-a-better-repo) must be free of personal identifiers before reaching the remote.

**Why:** A GitHub push on 2026-04-29 (commit `91cd35b`, "Daily sync 2026-04-29") triggered a corporate DLP/security escalation. The security team (Jerinthraj G) flagged the push for containing "User details or company related projects."

**What caused the alert:**
- The push contained files synced by `repo-sync.py` — hooks, memory files, skills, and MCP server code
- These files contained hardcoded local Windows paths like `<USER_HOME>/OneDrive - <ORG>/Claude code/Obsidian/` (specifically in `obsidian-session-logger.py`), personal email addresses (`<USER>@<ORG_DOMAIN>`, `@<ORG_PARENT>.com`, `@gmail.com`), Windows usernames (`<USER>`, `<ADMIN_USER>`), and org-specific identifiers (`OneDrive - <ORG>`)
- The `repo-sync.py` hook had redaction for API keys/secrets in `settings.json` but did NOT sanitize personal identifiers in any other file type — that was the gap
- The corporate DLP scanner (runs on GitHub push, not on local drives) pattern-matched these identifiers and escalated

**Detection mechanism:** Corporate DLP tool scanning GitHub repository pushes (not local filesystem scans). Every push to the org-visible repo triggers a content scan for PII patterns including usernames, email addresses, local file paths, and org-specific identifiers.

**How to apply:**
1. `repo-sync.py` now auto-sanitizes all text files (.md, .py, .json, .yaml, .yml, .toml) via `SANITIZE_RULES` + `_sanitize_content()` — this is the primary defense
2. Before every `git push` to the sync repo, run a grep scan for the 9 PII patterns (usernames, local paths, email addresses, org identifiers) on the OneDrive clone
3. If adding new file types or new watched directories to repo-sync.py, ensure they go through `_sanitize_content()`
4. If adding new usernames, paths, or email addresses to the local environment, add corresponding patterns to `SANITIZE_RULES` in repo-sync.py
5. Brand names (<ORG>, <ORG_PARENT>) are public company names and acceptable in descriptive content — only personal/account-specific identifiers need sanitization
6. The `sync_to_repo.py` batch script also needs sanitization if used directly — currently repo-sync.py is the primary path
