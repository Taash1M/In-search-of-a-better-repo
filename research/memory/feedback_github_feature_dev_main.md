---
name: github-feature-dev-main
description: "STANDARD GitHub process for ALL of the user's repos: feature branch → dev → main, never feature → main directly"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: d0518511-12b3-40f2-a588-f406002e059b
---

The GitHub workflow is **feature → dev → main** for **ALL of the user's repos** (made the universal standard 2026-06-28, confirmed explicitly for `Claude-Code-POC-ETL`). A feature branch PRs into `dev` first, then `dev` PRs into `main`. **Never merge a feature branch directly into `main`** — even when a repo's own history shows prior feature→main merges (that history is NOT the convention to follow; the three-stage flow is). If a repo has no `dev` branch yet, create it off `main` first.

**Why:** User first corrected this on 2026-06-19 (PR #9 merged straight to main on `PLM-AI-Drawing-tool`), then on 2026-06-28 generalized it to "make this feature→dev→main standard for ALL our GitHub pushes." Do not infer the flow from a repo's ambiguous history again — feature→dev→main is the standing rule.

**How to apply:** For any PR on the user's repos:
1. Create `feature/<name>` off `dev` (or main if dev tracks main)
2. PR `feature/<name>` → `dev`, merge
3. PR `dev` → `main`, merge
4. Keep `dev` and `main` from drifting — reconcile if a hotfix lands on one

Applies to ALL repos under `Taashi-Manyanga_fortive` (EMU, private), incl. `PLM-AI-Drawing-tool`, `PLM-AI-Drawing-tool-Azure`, `Claude-Code-POC-ETL`, and any future repo. Use schannel SSL backend for pushes through the corporate proxy ([[git-push-ssl-fix]]). Sanitize before every push ([[repo-sanitization]]).

Related:
- [[reference_github_work]] — work GitHub account + gh CLI path
- [[project-plm-drawing-agent-app]] — repos these apply to
