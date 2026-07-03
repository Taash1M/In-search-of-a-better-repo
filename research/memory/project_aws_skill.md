---
name: project-aws-skill
description: "aws-dev skill — MCP-enhanced AWS build/deploy/diagnose skill, INSTALLED 2026-06-21. 925 lines single-file; skill-judge 110/120 Grade A; 3-persona clean + 2 qa-gate PASS; bakes in all AWS-Twin runtime-gap lessons. Lives at ~/.claude/commands/aws-dev.md."
metadata: 
  node_type: memory
  type: project
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

## AWS Dev Skill (`aws-dev`)

A reusable Claude Code command-style skill for **creating, deploying, configuring, AND
discovering/diagnosing AWS resources** — and avoiding every runtime gap the [[project-aws-twin]]
engagement hit. **INSTALLED 2026-06-21** at `<ADMIN_HOME>/.claude\commands\aws-dev.md` (now an
active Skill the harness auto-lists). Source/canonical copy + all artifacts:
`<USER_HOME>/OneDrive - <ORG>\AWS\Skill\`.

### What it is
- **Single-file, 925 lines**, deliberate no-split per [[feedback_skill_no_split]] (decision tree + section
  anchors do the routing). Tool/Process hybrid pattern.
- **MCP-enhanced, NOT an MCP server we built**: one AWS skill that uses the official **AWS MCP Server**
  (Agent Toolkit, GA, IAM-SigV4 via `mcp-proxy-for-aws==1.6.0`) + **AWS Knowledge MCP Server** (no-auth,
  the orient/research authority) complementarily — for docs/discover/diagnose. **CloudFormation + CLI
  stay the source of truth for all create/deploy.** MCP config is DRAFT in `Skill/mcp/` (`aws-mcp.mcp.json`
  + `SETUP.md`), registered DELIBERATELY — never auto-installed.
- Encodes the L-rules (L2 KMS duality/caller-of-record, L3/L3a/L3b cross-region inference profiles +
  region-wildcard, L4 BDA-as-service-principal→AES256, L8 ECR immutable-tag, L9 manylinux wheels, L15
  uncatchable States.Runtime, L16 silent-failure/COST_ABORTED mirage, L18 BDA two-ARNs, L19 PassRole +
  Distributed-Map two-ARN-scopes, L20 MCP-green-proves-nothing, L22 MCP governance, L23 Anthropic-native
  MCP not-on-Bedrock), the **mandatory 3-part CLI-driven pre-spend gate** (IAM-sim + KMS-key-policy/bucket
  verify + live real-ASL smoke), and the terminal qa-gate discipline.

### How it was built (discipline)
research (official AWS sites) → `/data-dev-planning` plan (v5 FINAL, ACCEPTED) → `/data-engineering`
discipline → **3-persona adversarial review to clean** (rounds in `Skill/docs/reviews/skill_round1-4`) →
**qa-gate PASS** (`qa_gate_skill_result.md`) → **skill-judge 110/120 Grade A** (`skill_judge_report.md`).
Then judge fixes 2–6 applied (polish; fix #1 length-split DECLINED to keep single-file), **re-qa-gated
PASS** (`qa_gate_skill_polish_result.md`), installed.

### Judge scorecard (110/120, Grade A)
D1 Knowledge Delta 19/20 · D2 Mindset+Procedures 14/15 · D3 Anti-Pattern **15/15** · D4 Spec 14/15 ·
D5 Progressive Disclosure 11/15 (the single-file length cost — accepted trade-off) · D6 Freedom 14/15 ·
D7 Pattern 9/10 · D8 Usability 14/15. No critical issues. Polish fixes push toward ~116/120.

### Companion skills
`data-dev-planning` (plan upstream) · `data-engineering` (generic DE) · `audit-ubi` (audit built systems)
· `ubi-mcp` (the Azure analog — Azure is out of scope for aws-dev). See [[feedback_agents_use_skills]] for
the standing rule to tell every sub-agent to activate the relevant skill + follow the plan.
