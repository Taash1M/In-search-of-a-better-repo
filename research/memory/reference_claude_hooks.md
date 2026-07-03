---
name: claude-code-hooks
description: "The 8 Claude Code hooks at ~/.claude/hooks/ — secret-scanner, dangerous-command-blocker, change-logger, repo-sync, obsidian-session-logger, obsidian-memory-sync, aws-cost-tracker, qa-gate-enforcer — plus env facts (python path, Docker, sitecustomize, inventory.py)"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

# Claude Code Hooks (8 scripts)

- **Location**: `<ADMIN_HOME>/.claude\hooks\`
- **secret-scanner.py**: PreToolUse on Bash, blocks git commits with secrets (30+ patterns)
- **dangerous-command-blocker.py**: PreToolUse on Bash, 3-level protection
- **change-logger.py**: PostToolUse on Edit/Write/MultiEdit/Bash, logs to `~/.claude/critical_log_changes.csv`
- **repo-sync.py**: PostToolUse on Edit/Write/MultiEdit, auto-copies skills/hooks/memory/MCPs/settings to sync repo (2026-04-11). Sanitizes ALL text files (9 regex patterns, after DLP alert 2026-04-30). Does NOT commit/push.
- **obsidian-session-logger.py**: PostToolUse on Edit/Write/MultiEdit/Bash, appends tool activity to Obsidian vault `1-Projects/Claude Sessions/YYYY-MM-DD.md` (added 2026-04-17). Self-protecting (skips own session file). Read-only commands filtered.
- **obsidian-memory-sync.py**: PostToolUse on Edit/Write/MultiEdit, auto-syncs memory files to Obsidian `3-Resources/Claude Memory/` (2026-06-04). Skips MEMORY.md. Adds sync frontmatter + session-log entry. 68 files backfilled.
- **aws-cost-tracker.py**: PostToolUse on Bash, detects AWS commands, estimates cost from rate card → JSONL `AWS\costs\executions\` (2026-06-19). Non-blocking; never guesses volume. Rollup `AWS\costs\rollup_costs.py`. See [[project-aws-twin]].
- **qa-gate-enforcer.py**: SubagentStop, hard-enforces the `qa-gate` sub-agent (added 2026-06-19). FAIL-dominant, fail-CLOSED (blocks exit 2 on FAIL/unparseable). Ledger `~/.claude/qa_gate_ledger.ndjson`; sub-agent `~/.claude/agents/qa-gate.md`. See [[project-aws-twin]].

## Environment facts
- **CLAUDE.md**: `~/.claude/CLAUDE.md` — instructs Claude to read Obsidian session logs on start, write decisions/findings during sessions, summarize at end
- **Python path**: `python` not `python3` (Windows, Python 3.12)
- **Docker**: Available on `<USER>` account (2026-06-10) — local builds possible; ACR cloud build as fallback
- **sitecustomize.py**: `<USER_HOME>/Python312\Lib\sitecustomize.py` — auto-preloads DLLs from `tools\cairo-dlls\` on every Python start (eliminates manual ctypes.CDLL calls). Created 2026-06-08.
- **inventory.py**: `<USER_HOME>/tools\inventory.py` — catalogs 427 pip packages, CLI tools, native DLLs, PATH entries, tests native deps. Run: `python <USER_HOME>/tools/inventory.py`

Related: [[obsidian-secondbrain]] · [[dll-discovery-on-windows]] · [[cairosvg-windows-setup]]
