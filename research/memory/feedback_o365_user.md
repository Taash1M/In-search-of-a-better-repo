---
name: O365 apps user context
description: Open O365 apps (PowerPoint, Word, Excel) as tmanyang not adm-tmanyang
type: feedback
originSessionId: f4d03941-dd0b-44f2-bb99-51b65b072972
---
When opening O365 applications (PowerPoint, Word, Excel etc.) via COM automation or otherwise, open them as **tmanyang** (taashi.manyanga@fluke.com), NOT adm-tmanyang.

**Why:** The admin account (adm-tmanyang) is for elevated operations. O365/OneDrive apps should run under the standard user profile to avoid sync/licensing issues.

**How to apply:** When using comtypes COM automation for PowerPoint export, note this preference. If COM is running as adm-tmanyang, the user is aware — this is about the identity context (O365 sign-in), not the Windows process user.
