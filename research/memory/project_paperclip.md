---
name: Paperclip Agent Orchestration
description: Multi-agent orchestration skill cherry-picked from paperclipai/paperclip (MIT). Covers agent registry, task ticketing, budget tracking, heartbeat scheduling, and activity logging for the Fluke AI team.
type: project
---

## Overview

Paperclip is a Claude Code skill for multi-agent orchestration, adapted from the open-source paperclipai/paperclip project (MIT license). It was reviewed for security (clean — no telemetry, no exfiltration, no malicious code), then the best capabilities were cherry-picked into a single skill file rather than installing the full Node.js server.

**Why:** The full paperclip install (Node.js + React + SQLite) was overkill for 16 users on Azure AI Foundry. A single skill file gives us the orchestration patterns without the infrastructure overhead, while respecting existing hooks (secret-scanner, command-blocker, change-logger).

## Key Dates

- **2026-04-01**: Security review of paperclipai/paperclip repo completed (clean, MIT, no risks)
- **2026-04-01**: Skill v1 built, scored A- by skills judge
- **2026-04-01**: 6 improvements applied, re-scored A+ (100/100 all dimensions)
- **2026-04-01**: State directory initialized, usage guide DOCX generated

## Files

| File | Location | Purpose |
|---|---|---|
| `paperclip.md` | `C:\Users\adm-tmanyang\.claude\commands\paperclip.md` | Skill file (active) |
| `agents.json` | `C:\Users\tmanyang\Claude\deliverebles\paperclip\` | Agent registry |
| `issues.json` | same | Task/ticket backlog |
| `budgets.json` | same | Budget policies + incidents |
| `jobs.json` | same | Scheduled heartbeat jobs |
| `job-runs.json` | same | Immutable job execution history |
| `activity-log.json` | same | Redacted audit trail |
| `config.json` | same | Orchestration settings |
| `Paperclip_Usage_Guide.docx` | same | User guide with examples (10 sections) |
| `SECURITY_REVIEW.md` | `C:\Users\tmanyang\OneDrive - Fortive\Claude code\Paperclip\` | Full security audit of source repo |

## Architecture

5 modules, all state in JSON files under `C:\Users\tmanyang\Claude\deliverebles\paperclip\`:

1. **Agent Registry** — named agents with skills, models, adapter types (claude_local, codex_local, gemini_local, process, http). Status FSM: active/paused/error/retired.
2. **Task Ticketing** — issues with status FSM (backlog/todo/in_progress/in_review/blocked/done/cancelled), priority (critical/high/medium/low), execution locking, rework support.
3. **Budget Tracking** — policies at company/agent/project scope, calendar_month or lifetime windows, soft warning at 80%, hard stop at 100% with agent pause cascade.
4. **Heartbeat Scheduling** — cron-based jobs with overlap prevention, retry policy (exponential backoff: 30s base * 2^attempt, max 2 retries), timeout enforcement.
5. **Activity Log** — append-only with redaction pipeline (paths, usernames, secrets).

## Config Defaults

- Model: claude-opus-4-6
- Node: flk-team-ai-enablement-ai
- Max parallel agents: 5
- Budget check before spawn: enabled
- Timeout: 5 min
- Retries: 2 with 30s exponential backoff

## Skills Judge History

| Version | Grade | Key Gap | Resolution |
|---|---|---|---|
| v1 | A- (86/100) | Missing env tiering, task tracking, agent FSM, retry policy, standup template, config model | 6 targeted improvements |
| v2 | A+ (100/100) | None blocking | Minor future: schema migration, file locking, archive rotation |

## Suggested Agent Configurations

| Name | Skills | Model | Use Case |
|---|---|---|---|
| UBI-Dev | ubi-dev, audit-ubi | opus | Databricks, ADF, Gold views |
| AI-Builder | fluke-ai, ai-use-case-builder | opus | Azure AI solutions |
| Audit-Bot | audit-ubi | sonnet | Scheduled health checks |
| Doc-Writer | excel-create, powerpoint-create | sonnet | Reports and decks |
| Research-Agent | taashi-research | opus | Deep research |

## Source Repo Review Summary

- **Repo**: github.com/paperclipai/paperclip (MIT, ~56K lines TypeScript)
- **Security**: No telemetry, no phone-home, no obfuscation, no prompt injection
- **Good patterns cherry-picked**: plugin sandbox, secrets management (AES-256-GCM), heartbeat scheduler, adapter abstraction, activity logging with redaction, budget enforcement
- **Red flags (not malicious, just risky defaults)**: dangerouslySkipPermissions=true, SSRF in company import, default auth=local_trusted
- **Verdict**: Safe to install for evaluation, but skill approach preferred for our environment

## Integration Points

- Azure AI Foundry (ANTHROPIC_FOUNDRY_API_KEY)
- LLM Usage Tracking (DuckDB/PBI for budget data)
- Existing skills (agents reference by name)
- Hooks (all spawns go through secret-scanner + command-blocker)
- Session review (/session-review scans paperclip activity)
