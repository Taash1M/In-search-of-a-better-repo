---
name: feedback-archive-before-changes
description: Always archive/backup current codebase before making changes; maintain code in <ORG_PARENT> GitHub repo
metadata: 
  node_type: memory
  type: feedback
  originSessionId: a2318a0e-4ed6-487b-aff0-974774603d89
---

Always create a timestamped archive backup of affected code files BEFORE making any changes.

**Why:** User established this as a mandatory practice on 2026-05-18 to prevent losing working baselines. Archive serves as a local rollback point independent of git.

**How to apply:**
1. Create `archive/YYYY-MM-DD_<change-description>/` in the project directory
2. Copy all files that will be modified into the archive folder
3. Then proceed with code changes
4. Commit changes to the GitHub repo with descriptive message

**GitHub repo for ETL code:** `Taashi-Manyanga_fortive/Claude-Code-POC-ETL` (private, <ORG_PARENT> EMU)
- Repo path: `<USER_HOME>/OneDrive - <ORG>\AI\Claude code deployment\claude-code-poc-etl`
- Push with `gh auth setup-git` first (needed for EMU auth via keyring)
- .gitignore excludes: credentials.txt, etl_env.sh, *.env, litellm configs, *.docx/pptx, node_modules, archive/

Related: [[feedback_repo_sanitization]], [[reference_github_work]]
