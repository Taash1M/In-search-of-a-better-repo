---
name: o365-apps-user-context
description: Open O365 apps (Word/Excel/PowerPoint/PDF) as GLOBAL\<USER> not <ADMIN_USER> — system hook uses runas /savecred; needs one-time credential seed
metadata: 
  node_type: memory
  type: feedback
  originSessionId: e0f7108b-700f-475d-b7fe-0541a1fb0e73
---

When opening O365 apps (Word, Excel, PowerPoint, PDF) via CLI, open them as **GLOBAL\<USER>** (<USER>@<ORG_DOMAIN>), NOT <ADMIN_USER>. The admin account is for elevated ops; O365/OneDrive apps run under the standard user profile to avoid sync/licensing issues.

**Enforced by a system-level hook** (PreToolUse/Bash, global `~/.claude/settings.json`): `~/.claude/hooks/office-open-as-user.py`. It rewrites `start <office-file>` into `runas /savecred /user:GLOBAL\<USER> 'rundll32.exe url.dll,FileProtocolHandler "<path>"'` — rundll32 handles long paths with spaces; runas+savecred opens in the <USER> context. Non-office commands pass through untouched.

**ONE-TIME SEED REQUIRED** (the previously-"unsolved" piece): the hook falls back to a plain rundll32 open (as <ADMIN_USER>) + a reminder UNTIL a credential is saved. Seed it once, interactively, from any <ADMIN_USER> terminal:
```
runas /savecred /user:GLOBAL\<USER> "rundll32.exe url.dll,FileProtocolHandler C:\Windows\System32\notepad.exe"
```
Enter <USER>'s password when prompted → stored in Credential Manager (target "RunAs"). After that every O365 open launches as <USER> non-interactively. The hook auto-detects the seed via `cmdkey /list` and switches from fallback to runas. (As of 2026-06-25 the seed was NOT yet done on FLK-36F0P34 — verify with `cmdkey /list` | grep RunAs before assuming <USER> context.)

<USER> is a **domain** account (`GLOBAL\<USER>`), machine `FLK-36F0P34`. [[user-workstation]] · enforcement infra: [[claude-code-hooks]].
