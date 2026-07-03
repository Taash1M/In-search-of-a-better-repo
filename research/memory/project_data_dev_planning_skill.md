---
name: data-dev-planning-skill
description: "Reusable Claude Code skill that produces rigorously-reviewed, execution-ready PLANS for any data-engineering project via an adversarial iterative 3-persona review loop (SA/EA/DE) until zero P0-P3, plus a hard-enforced terminal QA gate. Built v1 2026-06-19 from the AWS Twin engagement."
metadata:
  node_type: memory
  type: project
  originSessionId: d0518511-12b3-40f2-a588-f406002e059b
---

## Data Dev Planning Skill

Single-file skill at **`~/.claude/commands/data-dev-planning.md`** (invocable as `/data-dev-planning`).
Generalizes the AWS Twin engagement method: orient on DE discipline → draft a structured plan →
scaffold on go-ahead → **adversarial iterative 3-persona review (Solutions Architect / Enterprise
Architect / Principal Data Engineer)** until a full round yields **zero P0/P1/P2/P3** → present.
Upstream of `data-engineering` (build) and `audit-ubi` (audit).

**Design doc:** `Obsidian/1-Projects/data-dev-planning-skill-design.md` (12 sections + 7 open questions).

### v1 decisions (baked in)
1. Round floor 2 / typical 3; escalate to user after round 6 if P2+ persist.
2. All personas on inherited model.
3. Auto-apply fixes between rounds; `--propose` flag for approve-each-round.
4. Inline Agent prompts (named sub-agents = future enhancement).
5. Always invoke `data-engineering`; `--light` flag to skip for trivial plans.
6. **Defer folder scaffolding until user go-ahead** (no litter on rejected plans).
7. Ship canonical **G0–G6 gate catalog** as a starting menu.

### Contents
Decision tree, operating loop, folder-structure template, plan-section template (§0–11), full 3-persona
mechanism (parallel dispatch, P0–P3 rubric, per-finding contract, consolidation format, terminate on
clean round, adversarial discipline), 3 persona checklists verbatim, lessons **L1–L15**, **Smoke-test
mandate** section, example invocation, integration note, Rules block, and a **QA Gate** section wiring
the `qa-gate` sub-agent + enforcer as the terminal per-artifact check.

### Quality status (2026-06-20)
- **Skill-judge: 112/120 (93.3%), Grade A** (the 120-pt rubric at `Claude code/best-components/.../skill-judge`).
  D8 Usability 15/15; sub-max only D1 19 (closing Rules recap) + D5 12 (single-file ~556 lines, split
  ruled not-yet-warranted). E:A:R ≈ 80:18:2.
- Hardened through skill-judge → 3-persona review → QA gate (all PASS). Reviews:
  `AWS/docs/reviews/skill_judge_data_dev_planning.md`, `qa_gate_validation_round{1,2,3}.md`.
- **ENFORCED vs ADVISORY-ONLY posture** model added: QA gate is hard-enforced when the enforcer hook is
  installed; degrades to advisory (banner + fallback log + FAIL→user-escalation) on a hook-less host —
  never silently claims "hard-enforced". Concrete prerequisite check (Glob agent + grep settings.json).
- **L15 = smoke-test mandate**: before any costly/irreversible full run, run the full pipeline E2E on a
  slice **<10% of the full run** + its QA gate; full run gated on green smoke (this caught real bugs in
  the AWS Twin execution — the scope miss surfaced at smoke time).

### QA Gate (the terminal per-artifact gate this skill prescribes)
- Sub-agent `~/.claude/agents/qa-gate.md` (read-only) + enforcer hook
  `~/.claude/hooks/qa-gate-enforcer.py` (SubagentStop, fail-closed). See [[project-aws-twin]] for the
  full mechanism + 3-round validation.
- The 3-persona loop reviews the **plan**; the QA gate verifies each finished **artifact**. They chain.

### Lessons encoded (the high-value ones)
L1 reviews adversarial+iterative (≥3 rounds); L2 verify claims vs **real artifacts** (highest-value
findings are "plan says X, code shows Y"); L3 flag tautological gates; L5 catch contradictory fixes;
L8 governance gates machine-enforced fail-closed in the write path; L9 provider fidelity (Nova Canvas
not GPT-Image on Bedrock); L12 local-first sanitized repos; L14 blast-radius-bound destructive ops;
**L15 smoke-test <10% of full run before any costly/irreversible run**.

### Related
- [[project-aws-twin]] — the proof-case engagement this skill generalizes
- [[feedback_skill_no_split]] — keep skills intact (single file, decision tree at top)
- [[feedback_skill_invocation]] — auto-invoke skills proactively