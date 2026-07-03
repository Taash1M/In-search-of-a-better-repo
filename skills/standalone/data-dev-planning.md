---
name: data-dev-planning
description: "Produce a rigorously reviewed, execution-ready PLAN for any data-engineering project — orient on DE discipline, scaffold the project, draft a structured plan, then run an adversarial iterative 3-persona review (SA / EA / Principal DE) until a full round yields zero P0-P3 findings. Trigger on: plan a pipeline, design a data pipeline, ETL plan, data project plan, execution plan, migration plan, lakehouse design, extraction plan, twin/reconciliation/comparison plan, 'plan and review', 'review-ready plan', medallion design, data product plan."
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, Task
---

# Data Dev Planning

This skill **PLANS** data-engineering work and **proves the plan via adversarial review** — it does not
build. Take any data-engineering project request and produce a rigorously reviewed, execution-ready
plan: orient on DE discipline → scaffold the project folder → draft a structured plan → subject it to
an adversarial, iterative 3-persona review (Solutions Architect / Enterprise Architect / Principal Data
Engineer) until a full round produces **zero P0/P1/P2/P3 findings** → present to the user. The output is
a single living plan document plus per-round consolidated reviews, ready to hand to a builder (human or
agent). It sits **upstream** of `data-engineering` (which builds) and `audit-ubi` (which audits built
systems).

<!-- ───────────────────────────────────────────────────────────────────────────
v1 DESIGN DECISIONS (applied as defaults; built from the approved design doc §9/§11)
  1. Round cap: hard floor 2 rounds, typical 3. Upper cap — after round 6 still-open P2+, ESCALATE
     to the user instead of looping further.
  2. Persona model: all three personas run on the inherited model (no per-persona override in v1).
  3. Auto-apply: fixes auto-applied between rounds, full trail presented at the end. Flag --propose
     switches to approve-each-round.
  4. Personas: inline Agent prompts in v1 (keeps the skill self-contained). Named reusable sub-agents
     are a future enhancement.
  5. Orient: ALWAYS invoke `data-engineering`. Flag --light skips it for trivial plans.
  6. Scaffolding side-effects: DEFER folder scaffolding until after the user gives go-ahead on the
     drafted approach. Draft the plan first in the parent folder's docs/plans; scaffold the rest on
     go-ahead. (Avoids litter on rejected plans.)
  7. Gate vocabulary: ship a canonical gate catalog (G0–G6) as a STARTING MENU to adapt, not mandatory.
──────────────────────────────────────────────────────────────────────────── -->

<!-- ───────────────────────────────────────────────────────────────────────────
v2 DESIGN DECISIONS (2026-07-03; extend v1 — nothing below removes a v1 rule)
  1. Named reusable sub-agents (fulfils v1 decision 4's "future enhancement"): when
     `agents\sa-reviewer.md` / `agents\ea-reviewer.md` / `agents\principal-de-reviewer.md` /
     `agents\qa-gate.md` exist (export or ~/.claude/agents/), dispatch them as the persona
     reviewers with the **plan-review lens** named. When absent, the inline prompts in this
     skill remain the fallback. Persona dispatches never emit the QA-GATE-VERDICT-V1 sentinel
     or any "gate" JSON object; only qa-gate does.
  2. Model separation (supersedes v1 decision 2): per-persona model override is available, and
     the terminal qa-gate invocation passes a non-inherited model override by default where the
     host supports it (invocation parameter only — qa-gate agent internals unchanged).
  3. Reviewer verification probes: reviewers may run read-only execution probes (schema checks,
     provider/model-availability checks) — "verify claims against the real platform/artifact
     before asserting", generalizing L9's kernel from model-hosting to any asserted fact.
  4. Loop budget (stated): ≤18 persona dispatches nominal (3 personas × 6 rounds) + ≤1
     re-dispatch per failed persona per round + qa-gate invocations; hard ceiling 36 dispatches
     per planning engagement — breach → stop and escalate to the user.
  5. Reviewer lessons: subagents return lessons to the orchestrator, which appends to
     agents\memory\ serially (single-writer); dream-cycle rules per agents\dreaming.md.
──────────────────────────────────────────────────────────────────────────── -->

## Decision tree

```
Is the request to PRODUCE A PLAN for a data-engineering effort (not build, not audit)?
├─ NO  → redirect: build → data-engineering | audit → audit-ubi | research → taashi-research | stop.
└─ YES
   ├─ Is scope/grain/source/target already crisp?
   │   ├─ NO  → run Step 1 Orient + clarifying questions (grain, write mode, idempotency are
   │   │        non-negotiable to pin — they cause most data incidents). Do not draft until answered
   │   │        or explicitly assumed-and-stated.
   │   └─ YES → proceed.
   ├─ Does it cross clouds / touch proprietary IP, PII, or export-controlled data?
   │   ├─ YES → governance is a P0 lens from round 1; bake a fail-closed pre-egress gate into the plan.
   │   └─ NO  → governance lens still runs, lighter.
   ├─ Is it a COMPARISON / TWIN / parity effort against an existing system?
   │   ├─ YES → comparison-validity is a P0 lens (apples-to-apples grain, non-tautological metrics,
   │   │        new diff vs reused drift-comparator). See Lesson L2/L6.
   │   └─ NO  → skip the comparison-validity sub-checks.
   └─ ALWAYS → run the full operating loop: Orient → Scaffold → Draft v1 → 3-persona review
               rounds until a clean round → present.
```

## The operating loop

Run sequentially. Report at each phase boundary (taashi-research convention). Use TaskCreate to track
the four phases + each review round (audit-ubi convention): mark each task `in_progress` when starting
and `completed` when done.

### 1. Orient (invoke data-engineering)

1. **Invoke the `data-engineering` skill** first (it triggers on ETL / pipeline / Bronze / Silver /
   Gold / medallion / grain / idempotent / reconciliation / schema drift / lakehouse / data modeling /
   SCD / orchestration). Use its operating loop's **Orient phase** to establish the **data contract**
   before anything else:
   - **Inputs**: sources, schemas, expected volume, freshness/SLA, nullable/changing fields.
   - **Output**: target table/file, its **grain** (one row per *what*?), partition/cluster strategy,
     **write mode** (append/overwrite/merge/upsert).
   - **Invariants**: uniqueness keys, referential expectations, value ranges, source→target row-count
     relationships.
   - **Reload semantics**: idempotency requirement, late/corrected-record handling.
   - *(`--light` flag: skip the `data-engineering` invocation for a trivially small plan — but the
     contract items above must still be established directly.)*
2. Read the **real artifacts** the request references — existing repos, scripts, CSVs, schemas, prod
   tables. Match existing conventions; do not invent a new style.
3. If grain, write mode, or idempotency is unclear, **ask** — these three are the non-negotiables.
4. Note reusable assets (with absolute paths) and explicitly note what must be built new.

### 2. Draft plan v1 (before scaffolding)

Write the plan into the **parent folder's** `docs/plans/<PROJECT>_EXECUTION_PLAN.md` using the
**plan-section template** below. Stamp it `Status: DRAFT v1`, absolute date, owner, parent folder.
Include the optional documentation-suite phase and repo phase if the engagement warrants deliverables.

> **Scaffolding is deferred (v1 decision 6).** Do NOT create the full folder skeleton yet — a rejected
> plan should leave no litter. Only the plan document (and its `docs/plans/` parent) is written at this
> point. Present the drafted approach and ask for go-ahead.

### 3. Scaffold the project folder (on go-ahead)

Once the user approves the drafted approach, create the logical folder structure (see
**Folder-structure template**) so the plan and reviews have a home and the eventual build has a
skeleton. **Secrets gitignored from creation.**

### 4. 3-persona adversarial review loop (the heart of the skill)

Run review **rounds** until a full round yields **zero findings at every severity (P0/P1/P2/P3)**.
Mechanism in **Review mechanism** below. Each round:
1. Dispatch **3 persona subagents in parallel** (SA, EA, Principal DE) — single message, multiple
   Agent calls (audit-ubi fan-out pattern).
2. Each subagent **reads the current plan AND the real artifacts it references**, emits findings as
   `[P<n>] <persona>-<n>` with **exact section + concrete fix**.
3. **Consolidate** the round into `docs/reviews/round<N>_consolidated.md` (format below).
4. **Apply** all findings to the plan; bump the plan version; add a change-log entry naming the
   resolved finding IDs. *(Default: auto-apply. With `--propose`, present the consolidated round to
   the user for approval before applying.)*
5. **Re-run** a fresh round. Later rounds must (a) **verify prior fixes held** and (b) **hunt
   new/second-order issues the fixes introduced**. Terminate only when a complete round is
   `P0=0 P1=0 P2=0 P3=0` across all three personas.
6. Present the final plan + the review trail to the user.

> A single review pass is insufficient. In the proof case, round 1 found governance +
> comparison-validity P0s; round 2 found *second-order* issues that round-1 fixes introduced; round 3
> found issues in *newly-added* Phase 8/9 scope. Budget for ≥3 rounds.

## Folder-structure template

Created in Step 3 (on go-ahead) under the project's parent folder (mirrors the AWS Twin layout):

```
<PROJECT_ROOT>/
  README.md                  # overview + (later) actual stats, Mermaid diagram
  PROJECT_MEMORY.md          # created during build, not planning (placeholder ok)
  docs/
    plans/                   # <PROJECT>_EXECUTION_PLAN.md — the living plan (versioned)
    reviews/                 # round<N>_consolidated.md — one per review round (.gitkeep)
    reports/                 # comparison/run reports, generated DOCX (build-time)
  src/
    common/                  # shared utils, config loaders, gate framework
    extract/                 # pass-1 / ingestion
    load/                    # graph/table loaders
    compare/                 # diff / reconciliation (if a comparison effort)
  data/
    bronze/                  # raw + manifest + _quarantine/
    silver/                  # validated/enriched, schema-conformed
    gold/                    # load-ready + reconciliation snapshot
  tests/                     # TDD fixtures + test bed (specified in plan, built later)
  config/                    # mapping tables, blueprints, phaseN_approval.json (gitignored if real refs)
  secrets/                   # GITIGNORED — creds, keys, URIs
  deliverables-scripts/      # doc-suite builders (if doc phase in scope)
  results/                   # baseline snapshots, run outputs (commit/gitignore decision recorded)
  .gitignore                 # secrets/, config/*approval*.json, data/, large binaries
```

**Rules:** `secrets/` and any real-credential/approval file are gitignored from creation.
`docs/reviews/` gets a `.gitkeep`. Decide and **record** the commit-vs-gitignore disposition for
`results/` and generated `docs/reports/*.docx` (sanitizer gap risk — see Lesson L9).

## Plan-section template

Path: `docs/plans/<PROJECT>_EXECUTION_PLAN.md`. Required sections (numbering matches the proof-case
plan so reviewers navigate consistently):

```markdown
# <Project> Execution Plan
**Status:** DRAFT v<N> (post review round <N-1>)   **Date:** <absolute YYYY-MM-DD>
**Owner:** <role/team>   **Parent folder:** <relative path>

## 0. Change log              # one entry per version; name resolved finding IDs per round
## 1. Objective & success criteria
   - Plain objective; explicit out-of-scope statement.
   - "Success = all true:" numbered, FALSIFIABLE *product* criteria (no circular/unfalsifiable gates —
     Lesson L4). These describe the plan/artifacts, never the review process itself.
   - Separate **Exit-gate** line (NOT a numbered product criterion — kept out of the falsifiable list so
     it does not re-introduce the L4 self-reference): "The plan exits review on a fully clean round
     (zero P0–P3 from three independent reviewers — itself falsifiable and non-circular); the only
     non-clean exit is a user-accepted upper-cap escalation (round 6+) where remaining P2/P3 are triaged
     with an owner by recorded user decision. The loop never self-defers P2/P3." (See Termination →
     "Reconciling termination…".)
## 2. Scope                   # in-scope enumerated; routing rules for edge types; out-of-scope listed
## 3. The validated pattern   # WHY this approach "best"; evidence table; accepted trade-offs (lock-in, etc.)
## 4. Data contract           # grain, keys, idempotency, reload, invariants — the orient output, formalized
   ### 4.1 Grain (one row per WHAT)
   ### 4.2 Keys, idempotency, reload (write mode, dedup semantics, stale handling, checkpoint/resume)
   ### 4.3 Invariants (each = a hard gate, cross-ref §5)
## 5. Architecture & data-quality gates
   - Medallion (bronze/silver/gold) ASCII/Mermaid data flow.
   - Gates G0..Gn — EVERY gate fail-closed (on breach: status='failed', exit(1), block downstream).
   - Governance gate G0 wired into the WRITE/UPLOAD path (machine-enforced, not prose — Lesson L8).
## 6. Execution phases        # Phase 0 governance/setup → Phase N validate; TDD-first per phase
   # MANDATORY: the first phase that incurs real cost or external/irreversible side-effects (egress,
   # paid API, bulk write) is preceded by a SMOKE TEST phase that runs the FULL pipeline end-to-end on
   # a slice sized < 10% of the full run (smallest natural unit — one entity/partition/FG), through
   # every downstream stage AND its QA gate, before the full run is authorized. See Smoke-test mandate.
## 7. Cost & runtime estimate # grounded in a measurable unit (per-page/per-row/per-token), hard ceiling + abort
   # State the smoke-test slice size + its cost, and that the full run is gated on a green smoke test.
## 8. Risks & mitigations     # table: Risk | Mitigation — each mitigation maps to a gate or phase
## 9. Deliverables            # pipeline+data, doc suite (optional), repo (optional)
## 10. (optional) Documentation suite phase   # generated FROM actual state, PII-stripped, sanitized
## 11. (optional) Repository phase            # local-first, sanitized, authorized push is separate step
```

**Quality bars baked into the template (so reviewers can check them):** every success criterion
falsifiable; every invariant has a fail-closed gate; every gate fail-closed with a defined breach
action; cost grounded in a measured unit with an abort ceiling; every risk maps to a mitigation in a
gate/phase; relative dates converted to absolute.

### Canonical gate catalog (starting menu — adapt, not mandatory)

The proof case used G0–G6. Ship these as a **starting menu** to adapt per project; not every project
needs all seven, and a project may add its own:

| Gate | Name | Asserts |
|---|---|---|
| **G0** | Governance | Signed approval/authorization artifact present in the write/upload path; absent → exit(1) (Lesson L8). |
| **G1** | Schema / grain | Output columns/types/nullability exact; grain key unique & non-null; no join fan-out. |
| **G2** | Manifest reconciliation | Every manifest item accounted for in the target (processed, quarantined, or declared-skipped). |
| **G3** | Coverage | Processed-set ∪ quarantine = manifest; coverage threshold met; quarantine reconciled before this gate. |
| **G4** | Referential | Foreign keys resolve to parents; orphan rate below threshold. |
| **G5** | Sanity | Volume/value bands vs history; tautological-by-construction recons are sanity-only, excluded from scoring (Lesson L3). |
| **G6** | Orphans / stale sweep | Destructive stale-node/row sweep scoped to the right labels, keyed to the manifest, run-once, count-capped with abort (Lesson L14). |

## Review mechanism

### Dispatch (parallel subagents)

- In one assistant turn, issue **three `Agent` (general-purpose) calls in a single message** so they
  run concurrently (audit-ubi fan-out).
- Each subagent prompt contains: (a) the persona's **verbatim checklist** (below), (b) the **absolute
  path to the current plan**, (c) the **absolute paths to the real artifacts** the plan references
  (scripts, CSVs, schemas), (d) the severity rubric, (e) the per-finding output contract.
- Subagents are **read-only reviewers** — they do not edit the plan. They return findings only.
- All three personas run on the inherited model by default (v1 decision 2 — superseded by v2 decision 2: per-persona override available; the terminal qa-gate invocation passes a non-inherited model by default where supported).
- If a subagent fails/times out, re-dispatch that one persona; never proceed with a missing persona
  (a clean round requires all three).

### Severity rubric

- **P0 (Blocker):** plan is not buildable / will corrupt data / violates governance or law /
  comparison is invalid. Must fix before execution.
- **P1 (Major):** will fail under load or edge cases; missing a required gate, idempotency, or
  fail-closed behavior; tautological or unfalsifiable metric.
- **P2 (Should-fix):** correctness/clarity gap that works but is fragile or ambiguous; missing
  tiebreaker, dedup key, symmetry check, observability.
- **P3 (Minor):** polish — wording, provenance stamping, naming, doc-stamp, gitignore disposition.

### Per-finding output contract

Each subagent returns each finding as:

```
[P<n>] <persona>-<seq>  — <imperative title ≤80 chars>
  Section: §<x.y> (exact)
  Claim-vs-artifact: <what the plan asserts> vs <what the real file shows>   # when applicable
  Fix: <concrete, specific change to make>
```

Plus a one-line **verdict** per persona: `NOT buildable / NOT approved / not ready` OR
`clean (P0=0 P1=0 P2=0 P3=0)`.

### Consolidation format

`docs/reviews/round<N>_consolidated.md` — mirrors the proof case exactly:

```markdown
# <Project> Plan — 3-Persona Review, Round <N> (on v<X>)
[one-line state: what's closed, where remaining issues concentrate]

## SA — verdict — P0=<n> P1=<n> P2=<n> P3=<n>
- [P<n>] <finding with section + fix>
## EA — verdict — P0=<n> P1=<n> P2=<n> P3=<n>
- ...
## Principal DE — verdict — P0=<n> P1=<n> P2=<n> P3=<n>
- ...

## Disposition: all applied in plan v<X+1>.   (or: CLEAN ROUND — present to user)
```

### Termination (zero P0-P3)

- A round is **clean** iff all three personas return `P0=0 P1=0 P2=0 P3=0`.
- On a non-clean round: apply every finding, bump plan version, add change-log entry citing finding
  IDs, run another round.
- **Do not stop early** on "only P3s remain" — a P3-only round still gets applied and re-reviewed (the
  re-review confirms no second-order issue and yields the clean round).
- **Hard floor: minimum 2 rounds** even if round 1 looks clean (second-order check). **Typical: 3
  rounds.**
- **Upper cap (v1 decision 1):** if after **round 6** there are still-open P2-or-higher findings,
  **stop looping and escalate to the user** — present the open findings and the apparent scope
  ambiguity driving them, and ask for a decision rather than continuing to loop indefinitely.
- **Reconciling termination with the §1 success criterion.** The default exit is a fully clean round
  (P0=P1=P2=P3=0) — drive there. The plan-template success criterion ("no P0/P1 open; P2/P3 triaged
  with owner or defer") describes the **only** sanctioned non-clean exit: the **upper-cap escalation**,
  where the *user explicitly accepts/defers* the remaining P2/P3 with an owner. P2/P3 are **never
  self-deferred by the loop** — they are deferred only by recorded user decision at the cap. So: the
  loop terminates on a clean round, OR on a user-accepted deferral at round 6+. A literal reading must
  not treat "P2/P3 may be deferred" as license to stop early — that license exists only post-escalation.

### Adversarial discipline

- **Verify claims against real artifacts.** "Plan asserts X but the code/CSV shows Y" is the
  highest-value finding class. A reviewer that only reads the plan is half-blind.
- **Hunt second-order issues** introduced by the *previous round's fixes* (e.g., a hard set-equality
  gate added in round 1 that now contradicts quarantine-by-design — flag the contradiction).
- **Flag tautological gates** — a reconciliation that passes by construction proves nothing (e.g.,
  CSV-sourced-both-sides quantity recon).
- **Flag mutually-contradictory fixes** across sections.
- **No rubber-stamping:** "this is well-established" is not a reason to pass a section. Every checklist
  item runs for every round.

## Persona checklists

### Solutions Architect (SA)

- **Solution coherence** — do the chosen components actually solve the stated objective?
- **Component fit** — is each tool the right one for its job (vs forced/awkward)?
- **Integration points** — are all hand-offs between components specified (formats, schemas, auth)?
- **Sequencing / dependencies** — is phase order correct? Any step depending on a later one?
- **Buildability** — could a competent engineer build this from the plan as written, with no hidden gaps?
- **Asset reuse** — does the plan correctly reuse existing assets, and is each reused asset actually fit
  for the new purpose (read the real script — does it do what the plan claims)?
- **End-to-end data-flow soundness** — trace one record source→target; does it survive every stage?
- **Apples-to-apples comparison validity** (comparison efforts) — same grain both sides? Is the
  comparator measuring the intended thing, or something guaranteed-equal-by-construction? Is a reused
  comparator actually graph-vs-graph (not drift)?

### Enterprise Architect (EA)

- **Data classification** — is the data classified, and does handling match the class?
- **PII handling** — identified, redaction/retention decision, lawful basis where relevant.
- **Secrets & least-privilege IAM** — no standing plaintext keys; SSO/STS; role scoped to exactly what's
  needed; secrets gitignored.
- **Cross-cloud / data-residency** — export authorization for IP leaving its home cloud; regional/
  no-training confirmation for any third-party model.
- **Cost governance & tagging** — budget cap + alert; resources tagged for usage tracking.
- **Lineage / provenance** — every output records its source identifiers, model/blueprint versions,
  key ARNs.
- **Compliance (incl. export-control where relevant)** — ITAR/EAR or sector determination by the right
  authority; default-deny → quarantine when undetermined.
- **Environment separation** — twin/dev isolated from prod (separate instance/URI, not just a flag).
- **Auditability** — a retained audit record (ledger) survives teardown; teardown/retention covers ALL
  layers (bronze→gold, derived artifacts, secrets, instances).
- **Fail-closed governance gates wired into CODE, not prose** — the upload/write path asserts a signed
  approval artifact and exits non-zero if absent.

### Principal Data Engineer (Principal DE)

- **Data-contract completeness** — grain, keys, write mode, idempotency, reload, invariants all pinned.
- **TDD / test-first** — tests defined before implementation; schema + grain + values + idempotency +
  volume-sanity asserted.
- **Grain / uniqueness guards** — grain stated as "one row per WHAT"; uniqueness key non-null and
  tested; no join fan-out.
- **Reconciliation that catches WRONG data** — not tautological; the recon must be able to fail on a
  real defect (source∩authoritative∩target three-way, count sub-checks, split-back-checks).
- **Idempotency** — rerun == run-once; dedup/cache keys defined (and versioned where derived from a
  model/blueprint).
- **Determinism** — temperature 0 for generative steps; **a total-order tiebreaker on EVERY
  `LIMIT 1`/top-1 selection**; pinned timezones; deterministic dedup tie-breaks.
- **Quarantine vs silent drop** — every un-processable record is quarantined with a reason and
  reconciled, never silently dropped; quarantine reconciled against the target set before any coverage
  gate.
- **Checkpoint / resume** — durable job-state; resume re-polls outstanding work, never re-runs
  completed work.
- **Null / type safety** — at every join and cast.
- **Blocking gates** — every gate fail-closed with a defined breach action (status='failed', exit(1),
  block downstream) and a real threshold (not "if desired").
- **Observability** — per-record run-ledger (NDJSON) with cost/tokens/stop_reason/status/
  quarantine-reason/versions; reports aggregate from it.
- **Silent-failure hunting** — find every place the pipeline could exit-zero while producing
  wrong/partial data (truncation, empty arrays, schema drift, dropped sub-records, stale nodes).

## Lessons encoded (L1–L15)

From the proof engagement (the AWS Twin Execution Plan, v3.2 after 3 review rounds) — bake these in:

- **L1 — Reviews must be adversarial AND iterative.** One pass is insufficient. Round 1 → governance +
  comparison-validity P0s; round 2 → second-order issues the round-1 fixes *introduced*; round 3 →
  issues in *newly-added* scope. Budget ≥3 rounds; never terminate before a fully clean round.
- **L2 — Verify claims against real artifacts.** Read the actual code/scripts/CSVs the plan references.
  Highest-value findings are "plan asserts X but the code shows Y" (e.g., "loaders apply unchanged" was
  false — BDA emits flat UPPERCASE, prod consumes nested objects).
- **L3 — Watch for tautological gates.** A reconciliation that passes by construction proves nothing
  (CSV-sourced-both-sides quantity recon → moved to sanity-only, excluded from scoring).
- **L4 — Success criteria must be falsifiable.** Kill circular/unfalsifiable gates (the "success #5 =
  passes review" self-reference).
- **L5 — Watch for fixes that contradict each other.** A hard set-equality gate (round 1) vs
  quarantine-by-design → redefine the gate to tolerate *declared* deltas only.
- **L6 — Apples-to-apples or it's not a comparison.** Same grain both sides; build a NEW diff when the
  reused comparator measures something else (drift, not graph-vs-graph); define the metric precisely
  (Drawing-level leaf-field count, not mixed levels).
- **L7 — Determinism everywhere.** Temperature 0 for generative steps; a tiebreaker on every `LIMIT 1`;
  order on the grain key, not a display field.
- **L8 — Governance gates must be machine-enforced (fail-closed) in the write/upload path**, not
  narrative. No valid signed approval artifact → no egress → exit(1). Default routing for undetermined
  items = quarantine, not "process anyway."
- **L9 — Provider fidelity.** Don't promise a model/service a cloud doesn't host. Caught "GPT-Image on
  AWS Bedrock" — it's not there; the AWS-native equivalent is **Amazon Nova Canvas**. Always verify a
  named model is actually available on the target platform (check `claude-api` / provider docs before
  asserting).
- **L10 — Convert relative dates to absolute** in every plan/doc.
- **L11 — PII-strip deliverables** (generic role labels, no names/emails); scan generated DOCX too (or
  gitignore them and commit Markdown sources only).
- **L12 — Local-first repos, then authorized push.** Sanitize before any commit (paths, usernames,
  emails, org names, account IDs, ARNs, creds); secret-scanner + sanitizer zero-findings is an explicit
  pre-commit gate; remote push is a separate, explicitly-authorized step (prior DLP incident history).
- **L13 — Stamp provenance** on every doc/output: run/load-event id + source-data hash + model/blueprint
  version; assert ledger run-id == gold snapshot before generating docs.
- **L14 — Destructive operations are blast-radius-bounded.** Stale-node/row sweeps scoped to the right
  labels only, keyed to the manifest, run once post-load, count-capped with an abort.
- **L15 — Smoke-test before any costly/irreversible full run.** The first phase that spends money or
  has external/irreversible side-effects is preceded by a full end-to-end run on a slice **< 10% of the
  full run** (smallest natural unit), through every downstream stage and its QA gate. The full run is
  gated on a green smoke test (and, if it spends money, on the user seeing the smoke result + projected
  full cost). Proves the integration seams cheaply on real data before scale. See Smoke-test mandate.

## QA Gate (final gate after each artifact)

The 3-persona loop hardens the **plan**. The **QA gate** verifies each finished **artifact** against
its Definition of Done — it is the **last** check before an artifact is accepted. They chain, they
don't overlap: harden the plan → build → QA-gate each artifact. (Anthropic Evaluator-optimizer /
Sectioning pattern: a *separate* screener beats self-review.)

**Prerequisite — determine the host enforcement posture (do this concretely, once, up front).** This
gate depends on two host artifacts: the **`qa-gate` sub-agent** (`~/.claude/agents/qa-gate.md`) and the
**`qa-gate-enforcer.py` `SubagentStop` hook** wired in `settings.json`. **Run the actual checks** (don't
infer): (1) the agent file exists (Glob/Read `~/.claude/agents/qa-gate.md`); (2) `settings.json`
registers `qa-gate-enforcer.py` under a `SubagentStop` matcher (Grep). Record the result as the
**host enforcement posture** stamp used everywhere below:
- **ENFORCED** (both present) → the gate is hard-enforced (see next paragraph).
- **ADVISORY-ONLY** (hook missing) → the sub-agent still returns PASS/FAIL but nothing blocks on FAIL.
  Because the durable ledger is written *by the hook*, advisory mode has **no automatic block AND no
  automatic audit trail** — so it requires **compensating controls**: the orchestrator MUST (a) print a
  one-line `ENFORCEMENT: ADVISORY-ONLY` banner at gate time, (b) write each verdict to a fallback log
  itself, and (c) on any FAIL, **stop and surface it to the user for explicit accept/defer** (mirroring
  the upper-cap escalation) — an artifact may NOT be accepted on a hook-less host without a recorded
  user acknowledgement. Never print "hard-enforced" in this mode. Stamp the posture into each generated
  plan's QA-Gate subsection (below) and its §Risks — never stamp "blocks until PASS" on an ADVISORY host.

**The gate is the `qa-gate` sub-agent** (`~/.claude/agents/qa-gate.md`, read-only Read/Glob/Grep/Bash),
invoked as the terminal check after each phase's DoD is claimed:

```
subagent_type: "qa-gate"   # pass it: the artifact path+type, its DoD, source/authoritative data to
                           # reconcile against, and (for code) leave to invoke /code-review + /simplify,
                           # (for runnable artifacts) /verify for ground truth.
```

**When the host posture is ENFORCED (hook installed — see Prerequisite), it is hard-enforced, not
advisory.** The `qa-gate-enforcer.py` `SubagentStop` hook identifies a qa-gate run by the
`QA-GATE-VERDICT-V1` sentinel the agent emits, then blocks (exit 2) on `verdict: FAIL` **and** when the sentinel is present but no parseable PASS verdict is found (fail-**closed** —
matching the agent's "default to FAIL when unsure"). It allows (exit 0) only on a parsed PASS or when
the sentinel is absent (genuinely not a qa-gate run, so other sub-agents are never wedged). It honors
`stop_hook_active` to avoid loops and appends every decision to a durable audit ledger
(`~/.claude/qa_gate_ledger.ndjson`).

**Verdict contract** (the gate emits a fenced ```json block):
`{ artifact, artifact_type, verdict: PASS|FAIL, checks_performed[], findings[{severity,location,issue,required_fix}], accept_rule }`
— **PASS only when zero blocker AND zero major findings.** PASS → accept + advance; FAIL → return with findings.

**Therefore every phase in the generated plan (§5 template, §6 phases) ends with a `## QA Gate`
subsection** right after its Definition of Done:

```markdown
### Phase N — <artifact>
- ... build steps ...
- Definition of Done: <objective, checkable completion criteria>
- ## QA Gate (terminal check — runs after DoD is claimed)
    - Reviewer: `qa-gate` sub-agent (read-only), `subagent_type: "qa-gate"`
    - Code/SQL artifacts also run `/code-review` (bugs) + `/simplify` (cleanup)
    - Runnable artifacts (graph load, pipeline) also run `/verify` (ground truth)
    - Contract: { verdict: PASS|FAIL, findings, severity };  PASS → advance, FAIL → remediate + re-run
    - Enforcement: <stamp host posture> — ENFORCED: SubagentStop hook (`qa-gate-enforcer.py`) blocks
      completion until PASS. ADVISORY-ONLY: no automatic block; FAIL escalates to user for accept/defer
      and is logged to a fallback ledger (see QA-Gate Prerequisite). Never stamp "blocks until PASS" on
      an ADVISORY host.
```

Accept criteria per artifact type live in the sub-agent (`agents/qa-gate.md`): plan doc, extraction
output, graph load, comparison report, DOCX, code/SQL. When drafting a plan, **add the `## QA Gate`
subsection to every phase** and point it at the right accept-criteria set.

## Smoke-test mandate (before any costly / irreversible full run)

**Every plan MUST include a smoke-test phase before the first phase that incurs real cost or external,
irreversible side-effects** — data egress, a paid API/model run, bulk writes, or anything you can't
cheaply undo. The smoke test is non-optional and is itself QA-gated.

Rules:
- **Size < 10% of the full run, every time.** Pick the smallest natural unit (one entity / partition /
  FG / file-group). State the slice and its absolute size+cost in §7. If 10% is still expensive, go
  smaller — one unit is fine; the point is to exercise the pipeline, not to sample representatively.
- **Full end-to-end, not a stage in isolation.** The smoke test runs the *entire* downstream chain the
  full run will (upload → process → enrich → load → validate) **and its QA gate(s)** — so integration
  seams, auth, schema-mapping, and the gate machinery are all proven on real data first.
- **The full run is GATED on a green smoke test.** Full run is not authorized until the smoke slice
  passes its QA gate and (if it spends money) the user has seen the smoke result + the projected full
  cost. Encode this as a hard dependency in the phase ordering.
- **Cheap by construction, real by fidelity.** Use the real source data and the real services (not
  mocks) on the small slice — a smoke test on fakes proves nothing about the seam that will actually
  break.
- **Checkpoint/resume + idempotency mean the smoke slice is not wasted** — its outputs are valid rows
  of the full run, not throwaway, when keyed identically (sha256/business key).

In the plan, render it as `### Phase <K.smoke> — Smoke test (1 <unit>, <N> docs/rows, ~$<cost>)`
immediately before the first costly phase, with its own QA gate and an explicit full-run-gating note:
on an **ENFORCED** host the full run is hard-blocked until the smoke QA gate returns PASS; on an
**ADVISORY-ONLY** host the smoke FAIL escalates to the user and the full run requires recorded user
acknowledgement before proceeding (same posture model as the QA Gate Prerequisite).

## Example invocation

```
/data-dev-planning Plan a project to build a "twin" of the production PLM Drawing Graph-RAG
knowledge graph on AWS (BDA + Claude two-pass extraction), load it into a separate Neo4j graph,
and produce a side-by-side comparison against the production graph. 15 finished goods in scope.
```

Expected behavior:
1. Orient — invokes `data-engineering`, reads `bom_metadata.json`, the real loader scripts, the qty
   CSV; establishes grain (one Drawing per source file), write mode (MERGE), idempotency (sha256 +
   blueprint version), invariants (coverage, orphans).
2. Drafts `AWS_TWIN_EXECUTION_PLAN.md` v1 in the parent folder's `docs/plans/`; presents the approach
   and asks for go-ahead (scaffolding deferred per v1 decision 6).
3. On go-ahead, scaffolds `AWS/` with `docs/{plans,reviews,reports}`, `src/`, `data/{bronze,silver,gold}`,
   `tests/`, `config/`, `secrets/` (gitignored).
4. Round 1 (3 parallel subagents) → SA finds drift-comparator + grain P0s; EA finds 3 governance P0s;
   DE finds grain + tautology + idempotency P0s → consolidate → apply → v2.
5. Round 2 → second-order issues (set-equality vs quarantine contradiction, determinism,
   schema-mapping) → v3.
6. Round 3 → newly-added doc-suite scope (Nova-Canvas-under-G0, generated-DOCX sanitization,
   richness-metric precision) → v3.2.
7. Round 4 → clean (P0=P1=P2=P3=0) → present plan + 3 consolidated reviews to user.

Other invocations the skill should handle: "Plan an Oracle→UBI medallion ingestion for the CPQ stream
and review it"; "Design and vet a customer-MDM matching pipeline plan"; "Plan a migration from
ADF+Databricks to Fabric with a reviewed execution plan."

## Integration with other skills

- **data-engineering** — the BUILD counterpart; this skill invokes it during Orient and hands the
  reviewed plan to it for implementation.
- **audit-ubi** — audits *built* systems; downstream of a build, not of a plan.
- **docx-beautify** — render the final plan or doc suite into a professional DOCX deliverable.
- **repo-eval** — if a repository gets adopted/forked as part of the engagement, evaluate it with this.
- **taashi-research** — upstream tech/vendor/architecture decisions feed the plan's §3 (validated
  pattern); use it when the "best approach" is genuinely unresolved.

## Rules

- **Never produce code in this skill — it produces a PLAN only.**
- **Never terminate before a fully clean round** (P0=P1=P2=P3=0); **minimum 2 rounds**, typical 3;
  escalate to the user after round 6 if P2+ still open.
- **Reviewers MUST read the real artifacts, not just the plan** — claim-vs-artifact is the highest-value
  finding class.
- **Every gate in the plan must be fail-closed; every success criterion falsifiable.**
- **Governance gates machine-enforced in the write path, not prose.**
- **Absolute dates; PII-stripped deliverables; local-first sanitized repos; authorized push is a
  separate step.**
- **Verify provider fidelity** (model actually hosted on the target cloud) before asserting it.
- **Scaffold only after go-ahead** — a rejected plan leaves no folder litter.
- If a persona subagent fails or times out, re-dispatch that persona; never declare a round (clean or
  otherwise) with a missing persona.
- Run every checklist item for every round. "This is well-established" is not a reason to skip a check.

## Six-Step Flow (labels)

This skill IS step 1.5 (Planning) of the standard six-step flow for the build skills. Internally
its loop maps as: 1 Orientation = Step 1 (Orient); 2 "TDD for plans" = the falsifiable success
criteria + fail-closed gates defined before drafting (the template's quality bars); 3 Build = the
draft + adversarial 3-persona review rounds (via the named agents, v2 decision 1); 4 E2E = the
fully-clean-round exit + terminal QA gate; 5 Documentation = the versioned plan + per-round
consolidated review trail.

## Agent Dispatch (v2)

Dispatch the named agents when present (v2 decision 1) with the plan-review lens; inline persona
checklists below remain the fallback and stay authoritative for it. qa-gate invocations pass the
model override (v2 decision 2). Memory writes go through the orchestrator only.
```
