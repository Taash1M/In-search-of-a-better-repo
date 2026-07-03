---
name: data-engineering
description: "Data engineering patterns, TDD methodology, code review, and architecture for ETL/ELT pipelines. Trigger on: ETL, pipeline, Bronze, Silver, Gold, Delta Lake, Databricks, ADF, medallion, data quality, schema drift, DuckDB, lakehouse, grain, idempotent, reconciliation, data modeling, SCD, orchestration."
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, Task
---

# Data Engineering

This skill is for producing data engineering work that is **correct, reproducible, well-tuned, and
regression-safe** — not just code that runs once. Data bugs are uniquely dangerous: a pipeline can
exit zero, populate a table, and quietly corrupt every downstream report. So the discipline here is
built around *proving* correctness, not assuming it.

The core idea, drawn from the strongest skills in the field, is to encode **how to work**, not just
what to write. Follow the operating loop below for every task. It is deliberately test-first and
review-driven.

## Contents

Everything is in this one file — the `*§Name*` pointers throughout jump to these headings, none are
external files. A pointer may use a short form that is a substring of the target heading (e.g.
*§Code Review* → "Data Engineering Code Review", *§Databricks* → "Databricks (Spark + Delta + Unity
Catalog)").

- **§The operating loop** — the 6-phase test-first build loop (start here for any build)
- **§Start here — route the task** — decision tree to the right section
- **§Task-type quick routing** — detailed entry-point list
- **§Correctness principles that override convenience** + **§NEVER — the quick-reference list**
- Reference sections:
  - **§Review Gate (3-Persona + QA)** — the phase-5 review gate for artifacts built this session
  - **§Data Engineering Code Review** — the review checklist (also the external-review deliverable)
  - **§Testing & TDD for Data Pipelines** · **§Data Quality & Validation** · **§Troubleshooting Data Pipelines**
  - **§Architecture & Design Patterns** · **§Data Modeling** · **§Orchestration & Scheduling** · **§Streaming & Real-Time**
  - **§Performance & Cost Tuning** · **§Governance, Security & Compliance** · **§Observability, Operations & DataOps** · **§Documenting Data Pipelines**
  - Language idioms: **§Python / PySpark Patterns** · **§SQL & dbt Patterns** · **§Scala / Spark Patterns**
  - Platforms: **§Cloud Overview — Azure / AWS / GCP** · **§Databricks (Spark + Delta + Unity Catalog)** · **§Azure Data Factory (ADF)** · **§BigQuery** · **§AWS Glue** · **§Amazon Redshift**
  - **§UBI Platform Notes** — Fluke-specific medallion, DuckDB, Fabric, and engine-corruption deltas

## Start here — route the task

This skill is one file with many inline reference sections (no separate files to open — every
"see *§Name*" points to a heading **below**). Use this tree to jump to the right place; the
detailed entry-point list is in *§Task-type quick routing*, and the validation + review phases of
the operating loop **always apply** regardless of where you enter.

```
What is the task?
├─ Design the shape (warehouse vs lakehouse, batch vs stream, formats, ingestion)
│     → §Architecture & Design Patterns, then the operating loop
├─ Model data (facts/dims, grain, history/SCD, surrogate keys)
│     → §Data Modeling
├─ Build / modify a pipeline or model (new code, a transform, a load)
│     → full operating loop, phases 1–6 (Orient → Test → Implement → Validate → Review → Guard)
├─ Review existing / someone else's code
│     → operating loop phase 1 (intent + conventions), then §Data Engineering Code Review as the deliverable
├─ Troubleshoot a failure or "the numbers are wrong"
│     → §Troubleshooting Data Pipelines (systematic method; resist guess-and-rerun)
├─ Make it faster / cheaper
│     → §Performance & Cost Tuning (measure first)
├─ Add tests / data-quality checks
│     → §Testing & TDD for Data Pipelines + §Data Quality & Validation
├─ Govern / secure (PII, access, lineage, compliance)
│     → §Governance, Security & Compliance
└─ Operate / deploy / monitor (SLAs, alerting, CI/CD, DR, FinOps)
      → §Observability, Operations & DataOps
```

When you produce a build artifact **in this session**, finish it through the operating loop's
phase 5 — which runs the **3-persona review gate** (see *§Review Gate (3-Persona + QA)*) before the
work is handed back. (An *external* "review my code" request is the §Data Engineering Code Review
deliverable, not the build gate.)

## The operating loop

Run these phases in order. Don't skip ahead to implementation — the early phases are what prevent
the silent failures.

### 1. Orient — understand the contract before touching code

Never generate pipeline code in a vacuum. First establish the **data contract** and discover the
**existing conventions**, because matching the project beats inventing a new style.

Establish, and state back to the user if anything is assumed:
- **Inputs**: sources, schemas, expected volume, freshness/SLA, and which fields can be null or change.
- **Output**: target table/file, its **grain** (one row per *what*?), the partition/cluster strategy,
  and the write mode (append / overwrite / merge / upsert).
- **Invariants**: uniqueness keys, referential expectations, allowed value ranges, row-count
  relationships between source and target.
- **Reload semantics**: must a rerun produce the same result (idempotency)? How are late or
  corrected records handled?

Then discover conventions by reading the repo (or asking): existing models/jobs in the same folder,
naming patterns, the test setup, how other code handles schemas, config, and secrets. Read
*§Code Review* for the discovery checklist.

If the grain, write mode, or idempotency requirement is unclear, ask — these three decisions cause
the majority of data-correctness incidents and can't be safely guessed.

When the task is greenfield **design** rather than editing existing code (e.g. "design a pipeline for
X", "how should we ingest Y", "warehouse or lakehouse?"), do the design before the loop: pick the
architecture pattern, ingestion mode, storage/table format, and modeling approach using
*§Architecture & Design Patterns* and *§Data Modeling*, then drop into the loop to
build it. Don't default to code when the real question is shape.

### 2. Specify behavior as tests first (TDD)

Before implementing, write the checks that define "correct". In data engineering, TDD means encoding
expected **schema, grain, and values**, not just function return values. Start with a tiny set of
representative input fixtures and the exact expected output, plus edge cases (nulls, duplicates,
empty input, late/out-of-order records, type boundaries, timezone edges, unicode).

A minimum first test set asserts:
- **Schema**: output columns, types, and nullability are exactly as contracted.
- **Grain / uniqueness**: the key is unique; no unexpected fan-out from joins.
- **Transformation correctness**: known inputs map to known outputs, including the edge cases.
- **Idempotency**: running twice yields the same result as running once.
- **Volume sanity**: row counts relate to source as expected (no silent row loss or explosion).

These tests should fail first (red), because the implementation doesn't exist yet. See
*§Testing & TDD* for framework-specific harnesses (pytest + chispa for PySpark, dbt
tests + unit tests, Great Expectations / Soda for runtime checks) and ready-to-adapt patterns.

### 3. Implement — minimal, explicit, deterministic

Write the smallest transformation that turns the tests green. Bias toward:
- **Explicit schemas** over inferred ones; pipelines that infer types break silently on new data.
- **Set-based / declarative logic** (SQL, DataFrame ops) over row-by-row loops.
- **Determinism**: never depend on row order; avoid non-deterministic UDFs in keys/dedup; pin
  timezones explicitly; make dedup tie-breaks deterministic.
- **Pushdown-friendly** patterns (filter/project early, partition pruning) so it's fast by construction.
- **Null- and type-safe** handling at every join and cast — the silent killers.

For language-specific idioms read the relevant file: *§Python / PySpark*,
*§SQL & dbt*, or *§Scala / Spark*.

### 4. Run and validate — execute, don't assume

Actually run the code against the fixtures/sample and confirm the tests pass. Then apply the
**data-quality gates** before declaring success — reconciliation (source-to-target counts and control
totals), null/uniqueness/range checks on the real output, and a spot-check of a few rows against the
source by hand. *§Data Quality & Validation* defines the gate framework and the
reconciliation patterns. Wrong-numbers bugs almost always surface here, not in the unit tests.

### 5. Review — the 3-persona review gate

Before handing back any artifact you **built in this session** (code, SQL, a pipeline/notebook, a
DDL/model), run the **3-persona review gate**: three independent reviewers — Solutions Architect,
Enterprise Architect, Principal Data Engineer — adversarially review the artifact, you apply every
finding, and you re-review until a round is clean, then a terminal `qa-gate` check accepts it. The
full mechanism, persona checklists, severity rubric, and termination rule are in
*§Review Gate (3-Persona + QA)*. This is the discipline that catches the silent-failure class a
single self-review misses.

Start by self-reviewing against *§Code Review* (correctness & grain, idempotency & reruns,
performance & cost, security/PII & secrets, observability, error handling & partial-failure recovery,
conventions) — that checklist is also what the three personas apply, re-lensed.

When the user asks you to *review their* (external, already-written) code, you are **not** in the
build gate — the *§Code Review* checklist **is** the deliverable: go through it explicitly and cite
concrete lines.

### 6. Guard against regression — leave correctness in place

A fix isn't done until it can't silently break again:
- Confirm **downstream** dependents still pass (re-run their tests / contract checks). Refactors must
  preserve outputs — diff before/after on a sample.
- Keep the validation **in the pipeline**, not as a one-off — quality checks and contract tests should
  run on every execution so the next regression is caught automatically.
- Add a regression test reproducing any bug you fixed, so it stays fixed.
- Document the contract and any non-obvious decisions (*§Documenting Data Pipelines*).

## Task-type quick routing

The loop adapts to the task. Use these entry points, but the validation and review phases always apply.

- **Design an architecture / pipeline** → *§Architecture & Design Patterns* (medallion, lakehouse
  vs. warehouse, ETL vs. ELT, batch vs. streaming vs. CDC, file & table format selection, ingestion
  patterns), then the loop.
- **Model data** (dimensions, facts, history) → *§Data Modeling* (dimensional/Kimball,
  SCD types 1/2/3, Data Vault, surrogate keys, grain).
- **Create / build a pipeline or model** → full loop, phases 1–6.
- **Orchestrate / schedule** (DAGs, dependencies, retries, backfills) → *§Orchestration & Scheduling*.
- **Build streaming / real-time** → *§Streaming & Real-Time* (exactly-once, watermarks, windowing,
  late data, checkpointing, CDC streams).
- **Review existing / external code** → phase 1 (understand intent + conventions), then
  *§Data Engineering Code Review* as the deliverable (NOT the phase-5 build gate, which is only for
  artifacts you built this session).
- **Troubleshoot a failure or wrong results** → *§Troubleshooting* for the systematic
  diagnosis method (read the real error → reproduce minimally → isolate upstream vs. logic vs.
  environment → fix → add regression test → re-validate). Resist guess-and-rerun.
- **Add tests / quality checks** → *§Testing & TDD* and
  *§Data Quality & Validation*.
- **Make it faster / cheaper** → *§Performance & Cost Tuning* (measure first, then partitioning,
  shuffle, file sizing, predicate pushdown, caching, cost levers).
- **Govern / secure** (PII, access, lineage, compliance) → *§Governance, Security & Compliance*.
- **Operate / monitor / deploy** (SLAs, alerting, CI/CD, DR, FinOps) → *§Observability, Operations & DataOps*.
- **Document** → *§Documenting Data Pipelines*.

## Cross-cutting concerns — always in scope

Correctness is necessary but not sufficient for production data engineering. On any non-trivial task,
also account for these, even when the user doesn't raise them — they're the difference between code
that works and a system an enterprise can run:

- **Governance & security**: classify data, handle PII per policy, use least-privilege access and
  managed secrets, and keep lineage/catalog entries current. See *§Governance, Security & Compliance*.
- **Observability & SLAs**: a pipeline isn't done until failures and freshness breaches are *visible*
  and alert someone. Emit run metrics and wire blocking quality gates. See
  *§Observability, Operations & DataOps*.
- **Operability & deployment**: code lives in version control, deploys through environments
  (dev→staging→prod) via CI/CD and IaC, and supports targeted backfill/reprocessing.
- **Cost**: data systems scale cost with data volume; design for it (pruning, file sizing, right-sized
  compute, auto-suspend) rather than treating it as an afterthought.

Raise these proactively when a request omits them, but stay proportional — a one-off ad-hoc query
doesn't need a DR plan.

## Platform & cloud notes

This skill is cloud-agnostic by design: it reasons in DE primitives (ingest, store, transform,
orchestrate, serve, govern) and maps them onto whichever cloud is in play. Start from
*§Cloud Overview* for the **Azure / AWS / GCP service-equivalence map** and how
to pick — so "do this on GCP" resolves to the right native services even if the user described it in
AWS or Azure terms.

When the work targets a specific engine, read its file for correctness and cost gotchas — they differ
enough to matter: *§Databricks* (multi-cloud Spark/Delta),
*§BigQuery* (GCP), *§AWS Glue* (AWS),
*§Amazon Redshift* (AWS), *§Azure Data Factory* (Azure). Snowflake patterns
live in *§SQL & dbt*; Synapse/Fabric, Athena/EMR, and Dataflow/Dataproc/Composer are
covered in the cloud-overview.

Prefer **portable abstractions** (SQL, Spark, open table formats like Delta/Iceberg, dbt, open
orchestrators) over proprietary lock-in unless the user has chosen a managed service deliberately —
it keeps the solution movable across clouds, which is the whole point of being comfortable on all three.

## Correctness principles that override convenience

These recur across every platform and are worth holding in mind constantly, because each is a common
source of data corruption that *runs clean*:

1. **Idempotency is non-negotiable for production loads.** A rerun after partial failure must not
   double-count or duplicate. Prefer merge/upsert or partition-overwrite over blind append.
2. **Guard the grain.** Every join is a chance to fan out rows. Assert uniqueness of join keys; a
   silently exploded grain is the most common "the numbers are wrong" cause.
3. **Make nulls and types explicit.** Implicit casts, `NULL`-swallowing aggregations, and inferred
   schemas fail quietly on new data. Declare and check.
4. **Handle time correctly.** Pin timezones, define event-time vs. processing-time, and design
   incremental loads for late and out-of-order data with watermarks/lookback windows.
5. **Reconcile.** A pipeline isn't trusted until source and target agree on counts and control totals.
6. **Determinism enables testing.** If the same input can produce different output, you can't test it —
   remove the nondeterminism rather than working around it.
7. **Design for portability and recovery.** Favor open formats and standard SQL/Spark so the solution
   isn't trapped on one cloud, and make every load reprocessable so a bad day is recoverable, not
   catastrophic.

When a request conflicts with these (e.g. "just append it, skip the merge"), implement what's asked
but flag the correctness risk plainly so the user is choosing it with eyes open.

## NEVER — the quick-reference list

Each of these runs clean and corrupts data silently. Treat them as hard stops; if a request forces
one, flag the risk explicitly (above). Detail and platform variants are in the reference sections.

1. **NEVER blind-`append`/`INSERT` to a reloadable target.** A retry double-counts. Use merge/upsert
   or partition-overwrite scoped to the load window — and the scope must name **every** partition
   column the batch spans (a `load_date`-only scope on a `(load_date, region)` table silently wipes
   other regions — see *§Looks-right-but-silently-corrupts*). Make the replace **atomic** (one
   transaction, or `MERGE`/`replaceWhere`), so a mid-step crash can't leave the window half-written.
   ```sql
   -- BAD: rerun after partial failure duplicates the window
   INSERT INTO marts.orders SELECT * FROM staging.orders WHERE load_date = '2024-06-01';
   -- GOOD: idempotent — atomically MERGE on the key. The source MUST be unique on the merge key
   -- first, or Delta errors (DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE) — see
   -- §Looks-right-but-silently-corrupts. So dedup the window to one row per key before merging:
   MERGE INTO marts.orders t
   USING (
     SELECT order_id, customer_id, amount, status, updated_at, ingest_id   -- project the contract, not *
     FROM staging.orders
     QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC, ingest_id DESC) = 1
   ) s
   ON t.order_id = s.order_id
   WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *;
   -- (delete+insert is also fine IF run in ONE transaction and scoped to every partition column)
   ```
   (`SET *`/`INSERT *` propagate the already-projected row, which is the point of an upsert — that's
   not the `SELECT *` rule 2 forbids; rule 2 targets wide columnar *reads* where you scan columns you
   don't need, so the source is projected to the contract above.)
2. **NEVER `SELECT *` through a columnar pipeline.** You pay to read every column and break on schema
   drift. Project only the columns you need.
3. **NEVER rely on schema inference for production reads.** Inference changes with the data and fails
   silently. Declare an explicit schema (it doubles as a contract).
   ```python
   # BAD: types shift when next month's file has a new/empty column
   df = spark.read.json(path)
   # GOOD: explicit, stable, self-documenting
   df = spark.read.schema(SCHEMA).json(path)
   ```
4. **NEVER put a filter on the right table of a `LEFT JOIN` in `WHERE`.** A `NULL` from the
   unmatched side fails the predicate and silently turns it into an inner join.
   ```sql
   -- BAD: drops customers with no order (the NULL fails the WHERE)
   FROM customers c LEFT JOIN orders o ON o.cust_id = c.id WHERE o.status = 'paid'
   -- GOOD: keep the condition in the ON clause
   FROM customers c LEFT JOIN orders o ON o.cust_id = c.id AND o.status = 'paid'
   ```
5. **NEVER dedup / `ROW_NUMBER()` / `LIMIT 1` without a deterministic tie-break.** Equal sort keys
   give nondeterministic, drifting results. Add a secondary key.
   ```sql
   -- BAD: ties on updated_at resolve differently each run
   QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1
   -- GOOD: secondary key breaks ties deterministically
   QUALIFY ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY updated_at DESC, ingest_id DESC) = 1
   ```
6. **NEVER use `Double`/`Float` for money.** Floating point silently loses cents. Use `Decimal`/
   `NUMERIC`, and watch scale truncation on cast.
7. **NEVER use `col NOT IN (subquery)` when the subquery can contain `NULL`.** It returns *no rows*.
   Use `NOT EXISTS`.
8. **NEVER transform/mutate the raw (Bronze) layer in place.** It's the replayable source of truth;
   land it append-only and fix bugs by rebuilding downstream layers, not by editing raw.

---

# Reference Sections

## Review Gate (3-Persona + QA)

This is the operating loop's **phase-5 gate for an artifact you built in this session** (code, SQL, a
pipeline/notebook, a model/DDL). It is an *adversarial, iterative* review by three independent
personas, chained into a terminal `qa-gate` check. It is the Evaluator-optimizer / Sectioning
pattern: a separate screener beats self-review. (This complements, and is distinct from, the broad
plan-hardening loop in the `data-dev-planning` skill — that hardens a **plan**; this hardens a **built
artifact**. They chain, they don't overlap.)

**When it runs:** after the artifact's build steps are done and you've self-reviewed against
*§Code Review*. **Not** for an external "review my code" request — that is the *§Code Review*
deliverable, not this gate.

### Mechanism — review rounds until clean

Run review **rounds** until a full round yields **zero findings at every severity (P0/P1/P2/P3)**.

1. **Dispatch three reviewers in parallel** — Solutions Architect (SA), Enterprise Architect (EA),
   Principal Data Engineer (Principal DE). Run them concurrently (a single message with three
   sub-agent calls, or three focused passes). Each gets the artifact, the data contract (grain/keys/
   write-mode/idempotency), and the real inputs/conventions it touches.
2. **Reviewers are read-only and adversarial** — they return findings only, each as
   `[P<n>] <persona>-<seq> — <title>` + exact location + the data consequence + a concrete fix. The
   highest-value finding is **claim-vs-artifact**: "the code says X but the data/contract shows Y".
3. **Apply every finding**, then **re-run a fresh round**. Later rounds must (a) verify prior fixes
   held and (b) hunt second-order issues the fixes introduced.
4. **Terminate** only on a fully clean round (`P0=0 P1=0 P2=0 P3=0` from all three). **Hard floor: 2
   rounds** even if round 1 looks clean (second-order check). **Upper cap: after round 6** with open
   P2+, stop and **escalate to the user** with the open findings rather than looping forever. Never
   stop early on "only P3s remain" — apply and re-review.

### Severity rubric

- **P0 (Blocker):** will corrupt data / break in prod / violate governance or law. Must fix.
- **P1 (Major):** fails under load or an edge case; missing a required gate, idempotency, or
  fail-closed behavior; a tautological or unfalsifiable check.
- **P2 (Should-fix):** correctness/clarity gap that works but is fragile — missing tiebreaker, dedup
  key, null guard, observability.
- **P3 (Minor):** polish — naming, wording, doc/lineage stamping.

### Persona checklists (re-lensed onto a built artifact)

- **Solutions Architect (SA)** — solution coherence; component fit; integration hand-offs (schemas,
  formats, auth); sequencing/dependencies; **end-to-end data-flow** (trace one record source→target,
  does it survive every stage?); buildability; correct reuse of existing assets.
- **Enterprise Architect (EA)** — data classification & PII handling; secrets & least-privilege
  identity; encryption in transit/at rest; lineage/catalog updated; retention & compliance
  (incl. right-to-erasure reachable); environment separation (dev/prod); **governance gates wired
  into code, not prose** (fail-closed); cost tagging/budget.
- **Principal Data Engineer (Principal DE)** — data-contract completeness (grain, keys, write-mode,
  idempotency, invariants pinned); **TDD/test-first** (schema+grain+values+idempotency+volume-sanity
  asserted); grain/uniqueness guards (no join fan-out); **reconciliation that can actually fail** on
  wrong data (not tautological); determinism (tie-break on every top-1; pinned timezones); quarantine
  vs silent drop; null/type safety at every join & cast; **blocking** gates with a real threshold;
  observability (run-id, row counts in/out, metrics); **silent-failure hunt** (every place the
  pipeline could exit-zero while producing wrong/partial data).

### Terminal QA gate (after the clean round)

The 3-persona loop hardens the artifact; the **`qa-gate`** then verifies the finished artifact
against its Definition of Done — the *last* check before acceptance. For code/SQL artifacts also run
`/code-review` (bugs) + `/simplify` (cleanup); for runnable artifacts (a pipeline/graph load) also run
`/verify` for ground truth.

**Host enforcement posture — determine it once, up front (don't assume):** check whether the
`qa-gate` sub-agent (`~/.claude/agents/qa-gate.md`) and its `qa-gate-enforcer.py` `SubagentStop` hook
are installed.
- **ENFORCED** (both present) → the gate is hard-enforced: the hook blocks completion on
  `verdict: FAIL` (and fail-closed when the verdict sentinel is present but unparseable), and logs
  every decision to a durable ledger. Stamp "blocks until PASS".
- **ADVISORY-ONLY** (hook missing) → the sub-agent still returns PASS/FAIL but **nothing blocks**, and
  there is no automatic audit trail. Compensating controls: print an `ENFORCEMENT: ADVISORY-ONLY`
  banner, write each verdict to a fallback log yourself, and on any FAIL **stop and surface it to the
  user** for explicit accept/defer. **Never stamp "blocks until PASS" on an advisory host.**

**Verdict contract** (the gate emits a fenced ```json block):
`{ artifact, artifact_type, verdict: PASS|FAIL, checks_performed[], findings[{severity,location,issue,required_fix}], accept_rule }`
— **PASS only when zero blocker AND zero major findings.** PASS → accept + advance; FAIL → remediate
and re-run.

# Data Engineering Code Review

Two uses for this section: (1) self-review before handing back any pipeline you wrote, and (2) the
deliverable when the user asks you to review *their* code. In both cases, be concrete — cite specific
lines and explain the data consequence, not just the style preference. Lead with correctness issues
that could corrupt data; cosmetic items come last.

## Step 0 — Understand intent and conventions first

Before judging code, know what it's supposed to do and what the project's norms are. Read sibling
models/jobs, the test setup, and config/secrets handling. A "fix" that ignores project conventions
creates inconsistency debt. If intent is ambiguous, ask rather than assuming.

## The review checklist

Walk these in order. For each finding, state: the line, the risk, and the suggested change.

### 1. Correctness & grain (highest priority)
- What is the output grain, and is it actually unique? Trace every join — could it fan out rows?
  Look for joins on non-unique keys, missing dedup before a join, or `LEFT JOIN` that should be
  `INNER` (or vice versa).
- Are aggregations grouping by the full intended key? A missing `GROUP BY` column silently merges rows.
- Do `NULL`s behave correctly? `NULL` in a join key drops rows; `NULL` in `NOT IN` returns nothing;
  `COUNT(col)` skips nulls while `COUNT(*)` doesn't; `NULL` in arithmetic poisons the result.
- Are casts explicit and safe? Implicit string→number or truncating casts corrupt values.
- Filters: are they applied at the right point, and do they accidentally drop rows that are NULL on
  the filtered column?

### 2. Idempotency & reruns
- If this runs twice (retry after partial failure), does it duplicate or double-count? Blind `INSERT`
  / `append` usually does. Prefer `MERGE`/upsert or partition-overwrite keyed on the load window.
- Is the write atomic enough that a mid-run crash doesn't leave a half-written, queryable table?
- For incremental loads: is the high-water mark advanced only after a successful write? Is there a
  lookback window or merge to absorb late/corrected records?

### 3. Determinism
- Any reliance on row order without an explicit `ORDER BY`? (`LIMIT` without order, `first()`/`row_number()`
  without a deterministic tie-break, `DISTINCT ON` without order.)
- Non-deterministic functions (`current_timestamp`, random, unordered `collect_list`) used inside keys,
  dedup, or anything that must be reproducible?

### 4. Performance & cost
- Filter/project early (predicate & projection pushdown)? Or does it scan/shuffle then filter?
- Partition pruning actually used, or is the whole table scanned? (BigQuery: partition + cluster;
  Spark/Delta: partition columns in the filter; Redshift: sort/dist keys.)
- Avoidable wide shuffles, cross joins, exploding `UDF`s, or `SELECT *` carried through many stages?
- Output file sizing — tiny-files problem (too many small files) or skew on one partition?
- Caching/persistence used where a DataFrame is reused, and unpersisted after? See *§Performance & Cost Tuning*.

### 5. Security, PII & secrets
- Secrets in code or logs? They must come from a secret manager / scope, never hardcoded.
- PII handled per policy (masking, tokenization, restricted columns)? Is PII being logged or written
  to a wide-open location?
- Least-privilege on the connection/role used?

For anything beyond a one-off, also confirm data classification is respected, PII is masked/restricted
per policy, encryption is on, and the catalog/lineage is updated — see *§Governance, Security & Compliance*.

### 6. Observability & operability
- Will a failure be visible? Structured logs with run id, row counts in/out, and meaningful errors?
- Are the data-quality checks present and *blocking* (fail the run) rather than warn-only?
- Can someone reprocess a single date/partition without rerunning everything?

Freshness/volume/schema monitoring and alerting, CI/CD promotion, and DR are covered in
*§Observability, Operations & DataOps* — check them for production-grade pipelines.

### 7. Error handling & partial failure
- Are transient errors retried and permanent errors surfaced? No bare `except: pass` swallowing data loss.
- On partial failure, is the state recoverable (idempotent rerun) or corrupted?

### 8. Tests & conventions
- Do tests exist and actually assert schema, grain, and edge cases — or just that it "runs"?
- Naming, structure, config, and style consistent with the rest of the project?
- Is there dead code, a copy-pasted block that should be a shared function, or a magic constant that
  should be config?

## Output format for a review

Group findings by severity so the user can triage:

```
## Blocking (will produce wrong data or break in prod)
- `orders.sql:42` — join on `customer_email` which is non-unique → fan-out duplicates the order grain.
  Dedupe customers first or join on `customer_id`.

## Should-fix (correctness risk under some inputs / cost)
- ...

## Nits (style, naming, minor)
- ...
```

Always end a review by confirming what's *good* too — it tells the author what to keep, and an
all-negative review gets ignored.

---

# Testing & TDD for Data Pipelines

Data tests fall into two layers, and a healthy pipeline needs both:

- **Unit / transformation tests** — run in CI on fixtures with no live data. Fast, deterministic,
  prove the *logic* is correct. This is where TDD happens.
- **Runtime data-quality checks** — run on every pipeline execution against real data. Prove the
  *data* is correct this run. Covered in *§Data Quality & Validation*; both layers are needed because
  correct logic can still receive bad input.

## The TDD loop for transformations

1. **Red** — write a test with a tiny hand-built input fixture and the exact expected output. Include
   one happy-path row and the edge cases that matter for this transform.
2. **Green** — write the minimal transformation that makes it pass.
3. **Refactor** — clean up while the test stays green.

The discipline that makes this pay off in DE: build the fixture by hand so you *know* the right
answer, rather than running the code and snapshotting whatever it produces (that just freezes bugs).

### Edge cases to cover by default

For almost any transform, add fixtures for: empty input, nulls in every nullable column, duplicate
keys, a value at each type boundary (max int, empty string, zero, negative), timezone boundaries
(DST, UTC midnight), unicode/special characters, and — for incremental logic — late-arriving and
out-of-order records and a reprocessed/corrected record.

## PySpark — pytest + chispa

Use a session-scoped local Spark fixture and `chispa` for DataFrame equality (it gives readable
diffs). Structure transforms as **pure functions of DataFrames** (`def transform(df) -> df`) so they
are testable without I/O — keep `spark.read`/`.write` at the edges.

```python
import pytest
from pyspark.sql import SparkSession, functions as F, types as T
from chispa import assert_df_equality
from my_pkg.transforms import clean_orders  # transform(df) -> df, no I/O inside

@pytest.fixture(scope="session")
def spark():
    s = (SparkSession.builder.master("local[2]").appName("tests")
         .config("spark.sql.shuffle.partitions", "2")          # fast tests
         .config("spark.sql.session.timeZone", "UTC")          # deterministic time
         .getOrCreate())
    yield s
    s.stop()

def df(spark, rows, schema):
    return spark.createDataFrame(rows, schema)

ORDER_SCHEMA = T.StructType([
    T.StructField("order_id", T.StringType(), False),
    T.StructField("amount",   T.DoubleType(), True),
    T.StructField("ts",       T.TimestampType(), True),
])

def test_drops_nulls_and_dedupes_keeping_latest(spark):
    import datetime as dt
    inp = df(spark, [
        ("o1", 10.0, dt.datetime(2024,1,1,0,0)),
        ("o1", 99.0, dt.datetime(2024,1,2,0,0)),   # duplicate key, later -> wins
        ("o2", None, dt.datetime(2024,1,1,0,0)),   # null amount -> dropped
    ], ORDER_SCHEMA)

    expected = df(spark, [("o1", 99.0, dt.datetime(2024,1,2,0,0))], ORDER_SCHEMA)

    out = clean_orders(inp)
    # ignore_row_order because output order is not part of the contract
    assert_df_equality(out, expected, ignore_row_order=True, ignore_nullable=False)

def test_idempotent(spark):
    inp = df(spark, [("o1", 10.0, None)], ORDER_SCHEMA)
    once = clean_orders(inp)
    twice = clean_orders(clean_orders(inp))   # transform must be safe to re-apply
    assert_df_equality(once, twice, ignore_row_order=True)

def test_empty_input_yields_empty_with_correct_schema(spark):
    out = clean_orders(df(spark, [], ORDER_SCHEMA))
    assert out.count() == 0
    assert out.schema == EXPECTED_OUTPUT_SCHEMA  # schema must hold even when empty
```

Assert the **schema explicitly**, including nullability — a transform that returns the right rows but
the wrong types is still broken and will fail downstream. Set `spark.sql.shuffle.partitions=2` and
`master("local[2]")` so the suite is fast.

## pandas / Polars

Use `pandas.testing.assert_frame_equal` (set `check_dtype=True`, `check_like=True` if column order is
not contractual) or Polars' `assert_frame_equal`. Same principle: transforms are pure functions of
frames; build expected output by hand.

## SQL via dbt

dbt gives two complementary mechanisms:

- **Schema tests** (`unique`, `not_null`, `relationships`, `accepted_values`, plus
  `dbt_utils`/`dbt_expectations`) — assert invariants on the *built* model. These are your grain and
  referential guards. Put them in the model's `.yml`.
- **Unit tests** (dbt ≥1.8) — assert that given mock input rows, the model SQL produces expected
  output rows. This is true TDD for SQL: define the mock inputs and expected output, write/fix the
  model until it passes.

```yaml
# models/marts/orders.yml
unit_tests:
  - name: dedupe_keeps_latest
    model: orders
    given:
      - input: ref('stg_orders')
        rows:
          - {order_id: o1, amount: 10, updated_at: '2024-01-01'}
          - {order_id: o1, amount: 99, updated_at: '2024-01-02'}
    expect:
      rows:
        - {order_id: o1, amount: 99}

models:
  - name: orders
    columns:
      - name: order_id
        data_tests: [unique, not_null]      # grain guard
      - name: customer_id
        data_tests:
          - relationships: {to: ref('dim_customers'), field: customer_id}  # referential guard
```

Run `dbt build` (not just `run`) so tests execute alongside the models, and `dbt test` in CI.

## Scala / Spark

Use ScalaTest with a shared `SparkSession` trait and compare via collected, sorted rows or a
DataFrame-equality helper. Keep transforms as `Dataset[A] => Dataset[B]`. See *§Scala / Spark*.

## Putting it in CI

- Run the full unit suite on every PR; it must be hermetic (no network, no live warehouse).
- Run `dbt build` / the integration suite against a small seeded dataset or a CI schema.
- Fail the build on any failing test. A flaky data test usually means hidden nondeterminism — fix the
  nondeterminism (sort keys, pinned timezone, deterministic dedup) rather than retrying.

## Regression tests

Every bug you fix gets a test that reproduces it on the minimal failing input. This is how a pipeline
accumulates protection over time instead of regressing on the same issue twice.

---

# Data Quality & Validation

Unit tests prove the logic is right; runtime validation proves *this run's data* is right. Correct
code fed bad or unexpected input still produces wrong output, so production pipelines need quality
gates that run every execution and **fail the run** when violated. Warn-only checks get ignored until
they cause an incident.

## The validation gate framework

Place gates at three points:

1. **On ingest (input contract)** — validate sources before transforming. Catches upstream breakage
   early and cheaply, and stops bad data from propagating.
2. **On output (output contract)** — validate the result before publishing. The last line of defense.
3. **Reconciliation** — confirm source and target agree. Independent of the transform logic, so it
   catches bugs the unit tests share with the implementation.

## The standard checks

For almost every table, assert:

- **Schema**: expected columns present, correct types, expected nullability. Detect schema drift
  (new/removed/renamed columns, widened types) explicitly rather than letting it pass silently.
- **Grain / uniqueness**: the primary key is unique and non-null. This single check catches most
  join fan-out bugs.
- **Completeness**: required columns are non-null above a threshold; expected partitions/dates are
  present (no missing day).
- **Validity / ranges**: values within allowed sets/ranges (amounts ≥ 0, status in enum, dates not in
  the future).
- **Referential integrity**: foreign keys exist in the parent (orphan rate below threshold).
- **Volume / freshness**: row count within an expected band vs. history (catch silent row loss or
  explosion), and max timestamp recent enough to meet the SLA.

## Reconciliation patterns

Reconciliation is the check that most reliably catches "the numbers are wrong". Compare independent
computations of the same quantity:

- **Row counts**: `count(source after filters) == count(target)` (adjusting for known transforms).
- **Control totals**: `sum(amount)` in source vs. target match within tolerance.
- **Distinct keys**: distinct count of the business key is preserved (or changes by exactly the
  expected dedup amount).
- **Pre/post refactor diff**: when refactoring, run old and new on the same input and diff the
  outputs — they must be identical (or differ only as intended). This is the regression guard.

```sql
-- Reconciliation example: target must not lose or gain rows vs. source for the load window
with s as (select count(*) c, sum(amount) amt from staging.orders where load_date = '2024-06-01'),
     t as (select count(*) c, sum(amount) amt from marts.orders   where load_date = '2024-06-01')
select s.c source_rows, t.c target_rows, s.amt source_amt, t.amt target_amt,
       (s.c = t.c) rows_match, (abs(s.amt - t.amt) < 0.01) amount_match
from s, t;   -- both flags must be true before publishing
```

## Tooling

- **dbt tests** (`unique`, `not_null`, `relationships`, `accepted_values`, `dbt_expectations`,
  `dbt_utils`): the simplest path when you're already in dbt; runs with `dbt build`/`dbt test`. Set
  `severity: error` for blocking checks.
- **Great Expectations**: rich expectation suites, data docs, and validation runs; good for non-dbt
  Python/Spark pipelines that need a catalog of expectations.
- **Soda (Soda Core / SodaCL)**: concise YAML checks, good for monitoring and CI gates.
- **Hand-rolled assertions**: for Spark/SQL, a small set of `assert` queries that the orchestrator
  fails on is often enough and has zero dependencies. Prefer this over no checks at all.

Whatever the tool: checks must be **blocking and version-controlled**, living next to the pipeline so
they run automatically and evolve with the schema.

## Data contracts

For inputs you don't control, encode the expectation as a contract (schema + constraints) and validate
against it on ingest. When the contract breaks, fail loudly with a clear message naming the field and
the violation — this turns a silent downstream corruption into an obvious upstream alert.

## Quarantine, don't drop

When rows fail validation, prefer routing them to a quarantine/dead-letter table with the failure
reason rather than silently dropping them. Dropped bad rows become invisible data loss; quarantined
rows are debuggable and recoverable.

---

# Troubleshooting Data Pipelines

Two failure modes need different approaches: **hard failures** (the job errored/crashed) and **silent
failures** (it succeeded but the data is wrong). Silent failures are more dangerous and need the same
systematic method, not guess-and-rerun. Resist the urge to tweak-and-rerun; each rerun is slow,
costs money, and can compound corruption.

## The systematic method

1. **Read the real error — all of it.** For Spark, the useful cause is usually buried below the top
   stack frame (look for the *root* `Caused by`, the failing stage, and executor logs, not just the
   driver message). For SQL, read the full message and the line/column. Don't act on a paraphrase.
2. **Reproduce minimally.** Shrink to the smallest input and the smallest slice of the pipeline that
   still shows the problem. A failing transform on 3 hand-picked rows is debuggable; a failing 2-hour
   job is not. This step alone solves many bugs.
3. **Isolate the layer.** Decide whether it's:
   - **Logic** — wrong transform, bad join, null handling, type cast. Reproducible on fixtures.
   - **Data** — input violated an assumption (new value, schema drift, nulls, duplicates, late data).
     Reproducible only on the real bad rows.
   - **Environment** — dependency/version, resources (OOM, skew), permissions, config, connectivity.
     Reproducible only in the real environment.
   Binary-search between source and target: query intermediate stages and find the first point where
   the data is wrong. The bug is at that boundary.
4. **Form one hypothesis and test it cheaply** before changing code — a `SELECT` on the suspect data
   beats a full rerun.
5. **Fix at the root.** Don't paper over a data issue with a downstream filter that hides it.
6. **Add a regression test** on the minimal reproducing input so this exact bug can't return.
7. **Re-validate** — rerun the quality gates and reconciliation, and confirm downstream consumers
   still pass.

## Diagnosing "the numbers are wrong" (silent failures)

Work backward from the wrong number:

- **Too many rows / inflated totals** → join fan-out (non-unique join key) or a missing `DISTINCT`/
  dedup. Check `count(*)` vs `count(distinct key)` at each stage.
- **Too few rows / missing data** → an `INNER JOIN` that should be `LEFT`, a filter dropping `NULL`s,
  partition pruning that excluded data, or a high-water mark that skipped a window.
- **Duplicated data after a rerun** → non-idempotent append; needs merge/upsert or partition overwrite.
- **Nulls where there shouldn't be** → failed join (key mismatch, type/whitespace/case differences),
  or a cast that produced `NULL` on bad input.
- **Wrong aggregates** → `NULL`-skipping (`COUNT(col)` vs `COUNT(*)`, `AVG` ignoring nulls), grain not
  what you think (group-by missing a column), or double-counting from fan-out before the aggregate.
- **Off-by-a-day / wrong time** → timezone mismatch (storage UTC vs. session local), event-time vs.
  processing-time confusion, or DST. Pin timezones and compare raw timestamps.
- **Numbers drift over time** → late-arriving data not reprocessed, or a non-deterministic dedup
  tie-break.

## Common Spark errors

- **`OutOfMemoryError` / executor lost** → skew (one key dominates), too-large broadcast, collecting to
  driver, or wide shuffle. Check the Spark UI stage with the largest shuffle; salt skewed keys; raise
  `autoBroadcastJoinThreshold` only deliberately. See *§Performance & Cost Tuning*.
- **`AnalysisException: cannot resolve` / column not found** → schema drift or a typo; print the actual
  schema at that point.
- **Serialization / task not serializable** → capturing a non-serializable object in a closure/UDF.
- **Nondeterministic / shuffle-related test flakiness** → unsorted output compared as ordered, or a
  nondeterministic key.

## Common SQL / warehouse errors

- **Division / type errors** → guard division by zero (`NULLIF`), cast explicitly.
- **`GROUP BY` errors** → a selected column not in `GROUP BY` or an aggregate.
- **Timeouts / huge scans** → missing partition filter or cluster/sort key; see the platform file.
- **Permission denied** → role/grant issue, not a logic bug.

## When stuck

If three hypotheses fail, the assumption is wrong, not the code. Re-examine the data contract: dump
the actual schema, a sample of real rows, the actual row counts, and the actual values in the suspect
column. The discrepancy between assumed and actual is the bug.

---

# Architecture & Design Patterns

Use this when designing a pipeline or platform, before writing code. The job here is to pick the right
**shape** — getting this wrong is far more expensive than any code bug because it's hard to reverse.
Decide deliberately; default to the simplest pattern that meets the freshness, scale, and cost
requirements.

## Warehouse vs. lake vs. lakehouse

- **Data warehouse** (BigQuery, Snowflake, Redshift, Synapse): structured, SQL-first, strong governance
  and BI performance. Choose for analytics on mostly-structured data where SQL skills dominate.
- **Data lake** (object store + files): cheap, any format, but no transactions/schema enforcement on
  its own — easy to turn into a swamp. Rarely the right *final* answer alone now.
- **Lakehouse** (Delta/Iceberg/Hudi on object store + a query engine): warehouse-grade ACID, schema
  enforcement, and time travel directly on cheap lake storage. The default modern choice for new
  platforms — open formats keep it portable across clouds.

Pick warehouse for "we live in SQL and BI"; lakehouse for "mixed workloads, ML, big data, open
formats, multi-engine, cost-sensitive".

## Medallion (bronze/silver/gold) layering

A clean, widely-applicable layering for lakehouse/warehouse pipelines:

- **Bronze (raw)**: land source data as-is, append-only, with ingestion metadata (source, load
  timestamp, batch id). Never transform here — it's your replayable source of truth.
- **Silver (cleaned/conformed)**: validated, deduped, typed, conformed to a standard schema; joins to
  reference data. This is where the quality gates and grain discipline live.
- **Gold (curated/serving)**: business-level aggregates, dimensional models, and marts consumers query.

The value: each layer is reprocessable from the one before it, so a bug is fixed by rebuilding
downstream layers rather than re-ingesting. Maps onto dbt's staging→intermediate→marts (*§SQL & dbt*).

## ETL vs. ELT

- **ELT** (load raw, transform in-warehouse): the default today — cheap storage + powerful warehouse
  compute means you load first and transform with SQL/dbt, keeping raw data for replay. Choose unless
  you have a reason not to.
- **ETL** (transform before load): use when you must mask/filter PII before it lands, when the target
  can't transform efficiently, or for heavy non-SQL transforms (better in Spark).

## Batch vs. micro-batch vs. streaming vs. CDC

Pick by **required freshness**, not by fashion — streaming is markedly harder to build and operate.

- **Batch** (hourly/daily): simplest, cheapest, easiest to test and reprocess. Default for analytics
  that tolerate minutes-to-hours latency.
- **Micro-batch** (e.g. Spark Structured Streaming `Trigger.AvailableNow`/short intervals): near-real-time
  with batch-like simplicity and exactly-once via checkpoints. A great middle ground.
- **Streaming** (continuous, Flink/Kafka Streams/Structured Streaming): seconds latency, but you take
  on watermarks, windowing, state, and exactly-once complexity. Use only when seconds matter. See
  *§Streaming & Real-Time*.
- **CDC** (change data capture from a source DB via Debezium/native logs): propagate inserts/updates/
  deletes incrementally. The right way to mirror an operational DB without full reloads; pairs with
  merge/upsert at the target. Handle deletes and out-of-order changes explicitly.

The **Lambda** pattern (parallel batch + speed layers) is largely superseded by **Kappa**
(stream-only, reprocess by replaying the log) and by micro-batch lakehouses — prefer one pipeline that
handles both speeds over maintaining two.

## File formats & table formats

- **File format**: use columnar **Parquet** (or ORC) for analytics — never CSV/JSON for large
  analytical storage (no pushdown, no stats). **Avro** for row-oriented streaming/serialization where
  schema evolution matters.
- **Table format** (transaction layer over files):
  - **Delta Lake** — strongest on Databricks/Spark; ACID, time travel, `MERGE`, mature.
  - **Apache Iceberg** — the most open/engine-neutral (Spark, Flink, Trino, Snowflake, BigQuery,
    Dataproc all read it); best choice for multi-engine, cross-cloud, lock-in-averse platforms.
  - **Apache Hudi** — strong for streaming upserts/incremental CDC ingestion.
  All three give ACID, schema evolution, time travel, and upserts; pick by engine ecosystem. For
  maximum portability across Azure/AWS/GCP, **Iceberg** is the safest default.

## Ingestion patterns

- **Full load**: simple, fine for small/reference tables; reprocess by overwrite.
- **Incremental by watermark**: load `> last_high_water_mark` with a **lookback window** for late data,
  upsert at the target. The workhorse for large tables.
- **CDC**: stream change events, merge by key, handle deletes. Best fidelity for operational mirrors.
- **File-arrival**: event/notification-driven ingestion (Auto Loader, S3 events, Pub/Sub
  notifications) — cheaper and faster than directory re-listing.
Always capture ingestion metadata (source, load time, batch id) so loads are auditable and replayable.

## Idempotent pipeline shape

Regardless of pattern, structure each stage so a rerun is safe: read input window → transform (pure)
→ validate → **idempotent write** (merge/upsert or partition-overwrite scoped to the window) → advance
the watermark only on success. This single shape prevents the duplicate-on-retry class of bugs.

## A note on data products / mesh

For large orgs, consider domain-oriented **data products** (owned, documented, contracted, discoverable
datasets) over one central monolith — but only when org scale justifies the coordination overhead.
Don't impose mesh on a small team; impose clear ownership and contracts (*§Governance, Security & Compliance*)
regardless of scale.

---

# Data Modeling

Modeling decisions outlive code. A wrong grain or a botched history strategy corrupts every report
built on top, so model deliberately. This file covers the patterns a Principal Data Engineer is
expected to apply correctly.

## Establish the grain first

Every table has exactly one grain — "one row per ___". Decide and document it before modeling. Most
modeling bugs (double-counting, fan-out, wrong aggregates) are grain confusion. Facts and dimensions
each have their own grain; never mix grains in one table.

## Dimensional modeling (Kimball)

The default for analytics/BI:

- **Fact tables**: measurements at a defined grain (one row per transaction/event/snapshot). Contain
  numeric **measures** + foreign keys to dimensions. Types: transaction (one row per event),
  periodic snapshot (one row per entity per period), accumulating snapshot (one row per process
  instance, updated as it progresses).
- **Dimension tables**: descriptive context (customer, product, date). Wide, denormalized, with a
  **surrogate key** as PK.
- **Star schema** (facts + denormalized dims) is the default — fast and simple for BI. **Snowflake
  schema** (normalized dims) only when dimension reuse/maintenance demands it.
- **Conformed dimensions**: shared dimensions (date, customer) used consistently across facts so
  metrics are comparable across the business.

### Surrogate keys

Use a system-generated surrogate key (sequence/hash) as the dimension PK rather than the source's
natural/business key. It decouples the warehouse from source key changes and is required for SCD
Type 2 (where one business key maps to multiple historical rows). Keep the natural key as an
attribute for lineage.

## Slowly Changing Dimensions (SCD) — handle history explicitly

How you treat a changed attribute is a correctness decision with reporting consequences:

- **Type 0** — never changes (e.g. original signup date).
- **Type 1** — overwrite; keep only the current value. Simple, but destroys history (past reports
  silently change). Use when history doesn't matter.
- **Type 2** — add a new row per change with `valid_from`/`valid_to`/`is_current` (and a new surrogate
  key). Preserves full history; facts join to the dimension row that was current *at the event time*.
  The default when historical accuracy matters. Watch: get the effective-dating and current-flag logic
  right, and make the load idempotent (re-running a day must not create duplicate versions).
- **Type 3** — keep a "previous" column alongside "current". Rare; only for one-step-back needs.

```sql
-- SCD Type 2 merge sketch: close the old version, insert the new when tracked attrs change
merge into dim_customer t
using staging_customer s on t.customer_nk = s.customer_nk and t.is_current
when matched and (t.address <> s.address or t.tier <> s.tier) then
  update set t.valid_to = current_date - 1, t.is_current = false
-- then a second insert step adds the new current row with a fresh surrogate key
```

dbt offers **snapshots** to implement SCD Type 2 declaratively — prefer them over hand-rolled merges
when on dbt.

## Data Vault

For large, audit-heavy, multi-source enterprises that need agility and full lineage: **hubs**
(business keys), **links** (relationships), **satellites** (descriptive, time-stamped attributes).
More moving parts than Kimball and not query-friendly directly — typically Raw Vault → Business Vault
→ Kimball marts for consumption. Choose only when auditability and source-agnostic integration justify
the complexity; otherwise Kimball is simpler and faster to deliver.

## Normalization vs. denormalization

- **3NF** in operational/source systems and sometimes a staging layer — reduces update anomalies.
- **Denormalize** in the serving/gold layer for query performance (star schema, wide tables) — analytic
  engines favor fewer joins and columnar scans. Match the layer to its job (*§Architecture & Design Patterns*).

## Semantic layer

Define metrics once (dbt Semantic Layer / metrics layer / BI semantic model) so "revenue" means the
same thing everywhere. Prevents the classic problem of five dashboards with five different numbers for
the same metric. Encode the metric definition with the model, not in each BI tool.

## Modeling checklist

- Grain stated and unique (tested with `unique`/`not_null` on the key)?
- Surrogate keys on dimensions; natural keys retained as attributes?
- History strategy (SCD type) chosen deliberately per attribute and idempotent on reload?
- Facts join to the correct dimension version (point-in-time for Type 2)?
- Conformed dimensions reused rather than re-derived?
- Metrics defined once in a semantic layer?

---

# Orchestration & Scheduling

Orchestration is where correctness meets operability: the same transform can be correct in isolation
and still corrupt data if scheduled, retried, or backfilled wrongly. Design the DAG so every task is
**idempotent, retryable, and reprocessable by partition**.

## Principles that apply to every orchestrator

- **Tasks must be idempotent.** A retried or re-run task must not duplicate or double-count. This is
  what makes retries and backfills safe. Pair with idempotent writes (*§Architecture & Design Patterns*).
- **Parameterize by run window** (logical/data interval), not "now". The task processes *its* date
  partition, so re-running 2024-06-01 always reprocesses that exact window — enabling clean backfills.
- **Make dependencies explicit and data-aware.** A task should run when its inputs are *ready*
  (data/asset available), not just on a clock. Use sensors/asset-awareness over blind time offsets.
- **Retries for transient, fail-fast for permanent.** Configure bounded retries with backoff for
  flaky I/O; surface logic/data errors immediately rather than retrying into the same failure.
- **Small, single-purpose tasks** over giant monolithic ones — easier to retry, observe, and
  reprocess the failed part only.
- **Atomic publish.** Write to a staging/temp location, validate, then swap/merge — so a mid-DAG
  failure never leaves a half-built table queryable.

## Backfill & reprocessing

A first-class requirement, not an afterthought. Design so you can reprocess one date, a range, or a
single partition without rerunning everything and without duplicating. Partition-scoped idempotent
writes + run-window parameterization make `backfill 2024-01-01..2024-03-31` safe and trivial. Document
the backfill command in the runbook (*§Documenting Data Pipelines*).

## Airflow

- Use **datasets / data-aware scheduling** (or sensors) so DAGs trigger on data readiness.
- Parameterize with the **logical date** (`{{ ds }}`/`data_interval_start`); never use `datetime.now()`
  inside a task — it breaks backfills and idempotency.
- Keep tasks idempotent and set `retries` + `retry_delay`; use `max_active_runs`/pools to bound
  concurrency and protect downstream systems.
- Prefer the **TaskFlow API** and deferrable/async operators for efficiency; push heavy compute to the
  warehouse/Spark, not the Airflow workers.
- Managed flavors: **MWAA** (AWS), **Cloud Composer** (GCP), Astronomer.

## Dagster

- **Software-defined assets** model the data, not just tasks — Dagster knows what each asset depends on
  and can materialize/backfill by partition automatically.
- Use **partitions** (daily/hourly) so backfills and reprocessing are built-in; **asset checks** embed
  data-quality gates next to the asset.
- Strong typing, lineage, and observability out of the box — a good fit when you want data-centric
  orchestration with built-in quality.

## Cloud-native orchestrators

- **Azure Data Factory / Synapse Pipelines**: low-code; parameterize everything, use watermark control
  tables, retries, and validation activities. See *§Azure Data Factory*.
- **AWS Step Functions** (+ **Glue Workflows**, EventBridge schedules): state-machine orchestration with
  built-in retry/catch; good for serverless ETL chaining Glue/Lambda/EMR.
- **GCP Cloud Composer** (managed Airflow) or **Workflows** (lightweight serverless) + Dataflow/Dataproc.

## dbt within orchestration

`dbt build` (models + tests together) is usually one orchestrated task; let the orchestrator handle
scheduling, retries, and upstream sensors while dbt manages intra-project DAG order. Fail the
orchestrated task on any dbt test failure so bad data blocks downstream.

## Failure handling & alerting

- On failure: route to alerting (the on-call should know within the SLA), and make the state
  recoverable via idempotent rerun rather than manual cleanup.
- Distinguish **data-quality failures** (block downstream, alert data owner) from **infra failures**
  (retry, alert platform team). See *§Observability, Operations & DataOps*.
- Avoid silent success-on-empty: if an upstream produced zero rows unexpectedly, that's usually a
  failure, not a no-op.

---

# Streaming & Real-Time

Streaming is correctness on hard mode: unbounded data, out-of-order arrival, and state make many
batch assumptions false. Only build streaming when the latency requirement (seconds) genuinely
demands it — micro-batch is far easier to operate and test (*§Architecture & Design Patterns*). When you do,
get these fundamentals right.

## Delivery semantics — be explicit about which you have

- **At-most-once**: may lose data. Almost never acceptable for data engineering.
- **At-least-once**: never loses, may duplicate. Acceptable only if the sink is idempotent (dedup by
  key / upsert) so duplicates collapse.
- **Exactly-once (effectively-once)**: no loss, no duplicates — achieved via **checkpointing +
  idempotent/transactional sinks**, not magic. Spark Structured Streaming and Flink provide it with
  proper checkpoint config and supported sinks. Confirm your sink actually participates; an
  exactly-once engine writing to a non-transactional sink is really at-least-once.

The pragmatic default: at-least-once delivery + idempotent merge/upsert at the sink keyed on a unique
event id. This survives reprocessing and replays cleanly.

## Event time vs. processing time, and watermarks

- Process on **event time** (when it happened), not **processing time** (when it arrived), or your
  windows are wrong whenever ingestion lags.
- A **watermark** tells the engine "no more events older than T are expected", letting it close windows
  and bound state. Set it to your tolerated lateness (e.g. 10 min). Events later than the watermark are
  dropped or sent to a side output — decide which and handle it.
- Too-tight watermark drops late data; too-loose watermark grows state unboundedly. Tune to real
  lateness observed in the data.

## Windowing

- **Tumbling** (fixed, non-overlapping) — standard periodic aggregates.
- **Sliding** (overlapping) — moving averages.
- **Session** (gap-based) — user activity bursts.
Aggregations are stateful; the state must be checkpointed so a restart resumes correctly.

## State & checkpointing

- Checkpoint to durable storage; on restart the job resumes from the last checkpoint — this is what
  makes exactly-once and recovery possible. Never delete checkpoints casually; a lost checkpoint can
  mean reprocessing or gaps.
- Bound state with watermarks and TTLs or it grows forever (the #1 streaming OOM cause).
- A **code/schema change** can be incompatible with an existing checkpoint — plan migrations (drain,
  or use compatible state schema evolution).

## Sources & sinks

- **Brokers/logs**: Kafka, AWS Kinesis, GCP Pub/Sub, Azure Event Hubs — durable, replayable logs.
  Replayability is what lets you reprocess (Kappa); preserve it.
- **Stream processors**: Spark Structured Streaming (great with Delta/lakehouse, micro-batch or
  continuous), Apache Flink (true streaming, rich state/windowing), Kafka Streams.
- **Sinks**: prefer transactional/idempotent sinks (Delta/Iceberg/Hudi tables, upsert to a warehouse)
  so at-least-once delivery doesn't duplicate.

## Streaming CDC

Mirror an operational DB by streaming change events (Debezium → Kafka) and merging into a lakehouse
table keyed on the PK. Handle **deletes** (tombstones) and **out-of-order** updates (apply by event
version/timestamp, not arrival order) explicitly, or you'll resurrect deleted rows or apply a stale
update over a fresh one. Hudi/Iceberg/Delta `MERGE` is the typical landing pattern.

## Testing streaming

- Unit-test the transform logic as a pure function on a bounded batch — the same `transform(df)` runs
  in batch and stream, so most logic is testable without a live stream.
- Test windowing/lateness with synthetic out-of-order and late events.
- Test restart-from-checkpoint and reprocessing for exactly-once behavior.
- Test the idempotency of the sink merge under duplicate delivery.

## Operability

Monitor **consumer lag**, **watermark progress**, **state size**, and **checkpoint duration** — these
are the streaming-specific health signals. Rising lag or stalled watermark means the pipeline is
falling behind or wedged. See *§Observability, Operations & DataOps*.

---

# Performance & Cost Tuning

Optimize in this order: **measure → reduce data scanned → reduce shuffle → right-size output →
tune resources**. Never tune by guessing — get the actual bottleneck first, because the slowest stage
is usually not where intuition points.

## 1. Measure first

- **Spark**: read the Spark UI / query plan (`df.explain("formatted")`). Find the longest stage, the
  largest shuffle (bytes), and any skew (one task far slower than the rest). The plan shows whether
  filters pushed down and whether a join broadcast or shuffled.
- **SQL warehouses**: read the query profile / `EXPLAIN`. Look for full table scans, large
  redistributions/broadcasts, and bytes scanned (which is what you're often billed on).

Optimize the dominant cost, then re-measure. Stop when it's good enough — over-tuning has diminishing
returns.

## 2. Reduce data scanned (usually the biggest win)

- **Predicate pushdown**: filter as early as possible, on partition/cluster columns, so the engine
  skips files/blocks. A filter on a non-partition column still scans everything.
- **Projection pushdown**: select only needed columns; never carry `SELECT *` through a columnar
  pipeline — you pay for every column read.
- **Partition pruning**: ensure the filter references the partition column directly (not wrapped in a
  function that defeats pruning, e.g. `WHERE date(ts) = ...` on a non-date-partitioned table).
- **Incremental processing**: process only the new/changed window instead of full reloads.

## 3. Reduce shuffle (the main Spark cost)

- **Broadcast the small side** of a join (`broadcast(df)`) when it fits in memory — turns a shuffle
  join into a map-side join.
- **Pre-aggregate before joining** to shrink the shuffled volume.
- **Filter before join**, not after.
- **Avoid repeated repartitioning**; set `spark.sql.shuffle.partitions` to match data size (the
  default 200 is wrong for both tiny and huge data). With Adaptive Query Execution (AQE) on, it
  coalesces automatically — keep AQE enabled.
- **Handle skew**: if one key dominates, salt it (add a random prefix, aggregate, then combine) or
  enable AQE skew-join handling. Skew shows up as one straggler task in the UI.

## 4. Right-size output files

- **Small-files problem**: thousands of tiny files cripple read performance and metadata operations.
  Coalesce/repartition to target ~128 MB–1 GB files; on Delta use `OPTIMIZE`/auto-compaction; on
  Iceberg use compaction/rewrite.
- **Over-partitioning**: too many partition values (e.g. partition by a high-cardinality id) creates
  the small-files problem and slow planning. Partition by columns you filter on, with reasonable
  cardinality (often date).
- **Compression & format**: use columnar formats (Parquet/ORC) for analytics; pick a sensible codec
  (Snappy for balance, Zstd for ratio).

## 5. Caching / persistence (Spark)

- Persist a DataFrame only if it's reused multiple times *and* recomputation is expensive; otherwise
  caching wastes memory and can spill. Unpersist when done. Caching a once-used DataFrame is a common
  anti-pattern that hurts.

## 6. Resource tuning (last resort)

Only after the logic is efficient: adjust executor cores/memory, partition count, and autoscaling.
Throwing hardware at a skewed or full-scan query is expensive and often doesn't help.

## Cost levers by platform

- **BigQuery**: bytes scanned drives cost — partition + cluster tables, select only needed columns,
  avoid `SELECT *`, materialize intermediate results, and prefer partition filters. Consider
  capacity/slot pricing for steady workloads.
- **Snowflake**: warehouse size and auto-suspend; cluster keys for large tables; result caching;
  avoid spilling to disk (size the warehouse to the query). See *§SQL & dbt*.
- **Databricks/Spark**: photon, AQE, right-sized clusters, `OPTIMIZE`/Z-ORDER on Delta, autoscaling,
  serverless where it reduces idle cost. See *§Databricks*.
- **Redshift**: dist key (collocate joins), sort key (range-restrict scans), `VACUUM`/`ANALYZE`,
  avoid broadcast of large tables. See *§Amazon Redshift*.

## Always re-validate after tuning

A faster query that returns different numbers is a regression, not an optimization. Re-run the
reconciliation and tests after any performance change, and diff the output against the pre-tuning
result on a sample.

---

# Governance, Security & Compliance

The Enterprise Architect's domain: the controls that let an organization trust and legally operate a
data platform. Build these in from the start — retrofitting governance onto a live platform is
painful and risky. Apply proportionally: a regulated enterprise needs all of it; a small internal tool
needs the essentials (secrets, least privilege, PII awareness).

## Classify data first

You can't protect what you haven't classified. Tag datasets/columns by sensitivity (public, internal,
confidential, PII/PHI/PCI). Classification drives every downstream control: access, masking,
encryption scope, retention, and audit. Record it in the catalog, not in someone's head.

## PII and sensitive data handling

- **Minimize**: don't ingest or persist PII you don't need.
- **Mask / tokenize / pseudonymize**: expose masked or tokenized values to general users; restrict raw
  PII to a small, audited group. Prefer transforming PII out (ETL) before it lands in broad-access
  layers when feasible.
- **Never log PII or secrets.** Scrub logs and error messages.
- **Column-level access**: use column masking / row-level security (Unity Catalog, BigQuery policy
  tags / authorized views, Snowflake masking policies, Lake Formation) so the same table serves
  different audiences safely.

## Access control — least privilege

- Grant the minimum needed; prefer **role/attribute-based** access over per-user grants.
- Pipelines run under **service identities** (managed identities / service accounts / IAM roles) with
  scoped permissions — never personal credentials, never broad admin.
- Separate environments (dev/staging/prod) with separate credentials and data; prod data access is
  restricted and audited.

## Secrets & encryption

- Secrets live in a **managed secret store** (Azure Key Vault, AWS Secrets Manager/SSM, GCP Secret
  Manager, Databricks secret scopes) — never in code, config files, notebooks, or logs.
- **Encryption in transit** (TLS) and **at rest** (cloud-managed keys by default; **customer-managed
  keys / CMEK** when policy requires control over the key). Confirm both are on; they usually are by
  default on managed services but verify for compliance.

## Compliance (GDPR / CCPA / HIPAA / etc.)

- **Right to erasure / deletion**: you must be able to find and delete an individual's data across all
  layers, including the immutable raw layer and backups. Open table formats' `DELETE`/`MERGE` (Delta/
  Iceberg/Hudi) make targeted deletes feasible on the lake — design keys so a person's records are
  findable. Plan this *before* you need it; "we can't delete from raw" is a compliance failure.
- **Data residency**: keep data in required regions; pin storage/compute regions accordingly.
- **Audit & lineage**: maintain who-accessed-what and where-data-came-from. Required for audits and
  invaluable for impact analysis.
- **Consent & purpose limitation**: only use data for permitted purposes; track it.

## Retention & lifecycle

Set retention per classification and regulation; expire/delete on schedule (lifecycle policies on
object storage, table retention, `VACUUM` mindful of legal-hold needs). Indefinite retention is both a
cost and a liability.

## Lineage & cataloging

A current catalog with lineage is the backbone of governance — it answers "where did this come from",
"what breaks if I change this", and "who can see this". Use the platform's catalog:

- **Azure**: Microsoft Purview (+ Unity Catalog on Databricks).
- **AWS**: Glue Data Catalog + Lake Formation (permissions), DataZone.
- **GCP**: Dataplex / Data Catalog.
- **Cross-platform**: Unity Catalog (Databricks), OpenLineage standard, dbt docs for model lineage.

Keep lineage and column docs current as part of the same PR that changes the pipeline
(*§Documenting Data Pipelines*) — stale lineage is worse than none.

## Data contracts as governance

Encode producer↔consumer expectations (schema + constraints + SLA + ownership) as versioned, validated
contracts. A contract breach fails the producer's pipeline loudly instead of silently corrupting
consumers. This is how you enforce quality and ownership at organization scale
(*§Data Quality & Validation*).

## Review hook

Every pipeline review (*§Code Review*) must check: classification respected, no secrets/PII in code
or logs, least-privilege identity, encryption on, retention set, lineage/catalog updated.

---

# Observability, Operations & DataOps

Correct code that fails silently in production is still an incident. This file covers making pipelines
observable, deployable, recoverable, and cost-controlled — the operational maturity an Enterprise/
Solutions Architect expects. Apply proportionally to the criticality of the data.

## Observability — make failure and drift visible

Logging alone isn't observability. Instrument these signals and alert on them:

- **Freshness / timeliness**: is the data as recent as the SLA requires? Alert when the latest
  partition/timestamp is older than threshold — stale data is the most common silent failure.
- **Volume**: row counts within an expected band vs. history. A sudden drop (silent row loss) or spike
  (fan-out) should page someone.
- **Schema drift**: new/removed/changed columns or types detected and surfaced, not silently absorbed.
- **Quality-check results**: the blocking gates from *§Data Quality & Validation* emit pass/fail
  metrics, not just halt the run.
- **Distribution drift**: key metrics (null rate, distinct counts, value ranges) tracked over time so
  gradual degradation is caught.
- **Pipeline health**: run duration, success/failure, retries, cost per run; for streaming, consumer
  lag, watermark progress, state size (*§Streaming & Real-Time*).

The "five pillars" framing (freshness, volume, schema, distribution, lineage) is a useful checklist.
Tools: native cloud monitoring + the quality framework you already run, or data-observability platforms
(Monte Carlo, Soda, Great Expectations data docs). Start with freshness + volume + quality gates — they
catch most incidents cheaply.

## Alerting that works

- Alert the **right owner** (data owner for quality, platform team for infra) within the SLA.
- Distinguish severity: a failed prod load with downstream consumers pages; a dev-env hiccup doesn't.
- Make alerts actionable — include run id, partition, and the failing check, so the responder can act
  without spelunking.
- Avoid alert fatigue: tune thresholds against history; a check that cries wolf gets muted and then
  misses the real incident.

## DataOps — CI/CD for data

- **Everything in version control**: pipeline code, SQL/dbt models, IaC, and the tests/contracts.
- **CI on every PR**: run the unit suite (hermetic, no live warehouse) and lint; run `dbt build`/
  integration tests against a seeded or CI dataset; block merge on failure (*§Testing & TDD*).
- **Environment promotion**: dev → staging → prod with the *same code*, parameterized by environment
  (catalog/dataset/region/credentials). No manual prod edits — they're unreviewable and unrepeatable.
- **Infrastructure as Code**: Terraform/Bicep/CloudFormation/Pulumi or platform-native (Databricks
  Asset Bundles, ADF ARM templates) so environments are reproducible and changes are reviewable and
  reversible.
- **Blue/green or staged deploys** for risky changes; keep the ability to roll back.

## Reliability — DR, RPO/RTO, SLAs

- Define **RPO** (acceptable data loss window) and **RTO** (acceptable recovery time) per pipeline, and
  design to them — not every pipeline needs the same rigor.
- **Backups & replication**: raw layer is the replayable source of truth; protect it (versioning,
  cross-region replication for critical data). Open-table-format time travel aids point-in-time
  recovery.
- **Reprocessability** is your cheapest DR: if any layer can be rebuilt from the one before, most
  corruption is recoverable by rerun rather than restore (*§Architecture & Design Patterns*,
  *§Orchestration & Scheduling*).
- Set and publish **data SLAs** (freshness, completeness) so consumers know what to expect and breaches
  are measurable.

## Cost / FinOps

Data systems scale cost with volume; treat it as a design constraint, not a surprise bill:

- **Scan less**: partition/cluster + pruning, columnar formats, select only needed columns
  (*§Performance & Cost Tuning*). On scan-priced engines (BigQuery, Athena, Snowflake) this is the dominant
  lever.
- **Right-size & auto-suspend compute**; serverless for spiky/idle-prone workloads; job clusters over
  always-on for scheduled work.
- **Manage small files** (compaction) — they inflate metadata and IO cost.
- **Tier & expire storage** per retention policy; move cold data to cheaper tiers.
- **Attribute cost** (tags/labels per pipeline/team) so spend is visible and owned, and **alert on
  anomalous spend** the way you alert on data quality.

## Operability checklist

- Failures and freshness breaches alert the right owner within SLA?
- Quality gates blocking and emitting metrics?
- Deploys via CI/CD + IaC, promotable and rollback-able?
- Backfill/reprocess by partition documented and tested?
- RPO/RTO defined for critical pipelines?
- Cost monitored, attributed, and alerted?

---

# Documenting Data Pipelines

Document the things a future maintainer (or you in six months) can't recover by reading the code: the
**contract**, the **why**, and the **operational facts**. Skip narrating what the code obviously does.

## What every pipeline/model should have

- **Purpose & grain**: one line on what it produces and "one row per ___". The grain is the single
  most useful fact and the most often missing.
- **Inputs**: source tables/files, their owners, and the assumptions made about them (freshness,
  nullability, expected volume). Link the data contract if one exists.
- **Output**: target location, schema, partition/cluster strategy, write mode (append/merge/overwrite),
  and refresh schedule/SLA.
- **Column descriptions**: business meaning, units, and allowed values for non-obvious columns —
  especially anything derived, flagged, or encoded.
- **Key logic decisions**: dedup rules, how late/corrected data is handled, timezone handling, and any
  business rule that isn't self-evident. Explain *why*, not just *what*.
- **Idempotency & reruns**: is it safe to rerun? How do you reprocess a single date/partition?
- **Known limitations & gotchas**: edge cases not handled, scale limits, manual steps.

## Where it lives

- **dbt**: model and column `description`s in `.yml`, surfaced in dbt docs / the catalog. Keep
  descriptions next to the tests so contract and docs stay in sync. This is the lowest-friction option
  when you're in dbt — prefer it.
- **Code**: a module/header docstring covering purpose, grain, inputs, output, and rerun semantics.
  Inline comments only for non-obvious *why*, not for restating code.
- **Repo**: a short `README` per pipeline with the operational facts (schedule, how to run/backfill,
  who owns it, where alerts go) — the runbook a person needs at 2 a.m.
- **Lineage & catalog**: keep the table/column documented in whatever catalog the org uses so
  downstream consumers can discover the grain and meaning without reading code.

## Keep docs honest

Out-of-date docs are worse than none because they mislead. Tie docs to code: column docs live with the
schema, contract docs are validated as tests (so a drifted schema fails CI), and the README is updated
in the same PR as the change. If a doc can't be kept current, prefer a test that enforces the fact
instead of prose that will rot.

## A reusable model-doc template

```yaml
models:
  - name: fct_orders
    description: >
      One row per completed order (grain: order_id). Built nightly from stg_orders, deduped to the
      latest record per order_id by updated_at. Late corrections are absorbed via a 3-day lookback
      merge. Safe to rerun (idempotent merge on order_id).
    columns:
      - name: order_id
        description: Business key. Unique, non-null.
        data_tests: [unique, not_null]
      - name: amount_usd
        description: Order total in USD (currency-converted at order time). Always >= 0.
      - name: order_ts_utc
        description: Order placement time, stored in UTC.
```

---

# Python / PySpark Patterns

Patterns for correct, testable, performant Python data code. See *§Testing & TDD* for the test
harness and *§Performance & Cost Tuning* for Spark optimization.

## Structure for testability

Keep I/O at the edges; make transforms pure functions of DataFrames. This is the single highest-value
structural choice — it makes everything unit-testable without a warehouse or files.

```python
# Edge: I/O. Core: pure transforms.
def run(spark, src_path, dst_path):
    raw = spark.read.parquet(src_path)      # I/O at the edge
    clean = clean_orders(raw)               # pure, testable
    enriched = enrich(clean, load_dims(spark))
    validate(enriched)                      # quality gate, raises on failure
    write_merge(enriched, dst_path)         # idempotent write at the edge

def clean_orders(df):                       # no spark.read / .write inside
    ...
    return df
```

## Explicit schemas, always

Never rely on schema inference for production reads — it changes with the data and fails silently.
Declare the schema; it doubles as documentation and a contract.

```python
from pyspark.sql import types as T
SCHEMA = T.StructType([
    T.StructField("order_id", T.StringType(), False),
    T.StructField("amount",   T.DecimalType(18, 2), True),   # money: Decimal, not Double
    T.StructField("ts",       T.TimestampType(), True),
])
df = spark.read.schema(SCHEMA).json(path)
```

Use `DecimalType` for money, never `Double`/`Float` — floating point silently loses cents.

## Null- and type-safe operations

- Joins drop rows where the key is `NULL` and silently mismatch on type/case/whitespace differences.
  Normalize keys (trim, cast, lower) before joining, and verify with a post-join null check.
- `F.col("a") == F.col("b")` is `NULL` when either side is `NULL`; use `eqNullSafe` (`<=>`) when nulls
  should match.
- Aggregations skip nulls (`F.sum`, `F.avg`) — decide whether that's intended; `count("col")` ignores
  nulls while `count("*")` doesn't.

## Deterministic dedup (the right way)

Row-numbering needs a deterministic tie-break or it's nondeterministic:

```python
from pyspark.sql import Window, functions as F
w = Window.partitionBy("order_id").orderBy(F.col("updated_at").desc(), F.col("ingest_id").desc())
deduped = (df.withColumn("rn", F.row_number().over(w))
             .filter(F.col("rn") == 1)
             .drop("rn"))   # second orderBy column breaks ties deterministically
```

Without the secondary sort key, two rows with equal `updated_at` produce nondeterministic results that
break tests intermittently and drift across runs.

## Idempotent writes

Prefer Delta/Iceberg `MERGE` or partition overwrite over blind `append`:

```python
# Partition-overwrite (idempotent for a load window)
(df.write.mode("overwrite")
   .option("replaceWhere", "load_date = '2024-06-01'")   # Delta: only this partition
   .format("delta").save(path))

# Or MERGE for upsert semantics
from delta.tables import DeltaTable
(DeltaTable.forPath(spark, path).alias("t")
   .merge(df.alias("s"), "t.order_id = s.order_id")
   .whenMatchedUpdateAll().whenNotMatchedInsertAll().execute())
```

## UDFs

Avoid Python UDFs when a built-in (`pyspark.sql.functions`) or SQL expression exists — UDFs break
Catalyst optimization and serialize row-by-row. If unavoidable, prefer pandas/vectorized UDFs, keep
them deterministic, and never use a nondeterministic UDF in a key or dedup.

## pandas / Polars

For data that fits in memory, Polars is faster and has stricter, more predictable typing than pandas;
both are fine for small-to-medium work. Same rules apply: explicit dtypes, pure transform functions,
deterministic sorts before any "take first" logic, and `Decimal` for money. Watch pandas' silent
`object` dtype and automatic `NaN` introduction on joins.

## Config & secrets

Secrets come from a secret manager / scope (Databricks secrets, env via a vault, cloud secret
manager) — never hardcoded, never logged. Parameterize paths, dates, and connection details as
config, not literals buried in code, so backfills and reruns are trivial.

## Logging & observability

Log run id, input and output row counts, and the load window at INFO; log full context on error. Row
counts in the logs make silent row-loss visible after the fact.

---

# SQL & dbt Patterns

Correctness-first SQL and dbt patterns. Snowflake-specific notes are at the end. See
*§Testing & TDD* for dbt unit tests and *§Data Quality & Validation* for schema tests.

## SQL correctness essentials

- **Guard the grain.** Before any join, know the grain of each input. Join on a unique key; if a side
  isn't unique on the join key, dedupe or pre-aggregate it first, or you fan out rows. After joining,
  sanity-check `count(*)` vs the expected grain.
- **Nulls bite:**
  - `NULL = NULL` is `NULL` (not true) — joins drop null keys; use `IS NOT DISTINCT FROM` to match nulls.
  - `col NOT IN (subquery)` returns no rows if the subquery contains any `NULL` — use `NOT EXISTS`.
  - `COUNT(col)` ignores nulls; `COUNT(*)` doesn't. `SUM`/`AVG` skip nulls.
  - Arithmetic with `NULL` yields `NULL`; wrap with `COALESCE` deliberately.
- **Division by zero:** `amount / NULLIF(divisor, 0)`.
- **Determinism:** `LIMIT` without `ORDER BY`, `DISTINCT ON` without a full order, and
  `ROW_NUMBER()`/`QUALIFY` without a tie-break are all nondeterministic. Always add a secondary sort
  key to break ties.
- **Explicit casts:** never rely on implicit coercion; cast strings to numbers/dates explicitly and
  handle parse failures (`TRY_CAST` / `SAFE_CAST`).
- **Filtering and outer joins:** a `WHERE` on the right table of a `LEFT JOIN` silently turns it into
  an inner join (nulls fail the predicate) — put that condition in the `ON` clause instead.

## Deterministic dedup with QUALIFY

```sql
select *
from staging.orders
qualify row_number() over (
  partition by order_id
  order by updated_at desc, ingest_id desc   -- tie-break makes it deterministic
) = 1
```

## dbt structure

Use staging → intermediate → marts layering:

- **staging** (`stg_`): one model per source, light cleaning (rename, cast, basic dedup), grain =
  source grain. Materialize as views.
- **intermediate** (`int_`): reusable business logic, joins, not exposed to BI.
- **marts** (`fct_`/`dim_`): final, documented, tested, the grain consumers rely on. Materialize as
  tables or incremental.

Conventions that prevent bugs: always `ref()`/`source()` (never hardcode table names — breaks lineage
and environments); keep one grain per model and document it; put `unique`+`not_null` on every model's
key.

## dbt incremental models (a top source of silent bugs)

```sql
{{ config(materialized='incremental', unique_key='order_id',
          incremental_strategy='merge', on_schema_change='append_new_columns') }}

select * from {{ ref('stg_orders') }}
{% if is_incremental() %}
  -- lookback window absorbs late-arriving and corrected records
  where updated_at >= (select dateadd(day, -3, max(updated_at)) from {{ this }})
{% endif %}
```

Incremental correctness rules:
- Set a `unique_key` and use `merge` so reruns upsert instead of duplicating (idempotency).
- Use a **lookback window**, not `> max(updated_at)`, so late/corrected rows aren't missed.
- Handle schema change explicitly with `on_schema_change`.
- Test the full-refresh and incremental paths both produce the same result for overlapping data.

## dbt testing

- Schema tests in `.yml`: `unique`, `not_null`, `relationships`, `accepted_values`, plus
  `dbt_expectations`/`dbt_utils` for ranges, recency, row-count comparisons.
- Unit tests (dbt ≥1.8) for transformation logic with mock inputs/expected outputs — true TDD.
- Run `dbt build` (runs models + tests together) in dev and CI; fail CI on any test failure.

## Snowflake notes

- **Cost = warehouse time.** Size the warehouse to avoid spilling (check the query profile for "bytes
  spilled to local/remote") but auto-suspend aggressively. Bigger warehouse + shorter time can be
  cheaper than small + long.
- **Clustering keys** on large tables for the columns you filter/join on; rely on automatic
  micro-partition pruning otherwise. Check `SYSTEM$CLUSTERING_INFORMATION`.
- **Result cache** serves identical queries free; structure dashboards to benefit.
- **Find expensive queries** via `SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY` ranked by
  `bytes_scanned`/`total_elapsed_time`/credits; optimize the top offenders first.
- **Optimizing a query**: read the query profile, look for full scans (add pruning), spilling (size
  up), exploding joins (fix the grain), and repeated subqueries (materialize/CTE). Always re-check the
  result is identical after optimizing.
- Use `SAFE`-style casts (`TRY_CAST`, `TRY_TO_NUMBER`) on dirty input; `QUALIFY` for dedup.

---

# Scala / Spark Patterns

For JVM Spark work. The correctness principles match the PySpark file; the idioms differ. Prefer
`Dataset[A]` with case classes over untyped `DataFrame` where practical — the compiler then catches
schema mistakes that PySpark only finds at runtime.

## Structure for testability

Transforms are functions `Dataset[A] => Dataset[B]`; keep `read`/`write` at the edges.

```scala
final case class RawOrder(orderId: String, amount: BigDecimal, ts: java.sql.Timestamp)
final case class CleanOrder(orderId: String, amount: BigDecimal, ts: java.sql.Timestamp)

object Transforms {
  def cleanOrders(ds: Dataset[RawOrder]): Dataset[CleanOrder] = {
    import ds.sparkSession.implicits._
    ds.filter($"amount".isNotNull)
      .withColumn("rn", row_number().over(
        Window.partitionBy($"orderId").orderBy($"ts".desc, $"orderId".desc)))  // deterministic
      .filter($"rn" === 1).drop("rn")
      .as[CleanOrder]
  }
}
```

Use `BigDecimal` for money (maps to `DecimalType`), never `Double`. Typed `Dataset` encoders enforce
the schema at compile time.

## Explicit schemas

Declare schemas with `Encoders`/`StructType` or case classes; avoid `inferSchema` for production reads.

```scala
val schema = Encoders.product[RawOrder].schema
val df = spark.read.schema(schema).json(path)
```

## Determinism & nulls

- Same rules as PySpark: `===` is null-unsafe (use `<=>` / `eqNullSafe` to match nulls); window
  functions need a tie-break column; no reliance on row order.
- Beware `Option` vs. nullable columns — a `null` in a non-`Option` case-class field throws on encode;
  model nullable columns as `Option[T]`.

## Idempotent writes

```scala
df.write.format("delta").mode("overwrite")
  .option("replaceWhere", s"load_date = '$loadDate'")   // idempotent for the window
  .save(path)
```

Or Delta `MERGE` via `io.delta.tables.DeltaTable` for upserts.

## Testing with ScalaTest

Share a `SparkSession` via a trait; compare collected, sorted rows or use a DataFrame-equality helper.

```scala
trait SparkSpec extends BeforeAndAfterAll { this: Suite =>
  @transient lazy val spark: SparkSession = SparkSession.builder()
    .master("local[2]").config("spark.sql.shuffle.partitions", "2")
    .config("spark.sql.session.timeZone", "UTC").getOrCreate()
  override def afterAll(): Unit = spark.stop()
}

class CleanOrdersSpec extends AnyFunSuite with SparkSpec {
  test("dedupes keeping latest, drops null amounts") {
    import spark.implicits._
    val in  = Seq(RawOrder("o1", BigDecimal(10), ts("2024-01-01")),
                  RawOrder("o1", BigDecimal(99), ts("2024-01-02"))).toDS()
    val out = Transforms.cleanOrders(in).collect().sortBy(_.orderId)
    assert(out.length == 1 && out.head.amount == BigDecimal(99))
  }
}
```

Set `local[2]` and `shuffle.partitions=2` for fast tests; pin the timezone for deterministic
timestamps.

## UDFs & performance

Prefer built-in functions and the typed Dataset API over UDFs (UDFs are opaque to Catalyst). If you
need a UDF, keep it deterministic and pure. See *§Performance & Cost Tuning* for shuffle/broadcast/skew.

## Build & dependency hygiene

Pin Spark and Scala versions in the build (sbt/Maven); a Spark/Scala version mismatch is a frequent
"task not serializable"/`NoSuchMethod` source. Keep the assembly lean — shade conflicting deps.

---

# Cloud Overview — Azure / AWS / GCP

Be fluent on all three clouds by reasoning in **DE primitives** and mapping them to native services.
When a user describes a need in one cloud's terms, translate to the target cloud using the map below.
Default to **portable abstractions** (open table formats, Spark, SQL, dbt, open orchestrators) so
solutions move across clouds; reach for proprietary services when the user has chosen them or when the
managed convenience clearly wins.

## Service-equivalence map

| DE primitive | Azure | AWS | GCP | Portable / multi-cloud |
|---|---|---|---|---|
| **Object storage (lake)** | ADLS Gen2 / Blob | S3 | Cloud Storage (GCS) | — |
| **Batch ingestion / data movement** | Data Factory, Fabric Data Factory | Glue, DMS, AppFlow | Dataflow, Data Transfer, Datastream | Airbyte, Fivetran, dbt+EL |
| **Streaming / messaging** | Event Hubs, Kafka on HDInsight | Kinesis, MSK (Kafka) | Pub/Sub, Managed Kafka | Apache Kafka |
| **Stream processing** | Stream Analytics, Databricks/Flink | Kinesis Data Analytics (Flink), Glue Streaming | Dataflow (Beam), Dataproc/Flink | Flink, Spark Structured Streaming |
| **Batch processing / Spark** | Synapse Spark, Databricks, Fabric | EMR, Glue, Databricks | Dataproc, Databricks | Apache Spark |
| **Data warehouse (SQL)** | Synapse SQL, Microsoft Fabric Warehouse | Redshift | BigQuery | Snowflake (all 3), Databricks SQL |
| **Lakehouse / table format** | Databricks (Delta), Fabric (Delta) | Databricks, EMR+Iceberg/Hudi, Athena+Iceberg | BigLake, Dataproc+Iceberg | Delta / **Iceberg** / Hudi |
| **Ad-hoc query on lake** | Synapse Serverless SQL | Athena | BigQuery (external) / BigLake | Trino / Presto |
| **Orchestration** | Data Factory, Synapse Pipelines | Step Functions, MWAA (Airflow), Glue Workflows | Cloud Composer (Airflow), Workflows | Airflow, Dagster |
| **Catalog & lineage** | Microsoft Purview, Unity Catalog | Glue Data Catalog, DataZone | Dataplex / Data Catalog | Unity Catalog, OpenLineage |
| **Access governance** | Purview, Unity Catalog, RBAC | Lake Formation, IAM | IAM, Dataplex, policy tags | Unity Catalog |
| **Secrets** | Key Vault | Secrets Manager / SSM | Secret Manager | Vault |
| **Serverless functions** | Azure Functions | Lambda | Cloud Functions / Run | — |
| **BI** | Power BI | QuickSight | Looker | Tableau, Superset |

Use this to answer "what's the X-cloud equivalent of Y" and to pick the native service when a cloud is
fixed. The right-hand column is what to prefer for a cloud-portable design.

## Azure native stack notes

- **ADLS Gen2** is the lake (hierarchical namespace on Blob). Pair with Delta/Iceberg for a lakehouse.
- **Microsoft Fabric** unifies ingestion (Data Factory), lakehouse (OneLake, Delta-backed),
  warehouse, and Power BI in one SaaS — increasingly the default Azure analytics platform. **OneLake**
  is the single logical lake; **shortcuts** avoid data copies.
- **Synapse Analytics**: dedicated SQL pools (MPP warehouse — distribution/partition like Redshift),
  serverless SQL (query files in the lake, billed per TB scanned — partition and select columns),
  and Spark pools. Being superseded by Fabric for new work, but widely deployed.
- **Azure Databricks** is first-class on Azure (see *§Databricks*); **ADF/Synapse
  Pipelines** orchestrate (see *§Azure Data Factory*).
- Governance via **Purview** (catalog/lineage/classification) + **Unity Catalog** on Databricks.

## AWS native stack notes

- **S3** is the lake; **Lake Formation** governs fine-grained (table/column/row) access over the Glue
  Catalog. **Glue Data Catalog** is the shared metastore across Athena/EMR/Redshift Spectrum.
- **Glue** for serverless Spark ETL (see *§AWS Glue*); **EMR** for full Spark/Hadoop/Flink
  clusters when you need control or heavy custom workloads; **EMR Serverless** to avoid cluster mgmt.
- **Redshift** is the warehouse (see *§Amazon Redshift*); **Redshift Spectrum** queries S3.
- **Athena** = serverless Trino/Presto SQL over S3, billed per TB scanned — partition + columnar +
  column projection are the cost levers; Athena now supports **Iceberg** tables for ACID/upserts on
  the lake.
- **Streaming**: Kinesis (Data Streams/Firehose) or MSK (managed Kafka); Kinesis Data Analytics or
  Glue Streaming or Flink-on-EMR for processing.
- **Orchestration**: Step Functions (state machines, native retry/catch — great for serverless
  chaining), MWAA (managed Airflow), or Glue Workflows. **DMS/Datastream-style CDC** via AWS DMS.

## GCP native stack notes

- **Cloud Storage (GCS)** is the lake; **BigLake** brings table-format/governed access (incl. Iceberg)
  across BigQuery and open engines.
- **BigQuery** is the flagship serverless warehouse (see *§BigQuery*) — bytes-scanned
  pricing, partition + cluster, BigQuery ML, external/BigLake tables.
- **Dataflow** = managed Apache Beam for unified batch + streaming (autoscaling, exactly-once) — the
  GCP-native equivalent of Glue Streaming / Kinesis Analytics. **Dataproc** = managed Spark/Hadoop/Flink
  for portable Spark workloads.
- **Pub/Sub** for messaging/streaming ingestion; **Datastream** for CDC.
- **Orchestration**: Cloud Composer (managed Airflow) for complex DAGs; Workflows for lightweight
  serverless sequencing.
- Governance via **Dataplex** (catalog, lineage, quality, data mesh organization) and IAM + BigQuery
  policy tags / authorized views for column/row security.

## Choosing per cloud

- **Already committed to a cloud** → use its native serverless analytics engine as the default
  (BigQuery on GCP, Synapse/Fabric on Azure, Redshift/Athena on AWS) and its native orchestrator,
  unless requirements (multi-engine, open formats, existing Databricks/Snowflake estate) say otherwise.
- **Multi-cloud or lock-in-averse** → standardize on **Iceberg** tables, **Spark**/**Trino** compute,
  **dbt** transforms, and **Airflow/Dagster** orchestration; run them via each cloud's managed flavor.
  This is the most portable elite-grade stack and runs comfortably on all three.
- **Snowflake or Databricks** → cloud-neutral platforms that run on all three; pick when you want one
  experience across clouds (see *§Databricks*, *§SQL & dbt* for Snowflake).

---

# Databricks (Spark + Delta + Unity Catalog)

Platform-specific correctness and cost notes. General Spark patterns are in *§Python / PySpark* /
*§Scala / Spark*; tuning in *§Performance & Cost Tuning*.

## Unity Catalog & identifiers

- Tables are **three-level**: `catalog.schema.table`. Always fully qualify in production code; relying
  on the default catalog/schema breaks across environments.
- Use environment-specific catalogs (e.g. `dev`/`staging`/`prod`) and parameterize the catalog so the
  same code promotes cleanly. Never hardcode a single catalog.

## Delta Lake for correctness

- **Idempotent writes**: use `MERGE` for upserts or `replaceWhere` partition overwrite for window
  reloads — never blind `append` for reloadable data.
- **ACID & time travel**: Delta gives atomic commits (no half-written tables) and `VERSION AS OF` /
  `TIMESTAMP AS OF` for auditing and recovery — use time travel to diff a bad run against the prior
  good version when debugging.
- **Schema enforcement**: Delta rejects mismatched schemas by default — good. Use
  `mergeSchema`/`overwriteSchema` only deliberately, and prefer explicit `ALTER TABLE` so drift is
  intentional and reviewed.
- **Constraints**: add `CHECK` constraints and `NOT NULL` on Delta tables so bad rows are rejected at
  write time — a free always-on quality gate.

## Cost & performance levers

- **Photon** for SQL/DataFrame workloads (faster, often cheaper per query).
- **Adaptive Query Execution** on (default) — handles skew joins and coalesces partitions.
- **`OPTIMIZE` + Z-ORDER** (or **Liquid Clustering** on newer tables) to compact small files and
  cluster on filter columns; schedule `OPTIMIZE` for streaming/incremental tables that accrete small
  files. Use `VACUUM` to reclaim storage (mind the retention window vs. time travel needs).
- **Cluster sizing**: right-size and enable autoscaling; use **serverless** SQL/compute to cut idle
  cost. Job clusters (not all-purpose) for scheduled jobs.
- **Auto Loader** (`cloudFiles`) for incremental file ingestion — handles new-file discovery and
  schema evolution with checkpointing; far cheaper than re-listing directories.

## Pipelines & orchestration

- **Lakeflow / Delta Live Tables (DLT)** for declarative pipelines: define tables + expectations and
  the platform manages dependencies, incremental compute, and data-quality `EXPECT` constraints
  (which can drop/fail/quarantine bad rows — wire these as your gates).
- **Lakeflow Jobs** for multi-task workflows (notebook/wheel/SQL tasks) with retries and alerts.
- **Structured Streaming**: use checkpointing for exactly-once; set watermarks for late data; prefer
  `availableNow`/trigger-based micro-batches for incremental batch.

## Testing on Databricks

- Develop transforms as pure functions in a Python package (`%pip install -e` or a wheel) so they're
  unit-testable off-cluster with pytest + chispa — don't bury logic in notebook cells.
- Use **Databricks Asset Bundles (DABs)** to define jobs/pipelines as code, version them, and deploy
  consistently across dev/prod — this is the regression-safe deployment path.

## Secrets

Use **Databricks secret scopes** (`dbutils.secrets.get`) or a backing key vault — never plaintext in
notebooks, and they're redacted from logs.

---

# Azure Data Factory (ADF)

ADF is an orchestration + data-movement service (pipelines, datasets, linked services, triggers,
Mapping Data Flows). It's mostly low-code, so the correctness discipline shifts toward configuration,
idempotency, and parameterization rather than handwritten transforms. For heavy transformation, ADF
typically delegates to Databricks/Synapse Spark or SQL — use the matching reference for that compute.

## Pipeline design for correctness

- **Parameterize everything** (dataset paths, table names, dates, environments) via pipeline
  parameters and global parameters, so the same pipeline runs across dev/test/prod and supports
  backfills. Hardcoded paths are the main source of environment bugs.
- **Idempotent loads**: design Copy/Data Flow steps so a rerun of a window replaces rather than
  duplicates — use an upsert (Data Flow `Alter Row` → upsert) or delete-then-insert the target window
  inside the same logical load. A plain append on retry double-loads.
- **Incremental loads**: use a **watermark** pattern (store last-loaded high-water mark in a control
  table, read it, load `> watermark`, update it only on success) with a lookback for late data. Or use
  Change Data Capture / change tracking on supported sources.

## Reliability & failure handling

- Set **retry** and **timeout** on activities for transient errors; use **failure paths**
  (on-failure dependencies) to route to alert/cleanup activities rather than leaving a half-load.
- Use **`Validation`** and **`Get Metadata`** activities to assert a source file exists / has expected
  size/schema before processing — an ingest-side gate.
- Make multi-step loads recoverable: stage to a landing area, validate, then publish, so a mid-pipeline
  failure leaves the target untouched.

## Data quality gates

- Add explicit check steps: a **Lookup**/**Script** activity running count/null/uniqueness/reconciliation
  SQL against the target, with an **If Condition** that fails the pipeline when a gate is violated.
- In **Mapping Data Flows**, use `Assert` transformations to fail or tag rows that violate expectations,
  and route failing rows to a quarantine sink rather than dropping them.

## Cost & performance

- **Copy activity**: tune Data Integration Units (DIUs) and parallel copies; use **staged copy** and
  **PolyBase/COPY** when loading Synapse for speed. Use binary/passthrough copy when no transform is
  needed (cheapest).
- **Mapping Data Flows** spin up Spark clusters — they have startup latency and cost; reuse an
  **integration runtime TTL** to keep a warm cluster for back-to-back flows, and prefer pushing
  set-based transforms down to the SQL/Spark engine when the volume is large.
- Right-size the **Integration Runtime**; use self-hosted IR only where network access requires it.

## CI/CD & testing

- Keep ADF as **ARM templates / Bicep** (or via the ADF Git integration) in source control; deploy
  through environments so changes are reviewable and reversible — this is the regression-safe path.
- Test pipelines against a small seeded dataset in a non-prod environment, and validate the
  reconciliation gates pass, before promoting.

## Secrets

Store credentials in **Azure Key Vault** referenced by linked services (managed identity) — never put
secrets in linked-service JSON or pipeline parameters.

---

# BigQuery

Cost and correctness notes specific to BigQuery. SQL correctness essentials are in *§SQL & dbt*.

## Cost model drives everything

On-demand pricing bills by **bytes scanned**, so reducing scan = reducing cost *and* time:

- **Partition** tables (usually by ingestion date or an event date column) and always filter on the
  partition column so BigQuery prunes partitions. A filter wrapped in a function
  (`WHERE DATE(ts) = ...` on a non-`DATE`-partitioned table) can defeat pruning.
- **Cluster** on the columns you filter/join on most (up to 4). Clustering prunes blocks within
  partitions.
- **Never `SELECT *`** — you pay for every column read; select only what you need.
- **Preview, don't scan**: use the table preview / `INFORMATION_SCHEMA` instead of `SELECT * LIMIT 10`
  (which still scans). Check the query validator's "this query will process X bytes" before running.
- Set **maximum bytes billed** on expensive queries as a guardrail.
- For steady high volume, consider **capacity (slot) pricing** instead of on-demand.

## Correctness specifics

- **`SAFE_CAST` / `SAFE.` functions** to avoid query-killing errors on dirty input (returns `NULL`
  instead of failing) — but then check for the resulting nulls.
- **`QUALIFY`** for deterministic dedup (with a tie-break in the window `ORDER BY`).
- **Floating point**: use `NUMERIC`/`BIGNUMERIC` for money, not `FLOAT64`.
- **Arrays & structs**: `UNNEST` changes the grain — re-check uniqueness after unnesting.
- **Streaming inserts vs. load jobs**: streaming buffer rows aren't immediately available to some
  operations and have different dedup semantics; for idempotent loads prefer `MERGE` from a staging
  table or load jobs with `WRITE_TRUNCATE` on a partition.

## Idempotent loads

- **`MERGE`** into the target keyed on the business key for upserts.
- **Partition overwrite**: write to `target$YYYYMMDD` (partition decorator) or use
  `WRITE_TRUNCATE` scoped to a partition via a partitioned staging pattern, so reruns replace rather
  than duplicate.

## Scheduling & transformation

- **Scheduled queries** for simple recurring SQL; **Dataform** or **dbt** (BigQuery adapter) for
  managed, tested, layered transformations — prefer these for anything non-trivial so you get lineage
  and tests.
- **Materialized views** for expensive repeated aggregations (auto-refreshed, query-time savings).

## Validation

Use `dbt_expectations`/`dbt` tests, or `ASSERT` statements / scheduled check queries against
`INFORMATION_SCHEMA` for row counts, freshness, and null/uniqueness gates. Make them block the
downstream step on failure.

---

# AWS Glue

Notes for Glue (Spark-based ETL + crawlers + catalog). Spark patterns are in *§Python / PySpark* /
*§Scala / Spark*; tuning in *§Performance & Cost Tuning*.

## DynamicFrame vs. DataFrame

- Glue's **DynamicFrame** tolerates schema inconsistencies (self-describing records, choice types) —
  useful for messy/evolving JSON. But for correctness-critical transforms, convert to a Spark
  **DataFrame** with an explicit schema (`toDF()`), do the typed work there, and convert back only for
  Glue-specific sinks. Don't let DynamicFrame's permissiveness hide schema drift you should be
  catching.
- Use `ResolveChoice` deliberately when a column has mixed types — decide the resolution rather than
  letting it pick.

## Job bookmarks (idempotency & incrementality)

- **Job bookmarks** track already-processed data so reruns don't reprocess — but they're stateful and
  can cause confusion: a failed-then-rerun job may skip or reprocess depending on commit timing.
  Understand the bookmark state; for deterministic reloads of a window, prefer an explicit date filter
  + idempotent write (overwrite/`MERGE`) over relying solely on bookmarks.
- Always call `job.commit()` only after a successful write so the bookmark advances correctly.

## Catalog & crawlers

- Crawlers infer schema and partitions into the **Glue Data Catalog**. Inferred schemas drift — pin
  the schema in the job where correctness matters, and treat crawler output as a hint, not a contract.
- Register partitions explicitly (or use partition projection) for predictable pruning instead of
  re-crawling.

## Cost & performance

- **Worker type & DPUs**: right-size workers (G.1X/G.2X) and number; over-provisioning is the main
  cost waste. Enable **auto scaling**.
- **Glue version**: use a current Glue/Spark version for AQE and performance.
- **Pushdown predicates**: pass `push_down_predicate` to read only needed partitions from S3 — major
  cost saver.
- **Output**: write partitioned Parquet to S3; coalesce to avoid the small-files problem; compact
  periodically.
- **Glue Python Shell / Ray** for lighter non-Spark jobs to avoid Spark overhead on small data.

## Streaming & quality

- Glue Streaming reads from Kafka/Kinesis with checkpointing for exactly-once-ish semantics.
- **Glue Data Quality** (DQDL rules) provides built-in quality gates on the catalog/job — wire rules
  for null/uniqueness/range and fail the job on violation.

## Testing

Develop transforms as pure functions in a local Spark environment and unit-test with pytest + chispa
(the Glue libs can run locally via the Glue Docker image / `aws-glue-libs`). Keep S3 I/O and
DynamicFrame conversion at the edges so the logic is testable without AWS.

## Secrets

Use **AWS Secrets Manager** / SSM Parameter Store and the job's IAM role (least privilege) — never
hardcode credentials; never log them.

---

# Amazon Redshift

MPP-warehouse-specific notes. SQL correctness essentials are in *§SQL & dbt*.

## Distribution & sort keys decide performance

These are the two levers that matter most, and getting them wrong causes slow queries and skew:

- **Distribution style**:
  - `KEY` on the join column for large fact↔dimension joins so matching rows are collocated on the
    same slice (avoids data redistribution — the main cost in MPP).
  - `ALL` for small dimensions referenced in many joins (replicated to every node).
  - `EVEN`/`AUTO` when there's no dominant join key. `AUTO` lets Redshift manage it — reasonable
    default until you have a clear join pattern.
  - Watch for **distribution skew**: a `KEY` on a low-cardinality/lopsided column piles data on few
    slices. Check `SVV_TABLE_INFO` (`skew_rows`).
- **Sort key** on the columns you range-filter on (often a date) so Redshift skips blocks via zone
  maps. Compound sort key for queries that filter on a leading prefix; interleaved only for varied
  filter patterns (and it needs `VACUUM REINDEX`).

## Maintenance affects correctness of performance

- **`VACUUM`** reclaims space and re-sorts after deletes/updates; an un-vacuumed table degrades and
  scans stale blocks.
- **`ANALYZE`** updates statistics so the planner picks good plans; stale stats cause bad joins.
- Run both after large loads (or rely on Redshift's auto-vacuum/auto-analyze, but verify).

## Loading data idempotently

- **`COPY`** from S3 for bulk loads (parallel, fast) — far better than row inserts.
- For idempotent upserts, use the **staging + `MERGE`** pattern (load to a temp/staging table, then
  `MERGE`/delete-then-insert in a transaction) so reruns don't duplicate. Redshift supports `MERGE`;
  wrap in a transaction for atomicity.
- Scope reloads to a date range and delete-then-insert that range within one transaction for
  partition-overwrite semantics.

## Cost & sizing

- **RA3** nodes separate compute and storage (scale independently); **Redshift Serverless** for
  spiky/idle-prone workloads to avoid paying for idle clusters.
- **Concurrency scaling** and **WLM/queues** to manage contention.
- **Spectrum** to query S3 directly for cold/large data without loading it (billed by bytes scanned —
  partition the external data).

## Correctness specifics

- Use `DECIMAL/NUMERIC` for money, not `FLOAT`.
- `COPY` with explicit column list and error handling (`MAXERROR`, check `STL_LOAD_ERRORS`) — silent
  load truncation/coercion is a common data-quality bug.
- Same null/join/dedup rules as standard SQL (*§SQL & dbt*); use `ROW_NUMBER() ... QUALIFY`-style dedup
  via a subquery (Redshift lacks `QUALIFY` in older versions — use a CTE + filter on `rn`).

## Validation

Run row-count/null/uniqueness/reconciliation checks as post-load SQL that the orchestrator fails on,
or via dbt tests (Redshift adapter). Check `STL_LOAD_ERRORS` after every `COPY`.

---

# UBI Platform Notes

For UBI stream creation/modification, use `/ubi-dev` instead. Use this skill for architecture design, cross-platform patterns, code review, data quality, and troubleshooting.

### UBI Medallion Architecture
- **Landing = Bronze** in UBI (no separate raw zone). ADF Copy Activity moves data from source to Landing.
- **Silver**: Type casting, business logic, JOINs to ~25 dimension tables. Oracle EBS columns use entity prefixes (OOHA=headers, OOLA=lines, MSIB=items, HCA/HCP/HCSUA=customers).
- **Gold**: Views with business-friendly aliases (backtick-quoted in Spark SQL). Published to ADLS as Delta format mirror.
- **STM format**: 45 columns, 7 stages (Source, Landing, Bronze, Silver, Gold DB, Gold ADLS, PBI).
- All Oracle VARCHAR2 fields land as STRING in Bronze.

### DuckDB
- Used for local ETL (LLM Usage Tracking pipeline) and ad-hoc analytics.
- Delta Lake integration via `deltalake` Python library (1.5.0+) with `abfss://` scheme + account_key.
- In-process (no server), shares memory with Python. Good for CI/CD fixture validation.
- `_delta_merge_or_create` pattern: try MERGE, fall back to overwrite on schema mismatch.
- Gotcha: `deltalake-rs` 1.5.0 has bugs (#2174, #2180, #3392) that can corrupt Gold tables using `mode="overwrite"`.

### Fabric / OneLake
- **Lakehouse**: ADLS Gen2 shortcuts for Delta tables. Schemas enabled changes API surface.
- **Warehouse**: SQL endpoint for DirectQuery from Power BI.
- **Direct Lake**: PBI reads Delta parquet directly from OneLake (no import/DirectQuery).
- **Shortcuts**: ADLS Gen2 shortcuts in /Tables/ for semantic model. Key auth via connection ID.
- **Schema refresh**: New Delta columns require manual table schema refresh in Fabric portal.
- **M query folding**: Table.AddColumn/Table.SelectColumns don't fold in Fabric DirectQuery. Keep M queries simple.

### Looks-right-but-silently-corrupts — engine deltas worth knowing

These pass review and run clean, but quietly produce wrong data on the specific engines we use. Each
is a concrete, non-obvious failure mode that the generic principles above don't spell out.

- **Delta `replaceWhere` that omits a partition column drops regions silently.** A
  `replaceWhere "load_date = '…'"` on a table partitioned by **`(load_date, region)`** deletes *all*
  matching `load_date` rows across **every** region, then writes back only the regions present in the
  current batch — silently dropping any region absent from this load. (Contrast: data that *violates*
  the predicate raises `DELTA_REPLACE_WHERE_MISMATCH` — that one is loud. The silent case is the
  *scope* mismatch.) Fix: make `replaceWhere` name every partition column the data spans.
- **Decimal cast truncates/`NULL`s without erroring.** `cast(x as decimal(18,2))` rounds scale loss
  **HALF_UP**; on precision *overflow* it returns **`NULL` silently** when `spark.sql.ansi.enabled=false`
  (the common legacy default), or errors when ANSI is on — current Spark raises
  `NUMERIC_VALUE_OUT_OF_RANGE` (SQLSTATE 22003; older Spark used the message
  `CANNOT_CHANGE_DECIMAL_PRECISION`). This is separate from the "use Decimal not Double" rule — even Decimal silently
  loses data on an under-sized target. Size the target scale/precision to the source and check for
  introduced nulls.
- **`MERGE` with a non-unique match key: source errors, target corrupts.** When **multiple source
  rows match the same target row** under a `WHEN MATCHED UPDATE/DELETE`, Delta **errors** with
  `DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE` (the deterministic-merge guard — it does
  *not* silently fan out; an insert-only merge, or a source non-unique only on a non-key column, won't
  raise it). But a non-unique **target** on the merge key silently updates **every** matching target
  row. Dedup the source on the merge key first, and assert target-key uniqueness.
- **Spark session timezone defaults to the cluster's JVM zone, not UTC.**
  `spark.sql.session.timeZone` is unset by default, so `current_date`, `date_trunc`, and
  timestamp-to-date casts resolve in the **cluster region's** zone — a Gold view shifts by region
  while UTC-pinned local tests pass. Set `spark.sql.session.timeZone=UTC` in the job config (not just
  in tests) so prod and CI agree.
- **Auto Loader on positional/CSV sources shifts columns silently.** For headerless/positional
  formats, a new upstream column shifts every downstream column by one with no error (schema-by-
  position). JSON/Parquet match by **name**, so they're safe here. If you must ingest positional CSV,
  pin column names / `cloudFiles.schemaHints` and use `rescuedDataColumn` to catch drift.
