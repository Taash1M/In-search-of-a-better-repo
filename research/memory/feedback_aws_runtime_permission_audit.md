---
name: feedback-aws-runtime-permission-audit
description: "For AWS deploys, run a deployed-config IAM-simulator audit BEFORE first spend; moto-mocked tests can't see IAM/bucket/SFN-integration denials"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

When deploying an AWS pipeline whose build-time tests use **mocked AWS (moto)**, those tests CANNOT
see real IAM policy / S3 bucket-policy / KMS / Step Functions service-integration denials — moto does
not enforce them. The PLM ETL Gold deploy (2026-06-20) hit a SEQUENCE of runtime AccessDenied/Deny
failures, one per live execution, each costing a full setup+trigger cycle: SSE-KMS header missing,
s3:PutObjectTagging missing on two roles, DistributedMap ResultWriter blocked by the bucket SSE-deny,
sfn-exec missing states:StartExecution (Distributed Map launches child execs), bedrock:GetDataAutomation
Status scoped to the wrong ARN (needs `data-automation-invocation/*` not project/profile), and a
Claude model-id triple-mismatch (code vs IAM grant vs the real `…-20250929-v1:0` profile, plus the
`us.` cross-region profile needing the FM ARN in us-east-1/2/us-west-2).

**Why:** mocked unit gates prove the LOGIC is right but say nothing about whether the DEPLOYED principals
can actually perform the API calls the code makes. Discovering these one-per-run is slow and, worse,
some gaps only surface AFTER real spend (e.g. the BDA-output SSE gap strikes after paying for BDA).

**How to apply:** before the FIRST real-spend execution of any deployed AWS pipeline, run an exhaustive
**runtime-permission audit** (the `qa-gate` sub-agent works well for this) that: (1) traces EVERY AWS API
call the runtime makes — including every Step Functions ASL state's service integration (lambda:invoke,
states:StartExecution for Distributed Map, ecs:RunTask.sync incl. its EventBridge managed-rule perms,
aws-sdk:* integrations, bedrock invoke/status on the RIGHT resource ARN); (2) uses
`aws iam simulate-principal-policy` as ground truth for each (principal, action, resource) triple against
the LIVE deployed roles; (3) checks bucket policies vs every write path (SSE-KMS header + exact CMK);
(4) verifies the run-start staging (source/ layout, _START schema, cfg has no placeholders + arrays for
subnets/SGs, live approval item, env vars on ALL functions, layer mounts). Output ONE consolidated,
stage-ordered gap list and batch-fix before triggering. Bake this audit into the data-dev-planning
skill's deploy phase. Related: [[feedback-agents-use-skills]] (qa-gate plan-compliance), [[project-aws-twin]].

**Extension (2026-06-21) — runtime gaps aren't only IAM; ASL/JSONPath and API-contract bugs hide the same way.** More classes surfaced one-execution-at-a-time on the same pipeline: (a) an **ASL JSONPath dereference of an absent field** — `ResumeDecision` referenced `$.ddb.Item`, but DynamoDB GetItem on a NEW key returns no `Item` → fatal uncatchable `States.Runtime` BEFORE the Lambda ran (the resume Lambda was correctly built for item=None but the ASL never reached it; mocked tests invoked the handler directly, bypassing the JSONPath). (b) **Bedrock invoke_model contract**: bare model id `us.anthropic.claude-sonnet-4-5` is invalid (must be the dated inference-profile id `...-20250929-v1:0`), and `max_tokens=65536` exceeds Sonnet 4.5's 64000 → ValidationException on the FIRST invoke — this is also why the deployed Stage-4 enriched 0. (c) **silent-corruption logic bugs**: BDA multi-subdocument splits truncated to sub-doc 0; a `stop_reason==max_tokens` truncated record written to silver as complete. All invisible to moto/mocked tests. **So the audit must ALSO include a live single-doc smoke that exercises the real ASL state-transition/JSONPath wiring + one real model invoke** — not just mocked handler unit tests. When the same logic lives in two code paths (a local runner AND a Lambda), QA BOTH: a fix applied to one (the truncation gate) was missing from the other and a re-gate caught it. Pattern: **find → batch-fix → re-gate, and re-gate again until a clean pass** — the re-gate itself found the final bug.
