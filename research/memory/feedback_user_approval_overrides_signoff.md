---
name: feedback-user-approval-overrides-signoff
description: "User's explicit build approval overrides plan-level sign-off artifact gates — don't block on file existence checks when user has given direct approval"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 4594d5a3-f2d4-42a6-81ce-eb254c9cde43
---

When the user explicitly approves a build that has a plan-level sign-off gate (e.g., `assert os.path.exists(signoff_artifact)`), their direct approval overrides that gate. Do not block the build or ask again for the physical artifact.

**Why:** The sign-off gate exists for unattended deployments and change-control processes. A direct user message "I approve" carries the same authority as the artifact and should be treated as sufficient.

**How to apply:** When building from a reviewed plan that has `os.path.exists(...)` approval gates: skip those specific assertions (or note them as user-approved in the notebook header), proceed with the build. Still honor all data-quality and technical gates (G0, G1, G4, etc.) — only the human-approval existence checks are overridden.
