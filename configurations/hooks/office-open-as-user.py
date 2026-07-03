"""
PreToolUse(Bash) hook: open Office/PDF files as the STANDARD user (GLOBAL\\<USER>),
not the admin account (<ADMIN_USER>).

Mechanism: rewrite `start <file>` into a `runas /savecred /user:GLOBAL\\<USER>`
launch of rundll32 FileProtocolHandler (handles long paths with spaces, and the
file's default O365 app opens in the <USER> context).

ONE-TIME SETUP (seeds the saved credential — run once, interactively, in a terminal):
    runas /savecred /user:GLOBAL\\<USER> "rundll32.exe url.dll,FileProtocolHandler C:\\Windows\\System32\\notepad.exe"
  Enter <USER>'s password when prompted. Windows stores it in Credential Manager
  (target "RunAs"), and every subsequent /savecred launch is non-interactive.

Behavior:
  - If a saved credential is present, rewrite the open to run as <USER>.
  - If NOT seeded yet, fall back to the plain rundll32 open (opens as <ADMIN_USER>)
    and surface a one-line reminder to seed the credential — never blocks the command.
"""
import json, sys, re, subprocess

OFFICE_EXTS = r'\.(docx|xlsx|pptx|doc|xls|ppt|pdf)(?:\s|"|$|\')'
RUN_USER = r"GLOBAL\<USER>"

def cred_seeded():
    """True if a RunAs/<USER> credential is saved in Credential Manager."""
    try:
        out = subprocess.run(["cmdkey", "/list"], capture_output=True, text=True, timeout=5).stdout.lower()
        return ("runas" in out) or ("<USER>" in out)
    except Exception:
        return False

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    if data.get("tool_name") != "Bash":
        return
    command = (data.get("tool_input") or {}).get("command", "")
    if not command or not re.search(OFFICE_EXTS, command, re.IGNORECASE):
        return

    seeded = cred_seeded()

    def rewrite_start(m):
        prefix = m.group(1) or ""
        path = m.group(2)
        rundll = f'rundll32.exe url.dll,FileProtocolHandler "{path}"'
        if seeded:
            # Launch the open in the <USER> context using the saved credential.
            return f'{prefix}runas /savecred /user:{RUN_USER} \'{rundll}\''
        return f'{prefix}{rundll}'

    new_cmd = re.sub(
        r'(^|[;&]\s*)start\s+(?:""?\s*)?["\']?([^"\';&\n]+?\.\w+)["\']?',
        rewrite_start, command, flags=re.IGNORECASE,
    )

    if new_cmd != command:
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "updatedInput": {"command": new_cmd}}}
        if not seeded:
            out["hookSpecificOutput"]["additionalContext"] = (
                "Office file opened as <ADMIN_USER> (fallback). To open as GLOBAL\\<USER>, "
                "seed the credential ONCE: run in a terminal — "
                "runas /savecred /user:GLOBAL\\<USER> \"rundll32.exe url.dll,FileProtocolHandler C:\\Windows\\System32\\notepad.exe\" "
                "— enter <USER>'s password. After that this hook launches O365 apps as <USER> automatically."
            )
        json.dump(out, sys.stdout)

if __name__ == "__main__":
    main()
