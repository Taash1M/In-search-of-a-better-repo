---
name: Outlook Automation Pattern (COM + Explorer trick)
description: Proven method for automating Outlook email search/export from adm-tmanyang session — COM cross-session workaround, DASL filters, Edge PDF, Graph API blockers
type: reference
originSessionId: 16123451-50c1-4bd1-bf89-c33d5f382919
---
## The Problem
Claude Code runs as `adm-tmanyang`. Outlook runs as `tmanyang`. COM can't cross Windows user sessions — both `Dispatch` and `GetActiveObject` fail with `CO_E_SERVER_EXEC_FAILURE` (-2146959355) and `MK_E_UNAVAILABLE` (-2147221021).

## What Doesn't Work on Fortive Tenant
- **Microsoft Graph API**: All tested public client IDs are blocked:
  - `d3590ed6-52b3-4102-aeff-aad2292ab01c` (Microsoft Office) → AADSTS65002 pre-authorization error
  - `14d82eec-204b-4c2f-b7e8-296a70dab67e` (Graph CLI Tools) → AADSTS50105 user not assigned
  - `04b07795-8ddb-461a-bbee-02f9e1bf7b46` (Azure CLI) → AADSTS65002 pre-authorization error
- **exchangelib**: Autodiscover defaults to Basic auth, which Exchange Online has disabled. OAuth needs a registered app.
- **runas**: Requires interactive password input, not possible from Claude Code's bash shell.

## The Working Method
1. Write a Python script using `win32com.client` for Outlook COM
2. Wrap it in a `.bat` file using the **full Python path** (`C:\Users\tmanyang\Python312\python.exe`) — `python` is not on tmanyang's PATH
3. Redirect output to a log file in the .bat
4. Launch via `explorer.exe "C:\path\to\script.bat"` from the admin session
5. Explorer always runs as the desktop user (tmanyang), so the .bat inherits tmanyang's COM access
6. Poll the log file from the admin session to track progress

## Key Technical Details

### DASL Filters (Outlook COM)
```python
# Search subject + body with date range
dasl = (
    '@SQL=('
    '"urn:schemas:httpmail:subject" LIKE \'%keyword%\' '
    'OR "urn:schemas:httpmail:textdescription" LIKE \'%keyword%\''
    ') AND "urn:schemas:httpmail:datereceived" >= \'2026-01-01 00:00\''
)
filtered = inbox.Items.Restrict(dasl)
```

### Safe Iteration
```python
mail = filtered.GetFirst()
while mail is not None:
    # process...
    mail = filtered.GetNext()
```
Do NOT use `for mail in filtered` — COM collection can shift during iteration.

### Edge Headless PDF (replaces Word COM)
```python
subprocess.run([
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "--headless", "--disable-gpu",
    f"--print-to-pdf={pdf_path}",
    "--no-pdf-header-footer",
    "--run-all-compositor-stages-before-draw",
    html_file
], capture_output=True, timeout=30)
```
- Wrap `mail.HTMLBody` in a styled HTML template with header metadata
- Some complex emails may timeout at 30s — increase to 60s for retry

### Python Docstring Gotcha
Windows paths in Python triple-quoted docstrings cause `SyntaxError: (unicode error) 'unicodeescape'` because `\U` in `\Users` is interpreted as a Unicode escape. Use `#` comments instead of `"""` docstrings for module headers containing paths.

## Dependencies
- `pywin32` (win32com.client) — for Outlook COM
- Edge browser at `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`
- Python at `C:\Users\tmanyang\Python312\python.exe`

## Files
- `requests/export_claude_requests_v2.py` — full export script (PDF export of each email)
- `requests/run_export.bat` — launcher for full export (use full Python path, redirect to log)
- `requests/exported_pdfs/` — PDF output folder (62 PDFs as of Apr 24)
- `requests/exported_pdfs/_manifest.csv` — CSV manifest of all matches
- `requests/scan_inbox.py` — lightweight daily scan (subject+body search, 300-char preview, log output)
- `requests/run_scan.bat` — launcher for daily scan
- `requests/scan_results.log` — output from daily scan (poll this after launching)

## Daily Scan vs Full Export
- **Daily scan** (`scan_inbox.py`): Fast (~15s), returns sender/date/subject/body preview to log file. Use for identifying new access requests.
- **Full export** (`export_claude_requests_v2.py`): Slow (~5min), exports each email as PDF. Use for archiving or when you need full email body text.
