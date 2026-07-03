#!/usr/bin/env python
"""
PreToolUse(Bash) hook — enforce the standing preference to run Databricks
queries on the ALL-PURPOSE CLUSTER, never on a SQL warehouse.

Rationale: SQL serverless/Starter warehouses cost-spin and are not the team's
sanctioned compute. UBI work must use the prod all-purpose cluster
(flkubi_adb_prd = 0512-005642-s3p6vwha) via the Command Execution API
(/api/1.2/contexts + /api/1.2/commands), which reuses the already-warm,
governed cluster.

Behavior: non-blocking. If a Bash command appears to hit a Databricks SQL
warehouse endpoint, inject a system reminder steering to the all-purpose
cluster. Pure read-only listing of warehouses is allowed (so discovery still
works) but flagged.
"""
import sys, json, re

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    cmd = (data.get("tool_input", {}) or {}).get("command", "") or ""
    low = cmd.lower()

    # Only relevant when talking to Databricks at all
    if "azuredatabricks.net" not in low and "databricks" not in low:
        sys.exit(0)

    # The thing we want to discourage: submitting QUERIES to a SQL warehouse.
    # /api/2.0/sql/statements  -> Statement Execution API (warehouse-backed)
    # warehouse_id=...         -> targeting a warehouse
    # /api/2.0/sql/warehouses/<id>/... with start/stop or query intent
    hits_warehouse_exec = (
        "/api/2.0/sql/statements" in low
        or "warehouse_id" in low
        or re.search(r"/api/2\.0/sql/warehouses/[0-9a-f]{8,}", low) is not None
    )

    # Pure listing of warehouses (discovery) is fine — don't nag on that alone.
    is_pure_list = (
        "/api/2.0/sql/warehouses" in low
        and not hits_warehouse_exec
    )

    if hits_warehouse_exec:
        msg = (
            "STANDING RULE — use the ALL-PURPOSE CLUSTER for Databricks queries, "
            "not a SQL warehouse. This command targets a SQL warehouse "
            "(Statement Execution / warehouse_id). Run the query on the prod "
            "all-purpose cluster instead: flkubi_adb_prd "
            "(cluster_id 0512-005642-s3p6vwha) via the Command Execution API "
            "(POST /api/1.2/contexts/create then /api/1.2/commands/execute), "
            "or DatabricksMCPClient bound to that cluster. Dev cluster: "
            "flkubi_adb_dev. Do NOT start/query serverless or Starter warehouses."
        )
        out = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": msg,
            }
        }
        print(json.dumps(out))
        sys.exit(0)

    if is_pure_list:
        # allow, but leave a light note
        out = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    "Note: listing warehouses is fine for discovery, but run "
                    "actual queries on the all-purpose cluster flkubi_adb_prd "
                    "(0512-005642-s3p6vwha), not a warehouse."
                ),
            }
        }
        print(json.dumps(out))
        sys.exit(0)

    sys.exit(0)

if __name__ == "__main__":
    main()
