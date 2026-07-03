---
name: audit-ubi
description: "Run a comprehensive health audit across UBI notebooks, ADF pipelines, and Gold views. Use when the user asks to audit, review, or check the health of UBI streams, notebooks, or data quality. Fans out parallel analysis agents by stream, then aggregates findings into a severity-ranked report."
allowed-tools: Read, Grep, Glob, Bash, Agent, Task
---

# UBI Codebase Audit Skill

Run a structured, multi-agent audit of UBI platform artifacts. Produces a severity-ranked findings report with a health dashboard.

## Task Tracking

At the start, use TaskCreate to create a task for each phase:
1. Scope and partition
2. Launch parallel analysis agents
3. Aggregate findings
4. Evaluate and deduplicate
5. Generate audit report

Mark each task in_progress when starting and completed when done.

## Step 1: Scope and Partition

Determine what to audit:
- If the user specifies a stream (e.g., "audit SOBacklog"), scope to that stream's notebooks and Gold views.
- If the user says "full audit" or doesn't specify, partition by stream.

### Partitioning Rules

1. Glob for all `.py` and `.sql` files under `<USER_HOME>/AzureDataBricks\FlukeCoreGrowth\`
2. Partition files by stream directory. Cap at 10 partitions.
3. If a partition has 50+ files, sub-partition by subdirectory (Staging/Mart/Gold).

Record the partition map before proceeding.

## Step 2: Launch Parallel Analysis Agents

For each partition, launch agents in parallel using the Agent tool. Each agent should analyze its partition for the categories below.

### Analysis Categories

**Per-Partition (one agent per partition per category):**

1. **Data Quality Review**
   - Null checks on PK columns present?
   - Row count validations present?
   - Freshness checks present?
   - Referential integrity checks?
   - MERGE idempotency verified?

2. **Security Review**
   - Hard-coded credentials, connection strings, or API keys?
   - Secrets accessed via Key Vault scope (good) vs. plaintext (bad)?
   - `Secure Output` / `Secure Input` on activities handling secrets?
   - Environment-specific values parameterized (not hard-coded)?

3. **Code Quality Review**
   - Standard notebook header present (widgets, imports)?
   - Status check pattern used (etl.status_control)?
   - Error handling: try/except around critical operations?
   - No `display()` or `print()` in production paths?
   - Consistent naming conventions?

4. **Performance Review**
   - Data skew mitigation present for known large tables?
   - Broadcast hints on small dimension joins?
   - `.cache()` / `.checkpoint()` used appropriately (not leaked)?
   - Partition pruning in WHERE clauses?
   - No `collect()` on large DataFrames?

**Project-Wide (one agent each):**

5. **ADF Pipeline Review**
   - Nesting depth within 8-level limit?
   - Retry/timeout configured (not default 7 days)?
   - Error handling paths defined?
   - Triggers active/stopped as expected?

6. **Gold View Consistency**
   - All Gold views reference existing Silver tables?
   - Column aliases are business-friendly (backtick-quoted)?
   - No orphan views (referenced in no downstream consumer)?

### Agent Prompt Template

Each agent should:
- Read all files in its partition
- For each finding, record: File path, line range, category, severity (P0-P3), one-paragraph description
- Return findings as a structured list

## Step 3: Aggregate Findings

Wait for all agents to complete. Collect all findings into a single list.

### Deduplication Rules
- If two findings reference the same file and same issue type, keep only the higher-severity one.
- If two findings conflict (one says "has error handling" and another says "missing error handling" for the same code), flag as conflict — present both and let user decide.

## Step 4: Evaluate and Classify

Apply severity levels to all findings:

### Severity Criteria

- **P0 (Critical):** Data corruption risk, security vulnerability, production blocker. Examples: hard-coded credentials, MERGE without idempotency on production table, missing PK uniqueness check on a table consumed by Power BI.
- **P1 (Urgent):** Will cause issues under load or during edge cases. Examples: missing data skew mitigation on US-heavy tables, no retry on Oracle extraction, no freshness check on daily-refresh table.
- **P2 (Normal):** Violates conventions but works. Examples: missing standard header, `display()` in production notebook, non-standard naming.
- **P3 (Low):** Polish item. Examples: inconsistent spacing, unused imports, redundant comments.

### Finding Output Format

For each finding:
```
### [P<N>] <title (imperative, ≤80 chars)>

**File:** `<file path>` (lines <start>-<end>)
**Category:** <Data Quality | Security | Code Quality | Performance | ADF | Gold Views>

<one paragraph explaining the issue, why it matters, and what to do about it>
```

### Flag Only When ALL Criteria Hold

1. The issue meaningfully impacts data accuracy, security, performance, or maintainability
2. The issue is discrete and actionable (not a general codebase concern)
3. Fixing it does not demand rigor beyond what exists in the rest of the codebase
4. The author would likely fix the issue if aware of it
5. The issue is clearly not intentional

## Step 5: Generate Audit Report

Create a Markdown report at `<USER_HOME>/Claude\deliverebles\UBI_Audit_<YYYYMMDD>.md`

### Report Structure

```markdown
# UBI Codebase Audit Report

**Date:** <date>
**Scope:** <what was audited>
**Partitions:** <N partitions, N files>

## Dashboard

| Category | Health | Findings | P0 | P1 | P2 | P3 |
|---|---|---|---|---|---|---|
| Data Quality | <Pass/Warn/Fail> | <N> | <N> | <N> | <N> | <N> |
| Security | <Pass/Warn/Fail> | <N> | <N> | <N> | <N> | <N> |
| Code Quality | <Pass/Warn/Fail> | <N> | <N> | <N> | <N> | <N> |
| Performance | <Pass/Warn/Fail> | <N> | <N> | <N> | <N> | <N> |
| ADF Pipelines | <Pass/Warn/Fail> | <N> | <N> | <N> | <N> | <N> |
| Gold Views | <Pass/Warn/Fail> | <N> | <N> | <N> | <N> | <N> |

**Health Legend:** Pass = zero P0/P1 | Warn = P1 present, no P0 | Fail = P0 present

## Summary

<3-5 sentence executive summary of overall health and top priorities>

## P0 Findings (Critical)

<all P0 findings in standard format>

## P1 Findings (Urgent)

<all P1 findings>

## P2 Findings (Normal)

<all P2 findings>

## P3 Findings (Low)

<all P3 findings, collapsed or summarized>

## Recommendations

<top 5 prioritized actions>
```

## Rules

- Every analysis category must run for every partition. No category is "obviously fine."
- "The stream is well-established" is not a reason to skip review.
- "There are too many files" is not a reason to reduce scope — partition smaller instead.
- Context window concerns are not a reason to skip a partition. Use subagents.
- If any agent fails or times out, re-dispatch it once; if the re-dispatch also fails, proceed with findings from remaining agents and note the gap.
- Do NOT create findings for patterns that are consistent with the rest of the codebase — only flag deviations.
- Severity P0 means "fix before next production run." Do not use P0 for style issues.
- Every finding must include a file path and line range. "General concern" findings are not actionable.
- Do NOT rewrite code as part of the audit. The audit produces a report, not fixes.

## Six-Step Flow (mapping)

1 Orientation = Step 1 (scope). 1.5 Planning = the partition map + run plan (Step 1 output).
2 Checks-first = analysis categories defined before scanning (Step 2). 3 Execute = agents + the
independent evaluator pass and QA gate per batch. 4 E2E = ledger/report consistency validation
(write ordering + delta reconciliation) before handback. 5 Documentation = report + ledger +
inbox summary.

## Agent Dispatch

When `agents\principal-de-reviewer.md` / `agents\qa-gate.md` exist (export or `~/.claude/agents/`),
dispatch them (evaluator = principal-de-reviewer in **evaluator mode**, naming that section;
terminal artifact checks = qa-gate). When absent, fall back to the inline prompts in this skill.
Evaluator-mode dispatches MUST NOT emit the `QA-GATE-VERDICT-V1` sentinel or any `"gate"` JSON
object. Memory writes go through the orchestrator only (single-writer).

## State Ledger & Delta Reporting

Ledger: `<USER_HOME>/Claude\deliverebles\ubi_audit_ledger.md`. Test invocations may override
ledger/report/inbox/memory paths (never mix test and real paths in one run).
- **Header:** `run_id` (UTC ISO-8601 basic, e.g. `20260703T0630Z`; scheduled reports suffix their
  filename with it), `last_run_utc`, `discovery_mode` (git|hash|mtime|full), `consecutive_failures`.
- **Findings table:** `finding_id | file | category | issue_type | severity | scope | status |
  status_reason | decided_by | decided_utc | first_seen_run | last_seen_run | downgraded_from |
  inconclusive_runs | regressions`. `accepted` rows without `decided_by/decided_utc` are invalid.
- **File-hash table:** `relpath | content_hash | last_scanned_run` for every globbed file;
  `content_hash` = SHA-256 over raw file bytes (no newline normalization).
- **finding_id** = first 12 hex of SHA-256 over
  `lower(relpath-from-glob-root, "/"-separated) + "|" + category + "|" + issue_type`.
  Out-of-root artifacts (ADF pipelines) use logical relpaths: `adf:/<pipeline-name>`.
  Match rule: fresh finding ↔ ledger row iff `finding_id` equal.
- **issue_type enum (closed):** DQ: `DQ-missing-pk-null-check, DQ-missing-rowcount-validation,
  DQ-missing-freshness-check, DQ-missing-referential-check, DQ-merge-not-idempotent`. SEC:
  `SEC-hardcoded-credential, SEC-plaintext-secret-access, SEC-missing-secure-io,
  SEC-hardcoded-env-value`. CQ: `CQ-missing-header, CQ-missing-status-check,
  CQ-missing-error-handling, CQ-debug-output-in-prod, CQ-nonstandard-naming`. PERF:
  `PERF-missing-skew-mitigation, PERF-missing-broadcast-hint, PERF-cache-misuse,
  PERF-missing-partition-pruning, PERF-collect-on-large-df`. ADF: `ADF-nesting-depth,
  ADF-default-timeout, ADF-missing-error-path, ADF-trigger-state`. GOLD:
  `GOLD-missing-silver-ref, GOLD-nonfriendly-alias, GOLD-orphan-view`.
- **Statuses:** `open|fixed|regressed|accepted|unverified|dropped|closed-gone`. Transitions:
  any of {open, regressed, unverified} → `fixed` when an in-scope run no longer detects it;
  `accepted` is terminal (user decision only — the audit never self-accepts); `scope=project`
  findings (ADF, Gold Views) re-evaluate every run; `fixed→regressed` on re-detection (latest
  severity; keep `first_seen_run`); `regressions`+1 on ANY transition into `regressed`, escalate
  to inbox at 2; `dropped→open` on re-detection (re-verify at every severity); file absent →
  `closed-gone`; `closed-gone→regressed` if the file returns with the issue; `unverified→open`
  (original severity restored) on full evidence; `inconclusive_runs` resets on conclusive
  disposition or non-detection, escalates at 3.
- **Write ordering:** findings + report first; file-hash table, then header `run_id`/`last_run_utc`
  LAST (completion marker). Hash rows newer than header `run_id` → ledger unparseable →
  cold-start full sweep.
- **Zero-change rule:** zero changed files and no scope=project firing → delta section says
  "no new findings"; open findings are not re-listed.
- **Hygiene:** NEVER quote secret values — cite file+line only. Ledger is not committed/pushed
  without sanitizing paths/usernames/creds first.
- **Handoff:** each P0/P1 row with status ∈ {open, regressed, unverified} emits
  `file=<path> issue=<finding_id> goal=<fix condition>` — consumable by `data-engineering`.

## Independent Evaluator Pass (before report generation)

Scope: every P0/P1; every P2/P3 on first ledger entry; every downgraded finding on every
appearance; every re-detection of a `dropped` finding. Evaluator = a separately dispatched fresh
`principal-de-reviewer` (evaluator mode) that produced none of the findings and receives only the
structured fields (title, file, line range, category, issue_type, severity). Default: assume the
finding is wrong until the cited lines prove it; run read-only checks where executable and paste
output. Disposition: contradicted → `dropped`; fully evidenced → `open` (downgraded rows: original
severity restored); plausible-not-evidenced → downgrade one level to `unverified`, once per
lifetime (P3 floor: severity unchanged, still `unverified`, downgrade spent). May shard per
partition group; shards count toward the 86 ceiling. Every disposition is written to a report
appendix + the ledger — nothing vanishes silently.

## Scheduling (specified, not activated)

Trigger the NAMED skill (`audit-ubi`) via Claude Code automations or Cowork scheduled tasks.
Decision rule: LOCAL scheduling by default — the source glob and output paths are local-only;
cloud only if/when the codebase is mirrored to a remote repo. Owner: Taashi.
- **Preflight:** source glob, report dir, ledger, or inbox unreachable → abort with an inbox
  entry — NEVER a zero-finding "clean" report. Fallback chain for EVERY inbox write: inbox →
  report dir → direct user message; increment `consecutive_failures` in any abort path that can
  still reach the ledger.
- **Inbox:** `<USER_HOME>/Claude\deliverebles\ubi_audit_inbox.md`, rows
  `| entry_type | run_id | utc | detail |`, `entry_type ∈ {abort, summary, escalation}`.
- **Caps (ALL runs, scheduled or manual):** ≤43 initial dispatches (10 partition-units × 4
  per-partition categories + 2 project-wide + 1 evaluator; sub-partitions share their stream's
  unit; oversized 50+-file streams may shard category agents with explicit accounting) + ≤1
  re-dispatch per failed agent + shards; ABSOLUTE CEILING 86 → abort to inbox. Delta scope > 200
  files → report-and-escalate instead of full fan-out.
- **Run-start self-gate (after preflight):** `consecutive_failures ≥ 2` → write inbox entry and
  exit without auditing until a human resets the counter.
- **Human door:** every scheduled run ends by surfacing the delta summary (inbox `summary` entry
  + message) — never silently filed.
- **Stop boundary (scheduled runs):** writes limited to report/ledger/inbox paths (+ memory via
  the orchestrator); no code edits; no git/network mutations; evaluator restricted to read-only
  commands; any violation → abort to inbox.

## Discovery Modes

Scheduled/ledger-present runs scope to files changed since `last_run_utc` (plus ALL scope=project
categories, every run). Manual runs keep the existing full partition-by-stream default. Change
detection order: git log (if the target is a repo) → content hash vs the ledger's file-hash
table → mtime last resort (caveat: sync rewrites mtimes — expect false positives). Record
`discovery_mode` each run. Cold start (no/unparseable ledger, incl. the completion-marker
inconsistency) → full sweep + ledger rebuild.
