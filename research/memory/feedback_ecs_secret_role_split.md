---
name: feedback-ecs-secret-role-split
description: "ECS task vs execution role — which one reads a secret depends on HOW the container reads it; app-side get_secret_value uses the TASK role, the secrets: block uses the EXECUTION role"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2cf779aa-85bb-4baa-9b27-7283644871da
---

When re-pointing an ECS/Fargate task at a new Secrets Manager secret, **two different IAM roles
can gate the read, and you must fix the right one:**

- The taskdef **`secrets:` block** (`ValueFrom <arn>:key::`, injected as env at container start) is read
  by the **EXECUTION role** (`*-task-exec`).
- The **application code calling `get_secret_value`/`get_secret_json(arn)` at runtime** uses the
  **TASK role** (`*-exec` in this project — confusingly named).

If the app reads the secret itself (as `neo4j_load.handler` does), the **TASK role** governs it — and
that grant may live in a DIFFERENT CloudFormation stack than the taskdef (here: the foundation stack,
not phase5_taskdefs). Redeploying only the taskdef stack leaves the task role still scoped to the OLD
secret → `iam simulate-principal-policy` shows `new=implicitDeny, old=allowed`.

**Why:** ARN-scoped least-privilege `secretsmanager:GetSecretValue` on `!Ref Neo4jSecretArn` resolves
per-stack, so each stack that defines a role granting secret access must get the new ARN.

**How to apply:** before launching, run `aws iam simulate-principal-policy` for **BOTH** the task role
and the execution role against BOTH the new and old secret ARNs — expect new=allowed, old=denied on
both. Find every stack that grants GetSecretValue (`grep -rn secretsmanager:GetSecretValue src/iac/`)
and redeploy each with the new ARN. Also note: when the ASL injects the secret ARN from the
START-EXECUTION input (`$.cfg.*`), the launch input — not the stack param — is the deciding value.

Surfaced on the AWS Twin Instance02 cutover (2026-06-23). See [[project-aws-twin]] and
[[feedback-aws-runtime-permission-audit]] (the moto-can't-see-IAM lesson this extends).
