---
name: Fabric Gold Lakehouse Permissions
description: Downstream lakehouse shortcut permissions — 4 approaches evaluated, 4 deliverables (audit xlsx + 3 DOCX guides), DAR blocked by tenant setting, managed tables recommended (2026-05-12)
type: project
originSessionId: c75a0674-7e11-4fff-8068-f0ac01bd1e3f
---
## Overview

Audited and resolved permissions for <ORG_ABBR>-Americas-Commercial-Fabric downstream lakehouse, which has 23 OneLake shortcuts pointing to the Gold Lakehouse (FLK_UBI_LH_GOLDS) in <ORG_ABBR>-UBI-GOLD-PROD workspace.

**Why:** Commercial Americas Users need to query data in their downstream lakehouse without having any direct access or visibility to the Gold workspace or Gold Lakehouse.

**How to apply:** Use these findings when configuring Fabric lakehouse permissions, shortcut architectures, or data isolation patterns.

## Key Facts

- **Gold Workspace**: <ORG_ABBR>-UBI-GOLD-PROD (`4037a9f7-9627-4b77-a7bb-ae42bbdaf1bc`)
- **Gold Lakehouse**: FLK_UBI_LH_GOLDS (`0a252e47-a44f-4002-8d96-4cbdb8dc1951`) — 441 tables
- **Downstream Workspace**: <ORG_ABBR>-Americas-Commercial-Fabric (`1b6e971e-c00a-4e39-9346-94f7c1aefca8`)
- **Downstream Lakehouse**: FLK_UBI_Commercial_LH — 23 shortcuts (21 from Gold, 2 from IIR lakehouse `8005cdb4-...`)
- **Security group overlap**: `<ORG_ABBR>-<ORG_ABBR>-flkazu-ubi-commercialusers` has Viewer on BOTH Gold and downstream workspaces — must be resolved for any approach
- **Deliverables folder**: `<USER_HOME>/OneDrive - <ORG>\ADHOC\UBI\Fabric Gold Lakehouse\`

## Critical Technical Finding

**OneLake shortcuts use delegated user identity** — every query is authenticated against the source lakehouse using the querying user's credentials. There is NO owner-identity mode for internal OneLake shortcuts. This means any user who queries a shortcut MUST have at least ReadAll on the source lakehouse.

## 4 Approaches Evaluated

| # | Approach | Gold Access | Granularity | Real-time | Status |
|---|----------|-------------|-------------|-----------|--------|
| 1 | Workspace Viewer role | Yes (sees entire workspace) | None | Yes | Too broad |
| 2 | Item-level ReadAll | No workspace visibility, but reads ALL 441 tables | None | Yes | Too broad |
| 3 | OneLake Data Access Roles (DAR) | Table-level restriction, no workspace visibility | Per-table | Yes | **Blocked** — tenant setting disabled |
| 4 | Managed tables via pipeline | Zero Gold access | Complete isolation | Scheduled | **Recommended** |

### DAR Blocker
OneLake Data Access Roles require tenant admin to enable "Users can define OneLake data access roles" in Fabric Admin Portal. API returns `UniversalSecurityFeatureDisabledForWorkspace`. Cannot be enabled via workspace-level or lakehouse-level API — requires <ORG_PARENT> tenant admin action.

## Deliverables (4 files, all PII-stripped)

| File | Description |
|------|-------------|
| `Fabric_Workspace_Audit_20260512.xlsx` | 7 sheets, 441 lakehouse tables, 14 role assignments, APAC/PPV focus |
| `Fabric_Lakehouse_Permissions_Guide_20260512.docx` | Data copy pipeline approach — full step-by-step |
| `Fabric_DAR_Permissions_Guide_20260512.docx` | OneLake Data Access Roles approach — 8 implementation steps, all 23 tables |
| `Fabric_Managed_Tables_Migration_Guide_20260512.docx` | 2-page managed tables conversion — recommended approach |

All documents sanitized: no personal names or email addresses (replaced with generic roles per user policy).
