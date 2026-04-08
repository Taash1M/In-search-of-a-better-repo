---
name: polish-notebook
description: "Iterative quality polish loop for Databricks notebooks. Use when the user asks to polish, clean up, review, or improve a specific UBI notebook. Runs lint, test, simplify, review, and re-checks until stable (max 3 iterations)."
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, Task
---

# Databricks Notebook Polish Skill

Run an iterative quality loop on a Databricks notebook. Each iteration: lint → test → simplify → review → fix. Re-runs if any changes are made, up to 3 total iterations.

## Task Tracking

At the start of EACH iteration, use TaskCreate to create a task for each step:
1. Lint check
2. Test validation
3. Code simplification
4. Quality review
5. Apply fixes
6. Change detection

Mark each task in_progress when starting and completed when done. Fresh tasks for each iteration.

## Step 0: Determine Scope

Identify the notebook to polish:
- If the user specifies a file path, use that.
- If the user names a stream, find the primary mart refresh notebook: `FlukeCoreGrowth/Mart/Refresh/Refresh_<StreamName>.py`
- Read the full notebook content before proceeding.

Record:
- Full file path
- Stream name (if applicable)
- Current line count
- Whether a test notebook exists (`Test_Insert_Mart_<StreamName>.py`)

## Step 1: Lint Check

Check the notebook against UBI conventions (from ubi-dev.md):

### Convention Checklist

| Check | Rule | Severity |
|---|---|---|
| Standard header | Notebook must have dbutils.widgets declarations | P2 |
| Standard imports | Must import from pyspark.sql.functions, pyspark.sql.types | P3 |
| Status check | Must check etl.status_control before processing | P1 |
| No hardcoded DBs | Use widget parameters, not literal "flukebi_Dev" | P1 |
| No display() | Production notebooks should not have display() calls | P2 |
| No collect() on large | collect() only on small result sets (< 1000 rows) | P1 |
| Error handling | Critical operations wrapped in try/except | P2 |
| Idempotent writes | MERGE/overwrite mode, not append | P1 |
| Consistent naming | Column aliases follow UBI naming conventions | P3 |

Record all lint findings with file, line, severity, and description.

## Step 2: Test Validation

If a test notebook exists:
- Read the test notebook
- Verify it covers: row counts, PK uniqueness, null checks, freshness, schema validation
- Flag any missing test categories

If NO test notebook exists:
- Flag as P1: "Missing test notebook for <StreamName>"
- Draft a skeleton test notebook (do NOT write it unless asked)

## Step 3: Code Simplification

Look for opportunities to simplify without changing behavior:

- Redundant `.filter()` chains that could be combined
- Nested `CASE WHEN` that could use `COALESCE` or `NULLIF`
- Duplicate column aliasing (same column aliased twice)
- Unused variables or intermediate DataFrames
- SQL that could be simplified with CTEs instead of nested subqueries
- Dead code (commented-out blocks, unreachable branches)

For each simplification, record:
- File, line range
- Current code (2-3 lines max)
- Proposed simplification
- Why it's better (clearer, shorter, same behavior)

### Simplification Criteria — Flag ONLY When ALL Hold

1. The simplification does not change behavior (provably equivalent)
2. The simplified version is clearly more readable
3. The change is not merely stylistic preference
4. The original code is not intentionally verbose (e.g., for debugging clarity)

## Step 4: Quality Review

Review the notebook holistically:

- **Correctness**: Are JOINs correct? Are WHERE clauses filtering as intended? Are aggregations at the right grain?
- **Performance**: Any full table scans that should use partition pruning? Any broadcast-eligible joins missing hints?
- **Data quality**: Are edge cases handled (NULLs, empty strings, negative amounts, future dates)?
- **Maintainability**: Can a new team member understand the flow? Are complex transforms commented?

For each finding, apply severity:
- **P0**: Produces wrong data in production
- **P1**: Fails under specific conditions (large data, NULL edge case, concurrent run)
- **P2**: Violates conventions, works correctly
- **P3**: Polish item

## Step 5: Apply Fixes

Apply all fixes with severity P0 and P1 using the Edit tool. For each fix:
1. Show the before (current code)
2. Apply the edit
3. Verify the edit was applied correctly

For P2 and P3 findings, list them in the output but do NOT apply automatically. The user decides.

## Step 6: Re-Run Check

Check whether any file was edited during Steps 1-5. Any edit counts, regardless of size.

**If any file was edited:** Run `/polish-notebook` again using the Skill tool. This is a full, fresh run — not a lightweight pass.

**If no files were edited:** The notebook is stable. Produce the final polish report.

**Cap at 3 total iterations** (initial run + 2 additional runs) to prevent runaway loops.

## Final Output

After the last iteration (either stable or cap reached), output a summary:

```markdown
## Polish Report: <notebook name>

**Iterations:** <N>
**Files modified:** <list>
**Findings:**

| Severity | Count | Applied | Deferred |
|---|---|---|---|
| P0 | <N> | <N> | <N> |
| P1 | <N> | <N> | <N> |
| P2 | <N> | <N> | <N> |
| P3 | <N> | <N> | <N> |

### Applied Fixes
<list of fixes applied with before/after>

### Deferred Findings (P2/P3)
<list of findings not applied — user decides>
```

## Rules

- Every step must run in every iteration. No change is "self-evidently correct."
- "The notebook is simple" is not a reason to skip steps.
- "The prior iteration covered it" is always wrong — each iteration operates on the current state.
- Context window concerns are not a reason to skip the review step.
- Do NOT add features, refactor architecture, or change the notebook's purpose. Polish means quality improvement within the existing design.
- Do NOT add docstrings, type annotations, or comments to code you didn't change.
- Do NOT modify test notebooks unless they have outright bugs. Test coverage gaps are reported, not fixed.
- If simplification changes behavior in ANY edge case, it is not a simplification — skip it.
- The user's existing patterns are intentional unless provably wrong. Match the codebase style.
