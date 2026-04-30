#!/usr/bin/env python3
"""
Obsidian Session Logger Hook (PostToolUse)
Appends significant tool activity to today's session log in the Obsidian vault.
Vault: <USER_HOME>/OneDrive - <ORG>/Claude code/Obsidian/
"""

import json
import os
import sys
from datetime import datetime

VAULT_PATH = "<USER_HOME>/OneDrive - <ORG>/Claude code/Obsidian"
SESSIONS_DIR = os.path.join(VAULT_PATH, "1-Projects", "Claude Sessions")
TODAY = datetime.now().strftime("%Y-%m-%d")
SESSION_FILE = os.path.join(SESSIONS_DIR, f"{TODAY}.md")

READONLY_COMMANDS = {
    "cat", "head", "tail", "less", "more",
    "ls", "dir", "tree", "pwd", "which", "where",
    "echo", "printf", "type", "file", "wc", "du", "df",
    "grep", "rg", "find", "fd", "ag",
    "git status", "git log", "git diff", "git show", "git branch",
    "git remote", "git stash list", "git tag",
    "node -e", "python -c", "python3 -c",
}

# Skip logging changes to the session log itself (avoid recursion)
SKIP_PATHS = {SESSION_FILE.replace("/", "\\"), SESSION_FILE}


def is_readonly_command(command):
    cmd = command.strip()
    for ro in READONLY_COMMANDS:
        if cmd.startswith(ro):
            return True
    return False


def ensure_session_file():
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    if not os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            f.write(f"""---
type: session-log
date: {TODAY}
tags:
  - claude-session
  - auto-generated
---

# Claude Session Log -- {TODAY}

## Activity Log

## Session Summary


## Key Decisions


## Findings & Insights


## Links

""")


def append_entry(tool, file_path, action, detail=""):
    ensure_session_file()
    ts = datetime.now().strftime("%H:%M:%S")
    path_short = file_path
    if len(path_short) > 80:
        path_short = "..." + path_short[-77:]

    line = f"- `{ts}` | **{tool}** | `{path_short}` | {action}"
    if detail:
        line += f" | {detail[:120]}"
    line += "\n"

    with open(SESSION_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    marker = "## Activity Log\n"
    idx = content.find(marker)
    if idx == -1:
        content += "\n" + line
    else:
        insert_at = idx + len(marker)
        # Find the next line after marker that's either empty or another entry
        # Insert right after the marker
        rest = content[insert_at:]
        # Find where Activity Log entries end (next ## heading)
        next_section = rest.find("\n## ")
        if next_section == -1:
            content = content[:insert_at] + line + rest
        else:
            content = content[:insert_at] + rest[:next_section] + line + rest[next_section:]

    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name in ("Edit", "MultiEdit"):
        fp = tool_input.get("file_path", "unknown")
        if fp not in SKIP_PATHS:
            append_entry(tool_name, fp, "modified")

    elif tool_name == "Write":
        fp = tool_input.get("file_path", "unknown")
        if fp not in SKIP_PATHS:
            append_entry(tool_name, fp, "created/overwritten")

    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        if command and not is_readonly_command(command):
            cmd_short = command[:100].replace("\n", " ")
            append_entry(tool_name, "-", "executed", cmd_short)

    sys.exit(0)


if __name__ == "__main__":
    main()
