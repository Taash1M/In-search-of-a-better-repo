---
name: O365 apps user context
description: Open O365 apps (PowerPoint, Word, Excel) as <USER> not <ADMIN_USER>
type: feedback
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---
When opening O365 applications (PowerPoint, Word, Excel etc.) via COM automation or otherwise, open them as **<USER>** (<USER>@<ORG_DOMAIN>), NOT <ADMIN_USER>.

**Why:** The admin account (<ADMIN_USER>) is for elevated operations. O365/OneDrive apps should run under the standard user profile to avoid sync/licensing issues.

**How to apply:** When using comtypes COM automation for PowerPoint export, note this preference. If COM is running as <ADMIN_USER>, the user is aware — this is about the identity context (O365 sign-in), not the Windows process user.
