#!/usr/bin/env python
"""
Data Engineering Skill Activator Hook (PreToolUse)

Detects data engineering work from tool inputs and outputs a reminder
to activate the /data-engineering skill. Fires on Bash, Edit, Write, Agent calls.

Lightweight: keyword scan only, no external calls, <10ms execution.
"""
import json
import sys
import re

DE_KEYWORDS = re.compile(
    r"\b("
    r"etl|elt|pipeline|bronze|silver|gold|delta.?lake|databricks|"
    r"adf|medallion|data.?quality|schema.?drift|duckdb|lakehouse|"
    r"warehouse|grain|idempotent|reconciliation|data.?model|"
    r"scd|orchestration|dag|backfill|incremental|merge|upsert|"
    r"parquet|iceberg|delta.?table|write_deltalake|read_delta|"
    r"dim_|fact_|gold_|silver_|bronze_|"
    r"pyspark|spark\.sql|spark\.read|dataframe|"
    r"data.?contract|data.?validation|data.?test|"
    r"llm_usage_etl|per_user_usage|diagnostic_user_activity"
    r")\b",
    re.IGNORECASE,
)

SKIP_PATTERNS = re.compile(
    r"(git\s+(status|log|diff|push|pull|commit)|"
    r"az\s+vm\s+(start|stop|deallocate|show)|"
    r"wc\s+-[cl]|grep\s+-c|head\s+-|tail\s+-|"
    r"echo\s+|cat\s+.*\.output)",
    re.IGNORECASE,
)


def main():
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        print(json.dumps({}))
        return

    tool_name = event.get("tool_name", "")
    tool_input = json.dumps(event.get("tool_input", {})).lower()

    # Skip non-DE tools
    if tool_name not in ("Bash", "Edit", "Write", "Agent"):
        print(json.dumps({}))
        return

    # Skip trivial commands (git, vm management, file checks)
    if SKIP_PATTERNS.search(tool_input):
        print(json.dumps({}))
        return

    # Check for DE keywords
    matches = DE_KEYWORDS.findall(tool_input)
    if matches:
        unique = sorted(set(m.lower() for m in matches))
        print(json.dumps({
            "message": f"[DE Skill] Data engineering keywords detected: {', '.join(unique[:5])}. "
                       f"Ensure /data-engineering skill methodology is being followed "
                       f"(Orient -> TDD -> Implement -> Validate -> Review -> Guard)."
        }))
    else:
        print(json.dumps({}))


if __name__ == "__main__":
    main()
