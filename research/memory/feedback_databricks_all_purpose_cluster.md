---
name: feedback_databricks_all_purpose_cluster
description: "Always run Databricks queries on the all-purpose cluster, never a SQL warehouse"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e0f7108b-700f-475d-b7fe-0541a1fb0e73
---

For UBI Databricks work, ALWAYS run queries on the **all-purpose cluster**, never a SQL warehouse (serverless or Starter).

**Why:** SQL warehouses cost-spin and are not the team's sanctioned compute. The all-purpose clusters are already governed and (usually) warm. User made this a standing system-level rule (2026-06-25).

**How to apply:**
- Prod: `flkubi_adb_prd` = cluster_id `0512-005642-s3p6vwha` (DS5_v2, autoscale 2–10, Photon STANDARD). Also `flkubi_adb_prd2` = `0415-073119-t18z28zj`.
- Dev: `flkubi_adb_dev`.
- Query via the **Command Execution API**: `POST /api/1.2/contexts/create` (clusterId + language) → `POST /api/1.2/commands/execute` → poll `/api/1.2/commands/status`. Or `DatabricksMCPClient` bound to the cluster.
- A RESIZING cluster still accepts commands (driver up, workers scaling) — don't wait for RUNNING to start a context.
- Do NOT call `/api/2.0/sql/statements` or pass `warehouse_id`. Listing warehouses for discovery is OK.

**Enforcement:** system-level PreToolUse(Bash) hook `~/.claude/hooks/databricks-all-purpose-cluster.py` (registered in `~/.claude/settings.json`) injects a reminder if a Bash command targets a SQL warehouse. See [[reference_claude_hooks]].
Related: [[so-backlog-stream-specifics]] · the /ubi-mcp skill.
