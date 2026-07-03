---
name: data-engineering-skill-refinement
description: Refined the data-engineering skill (4 Skill-Judge fixes + embedded 3-persona review gate). COMPLETE 2026-06-26 — final Skill-Judge 109/120 Grade A (+19 from 90), zero regression. Workspace in Claude code/skills/.
metadata: 
  node_type: memory
  type: project
  originSessionId: 88ba5242-fb95-4479-8913-79171496f8c1
---

## Overview
Refining `<ADMIN_HOME>/.claude\commands\data-engineering.md` (1944 lines, Skill-Judge baseline **90/120 C+**). Two goals: (1) fix the 4 Skill-Judge gaps; (2) **embed a per-artifact 3-persona test+QA review gate** into the skill's operating loop.

**Why:** User asked to refine the skill, run Skill Judge, close gaps, and bake the 3-persona+QA discipline into the skill itself — with a double review loop (harden the plan, then the edited skill) and zero regression.

## Workspace (NOT the old Skill Evaluation folder)
`<USER_HOME>/OneDrive - <ORG>\Claude code\skills\data-engineering-refinement\`
- `PROJECT_MEMORY.md` — living cold-resume handoff (READ THIS FIRST on resume)
- `docs/plans/DATA_ENGINEERING_REFINEMENT_PLAN.md` — the plan, **v7 PROVEN CLEAN**
- `docs/reviews/round{1-7}_plan_consolidated.md` — 7 plan-review rounds
- `docs/reports/regression-check.md` — baseline inventory + 8-dim vector + S4 checks
- `baseline_fences/00-15.txt` — original 16 code-block bodies (S4 substring gate)
- **Restore point:** `…\AI\Technical Validation\Bkps\data-engineering.RESTORE-POINT.20260625.md` (sha256 c0f0c081…02, byte-identical)

## The 4 fixes (F1-F4) + review gate (S3)
- **F1/D5:** rewrite 80 dangling `.md` pointers → inline `*§Section*` pointers + add TOC. (D5 8→≥13.)
- **F2/D8:** ≥7-branch decision tree before operating loop, reconciled with existing `## Task-type quick routing`.
- **F3/D3:** consolidated NEVER block (≥8 rules, ≥4 BAD/GOOD pairs).
- **F4/D1:** 5 platform silently-corrupts deltas, each grep-proven-absent + error-class-exact: replaceWhere region-drop (`DELTA_REPLACE_WHERE_MISMATCH`), decimal cast (`CANNOT_CHANGE_DECIMAL_PRECISION`/`NUMERIC_VALUE_OUT_OF_RANGE`), MERGE multi-source (`DELTA_MULTIPLE_SOURCE_ROW_MATCHING_TARGET_ROW_IN_MERGE`), session-TZ drift, Auto-Loader-by-position.
- **S3:** §Review Gate as **H2 under existing "# Reference Sections"** (keeps H1 set=23); embeds 3 personas + severity rubric + per-finding contract + termination (floor 2/cap 6) + qa-gate chaining + BOTH host postures; scoped to artifacts the skill built this session (external "review my code" → existing §Code Review checklist).

## Execution order (Phase C — one coordinated edit)
C2 (de-dangle) → C3 (tree) → C4 (NEVER) → C5 (review gate) → C6 (deltas) → **C1 (TOC built LAST)**. Then Phase D smoke (all `*§label*` resolve via case-insensitive substring vs `^#{1,3}` headings; YAML valid; no truncation). Then Phase E (3-persona on edited skill until clean). Then Phase F (final Skill-Judge, target ≥104/120, D5≥13, no dim < baseline).

## Baseline numbers (S4 regression guard — non-tautological)
23 H1, **141 fence-aware H2** (144 raw − 3 inside review-output fence L279/283/286), 19 H3 (3 UBI gated), 16 code blocks, 1944 lines, 80 dangling pointers (21 unique). Baseline 8-dim vector: D1=10 D2=14 D3=11 D4=13 **D5=8** D6=14 D7=8 D8=12 = 90.

## Status (2026-06-26) — ✅ COMPLETE + LIVE
All phases done. Plan hardened (7 rounds clean), skill edited in place (1944→2185 lines), edited skill hardened (5 rounds, R5 all-clean), **final Skill-Judge 109/120 Grade A (+19 from 90 baseline)**. Acceptance met: ≥104, D5 8→14, no dim regressed, zero regression (S4 a-e pass). Per-dim: D1 10→15, D2 14→15, D3 11→14, D4 13→14, D5 8→14, D6 14, D7 8→9, D8 12→14. Final report: `docs/reports/skill-judge-data-engineering-FINAL.md`. **INSTALLED + LIVE** at `~/.claude/commands/data-engineering.md` (last mod 2026-06-26 00:52, valid frontmatter, 0 dangling pointers). Restore point in Bkps/ if rollback ever needed.

## BACKLOG to 120 (deferred — execute later)
`docs/BACKLOG_to_120.md`. Remaining 11 pts: **D1 −5** (main lever: more org/engine deltas), D3 −1 (BAD/GOOD for 3 bare NEVER rules), D8 −1 (60-sec quick-start), D6/D7 −1 each (judgment-ceiling), **D4 −1 + D5 −1 policy-capped by no-split**. Cheap genuine pass = +3–4 → ~113–114. **120 NOT reachable under no-split policy**; practical A+ max ≈115–116 with sustained D1 work. Re-run S4 regression + 3-persona loop + judge when executed.

## Related
[[project_data_dev_planning_skill]] (source of the 3-persona pattern), [[project_skill_evaluation]] (Skill-Judge rubric), [[feedback_skill_no_split]] (no file split — fixes stay inline), [[reference_claude_hooks]] (qa-gate-enforcer SubagentStop = ENFORCED).
