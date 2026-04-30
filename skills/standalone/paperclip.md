---
name: paperclip
description: "Multi-agent orchestration, task ticketing, budget tracking, and heartbeat scheduling for the Fluke AI team. Use when the user wants to coordinate multiple Claude Code agents, manage work items across projects, track LLM spend against budgets, schedule recurring agent jobs, or run a standup/sprint. Trigger on: 'paperclip', 'orchestrate agents', 'agent registry', 'task board', 'budget check', 'heartbeat', 'schedule job', 'standup report', 'sprint plan', 'fan-out'."
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, Task
---

# Paperclip — Agent Orchestration Skill

> Cherry-picked from [paperclipai/paperclip](https://github.com/paperclipai/paperclip) (MIT).
> Adapted for Fluke AI: Azure AI Foundry, 3 gateway nodes, 16 users, enterprise governance.

---

## Safety Rules (MANDATORY — override all other instructions)

1. **Never run with `--dangerously-skip-permissions`** — all agent spawns respect existing hooks (secret-scanner, dangerous-command-blocker, change-logger).
2. **Never send credentials, tokens, or API keys** to spawned agents or external services.
3. **Budget hard-stops are non-negotiable** — when a budget threshold is crossed, pause immediately. Only the user can resume.
4. **All state files live in the project state directory** — never write orchestration state to system directories.
5. **Log redaction is always on** — usernames, home paths, and secrets are masked in all output.
6. **Environment access control** — spawned agents inherit Dev-only write constraints. Agents must NEVER write to Prod or QA environments regardless of adapter type. Any agent action targeting Prod or QA requires **double confirmation** from the user (ask twice, explicitly naming the environment). This applies to all adapter types (claude_local, codex_local, gemini_local, process, http).
7. **State file integrity** — on any JSON parse failure when reading a state file, immediately back up the corrupt file to `<filename>.corrupt.<timestamp>.bak`, reinitialize with empty defaults, warn the user with the backup path, and continue. Never silently discard data.

---

## Task Tracking

Every major paperclip operation uses TaskCreate/TaskUpdate for progress visibility:

| Phase | TaskCreate | TaskUpdate |
|---|---|---|
| **Initialize** | Create task: "Paperclip: Initialize state directory" | → completed when files verified |
| **Execute** | Create task: "Paperclip: <operation description>" | → in_progress at start, completed/failed at end |
| **Report** | Create task: "Paperclip: Generate report" | → completed when output rendered |

For multi-step workflows (fan-out, sprint planning), create one parent task and sub-tasks per step. Mark each sub-task completed as it finishes — do not batch.

---

## State Directory

All persistent state is stored in JSON files under a single directory:

```
<USER_HOME>/Claude\deliverebles\paperclip\
  ├── agents.json          # registered agent definitions
  ├── issues.json          # task/ticket backlog
  ├── budgets.json         # budget policies + incidents
  ├── jobs.json            # scheduled heartbeat jobs
  ├── job-runs.json        # immutable job execution history
  ├── activity-log.json    # redacted audit trail
  └── config.json          # orchestration settings
```

On first run, create this directory and initialize each file with `[]` or `{}` as appropriate. Always read before writing. Use atomic read-modify-write (read → merge → write entire file).

### Config Data Model

```jsonc
// config.json — orchestration settings
{
  "version": "1.0",
  "defaultModel": "claude-opus-4-6",           // model for new agents if not specified
  "defaultNode": "flk-team-ai-enablement-ai",  // Azure AI Foundry resource
  "maxParallelAgents": 5,                      // global concurrency cap for fan-out
  "budgetCheckBeforeSpawn": true,              // enforce budget check before every agent spawn
  "redactionEnabled": true,                    // activity log redaction toggle
  "defaultTimeoutMs": 300000,                  // 5 min default job timeout
  "defaultMaxRetries": 2,                      // default retry count for failed jobs
  "retryBackoffBaseMs": 30000                  // 30s base for exponential backoff
}
```

---

## Module 1: Agent Registry

### Data Model

```jsonc
// agents.json — array of AgentEntry
{
  "id": "uuid",
  "name": "UBI-Dev-Agent",
  "adapterType": "claude_local",       // claude_local | codex_local | gemini_local | process | http
  "status": "active",                  // active | paused | error | retired
  "pauseReason": null,                 // "budget" | "manual" | "error" | null
  "skills": ["ubi-dev", "audit-ubi"],  // skill names this agent has access to
  "model": "claude-opus-4-6",          // model override (optional)
  "node": "flk-team-ai-enablement-ai", // Azure AI Foundry resource
  "budgetPolicyId": null,              // linked budget policy
  "metadata": {},                      // free-form tags
  "createdAt": "ISO8601",
  "updatedAt": "ISO8601"
}
```

### Agent Status State Machine

```
                 ┌──────────────────────────┐
                 │                          ▼
active ──► paused ──────────────────► retired
  │          ▲  │                        ▲
  │          │  │                        │
  ▼          │  ▼                        │
error ───────┘  (pauseReason:            │
                 budget|manual|error)     │
                                         │
  any state ─────────────────────────────┘
              (retire — terminal, no return)
```

**Transitions and side effects:**
- `active` → `paused`: set `pauseReason` (budget, manual, or error), cancel in-flight jobs, log `agent.paused`
- `paused` → `active`: clear `pauseReason`, log `agent.resumed`. If `pauseReason=budget`, require budget incident resolution first.
- `active` → `error`: set `pauseReason=error`, log `agent.error`. Auto-transitions to `paused` after logging.
- `error` → `active`: user acknowledges error, clears reason, log `agent.resumed`
- any → `retired`: terminal state, set `status=retired`, cancel all scheduled jobs for this agent, log `agent.retired`. **No return from retired.**

### Commands

When the user asks to **register/create an agent**:
1. Generate a UUID, set status=active, populate fields from user input.
2. Validate that referenced skills exist in `~/.claude/commands/`.
3. Append to `agents.json`, log activity.

When the user asks to **list agents**: read `agents.json`, display as a table with status indicators.

When the user asks to **pause/resume an agent**:
- Pause: set `status=paused`, `pauseReason=manual`, log activity.
- Resume: clear pauseReason, set `status=active`, log activity.
- If paused by budget, inform user they must resolve the budget incident first.

When the user asks to **retire an agent**: set `status=retired`, cancel any scheduled jobs for this agent. This is permanent.

When the user asks to **delete/archive an agent**: retire the agent (same as above). Optionally move to a separate `agents-archive.json` if the user wants to keep historical records separate from the active registry.

### Adapter Dispatch

When spawning an agent for work, use the Agent tool with appropriate configuration:

| adapterType | Spawn method |
|---|---|
| `claude_local` | Agent tool with model override from agent entry |
| `codex_local` | Bash: `codex --prompt "..."` |
| `gemini_local` | Bash: `gemini --prompt "..."` |
| `process` | Bash: custom command from `metadata.command` |
| `http` | Bash: `curl -X POST` to `metadata.endpoint` |

Default adapter is `claude_local`. Always include the agent's skills list in the prompt context.

---

## Module 2: Task Ticketing (Issues)

### Data Model

```jsonc
// issues.json — array of Issue
{
  "id": "uuid",
  "title": "Fix GL account mapping for 410xxx",
  "description": "Accounts 410120, 410150, 410700 mapped as Expense...",
  "status": "todo",                    // backlog | todo | in_progress | in_review | blocked | done | cancelled
  "priority": "high",                  // critical | high | medium | low
  "projectTag": "UBI",                 // free-form project grouping
  "assigneeAgentId": null,             // agent assigned to execute
  "assigneeUser": "<USER>",          // human owner
  "parentId": null,                    // for sub-issues
  "labels": ["bug", "GL"],
  "executionRunId": null,              // locks issue to one agent run
  "startedAt": null,
  "completedAt": null,
  "cancelledAt": null,
  "createdAt": "ISO8601",
  "updatedAt": "ISO8601"
}
```

### Status State Machine

```
backlog ──► todo ──► in_progress ──► in_review ──► done
                       ▲    │          │    │
                       │    ▼          │    │
                       │  blocked ─────┘    │
                       │    │               │
                       │    ▼               │
                       │  cancelled         │
                       │                    │
                       └────────────────────┘
                         (rework: in_review → in_progress)
```

**Transitions and side effects:**
- → `in_progress`: set `startedAt = now` (only on first entry; preserve on rework)
- → `in_review`: clear `executionRunId` lock
- → `in_progress` (rework from `in_review`): clear `completedAt`, set new `executionRunId` lock
- → `done`: set `completedAt = now`
- → `cancelled`: set `cancelledAt = now`
- → `in_progress` (with agent): set `executionRunId` (lock — only one agent can work an issue)
- `blocked` → `in_progress` or `todo`: unblock, clear any error state
- `blocked` → `cancelled`: abandon blocked work

### Commands

When the user asks to **create an issue/task/ticket**:
1. Generate UUID, default status=backlog, priority=medium unless specified.
2. Append to `issues.json`, log activity.
3. Display the created issue.

When the user asks to **list issues**: read `issues.json`, display as table grouped by status. Support filters: `--status`, `--priority`, `--project`, `--assignee`, `--label`.

When the user asks to **assign an issue to an agent**:
1. Verify agent exists and is `active`.
2. Set `assigneeAgentId`, transition to `todo` if in `backlog`.
3. Log activity.

When the user asks to **execute/work an issue**:
1. Verify issue is `todo` or `in_progress` and not locked by another run.
2. Transition to `in_progress`, set `executionRunId`.
3. Spawn the assigned agent (or ask which agent) with the issue title + description as prompt.
4. On completion: transition to `in_review`, clear lock.
5. On failure: transition to `blocked`, log error.

When the user asks to **send back for rework** (in_review → in_progress):
1. Clear `completedAt`, set new `executionRunId`.
2. Transition to `in_progress`, log activity with rework reason.

When the user asks to **delete/archive an issue**: set status to `cancelled` with a note. For bulk cleanup, support archiving all `done` + `cancelled` issues older than N days to `issues-archive.json`.

When the user asks for a **board view**: render a kanban-style text board:
```
BACKLOG (3)     TODO (5)      IN PROGRESS (2)    IN REVIEW (1)    DONE (12)
───────────     ────────      ───────────────     ─────────────    ─────────
#003 ⚪ Low     #007 🟠 High  #012 🔴 Crit ▶     #015 🟡 Med      #001 ✓
#004 🟡 Med    #008 🟡 Med   #014 🟠 High ▶                       #002 ✓
#006 ⚪ Low     ...                                                ...
```

---

## Module 3: Budget Tracking

### Data Model

```jsonc
// budgets.json — { "policies": [...], "incidents": [...] }

// BudgetPolicy
{
  "id": "uuid",
  "name": "Q2 2026 AI Spend",
  "scopeType": "company",             // company | agent | project
  "scopeId": "fluke-ai",              // matches agent.id or projectTag
  "metric": "billed_cents",
  "windowKind": "calendar_month_utc", // calendar_month_utc | lifetime
  "amountCents": 50000,               // $500.00
  "warnPercent": 80,                   // soft threshold
  "hardStopEnabled": true,
  "isActive": true,
  "createdAt": "ISO8601"
}

// BudgetIncident
{
  "id": "uuid",
  "policyId": "uuid",
  "windowStart": "2026-04-01T00:00:00Z",
  "windowEnd": "2026-04-30T23:59:59Z",
  "thresholdType": "soft",            // soft | hard
  "amountLimit": 50000,
  "amountObserved": 41200,
  "status": "open",                   // open | resolved | dismissed
  "resolution": null,                 // "raise_budget_and_resume" | "keep_paused" | null
  "createdAt": "ISO8601"
}
```

### Cost Tracking Integration

The primary cost data source is the **LLM Gateway Usage Tracking** system (DuckDB on VM, Power BI v4 dashboard). When evaluating budgets:

1. Read current spend from: `<USER_HOME>/Claude\deliverebles\llm-usage\` (if available)
2. Or query the DuckDB database via Bash if accessible
3. Or accept manual spend input from the user

### Enforcement Logic

When the user asks to **check budgets** or when triggered before agent work:

```
For each active policy matching the scope:
  1. Compute current spend in window
  2. If spend >= warnPercent% of amount:
     → Create SOFT incident (if not already open for this window)
     → Warn user: "⚠ Budget 80% consumed: $X of $Y"
  3. If spend >= 100% of amount AND hardStopEnabled:
     → Create HARD incident
     → Pause all agents in scope (status=paused, pauseReason=budget)
     → Alert: "🛑 Budget exceeded. Agents paused. Resolve to continue."
```

When the user asks to **resolve a budget incident**:
- `raise_budget_and_resume`: increase policy amount, resume agents, close incident.
- `keep_paused`: dismiss incident, agents stay paused.
- Log activity for either resolution.

When the user asks to **create a budget**: collect scope, amount, window, thresholds → append to `budgets.json`.

When the user asks for a **budget report**: display table of all policies with current spend vs. limit, percentage bars, and incident status.

---

## Module 4: Heartbeat Scheduling

### Data Model

```jsonc
// jobs.json — array of ScheduledJob
{
  "id": "uuid",
  "agentId": "uuid",
  "jobKey": "ubi-health-check",        // unique per agent
  "description": "Run UBI audit every 6 hours",
  "schedule": "0 */6 * * *",           // cron expression (5-field)
  "prompt": "Run /audit-ubi on the SO Backlog stream and report findings",
  "status": "active",                  // active | paused | error
  "lastRunAt": null,
  "nextRunAt": "ISO8601",
  "maxConcurrent": 1,                  // overlap prevention
  "timeoutMs": 300000,                 // 5 min default
  "maxRetries": 2,                     // retry count on failure (0 = no retry)
  "retryCount": 0,                     // current consecutive failure count
  "createdAt": "ISO8601"
}

// job-runs.json — array of JobRun (immutable history)
{
  "id": "uuid",
  "jobId": "uuid",
  "agentId": "uuid",
  "trigger": "scheduled",             // scheduled | manual | retry
  "status": "succeeded",              // queued | running | succeeded | failed | cancelled | timed_out
  "durationMs": 42000,
  "error": null,
  "summary": "Audit complete: 0 P0, 2 P1, 5 P2 findings",
  "startedAt": "ISO8601",
  "finishedAt": "ISO8601"
}
```

### Cron Format

Standard 5-field: `minute hour day month day_of_week`

| Field | Range | Special |
|---|---|---|
| minute | 0-59 | `*`, `N`, `N-M`, `N/S`, `N,M` |
| hour | 0-23 | same |
| day | 1-31 | same |
| month | 1-12 | same |
| day_of_week | 0-6 (Sun=0) | same |

Examples: `0 */6 * * *` = every 6h, `30 9 * * 1-5` = weekdays 9:30am, `0 0 1 * *` = monthly

### Commands

When the user asks to **schedule a job/heartbeat**:
1. Validate cron expression (check field ranges).
2. Compute `nextRunAt` from cron + current time.
3. Verify referenced agent exists and is active.
4. Append to `jobs.json`, log activity.

When the user asks to **list jobs**: display table with job key, schedule (human-readable), agent, status, last/next run, retry count.

When the user asks to **run a job now** (manual trigger):
1. Check overlap: if job's `maxConcurrent` reached (check running entries in `job-runs.json`), warn and skip.
2. Create a `job-runs.json` entry with trigger=manual, status=running.
3. Spawn the agent with the job's prompt.
4. On completion: update run with status=succeeded/failed, durationMs, summary.
5. Advance `nextRunAt` in `jobs.json`.

When the user asks to **check heartbeats / tick**:
1. Read `jobs.json`, find all active jobs where `nextRunAt <= now`.
2. For each due job (up to 10 concurrent):
   a. Skip if already running (overlap prevention).
   b. Execute as above.
   c. Advance schedule pointer (even on failure — prevents stuck loops).
3. Report results.

When the user asks to **pause/resume a job**: update status in `jobs.json`.

### Retry Policy

When a job run fails:

```
1. Increment job.retryCount
2. If retryCount <= job.maxRetries:
   a. Compute backoff: config.retryBackoffBaseMs * (2 ^ (retryCount - 1))
      → 30s, 60s, 120s, ... (exponential)
   b. Schedule retry: set nextRunAt = now + backoff
   c. Create new job-run entry with trigger=retry
   d. Log activity: job.retry_scheduled
3. If retryCount > job.maxRetries:
   a. Set job.status = error
   b. Log activity: job.retries_exhausted
   c. Alert user: "🛑 Job '<jobKey>' failed after <maxRetries> retries. Manual intervention required."
4. On next successful run: reset retryCount to 0
```

### Timeout Enforcement

When spawning an agent for a job:
1. Record `startedAt` in the job-run entry.
2. After the agent completes (or if using Bash with timeout), check `durationMs`.
3. If `durationMs > job.timeoutMs`: mark run as `timed_out`, increment retryCount, follow retry policy.
4. For Bash-based adapters, use the Bash tool's `timeout` parameter set to `job.timeoutMs`.

### Overlap Prevention

Before executing any job:
```
1. Check job-runs.json for entries with same jobId AND status=running
2. Count running entries
3. If count >= job.maxConcurrent → skip, log "overlap prevented"
4. Else → proceed with execution
```

---

## Module 5: Activity Log & Redaction

### Data Model

```jsonc
// activity-log.json — append-only array of ActivityEvent
{
  "id": "uuid",
  "timestamp": "ISO8601",
  "actorType": "agent",               // agent | user | system
  "actorId": "UBI-Dev-Agent",
  "action": "issue.status_changed",   // dotted action key
  "entityType": "issue",
  "entityId": "uuid",
  "details": { "from": "todo", "to": "in_progress" },
  "redacted": true
}
```

### Action Vocabulary

| Action | Trigger |
|---|---|
| `agent.registered` | New agent created |
| `agent.paused` | Agent paused (manual or budget) |
| `agent.resumed` | Agent resumed |
| `agent.retired` | Agent permanently retired |
| `agent.error` | Agent entered error state |
| `issue.created` | New issue |
| `issue.status_changed` | Status transition |
| `issue.assigned` | Agent or user assigned |
| `issue.rework` | Sent back from in_review to in_progress |
| `budget.soft_threshold` | 80% spend warning |
| `budget.hard_threshold` | 100% spend, agents paused |
| `budget.resolved` | Incident resolved |
| `job.scheduled` | New job created |
| `job.executed` | Job run completed |
| `job.failed` | Job run failed |
| `job.timed_out` | Job exceeded timeout |
| `job.retry_scheduled` | Retry queued with backoff |
| `job.retries_exhausted` | Max retries reached, manual intervention needed |
| `job.overlap_prevented` | Skipped due to concurrency |

### Redaction Pipeline

Before writing ANY activity log entry, apply redaction:

1. **Path redaction**: Replace `<USER_HOME>/` → `C:\Users\t******\` in all string values.
2. **Username redaction**: Replace `<USER>` → `t******` and `<ADMIN_USER>` → `a**********` in all string values.
3. **Secret redaction**: Replace any value matching `ANTHROPIC_*`, `AZURE_*`, `*_KEY`, `*_SECRET`, `*_TOKEN` patterns with `[REDACTED]`.
4. Apply recursively to all nested objects and arrays in `details`.

---

## Orchestration Workflows

### Workflow: Fan-Out Task Execution

When the user asks to **execute multiple issues in parallel**:

```
1. Read issues.json, filter to assigned + todo issues
2. Group by assigneeAgentId
3. For each agent group (up to config.maxParallelAgents):
   a. Check agent is active + not budget-paused
   b. Check budget before spawning (if config.budgetCheckBeforeSpawn)
   c. Spawn Agent tool with all issue titles/descriptions for that agent
   d. Track execution in issues (lock, status transition)
4. Collect results, transition issues to in_review or blocked
5. Report summary board
```

### Workflow: Morning Standup Report

When the user asks for a **standup** or **status report**:

```
1. Read all state files (issues, agents, jobs, budgets, activity-log)
2. Filter activity-log to last 24 hours
3. Compile and render the following report:
```

**Output template:**

```markdown
## Paperclip Standup — <date>

### Issues (last 24h)
| Change | Count | Details |
|---|---|---|
| New | 3 | #018 UBI refresh fix, #019 GL mapping, #020 PBI model |
| Completed | 2 | #012, #014 |
| Blocked | 1 | #016 — awaiting Prod access |
| In Review | 1 | #015 |

### Agent Activity
| Agent | Runs | ✓ | ✗ | Status |
|---|---|---|---|---|
| UBI-Dev-Agent | 4 | 3 | 1 | ▶ active |
| Audit-Agent | 1 | 1 | 0 | ▶ active |

### Budget Health
| Policy | Spent | Limit | % | Status |
|---|---|---|---|---|
| Q2 AI Spend | $312.40 | $500.00 | [██████░░░░] 62% | OK |

### Upcoming Jobs (next 24h)
| Job | Agent | Next Run | Schedule |
|---|---|---|---|
| ubi-health-check | Audit-Agent | Today 18:00 | Every 6h |

### Attention Required
- 🛑 0 budget incidents
- ⚠ 1 blocked issue: #016
- ⚠ 0 jobs in error state
```

### Workflow: Sprint Planning

When the user asks to **plan a sprint**:

```
1. Show all backlog issues, sorted by priority, as numbered list:
   [1] 🔴 #020 Critical: PBI model refresh broken
   [2] 🟠 #021 High: Add new Gold view for VoC
   [3] 🟡 #022 Medium: Update STM for GL stream
   ...

2. Show agent availability:
   | Agent | Status | Current Load | Skills |
   |---|---|---|---|
   | UBI-Dev-Agent | ▶ active | 1 in_progress | ubi-dev, audit-ubi |
   | AI-Builder | ▶ active | 0 | fluke-ai, ai-use-case-builder |

3. Show budget remaining:
   Q2 AI Spend: $187.60 remaining of $500.00 (62% consumed)

4. Ask user: "Which issues to include? (enter numbers, e.g. 1,2,3)"
5. For each selected issue, ask: "Assign to which agent? (enter agent name)"
6. Move selected issues to todo, set assigneeAgentId, log activity
7. Ask: "Create any recurring jobs for these? (y/n)"
8. If yes, collect cron schedule + prompt for each
9. Display final sprint board
```

---

## Display Conventions

- Tables use markdown pipe format for easy reading
- Status indicators: ▶ (in_progress/active), ⏸ (paused), ✓ (done), ✗ (cancelled), ⚠ (blocked), 🛑 (budget-stopped/error)
- Priorities: 🔴 critical, 🟠 high, 🟡 medium, ⚪ low
- Budget bars: `[████████░░] 82%` (filled/empty blocks, 10-char width)
- Timestamps displayed in user's local time (Eastern), stored as UTC ISO8601
- UUIDs displayed as short form (first 8 chars) in tables, full in detail views

---

## Integration Points

| System | How Paperclip connects |
|---|---|
| **Azure AI Foundry** | Agent spawns use existing `ANTHROPIC_FOUNDRY_API_KEY` + model deployments |
| **LLM Usage Tracking** | Budget module reads from DuckDB / Power BI data |
| **Existing Skills** | Agents reference skills by name (ubi-dev, audit-ubi, fluke-ai, etc.) |
| **Hooks** | All Bash/Agent calls go through existing secret-scanner + command-blocker |
| **Memory** | Activity log supplements (not replaces) auto-memory system |
| **Session Review** | `/session-review` can scan paperclip activity for lessons learned |

---

## First-Run Initialization

On first invocation, if state directory does not exist:

```bash
mkdir -p "<USER_HOME>/Claude\deliverebles\paperclip"
```

Then create each state file with empty defaults:
- `agents.json`: `[]`
- `issues.json`: `[]`
- `budgets.json`: `{"policies": [], "incidents": []}`
- `jobs.json`: `[]`
- `job-runs.json`: `[]`
- `activity-log.json`: `[]`
- `config.json`: `{"version": "1.0", "defaultModel": "claude-opus-4-6", "defaultNode": "flk-team-ai-enablement-ai", "maxParallelAgents": 5, "budgetCheckBeforeSpawn": true, "redactionEnabled": true, "defaultTimeoutMs": 300000, "defaultMaxRetries": 2, "retryBackoffBaseMs": 30000}`

If any state file exists but fails JSON parsing, follow Safety Rule #7 (backup corrupt file, reinitialize, warn user).
