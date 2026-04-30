#!/usr/bin/env python3
"""
Sync Script — Copies skills, hooks, memory, modules, MCPs, and settings from
live Claude Code locations to the master repo.

Usage:
    python sync_to_repo.py                        # Sync all categories
    python sync_to_repo.py --dry-run              # Preview without copying
    python sync_to_repo.py --category skills      # Sync only skills
    python sync_to_repo.py --category mcp         # Sync only MCP servers
    python sync_to_repo.py --auto-discover        # Also detect NEW files not in map
"""

import argparse
import io
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows cp1252 encoding for Unicode output
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ─── Configuration ───────────────────────────────────────────────────────────

REPO_ROOT = Path(r"<USER_HOME>/OneDrive - <ORG>\Claude code\In search of a more perfect repo")
CLAUDE_DIR = Path(os.path.expanduser("~")) / ".claude"

SECRET_KEY_PATTERNS = re.compile(r"(KEY|SECRET|TOKEN|PASSWORD)", re.IGNORECASE)

# Source → Destination mappings
SYNC_MAP = {
    "skills": {
        # AI UCB orchestrator
        (r"~\.claude\commands\ai-use-case-builder.md", "skills/ai-ucb/orchestrator/"),
        # AI UCB sub-skills
        *[(rf"~\.claude\commands\{f}", "skills/ai-ucb/sub-skills/") for f in [
            "ai-ucb-ai.md", "ai-ucb-deploy.md", "ai-ucb-discover.md", "ai-ucb-docs.md",
            "ai-ucb-frontend.md", "ai-ucb-infra.md", "ai-ucb-pipeline.md", "ai-ucb-test.md",
        ]],
        # AI UCB companions
        *[(rf"~\.claude\commands\{f}", "skills/ai-ucb/companions/") for f in [
            "agentic-deploy.md", "doc-intelligence.md", "eval-framework.md",
            "rag-multimodal.md", "web-ingest.md",
        ]],
        # AI UCB reference
        *[(rf"~\.claude\commands\ai-ucb\{f}", "skills/ai-ucb/reference/") for f in [
            "archetypes.md", "pricing.md", "governance.md", "infra-templates.md",
            "pipeline-templates.md", "frontend-templates.md", "doc-templates.md",
        ]],
        # Document skills
        *[(rf"~\.claude\commands\{f}", "skills/document/") for f in [
            "docx-beautify.md", "doc-extract.md", "doc-extract-reference.md",
            "excel-create.md", "powerpoint-create.md", "powerbi-desktop.md",
            "azure-diagrams.md",
        ]],
        # Knowledge graph
        *[(rf"~\.claude\commands\{f}", "skills/knowledge-graph/") for f in [
            "graphify.md", "graphify-reference.md",
        ]],
        # Standalone
        *[(rf"~\.claude\commands\{f}", "skills/standalone/") for f in [
            "ubi-dev.md", "ubi-neo4j.md", "audit-ubi.md", "polish-notebook.md",
            "session-review.md", "paperclip.md", "fluke-ai.md", "flk-litellm.md",
            "taashi-research.md", "repo-eval.md", "521-assignment.md",
            "azure-logic-apps.md",
        ]],
    },
    "skill_dirs": {
        # Skill subdirectories — copied recursively
        (r"~\.claude\commands\frontend-slides", "skills/standalone/frontend-slides/"),
        (r"~\.claude\commands\notebooklm", "skills/standalone/notebooklm/"),
    },
    "hooks": {
        *[(rf"~\.claude\hooks\{f}", "configurations/hooks/") for f in [
            "secret-scanner.py", "dangerous-command-blocker.py",
            "change-logger.py", "repo-sync.py",
        ]],
    },
    "memory": {
        # Auto-discovered — but explicit list ensures we don't miss any
        *[(rf"~\.claude\projects\C--windows-system32\memory\{f}", "research/memory/")
          for f in [
            "MEMORY.md",
            # Feedback
            "feedback_arrow_direction.md", "feedback_diagram_quality_gate.md",
            "feedback_pbi_underlyingtype.md", "feedback_pptx_layout.md",
            "feedback_rbac_rest_api.md", "feedback_skill_invocation.md",
            # Projects
            "project_579_writeup.md", "project_ai_bi_tool.md",
            "project_ai_use_case_builder.md", "project_alex_b_fortive_gl.md",
            "project_customer_mdm.md", "project_daily_report.md",
            "project_doc_extract.md", "project_graphify.md",
            "project_leadership_forum.md", "project_llm_usage_tracking.md",
            "project_obsidian.md", "project_paperclip.md",
            "project_pbi_mcp.md", "project_plm_drawing_extraction.md",
            "project_pptx_beautify.md", "project_q1_start_deck.md",
            "project_rag_skills.md", "project_sandbox_logic_apps.md",
            "project_skill_framework.md", "project_sync_repo.md",
            "project_team_ai_enablement.md", "project_ubi_gold_graph.md",
            # Reference
            "reference_cairosvg_windows.md",
        ]],
    },
    "modules": {
        (r"<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification\docx_beautify.py", "modules/"),
        (r"<USER_HOME>/OneDrive - <ORG>\Claude code\Document Beautification\azure_diagrams.py", "modules/"),
    },
    "settings": {
        # settings.json — will be sanitized (secrets redacted) before copy
        (r"~\.claude\settings.json", "configurations/"),
    },
}

# MCP servers — synced as directory trees (not individual files)
MCP_SERVERS = [
    {
        "name": "pbi-semantic",
        "source_root": Path(r"<USER_HOME>/OneDrive - <ORG>\Claude code\MCP\PBI MCP"),
        "dest_root": "modules/mcp-servers/pbi-semantic/",
        "paths": [
            # (source relative path, dest relative path, glob pattern)
            ("src/pbi_semantic_mcp", "src/pbi_semantic_mcp", "*.py"),
            ("src/pbi_semantic_mcp/tools", "src/pbi_semantic_mcp/tools", "*.py"),
            ("src/pbi_semantic_mcp/metadata", "src/pbi_semantic_mcp/metadata", "*.py"),
            ("src/pbi_semantic_mcp/data", "data", "*.yaml"),
            ("src/pbi_semantic_mcp/data/streams", "data/streams", "*.yaml"),
            ("tests", "tests", "*.py"),
        ],
        "root_files": ["pyproject.toml", "README.md"],
    },
]


def resolve_path(p: str) -> Path:
    """Resolve ~ and return a Path object."""
    if p.startswith("~"):
        p = p.replace("~", os.path.expanduser("~"), 1)
    return Path(p)


def sanitize_settings(src: Path) -> str:
    """Read settings.json, redact secrets, return sanitized JSON string."""
    data = json.loads(src.read_text(encoding="utf-8"))
    env = data.get("env", {})
    for key in env:
        if SECRET_KEY_PATTERNS.search(key):
            env[key] = "<REDACTED — set via environment>"
    return json.dumps(data, indent=2, ensure_ascii=False)


def sync_file(src_str: str, dest_rel: str, dry_run: bool = False, sanitize: bool = False) -> str:
    """Copy a single file. Returns: 'copied', 'skipped', or 'missing'."""
    src = resolve_path(src_str)
    dest_dir = REPO_ROOT / dest_rel
    dest = dest_dir / src.name

    if not src.exists():
        return "missing"

    if dest.exists():
        src_stat = src.stat()
        dest_stat = dest.stat()
        if dest_stat.st_mtime >= src_stat.st_mtime and src_stat.st_size == dest_stat.st_size:
            return "skipped"

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        if sanitize:
            dest.write_text(sanitize_settings(src), encoding="utf-8")
        else:
            shutil.copy2(str(src), str(dest))

    return "copied"


def sync_directory(src_dir: str, dest_rel: str, dry_run: bool = False) -> tuple:
    """Recursively copy a directory tree. Returns (copied, skipped, missing) counts."""
    src = resolve_path(src_dir)
    if not src.exists() or not src.is_dir():
        return 0, 0, 1

    copied = skipped = 0
    dest_base = REPO_ROOT / dest_rel
    for f in src.rglob("*"):
        if f.is_file():
            rel = f.relative_to(src)
            dest_file = dest_base / rel
            should_copy = True
            if dest_file.exists():
                if dest_file.stat().st_mtime >= f.stat().st_mtime and f.stat().st_size == dest_file.stat().st_size:
                    should_copy = False
                    skipped += 1

            if should_copy:
                if not dry_run:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(f), str(dest_file))
                copied += 1

    return copied, skipped, 0


def sync_mcp(server: dict, dry_run: bool = False) -> tuple:
    """Sync an MCP server's files. Returns (copied, skipped, missing) counts."""
    copied = skipped = missing = 0
    src_root = server["source_root"]
    dest_root = server["dest_root"]

    for src_rel, dest_rel, glob_pat in server["paths"]:
        src_dir = src_root / src_rel
        if not src_dir.exists():
            missing += 1
            continue
        for f in src_dir.glob(glob_pat):
            dest_dir = REPO_ROOT / dest_root / dest_rel
            dest_file = dest_dir / f.name
            should_copy = True
            if dest_file.exists():
                if dest_file.stat().st_mtime >= f.stat().st_mtime and f.stat().st_size == dest_file.stat().st_size:
                    should_copy = False
                    skipped += 1
            if should_copy:
                if not dry_run:
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(f), str(dest_file))
                copied += 1

    for rf in server.get("root_files", []):
        src_file = src_root / rf
        if src_file.exists():
            dest_file = REPO_ROOT / dest_root / rf
            should_copy = True
            if dest_file.exists():
                if dest_file.stat().st_mtime >= src_file.stat().st_mtime:
                    should_copy = False
                    skipped += 1
            if should_copy:
                if not dry_run:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(str(src_file), str(dest_file))
                copied += 1
        else:
            missing += 1

    return copied, skipped, missing


def auto_discover(category: str, dry_run: bool = False) -> list:
    """Detect new files not in the explicit sync map."""
    new_files = []

    if category == "skills":
        known = {resolve_path(src).name for src, _ in SYNC_MAP["skills"]}
        known_dirs = {resolve_path(src).name for src, _ in SYNC_MAP.get("skill_dirs", set())}
        commands_dir = resolve_path(r"~\.claude\commands")
        if commands_dir.exists():
            for f in commands_dir.glob("*.md"):
                if f.name not in known:
                    new_files.append((str(f), "skills/standalone/", f.name))
                    if not dry_run:
                        dest = REPO_ROOT / "skills/standalone"
                        dest.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(f), str(dest / f.name))
            for d in commands_dir.iterdir():
                if d.is_dir() and d.name not in known_dirs and d.name != "ai-ucb" and d.name != "__pycache__":
                    dest_rel = f"skills/standalone/{d.name}/"
                    new_files.append((str(d), dest_rel, f"{d.name}/ (dir)"))
                    if not dry_run:
                        c, _, _ = sync_directory(str(d), dest_rel)

    elif category == "memory":
        known = {resolve_path(src).name for src, _ in SYNC_MAP["memory"]}
        mem_dir = resolve_path(r"~\.claude\projects\C--windows-system32\memory")
        if mem_dir.exists():
            for f in mem_dir.glob("*.md"):
                if f.name not in known:
                    new_files.append((str(f), "research/memory/", f.name))
                    if not dry_run:
                        dest = REPO_ROOT / "research/memory"
                        dest.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(f), str(dest / f.name))

    elif category == "hooks":
        known = {resolve_path(src).name for src, _ in SYNC_MAP["hooks"]}
        hooks_dir = resolve_path(r"~\.claude\hooks")
        if hooks_dir.exists():
            for f in hooks_dir.glob("*.py"):
                if f.name not in known:
                    new_files.append((str(f), "configurations/hooks/", f.name))
                    if not dry_run:
                        dest = REPO_ROOT / "configurations/hooks"
                        dest.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(f), str(dest / f.name))

    return new_files


def main():
    parser = argparse.ArgumentParser(description="Sync Claude Code assets to master repo")
    parser.add_argument("--dry-run", action="store_true", help="Preview without copying")
    parser.add_argument("--category",
                        choices=["skills", "hooks", "memory", "modules", "mcp", "settings", "all"],
                        default="all", help="Sync a specific category")
    parser.add_argument("--auto-discover", action="store_true",
                        help="Also detect NEW files not in the explicit map")
    args = parser.parse_args()

    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"{prefix}Sync started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Repo: {REPO_ROOT}")
    print()

    total_copied = total_skipped = total_missing = total_new = 0

    # Determine categories to sync
    if args.category == "all":
        categories = ["skills", "skill_dirs", "hooks", "memory", "modules", "settings", "mcp"]
    elif args.category == "skills":
        categories = ["skills", "skill_dirs"]
    else:
        categories = [args.category]

    for category in categories:
        # ── MCP servers (special handling) ───────────────────────────────
        if category == "mcp":
            print("── MCP SERVERS ──")
            for server in MCP_SERVERS:
                print(f"  [{server['name']}]")
                c, s, m = sync_mcp(server, dry_run=args.dry_run)
                total_copied += c
                total_skipped += s
                total_missing += m
                print(f"    {c} copied, {s} up-to-date, {m} missing")
            print()
            continue

        if category not in SYNC_MAP:
            continue

        label = category.upper().replace("_", " ")
        print(f"── {label} ──")

        # ── Skill directories (recursive copy) ───────────────────────────
        if category == "skill_dirs":
            for src, dest in sorted(SYNC_MAP[category]):
                src_path = resolve_path(src)
                if src_path.exists():
                    c, s, _ = sync_directory(src, dest, dry_run=args.dry_run)
                    total_copied += c
                    total_skipped += s
                    print(f"  {src_path.name}/  →  {c} copied, {s} up-to-date")
                else:
                    print(f"  MISSING  {src_path.name}/")
                    total_missing += 1
            print()
            continue

        # ── Standard flat-file sync ──────────────────────────────────────
        sanitize = (category == "settings")
        for src, dest in sorted(SYNC_MAP[category]):
            result = sync_file(src, dest, dry_run=args.dry_run, sanitize=sanitize)
            filename = resolve_path(src).name
            if result == "copied":
                print(f"  {'WOULD COPY' if args.dry_run else 'COPIED'}  {filename}")
                total_copied += 1
            elif result == "missing":
                print(f"  MISSING  {filename}")
                total_missing += 1
            else:
                total_skipped += 1

        # ── Auto-discover new files ──────────────────────────────────────
        if args.auto_discover and category in ("skills", "memory", "hooks"):
            new_files = auto_discover(category, dry_run=args.dry_run)
            for _, dest, name in new_files:
                print(f"  {'WOULD ADD' if args.dry_run else 'NEW'}  {name} → {dest}")
                total_new += 1

        print()

    print(f"Summary: {total_copied} copied, {total_new} new, {total_skipped} up-to-date, {total_missing} missing")

    if not args.dry_run:
        log_path = REPO_ROOT / ".last_sync"
        log_path.write_text(
            f"timestamp: {datetime.now().isoformat()}\n"
            f"copied: {total_copied}\n"
            f"new: {total_new}\n"
            f"skipped: {total_skipped}\n"
            f"missing: {total_missing}\n"
        )
        print(f"\nSync log written to {log_path}")


if __name__ == "__main__":
    main()
