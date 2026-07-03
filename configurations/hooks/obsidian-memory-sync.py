#!/usr/bin/env python3
"""
Obsidian Memory Sync Hook (PostToolUse)
When a Claude Code memory file is created or updated, mirrors its content
as a note in the Obsidian vault under 3-Resources/Claude Memory/.

Protections:
  - Content-hash comparison: skips write if source content unchanged
  - No duplicate session log entries for the same file within 60 seconds
  - Orphan detection: flags Obsidian files whose source no longer exists
  - Source validation: verifies file exists and is readable before sync
  - Atomic write: writes to .tmp then renames to avoid partial files
"""

import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime

MEMORY_DIR = "<ADMIN_HOME>/.claude/projects/C--WINDOWS-system32/memory"
VAULT_PATH = "<USER_HOME>/OneDrive - <ORG>/Claude code/Obsidian"
OBSIDIAN_MEMORY_DIR = os.path.join(VAULT_PATH, "3-Resources", "Claude Memory")
SESSION_DIR = os.path.join(VAULT_PATH, "1-Projects", "Claude Sessions")
TODAY = datetime.now().strftime("%Y-%m-%d")
SESSION_FILE = os.path.join(SESSION_DIR, f"{TODAY}.md")
SYNC_STATE_FILE = os.path.join(OBSIDIAN_MEMORY_DIR, ".sync_state.json")

DEDUP_WINDOW_SECONDS = 60


def is_memory_file(file_path):
    """Check if the file is in the memory directory."""
    normalized = file_path.replace("\\", "/").lower()
    mem_normalized = MEMORY_DIR.replace("\\", "/").lower()
    return normalized.startswith(mem_normalized) and normalized.endswith(".md")


def content_hash(text):
    """SHA-256 hash of the text content (ignoring sync metadata)."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_sync_state():
    """Load the sync state tracking file."""
    if os.path.exists(SYNC_STATE_FILE):
        try:
            with open(SYNC_STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"files": {}, "last_orphan_check": ""}


def save_sync_state(state):
    """Save the sync state tracking file."""
    try:
        tmp = SYNC_STATE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        os.replace(tmp, SYNC_STATE_FILE)
    except OSError:
        pass


def extract_existing_source_hash(dest_path):
    """Extract the source content hash from an existing Obsidian file.
    The hash is stored after the sync metadata wrapper, so we extract
    just the original memory content and hash it for comparison."""
    if not os.path.exists(dest_path):
        return None
    try:
        with open(dest_path, "r", encoding="utf-8") as f:
            existing = f.read()
        # The original content starts after the callout line + blank line
        marker = "> Source: `"
        idx = existing.find(marker)
        if idx == -1:
            return None
        # Find the end of the callout line
        end_callout = existing.find("\n\n", idx)
        if end_callout == -1:
            return None
        original_content = existing[end_callout + 2:]
        return content_hash(original_content.rstrip("\n"))
    except (OSError, UnicodeDecodeError):
        return None


def sync_memory_to_obsidian(file_path, state):
    """Sync a memory file to Obsidian. Returns ('created'|'updated'|'unchanged'|'error')."""
    os.makedirs(OBSIDIAN_MEMORY_DIR, exist_ok=True)

    filename = os.path.basename(file_path)
    dest_path = os.path.join(OBSIDIAN_MEMORY_DIR, filename)

    # Validate source exists and is readable
    if not os.path.isfile(file_path):
        return "error"

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            source_content = f.read()
    except (OSError, UnicodeDecodeError):
        return "error"

    # Content-hash comparison: skip if unchanged
    source_hash = content_hash(source_content.rstrip("\n"))
    existing_hash = state.get("files", {}).get(filename, {}).get("hash", "")
    already_exists = os.path.exists(dest_path)

    if already_exists and source_hash == existing_hash:
        # Double-check by reading the actual Obsidian file
        actual_hash = extract_existing_source_hash(dest_path)
        if actual_hash == source_hash:
            return "unchanged"

    # Build the Obsidian note
    sync_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    action = "updated" if already_exists else "created"

    obsidian_content = f"""---
synced_from: "{file_path.replace(chr(92), '/')}"
last_synced: "{sync_ts}"
source_hash: "{source_hash[:12]}"
tags:
  - claude-memory
  - auto-synced
---

> [!info] Auto-synced from Claude Code memory
> Source: `{filename}` | Last synced: {sync_ts}

{source_content}
"""

    # Atomic write: .tmp then rename
    try:
        tmp_path = dest_path + ".tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(obsidian_content)
        os.replace(tmp_path, dest_path)
    except OSError:
        # Clean up temp file on failure
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        return "error"

    # Update sync state
    state.setdefault("files", {})[filename] = {
        "hash": source_hash,
        "last_synced": sync_ts,
        "source": file_path.replace("\\", "/"),
    }

    return action


def check_orphans(state):
    """Flag Obsidian memory files whose source no longer exists.
    Runs at most once per day to avoid performance overhead."""
    today = datetime.now().strftime("%Y-%m-%d")
    if state.get("last_orphan_check", "") == today:
        return []

    orphans = []
    if not os.path.isdir(OBSIDIAN_MEMORY_DIR):
        return orphans

    for filename in os.listdir(OBSIDIAN_MEMORY_DIR):
        if not filename.endswith(".md") or filename.startswith("."):
            continue
        source = os.path.join(MEMORY_DIR, filename)
        if not os.path.exists(source):
            dest = os.path.join(OBSIDIAN_MEMORY_DIR, filename)
            # Add orphan warning to the file if not already flagged
            try:
                with open(dest, "r", encoding="utf-8") as f:
                    content = f.read()
                if "ORPHANED" not in content:
                    warning = (
                        "\n\n> [!warning] ORPHANED — Source file deleted\n"
                        f"> The source memory file `{filename}` no longer exists in Claude Code memory.\n"
                        f"> Flagged: {today}. Review and archive or delete this note.\n"
                    )
                    with open(dest, "a", encoding="utf-8") as f:
                        f.write(warning)
                    orphans.append(filename)
            except OSError:
                pass

    state["last_orphan_check"] = today
    return orphans


def is_duplicate_session_entry(filename):
    """Check if we already logged a sync for this file within the dedup window."""
    if not os.path.exists(SESSION_FILE):
        return False
    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        # Find the most recent MemorySync entry for this file
        pattern = rf"`(\d{{2}}:\d{{2}}:\d{{2}})` \| \*\*MemorySync\*\* \| `{re.escape(filename)}`"
        matches = list(re.finditer(pattern, content))
        if not matches:
            return False
        last_ts_str = matches[-1].group(1)
        last_ts = datetime.strptime(f"{TODAY} {last_ts_str}", "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        delta = (now - last_ts).total_seconds()
        return delta < DEDUP_WINDOW_SECONDS
    except (OSError, ValueError):
        return False


def append_sync_to_session(filename, action):
    """Append a memory sync note to today's session log, with dedup protection."""
    if not os.path.exists(SESSION_FILE):
        return
    if is_duplicate_session_entry(filename):
        return

    ts = datetime.now().strftime("%H:%M:%S")
    line = f"- `{ts}` | **MemorySync** | `{filename}` | {action} → Obsidian 3-Resources/Claude Memory/\n"

    try:
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.rstrip("\n") + "\n" + line
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            f.write(content)
    except OSError:
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path or not is_memory_file(file_path):
        sys.exit(0)

    filename = os.path.basename(file_path)

    # Skip MEMORY.md index
    if filename.upper() == "MEMORY.MD":
        sys.exit(0)

    state = load_sync_state()
    result = sync_memory_to_obsidian(file_path, state)

    # Run daily orphan check
    orphans = check_orphans(state)

    save_sync_state(state)

    # Only log to session if something actually changed
    if result in ("created", "updated"):
        append_sync_to_session(filename, result)

    if orphans:
        for o in orphans:
            append_sync_to_session(o, "orphaned — source deleted")

    sys.exit(0)


if __name__ == "__main__":
    main()
