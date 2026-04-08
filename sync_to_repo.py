#!/usr/bin/env python3
"""
Sync Script — Copies skills, hooks, memory, and modules from live Claude Code
locations to the master repo. Run manually or via cron/scheduled task.

Usage:
    python sync_to_repo.py              # Sync all categories
    python sync_to_repo.py --dry-run    # Show what would be copied without copying
    python sync_to_repo.py --category skills  # Sync only skills
"""

import argparse
import io
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Fix Windows cp1252 encoding for Unicode output
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ─── Configuration ───────────────────────────────────────────────────────────

REPO_ROOT = Path(r"C:\Users\tmanyang\OneDrive - Fortive\Claude code\In search of a more perfect repo")

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
        # Standalone
        *[(rf"~\.claude\commands\{f}", "skills/standalone/") for f in [
            "ubi-dev.md", "ubi-neo4j.md", "audit-ubi.md", "polish-notebook.md",
            "session-review.md", "paperclip.md", "fluke-ai.md", "flk-litellm.md",
            "taashi-research.md", "repo-eval.md", "521-assignment.md",
        ]],
        # Document
        *[(rf"~\.claude\commands\{f}", "skills/document/") for f in [
            "docx-beautify.md", "doc-extract.md", "doc-extract-reference.md",
            "excel-create.md", "powerpoint-create.md", "powerbi-desktop.md",
            "azure-diagrams.md",
        ]],
        # Knowledge graph
        *[(rf"~\.claude\commands\{f}", "skills/knowledge-graph/") for f in [
            "graphify.md", "graphify-reference.md",
        ]],
    },
    "hooks": {
        *[(rf"~\.claude\hooks\{f}", "configurations/hooks/") for f in [
            "secret-scanner.py", "dangerous-command-blocker.py", "change-logger.py",
        ]],
    },
    "memory": {
        *[(rf"~\.claude\projects\C--windows-system32\memory\{f}", "research/memory/")
          for f in [
            "MEMORY.md",
            "feedback_arrow_direction.md", "feedback_diagram_quality_gate.md",
            "feedback_pbi_underlyingtype.md", "feedback_rbac_rest_api.md",
            "feedback_skill_invocation.md",
            "project_579_writeup.md", "project_ai_bi_tool.md",
            "project_ai_use_case_builder.md", "project_alex_b_fortive_gl.md",
            "project_customer_mdm.md", "project_daily_report.md",
            "project_doc_extract.md", "project_graphify.md",
            "project_llm_usage_tracking.md", "project_paperclip.md",
            "project_plm_drawing_extraction.md", "project_pptx_beautify.md",
            "project_rag_skills.md", "project_skill_framework.md",
            "project_team_ai_enablement.md", "project_ubi_gold_graph.md",
            "reference_cairosvg_windows.md",
        ]],
    },
    "modules": {
        (r"C:\Users\tmanyang\OneDrive - Fortive\Claude code\Document Beautification\docx_beautify.py", "modules/"),
        (r"C:\Users\tmanyang\OneDrive - Fortive\Claude code\Document Beautification\azure_diagrams.py", "modules/"),
    },
}


def resolve_path(p: str) -> Path:
    """Resolve ~ and return a Path object."""
    if p.startswith("~"):
        p = p.replace("~", os.path.expanduser("~"), 1)
    return Path(p)


def sync_file(src_str: str, dest_rel: str, dry_run: bool = False) -> str:
    """Copy a single file if source is newer or destination doesn't exist.
    Returns: 'copied', 'skipped' (up-to-date), or 'missing' (source not found).
    """
    src = resolve_path(src_str)
    dest_dir = REPO_ROOT / dest_rel
    dest = dest_dir / src.name

    if not src.exists():
        return "missing"

    # Skip if destination exists and is same size + same or newer mtime
    if dest.exists():
        src_mtime = src.stat().st_mtime
        dest_mtime = dest.stat().st_mtime
        src_size = src.stat().st_size
        dest_size = dest.stat().st_size
        if dest_mtime >= src_mtime and src_size == dest_size:
            return "skipped"

    if not dry_run:
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(src), str(dest))

    return "copied"


def sync_new_files(category: str, dry_run: bool = False) -> list:
    """Detect new .md files in source dirs that aren't in the sync map."""
    new_files = []

    if category == "skills":
        commands_dir = resolve_path(r"~\.claude\commands")
        if commands_dir.exists():
            known_files = {resolve_path(src).name for src, _ in SYNC_MAP["skills"]}
            for f in commands_dir.glob("*.md"):
                if f.name not in known_files:
                    dest = "skills/standalone/"  # Default new skills to standalone
                    new_files.append((str(f), dest, f.name))
                    if not dry_run:
                        (REPO_ROOT / dest).mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(f), str(REPO_ROOT / dest / f.name))

    elif category == "memory":
        memory_dir = resolve_path(r"~\.claude\projects\C--windows-system32\memory")
        if memory_dir.exists():
            known_files = {resolve_path(src).name for src, _ in SYNC_MAP["memory"]}
            for f in memory_dir.glob("*.md"):
                if f.name not in known_files:
                    dest = "research/memory/"
                    new_files.append((str(f), dest, f.name))
                    if not dry_run:
                        (REPO_ROOT / dest).mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(f), str(REPO_ROOT / dest / f.name))

    elif category == "hooks":
        hooks_dir = resolve_path(r"~\.claude\hooks")
        if hooks_dir.exists():
            known_files = {resolve_path(src).name for src, _ in SYNC_MAP["hooks"]}
            for f in hooks_dir.glob("*.py"):
                if f.name not in known_files:
                    dest = "configurations/hooks/"
                    new_files.append((str(f), dest, f.name))
                    if not dry_run:
                        (REPO_ROOT / dest).mkdir(parents=True, exist_ok=True)
                        shutil.copy2(str(f), str(REPO_ROOT / dest / f.name))

    return new_files


def main():
    parser = argparse.ArgumentParser(description="Sync Claude Code assets to master repo")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be synced without copying")
    parser.add_argument("--category", choices=["skills", "hooks", "memory", "modules", "all"],
                        default="all", help="Sync only a specific category")
    args = parser.parse_args()

    categories = list(SYNC_MAP.keys()) if args.category == "all" else [args.category]

    print(f"{'[DRY RUN] ' if args.dry_run else ''}Sync started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Repo: {REPO_ROOT}")
    print()

    total_copied = 0
    total_skipped = 0
    total_missing = 0
    total_new = 0

    for category in categories:
        print(f"── {category.upper()} ──")

        # Sync known files
        for src, dest in sorted(SYNC_MAP[category]):
            result = sync_file(src, dest, dry_run=args.dry_run)
            filename = resolve_path(src).name
            if result == "copied":
                print(f"  {'WOULD COPY' if args.dry_run else 'COPIED'}  {filename}")
                total_copied += 1
            elif result == "missing":
                print(f"  MISSING  {filename}")
                total_missing += 1
            else:
                total_skipped += 1

        # Detect new files not in the sync map
        new_files = sync_new_files(category, dry_run=args.dry_run)
        for src_path, dest, name in new_files:
            print(f"  {'WOULD ADD' if args.dry_run else 'NEW'}      {name} → {dest}")
            total_new += 1

        print()

    print(f"Summary: {total_copied} copied, {total_new} new, {total_skipped} up-to-date, {total_missing} missing")

    # Write sync log
    if not args.dry_run:
        log_path = REPO_ROOT / ".last_sync"
        log_path.write_text(
            f"timestamp: {datetime.now().isoformat()}\n"
            f"copied: {total_copied}\n"
            f"new: {total_new}\n"
            f"skipped: {total_skipped}\n"
            f"missing: {total_missing}\n"
        )


if __name__ == "__main__":
    main()
