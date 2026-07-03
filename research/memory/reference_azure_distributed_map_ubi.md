---
name: reference-azure-distributed-map-ubi
description: "When doing UBI work, evaluate the Azure equivalent of the AWS Step Functions Distributed Map fan-out pattern; start with the SO Backlog project"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 26203117-c07b-47a6-b7d2-fc239094e124
---

When we next do UBI ETL/orchestration work, look at the **Azure equivalent of the AWS Step Functions
Distributed Map** pattern proven in the PLM Twin ETL pipeline (see [[project-aws-twin]]). The Map is the
fan-out engine: take a work-list of N items, process the same recipe per item across M parallel workers,
with per-item idempotent state tracking (claim → cost-admit → invoke → poll → confirm-output → mark
COMPLETED), resume-safe (skip already-done), and a global cost ceiling.

**Start with:** `<USER_HOME>/OneDrive - <ORG>\ADHOC\UBI\SO Backlog` — assess whether its
per-item/parallel processing would benefit from this orchestration shape.

**Azure equivalents to evaluate** (the AWS→Azure service-equivalence work is in the `data-engineering`
skill's `platforms/cloud-overview.md`):
- **Azure Durable Functions — fan-out/fan-in pattern** (the closest analog to Distributed Map: an
  orchestrator function fans out N activity functions, fans in results; built-in checkpointing/replay
  for idempotent resume).
- **ADF / Synapse pipelines — ForEach activity** with batchCount (parallelism) — simpler, good for
  pipeline-level fan-out over a manifest; pair with a state table for idempotency.
- **Databricks** — for SO Backlog specifically (11 notebooks, 52 Gold views, bi-hourly refresh per the
  UBI facts), Spark-native partition parallelism may already cover the fan-out; the Map pattern matters
  more for per-document/per-API-call external-service work than for set-based SQL transforms.

**Key lessons to carry over from the AWS build** (so UBI doesn't re-learn them):
- Idempotent state table keyed by a content hash so reruns skip completed items (no double-spend).
- Cost-admission gate BEFORE the fan-out + an in-flight ceiling (bounded overshoot).
- The orchestrator's "succeeded" count can be a MIRAGE if items roll back without producing output —
  always verify the actual output landed, not just the control-flow status.
- Mocked/unit tests can't see IAM/managed-identity/Key Vault/storage-firewall denials or service-to-
  service access gaps — run a live single-item smoke that exercises the real wiring before the full run
  (see [[feedback-aws-runtime-permission-audit]]).

Related: [[project-aws-twin]] (the AWS pattern + the full debugging saga), the SO Backlog stream facts
in MEMORY.md, [[feedback-aws-runtime-permission-audit]].
