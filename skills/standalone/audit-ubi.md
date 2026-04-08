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

1. Glob for all `.py` and `.sql` files under `C:\Users\tmanyang\AzureDataBricks\FlukeCoreGrowth\`
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

Create a Markdown report at `C:\Users\tmanyang\Claude\deliverebles\UBI_Audit_<YYYYMMDD>.md`

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
- If any agent fails or times out, proceed with findings from remaining agents and note the gap.
- Do NOT create findings for patterns that are consistent with the rest of the codebase — only flag deviations.
- Severity P0 means "fix before next production run." Do not use P0 for style issues.
- Every finding must include a file path and line range. "General concern" findings are not actionable.
- Do NOT rewrite code as part of the audit. The audit produces a report, not fixes.
