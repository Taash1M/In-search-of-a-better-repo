#!/usr/bin/env python3
"""
Push to GitHub — Handles the OneDrive clone → local clone → push workflow.

OneDrive + OpenSSL git push fails on large payloads through corporate proxy.
This script works around it by:
  1. Committing in the OneDrive clone (if uncommitted changes exist)
  2. Creating a git bundle
  3. Pulling the bundle into the local (non-OneDrive) clone
  4. Pushing from the local clone with schannel SSL backend
  5. Cleaning up the bundle

Usage:
    python push_to_github.py                    # Auto-commit + push
    python push_to_github.py --no-commit        # Push existing commits only
    python push_to_github.py --message "msg"    # Custom commit message
    python push_to_github.py --dry-run          # Show what would happen
"""

import argparse
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

# ─── Configuration ───────────────────────────────────────────────────────────

ONEDRIVE_CLONE = Path(r"<USER_HOME>/OneDrive - <ORG>\Claude code\In search of a more perfect repo")
LOCAL_CLONE = Path(r"<USER_HOME>/In-search-of-a-better-repo")
BRANCH = "main"
BUNDLE_PATH = Path(tempfile.gettempdir()) / "repo-sync-bundle.bundle"


def run(cmd: list[str], cwd: Path, check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run a git command and print it."""
    print(f"  $ {' '.join(cmd)}")
    result = subprocess.run(
        cmd, cwd=str(cwd), check=check,
        capture_output=capture, text=True,
    )
    return result


def has_changes(clone: Path) -> bool:
    """Check if the clone has uncommitted changes."""
    result = run(["git", "status", "--porcelain"], clone, capture=True)
    return bool(result.stdout.strip())


def get_head(clone: Path) -> str:
    """Get the HEAD commit hash."""
    result = run(["git", "rev-parse", "HEAD"], clone, capture=True)
    return result.stdout.strip()


def get_remote_head(clone: Path) -> str:
    """Get the remote HEAD commit hash."""
    result = run(["git", "ls-remote", "origin", BRANCH], clone, capture=True)
    if result.stdout.strip():
        return result.stdout.strip().split()[0]
    return ""


def main():
    parser = argparse.ArgumentParser(description="Push sync repo to GitHub")
    parser.add_argument("--no-commit", action="store_true", help="Skip auto-commit, push existing commits only")
    parser.add_argument("--message", "-m", default=None, help="Custom commit message")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without doing it")
    args = parser.parse_args()

    print(f"Push to GitHub — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"OneDrive clone: {ONEDRIVE_CLONE}")
    print(f"Local clone:    {LOCAL_CLONE}")
    print()

    # Verify both clones exist
    for clone, label in [(ONEDRIVE_CLONE, "OneDrive"), (LOCAL_CLONE, "Local")]:
        if not (clone / ".git").exists():
            print(f"ERROR: {label} clone not found at {clone}")
            sys.exit(1)

    # ── Step 1: Commit in OneDrive clone ─────────────────────────────────
    if not args.no_commit and has_changes(ONEDRIVE_CLONE):
        print("Step 1: Committing changes in OneDrive clone...")
        if args.dry_run:
            print("  [DRY RUN] Would stage and commit")
        else:
            run(["git", "add", "-A"], ONEDRIVE_CLONE)
            msg = args.message or f"Sync update {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            run(["git", "commit", "-m", msg], ONEDRIVE_CLONE)
        print()
    else:
        print("Step 1: No uncommitted changes (skipping commit)")
        print()

    # ── Step 2: Check if push is needed ──────────────────────────────────
    local_head = get_head(ONEDRIVE_CLONE)
    remote_head = get_remote_head(ONEDRIVE_CLONE)
    print(f"Step 2: Checking sync state...")
    print(f"  Local HEAD:  {local_head[:12]}")
    print(f"  Remote HEAD: {remote_head[:12]}")

    if local_head == remote_head:
        print("  Already up to date — nothing to push.")
        sys.exit(0)
    print()

    # ── Step 3: Bundle from OneDrive clone ───────────────────────────────
    print("Step 3: Creating git bundle...")
    if args.dry_run:
        print(f"  [DRY RUN] Would create bundle at {BUNDLE_PATH}")
    else:
        run(["git", "bundle", "create", str(BUNDLE_PATH), BRANCH], ONEDRIVE_CLONE)
        size_mb = BUNDLE_PATH.stat().st_size / (1024 * 1024)
        print(f"  Bundle: {BUNDLE_PATH} ({size_mb:.1f} MB)")
    print()

    # ── Step 4: Pull bundle into local clone ─────────────────────────────
    print("Step 4: Pulling bundle into local clone...")
    if args.dry_run:
        print("  [DRY RUN] Would pull bundle")
    else:
        run(["git", "pull", str(BUNDLE_PATH), BRANCH], LOCAL_CLONE)
    print()

    # ── Step 5: Push from local clone (schannel SSL) ─────────────────────
    print("Step 5: Pushing from local clone (schannel SSL)...")
    if args.dry_run:
        print("  [DRY RUN] Would push to origin/main")
    else:
        # Ensure schannel is set
        run(["git", "config", "http.sslBackend", "schannel"], LOCAL_CLONE)
        run(["git", "push", "origin", BRANCH], LOCAL_CLONE)
    print()

    # ── Step 6: Cleanup ──────────────────────────────────────────────────
    if BUNDLE_PATH.exists() and not args.dry_run:
        BUNDLE_PATH.unlink()
        print("Step 6: Bundle cleaned up.")
    else:
        print("Step 6: Nothing to clean up.")

    print()
    print("Done! Remote HEAD should now match local.")

    # Verify
    if not args.dry_run:
        new_remote = get_remote_head(LOCAL_CLONE)
        new_local = get_head(LOCAL_CLONE)
        if new_remote == new_local:
            print(f"  Verified: {new_remote[:12]}")
        else:
            print(f"  WARNING: Remote {new_remote[:12]} != Local {new_local[:12]}")
            print("  Push may have failed — check manually.")
            sys.exit(1)


if __name__ == "__main__":
    main()
