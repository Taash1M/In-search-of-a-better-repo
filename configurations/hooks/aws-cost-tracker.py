#!/usr/bin/env python3
"""
AWS Cost Tracker Hook (PostToolUse on Bash)
-------------------------------------------
Whenever a Bash command touches AWS (aws CLI, boto3 via python, BDA/Bedrock/S3
calls), append a granular cost-event row to the per-day execution ledger so spend
can be rolled up per project / per service / per execution.

Design:
  * NON-BLOCKING: always exit 0. Never interferes with the actual command.
  * GRANULAR: one JSONL line per detected AWS action; keeps raw signal
    (command, service, detected resource, units when parseable) so rollups can
    aggregate any way later (rollup_costs.py).
  * BEST-EFFORT COST: estimates cost from costs/rate_card.json when units are
    knowable (e.g. an explicit --pages / image count); otherwise logs the event
    with cost=null + needs_actuals=true so it is captured but not guessed.
  * Authoritative actuals come from AWS Cost Explorer / CUR; this hook captures
    activity + estimates for same-day visibility and reconciliation.

Ledger: <AWS project>/costs/executions/aws_costs_YYYY-MM-DD.jsonl
The AWS project root is resolved from the command's working dir / paths; falls
back to AWS_TWIN_COSTS_DIR env or a default sentinel so nothing is lost.
"""

import json
import os
import re
import sys
from datetime import datetime

DEFAULT_PROJECT_ROOT = (
    "<USER_HOME>/OneDrive - <ORG>/AI/Technical Validation/AWS"
)

# Service detection: regex -> (service tag, optional unit-extractor)
AWS_TRIGGERS = [
    (r"\baws\s+bedrock-data-automation", "bda"),
    (r"\bdata-automation", "bda"),
    (r"\baws\s+bedrock(?:-runtime)?\b", "bedrock"),
    (r"\binvoke[-_]model", "bedrock"),
    (r"\bnova-canvas|nova_canvas|titan-image|image-generat", "bedrock-image"),
    (r"\baws\s+s3\b|\baws\s+s3api\b|\bs3://", "s3"),
    (r"\baws\s+ec2\b", "ec2"),
    (r"boto3|botocore", "boto3"),
    (r"\baws\s+", "aws-cli"),
]

# Commands that are pure reads / config — capture activity but cost ~0.
READONLY_HINTS = (
    "get-", "list-", "describe-", "head-", "ls ", " ls", "show", "wait",
    "sts get-caller-identity", "configure", "--version", "help",
)


def resolve_project_root(command, cwd):
    """Best-effort: find the AWS project root so the ledger lands in costs/."""
    env_dir = os.environ.get("AWS_TWIN_COSTS_DIR")
    if env_dir:
        return env_dir
    hay = f"{command}\n{cwd or ''}"
    m = re.search(r"(.*?[/\\]Technical Validation[/\\]AWS)(?![A-Za-z])", hay)
    if m:
        return m.group(1)
    return DEFAULT_PROJECT_ROOT


def detect_service(command):
    for pattern, tag in AWS_TRIGGERS:
        if re.search(pattern, command, re.IGNORECASE):
            return tag
    return None


def load_rate_card(project_root):
    path = os.path.join(project_root, "costs", "rate_card.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f).get("rates", {})
    except Exception:
        return {}


def estimate_cost(service, command, rates):
    """Return (cost_or_None, units_dict, needs_actuals_bool).

    Only estimate when units are explicit in the command; never guess volume.
    """
    units = {}
    cl = command.lower()

    # explicit page count, e.g. --pages 4  /  pages=4
    pages = re.search(r"--?pages[ =](\d+)", cl)
    images = re.search(r"--?(?:num[-_]?images|image[-_]?count)[ =](\d+)", cl)

    if service == "bda" and pages:
        n = int(pages.group(1))
        units["pages"] = n
        rate = rates.get("bda.custom_output_per_page")
        if rate is not None:
            return round(n * rate, 6), units, False

    if service in ("bedrock-image",) and images:
        n = int(images.group(1))
        units["images"] = n
        rate = rates.get("bedrock.nova_canvas_per_image_standard_1024")
        if rate is not None:
            return round(n * rate, 6), units, False

    # read-only / config calls cost ~nothing
    if any(h in cl for h in READONLY_HINTS):
        return 0.0, units, False

    # activity captured, but volume not parseable -> reconcile from AWS actuals
    return None, units, True


def append_event(project_root, row):
    day = datetime.now().strftime("%Y-%m-%d")
    ledger_dir = os.path.join(project_root, "costs", "executions")
    try:
        os.makedirs(ledger_dir, exist_ok=True)
        path = os.path.join(ledger_dir, f"aws_costs_{day}.jsonl")
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        pass  # never block


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    if data.get("tool_name") != "Bash":
        sys.exit(0)

    tool_input = data.get("tool_input", {}) or {}
    command = tool_input.get("command", "") or ""
    if not command.strip():
        sys.exit(0)

    service = detect_service(command)
    if not service:
        sys.exit(0)  # not an AWS command

    cwd = data.get("cwd") or tool_input.get("cwd") or ""
    project_root = resolve_project_root(command, cwd)
    rates = load_rate_card(project_root)
    cost, units, needs_actuals = estimate_cost(service, command, rates)

    # detected resource hints (bucket / project arn / model id) — granular signal
    bucket = re.search(r"s3://([^/\s]+)", command)
    model = re.search(r"--model-id[ =]([^\s]+)", command)
    project_arn = re.search(r"data-automation-project/([0-9a-f]+)", command)

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "project": "aws-twin-plm-drawings",
        "service": service,
        "command": command[:500],
        "units": units,
        "estimated_cost_usd": cost,
        "needs_actuals": needs_actuals,
        "resource": {
            "bucket": bucket.group(1) if bucket else None,
            "model_id": model.group(1) if model else None,
            "bda_project": project_arn.group(1) if project_arn else None,
        },
        "session_id": data.get("session_id", ""),
        "source": "aws-cost-tracker-hook",
    }
    append_event(project_root, row)
    sys.exit(0)


if __name__ == "__main__":
    main()
