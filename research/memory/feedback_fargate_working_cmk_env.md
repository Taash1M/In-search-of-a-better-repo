---
name: feedback-fargate-working-cmk-env
description: "Fargate tasks that write to a CMK-forced S3 prefix need WORKING_CMK_ARN injected in their taskdef — Lambda env-injection does NOT carry to ECS taskdefs; a missing SSE-KMS header → AccessDenied \"explicit deny in resource policy\""
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2cf779aa-85bb-4baa-9b27-7283644871da
---

When an S3 bucket policy **forces SSE-KMS** on a prefix (`DenyUnencryptedPut` /
`DenyWrongKmsKey`, with only specific prefixes in the `NotResource` carve-out), every writer
to a non-carved prefix MUST send the `ServerSideEncryption=aws:kms` + `SSEKMSKeyId=<cmk>`
headers, or the PutObject fails:

`AccessDenied: ... is not authorized to perform: s3:PutObject ... with an explicit deny in a
resource-based policy`

**The gotcha:** a shared S3 helper (e.g. `aws_io._sse_args()`) typically reads the CMK ARN
from an env var (`WORKING_CMK_ARN`) and **silently sends no header when it's unset** (so it
still works under moto, which doesn't enforce bucket policy). Lambda stacks inject that env
into every function — but **ECS/Fargate task definitions are a SEPARATE place** and are easy to
miss. The env does NOT propagate from Lambdas to taskdefs. A Fargate stage that writes to the
CMK-forced prefix then fails AccessDenied at runtime even though the IAM/KMS grants are fine.

**Why it hides:** a stage that only READS S3 (or writes only to a non-S3 sink like Neo4j) never
trips it, so the gap can sit latent until a sibling stage writes gold/silver to the forced prefix.

**How to apply:**
- For EVERY Fargate taskdef that uses the shared S3 writer, inject `WORKING_CMK_ARN` (sourced
  from the same CMK param the Lambdas use), in BOTH the relevant containers — even ones that
  "only read today" (symmetry + regression-safety; the shared helper is one call from writing).
- Add an IaC test asserting the env is present on every taskdef (`...inject_working_cmk_arn`).
- Distinguish from a KMS-grant problem: simulate `kms:GenerateDataKey`/`Decrypt` for the task
  role on the CMK — if allowed, the fix is the missing HEADER (env), not a grant.
- No Docker rebuild needed if the image code already reads the env — just redeploy the taskdef
  stack with the new param + bump the taskdef revision in the launch input.
- Ignore the GuardDuty-sidecar `403 CannotPullContainerError` in ECS failure blobs — it's a
  non-essential AWS-injected container, not your image; read your container's exit code/logs.

Surfaced on the AWS Twin Instance02 cutover gold-write failure (run-2538815a-twin-1, 2026-06-23;
fixed in twin-2). Same CMK-forced-prefix family as the earlier silver/map_results ResultWriter
carve-out lesson. See [[project-aws-twin]], [[feedback-ecs-secret-role-split]],
[[feedback-aws-runtime-permission-audit]].
