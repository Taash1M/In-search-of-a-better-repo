---
name: feedback-agents-use-skills
description: "When delegating build/data work to sub-agents, instruct them to activate the relevant skill AND follow the execution plan exactly; qa-gate now checks plan-compliance"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

When tasking sub-agents to build or do data-engineering work, the agent prompt MUST explicitly
instruct them to (1) **activate and follow the relevant skill** — e.g. the `data-engineering` skill
(orient → TDD-first → implement → validate → review → regression-guard) for pipeline/manifest/grain/
idempotency work — AND (2) **follow the governing execution plan exactly** (cite the
`*_EXECUTION_PLAN.md` + the specific sections). User caught that the Phase-0 build agent was dispatched
without an explicit skill directive, then made "activate skills + follow the plan" a standing
instruction for every agent tasking.

**Why:** sub-agents don't auto-inherit the main session's skill context or the plan; without an explicit
instruction they may skip the disciplined operating loop the skill encodes, or drift from the plan's
contract — producing work that passes a shallow check but misses DE quality bars (e.g. the Phase-2
build self-graded PASS but the independent qa-gate caught 2 blockers: a non-runnable resume path and
tests that asserted nothing — both deviations from plan §4.2 idempotent-resume).

**How to apply:** in every build/data sub-agent prompt, add: "Activate and follow the
`data-engineering` skill's operating loop, AND follow `<plan path>` exactly (§X/§Y)." Pure-infra/IAM
phases (less DE-relevant) can note the skill is optional, but data-bearing phases (Lambdas, transforms,
loaders, manifests) must use it. The `qa-gate` sub-agent (`~/.claude/agents/qa-gate.md`) was enhanced
(2026-06-20) so **plan-compliance is a first-class, always-on check**: it locates the governing
execution plan, treats it as the authoritative spec (not just the handed DoD bullets), and raises a
**blocker** for any material deviation from the plan's contract/architecture/gates — even one the DoD
didn't enumerate. This closed the gap where the gate only checked plan-compliance if the invoker
happened to paste the plan sections in. Related: [[project-data-dev-planning-skill]],
[[feedback-skill-invocation]] (proactively activate skills, FYI as you go).
