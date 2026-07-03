---
name: ado-shallow-clone-diff
description: ADO YAML pipelines with fetchDepth:1 break git diff merge-base — use fetchDepth:0 for PR review pipelines
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2c4cba16-c1a6-4ffb-91b5-2a773633a61f
---

Never use `fetchDepth: 1` in ADO YAML pipelines that need `git diff` between PR source and target branches. Shallow clones create disconnected histories — `git diff origin/{target}...HEAD` fails with "no merge base" every time.

**Why:** Phase 0 AI Code Review Gate deployed with `fetchDepth: 1` and ran 8 times over 7 days with zero actual reviews — every run silently exited 0 ("nothing to review"). The fallback `HEAD~1` also fails at depth 1 (no parent commit). Cost: a week of PRs with no AI review while the team believed it was working.

**How to apply:**
- Use `fetchDepth: 0` for any pipeline that needs to diff PR changes against a target branch
- Fetch the target branch without `--depth=1`: `git fetch origin "$TARGET_BRANCH"` (not `--depth=1`)
- Add diagnostic logging: `git merge-base origin/$TARGET_BRANCH HEAD` to confirm the merge base exists
- Distinguish "empty diff" (genuine no-changes) from "diff extraction failed" (infrastructure error) — the latter should exit non-zero, not silently pass
- ADO YAML `pr.branches.include` must list the exact branch names used by each repo (e.g., `develop` not just `dev`)
- Pipeline default branch must point to the branch where `pr-ai-review.yml` actually lives (not a stale feature branch)

Related: [[project_ubi_ai_integration]]
