#!/usr/bin/env python3
"""
Repo Sync Hook (PostToolUse)
Automatically copies modified skill, hook, and memory files to the master sync repo
when Claude Code writes or edits them.

Triggers on: Edit, Write, MultiEdit
Watches: ~/.claude/commands/*.md, ~/.claude/hooks/*.py, ~/.claude/projects/.../memory/*.md

This hook does NOT git commit/push — that's done by the sync script or manually.
It only ensures the repo directory stays in sync with local Claude Code files.
"""

import json
import os
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(r"C:\Users\tmanyang\OneDrive - Fortive\Claude code\In search of a more perfect repo")

# Map source directory patterns to repo destinations
WATCH_RULES = [
    # Skills: ~/.claude/commands/*.md
    {
        "pattern": os.path.join(os.path.expanduser("~"), ".claude", "commands"),
        "extension": ".md",
        "dest_default": "skills/standalone/",
        "dest_overrides": {
            "ai-use-case-builder.md": "skills/ai-ucb/orchestrator/",
            "ai-ucb-ai.md": "skills/ai-ucb/sub-skills/",
            "ai-ucb-deploy.md": "skills/ai-ucb/sub-skills/",
            "ai-ucb-discover.md": "skills/ai-ucb/sub-skills/",
            "ai-ucb-docs.md": "skills/ai-ucb/sub-skills/",
            "ai-ucb-frontend.md": "skills/ai-ucb/sub-skills/",
            "ai-ucb-infra.md": "skills/ai-ucb/sub-skills/",
            "ai-ucb-pipeline.md": "skills/ai-ucb/sub-skills/",
            "ai-ucb-test.md": "skills/ai-ucb/sub-skills/",
            "agentic-deploy.md": "skills/ai-ucb/companions/",
            "doc-intelligence.md": "skills/ai-ucb/companions/",
            "eval-framework.md": "skills/ai-ucb/companions/",
            "rag-multimodal.md": "skills/ai-ucb/companions/",
            "web-ingest.md": "skills/ai-ucb/companions/",
            "docx-beautify.md": "skills/document/",
            "doc-extract.md": "skills/document/",
            "doc-extract-reference.md": "skills/document/",
            "excel-create.md": "skills/document/",
            "powerpoint-create.md": "skills/document/",
            "powerbi-desktop.md": "skills/document/",
            "azure-diagrams.md": "skills/document/",
            "graphify.md": "skills/knowledge-graph/",
            "graphify-reference.md": "skills/knowledge-graph/",
        },
    },
    # AI UCB reference files: ~/.claude/commands/ai-ucb/*.md
    {
        "pattern": os.path.join(os.path.expanduser("~"), ".claude", "commands", "ai-ucb"),
        "extension": ".md",
        "dest_default": "skills/ai-ucb/reference/",
        "dest_overrides": {},
    },
    # Hooks: ~/.claude/hooks/*.py
    {
        "pattern": os.path.join(os.path.expanduser("~"), ".claude", "hooks"),
        "extension": ".py",
        "dest_default": "configurations/hooks/",
        "dest_overrides": {},
    },
    # Memory: ~/.claude/projects/.../memory/*.md
    {
        "pattern": os.path.join(os.path.expanduser("~"), ".claude", "projects",
                                "C--windows-system32", "memory"),
        "extension": ".md",
        "dest_default": "research/memory/",
        "dest_overrides": {},
    },
]


def should_sync(file_path: str) -> tuple:
    """Check if a file path matches any watch rule. Returns (True, dest_dir) or (False, None)."""
    fp = Path(file_path)
    for rule in WATCH_RULES:
        rule_dir = Path(rule["pattern"])
        if fp.parent == rule_dir and fp.suffix == rule["extension"]:
            dest = rule["dest_overrides"].get(fp.name, rule["dest_default"])
            return True, dest
    return False, None


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only trigger on file write/edit tools
    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    match, dest_rel = should_sync(file_path)
    if not match:
        sys.exit(0)

    src = Path(file_path)
    if not src.exists():
        sys.exit(0)

    dest_dir = REPO_ROOT / dest_rel
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name

    try:
        shutil.copy2(str(src), str(dest))
    except Exception:
        pass  # Never block tool execution

    # Never block
    sys.exit(0)


if __name__ == "__main__":
    main()
