---
name: ado-build-service-permissions
description: ADO Build Service needs explicit PullRequestContribute permission to post PR comments — use REST API with ServiceIdentity descriptor. Bypass deployment uses ClaimsIdentity + Python requests (not az rest).
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2c4cba16-c1a6-4ffb-91b5-2a773633a61f
---

ADO Build Service cannot post PR comments by default. The `System.AccessToken` in pipelines returns 403 `TF401027: You need the Git 'PullRequestContribute' permission` unless explicitly granted.

**Why:** Phase 0 AI Code Review Gate's `post_pr_summary_comment()` silently failed on every run because Build Service lacked permission. The function returned False with no log output, making the failure invisible in pipeline logs.

**How to apply:**
- Grant `PullRequestContribute` (bit 16384) in the Git Repositories security namespace (`2e9eb7ed-3c0a-47d4-87c1-0ffdd275fd87`)
- Find the correct Build Service identity: `vssps.dev.azure.com/{org}/_apis/graph/users` → filter for "{ProjectName} Build Service ({OrgName})"
- Convert to ACL descriptor: `vssps.dev.azure.com/{org}/_apis/identities?searchFilter=AccountName&filterValue={projectGuid}` → returns `Microsoft.TeamFoundation.ServiceIdentity;{orgGuid}:Build:{projectGuid}`
- Grant via: `POST /_apis/accesscontrolentries/{nsId}` with `{token: "repoV2/{projectId}/{repoId}", merge: true, accessControlEntries: [{descriptor, allow: 16384, deny: 0}]}`
- `az devops security permission` CLI doesn't work with ServiceIdentity descriptors — always use REST API

**Bypass deployment gotchas (learned 2026-06-17 after 2 hours of churn):**
- For bypass policies (bit 32768), use `Microsoft.IdentityModel.Claims.ClaimsIdentity;{tenantId}\{email}` descriptor — NOT `Microsoft.TeamFoundation.Identity;{GUID}` (returns TF14045)
- **MUST use Python `requests.post(json=payload)`** — `az rest --body` corrupts the backslash (`\t` → tab). This is the #1 cause of churn. See [[reference_ado_bypass_deploy]] for the copy-paste pattern.
- Grant bypass at **repo level** (`repoV2/{project}/{repo}`), not branch level — it inherits
- Revoke bypass with **DELETE** endpoint, not by setting `allow=0` (POST with allow=0 does NOT remove the ACE)
- ADF Main branch requires 2 approvals, Databricks main requires 1 — bypass needed for self-merge on both
- Always audit ALL repos for stale bypass ACEs after deployment — leftover ACEs from prior sessions persist silently

Related: [[reference_ado_bypass_deploy]], [[project_ubi_ai_integration]], [[feedback_rbac_rest_api]]
