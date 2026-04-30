#!/usr/bin/env python3
"""
Repo Sync Hook (PostToolUse)
Automatically copies modified skill, hook, memory, MCP, and settings files to the
master sync repo when Claude Code writes or edits them.

Triggers on: Edit, Write, MultiEdit
Watches:
  - ~/.claude/commands/*.md              → skills/ (routed by name)
  - ~/.claude/commands/ai-ucb/*.md       → skills/ai-ucb/reference/
  - ~/.claude/commands/<subdir>/         → skills/standalone/<subdir>/
  - ~/.claude/hooks/*.py                 → configurations/hooks/
  - ~/.claude/projects/.../memory/*.md   → research/memory/
  - ~/.claude/settings.json              → configurations/ (secrets redacted)
  - MCP server source files              → modules/mcp-servers/

This hook does NOT git commit/push — use push_to_github.py for that.
It only ensures the repo directory stays in sync with local Claude Code files.
"""

import json
import os
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(r"<USER_HOME>/OneDrive - <ORG>\Claude code\In search of a more perfect repo")
CLAUDE_DIR = Path(os.path.expanduser("~")) / ".claude"

# ── MCP server source directories ────────────────────────────────────────────
# Order matters: more-specific paths MUST come before less-specific ones,
# because the first match wins.
MCP_ROOTS = [
    # data/ subdir gets special dest (no src/ prefix)
    (Path(r"<USER_HOME>/OneDrive - <ORG>\Claude code\MCP\PBI MCP\src\pbi_semantic_mcp\data"),
     "modules/mcp-servers/pbi-semantic/data"),
    # everything else under pbi_semantic_mcp/
    (Path(r"<USER_HOME>/OneDrive - <ORG>\Claude code\MCP\PBI MCP\src\pbi_semantic_mcp"),
     "modules/mcp-servers/pbi-semantic/src/pbi_semantic_mcp"),
]
MCP_EXTENSIONS = {".py", ".yaml", ".yml", ".md", ".toml", ".json"}

# ── Settings file (exact match, secrets redacted on copy) ────────────────────
SETTINGS_FILE = CLAUDE_DIR / "settings.json"

# Secret patterns to redact in settings.json
SECRET_KEY_PATTERNS = re.compile(r"(KEY|SECRET|TOKEN|PASSWORD)", re.IGNORECASE)

# ── Path / PII sanitization (applied to ALL synced content) ─────────────────
# Order matters: longer / more-specific patterns first.
SANITIZE_RULES = [
    # Admin user paths (both slash styles) — before regular user
    (re.compile(r"C:[/\\]Users[/\\]<ADMIN_USER>[/\\]?"), "<ADMIN_HOME>/"),
    # Regular user paths
    (re.compile(r"C:[/\\]Users[/\\]<USER>[/\\]?"), "<USER_HOME>/"),
    # Company name in OneDrive paths
    (re.compile(r"OneDrive\s*-\s*Fortive"), "OneDrive - <ORG>"),
    # VM user paths
    (re.compile(r"<VM_HOME>/?"), "<VM_HOME>/"),
    # Email addresses (before standalone username)
    (re.compile(r"taashi\.manyanga@fluke\.com"), "<USER>@<ORG_DOMAIN>"),
    (re.compile(r"taashi\.manyanga@fortive\.com"), "<USER>@<ORG_DOMAIN>"),
    (re.compile(r"taashi\.manyanga@gmail\.com"), "<USER>@<PERSONAL_DOMAIN>"),
    # Standalone usernames (word-boundary)
    (re.compile(r"\badm-<USER>\b"), "<ADMIN_USER>"),
    (re.compile(r"\btmanyang\b"), "<USER>"),
]


def _sanitize_content(text: str) -> str:
    """Replace local paths, usernames, and email addresses with generic placeholders."""
    for pattern, replacement in SANITIZE_RULES:
        text = pattern.sub(replacement, text)
    return text

# ── Skill routing ────────────────────────────────────────────────────────────
SKILL_DIR = CLAUDE_DIR / "commands"
SKILL_OVERRIDES = {
    # AI UCB orchestrator
    "ai-use-case-builder.md": "skills/ai-ucb/orchestrator/",
    # AI UCB sub-skills
    "ai-ucb-ai.md": "skills/ai-ucb/sub-skills/",
    "ai-ucb-deploy.md": "skills/ai-ucb/sub-skills/",
    "ai-ucb-discover.md": "skills/ai-ucb/sub-skills/",
    "ai-ucb-docs.md": "skills/ai-ucb/sub-skills/",
    "ai-ucb-frontend.md": "skills/ai-ucb/sub-skills/",
    "ai-ucb-infra.md": "skills/ai-ucb/sub-skills/",
    "ai-ucb-pipeline.md": "skills/ai-ucb/sub-skills/",
    "ai-ucb-test.md": "skills/ai-ucb/sub-skills/",
    # AI UCB companions
    "agentic-deploy.md": "skills/ai-ucb/companions/",
    "doc-intelligence.md": "skills/ai-ucb/companions/",
    "eval-framework.md": "skills/ai-ucb/companions/",
    "rag-multimodal.md": "skills/ai-ucb/companions/",
    "web-ingest.md": "skills/ai-ucb/companions/",
    # Document skills
    "docx-beautify.md": "skills/document/",
    "doc-extract.md": "skills/document/",
    "doc-extract-reference.md": "skills/document/",
    "excel-create.md": "skills/document/",
    "powerpoint-create.md": "skills/document/",
    "powerbi-desktop.md": "skills/document/",
    "azure-diagrams.md": "skills/document/",
    # Knowledge graph
    "graphify.md": "skills/knowledge-graph/",
    "graphify-reference.md": "skills/knowledge-graph/",
}
SKILL_DEFAULT = "skills/standalone/"

# ── Watch rules for flat-directory matching ──────────────────────────────────
WATCH_RULES = [
    # AI UCB reference: ~/.claude/commands/ai-ucb/*.md
    {
        "dir": SKILL_DIR / "ai-ucb",
        "extension": ".md",
        "dest": "skills/ai-ucb/reference/",
    },
    # Hooks: ~/.claude/hooks/*.py
    {
        "dir": CLAUDE_DIR / "hooks",
        "extension": ".py",
        "dest": "configurations/hooks/",
    },
    # Memory: ~/.claude/projects/.../memory/*.md
    {
        "dir": CLAUDE_DIR / "projects" / "C--windows-system32" / "memory",
        "extension": ".md",
        "dest": "research/memory/",
    },
]


def _redact_settings(src: Path) -> str:
    """Read settings.json and redact any values whose key matches SECRET_KEY_PATTERNS."""
    try:
        data = json.loads(src.read_text(encoding="utf-8"))
        env = data.get("env", {})
        for key in env:
            if SECRET_KEY_PATTERNS.search(key):
                env[key] = "<REDACTED — set via environment>"
        return json.dumps(data, indent=2, ensure_ascii=False)
    except Exception:
        return src.read_text(encoding="utf-8")


def resolve(file_path: str):
    """Determine where a file should be synced.

    Returns (dest_dir: str, sanitized_content: str | None).
    dest_dir is relative to REPO_ROOT.  sanitized_content is non-None only when
    the file content must be rewritten (e.g. settings.json with redacted secrets).
    Returns (None, None) if the file shouldn't be synced.
    """
    fp = Path(file_path)

    # ── settings.json (exact match, redact secrets) ──────────────────────
    if fp == SETTINGS_FILE:
        return "configurations/", _redact_settings(fp)

    # ── MCP source directories (preserve subpath) ────────────────────────
    for mcp_root, dest_prefix in MCP_ROOTS:
        try:
            rel = fp.relative_to(mcp_root)
            if fp.suffix in MCP_EXTENSIONS:
                parent = str(rel.parent).replace("\\", "/")
                if parent == ".":
                    return dest_prefix + "/", None
                return dest_prefix + "/" + parent + "/", None
        except ValueError:
            continue

    # ── Skills: ~/.claude/commands/*.md ───────────────────────────────────
    # Direct children (*.md files)
    if fp.parent == SKILL_DIR and fp.suffix == ".md":
        dest = SKILL_OVERRIDES.get(fp.name, SKILL_DEFAULT)
        return dest, None

    # Skill subdirectories (e.g. commands/frontend-slides/*)
    # Copy the whole relative path under skills/standalone/<subdir>/
    try:
        rel = fp.relative_to(SKILL_DIR)
        parts = rel.parts
        if len(parts) >= 2:
            subdir = parts[0]
            sub_rel = Path(*parts[1:])
            dest = f"skills/standalone/{subdir}/{str(sub_rel.parent).replace(chr(92), '/')}".rstrip("/") + "/"
            if dest.endswith("./"):
                dest = f"skills/standalone/{subdir}/"
            return dest, None
    except ValueError:
        pass

    # ── Flat watch rules (hooks, memory, ai-ucb reference) ───────────────
    for rule in WATCH_RULES:
        if fp.parent == rule["dir"] and fp.suffix == rule["extension"]:
            return rule["dest"], None

    return None, None


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
    if not file_path:
        sys.exit(0)

    dest_rel, sanitized = resolve(file_path)
    if dest_rel is None:
        sys.exit(0)

    src = Path(file_path)
    if not src.exists():
        sys.exit(0)

    dest_dir = REPO_ROOT / dest_rel
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name

    try:
        if sanitized is not None:
            dest.write_text(_sanitize_content(sanitized), encoding="utf-8")
        elif src.suffix in {".md", ".py", ".json", ".yaml", ".yml", ".toml"}:
            raw = src.read_text(encoding="utf-8")
            dest.write_text(_sanitize_content(raw), encoding="utf-8")
        else:
            shutil.copy2(str(src), str(dest))
    except Exception:
        pass  # Never block tool execution

    sys.exit(0)


if __name__ == "__main__":
    main()
