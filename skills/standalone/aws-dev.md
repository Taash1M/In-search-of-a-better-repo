---
name: aws-dev
description: "Use when creating, deploying, configuring, OR discovering/diagnosing AWS infrastructure/resources — CloudFormation IaC, least-privilege IAM/KMS/S3, Step Functions + Lambda + ECS/Fargate orchestration, Bedrock model invoke, Bedrock Data Automation (BDA), Nova Canvas, ECR/CodeBuild, Secrets Manager — with the AWS MCP + AWS Knowledge MCP servers for docs/discover/diagnose and a mandatory pre-first-spend runtime-permission audit + live smoke. Trigger on: 'AWS', 'CloudFormation', 'CFN', 'deploy to AWS', 'IAM policy', 'KMS', 'S3 bucket policy', 'Step Functions', 'state machine', 'Lambda', 'Fargate', 'ECS', 'Bedrock', 'BDA', 'Data Automation', 'Nova Canvas', 'ECR', 'CodeBuild', 'Secrets Manager', 'least privilege', 'IAM simulator', 'AccessDenied', 'cross-region inference profile', 'AWS MCP', 'MCP server', 'call_aws', 'aws-mcp', 'Knowledge MCP', 'search_documentation', 'mcp-proxy-for-aws', 'discover AWS resources', 'diagnose AWS'."
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, Agent, Task
---

# AWS Dev Skill

You are an expert AWS infrastructure engineer. This skill lets you **create, deploy, configure, AND
discover/diagnose AWS resources seamlessly** — and, crucially, **avoid every failure mode the AWS Twin
engagement hit** (a real BDA+Claude+Step-Functions+Fargate pipeline that bled ~15+ runtime gaps across
deploys). Every rule below is sourced to either an official `docs.aws.amazon.com` page, the
`MCP_VALIDATION.md` official-source record (for MCP facts), or a production-verified record; rules that
are production-verified-but-not-in-docs are flagged **[production-verified]**.

This skill is the **AWS-specific BUILD/DEPLOY + MCP-OPERATIONS companion** to:
- `data-dev-planning` — produces and hardens the PLAN (upstream; run it FIRST for any non-trivial build).
- `data-engineering` — generic DE discipline (grain/idempotency/TDD/reconciliation) the build follows.
- `audit-ubi` — audits already-built data systems (generic, downstream).
- `ubi-mcp` — the UBI-**Azure** MCP operations skill (this skill is its AWS analog; Azure is out of scope here).

> **House rule (no progressive-disclosure splits):** this is one self-contained file. The decision tree
> and section anchors do the routing that splitting would otherwise do.

---

## The ONE rule that matters most

**Mocked/unit tests (moto, stubbed boto) CANNOT see IAM / KMS-key-policy / S3-bucket-policy /
Step-Functions-service-integration denials, NOR uncatchable `States.Runtime` JSONPath errors, NOR
silent-corruption logic bugs.** "Green unit tests" never authorize a real-spend AWS run. **And neither
does a green MCP `call_aws`/`run_script` — those run as the *MCP caller's* identity, not the runtime
role (L20).** Before ANY full/first-spend execution you MUST run the **3-part pre-spend gate**
(§Pre-spend gate): a deployed-config IAM-simulator audit, a separate KMS-key-policy/bucket/staging
verification, and a **live single-item smoke on REAL services + the REAL deployed ASL**, all
**CLI-driven**. The AWS Twin lost ~6 live runs chasing one error per execution because this gate did not
exist. [production-verified — `project_aws_twin.md`, `feedback_aws_runtime_permission_audit.md`]

---

## Decision tree

```
What is the AWS task?
├─ "Plan / design it first" (no build yet)        → /data-dev-planning (planning is upstream). Come back to build.
├─ Generic DE discipline, not AWS-specific         → /data-engineering (grain/idempotency/TDD/reconciliation).
├─ Audit an ALREADY-BUILT data system (generic)    → /audit-ubi.
├─ Non-AWS cloud (Azure / GCP)                      → OUT OF SCOPE. Azure MCP/UBI ops → /ubi-mcp.
│
├─ FIRST REAL-SPEND AWS EXECUTION IS IMMINENT       → §Pre-spend gate (MANDATORY, CLI-driven; MCP does
│                                                      NOT replace it — L20) BEFORE you spend a cent.
│
│  ── MCP-vs-CLI/CFN routing (the source-of-truth split — see §MCP-vs-CLI/CFN decision matrix) ──
├─ "What's the CURRENT AWS doc / best practice /    → MCP: §AWS Knowledge MCP (or AWS MCP Server
│   service limit / API shape?"                        search_documentation/read_documentation). NOT
│                                                      training-data recall. This is the ORIENT authority.
├─ "Discover / list / read / what exists / why      → MCP: AWS MCP Server `call_aws` (read-only) to
│   did it fail" (diagnose existing resources)         GATHER; the skill's L-rules + the CLI simulator +
│                                                      the §Troubleshooting L5 cheap-first ladder DECIDE
│                                                      (Diagnose = BOTH). §AWS MCP Server runbook.
├─ "Create / deploy / change infra that should be   → CLI + CloudFormation (SOURCE OF TRUTH). Do NOT
│   reproducible"                                      author it as ad-hoc MCP `call_aws` mutations.
├─ "Register / wire up the AWS MCP Server"          → §MCP setup/auth/governance (draft, register
│                                                      DELIBERATELY — not auto-installed).
├─ "Use the MCP connector / Managed Agents on       → §Anthropic-native MCP surfaces — BETA + NOT on
│   our Bedrock-hosted Claude Code"                    Bedrock (L23). Reference/future only.
│
├─ Identity / access (who can do what)             → §IAM, KMS & resource-policy duality
├─ Encryption choice (CMK vs AES256)               → §Encryption: SSE-KMS vs AES256
├─ Provision infra as code                         → §CloudFormation deploy
├─ Package / deploy a Lambda                       → §Lambda (packaging + the code-refresh trap)
├─ Orchestrate (state machine, fan-out)            → §Step Functions (caller-of-record, Distributed Map, States.Runtime)
├─ Run a container (long task, VPC egress)         → §ECS / Fargate networking & the two roles
├─ Call a Bedrock model (Claude etc.)              → §Bedrock model invoke (cross-region profiles)
├─ Extract documents at scale (multimodal)         → §Bedrock Data Automation (BDA)
├─ Generate an image on AWS                         → §Nova Canvas (NOT GPT-Image — it is not on Bedrock)
├─ Build/push a container image                    → §ECR & CodeBuild (immutable tags, in-cloud build)
├─ Store a secret / credential                     → §Secrets Manager
├─ Governance, cost, Config/Control-Tower          → §Governance, cost & Config
├─ Lay out data on S3                               → §S3 medallion data architecture
└─ "Access Denied" / a run failed                  → §Troubleshooting decision trees (cheap check FIRST)
```

## Operating loop

Run sequentially. Report at each phase boundary. Use the task-tracking tool (`Task`) to track phases; mark
`in_progress` / `completed`. (Loop phases 0–8 and the §Worked-example steps 1–12 are different
granularities of the SAME flow — not a 1:1 step map.)

```
0. ORIENT (MCP)    → for any AWS rule you're about to rely on, look up the CURRENT doc via the AWS
                     Knowledge MCP / search_documentation INSTEAD of training-data recall (L16 source).
                     This grounds every L-rule below in current docs.
1. ORIENT (DATA)   → invoke /data-engineering for the data contract (grain, keys, idempotency, reload,
                     invariants). Read the governing *_EXECUTION_PLAN.md — it is the authoritative spec.
2. PLAN            → if no reviewed plan exists, run /data-dev-planning FIRST. Do not build off an
                     unreviewed plan for anything that spends money or has irreversible side-effects.
3. BUILD (TDD)     → author IaC + code test-first. CloudFormation + CLI/boto3 are the SOURCE OF TRUTH
                     for all create/deploy (auditable, repeatable, reviewable) — never author
                     create/deploy as ad-hoc MCP mutations. Mocked tests prove LOGIC only (The ONE rule).
                     Content-address with sha256; idempotency key = (sha256, blueprint_version).
4. DISCOVER/DIAGNOSE (MCP) → use read-only `call_aws`/`run_script` (under a resource-scoped read-only
                     role) to inspect deployed state, gather evidence for the pre-spend audit, and trace
                     failures. MCP GATHERS; the skill's L-rules + the CLI simulator DECIDE.
5. PRE-SPEND GATE  → MANDATORY before first/full spend (CLI-driven; §Pre-spend gate): (a) IAM-simulator
                     audit over the itemized surface; (b) KMS-key-policy + bucket-policy + run-start
                     staging verify (simulator is BLIND to key policies); (c) LIVE single-item smoke on
                     REAL services + REAL ASL. A green MCP read does NOT substitute for any part (L20).
6. FULL-RUN AUTH   → the live smoke from step 5(c) IS pre-spend-gate part (c) (not a second smoke). The
                     full run is HARD-GATED on: that smoke green (its qa-gate PASS) + (if it spends) the
                     user having seen the smoke result + the projected full-run cost and given go/no-go.
7. FULL RUN        → checkpointed, idempotent, cost-ceiling that ABORTS on breach, tagged for cost
                     attribution. Verify REAL side-effects after the run (never trust green status — and
                     never trust a green MCP read as proof of real state, L16/L20).
8. QA-GATE         → terminal qa-gate per artifact (see §QA gate). find→batch-fix→re-gate, and re-gate
                     AGAIN until a fully clean pass (the re-gate itself may surface the final bug). ANY
                     runbook that MUTATES state — CLI/CFN OR a mutating MCP `call_aws`/`run_script` —
                     ends with the qa-gate.
```

**Delegation rule [L14]:** every build/data sub-agent you spawn MUST be told, in its prompt, to
"**activate the relevant skill (this `aws-dev` skill and/or `data-engineering`) AND follow the governing
`*_EXECUTION_PLAN.md` exactly (cite §X)**." Sub-agents do not inherit your skill context or the plan.
**This explicitly covers any sub-agent you tell to use MCP:** name the MCP server (AWS MCP Server vs AWS
Knowledge MCP) AND its read-only-vs-mutating posture (default read-only; mutation is G0-gated, §MCP
setup). [production-verified — `feedback_agents_use_skills.md`]

---

## Foundational rules (ground everything below)

### IAM evaluation logic (research §1) — only the non-obvious parts
(Implicit-deny / explicit-Deny-wins basics assumed.) The traps:
- Same-account **identity + resource policies = UNION** (an Allow in either suffices).
- **SCP / RCP / permission-boundary = INTERSECTION guardrail** — they grant nothing; they only deny. An
  SCP `Deny` beats any IAM `Allow`. (This is WHY §Governance's Control-Tower SCP denies bite.)
- **KMS is the documented EXCEPTION to the union rule** — a key policy does NOT auto-trust the account, so
  IAM `kms:*` alone is insufficient; see the duality below (§IAM/KMS L2).
- Source: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_evaluation-logic.html

### Canonical IAM-simulator blind-spot list (research §4) — state once, reference everywhere
`aws iam simulate-principal-policy` does **NOT** evaluate: **(1) KMS key policies, (2) RCPs, (3)
conditioned SCPs, (4) cross-account resource policies for roles.** Therefore **a green simulator result
does NOT prove KMS-key-policy access** — the pre-spend gate verifies the key policy SEPARATELY. **And a
green MCP `call_aws`/`run_script` proves even less** — it runs as a *different* principal (the MCP
caller, not the runtime role) and the sandbox cannot see key policies, the real ASL, or integration
seams (L20).
- Source: https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_testing-policies.html

### ARN hygiene (no PII / no account-as-universal)
All ARN shapes in your work use `<acct>` / `<region>` / `<resource>` **placeholders**. The AWS-Twin
reference environment (account `<acct>`, region `us-east-2`, BDA profile `us.data-automation-v1`, the MCP
`AWS_REGION=us-east-2` routed-region example) is an EXAMPLE, not a universal constant — never paste a real
account id into a copy-pasteable ARN/command, and the MCP endpoint region + routed region are choices, not
constants (§MCP setup).

---

## IAM, KMS & the resource-policy duality

**Use when:** granting any principal access; wiring KMS or S3 bucket policies; debugging an access denial.

### Least-privilege, resource-ARN-scoped IAM
- Grant only the actions on the specific resource ARNs under the specific conditions needed. Start from a
  broad managed policy only to discover the surface, then reduce to a customer-managed policy scoped to
  exact ARNs. Use IAM Access Analyzer to generate from CloudTrail + validate.
- Source: https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html

### KMS duality — BOTH the IAM policy AND the key policy [L2]
**The headline rule:** *"Unless the key policy explicitly allows it, you cannot use IAM policies to allow
access to a KMS key. Without permission from the key policy, IAM policies that allow permissions have no
effect."* A KMS key policy does NOT automatically trust the account — granting IAM `kms:*` alone is
**insufficient**.
- The default `Sid: "Enable IAM User Permissions"` statement (`Principal:{"AWS":"arn:aws:iam::<acct>:root"}`,
  `Action:"kms:*"`, `Resource:"*"`) lets the account DELEGATE via IAM. If it (or a statement naming the
  principal directly) is absent, IAM grants do nothing for that key.
- **Caller-of-record matters [L2]:** a Step Functions native/optimized/`.sync` task runs as the **STATE
  MACHINE EXECUTION ROLE**, NOT as any Lambda's role. So the SM role — not the Lambda role — is the
  principal that must be named in the key policy and granted the kms actions. (See §Step Functions.)
- **Per-operation least-privilege CMK actions for S3 SSE-KMS** (research §2 — do NOT over-grant):
  | Operation | KMS action |
  |---|---|
  | Write (PutObject, SSE-KMS) | `kms:GenerateDataKey` |
  | Read (GetObject) | `kms:Decrypt` |
  | Always | `kms:DescribeKey` |
  | Re-encrypt (**only if** you actually re-encrypt) | `kms:ReEncrypt*` |
  | Multipart upload | both GenerateDataKey + Decrypt |
  **NOT `kms:Encrypt`** for S3 SSE-KMS — S3 uses envelope encryption via GenerateDataKey; listing Encrypt
  is an over-grant. (**The proven Twin grant was `Decrypt` + `GenerateDataKey`.**) [production-verified]
- A **service principal** that touches an encrypted resource on your behalf must be permitted in the key
  policy: `Principal:{"AWS":"*"}` + `Condition:{"StringEquals":{"kms:CallerAccount":"<acct>",
  "kms:ViaService":"<svc>.<region>.amazonaws.com"}}`. (See §BDA for the BDA caveat — ViaService is
  UNVERIFIED for BDA.)
- Sources: https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html ,
  https://docs.aws.amazon.com/kms/latest/developerguide/key-policy-default.html ,
  https://docs.aws.amazon.com/kms/latest/developerguide/conditions-kms.html

### S3 bucket policy patterns
- **Enforce SSE-KMS:** Deny `s3:PutObject` when `Null:{"s3:x-amz-server-side-encryption-aws-kms-key-id":
  "true"}`, or pin a specific CMK by equality on that key.
- **TLS-only:** Deny when `Bool:{"aws:SecureTransport":"false"}`.
- **Block Public Access** on every bucket (overrides permissive ACL/policy).
- **NotResource carve-out:** a CMK-deny bucket policy can `NotResource` specific prefixes to let a
  service write AES256 to just those prefixes (the BDA-I/O pattern — see §Encryption).
- Source: https://docs.aws.amazon.com/AmazonS3/latest/userguide/UsingKMSEncryption.html

### iam:PassRole for service integrations [L19]
A service integration that passes a role (e.g. Step Functions `ecs:RunTask.sync` passes the task +
execution roles) requires **`iam:PassRole`** on the caller (the SM exec role), scoped to the passed role
ARNs with the `iam:PassedToService` condition. Omitting it → AccessDenied at RunTask. Include it in the
pre-spend IAM-sim audit. [production-verified]

---

## Encryption: SSE-KMS (payloads) vs AES256/SSE-S3 (service I/O)

**Use when:** choosing bucket encryption; a managed service can't read/write your bucket.

- **SSE-KMS (`aws:kms`, a CMK):** for **PAYLOADS** (PII, derived data — silver/gold). Needs KMS perms +
  the key policy (duality). The **CMK must be symmetric and in the SAME Region as the bucket**. Enable
  `BucketKeyEnabled` to cut KMS request cost ~99%.
- **AES256 (SSE-S3):** S3-managed keys, **no KMS principal needed**. Use for **service I/O** a managed
  service writes (see L4 below) and any non-sensitive area.
- **The SSE split [good pattern]:** put PII/derived payloads behind a CMK; keep a managed service's I/O
  prefixes on AES256. Enforce explicit SSE-KMS on payload prefixes via the bucket policy; carve the
  service-I/O prefixes out with `NotResource`.

### A managed service may access S3 as its OWN service principal [L4]
**BDA (and likely other Bedrock async S3-output features) reads/writes S3 as the Bedrock SERVICE
PRINCIPAL, not as your caller role, and `InvokeDataAutomationAsync` has NO serviceRole param to redirect
it.** Consequences:
- A customer **CMK** bucket the service principal doesn't trust → denied, and **granting the CALLER role
  on the CMK does NOT help** (the actor is the service, not the caller).
- **DEFAULT proven fix:** set **AES256 (SSE-S3)** on the service's I/O prefix (the proven 624/624 manual
  BDA run worked precisely because its bucket was AES256). [production-verified — `project_aws_twin.md`
  gap #10]
- The key-policy service-principal grant (`kms:ViaService` + `kms:CallerAccount` for the Bedrock service
  principal) is a valid documented KMS pattern in general, BUT is **UNVERIFIED specifically for BDA** —
  present it only as an untested alternative the user must validate live, **never as the primary fix**.
- Source: https://docs.aws.amazon.com/bedrock/latest/userguide/bda.html (S3-access behavior production-verified)

---

## CloudFormation deploy

**Use when:** provisioning any infra (always IaC, never click-ops; **never ad-hoc MCP `call_aws create-*`**
— that leaves no version-controlled artifact, §MCP-vs-CLI/CFN matrix).

- **Package + upload:** `aws cloudformation deploy --s3-bucket <b>` uploads the template (REQUIRED for
  templates > 51,200 bytes). `--no-execute-changeset` to review a change set first. **Capabilities:**
  `CAPABILITY_IAM`, or **`CAPABILITY_NAMED_IAM`** if any IAM resource has a custom name (omitting it →
  `InsufficientCapabilities`).
- **CMK-deny bucket trap [L6]:** `deploy --s3-bucket` uploads the template WITHOUT an SSE-KMS header → a
  CMK-deny bucket rejects it. **Fix:** upload explicitly with `aws s3 cp template.yaml s3://<b>/key
  --sse aws:kms --sse-kms-key-id <arn>` (or `deploy --kms-key-id <arn>`), then `create/update-stack
  --template-url https://<b>.s3.../key`. [production-verified]
- **Lambda code does NOT refresh on `update-stack` if the S3 key is unchanged [L7]** — it is a silent
  no-op. **Fix:** either change `S3Key`/`S3ObjectVersion` (new versioned key) OR call
  `aws lambda update-function-code` directly. **Also: a CFN stack update can RESET Lambda layers** —
  reattach them after the update. [production-verified]
- Sources: https://docs.aws.amazon.com/cli/latest/reference/cloudformation/deploy.html ,
  https://docs.aws.amazon.com/cli/latest/reference/cloudformation/create-stack.html ,
  https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-lambda-function.html

---

## Lambda (packaging + the code-refresh trap)

**Use when:** building/deploying a Lambda.

- **Cross-platform wheels [L9]:** Windows `pip install` builds **Windows wheels (.pyd)** that **fail in a
  Linux Lambda/layer**. Fix: `pip download --platform manylinux2014 --only-binary=:all: -r reqs.txt -d ./build`
  then unzip into the package; OR build the artifact in-cloud via **CodeBuild** (§ECR & CodeBuild). Pure-Python
  deps are fine either way.
- **Code refresh:** see §CloudFormation L7 — same-key re-upload is a no-op; `update-function-code` or new key.
- **Layers:** a CFN update can reset them; reattach. Keep handler logic importable so tests target functions.
- Source: https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

---

## Step Functions (caller-of-record, Distributed Map, States.Runtime)

**Use when:** orchestrating Lambda/ECS/Bedrock/BDA; fan-out over many items.

- **Integration patterns:** Request/Response, **Run-a-Job `.sync`** (waits), **Wait-for-Callback
  `.waitForTaskToken`**. SDK integrations `arn:aws:states:::aws-sdk:svc:action`; optimized
  `arn:aws:states:::lambda:invoke` / `:::ecs:runTask.sync`.
- **Caller-of-record [L2]:** native/optimized/SDK/`.sync` tasks run as the **STATE MACHINE EXECUTION
  ROLE**, not any Lambda role. So the SM role needs the downstream perms (`bedrock:Invoke*`, `s3:*`,
  `kms:Decrypt`/`GenerateDataKey`, `ecs:RunTask`, **`iam:PassRole`** [L19]) AND must be the principal named
  in any CMK key policy it touches. Trust principal `states.amazonaws.com`; scope `aws:SourceArn`/
  `aws:SourceAccount` (confused-deputy).
- **Distributed Map launches CHILD EXECUTIONS** — the SM role needs **two distinct ARN scopes** [L19,
  research §6]: `states:StartExecution` on the **stateMachine ARN**; `states:DescribeExecution` /
  `states:StopExecution` on the **`execution:<sm>/*` child-execution ARN** (do NOT scope all three to one
  ARN). PLUS the **S3 ItemReader / ResultWriter perms** and a **`bronze/map_results/*` SSE carve-out** if
  the bucket is CMK-deny. `ecs:RunTask.sync` additionally needs its **EventBridge managed-rule perms**.
- **`States.Runtime` is UNCATCHABLE [L15]:** a JSONPath dereference of a **possibly-absent field** — e.g.
  `$.ddb.Item` when DynamoDB `GetItem` on a brand-new `(sha256, blueprint_version)` returns **no `Item`** —
  throws a fatal `States.Runtime` that runs BEFORE the Lambda and **bypasses `Catch[States.ALL]`** (input/
  output processing errors are uncatchable). It is **invisible to mocked handler tests** (they call the
  handler directly, skipping the ASL JSONPath) **AND invisible to a green MCP read** (the MCP sandbox does
  not exercise the real ASL — L20). **Fix:** pass the always-present container (`$.ddb`) into the task and
  `.get("Item")` defensively in-handler. The live smoke MUST exercise the real ASL state-transition/JSONPath
  wiring. [production-verified — `project_aws_twin.md` gap #8]
- Sources: https://docs.aws.amazon.com/step-functions/latest/dg/concepts-service-integrations.html ,
  https://docs.aws.amazon.com/step-functions/latest/dg/use-dist-map-orchestrate-large-scale-parallel-workloads.html ,
  https://docs.aws.amazon.com/step-functions/latest/dg/concepts-error-handling.html

---

## ECS / Fargate networking & the two roles

**Use when:** running a long/containerized task; the task needs network egress.

- **Two distinct roles:** the **task EXECUTION role** (`executionRoleArn`, managed policy
  `AmazonECSTaskExecutionRolePolicy`) pulls the ECR image, writes logs, and **retrieves Secrets/SSM
  referenced in the task def** — so the EXECUTION role (not the task role) needs `secretsmanager:GetSecretValue`
  (+ `kms:Decrypt` for a custom CMK). The **task ROLE** (`taskRoleArn`) is the app's runtime AWS perms
  (S3, Bedrock). Both trust `ecs-tasks.amazonaws.com`.
- **Egress [L11]:** a Fargate task must have a route to the internet to pull its image and reach public
  endpoints (e.g. Neo4j Aura). Options: public subnet + `assignPublicIp=ENABLED`; **private subnet + NAT
  gateway** (private route table `0.0.0.0/0` → NAT); or ECR/SSM/Secrets interface VPC endpoints. **An
  account may have NO default VPC** — then you must build the VPC + subnets + IGW/NAT + route tables + SGs
  yourself. [production-verified]
- **When launched via SFN `ecs:RunTask.sync`:** the SM exec role needs `iam:PassRole` on BOTH this
  execution role AND the task role ARNs (§Step Functions L19) — and the EXECUTION role (not the task
  role) is the one that needs `secretsmanager:GetSecretValue` for task-def `secrets`.
- Sources: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html ,
  https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task-iam-roles.html ,
  https://docs.aws.amazon.com/AmazonECS/latest/developerguide/fargate-task-networking.html

---

## Bedrock model invoke (cross-region inference profiles)

**Use when:** calling Claude (or any FM) on Bedrock.

- **Cross-region profile [L3 / L3a]:** an id prefixed `us.` / `global.` (e.g.
  `us.anthropic.claude-sonnet-4-5-20250929-v1:0`) routes one call to one of SEVERAL regions. The model id
  passed to `invoke_model` must be the **exact dated inference-profile id**, NOT the bare FM id.
  (Only the `us.` set is production-verified here; a `global.` profile's routing region set is
  undocumented/unverified — simulator-sweep it per its own routing, same as BDA.)
- **IAM:** grant `bedrock:InvokeModel*` on BOTH the **inference-profile ARN** AND the **FM ARN**, with a
  **wildcard on ONLY the region segment** (acct + exact id stay pinned — **never an action or account
  wildcard**; still least-privilege). AWS: *"you must also specify the foundation model in each Region
  associated with it."* Per-region enumeration is a trap.
  - Profile ARN: `arn:aws:bedrock:*:<acct>:inference-profile/us.anthropic.claude-sonnet-4-5-20250929-v1:0`
  - FM ARN: `arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0` (no acct, `::`)
  - `bedrock:InvokeModel*` is a deliberate action-FAMILY suffix (covers `InvokeModelWithResponseStream`),
    NOT the prohibited bare-action wildcard — the region/account/resource stay pinned.
- **Observed routing region set (Bedrock Claude `us.` model) [production-verified, L3a]:** us-east-1,
  us-east-2, **us-west-2** — the region-wildcard covers all; simulator-sweep these to verify.
- **The model-id triple-match [L3a]:** the id in your CODE, the id GRANTED in IAM, and the REAL deployed
  profile must all agree — a mismatch fails the FIRST invoke. And **`max_tokens` must be ≤ the TARGET
  model's documented output ceiling** (verify PER MODEL — Sonnet 4.5 = **64000** is the Twin's value, NOT
  universal; `65536` → `ValidationException` on first invoke, which is exactly why a deployed enrich stage
  once produced 0). Look the current ceiling up via the AWS Knowledge MCP / `search_documentation` rather
  than recalling it. [production-verified]
- Sources: https://docs.aws.amazon.com/bedrock/latest/userguide/cross-region-inference.html ,
  https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-prereq.html

---

## Bedrock Data Automation (BDA)

**Use when:** extracting structure from documents at scale (PDF/TIFF/DOCX/images only — BDA natively
rejects DWG/FM/PPTX/etc.; render those off-cloud first or reuse existing extractions).

- **API:** async **`InvokeDataAutomationAsync`** → poll **`GetDataAutomationStatus`**. Input/output via S3
  URIs; `dataAutomationProjectArn` + a REQUIRED **`dataAutomationProfileArn`** pinned to
  `us.data-automation-v1`.
- **IAM — two DIFFERENT ARNs, do not conflate [L18]:**
  - `bedrock:InvokeDataAutomationAsync` → region-WILDCARD profile ARN
    `arn:aws:bedrock:*:<acct>:data-automation-profile/us.data-automation-v1` (cross-region, same trap as L3).
  - `bedrock:GetDataAutomationStatus` → **`arn:aws:bedrock:<region>:<acct>:data-automation-invocation/*`**
    — NOT the project/profile ARN (a common misconfig that denies every status poll). [production-verified]
- **Observed routing region set (BDA `us.data-automation-v1`) [production-verified, L3b]:** us-east-1,
  us-east-2, **us-west-1** — note this DIFFERS from the Bedrock-model set (which is us-west-2). The
  home-region set is **undocumented / non-deterministic**; the region-WILDCARD is the only robust resource.
  Simulator-sweep the **union (us-east-1/2 + us-west-1/2)** to verify both. [production-verified —
  `project_aws_twin.md` gap #9]
- **S3 access:** BDA reads/writes as the **Bedrock service principal** (§Encryption L4) → put BDA I/O on
  **AES256**, NOT a customer CMK.
- **The generic "Access Denied. Check S3 URIs" is an authz-OR-missing-input message** — see §Troubleshooting.
- Source: https://docs.aws.amazon.com/bedrock/latest/userguide/bda.html (overview; params production-verified)

---

## Nova Canvas (AWS-native text-to-image)

**Use when:** generating images on AWS. **[L12 — provider fidelity]** **GPT-Image is NOT hosted on
Bedrock.** The AWS-native text-to-image model is **Amazon Nova Canvas** (`amazon.nova-canvas-v1:0`, via
`InvokeModel`, returns base64 PNG at fixed supported dimensions); alternatives are Titan Image Generator
v2 / Stability. Always verify a named model is actually hosted on the target cloud before asserting it —
confirm via the AWS Knowledge MCP / `search_documentation`, not recall.
- Source: https://docs.aws.amazon.com/nova/latest/userguide/image-generation.html

---

## ECR & CodeBuild

**Use when:** building/pushing a container image.

- **Immutable-tag trap [L8]:** an `IMMUTABLE` repo rejects a re-push of an existing tag
  (`ImageTagAlreadyExistsException`) — **pushing `:latest` a second time FAILS and can block subsequent
  pushes.** Push only a **unique versioned tag** (e.g. `run2538815-3`); the buildspec must NOT also push
  `:latest`. [production-verified]
- **In-cloud build [L13, branch of L9]:** **no local Docker? → build in-cloud via CodeBuild → ECR.**
  CodeBuild also produces Linux/manylinux wheels (avoiding the Windows-wheel trap). Define steps in a
  `buildspec.yml`.
- Sources: https://docs.aws.amazon.com/AmazonECR/latest/userguide/image-tag-mutability.html ,
  https://docs.aws.amazon.com/codebuild/latest/userguide/welcome.html

---

## Secrets Manager

**Use when:** storing a credential / connection string / API key.

- `secretsmanager:GetSecretValue` scoped to the secret ARN (+ `kms:Decrypt` + key-policy access for a
  custom CMK). ECS injects via the task-def `secrets` block (`valueFrom` ARN) — the **EXECUTION role**
  needs GetSecretValue (§ECS/Fargate). Never hard-code secrets; rotate; keep local copies shredded.
- **MCP boundary:** the default read-only MCP role **EXCLUDES `secretsmanager:GetSecretValue`** (§MCP
  setup) — never read secret values through `call_aws`/`run_script`.
- Source: https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html

---

## Governance, cost & Config

**Use when:** standing up governance, budgets, or compliance controls.

- **Fail-closed governance gate G0 [good pattern]:** the write/upload path asserts a signed approval
  artifact and `exit(1)`s if absent — machine-enforced, not prose. Undetermined export-control/PII items
  default to **quarantine**, not "process anyway." **Any MUTATING MCP path (a `call_aws`/`run_script`
  that changes state or egresses data) passes this SAME G0 gate + cost-ceiling + terminal qa-gate** —
  MCP is never an un-audited side channel around governance (L22, §MCP setup).
- **Cost-admission gate + ceiling [good pattern]:** before a paid run, estimate cost from a measured unit
  (per-page/row/token); a hard ceiling that **ABORTS the run (fail-closed) on breach**. **Before the FIRST
  paid run, surface the projected full-run cost (unit × volume) to the user and obtain explicit go/no-go —
  the ceiling-abort is the BACKSTOP, not the approval.** Tag every resource with cost-allocation tags
  (`Project=`, `env=`) and reconcile vs Cost Explorer. (Tag the MCP role/session too, §MCP setup.)
- **AWS Config / Control Tower SCP [L10]:** a Control-Tower / Landing-Zone account has an **org-managed
  Config recorder**, and a guardrail SCP commonly **denies `config:PutConfigurationRecorder`** — you
  **cannot create your own recorder** (it will roll back the stack). Attach Config **RULES** to the org
  recorder via `config:PutConfigRule` (typically allowed); make any recorder infra robustly optional.
  Remember SCPs deny regardless of IAM (Foundational rules).
- Sources: https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html ,
  https://docs.aws.amazon.com/config/latest/developerguide/stop-start-recorder.html ,
  Well-Architected Security + Cost pillars:
  https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html ,
  https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html

---

## S3 medallion data architecture

**Use when:** laying out data for an AWS-native pipeline.

- **Medallion on S3 [good pattern]:** `source/ → bronze/ → silver/ → gold/` under a frozen housekeeping
  partition (e.g. a fixed `date=` prefix, or content-addressed paths). Bronze is content-addressed; silver/
  gold are payloads.
- **Content-addressed keys + DynamoDB idempotency [good pattern]:** key objects by **sha256** of content;
  the idempotency authority is a DynamoDB item keyed **`(sha256, blueprint_version)`** (**PK = sha256 / SK
  = the blueprint/prompt version — NOT a Lambda/object version**). Rerun == run-once. Carry an explicit
  **disposition state** on each item (`PENDING` / `COMPLETED` / `QUARANTINED` / outstanding); **resume
  re-claims everything NOT `COMPLETED`** — including items a "succeeded" orchestration step left in
  `PENDING` (a `CostAborted`/silently-failed step can roll an item back to PENDING while the Map reports
  success — the mirage; see §Silent-failure hunting). Never re-run a `COMPLETED` item.
- **Producer/consumer S3 key-contract [good pattern — the gap-#11 PREVENTION]:** the producer write-key and
  the consumer read-key must be **identical INCLUDING the file extension**. Thread the key components
  (sha256 + `ext`) through the worklist row → the Map `ItemSelector` → the consumer's input URI (e.g.
  `States.Format('.../bronze/docs/{}{}', $.sha256, $.ext)`), and **assert a contract test** that
  write-key == read-key. The Twin's single bloodiest gap (~6 lost runs) was an upload writing
  `bronze/docs/<sha>.pdf` while the ASL read `bronze/docs/<sha>` (no extension) → 404 surfaced as the
  generic BDA "Access Denied. Check S3 URIs." [production-verified — `project_aws_twin.md` gap #11]
  > **The break was in the ASL `States.Format` template, NOT in Python — so a pure Python
  > write-key==read-key unit test would PASS while the deployed ASL still dropped the extension (mocked
  > tests don't exercise the ASL — L15).** The contract test MUST therefore EITHER (a) parse the deployed
  > ASL `States.Format` input URI and assert it includes the `ext` component, OR (b) be covered by the
  > live single-item smoke (pre-spend gate part c) which exercises the REAL ASL. A Python-only contract
  > test is insufficient.
- **SSE split:** payloads (silver/gold) behind a CMK; service I/O (bronze BDA prefixes) on AES256 (§Encryption).

---

## AWS MCP Server (Agent Toolkit) — docs + discover/read/diagnose at runtime

**Use when:** you need the CURRENT AWS doc/best-practice (orient), OR to discover/list/read/diagnose
existing AWS state — **NOT** to author create/deploy (that is CLI+CFN, §MCP-vs-CLI/CFN matrix). All facts
here are grounded in `Skill/docs/research/MCP_VALIDATION.md` (official AWS Agent Toolkit GA blog +
`docs.aws.amazon.com/agent-toolkit` + `awslabs/mcp`).

- **What it is [L21]:** the official **AWS MCP Server (Agent Toolkit), GA** — a managed remote MCP server
  with a single endpoint, CloudWatch `AWS-MCP` metrics, and IAM-based access; **CloudTrail logs all API
  calls** (and at minimum every `call_aws`).
- **Tools:**
  - `search_documentation` / `read_documentation` — current AWS docs at query time. **No auth.** This is
    the **orient/research authority** that replaces training-data recall (criterion 16, strengthens every
    L-rule's grounding).
  - `call_aws` — runs any of 15,000+ AWS API operations **using your IAM credentials**. Full-API reach;
    **its safety comes entirely from the assumed ROLE, not the tool** — use the resource-scoped read-only
    role (§MCP setup). Read-only describe/get/list is the default use: fast, low-token diagnosis, audited.
  - `run_script` — runs a short Python script **server-side in a sandbox** that inherits IAM perms but has
    **no internet egress (it can still invoke AWS APIs as that identity — that is how it does multi-resource
    reads; "no network" means no arbitrary outbound, NOT exempt from least-privilege/audit)**. Good for
    one-shot read aggregation (e.g. "summarize all roles that can assume X"). Governed **identically to
    `call_aws`** (same resource-scoped read-only role + audit); a **mutating** `run_script` is a mutation
    path (G0 + cost-ceiling + qa-gate, L22). **A green `run_script` return is subject to the L16
    verify-real-side-effects rule** (green ≠ real-state truth — reconcile with a CLI read).
  - **Skills** — curated best-practice guidance maintained by AWS service teams (this replaced the older
    "Agent SOPs" / `retrieve_skill` naming; advisory — this skill's L-rules govern on conflict).
- **Endpoint (pinned, L21):** `https://aws-mcp.us-east-1.api.aws/mcp` (N. Virginia) or Frankfurt; can call
  ANY region — routed region set via `--metadata AWS_REGION=<region>` (independent of the endpoint
  region). The endpoint region is **where the MCP request transits**; choose it by data-residency policy
  (§MCP setup). Proxy `mcp-proxy-for-aws==1.6.0` bridges SigV4→OAuth via `uvx`. **No `@latest`.**
- **L20 boundary (load-bearing):** a green `call_aws`/`run_script` does **NOT** prove the *runtime* role
  (SFN exec role / Lambda role / BDA service principal) has its perms — it runs as the MCP caller, a
  *different* principal — and the sandbox can't see KMS key policies, the real ASL JSONPath wiring, or
  integration-seam denials. **The CLI `simulate-principal-policy` audit + the live real-ASL smoke remain
  mandatory and CLI-driven (§Pre-spend gate). MCP does not replace any part of the gate.**
- Sources: `MCP_VALIDATION.md §1`;
  https://docs.aws.amazon.com/agent-toolkit/latest/userguide/mcp-server.html ;
  https://aws.amazon.com/blogs/aws/the-aws-mcp-server-is-now-generally-available/

## AWS Knowledge MCP Server — the orient/research authority

**Use when:** looking up ANY current AWS doc, API reference, best practice, or service limit — **instead
of training-data recall.** This is what grounds every L-rule above in current docs (criterion 16).

- **What [L21]:** a managed remote docs/API-reference server at
  **`https://knowledge-mcp.global.api.aws`** — **credential-free per the awslabs install config, but
  not-verbatim-confirmed (confirm before air-gapped reliance; see Auth)**. The `global.api.aws` endpoint
  receives your orient-phase queries — confirm the processor boundary if residency-sensitive (§MCP setup).
- **Auth:** the awslabs install config specifies only the URL → **no-credentials**, BUT this is
  **awslabs-config-supported, not verbatim-confirmed** — flag it as such and **confirm before relying on
  it for an air-gapped use case** (`MCP_VALIDATION.md §2`).
- Sources: `MCP_VALIDATION.md §2`; `https://github.com/awslabs/mcp`.

## MCP-vs-CLI/CFN decision matrix (the source-of-truth split)

For each operation class: use **MCP** / use **CLI+CFN** / use **BOTH**. This is the routing the decision
tree points at. **One-line headline:** *Use MCP for orient/research (Knowledge MCP = the current-doc
authority, not training-data recall), discover/read, and diagnose; use CLI+CFN for create/deploy and the
mandatory pre-spend gate (policy-sim + live smoke); use BOTH for diagnosis (MCP gathers, the skill
decides). MCP never bypasses the IaC + pre-spend-gate + qa-gate discipline.*

| Operation class | Primary tool | Rationale | Guardrails |
|---|---|---|---|
| **Orient / research** (current doc, best practice, limit, API shape) | **MCP: AWS Knowledge MCP** (or AWS MCP Server `search_documentation`/`read_documentation`) | Authoritative + always-current; replaces training-data recall → strengthens L1–L19 grounding (criterion 10/16) | Read-only; doc tools **no-auth** (Knowledge-MCP no-auth is awslabs-config-supported, not verbatim-confirmed — confirm before air-gapped reliance). **Preferred** over recalling AWS behavior. |
| **Discover / list / read state** (what exists; this role's policy; bucket encryption; profile region) | **MCP: AWS MCP Server `call_aws`** (read-only describe/get/list) | Fast, low-token, IAM-scoped; diagnosis without writing a script | Use the **resource-scoped read-only role** (§MCP setup). Safe **ONLY under that role** (`call_aws` itself has full-API reach — safety is the role, not the tool); audited (CloudTrail). |
| **Diagnose** (why did it fail; trace AccessDenied; deployed-vs-plan) | **BOTH** — MCP reads + the CLI Diagnose-AccessDenied stepped ladder (L5) | MCP makes the cheap reads cheap; the L5 ladder is the *method* and stays authoritative | MCP `call_aws`/`run_script` (read-only) accelerates evidence-gathering; the **diagnosis logic is the skill's, not the server's**. |
| **Multi-step read/aggregate** (all roles that can assume X; reconcile deployed config vs plan) | **MCP: AWS MCP Server `run_script`** (read-only) | Sandboxed Python, IAM perms; invokes AWS APIs as the identity but **no internet egress** — good for read-heavy AWS-API aggregation in one shot | Governed identically to `call_aws` ("no network" ≠ exempt from least-privilege); a mutating `run_script` is a mutation path (below). A green `run_script` is subject to the L16 verify-real-side-effects rule. |
| **Authoritative best-practice / SOP** | **MCP: AWS MCP Server Skills** + AWS Knowledge MCP | Curated by AWS service teams; current | Advisory; the skill's L-rules govern where they conflict with generic advice. |
| **Create / provision infra** | **CLI+CFN (source of truth)** | IaC is auditable, repeatable, reviewable, diff-able, change-set-able | **Do NOT** author create/deploy as MCP `call_aws create-*` mutations (no version-controlled artifact). CFN template + change set + capabilities (L6/L7). |
| **Deploy / update infra** | **CLI+CFN (source of truth)** | Same; plus the CFN traps (L6 SSE-KMS upload, L7 Lambda-code-refresh + layer reattach) are CLI/CFN-specific | Lambda code refresh = `update-function-code` or new S3 key (L7). |
| **Policy simulation (pre-spend gate part a)** | **CLI: `aws iam simulate-principal-policy`** (mandatory) | Ground-truth authorization check over the itemized runtime surface; **the MCP server does not run it, and `call_aws`/`run_script` SUCCEEDING is NOT proof of the runtime role's perms** (different principal) — L20 | MCP `call_aws get-role-policy`/`list-attached-role-policies` may *gather* the inputs; the **decision is the simulator's**. |
| **KMS-key-policy / bucket-policy / staging verify (part b)** | **CLI/SDK read** (+ MCP read to gather) | The simulator is BLIND here; separate manual check (L1/L2) | MCP read can fetch the key policy JSON; the *verification* (caller-of-record named in the key policy) is the skill's check. |
| **Live single-item smoke (part c)** | **CLI/SDK on REAL services + REAL deployed ASL** (mandatory) | Only a real run on the real ASL catches uncatchable States.Runtime + integration-seam denials + the COST_ABORTED mirage (L1/L15/L16) | **The MCP server does NOT substitute for the live smoke** (L20). |
| **Mutating runtime action via MCP** (rare; an operator one-off the user explicitly authorizes) | **MCP allowed ONLY under the same governance as CLI** | Convenience must not bypass governance | **G0 signed-approval gate + cost-ceiling + a terminal qa-gate**, exactly like a CLI mutation (L22). Read-only is the default; mutation is explicit opt-in (§MCP setup). |

---

## MCP setup / auth / governance (the AWS MCP Server config — DRAFT, NOT installed)

**Use when:** wiring up the AWS MCP Server. The config is **draft** in `Skill/mcp/` (`aws-mcp.mcp.json` +
`SETUP.md`); **register it DELIBERATELY — do NOT auto-install.** Every fact here is grounded in
`MCP_VALIDATION.md`.

- **Source-of-truth rule [L22]:** **CloudFormation + CLI/boto3 remain the source of truth for all
  create/deploy.** The AWS MCP Server is for **docs / discover / read / diagnose**. Never author
  create/deploy as ad-hoc MCP `call_aws` mutations.
- **Auth [L21/L22]:** IAM **SigV4**; the local **`mcp-proxy-for-aws==1.6.0`** (pinned **— verify current,
  may drift**; the principle "pin a version, never `@latest`" is permanent, the *number* is not) via `uvx`
  bridges SigV4→OAuth (MCP requires OAuth 2.1). Doc tools need no auth; `call_aws`/`run_script` inherit the
  proxy's IAM identity. **No `@latest`** in any wired `Skill/mcp/` deliverable.
- **Least-privilege default role [L22 / SQ11b] — RESOURCE-SCOPED read-only, NOT a blanket allow-all:**
  the default MCP profile uses `Describe*` / `List*` + **narrow** `Get*` — but **NOT** a bare
  `Get*/List*/Describe*` allow-all (that is read-only yet NOT least-privilege: it would include
  `secretsmanager:GetSecretValue`, all-bucket `s3:GetObject`, `iam:Get*` role/policy exfiltration).
  **Exclude `secretsmanager:GetSecretValue`; scope `s3:GetObject`/`s3:ListBucket` to the medallion
  buckets;** prefer `Describe*`/`List*` over broad `Get*` on data/secret-bearing services — consistent
  with the resource-ARN-scoped least-privilege bar (§IAM/KMS). Safety comes from the **role**, not the
  tool.
- **Mutation is explicit opt-in [L22]:** under a separately-assumed, narrowly-scoped role — and any
  mutating MCP use is governed by the **same fail-closed G0 signed-approval gate + cost-ceiling + terminal
  qa-gate** as a CLI mutation. Tag the role/session (`Project=`, `env=`) for cost + audit; reconcile
  CloudTrail / Cost Explorer.
- **Audit [SQ11c]:** **CloudTrail logs all API calls** (and at minimum every `call_aws`). **Open item:**
  whether `run_script`'s server-side AWS calls are individually CloudTrailed under the caller identity is
  unconfirmed — **prefer `call_aws` for any state read that must be individually auditable** until
  confirmed.
- **Data residency [criterion 15]:** the AWS MCP Server endpoint (us-east-1 / Frankfurt) is where the MCP
  request **transits** even when `AWS_REGION` routes elsewhere; the Knowledge-MCP `global.api.aws`
  endpoint receives orient-phase doc queries. **Choose the endpoint by data-residency/latency policy
  (nearest the governance boundary) and confirm both endpoints are acceptable processor boundaries before
  relying on them.** The Anthropic-native connector is additionally **not ZDR-eligible** (below).
- **Registration (deliberate, pins the proxy — do NOT use `@latest`):**
  ```
  claude mcp add-json aws-mcp --scope user \
    '{"command":"uvx","args":["mcp-proxy-for-aws==1.6.0","https://aws-mcp.us-east-1.api.aws/mcp","--metadata","AWS_REGION=us-east-2"]}'
  ```
  `AWS_REGION=us-east-2` is the **AWS-Twin reference-env value — replace with your operating region** (not
  a universal constant). Knowledge MCP (no proxy; no-auth per awslabs config, not verbatim-confirmed —
  confirm before air-gapped reliance): `https://knowledge-mcp.global.api.aws`.
  **Do NOT copy the proxy line from the resource-hub example** (`aws-mcp-claude-resource-hub/.../examples/
  claude-code/aws-mcp-config.md`) — it ships `mcp-proxy-for-aws@latest` (SUPERSEDED). That hub is a
  **frozen upstream snapshot**; its correction lives in `MCP_VALIDATION.md §6 (S1)` + `Skill/mcp/SETUP.md
  §3`. Use the pinned `==1.6.0` form.
- Sources: `MCP_VALIDATION.md §1,§2,§6`; `Skill/mcp/SETUP.md`; `Skill/mcp/aws-mcp.mcp.json`.

## Anthropic-native MCP surfaces — REFERENCE / FUTURE (beta, provider-gated) [L23]

**Use when:** asked whether to wire the Anthropic-native **MCP connector** or **Managed Agents** into the
Twin's Claude Code. **Short answer: not on the current provider.**

- **Provider fidelity [L23]:** the **MCP connector** (Messages API, beta `mcp-client-2025-11-20`) and
  **Managed Agents** (beta `managed-agents-2026-04-01`) are available on **Claude API / Claude Platform on
  AWS / (connector also Microsoft Foundry)** but **NOT on Amazon Bedrock or Vertex AI**. The AWS Twin runs
  Claude Code **on Amazon Bedrock**, so these surfaces are **reference/future, gated on a provider
  decision** — using them would require **Claude Platform on AWS** (Anthropic-operated; bare model IDs;
  SigV4 + `AWS_REGION` + `ANTHROPIC_AWS_WORKSPACE_ID`). They are NOT a usable runbook today. By contrast,
  the **AWS MCP Server + AWS Knowledge MCP Server are provider-agnostic MCP servers the client connects to
  — usable now** regardless of provider.
- **MCP connector shape (reference):** two-part — `mcp_servers:[{type:"url", name, url,
  authorization_token?}]` defines the server; the `tools` array carries `{type:"mcp_toolset",
  mcp_server_name, default_config/configs}`. Tool-calls only; public HTTP (Streamable/SSE); **not
  ZDR-eligible.** REQUIRED header `anthropic-beta: mcp-client-2025-11-20` (the deprecated header is
  `mcp-client-2025-04-04`).
- **Managed Agents shape (reference):** flow is **Agent (create once) → Session (every run)**.
  `model`/`system`/`tools`/`mcp_servers`/`skills` live on the **agent**; **MCP credentials live in a VAULT
  attached to the SESSION via `vault_ids`** (NOT on the agent). The `skills` element uses the typed shape
  **`{type:"anthropic"|"custom", skill_id, version?}`** (the hub's `{name:...}` is imprecise) — beta /
  illustrative; validate before use.
- Sources: `MCP_VALIDATION.md §3,§4,§5` (platform-availability table); `Skill/mcp/SETUP.md §5`.

---

## The pre-spend gate (MANDATORY before any first/full real-spend run)

> **Before any first-spend run, ask yourself (the three diagnostic questions):**
> 1. **Who is the caller-of-record?** For every runtime AWS call, which principal actually makes it — the
>    SM exec role, a Lambda role, or a service principal (BDA)? That principal — not the one you assume —
>    is what must be granted + named in key policies (L2).
> 2. **What is the simulator BLIND to here?** KMS key policies, RCPs, conditioned SCPs, cross-account
>    resource policies — and a green MCP read proves even less (L20). Those go to part (b), not part (a).
> 3. **What REAL side-effect proves success?** Not green status / "N succeeded" — the actual landed output
>    with count > 0 (the COST_ABORTED mirage, L16). Part (c) must observe it on the real ASL.

Three parts, ALL required, ALL **CLI-driven**. Mocked tests do not substitute for any of them (The ONE
rule); **a green MCP `call_aws`/`run_script` does not substitute for any of them either (L20)** — MCP may
GATHER inputs, but the simulator + the live smoke are the DECISIONS.

### Part (a) — Deployed-config IAM-simulator audit
Trace EVERY AWS API call the runtime makes and run `aws iam simulate-principal-policy --policy-source-arn
<live-role> --action-names <svc:Action...> --resource-arns <arn...>` against the **live deployed roles**
(`EvalDecision` must be `allowed`). Cover the **itemized surface** [production-verified —
`feedback_aws_runtime_permission_audit.md`]:
- Every Step Functions ASL state's service integration: `lambda:invoke`; Distributed Map
  `states:StartExecution` (stateMachine ARN) + `states:DescribeExecution`/`StopExecution`
  (`execution:<sm>/*` ARN) + its **S3 ItemReader/ResultWriter perms** (+ `bronze/map_results/*` SSE
  carve-out); `ecs:RunTask.sync` **incl. its EventBridge managed-rule perms**; `aws-sdk:*` integrations;
  **`iam:PassRole`** (with `iam:PassedToService`).
- Bedrock: `bedrock:InvokeModel*` on the dated profile + FM ARNs (region-wildcard); BDA
  `bedrock:InvokeDataAutomationAsync` (region-wildcard profile) + `bedrock:GetDataAutomationStatus`
  (`data-automation-invocation/*`).
- KMS: the caller-of-record's `kms:Decrypt`/`GenerateDataKey`/`DescribeKey` on the CMK ARN.

> **MCP may help here (BOTH):** read-only `call_aws get-role-policy` / `list-attached-role-policies` can
> *gather* the policy inputs faster — but the **`simulate-principal-policy` decision is the CLI's**, and a
> green `call_aws` is NOT proof (it runs as a different principal — L20).

### Part (b) — KMS-key-policy + bucket-policy + staging verification (the simulator is BLIND here)
The simulator does NOT see KMS key policies / RCPs / conditioned SCPs / cross-account resource policies
(canonical blind-spot list, Foundational rules). So SEPARATELY:
- Confirm the **caller-of-record principal is NAMED in each CMK key policy** it must use.
- Check the **bucket policy vs every write path** (SSE-KMS header + exact CMK on payload prefixes; AES256
  carve-out for service I/O).
- Verify **run-start staging:** config has NO placeholders; subnets/SGs are arrays; the live approval item
  exists; env vars are set on ALL functions; Lambda layer mounts are attached.

### Part (c) — Live single-item smoke (REAL services + REAL deployed ASL)
Run ONE smallest-unit slice (< 10% of the full run) end-to-end through the **real deployed pipeline** —
real services, the real ASL (real JSONPath/state transitions), one real API call — **never moto/mocks,
never a green MCP read as a substitute**. This is the only thing that catches uncatchable
`States.Runtime` JSONPath errors and integration-seam denials. **This single live smoke is the ONLY smoke —
the full-run gate (operating-loop step 6 / step 7) CONSUMES this smoke's result, it does NOT re-run it.**
The full run is GATED on a green smoke + (if it spends) the user seeing the smoke result + projected full cost.

---

## Silent-failure / wrong-data hunting [L16] (the bloodiest class — enrich 6 + retry10 9 = 15 bugs)

A run can `exit 0` while producing truncated / partial / wrong data — invisible to mocked tests, to a
green status, AND to a green MCP read. Hunt and gate every one of these:
- **The MIRAGE:** a step reports "succeeded" while producing NOTHING (the Twin's Distributed Map
  "117/117 succeeded" was a `CostAborted` $0 mirage — `bronze/bda/` was empty). **Verify REAL
  side-effects: output landed, count > 0** — never trust green status (or a green `run_script` return).
  This applies BOTH in the pre-spend smoke AND after the full run; it is NOT retired once the smoke passes.
- **Truncation:** gate on **`stop_reason == max_tokens`** → quarantine (do not write a truncated record as
  complete). Keep `max_tokens` ≤ the model ceiling (§Bedrock).
- **Robust LLM-JSON parse:** never `json.loads` raw model output — strip code fences / extract the brace
  span / quarantine-on-failure (Claude wraps JSON in prose/fences).
- **Multi-subdocument aggregation:** a BDA split can produce multiple sub-docs — aggregate ALL
  `standard_output/<N>/result.json`, never just sub-doc 0.
- **Read the right nested path:** e.g. markdown is at **`document.representation.markdown`**, not
  top-level — a wrong nested-path read silently yields empty/partial.
- **Per-item NOT run-wide schema flag:** one bad doc must not fail the whole run (and a run-wide flag must
  not pass on one good doc) — emit `{schema_ok, pii_clean, enriched_count, quarantined_count}` per item;
  the gate proceeds on the COMPLETED set, fails only on a governance breach / threshold.
- **Quarantine vs silent drop:** every un-processable record is quarantined with a reason and reconciled
  against the manifest before any coverage gate; the reconcile universe = ALL manifest items (don't drop
  QUARANTINE shas).
- **Empty-load exit-0** and **stale/orphan nodes** are failures — assert count > 0 and sweep orphans
  (blast-radius-bounded, count-capped).

---

## Worked example: a BDA-extract pipeline (Lambda + SFN Distributed Map + BDA → S3)

Build order, with the gotcha to check at each step (section anchors in brackets):

1. **Orient via MCP** [§AWS Knowledge MCP] — look up the CURRENT BDA params, the target model's
   `max_tokens` ceiling, and any limit you'd otherwise recall, via `search_documentation` — don't trust
   training-data recall.
2. **Plan first** [§Operating loop] — run `/data-dev-planning`; pin grain, idempotency `(sha256,
   blueprint_version)`, reload. Sub-agents get "activate this skill + follow the plan §X" [L14], and any
   MCP-using sub-agent is told the server + read-only posture.
3. **S3 layout** [§S3 medallion] — `source/→bronze/→silver/→gold/`; bronze content-addressed; **define the
   producer/consumer key-contract incl. `ext` NOW** (thread sha256+ext to the ASL `States.Format` URI).
4. **Encryption** [§Encryption] — payloads (silver/gold) behind a same-Region symmetric CMK; **BDA I/O
   prefix on AES256** [L4] (BDA writes as the Bedrock service principal); CMK-deny bucket carves the BDA
   prefix out with `NotResource`.
5. **Lambdas** [§Lambda] — manylinux wheels [L9]; remember code won't refresh on same S3 key [L7].
6. **State machine** [§Step Functions] — Distributed Map over the manifest; **the SM exec role is the
   caller-of-record** [L2] (it — not a Lambda — needs bedrock/S3/KMS perms + `iam:PassRole` [L19] +
   Distributed Map's two ARN scopes + ItemReader/ResultWriter); **never deref `$.ddb.Item`** — pass `$.ddb`,
   `.get("Item")` in-handler [L15].
7. **BDA** [§BDA] — `InvokeDataAutomationAsync` on the region-wildcard profile ARN + `GetDataAutomationStatus`
   on `data-automation-invocation/*` [L18]; sweep the union region set [L3b].
8. **CFN deploy** [§CloudFormation] — author as IaC (NOT ad-hoc MCP mutations); upload the template with
   `--sse-kms-key-id` then `--template-url` [L6]; `CAPABILITY_NAMED_IAM`.
9. **DISCOVER/DIAGNOSE via MCP** [§AWS MCP Server] — read-only `call_aws` to inspect the deployed roles/
   policies and gather the pre-spend audit inputs (check `claude mcp list` for `aws-mcp`; requires it
   registered per §MCP setup — else gather via `aws iam get-role-policy` / `list-attached-role-policies`
   directly). **Diagnose = BOTH:** MCP GATHERS; the step-10 CLI simulator AND the §Troubleshooting **L5
   cheap-first ladder** DECIDE (1:1 with the decision tree's diagnose branch) — a green `call_aws` is NOT
   proof (L20).
10. **PRE-SPEND GATE** [§Pre-spend gate] — IAM-sim audit (itemized) + KMS-key-policy/bucket/staging verify +
    **live single-item smoke on the REAL ASL** before any spend. Then surface projected cost → user go/no-go.
11. **Full run** — checkpointed, idempotent, cost-ceiling ABORT; **verify real side-effects, not green
    status** [L16]; per-item schema flag; gate truncation. **QA both code paths** [L17].
12. **QA-GATE (terminal)** [§QA gate] — the `qa-gate` sub-agent on each artifact; find→batch-fix→re-gate,
    and re-gate AGAIN until a fully clean pass (the re-gate may surface the final bug). Any mutating MCP
    `call_aws`/`run_script` ends here too.

## Troubleshooting decision trees

### Diagnose "Access Denied" — CHEAPEST CHECK FIRST [L5]
The generic **"Access Denied. Check S3 URIs"** (esp. from BDA) is an authz-OR-missing-input message. Walk
the stepped ladder; all three were REAL on the Twin (the IAM/KMS fixes were necessary groundwork, not red
herrings — but the wall was the key-contract). **MCP read-only `call_aws` accelerates the evidence
(head-object, get-bucket-policy, get-role-policy), but the diagnosis logic below is the skill's (L20):**
```
1. CHEAPEST — does the object EXIST at the EXACT key, including extension?
   (producer write-key == consumer read-key incl. .pdf/.tif?)   → fix the key-contract (§S3 medallion).
   The qa-gate proved it: no-ext key → AccessDenied; .pdf key → SUCCESS. Saves ~6 runs.
   (MCP: `call_aws s3api head-object` confirms existence at the exact key — cheap.)
2. Cross-region profile IAM: is the region-WILDCARD profile/FM ARN granted? sim-sweep the union of
   routed regions (§Bedrock / §BDA).  (The DECISION is the CLI simulator's, not a green call_aws.)
3. CMK vs service principal: is this a managed service (BDA) writing to a CMK bucket? → AES256 the I/O
   prefix (§Encryption L4). Is the caller-of-record named in the key policy (§IAM/KMS L2)?
4. iam:PassRole missing for a .sync integration (§Step Functions L19)?
```

### Diagnose a Step Functions failure
```
States.Runtime (uncatchable, Catch[States.ALL] didn't fire)?
   → a JSONPath deref of an absent field (e.g. $.ddb.Item on a new key). Pass the container, .get() in
     handler (§Step Functions L15). Mocked handler tests AND a green MCP read can't see this — use the
     live smoke.
Map children all failed identically before the Lambda ran?
   → same JSONPath class, OR a missing states:StartExecution / ResultWriter perm (§Step Functions, Map).
A "succeeded" Map but no output?
   → the COST_ABORTED mirage — verify real side-effects (§Silent-failure hunting). A green Map status
     (or a green MCP read of the execution) is NOT proof — read the actual S3 output count.
```

---

## Reference — ARN shapes, CLI & MCP (placeholders only)

```
# Inference profile (region-wildcard, acct + id pinned)
arn:aws:bedrock:*:<acct>:inference-profile/us.anthropic.claude-sonnet-4-5-20250929-v1:0
arn:aws:bedrock:*::foundation-model/anthropic.claude-sonnet-4-5-20250929-v1:0   # FM, no acct, ::
# BDA — two different ARNs
arn:aws:bedrock:*:<acct>:data-automation-profile/us.data-automation-v1          # InvokeDataAutomationAsync
arn:aws:bedrock:<region>:<acct>:data-automation-invocation/*                     # GetDataAutomationStatus
# Distributed Map — two scopes
arn:aws:states:<region>:<acct>:stateMachine:<sm>                                 # states:StartExecution
arn:aws:states:<region>:<acct>:execution:<sm>/*                                  # Describe/Stop

# IAM simulator (ground-truth authorization check, no real call) — the pre-spend DECISION
aws iam simulate-principal-policy --policy-source-arn <role-arn> \
  --action-names bedrock:InvokeDataAutomationAsync s3:GetObject kms:Decrypt iam:PassRole \
  --resource-arns <arn1> <arn2> --query 'EvaluationResults[].{a:EvalActionName,d:EvalDecision}'

# Upload a CFN template to a CMK-deny bucket, then deploy by URL
aws s3 cp template.yaml s3://<bucket>/<key> --sse aws:kms --sse-kms-key-id <cmk-arn>
aws cloudformation create-stack --stack-name <s> --template-url https://<bucket>.s3.<region>.amazonaws.com/<key> \
  --capabilities CAPABILITY_NAMED_IAM

# Refresh Lambda code (CFN won't on same S3 key)
aws lambda update-function-code --function-name <fn> --s3-bucket <b> --s3-key <new-key>

# Linux wheels for a Lambda from Windows
pip download --platform manylinux2014 --only-binary=:all: -r requirements.txt -d ./build/wheels

# MCP — register the AWS MCP Server DELIBERATELY (draft; pin the proxy, no @latest)
claude mcp add-json aws-mcp --scope user \
  '{"command":"uvx","args":["mcp-proxy-for-aws==1.6.0","https://aws-mcp.us-east-1.api.aws/mcp","--metadata","AWS_REGION=us-east-2"]}'
# MCP endpoints (pinned — MCP_VALIDATION.md):
#   AWS MCP Server:     https://aws-mcp.us-east-1.api.aws/mcp   (or Frankfurt)
#   AWS Knowledge MCP:  https://knowledge-mcp.global.api.aws    (no proxy; no-auth per awslabs config, not verbatim-confirmed)
# MCP connector beta header (REFERENCE/FUTURE — NOT on Bedrock): anthropic-beta: mcp-client-2025-11-20
# Managed Agents beta header (REFERENCE/FUTURE — NOT on Bedrock): managed-agents-2026-04-01

# AWS-Twin reference env (EXAMPLE ONLY — not a universal constant; use placeholders in real ARNs):
#   account <acct>, region us-east-2, BDA profile us.data-automation-v1, Bedrock via SSO,
#   MCP routed AWS_REGION=us-east-2 (replace with your operating region).
```

---

## QA gate (terminal check after each artifact)

Each finished artifact (IaC stack, Lambda bundle, ASL, a run's output, a deploy, **OR a mutating MCP
`call_aws`/`run_script`**) ends with the **`qa-gate` sub-agent** (`subagent_type: "qa-gate"`, read-only).
Pass it: the artifact path+type, its DoD, the source/authoritative data to reconcile against, and (for
code) leave to invoke `/code-review` + `/simplify`, (for runnable artifacts) `/verify`. It emits a
`QA-GATE-VERDICT-V1` PASS/FAIL; **PASS only on zero blocker AND zero major.**
- **Enforcement (ENFORCED on this host):** the `qa-gate-enforcer.py` `SubagentStop` hook blocks (exit 2)
  on FAIL or an unparseable gate run (fail-closed); ledger `~/.claude/qa_gate_ledger.ndjson`. If ever run
  on a host WITHOUT the hook → ADVISORY-ONLY: print the banner, log to a fallback ledger, and escalate any
  FAIL to the user for accept/defer — never claim "blocks until PASS."
- **find → batch-fix → re-gate, and re-gate AGAIN until a fully clean pass** [good pattern]: when a whole
  stage is unproven, scope-QA it against REAL upstream output in ONE pass and batch-fix — do NOT
  re-run-and-discover one bug at a time. The re-gate itself may surface the final bug.
- **Two-code-paths double-QA [L17]:** when the same logic lives in two paths (a local runner AND a Lambda,
  or two stages), **QA BOTH and re-gate** — a one-path fix is a known trap (a truncation-gate fix once
  landed on one path only; the re-gate caught it). **At BUILD time, inventory every shared-logic surface
  (runner ↔ Lambda, stage ↔ stage) and record the list, so every fix and every re-gate covers ALL copies.**
  [production-verified]

---

## OPEN ITEMS (unverified — confirm before relying)

These load-bearing facts are flagged inline above; consolidated here so an agent sees all of them in one
place before acting. **Default to the conservative route given; confirm via the Knowledge MCP / a live
check before depending on the optimistic one.**

| Open item | Status | Conservative default until confirmed |
|---|---|---|
| Knowledge-MCP **no-auth** | awslabs-config-supported, NOT verbatim-confirmed | Confirm before any air-gapped reliance (§Knowledge MCP). |
| BDA key-policy **`kms:ViaService`** pattern | UNVERIFIED specifically for BDA | Use **AES256** on BDA I/O prefix (proven); present ViaService only as an untested alternative (§Encryption L4). |
| `run_script` server-side calls **individually CloudTrailed?** | unconfirmed | Prefer **`call_aws`** for any state read that must be individually auditable (§MCP setup). |
| `mcp-proxy-for-aws==1.6.0`, `max_tokens` ceiling, routing region sets | pinned values **may drift** | Verify current per-model / per-tool; pin-a-version (not the number) is the permanent rule. |

---

## Rules (non-negotiable)

- **Never authorize a real-spend AWS run on green unit tests alone — NOR on a green MCP `call_aws`/
  `run_script`** [L20] — run the 3-part **CLI-driven** pre-spend gate (IAM-sim audit + KMS-key-policy/
  bucket/staging verify + live real-services real-ASL smoke) first.
- **CloudFormation + CLI/boto3 are the SOURCE OF TRUTH for all create/deploy** — never author create/
  deploy as ad-hoc MCP `call_aws` mutations (no version-controlled, reviewable IaC).
- **Use MCP for orient/research (Knowledge MCP = current-doc authority, NOT training-data recall),
  discover/read, and diagnose; use BOTH for diagnosis (MCP gathers, the skill decides).** The pre-spend
  gate (policy-sim + live smoke) stays CLI + mandatory; MCP never replaces it.
- **KMS needs BOTH the IAM policy AND the key policy** — and the caller-of-record (an SFN task = the SM
  exec role, not a Lambda role) is the principal that must be named.
- **`us.`/`global.` cross-region profiles (Bedrock model AND BDA) need a region-WILDCARD on the pinned
  profile/FM ARN** — region segment only; never an action/account wildcard. Per-region enumeration is a
  trap; BDA and the Bedrock model route to DIFFERENT region sets (sweep the union us-east-1/2+us-west-1/2).
- **BDA does S3 I/O as the Bedrock service principal** — put its I/O prefix on AES256, never a customer
  CMK; granting the caller does not help; ViaService is UNVERIFIED for BDA.
- **"Access Denied. Check S3 URIs" → verify the object exists at the EXACT key (incl. extension) FIRST**
  before chasing IAM/KMS.
- **CFN `deploy --s3-bucket` skips the SSE-KMS header** (upload with `--sse-kms-key-id` then
  `--template-url`); **`update-stack` won't refresh Lambda code on the same S3 key** (use
  `update-function-code`; reattach layers).
- **ECR IMMUTABLE: push only unique versioned tags**, never re-push `:latest`.
- **Windows pip builds Windows wheels** — use `--platform manylinux2014 --only-binary=:all:` or CodeBuild.
- **Control-Tower accounts SCP-deny self-managed Config recorders** — attach rules to the org recorder.
- **No default VPC?** Build VPC + NAT for Fargate egress.
- **GPT-Image is NOT on Bedrock** — use Nova Canvas. Verify a model is hosted (Knowledge MCP) before asserting it.
- **No local Docker?** Build in-cloud via CodeBuild → ECR.
- **Verify REAL side-effects, never green status (or a green MCP read)** (the COST_ABORTED mirage); gate
  truncation (`stop_reason==max_tokens`); per-item not run-wide; robust LLM-JSON parse; read the right
  nested path; quarantine-not-drop.
- **Idempotency = content-addressed sha256 + DynamoDB `(sha256, blueprint_version)`** (SK = blueprint/
  prompt version, NOT a Lambda/object version); producer/consumer S3 key-contract identical incl.
  extension, with a contract test that is ASL-aware or smoke-covered (a Python-only test is insufficient).
- **MCP governance (L22):** SigV4 + `mcp-proxy-for-aws==1.6.0` (no `@latest`); default = a RESOURCE-SCOPED
  read-only role (exclude `secretsmanager:GetSecretValue`; scope `s3:GetObject` to the medallion buckets);
  mutation is explicit opt-in under **G0 + cost-ceiling + terminal qa-gate**; CloudTrail audits all calls;
  MCP is never an un-audited side channel around IaC/governance.
- **MCP provider fidelity (L23):** the Anthropic-native MCP connector (`mcp-client-2025-11-20`) + Managed
  Agents (`managed-agents-2026-04-01`) are BETA and **NOT on Amazon Bedrock** (the Twin's provider) →
  reference/future only; the AWS MCP Server + AWS Knowledge MCP Server are provider-agnostic + usable now.
- **Every delegated build/data sub-agent is told to activate the relevant skill AND follow the governing
  execution plan exactly** — including which MCP server + read-only-vs-mutating posture for any MCP-using
  sub-agent.
- **Least-privilege, resource-ARN-scoped IAM; CMK on payloads, AES256 on service I/O; TLS-only + Block
  Public Access on buckets; secrets in Secrets Manager, never hard-coded (never via MCP read); placeholder
  ARNs, no PII.**
- **Every cost/irreversible artifact — CLI/CFN OR a mutating MCP path — ends with the qa-gate;
  find→batch-fix→re-gate until clean; QA both code paths.**
- **Never state an AWS or MCP behavior you can't source** — AWS rules to a `docs.aws.amazon.com` page or a
  production-verified record (flag the latter); MCP facts to `MCP_VALIDATION.md` (endpoints, beta headers,
  `mcp-proxy-for-aws==1.6.0`).
